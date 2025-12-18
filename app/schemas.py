from pydantic import BaseModel
from typing import List, Optional, Dict

class IngestRequest(BaseModel):
    path: str  # file or folder path

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

class Chunk(BaseModel):
    id: str
    text: str
    meta: Dict

class SearchResponse(BaseModel):
    query: str
    results: List[Chunk]

class AskRequest(BaseModel):
    query: str
    top_k: int = 5

class Citation(BaseModel):
    source: str
    path: str
    page: int | None = None
    score: float | None = None
    excerpt: str | None = None

class AskResponse(BaseModel):
    query: str
    answer: str
    citations: List[Citation]
