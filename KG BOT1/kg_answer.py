import re
from dotenv import load_dotenv
load_dotenv()

from neo4j import GraphDatabase
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password123"

MODEL_NAME = "gpt-3.5-turbo"


def extract_keywords(question: str):
    """
    Beginner-simple keyword extractor.
    Later we can replace this with LLM-based entity extraction.
    """
    tokens = re.findall(r"[A-Za-z0-9_]+", question)
    tokens = [t for t in tokens if len(t) >= 3]
    seen = set()
    out = []
    for t in tokens:
        k = t.lower()
        if k not in seen:
            seen.add(k)
            out.append(t)
    return out[:8]


def get_entities(driver, keywords, limit=8):
    with driver.session() as session:
        rows = session.run(
            """
            MATCH (e:Entity)
            WHERE any(k IN $keywords WHERE toLower(e.name) CONTAINS toLower(k))
            RETURN e.name AS name
            LIMIT $limit
            """,
            keywords=keywords,
            limit=limit
        ).data()
    return [r["name"] for r in rows]


def get_facts_and_edges(driver, entity_names, limit=40):
    """
    Returns facts plus direct entity->entity edges near matched entities.
    """
    if not entity_names:
        return [], []

    with driver.session() as session:
        facts = session.run(
            """
            MATCH (e:Entity)<-[:SOURCE]-(f:Fact)-[:TARGET]->(t:Entity)
            WHERE e.name IN $names
            RETURN f.id AS fact_id, f.relation AS relation, e.name AS source, t.name AS target
            LIMIT $limit
            """,
            names=entity_names,
            limit=limit
        ).data()

        edges = session.run(
            """
            MATCH (a:Entity)-[r]->(b:Entity)
            WHERE a.name IN $names
            RETURN a.name AS source, type(r) AS relation, b.name AS target
            LIMIT $limit
            """,
            names=entity_names,
            limit=limit
        ).data()

    return facts, edges


def get_supporting_chunks(driver, fact_ids, limit=6):
    if not fact_ids:
        return []

    with driver.session() as session:
        rows = session.run(
            """
            MATCH (c:Chunk)-[:SUPPORTS]->(f:Fact)
            WHERE f.id IN $fact_ids
            RETURN c.id AS chunk_id, c.text AS text
            LIMIT $limit
            """,
            fact_ids=fact_ids,
            limit=limit
        ).data()

    # Keep unique by chunk_id
    seen = set()
    out = []
    for r in rows:
        cid = r["chunk_id"]
        if cid in seen:
            continue
        seen.add(cid)
        out.append(r)
    return out


def answer(question: str) -> str:
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    llm = ChatOpenAI(model=MODEL_NAME)

    keywords = extract_keywords(question)
    entity_names = get_entities(driver, keywords, limit=8)

    facts, edges = get_facts_and_edges(driver, entity_names, limit=60)
    fact_ids = [f["fact_id"] for f in facts[:12]]  # top facts
    chunks = get_supporting_chunks(driver, fact_ids, limit=6)

    driver.close()

    # Build context strings
    facts_txt = "\n".join([f'- ({x["relation"]}) {x["source"]} -> {x["target"]} [fact:{x["fact_id"]}]' for x in facts[:20]])
    edges_txt = "\n".join([f'- ({x["relation"]}) {x["source"]} -> {x["target"]}' for x in edges[:20]])
    chunks_txt = "\n\n".join([f'[{c["chunk_id"]}] {c["text"][:1200]}' for c in chunks])

    prompt = ChatPromptTemplate.from_template("""
You are a helpful assistant.

Answer ONLY using the provided GRAPH and EVIDENCE context.
If the answer is not supported, say: "I don't know from this PDF."

GRAPH (Facts):
{facts}

GRAPH (Edges):
{edges}

EVIDENCE (PDF chunks):
{chunks}

QUESTION:
{question}

Write the answer in simple language.
Add 1–3 citations using chunk ids like [some::chunk::12].
""")

    chain = prompt | llm | StrOutputParser()

    return chain.invoke({
        "facts": facts_txt or "(no facts found)",
        "edges": edges_txt or "(no edges found)",
        "chunks": chunks_txt or "(no evidence chunks found)",
        "question": question
    })


if __name__ == "__main__":
    print("KG-RAG Answering (terminal). Type 'exit' to stop.\n")
    while True:
        q = input("You: ").strip()
        if q.lower() == "exit":
            break
        print("\nBot:", answer(q), "\n")
