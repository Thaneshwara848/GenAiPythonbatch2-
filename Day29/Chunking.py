
text = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

CHUNK_SIZE = 5
CHUNK_OVERLAP = 0

def split_text(text):
    chunks = []
    start = 0

    while start < len(text):
        end = start + CHUNK_SIZE

        chunk = text[start:end]
        chunks.append(chunk)

        start = end - CHUNK_OVERLAP

    return chunks


result = split_text(text)

for i, chunk in enumerate(result, 1):
    print(f"Chunk {i}: {chunk}")
