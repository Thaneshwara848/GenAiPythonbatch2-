
import pymupdf
import chromadb
import hashlib
from docx import Document
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# Load API Key
load_dotenv()
client = OpenAI()


# STEP 1: DOCUMENT TO TEXT
def extract_text(filename):

    ext = Path(filename).suffix.lower()

    if ext == ".txt":
        with open(filename, "r", encoding="utf-8") as file:
            return file.read()

    elif ext == ".pdf":
        with pymupdf.open(filename) as pdf:
            return "\n".join(page.get_text() for page in pdf)

    elif ext == ".docx":
        doc = Document(filename)
        return "\n".join(p.text for p in doc.paragraphs)

    else:
        raise ValueError("Only PDF, DOCX, TXT supported")


# STEP 2: TEXT TO CHUNKS
def split_text(text):

    words = text.split()
    chunks = []

    CHUNK_SIZE = 10

    for i in range(0, len(words), CHUNK_SIZE):
        chunk = " ".join(words[i:i + CHUNK_SIZE])
        chunks.append(chunk)

    return chunks


# STEP 3: CHUNK TO EMBEDDING
def get_embedding(chunk):

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=chunk
    )

    return response.data[0].embedding


# STEP 4: CONNECT TO VECTOR DATABASE
db = chromadb.PersistentClient(path="./vector_db")

collection = db.get_or_create_collection(
    name="rag_documents",
    embedding_function=None
)


# MAIN PROGRAM
filename = input("Enter Document Name: ")

# Extract Text
text = extract_text(filename)

print("\n===== EXTRACTED TEXT =====")
print(text)

# Chunking
chunks = split_text(text)

print("\n===== CHUNKS =====")
for i, chunk in enumerate(chunks, 1):
    print(f"Chunk {i}: {chunk}")


# Embeddings and Vector DB Storage
print("\n===== EMBEDDINGS AND VECTOR DB =====")

# Create stable IDs for this document
document_id = hashlib.sha256(
    Path(filename).resolve().as_posix().encode()
).hexdigest()[:16]

for i, chunk in enumerate(chunks, 1):

    embedding = get_embedding(chunk)

    print(f"\nChunk {i}: {chunk}")
    print("Embedding:", embedding)
    print("Total Dimensions:", len(embedding))

    # Store into ChromaDB
    collection.upsert(
        ids=[f"{document_id}_chunk_{i}"],
        documents=[chunk],
        embeddings=[embedding],
        metadatas=[{
            "filename": Path(filename).name,
            "chunk_number": i
        }]
    )

    print("Stored Successfully in ChromaDB!")


# STEP 5: VERIFY STORED RECORDS
print("\n===== VECTOR DATABASE RECORDS =====")

results = collection.get()

for record_id, document in zip(
    results["ids"], results["documents"]
):
    print("ID:", record_id)
    print("Text:", document)
    print("----------------------------")

print("Total Stored Records:", collection.count())
