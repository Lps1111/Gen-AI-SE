import os
from typing import List, Dict
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USERNAME")
PASS = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(URI, auth=(USER, PASS))

def close_driver():
    driver.close()

def ensure_schema():
    with driver.session() as session:
        session.run("CREATE CONSTRAINT doc_id IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE")
        session.run("CREATE CONSTRAINT chunk_id IF NOT EXISTS FOR (c:Chunk) REQUIRE c.id IS UNIQUE")
        session.run("CREATE CONSTRAINT ent_name IF NOT EXISTS FOR (e:Entity) REQUIRE e.name IS UNIQUE")
        session.run("""
        CREATE FULLTEXT INDEX entityNameIndex IF NOT EXISTS
        FOR (e:Entity) ON EACH [e.name]
        """)

def upsert_document(doc_id: str, source: str):
    with driver.session() as session:
        session.run("""
            MERGE (d:Document {id:$doc_id})
            SET d.source=$source
        """, doc_id=doc_id, source=source)

def upsert_chunk(chunk_id: str, doc_id: str, source: str, text: str, position: int):
    with driver.session() as session:
        session.run("""
            MERGE (c:Chunk {id:$chunk_id})
            SET c.text=$text, c.source=$source, c.position=$position
            WITH c
            MATCH (d:Document {id:$doc_id})
            MERGE (d)-[:HAS_CHUNK]->(c)
        """, chunk_id=chunk_id, doc_id=doc_id, source=source, text=text, position=position)

def add_triples(triples: List[Dict[str, str]], chunk_id: str, doc_id: str, source: str):
    if not triples:
        return

    with driver.session() as session:
        for t in triples:
            session.run("""
                MERGE (a:Entity {name:$subject})
                MERGE (b:Entity {name:$object})
                WITH a,b
                MERGE (a)-[r:RELATION {type:$relation, chunk_id:$chunk_id, doc_id:$doc_id}]->(b)
                SET r.source = $source
            """, subject=t["subject"], relation=t["relation"], object=t["object"],
                 chunk_id=chunk_id, doc_id=doc_id, source=source)

            session.run("""
                MATCH (c:Chunk {id:$chunk_id})
                MERGE (e:Entity {name:$name})
                MERGE (c)-[:MENTIONS]->(e)
            """, chunk_id=chunk_id, name=t["subject"])

            session.run("""
                MATCH (c:Chunk {id:$chunk_id})
                MERGE (e:Entity {name:$name})
                MERGE (c)-[:MENTIONS]->(e)
            """, chunk_id=chunk_id, name=t["object"])
