from typing import List, Dict

def chunk_text(text: str, meta: Dict, chunk_size: int = 800, overlap: int = 120) -> List[Dict]:
    chunks = []
    i = 0
    n = len(text)
    while i < n:
        j = min(i + chunk_size, n)
        chunk = text[i:j]
        chunks.append({"text": chunk, "meta": meta})
        i = j - overlap
        if i < 0: i = 0
        if j == n: break
    return chunks
