
import os
from datetime import date
from pathlib import Path
from typing import Generator

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from fastapi.responses import FileResponse
from openai import OpenAI, OpenAIError
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import Column, Date, Integer, Numeric, String, create_engine, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, declarative_base, sessionmaker

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:root@localhost:3306/genAiB2?charset=utf8mb4",
)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

app = FastAPI(title="Employee Manager API", version="1.0.0")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


class Employee(Base):
    __tablename__ = "u"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(254), nullable=False, unique=True, index=True)
    department = Column(String(100), nullable=False)
    position = Column(String(120), nullable=False)
    phone = Column(String(40), nullable=True)
    salary = Column(Numeric(12, 2), nullable=False)
    hire_date = Column(Date, nullable=True)


class EmployeeFields(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    department: str = Field(min_length=2, max_length=100)
    position: str = Field(min_length=2, max_length=120)
    phone: str | None = Field(default=None, max_length=40)
    salary: float = Field(ge=0, le=9999999999.99)
    hire_date: date | None = None


class EmployeeCreate(EmployeeFields):
    pass


class EmployeeUpdate(EmployeeFields):
    pass


class EmployeeResponse(EmployeeFields):
    id: int


class ChatRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=4000)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def employee_response(employee: Employee) -> dict:
    return {
        "id": employee.id,
        "name": employee.name,
        "email": employee.email,
        "department": employee.department,
        "position": employee.position,
        "phone": employee.phone,
        "salary": float(employee.salary),
        "hire_date": employee.hire_date,
    }


def get_employee_or_404(db: Session, employee_id: int) -> Employee:
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@app.on_event("startup")
def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    return FileResponse(BASE_DIR / "index.html")


@app.post("/chat")
def chat(request: ChatRequest) -> dict[str, str]:
    if openai_client is None:
        raise HTTPException(status_code=503, detail="OpenAI API key is not configured")

    try:
        response = openai_client.responses.create(
            model=OPENAI_MODEL,
            instructions=(
                "You are a helpful assistant for employee management workflows. "
                "Give concise, practical guidance. You do not have access to this "
                "application's employee records or private employee data."
            ),
            input=request.prompt,
        )
        return {"question": request.prompt, "answer": response.output_text}
    except OpenAIError as exc:
        raise HTTPException(
            status_code=502,
            detail="The assistant service is unavailable. Check the OpenAI key and model settings.",
        ) from exc


@app.get("/api/employees", response_model=list[EmployeeResponse])
def list_employees(
    q: str | None = Query(default=None, max_length=120),
    department: str | None = Query(default=None, max_length=100),
    db: Session = Depends(get_db),
) -> list[dict]:
    query = db.query(Employee)
    if q and q.strip():
        term = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Employee.name.ilike(term),
                Employee.email.ilike(term),
                Employee.position.ilike(term),
            )
        )
    if department:
        query = query.filter(Employee.department == department)
    employees = query.order_by(Employee.name.asc()).all()
    return [employee_response(employee) for employee in employees]


@app.post(
    "/api/employees",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_employee(payload: EmployeeCreate, db: Session = Depends(get_db)) -> dict:
    employee = Employee(**payload.dict())
    db.add(employee)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already exists") from exc
    db.refresh(employee)
    return employee_response(employee)


@app.get("/api/employees/{employee_id}", response_model=EmployeeResponse)
def read_employee(employee_id: int, db: Session = Depends(get_db)) -> dict:
    return employee_response(get_employee_or_404(db, employee_id))


@app.put("/api/employees/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: int,
    payload: EmployeeUpdate,
    db: Session = Depends(get_db),
) -> dict:
    employee = get_employee_or_404(db, employee_id)
    for field, value in payload.dict().items():
        setattr(employee, field, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already exists") from exc
    db.refresh(employee)
    return employee_response(employee)


@app.delete("/api/employees/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(employee_id: int, db: Session = Depends(get_db)) -> Response:
    employee = get_employee_or_404(db, employee_id)
    db.delete(employee)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
