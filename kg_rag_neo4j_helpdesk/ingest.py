import os
import hashlib
from tqdm import tqdm
from dotenv import load_dotenv

from src.ingest.loaders import load_documents
from src.ingest.chunker import chunk_text
from src.ingest.kg_extractor import extract_triples
from src.ingest.neo4j_builder import ensure_schema, upsert_document, upsert_chunk, add_triples, close_driver
from src.ingest.vector_builder import add_chunks_to_vector_db

load_dotenv()

DOCS_DIR = "data/docs"
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1200"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))

def _doc_id(source: str) -> str:
    return hashlib.sha256(source.encode("utf-8")).hexdigest()[:16]

def _chunk_id(doc_id: str, idx: int) -> str:
    return f"{doc_id}_chunk_{idx:04d}"

def main():
    ensure_schema()

    docs = load_documents(DOCS_DIR)
    if not docs:
        print(f"[INFO] No documents found in {DOCS_DIR}. Add files and re-run ingest.py")
        return

    all_vector_items = []

    for d in docs:
        source = d["source"]
        text = d["text"]
        doc_id = _doc_id(source)

        upsert_document(doc_id=doc_id, source=source)

        chunks = chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP)
        print(f"\n[INFO] {source}: {len(chunks)} chunks")

        for i, ch in enumerate(tqdm(chunks, desc=f"Ingesting {source}", unit="chunk")):
            cid = _chunk_id(doc_id, i)

            upsert_chunk(chunk_id=cid, doc_id=doc_id, source=source, text=ch, position=i)

            triples = extract_triples(ch, source=source, chunk_id=cid)
            add_triples(triples, chunk_id=cid, doc_id=doc_id, source=source)

            all_vector_items.append({
                "id": cid,
                "text": ch,
                "metadata": {
                    "source": source,
                    "doc_id": doc_id,
                    "chunk_id": cid,
                    "position": i
                }
            })

    # Add to Chroma in one go (fast)
    add_chunks_to_vector_db(all_vector_items)

    close_driver()
    print("\n✅ Hybrid ingestion complete: Neo4j graph + Chroma vectors built successfully.")

if __name__ == "__main__":
    main()
