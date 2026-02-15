import os
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

ENABLE_RERANK = os.getenv("ENABLE_RERANK", "true").lower() == "true"
RERANK_MODEL = os.getenv("HF_RERANK_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
RERANK_TOP_N = int(os.getenv("RERANK_TOP_N", "12"))

_reranker = None

def _init():
    global _reranker
    from sentence_transformers import CrossEncoder
    _reranker = CrossEncoder(RERANK_MODEL)

def rerank(query: str, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not ENABLE_RERANK:
        return chunks

    if not chunks:
        return []

    global _reranker
    if _reranker is None:
        _init()

    top = chunks[:RERANK_TOP_N]
    pairs = [(query, c.get("text", "")) for c in top]
    scores = _reranker.predict(pairs).tolist()

    for c, s in zip(top, scores):
        c["rerank_score"] = float(s)

    top.sort(key=lambda x: x.get("rerank_score", 0.0), reverse=True)
    # append the rest
    return top + chunks[RERANK_TOP_N:]
