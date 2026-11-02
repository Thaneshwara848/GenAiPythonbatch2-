
import pymupdf
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


# STEP 3: CHUNK TO EMBEDDING        chhunks ge number assign aguthe ...!  yar ? 
def get_embedding(chunk):

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=chunk
    )

    return response.data[0].embedding




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

# Embeddings
print("\n===== EMBEDDINGS =====")

for i, chunk in enumerate(chunks, 1):

    embedding = get_embedding(chunk)

    print(f"\nChunk {i}: {chunk}")
    print("Embedding:", embedding)
    print("Total Dimensions:", len(embedding))
