text = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
CHUNK_SIZE = 5          # 
CHUNK_OVERLAP = 0
def split_text(text):
    text = " ".join(text.split())
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk)
        if end == len(text):
            break
        start = end - CHUNK_OVERLAP
    return chunks

# Call function
result = split_text(text)

# Print chunks
for i, chunk in enumerate(result, start=1):
    print(f"Chunk {i}: {chunk}")