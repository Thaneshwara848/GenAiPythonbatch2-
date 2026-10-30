import os
import logging
from contextlib import contextmanager
from pathlib import Path
from typing import Literal

import mysql.connector
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from mysql.connector import Error as MySQLError
from openai import OpenAI, OpenAIError
from pydantic import BaseModel, Field, field_validator

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('employees')

app = FastAPI(title='Employee Management API', version='1.0.0')
app.mount('/static', StaticFiles(directory=BASE_DIR / 'static'), name='static')


def db_config():
    return {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', '3306')),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME', 'employee_management'),
        'connection_timeout': 5,
    }


@contextmanager
def database():
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(**db_config())
        cursor = connection.cursor(dictionary=True)
        yield connection, cursor
    except MySQLError:
        logger.exception('Database operation failed')
        if connection and connection.is_connected():
            connection.rollback()
        raise HTTPException(status_code=503, detail='Database unavailable or query failed. Check MySQL and .env.')
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


class EmployeeInput(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    age: int = Field(ge=18, le=70)
    email: str = Field(min_length=5, max_length=150)
    department: str = Field(min_length=2, max_length=80)
    designation: str = Field(min_length=2, max_length=80)
    salary: float = Field(ge=0, le=100000000)
    status: Literal['Active', 'Inactive'] = 'Active'

    @field_validator('name', 'email', 'department', 'designation')
    @classmethod
    def trim(cls, value: str):
        value = value.strip()
        if not value:
            raise ValueError('This field cannot be blank')
        return value

    @field_validator('email')
    @classmethod
    def check_email(cls, value: str):
        if '@' not in value or '.' not in value.rsplit('@', 1)[-1]:
            raise ValueError('Enter a valid email address')
        return value.lower()


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)


@app.get('/', include_in_schema=False)
def home():
    return FileResponse(BASE_DIR / 'static' / 'index.html')


@app.get('/api/health')
def health():
    with database() as (_, cursor):
        cursor.execute('SELECT 1 AS ok')
        cursor.fetchone()
    return {'status': 'ok', 'database': 'connected'}


@app.get('/api/employees')
def list_employees(search: str = Query('', max_length=100)):
    with database() as (_, cursor):
        if search:
            pattern = '%' + search + '%'
            cursor.execute('SELECT * FROM employees WHERE name LIKE %s OR department LIKE %s OR designation LIKE %s OR email LIKE %s ORDER BY id DESC', (pattern, pattern, pattern, pattern))
        else:
            cursor.execute('SELECT * FROM employees ORDER BY id DESC')
        return cursor.fetchall()


@app.get('/api/employees/{employee_id}')
def get_employee(employee_id: int):
    with database() as (_, cursor):
        cursor.execute('SELECT * FROM employees WHERE id = %s', (employee_id,))
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail='Employee not found')
        return result


@app.post('/api/employees', status_code=201)
def create_employee(employee: EmployeeInput):
    with database() as (connection, cursor):
        try:
            cursor.execute('INSERT INTO employees (name, age, email, department, designation, salary, status) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                           (employee.name, employee.age, employee.email, employee.department, employee.designation, employee.salary, employee.status))
            connection.commit()
            return {'message': 'Employee created', 'id': cursor.lastrowid}
        except mysql.connector.IntegrityError as exc:
            raise HTTPException(status_code=409, detail='Email already exists') from exc


@app.put('/api/employees/{employee_id}')
def update_employee(employee_id: int, employee: EmployeeInput):
    with database() as (connection, cursor):
        try:
            cursor.execute('UPDATE employees SET name=%s, age=%s, email=%s, department=%s, designation=%s, salary=%s, status=%s WHERE id=%s',
                           (employee.name, employee.age, employee.email, employee.department, employee.designation, employee.salary, employee.status, employee_id))
            if cursor.rowcount == 0:
                # An unchanged UPDATE can report 0 even for an existing row.
                cursor.execute('SELECT id FROM employees WHERE id=%s', (employee_id,))
                if not cursor.fetchone():
                    raise HTTPException(status_code=404, detail='Employee not found')
            connection.commit()
            return {'message': 'Employee updated'}
        except mysql.connector.IntegrityError as exc:
            raise HTTPException(status_code=409, detail='Email already exists') from exc


@app.delete('/api/employees/{employee_id}')
def delete_employee(employee_id: int):
    with database() as (connection, cursor):
        cursor.execute('DELETE FROM employees WHERE id=%s', (employee_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail='Employee not found')
        connection.commit()
        return {'message': 'Employee deleted'}


@app.post('/api/chat')
def chat(data: ChatRequest):
    api_key = os.getenv('OPENAI_API_KEY', '').strip()
    if not api_key or api_key == 'your_openai_api_key_here':
        raise HTTPException(status_code=503, detail='Configure OPENAI_API_KEY in your .env file')
    try:
        client = OpenAI(api_key=api_key, timeout=25.0, max_retries=1)
        response = client.responses.create(
            model=os.getenv('OPENAI_MODEL', 'gpt-4.1-mini'),
            instructions=('You are a concise and helpful assistant inside an Employee Management app. '
                          'Help users understand employee management, CRUD and dashboard usage. '
                          'You cannot see, access or change employee records; do not claim otherwise. '
                          'Never ask users for passwords or secrets.'),
            input=data.message,
            max_output_tokens=350,
        )
        return {'reply': response.output_text or 'I could not generate a response.'}
    except OpenAIError:
        logger.exception('OpenAI request failed')
        raise HTTPException(status_code=502, detail='AI service unavailable. Check your model, API key, quota and network.')
