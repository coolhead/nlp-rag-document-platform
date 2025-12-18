from sentence_transformers import SentenceTransformer
from .settings import EMBED_MODEL
import numpy as np


_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBED_MODEL)
    return _model

def embed_texts(texts):
    model = get_model()
    vecs = model.encode(texts, normalize_embeddings=True)

    vecs = np.array(vecs)
    if vecs.ndim == 1:
        vecs = vecs.reshape(1, -1)
    return vecs
