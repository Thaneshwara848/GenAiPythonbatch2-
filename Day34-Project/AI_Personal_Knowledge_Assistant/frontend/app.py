"""Run: streamlit run frontend/app.py"""
import os
import uuid

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
API = os.getenv("API_BASE_URL", "http://127.0.0.1:9999").rstrip("/")

st.set_page_config(page_title="AI Knowledge Assistant", page_icon="📚", layout="wide")
st.title("📚 AI Personal Knowledge Assistant")
st.caption("Streamlit • FastAPI • MySQL chat history • ChromaDB embeddings • RAG + Single AI Agent")


def api(method, path, **kwargs):
    try:
        response = requests.request(method, f"{API}{path}", timeout=180, **kwargs)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        detail = ""
        if getattr(exc, "response", None) is not None:
            detail = exc.response.text[:600]
        st.error(f"API error: {exc} {detail}")
        return None


if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("⚙️ Chat Settings")
    mode = st.radio("Mode", ["RAG", "Single Agent"], horizontal=False)
    if st.button("➕ New chat", use_container_width=True):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()
    st.caption("Chat history is stored in MySQL after the first message.")
    sessions = api("GET", "/chat/sessions") or []
    choices = {f"{s['created_at']} | {s['session_id'][:8]} | {s['message_count']} msgs": s["session_id"]
               for s in sessions}
    if choices:
        selected = st.selectbox("Previous chats", ["Select a chat"] + list(choices))
        if selected != "Select a chat" and st.button("Load selected chat"):
            sid = choices[selected]
            data = api("GET", f"/chat/history/{sid}")
            if data:
                st.session_state.session_id = sid
                st.session_state.messages = data["messages"]
                st.rerun()
    st.divider()
    st.write("Session ID:")
    st.code(st.session_state.session_id)

upload_tab, documents_tab, chat_tab = st.tabs(["📤 Upload", "📄 Documents", "💬 Chat"])

with upload_tab:
    st.subheader("Upload and index documents")
    uploaded = st.file_uploader("Select PDF, DOCX or TXT (max 10 MB)", type=["pdf", "docx", "txt"])
    if uploaded and st.button("Upload & create embeddings", type="primary"):
        with st.spinner("Extracting, chunking and embedding document..."):
            result = api("POST", "/documents/upload", files={"file": (uploaded.name, uploaded.getvalue())})
        if result:
            st.success(f"Indexed {result['filename']} in {result['chunk_count']} chunks")
            st.json(result)
    st.info("Text-based PDFs work directly. Scanned/image-only PDFs need OCR, which is not enabled in this starter version.")

with documents_tab:
    st.subheader("Uploaded documents")
    docs = api("GET", "/documents")
    if docs is not None:
        if not docs:
            st.info("No documents uploaded yet.")
        for d in docs:
            col1, col2, col3 = st.columns([5, 2, 2])
            col1.write(f"**{d['filename']}** — {d['type']}")
            col2.write(f"{d['chunk_count']} chunks")
            with col3:
                if st.button("Delete", key=f"delete_{d['id']}"):
                    st.session_state.confirm_delete = d['id']
            if st.session_state.get("confirm_delete") == d["id"]:
                st.warning(f"Permanently delete {d['filename']} and its vectors?")
                if st.button("Yes, permanently delete", key=f"confirm_{d['id']}"):
                    result = api("DELETE", f"/documents/{d['id']}")
                    if result:
                        st.session_state.confirm_delete = None
                        st.rerun()

with chat_tab:
    st.subheader("Ask about your uploaded documents")
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
            if m.get("sources"):
                with st.expander("📎 Sources"):
                    for s in m["sources"]:
                        page = f"page {s['page']}" if s.get("page") else "no page number"
                        st.write(f"• {s['filename']} ({page}), chunk {s['chunk_index']}")
            if m.get("tools_used"):
                st.caption("Tools used: " + ", ".join(m["tools_used"]))

    question = st.chat_input("E.g., How many casual leaves are allowed?")
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        endpoint = "/agent/chat" if mode == "Single Agent" else "/chat/ask"
        with st.spinner("Searching documents and generating answer..."):
            result = api("POST", endpoint, json={
                "question": question, "session_id": st.session_state.session_id})
        if result:
            st.session_state.session_id = result["session_id"]
            st.session_state.messages.append({"role": "assistant", "content": result["answer"],
                                              "sources": result["sources"],
                                              "tools_used": result["tools_used"]})
        else:
            st.session_state.messages.pop()  # Failed request was not saved in MySQL
        st.rerun()
