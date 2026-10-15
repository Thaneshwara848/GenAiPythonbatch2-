from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, field_validator, model_validator
import mysql.connector

BASE_DIR = Path(__file__).resolve().parent


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="genaib2",
    )
def create_employee_table():
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS employee (
                eid INT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                age INT NOT NULL,
                salary DECIMAL(10, 2) NOT NULL,
                desig VARCHAR(100) NOT NULL
            )
            """
        )
        connection.commit()
    finally:
        cursor.close()
        connection.close()


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_employee_table()
    yield


app = FastAPI(title="Employee Management API", lifespan=lifespan)


class Employee(BaseModel):
    id: int
    name: str
    age: int
    salary: float
    designation: str

    @model_validator(mode="before")
    def validate_required_fields(cls, values):
        if isinstance(values, dict):
            error_messages = {
                "id": "ID is required and must be a positive integer.",
                "name": "Name is required and cannot be blank.",
                "age": "Age is required and must be greater than 18 and less than 60.",
                "salary": "Salary is required and must be greater than 25,000.",
                "designation": "Designation is required and cannot be blank.",
            }
            for field_name, error_message in error_messages.items():
                if field_name not in values or values[field_name] is None:
                    raise ValueError(error_message)
        return values

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("ID must be a positive integer.")
        return value

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Name is required and cannot be blank.")
        return value.strip()

    @field_validator("age")
    @classmethod
    def validate_age(cls, value: int) -> int:
        if not 18 < value < 60:
            raise ValueError("Age must be greater than 18 and less than 60.")
        return value

    @field_validator("salary")
    @classmethod
    def validate_salary(cls, value: float) -> float:
        if value <= 25000:
            raise ValueError("Salary must be greater than 25,000.")
        return value

    @field_validator("designation", mode="before")
    @classmethod
    def validate_designation(cls, value: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Designation is required and cannot be blank.")
        return value.strip()

@app.get("/")
def home():
    return FileResponse(BASE_DIR / "index.html")


@app.get("/health")
def test_endpoint():
    return {"message": "FastAPI is working!"}


@app.get("/employees")
def get_employees():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT eid AS id, name, age, salary, desig AS designation
            FROM employee
            ORDER BY eid
            """
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


@app.get("/employees/{employee_id}")
def get_employee(employee_id: int):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT eid AS id, name, age, salary, desig AS designation
            FROM employee
            WHERE eid = %s
            """,
            (employee_id,),
        )
        employee = cursor.fetchone()
        if employee is None:
            raise HTTPException(status_code=404, detail="Employee not found")
        return employee
    finally:
        cursor.close()
        connection.close()


@app.post("/employees", status_code=201)
def create_employee(employee: Employee):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT eid FROM employee WHERE eid = %s", (employee.id,))
        if cursor.fetchone() is not None:
            raise HTTPException(status_code=409, detail="Employee ID already exists")

        cursor.execute(
            """
            INSERT INTO employee (eid, name, age, salary, desig)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                employee.id,
                employee.name,
                employee.age,
                employee.salary,
                employee.designation,
            ),
        )
        connection.commit()
        return employee
    finally:
        cursor.close()
        connection.close()


@app.put("/employees/{employee_id}")
def update_employee(employee_id: int, employee: Employee):
    if employee.id != employee_id:
        raise HTTPException(
            status_code=400,
            detail="Employee ID in the URL must match the request body",
        )

    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT eid FROM employee WHERE eid = %s", (employee_id,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Employee not found")

        cursor.execute(
            """
            UPDATE employee
            SET name = %s, age = %s, salary = %s, desig = %s
            WHERE eid = %s
            """,
            (
                employee.name,
                employee.age,
                employee.salary,
                employee.designation,
                employee_id,
            ),
        )
        connection.commit()
        return employee
    finally:
        cursor.close()
        connection.close()


@app.delete("/employees/{employee_id}")
def delete_employee(employee_id: int):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM employee WHERE eid = %s", (employee_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Employee not found")
        connection.commit()
        return {"message": "Employee deleted successfully"}
    finally:
        cursor.close()
        connection.close()