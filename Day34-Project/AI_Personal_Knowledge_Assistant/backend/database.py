"""MySQL persistence: document metadata and chat history. NO vector embeddings here."""
import os
from datetime import datetime, timezone
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy import create_engine, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

load_dotenv()


def utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


password = quote_plus(os.getenv("MYSQL_PASSWORD", ""))
username = quote_plus(os.getenv("MYSQL_USER", "root"))
host = os.getenv("MYSQL_HOST", "127.0.0.1")
port = os.getenv("MYSQL_PORT", "3306")
database = os.getenv("MYSQL_DATABASE", "ai_knowledge_assistant")
DATABASE_URL = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}?charset=utf8mb4"
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Document(Base):
    __tablename__ = "documents"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    saved_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_type: Mapped[str] = mapped_column(String(8), nullable=False)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)


class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("chat_sessions.id"), index=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    mode: Mapped[str] = mapped_column(String(20), default="rag")
    sources_json: Mapped[str] = mapped_column(Text, default="[]")
    tools_json: Mapped[str] = mapped_column(Text, default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    session: Mapped[ChatSession] = relationship(back_populates="messages")


def init_db():
    Base.metadata.create_all(bind=engine)


def save_exchange(session_id, question, answer, mode, sources, tools):
    import json
    with SessionLocal() as db:
        if db.get(ChatSession, session_id) is None:
            db.add(ChatSession(id=session_id))
            db.flush()
        db.add(ChatMessage(session_id=session_id, role="user", content=question, mode=mode))
        db.add(ChatMessage(session_id=session_id, role="assistant", content=answer,
                           mode=mode, sources_json=json.dumps(sources),
                           tools_json=json.dumps(tools)))
        db.commit()


def get_messages(session_id, limit=12):
    import json
    with SessionLocal() as db:
        rows = (db.query(ChatMessage)
                .filter(ChatMessage.session_id == session_id)
                .order_by(ChatMessage.id.desc()).limit(limit).all())
        return [{"role": row.role, "content": row.content, "mode": row.mode,
                 "sources": json.loads(row.sources_json or "[]"),
                 "tools_used": json.loads(row.tools_json or "[]")}
                for row in reversed(rows)]
