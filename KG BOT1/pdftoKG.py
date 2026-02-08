import os
import json
import re
from dotenv import load_dotenv
load_dotenv()

from neo4j import GraphDatabase
from pypdf import PdfReader

from langchain_openai import ChatOpenAI

# ----------------------------
# CONFIG (edit these)
# ----------------------------
PDF_PATH = "Assignment.pdf"  # <-- change to your PDF filename/path
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password123"

MODEL_NAME = "gpt-3.5-turbo"  # keep simple for now


# ----------------------------
# Helpers: PDF text + chunking
# ----------------------------
def read_pdf_text(path: str) -> str:
    reader = PdfReader(path)
    pages = []
    for i, page in enumerate(reader.pages):
        txt = page.extract_text() or ""
        # Normalize whitespace
        txt = re.sub(r"\s+", " ", txt).strip()
        if txt:
            pages.append(f"[PAGE {i+1}] {txt}")
    return "\n\n".join(pages)


def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 200):
    """
    Simple chunker: creates overlapping chunks so we don't break meaning.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
        if start < 0:
            start = 0
        if end == len(text):
            break
    return chunks


# ----------------------------
# LLM extractor (triples)
# ----------------------------
def extract_triples(llm, chunk: str):
    """
    Returns:
      - entities: [{name, type}]
      - relations: [{source, relation, target}]
    """
    prompt = f"""
You are extracting a knowledge graph from text.

Return ONLY valid JSON with this exact format:
{{
  "entities": [{{"name": "...", "type": "PERSON|ORG|PRODUCT|CONCEPT|LOCATION|DATE|OTHER"}}],
  "relations": [{{"source": "...", "relation": "RELATION_NAME", "target": "..."}}]
}}

Rules:
- Keep entity names short but specific (no long sentences).
- relation should be uppercase with underscores, like WORKS_FOR, HAS_POLICY, CAUSES, PART_OF, LOCATED_IN, OWNS, DEFINES, REQUIRES, IMPACTS.
- Only extract relations that are supported by the text.
- If nothing clear, return empty arrays.

