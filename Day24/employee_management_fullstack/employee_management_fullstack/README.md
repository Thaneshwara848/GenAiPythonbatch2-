# Employee Management – FastAPI + MySQL + OpenAI

## Requirements
Python 3.11+, MySQL Server 8+, an OpenAI API key for chat.

## Run on Windows (PowerShell / VS Code terminal)

1. Extract the ZIP and open the `employee_management_fullstack` folder in VS Code.
2. In MySQL Workbench, open and execute `schema.sql` to create the database and table.
3. Edit `.env` and set `DB_PASSWORD` and `OPENAI_API_KEY`.
4. Run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --port 9999
```

If PowerShell prevents activation, use `\.venv\Scripts\python.exe -m pip install -r requirements.txt` and `\.venv\Scripts\python.exe -m uvicorn main:app --reload --port 9999` instead.

Go to http://127.0.0.1:9999/ . API Swagger docs: http://127.0.0.1:9999/docs .

## Endpoints

- GET `/api/health` – database status
- GET `/api/employees` – all employees
- GET `/api/employees/{id}` – single employee
- POST `/api/employees` – add employee
- PUT `/api/employees/{id}` – update employee
- DELETE `/api/employees/{id}` – delete employee
- POST `/api/chat` – AI assistant

Example POST `/api/employees` body:
```json
{"name":"Asha Kumar","age":28,"email":"asha@example.com","department":"Engineering","designation":"Developer","salary":65000,"status":"Active"}
```

## Important

- `.env` is ignored by Git; keep the API key and DB credentials private.
- Chatbot answers general questions only. It does **not** read or modify the employee database.
- No login/roles are included. This is a local training/demo app; add authentication, authorization, rate limiting, CSRF considerations, TLS, backups and secrets management before deploying publicly.
- OpenAI requests incur API charges, separate from ChatGPT subscription.
- `OPENAI_MODEL` defaults to `gpt-4.1-mini`; replace it with a model available to your API project as needed.
