import os
from typing import List, Dict
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

load_dotenv()

PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "storage/vectordb")
COLLECTION = os.getenv("CHROMA_COLLECTION", "helpdesk_chunks")
HF_EMBED_MODEL = os.getenv("HF_EMBED_MODEL", "sentence-transformers/all-mpnet-base-v2")

_client = None
_collection = None
_model = None

def _init():
    global _client, _collection, _model
    os.makedirs(PERSIST_DIR, exist_ok=True)

    _client = chromadb.PersistentClient(path=PERSIST_DIR, settings=Settings(anonymized_telemetry=False))
    _collection = _client.get_or_create_collection(name=COLLECTION)

    _model = SentenceTransformer(HF_EMBED_MODEL)

def add_chunks_to_vector_db(items: List[Dict]):
    """
    items: [{"id": chunk_id, "text": chunk_text, "metadata": {...}}, ...]
    """
    if not items:
        return

    if _client is None:
        _init()

    ids = [x["id"] for x in items]
    texts = [x["text"] for x in items]
    metas = [x["metadata"] for x in items]

    embeddings = _model.encode(texts, convert_to_numpy=True, normalize_embeddings=True).tolist()

    # Chroma will error if ids exist; safe approach: upsert via delete+add
    # (simple and reliable for a local project)
    try:
        _collection.delete(ids=ids)
    except Exception:
        pass

    _collection.add(ids=ids, documents=texts, metadatas=metas, embeddings=embeddings)

def reset_collection():
    if _client is None:
        _init()
    try:
        _client.delete_collection(name=COLLECTION)
    except Exception:
        pass
    _client.get_or_create_collection(name=COLLECTION)
