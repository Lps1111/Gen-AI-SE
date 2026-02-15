import os
from dotenv import load_dotenv
from openai import OpenAI

from src.chat.memory_store import get_last_turns, save_turn
from src.chat.prompts import build_answer_prompt
from src.retrieval.entity_linker import extract_entities
from src.retrieval.graph_retriever import retrieve_graph_payload
from src.retrieval.vector_retriever import vector_search
from src.retrieval.hybrid_merger import merge_context
from src.retrieval.reranker import rerank

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL_ANSWER = os.getenv("OPENAI_MODEL_ANSWER", "gpt-4o")
MEMORY_MAX_TURNS = int(os.getenv("MEMORY_MAX_TURNS", "8"))

def answer_question(question: str) -> str:
    question = (question or "").strip()
    if not question:
        return "Please type a question."

    # memory
    memory_turns = get_last_turns(limit=MEMORY_MAX_TURNS)

    # graph retrieval
    entities = extract_entities(question)
    graph_payload = retrieve_graph_payload(entities)
    graph_chunks = graph_payload.get("chunks", [])

    # vector retrieval
    vector_chunks = vector_search(question)

    # merge + optional rerank
    merged = merge_context(graph_chunks, vector_chunks)
    reranked = rerank(question, merged)

    # prompt + answer
    prompt = build_answer_prompt(question, memory_turns, graph_payload, reranked)

    resp = client.chat.completions.create(
        model=MODEL_ANSWER,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    answer = resp.choices[0].message.content.strip()

    save_turn(question, answer)
    return answer
