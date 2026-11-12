
import json
import requests
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()
BASE_URL = "http://127.0.0.1:9999"


# STEP 1: Python Tool Functions

def get_all_employees():
    response = requests.get(
        BASE_URL + "/getAllEmployees",
        timeout=10
    )
    return {
        "status": response.status_code,
        "data": response.json()
    }


def get_employee_by_id(id):
    response = requests.get(
        BASE_URL + f"/getEmployeeById/{id}",
        timeout=10
    )
    return {
        "status": response.status_code,
        "data": response.json()
    }


def add_employee(id, name, age, salary, desig):
    emp = {
        "id": id,
        "name": name,
        "age": age,
        "salary": salary,
        "desig": desig
    }

    response = requests.post(
        BASE_URL + "/addEmployee",
        json=emp,
        timeout=10
    )
    return {
        "status": response.status_code,
        "data": response.json()
    }


def delete_employee(id):
    response = requests.delete(
        BASE_URL + f"/deleteEmployee/{id}",
        timeout=10
    )
    return {
        "status": response.status_code,
        "data": response.json()
    }

def delete_all_employees():
    response = requests.delete(
        BASE_URL + "/deleteAllEmployees",
        timeout=10
    )
    return {
        "status": response.status_code,
        "data": response.json()
    }

# STEP 2: Register Tools with OpenAI

tools = [
    {
        "type": "function",
        "name": "get_all_employees",
        "description": "Retrieve all employees from MySQL",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False
        },
        "strict": True
    },
    {
        "type": "function",
        "name": "get_employee_by_id",
        "description": "Retrieve employee using employee ID",
        "parameters": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"}
            },
            "required": ["id"],
            "additionalProperties": False
        },
        "strict": True
    },
    {
        "type": "function",
        "name": "add_employee",
        "description": "Add an employee to MySQL only when the user explicitly requests it and provides all fields",
        "parameters": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "age": {"type": "integer"},
                "salary": {"type": "number"},
                "desig": {"type": "string"}
            },
            "required": [
                "id", "name", "age","salary", "desig"
            ],
            "additionalProperties": False
        },
        "strict": True
    },
    {
    
        "type": "function",
        "name": "delete_employee",
        "description": "Delete an employee by ID only when the user explicitly requests deletion",
        "parameters": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"}
            },
            "required": ["id"],
            "additionalProperties": False
        },
        "strict": True
    },
    {
    "type": "function",
    "name": "delete_all_employees",
    "description": "Delete all employee records from MySQL only when the user explicitly requests to delete all employees. This is a permanent operation.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False
    },
    "strict": True
}
]


# STEP 3: Tool Execution

def execute_tool(name, args):

    print("Selected Tool:", name)
    print("Arguments:", args)

    if name == "get_all_employees":
        return get_all_employees()

    if name == "get_employee_by_id":
        return get_employee_by_id(args["id"])

    if name == "add_employee":
        return add_employee(**args)

    if name == "delete_employee":
        return delete_employee(args["id"])

    if name == "delete_all_employees":
        return delete_all_employees()

    return {"error": "Unknown Tool"}


# STEP 4: Ask AI

def ask_ai(question):

    messages = [
        {"role": "user", "content": question}
    ]

    instructions = """
    You are an Employee Management Assistant.
    Use the provided tools for employee data.
    Do not invent employee records or salaries.
    Only add an employee when the user explicitly
    requests insertion and supplies id, name,
    age, salary and designation.
    Only delete an employee when the user explicitly
    requests deletion and supplies the employee ID.
    Only delete all employees when the user explicitly
    requests deletion of all employee records. Do not
    ask for an employee ID for this request. The user
    has already confirmed destructive requests in the UI;
    do not ask for a second confirmation.
    If the requested deletion scope is ambiguous, ask
    the user to clarify before deleting anything.
    If details are missing, ask for them.
    Never invent missing employee fields.
    Report API errors accurately.
    """

    # Limit execution to three rounds
    for _ in range(3):

        response = client.responses.create(
            model="gpt-4.1-mini",
            instructions=instructions,
            input=messages,
            tools=tools,
            parallel_tool_calls=False
        )

        messages.extend(response.output)

        calls = [
            item for item in response.output
            if item.type == "function_call"
        ]

        if not calls:
            return response.output_text

        for item in calls:

            args = json.loads(item.arguments)

            try:
                result = execute_tool(item.name, args)
            except requests.RequestException:
                result = {"error": "Employee API unavailable"}

            messages.append({
                "type": "function_call_output",
                "call_id": item.call_id,
                "output": json.dumps(result)
            })

    return "Tool-call limit reached. Please try again."
