from contextlib import contextmanager
from pathlib import Path
from typing import Literal
import json
import logging
import os
import secrets
import time

import mysql.connector
from mysql.connector import Error, IntegrityError
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from openai import APIError, AsyncOpenAI
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

load_dotenv(Path(__file__).with_name('.env'))
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('hotel')

app = FastAPI(title='Hotel Room Booking System', version='1.0.0')
BASE_DIR = Path(__file__).resolve().parent


def connect_db():
    try:
        return mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', '3306')),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'hotel_db'),
            connection_timeout=5,
        )
    except Error:
        logger.exception('MySQL connection failed')
        raise HTTPException(status_code=503, detail='Database unavailable. Check MySQL and .env settings.')


@contextmanager
def database():
    conn = connect_db()
    try:
        yield conn
    except HTTPException:
        conn.rollback()
        raise
    except Error:
        conn.rollback()
        logger.exception('MySQL query failed')
        raise HTTPException(status_code=500, detail='Database operation failed.')
    finally:
        conn.close()


class BookingCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    customer_name: str = Field(min_length=2, max_length=100)
    room_number: int = Field(ge=1, le=9999)
    room_type: Literal['Single', 'Double', 'Deluxe', 'Suite']
    amount: float = Field(gt=0, le=10000000, allow_inf_nan=False)

    @field_validator('customer_name')
    @classmethod
    def validate_name(cls, value):
        if not any(ch.isalpha() for ch in value):
            raise ValueError('Customer name must contain letters')
        return value


class RoomUpdate(BaseModel):
    room_number: int = Field(ge=1, le=9999)
    room_type: Literal['Single', 'Double', 'Deluxe', 'Suite']


class ChatMessage(BaseModel):
    role: Literal['user', 'assistant']
    content: str = Field(min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1, max_length=30)


class BookingConfirmation(BaseModel):
    token: str = Field(min_length=20, max_length=100)


pending_bookings: dict[str, tuple[BookingCreate, float]] = {}


def get_booking(conn, booking_id):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute('SELECT booking_id, customer_name, room_number, room_type, amount, status FROM bookings WHERE booking_id = %s', (booking_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(404, f'Booking {booking_id} not found')
        row['amount'] = float(row['amount'])
        return row
    finally:
        cursor.close()


def check_room_available(conn, room_number, exclude_id=None):
    cursor = conn.cursor()
    try:
        cursor.execute('''SELECT booking_id FROM bookings
            WHERE room_number = %s AND status IN ('BOOKED', 'CHECKED_IN')
            AND (%s IS NULL OR booking_id <> %s) LIMIT 1''',
            (room_number, exclude_id, exclude_id))
        if cursor.fetchone():
            raise HTTPException(409, f'Room {room_number} is already reserved or occupied')
    finally:
        cursor.close()


def persist_booking(data: BookingCreate):
    with database() as conn:
        check_room_available(conn, data.room_number)
        cursor = conn.cursor()
        try:
            cursor.execute('''INSERT INTO bookings (customer_name, room_number, room_type, amount, status)
                VALUES (%s, %s, %s, %s, 'BOOKED')''',
                (data.customer_name, data.room_number, data.room_type, data.amount))
            booking_id = cursor.lastrowid
            conn.commit()
        finally:
            cursor.close()
        return get_booking(conn, booking_id)


@app.get('/', include_in_schema=False)
def homepage():
    return FileResponse(BASE_DIR / 'index.html')


@app.post('/api/chat')
async def chat(data: ChatRequest):
    api_key = os.getenv('OPENAI_API_KEY')
    model = os.getenv('OPENAI_MODEL')
    if not api_key or not model:
        raise HTTPException(503, 'Chat is not configured. Set OPENAI_API_KEY and OPENAI_MODEL in .env.')

    client = AsyncOpenAI(api_key=api_key)
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {
                    'role': 'system',
                    'content': 'You are StayEase Booking Agent, a single-purpose hotel room booking assistant. Collect the guest name, room number, room type, and amount. Ask for missing details. Do not invent room availability, prices, or booking dates; this system does not track dates. When all required details are provided, call prepare_room_booking. It only checks availability and prepares a draft. Never claim a booking is complete; the guest must use the explicit confirmation button.',
                },
                *[message.model_dump() for message in data.messages],
            ],
            tools=[{
                'type': 'function',
                'function': {
                    'name': 'prepare_room_booking',
                    'description': 'Check room availability and prepare a reservation draft after the guest has provided all required booking details. This does not create the booking.',
                    'strict': True,
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'customer_name': {'type': 'string'},
                            'room_number': {'type': 'integer'},
                            'room_type': {'type': 'string', 'enum': ['Single', 'Double', 'Deluxe', 'Suite']},
                            'amount': {'type': 'number'},
                        },
                        'required': ['customer_name', 'room_number', 'room_type', 'amount'],
                        'additionalProperties': False,
                    },
                },
            }],
            tool_choice='auto',
        )
        message = response.choices[0].message
        if not message.tool_calls:
            return {'reply': message.content or 'Please provide the guest name, room number, room type, and amount.'}

        tool_call = message.tool_calls[0]
        if tool_call.function.name != 'prepare_room_booking':
            raise HTTPException(502, 'The booking agent returned an unsupported action.')
        try:
            booking_data = BookingCreate.model_validate(json.loads(tool_call.function.arguments))
        except (json.JSONDecodeError, ValidationError):
            return {'reply': 'Please provide a valid guest name, room number, room type, and amount.'}

        try:
            with database() as conn:
                check_room_available(conn, booking_data.room_number)
        except HTTPException as error:
            if error.status_code == 409:
                return {'reply': error.detail}
            raise

        now = time.monotonic()
        for token, (_, expires_at) in list(pending_bookings.items()):
            if expires_at <= now:
                pending_bookings.pop(token, None)
        token = secrets.token_urlsafe(32)
        pending_bookings[token] = (booking_data, now + 600)
        return {
            'reply': 'The room is available. Review the reservation details and confirm to create the booking.',
            'pending_confirmation': {
                'token': token,
                'booking': booking_data.model_dump(),
            },
        }
    except APIError:
        logger.exception('OpenAI chat request failed')
        raise HTTPException(502, 'The chat service could not complete your request.')
    finally:
        await client.close()


