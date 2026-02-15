# src/retrieval/vector_retriever.py
"""
Chroma Vector Retriever (Semantic Search)

What it does:
- Loads Chroma persistent collection
- Embeds the user query using HuggingFace SentenceTransformer
- Searches Chroma for the most semantically similar chunks
- Returns a list of chunks with: chunk_id, text, source, score
"""

import os
from typing import List, Dict, Any
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

load_dotenv()

PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "storage/vectordb")
COLLECTION = os.getenv("CHROMA_COLLECTION", "helpdesk_chunks")
HF_EMBED_MODEL = os.getenv("HF_EMBED_MODEL", "sentence-transformers/all-mpnet-base-v2")
VECTOR_TOP_K = int(os.getenv("VECTOR_TOP_K", "8"))

_client = None
_collection = None
_model = None


def _init():
    global _client, _collection, _model
    os.makedirs(PERSIST_DIR, exist_ok=True)

    _client = chromadb.PersistentClient(
        path=PERSIST_DIR,
        settings=Settings(anonymized_telemetry=False)
    )
    _collection = _client.get_or_create_collection(name=COLLECTION)

    _model = SentenceTransformer(HF_EMBED_MODEL)


def vector_search(query: str, top_k: int = None) -> List[Dict[str, Any]]:
    q = (query or "").strip()
    if not q:
        return []

    if top_k is None:
        top_k = VECTOR_TOP_K

    if _client is None:
        _init()

    # Embed query (normalize so cosine works well)
    q_emb = _model.encode([q], convert_to_numpy=True, normalize_embeddings=True).tolist()[0]

    # NOTE: In newer Chroma versions, "ids" is NOT allowed in include.
    res = _collection.query(
        query_embeddings=[q_emb],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],  # ✅ removed "ids"
    )

    # Chroma returns ids always in res["ids"]
    ids = res.get("ids", [[]])[0]
    docs = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]
    dists = res.get("distances", [[]])[0]

    hits = []
    for cid, doc, meta, dist in zip(ids, docs, metas, dists):
        # distance smaller => better. Convert to a "bigger is better" score
        score = 1.0 / (1.0 + float(dist))
        hits.append({
            "chunk_id": cid,
            "text": doc,
            "source": (meta or {}).get("source", "unknown"),
            "score": score
        })

    return hits
