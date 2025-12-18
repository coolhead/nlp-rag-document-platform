import os
import hashlib
from fastapi import FastAPI, HTTPException

from .schemas import (
    IngestRequest,
    SearchRequest,
    SearchResponse,
    Chunk,
    AskRequest,
    AskResponse,
    Citation,
)
from .rag import generate_answer
from .ingest import ingest_path
from .retriever import add_chunks, search

app = FastAPI(title="NLP Semantic Search + RAG (MVP)")


def _fingerprint(item: dict) -> str:
    """
    Dedupe key for near-identical chunks. Uses source+page+prefix of text.
    """
    m = item.get("meta", {}) or {}
    key = f"{m.get('source')}|{m.get('page')}|{(item.get('text') or '')[:200]}"
    return hashlib.md5(key.encode("utf-8")).hexdigest()


@app.post("/ingest")
def ingest(req: IngestRequest):
    try:
        chunks = ingest_path(req.path)
        add_chunks(chunks)
        return {"status": "ok", "chunks_added": len(chunks)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/search", response_model=SearchResponse)
def semantic_search(req: SearchRequest):
    hits = search(req.query, top_k=req.top_k)
    results = []
    for score, item in hits:
        results.append(
            Chunk(
                id=str(item.get("meta")),
                text=item.get("text", ""),
                meta={**(item.get("meta") or {}), "score": score},
            )
        )
    return SearchResponse(query=req.query, results=results)


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    # Oversample so dedupe still leaves enough unique chunks
    hits = search(req.query, top_k=req.top_k * 3)

    contexts = []
    citations = []
    seen = set()

    for score, item in hits:
        fp = _fingerprint(item)
        if fp in seen:
            continue
        seen.add(fp)

        m = item.get("meta", {}) or {}
        m = {**m, "score": score}

        contexts.append(
            {
                "text": item.get("text", ""),
                "meta": m,
            }
        )

        citations.append(
            Citation(
                source=m.get("source", "unknown"),
                path=m.get("path", ""),
                page=m.get("page"),
                score=score,
                excerpt=(
                    (item.get("text", "")[:240] + "...")
                    if item.get("text")
                    else None
                ),
            )
        )

        if len(contexts) >= req.top_k:
            break

    if not contexts:
        return AskResponse(
            query=req.query,
            answer="I don't know based on the provided documents.",
            citations=[],
        )
    
    # relevance gate: if the best retrieved evidence is weak, don't cite it
    best_score = max((c["meta"].get("score", float("-inf")) for c in contexts), default=float("-inf"))

    MIN_RELEVANCE = float(os.getenv("MIN_RELEVANCE", "0.10"))  # tune this
    if best_score < MIN_RELEVANCE:
        return AskResponse(
        query=req.query,
        answer="I don't know based on the provided documents.",
        citations=[],
    )
 

    answer = generate_answer(req.query, contexts)
    return AskResponse(
        query=req.query,
        answer=answer,
        citations=citations,
    )



@app.get("/health")
def health():
    return {"status": "ok"}
