import os, json
import numpy as np
import faiss

class FaissStore:
    def __init__(self, dim: int, index_path: str, meta_path: str):
        self.dim = dim
        self.index_path = index_path
        self.meta_path = meta_path
        self.index = faiss.IndexFlatIP(dim)
        self.meta = []

        if os.path.exists(index_path) and os.path.exists(meta_path):
            self.index = faiss.read_index(index_path)
            with open(meta_path, "r", encoding="utf-8") as f:
                self.meta = json.load(f)

    def add(self, vectors: np.ndarray, chunks):
        self.index.add(vectors.astype("float32"))
        self.meta.extend(chunks)

    def search(self, qvec: np.ndarray, top_k: int = 5):
        D, I = self.index.search(qvec.astype("float32"), top_k)
        hits = []
        for score, idx in zip(D[0], I[0]):
            if idx == -1: 
                continue
            item = self.meta[idx]
            hits.append((float(score), item))
        return hits

    def persist(self):
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(self.meta, f, ensure_ascii=False, indent=2)
