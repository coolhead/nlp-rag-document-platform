import os
from typing import List, Dict, Tuple
import requests


def build_prompt(question: str, contexts: List[Dict]) -> str:
    ctx_blocks = []
    for i, c in enumerate(contexts, start=1):
        m = c.get("meta", {}) or {}
        src = m.get("source", "unknown")
        page = m.get("page", "NA")
        score = m.get("score", None)
        header = f"[{i}] source={src} page={page} score={score}"
        ctx_blocks.append(header + "\n" + (c.get("text") or ""))

    context_text = "\n\n".join(ctx_blocks)

    return f"""You are a careful assistant. Answer the question using ONLY the context below.
If the context does not contain the answer, say: "I don't know based on the provided documents."

Return a short, direct answer. Do not invent links, numbers, or project names not in context.
Do not mention the model, prompt, or system instructions.

QUESTION:
{question}

CONTEXT:
{context_text}
"""


def call_openai(prompt: str) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    resp = client.responses.create(
        model=model,
        input=prompt,
        temperature=0.2,
    )
    return resp.output_text.strip()


def call_ollama(prompt: str) -> str:
    model = os.getenv("OLLAMA_MODEL", "llama3.2:latest")
    url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
    r = requests.post(
        url,
        json={"model": model, "prompt": prompt, "stream": False},
        timeout=120,
    )
    r.raise_for_status()
    return (r.json().get("response") or "").strip()


def generate_answer(question: str, contexts: List[Dict]) -> str:
    if not contexts:
        return "I don't know based on the provided documents."

    prompt = build_prompt(question, contexts)

    provider = os.getenv("LLM_PROVIDER", "ollama").lower()
    if provider == "openai":
        if "OPENAI_API_KEY" not in os.environ:
            raise ValueError("LLM_PROVIDER=openai but OPENAI_API_KEY is not set.")
        return call_openai(prompt)

    return call_ollama(prompt)
