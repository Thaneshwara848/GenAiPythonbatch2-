import fitz
from docx import Document
from pathlib import Path

def extract_text(filename):
    extension = Path(filename).suffix.lower()

    if extension == ".pdf":
        with fitz.open(filename) as pdf:
            text = "\n".join(page.get_text() for page in pdf)
    
    elif extension == ".docx":
        doc = Document(filename)
        text = "\n".join(para.text for para in doc.paragraphs)

    
    elif extension == ".txt":
        text = Path(filename).read_text(encoding="utf-8")
    
    else:
        return "Unsupported file format"
    
    return text
# Main Program
filename = input("Enter document filename: ")
result = extract_text(filename)
print("\n===== EXTRACTED TEXT =====")
print(result)

