import os
import numpy as np
from .embeddings import embed_texts
from .store_faiss import FaissStore
from .settings import DATA_DIR

INDEX_PATH = os.path.join(DATA_DIR, "index", "faiss.index")
META_PATH  = os.path.join(DATA_DIR, "index", "chunks.json")

_store = None

def get_store(dim: int):
    global _store
    if _store is None:
        _store = FaissStore(dim=dim, index_path=INDEX_PATH, meta_path=META_PATH)
    return _store

def add_chunks(chunks):
    # keep only non-empty text chunks
    chunks = [c for c in chunks if c.get("text") and c["text"].strip()]
    if not chunks:
        raise ValueError("No valid text chunks found to index. Check PDFs in data/raw and extraction.")

    texts = [c["text"] for c in chunks]
    vecs = embed_texts(texts)

    # force 2D shape: (n, d)
    if vecs.ndim == 1:
        vecs = vecs.reshape(1, -1)

    store = get_store(dim=vecs.shape[1])
    store.add(vecs, chunks)
    store.persist()


def search(query: str, top_k: int = 5):
    qvec = embed_texts([query])
    store = get_store(dim=qvec.shape[1])
    hits = store.search(qvec, top_k=top_k)
    return hits
