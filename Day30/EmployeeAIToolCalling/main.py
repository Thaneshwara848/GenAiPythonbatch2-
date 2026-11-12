
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error, IntegrityError
import os

from agent import ask_ai

# Load .env
load_dotenv()

app = FastAPI(title="Employee AI Management System")


# --------------------------------
# STEP 1: MYSQL CONNECTION
# --------------------------------
def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME", "employee_ai")
    )


# --------------------------------
# STEP 2: EMPLOYEE MODEL
# --------------------------------
class Employee(BaseModel):
    id: int = Field(gt=0)
    name: str = Field(min_length=2)
    age: int = Field(ge=18, le=60)
    salary: float = Field(gt=0)
    desig: str = Field(min_length=2)


# --------------------------------
# STEP 3: CHAT MODEL
# --------------------------------
class ChatRequest(BaseModel):
    question: str = Field(min_length=1)


# --------------------------------
# API 1: FRONTEND
# --------------------------------
@app.get("/", include_in_schema=False)
def home():
    return FileResponse(
        os.path.join(
            os.path.dirname(__file__),
            "index.html"
        )
    )


# --------------------------------
# API 2: GET ALL EMPLOYEES
# --------------------------------
@app.get("/getAllEmployees")
def get_all_employees():

    try:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:

                cursor.execute("SELECT * FROM Employee")
                employees = cursor.fetchall()

        return employees

    except Error:
        raise HTTPException(
            status_code=500,
            detail="Database Connection Error"
        )


# --------------------------------
# API 3: GET EMPLOYEE BY ID
# --------------------------------
@app.get("/getEmployeeById/{id}")
def get_employee_by_id(id: int):

    try:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:

                cursor.execute(
                    "SELECT * FROM Employee WHERE id = %s",
                    (id,)
                )

                employee = cursor.fetchone()

        if employee is None:
            raise HTTPException(
                status_code=404,
                detail="Employee Not Found"
            )

        return employee

    except Error:
        raise HTTPException(
            status_code=500,
            detail="Database Connection Error"
        )


# --------------------------------
# API 4: ADD EMPLOYEE
# --------------------------------
@app.post("/addEmployee", status_code=201)
def add_employee(emp: Employee):

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:

                sql = """
                INSERT INTO Employee
                (id, name, age, salary, desig)
                VALUES (%s, %s, %s, %s, %s)
                """

                values = (
                    emp.id,
                    emp.name,
                    emp.age,
                    emp.salary,
                    emp.desig
                )

                cursor.execute(sql, values)
                conn.commit()

        return {
            "message": "Employee Added Successfully"
        }

    except IntegrityError:
        raise HTTPException(
            status_code=400,
            detail="Employee ID Already Exists"
        )

    except Error:
        raise HTTPException(
            status_code=500,
            detail="Database Error"
        )


# --------------------------------
# API 5: DELETE EMPLOYEE
# --------------------------------
@app.delete("/deleteEmployee/{id}")
def delete_employee(id: int):

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:

                cursor.execute(
                    "DELETE FROM Employee WHERE id = %s",
                    (id,)
                )

                if cursor.rowcount == 0:
                    raise HTTPException(
                        status_code=404,
                        detail="Employee Not Found"
                    )

                conn.commit()

        return {
            "message": "Employee Deleted Successfully"
        }

    except Error:
        raise HTTPException(
            status_code=500,
            detail="Database Error"
        )


# --------------------------------
# API 6: AI TOOL CALLING
# --------------------------------
@app.post("/chat")
def chat(request: ChatRequest):

    try:
        answer = ask_ai(request.question)

        return {
            "answer": answer
        }

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="AI Service Error"
        )
