import os
from typing import List, Dict
from pypdf import PdfReader
from docx import Document

def _read_pdf(path: str) -> str:
    reader = PdfReader(path)
    parts = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    return "\n".join(parts).strip()

def _read_docx(path: str) -> str:
    doc = Document(path)
    return "\n".join([p.text for p in doc.paragraphs if p.text is not None]).strip()

def _read_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read().strip()

def load_documents(folder_path: str) -> List[Dict]:
    docs: List[Dict] = []
    if not os.path.isdir(folder_path):
        raise FileNotFoundError(f"Docs folder not found: {folder_path}")

    for fname in os.listdir(folder_path):
        path = os.path.join(folder_path, fname)
        if not os.path.isfile(path):
            continue

        lower = fname.lower()
        try:
            if lower.endswith(".pdf"):
                text = _read_pdf(path)
            elif lower.endswith(".docx"):
                text = _read_docx(path)
            elif lower.endswith(".txt"):
                text = _read_txt(path)
            else:
                continue

            if text:
                docs.append({"source": fname, "text": text})
        except Exception as e:
            print(f"[WARN] Failed to read {fname}: {e}")

    return docs
