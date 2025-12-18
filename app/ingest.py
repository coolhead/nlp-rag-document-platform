import os
from typing import List, Dict
from pypdf import PdfReader
from .cleaning import clean_text
from .chunking import chunk_text

def read_pdf(path: str) -> List[Dict]:
    reader = PdfReader(path)
    out: List[Dict] = []

    for idx, page in enumerate(reader.pages):
        txt = page.extract_text() or ""
        txt = clean_text(txt)
        if not txt.strip():
            continue

        meta = {"source": os.path.basename(path), "path": path, "page": idx + 1}
        out.extend(chunk_text(txt, meta))

    return out

def ingest_path(path: str) -> List[Dict]:
    if os.path.isdir(path):
        docs: List[Dict] = []
        for root, _, files in os.walk(path):
            for f in files:
                fp = os.path.join(root, f)
                if f.lower().endswith(".pdf"):
                    docs.extend(read_pdf(fp))
        return docs

    if path.lower().endswith(".pdf"):
        return read_pdf(path)

    raise ValueError("Only PDF supported in MVP. Add DOCX/TXT later.")