TEXT:
\"\"\"{chunk}\"\"\"
"""

    resp = llm.invoke(prompt).content

    # Try to locate JSON if model adds extra text (shouldn't, but safe)
    json_text = resp.strip()
    if not json_text.startswith("{"):
        m = re.search(r"\{.*\}", json_text, re.DOTALL)
        if m:
            json_text = m.group(0)

    data = json.loads(json_text)
    entities = data.get("entities", [])
    relations = data.get("relations", [])
    return entities, relations
def to_str_list(x):
    """
    Accepts string or list; returns a clean list of strings.
    """
    if x is None:
        return []
    if isinstance(x, str):
        s = x.strip()
        return [s] if s else []
    if isinstance(x, list):
        out = []
        for item in x:
            if isinstance(item, str):
                s = item.strip()
                if s:
                    out.append(s)
        return out
    # fallback: convert other types to string
    s = str(x).strip()
    return [s] if s else []


# ----------------------------
# Neo4j writer
# ----------------------------
def to_str_list(x):
    """
    Accepts string or list; returns a clean list of strings.
    """
    if x is None:
        return []
    if isinstance(x, str):
        s = x.strip()
        return [s] if s else []
    if isinstance(x, list):
        out = []
        for item in x:
            if isinstance(item, str):
                s = item.strip()
                if s:
                    out.append(s)
        return out
    s = str(x).strip()
    return [s] if s else []


def upsert_graph(driver, doc_id: str, doc_name: str, chunk_id: str, chunk_text: str, entities, relations):
    """
    Writes:
    (Document)-[:HAS_CHUNK]->(Chunk)
    (Chunk)-[:MENTIONS]->(Entity)
    (Chunk)-[:SUPPORTS]->(Fact)
    (Fact)-[:SOURCE]->(Entity)
    (Fact)-[:TARGET]->(Entity)
    Also stores direct (Entity)-[:REL]->(Entity) edges for traversal.
    """
    def sanitize_rel(rel: str) -> str:
        rel = (rel or "").upper().strip()
        rel = re.sub(r"[^A-Z0-9_]", "_", rel)
        if not rel or rel[0].isdigit():
            rel = "RELATED_TO"
        return rel

    with driver.session() as session:
        # 1) Document + Chunk
        session.run(
            """
            MERGE (d:Document {id: $doc_id})
            SET d.name = $doc_name
            MERGE (c:Chunk {id: $chunk_id})
            SET c.text = $chunk_text
            MERGE (d)-[:HAS_CHUNK]->(c)
            """,
            doc_id=doc_id,
            doc_name=doc_name,
            chunk_id=chunk_id,
            chunk_text=chunk_text
        )

        # 2) Entities + mentions
        for e in entities or []:
            name = (e.get("name") or "").strip() if isinstance(e, dict) else ""
            etype = (e.get("type") or "OTHER").strip().upper() if isinstance(e, dict) else "OTHER"
            if not name:
                continue

            session.run(
                """
                MERGE (en:Entity {name: $name})
                SET en.type = $etype
                WITH en
                MATCH (c:Chunk {id: $chunk_id})
                MERGE (c)-[:MENTIONS]->(en)
                """,
                name=name,
                etype=etype,
                chunk_id=chunk_id
            )

        # 3) Relations -> Fact nodes + direct entity edges
        for r in relations or []:
            if not isinstance(r, dict):
                continue

            rel = sanitize_rel(r.get("relation") or "RELATED_TO")
            src_list = to_str_list(r.get("source"))
            tgt_list = to_str_list(r.get("target"))

            if not src_list or not tgt_list:
                continue

            for src in src_list:
                for tgt in tgt_list:
                    fact_id = f"{chunk_id}::{src}::{rel}::{tgt}"

                    session.run(
                        """
                        MERGE (a:Entity {name: $src})
                        MERGE (b:Entity {name: $tgt})

                        MERGE (f:Fact {id: $fact_id})
                        SET f.relation = $rel

                        MERGE (f)-[:SOURCE]->(a)
                        MERGE (f)-[:TARGET]->(b)

                        WITH f
                        MATCH (c:Chunk {id: $chunk_id})
                        MERGE (c)-[:SUPPORTS]->(f)
                        """,
                        src=src,
                        tgt=tgt,
                        rel=rel,
                        fact_id=fact_id,
                        chunk_id=chunk_id
                    )

                    # direct edge for traversal
                    cypher2 = f"""
                    MERGE (a:Entity {{name: $src}})
                    MERGE (b:Entity {{name: $tgt}})
                    MERGE (a)-[:{rel}]->(b)
                    """
                    session.run(cypher2, src=src, tgt=tgt)






def main():
    if not os.path.exists(PDF_PATH):
        raise FileNotFoundError(f"PDF not found: {PDF_PATH}")

    # 1) Read PDF
    full_text = read_pdf_text(PDF_PATH)
    if not full_text.strip():
        raise ValueError("No extractable text found. If this is a scanned PDF, we need OCR (next step).")

    # 2) Chunk
    chunks = chunk_text(full_text, chunk_size=1200, overlap=200)
    print(f"Loaded PDF text. Created {len(chunks)} chunks.")

    # 3) LLM
    llm = ChatOpenAI(model=MODEL_NAME)

    # 4) Neo4j
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    doc_id = os.path.basename(PDF_PATH)
    doc_name = os.path.basename(PDF_PATH)

    for i, ch in enumerate(chunks, start=1):
        chunk_id = f"{doc_id}::chunk::{i}"

        # Extract KG
        entities, relations = extract_triples(llm, ch)

        # Write to Neo4j
        upsert_graph(
            driver=driver,
            doc_id=doc_id,
            doc_name=doc_name,
            chunk_id=chunk_id,
            chunk_text=ch,
            entities=entities,
            relations=relations
        )

        print(f"Chunk {i}/{len(chunks)} -> entities:{len(entities)} relations:{len(relations)}")

    driver.close()
    print("\n✅ Done. Knowledge Graph stored in Neo4j.")

if __name__ == "__main__":
    main()
