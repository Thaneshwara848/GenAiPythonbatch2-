"""Run: uvicorn backend.main:app --reload --port 9999"""
import json
import os
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy import func

from backend.agent import agent_chat
from backend.database import (ChatMessage, ChatSession, Document, SessionLocal,
                              get_messages, init_db, save_exchange)
from backend.rag import answer_from_documents, index_document, remove_vectors

load_dotenv()
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "./uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED = {".pdf", ".docx", ".txt"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="AI Personal Knowledge Assistant", version="1.0.0",
              lifespan=lifespan)


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=5000)
    session_id: str | None = None


def validated_session_id(session_id):
    if not session_id:
        return str(uuid.uuid4())
    try:
        return str(uuid.UUID(session_id))
    except (ValueError, AttributeError) as exc:
        raise HTTPException(status_code=422, detail="Invalid session_id UUID") from exc


@app.get("/health")
def health():
    return {"status": "UP", "app": "AI Personal Knowledge Assistant"}


@app.post("/documents/upload", status_code=201)
async def upload_document(file: UploadFile = File(...)):
    filename = Path(file.filename or "").name
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED:
        raise HTTPException(400, "Only PDF, DOCX and TXT are allowed")
    max_bytes = int(os.getenv("MAX_UPLOAD_MB", "10")) * 1024 * 1024
    content = await file.read(max_bytes + 1)
    if not content or len(content) > max_bytes:
        raise HTTPException(413, "File empty or exceeds configured size limit")
    doc_id = str(uuid.uuid4())
    saved = UPLOAD_DIR / f"{doc_id}{ext}"
    try:
        # Parse / embed before writing persistent metadata; rollback vectors on failure.
        count = index_document(doc_id, filename, content, ext)
        saved.write_bytes(content)
        with SessionLocal() as db:
            db.add(Document(id=doc_id, filename=filename, saved_path=str(saved),
                            file_type=ext, chunk_count=count))
            db.commit()
        return {"document_id": doc_id, "filename": filename, "chunk_count": count}
    except Exception as exc:
        try:
            remove_vectors(doc_id)
        except Exception:
            pass
        saved.unlink(missing_ok=True)
        if isinstance(exc, (ValueError, UnicodeError)):
            raise HTTPException(400, str(exc)) from exc
        raise
    finally:
        await file.close()


@app.get("/documents")
def list_documents():
    with SessionLocal() as db:
        rows = db.query(Document).order_by(Document.uploaded_at.desc()).all()
        return [{"id": d.id, "filename": d.filename, "type": d.file_type,
                 "chunk_count": d.chunk_count,
                 "uploaded_at": d.uploaded_at.isoformat()} for d in rows]


@app.delete("/documents/{document_id}")
def delete_document(document_id: str):
    with SessionLocal() as db:
        doc = db.get(Document, document_id)
        if not doc:
            raise HTTPException(404, "Document not found")
        remove_vectors(doc.id)
        Path(doc.saved_path).unlink(missing_ok=True)
        db.delete(doc)
        db.commit()
    return {"deleted": document_id}


def run_chat(body: ChatRequest, mode: str):
    sid = validated_session_id(body.session_id)
    history = get_messages(sid)
    result = (answer_from_documents(body.question, history)
              if mode == "rag" else agent_chat(body.question, history))
    sources, tools = result.get("sources", []), result.get("tools_used", [])
    save_exchange(sid, body.question, result["answer"], mode, sources, tools)
    return {"session_id": sid, "mode": mode, "question": body.question,
            "answer": result["answer"], "sources": sources, "tools_used": tools}


@app.post("/chat/ask")
def ask(body: ChatRequest):
    return run_chat(body, "rag")


@app.post("/agent/chat")
def chat_agent(body: ChatRequest):
    return run_chat(body, "agent")


@app.get("/chat/sessions")
def list_chat_sessions():
    with SessionLocal() as db:
        sessions = db.query(ChatSession).order_by(ChatSession.created_at.desc()).all()
        return [{"session_id": s.id, "created_at": s.created_at.isoformat(),
                 "message_count": db.query(func.count(ChatMessage.id)).filter(
                     ChatMessage.session_id == s.id).scalar()}
                for s in sessions]


@app.get("/chat/history/{session_id}")
def chat_history(session_id: str):
    session_id = validated_session_id(session_id)
    with SessionLocal() as db:
        if db.get(ChatSession, session_id) is None:
            raise HTTPException(404, "Session not found")
    return {"session_id": session_id, "messages": get_messages(session_id, limit=1000)}