@app.post('/api/chat/confirm')
def confirm_chat_booking(data: BookingConfirmation):
    pending = pending_bookings.get(data.token)
    if not pending or pending[1] <= time.monotonic():
        pending_bookings.pop(data.token, None)
        raise HTTPException(410, 'This booking confirmation expired. Please prepare the booking again.')
    booking = persist_booking(pending[0])
    pending_bookings.pop(data.token, None)
    return {'booking': booking}


@app.delete('/api/chat/confirm/{token}')
def cancel_chat_booking(token: str):
    pending_bookings.pop(token, None)
    return {'cancelled': True}


@app.get('/api/bookings')
def list_bookings():
    with database() as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute('SELECT booking_id, customer_name, room_number, room_type, amount, status FROM bookings ORDER BY booking_id DESC')
            rows = cursor.fetchall()
            for row in rows:
                row['amount'] = float(row['amount'])
            return rows
        finally:
            cursor.close()


@app.get('/api/bookings/{booking_id}')
def booking_by_id(booking_id: int):
    with database() as conn:
        return get_booking(conn, booking_id)


@app.post('/api/bookings', status_code=201)
def create_booking(data: BookingCreate):
    return persist_booking(data)


@app.put('/api/bookings/{booking_id}/room')
def update_room(booking_id: int, data: RoomUpdate):
    with database() as conn:
        booking = get_booking(conn, booking_id)
        if booking['status'] != 'BOOKED':
            raise HTTPException(409, 'Only BOOKED reservations can change rooms')
        check_room_available(conn, data.room_number, exclude_id=booking_id)
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE bookings SET room_number=%s, room_type=%s WHERE booking_id=%s',
                           (data.room_number, data.room_type, booking_id))
            conn.commit()
        finally:
            cursor.close()
        return get_booking(conn, booking_id)


def transition(booking_id: int, expected: str, new_status: str):
    with database() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE bookings SET status=%s WHERE booking_id=%s AND status=%s',
                           (new_status, booking_id, expected))
            if cursor.rowcount == 0:
                booking = get_booking(conn, booking_id)
                raise HTTPException(409, f"Cannot change {booking['status']} booking to {new_status}; expected {expected}")
            conn.commit()
        finally:
            cursor.close()
        return get_booking(conn, booking_id)


@app.patch('/api/bookings/{booking_id}/check-in')
def check_in(booking_id: int):
    return transition(booking_id, 'BOOKED', 'CHECKED_IN')


@app.patch('/api/bookings/{booking_id}/check-out')
def check_out(booking_id: int):
    return transition(booking_id, 'CHECKED_IN', 'CHECKED_OUT')


@app.patch('/api/bookings/{booking_id}/cancel')
def cancel_booking(booking_id: int):
    return transition(booking_id, 'BOOKED', 'CANCELLED')


@app.delete('/api/bookings')
def delete_all_bookings():
    with database() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM bookings')
            count = cursor.rowcount
            conn.commit()
        finally:
            cursor.close()
        return {'message': 'All bookings deleted', 'deleted_count': count}
