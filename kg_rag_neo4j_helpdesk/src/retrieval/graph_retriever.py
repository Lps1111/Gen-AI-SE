# src/retrieval/graph_retriever.py
"""
Neo4j Graph Retriever (KG Retrieval)

What it does:
- Takes extracted entities from the user question
- Finds best matching Entity nodes using Neo4j FULLTEXT index (entityNameIndex)
- Expands the graph by k-hops (GRAPH_HOPS) over :RELATION edges
- Returns:
  - matched_entities
  - triples (subject, relation, object + source + chunk_id)
  - chunks (chunk text evidence)
"""

import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

# Neo4j connection
URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USERNAME", "neo4j")
PASS = os.getenv("NEO4J_PASSWORD", "password123")

# Retrieval knobs
HOPS = int(os.getenv("GRAPH_HOPS", "2"))            # k-hop expansion depth
LIMIT = int(os.getenv("GRAPH_LIMIT", "80"))         # max triples returned
GRAPH_CHUNK_TOP_K = int(os.getenv("GRAPH_CHUNK_TOP_K", "8"))  # number of evidence chunks to return

driver = GraphDatabase.driver(URI, auth=(USER, PASS))


def _entity_candidates(session, term: str, top_k: int = 2) -> List[str]:
    """
    Use Neo4j fulltext index to find best matching Entity names.
    Requires index created during ingestion:
      CREATE FULLTEXT INDEX entityNameIndex IF NOT EXISTS
      FOR (e:Entity) ON EACH [e.name]
    """
    res = session.run(
        """
        CALL db.index.fulltext.queryNodes('entityNameIndex', $q) YIELD node, score
        RETURN node.name AS name, score
        ORDER BY score DESC
        LIMIT $k
        """,
        q=term,
        k=top_k,
    )
    return [r["name"] for r in res]


def retrieve_graph_payload(entities: List[str]) -> Dict[str, Any]:
    """
    Graph retrieval:
    1) entity linking (fulltext)
    2) k-hop expansion over :RELATION edges
    3) fetch chunk texts for evidence

    Returns dict:
    {
      "matched_entities": [...],
      "triples": [ {"s":..., "r":..., "o":..., "source":..., "chunk_id":...}, ... ],
      "chunk_ids": [...],
      "chunks": [ {"chunk_id":..., "source":..., "text":...}, ... ]
    }
    """
    if not entities:
        return {"matched_entities": [], "triples": [], "chunk_ids": [], "chunks": []}

    matched: List[str] = []
    triples: List[Dict[str, Any]] = []
    chunk_ids = set()

    with driver.session() as session:
        # 1) entity linking
        for e in entities:
            for c in _entity_candidates(session, e, top_k=2):
                if c not in matched:
                    matched.append(c)

        if not matched:
            return {"matched_entities": [], "triples": [], "chunk_ids": [], "chunks": []}

        # 2) k-hop expansion
        # IMPORTANT: Neo4j does NOT allow a parameter like $hops inside *1..$hops.
        # So we inject HOPS as a literal via Python f-string.
        query = f"""
        UNWIND $ents AS ent
        MATCH (start:Entity {{name: ent}})
        CALL {{
          WITH start
          MATCH p=(start)-[:RELATION*1..{HOPS}]->(x:Entity)
          UNWIND relationships(p) AS rel
          RETURN rel AS rel
        }}
        WITH DISTINCT rel
        MATCH (a:Entity)-[rel:RELATION]->(b:Entity)
        RETURN a.name AS s, rel.type AS r, b.name AS o,
               rel.source AS source, rel.chunk_id AS chunk_id
        LIMIT $lim
        """

        res = session.run(query, ents=matched, lim=LIMIT)

        for row in res:
            t = {
                "s": row["s"],
                "r": row["r"],
                "o": row["o"],
                "source": row["source"],
                "chunk_id": row["chunk_id"],
            }
            triples.append(t)
            if row["chunk_id"]:
                chunk_ids.add(row["chunk_id"])

        # 3) fetch chunk evidence texts
        chunks: List[Dict[str, Any]] = []
        if chunk_ids:
            cres = session.run(
                """
                UNWIND $cids AS cid
                MATCH (c:Chunk {id: cid})
                RETURN c.id AS chunk_id, c.source AS source, c.text AS text
                """,
                cids=list(chunk_ids)[:50],
            )
            for row in cres:
                chunks.append(
                    {
                        "chunk_id": row["chunk_id"],
                        "source": row["source"],
                        "text": row["text"],
                    }
                )

    # de-dup triples
    seen = set()
    uniq_triples = []
    for t in triples:
        key = (t["s"], t["r"], t["o"], t["chunk_id"])
        if key not in seen:
            seen.add(key)
            uniq_triples.append(t)

    # keep only top K chunks (simple cap)
    chunks = chunks[:GRAPH_CHUNK_TOP_K]

    return {
        "matched_entities": matched,
        "triples": uniq_triples,
        "chunk_ids": list(chunk_ids),
        "chunks": chunks,
    }
