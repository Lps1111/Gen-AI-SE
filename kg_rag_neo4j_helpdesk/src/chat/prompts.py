def build_answer_prompt(question: str, memory_turns, graph_payload, final_chunks):
    mem_block = ""
    if memory_turns:
        mem_block = "\n\n".join([f"User: {u}\nAssistant: {b}" for u, b in memory_turns])

    matched = graph_payload.get("matched_entities", [])
    triples = graph_payload.get("triples", [])

    triples_text = "\n".join(
        [f"- {t['s']} —[{t['r']}]→ {t['o']} (src={t['source']}, chunk={t['chunk_id']})"
         for t in triples[:120]]
    )

    chunks_text = "\n\n".join(
        [f"[{c['source']} | {c['chunk_id']} | origin={c.get('origin','?')}]\n{c['text']}"
         for c in final_chunks[:10]]
    )

    prompt = f"""
You are a helpdesk assistant that answers using ONLY the provided evidence.
If evidence is insufficient, say you don't have enough information and ask what document or detail is missing.
Be concise, correct, and practical.

Recent conversation:
{mem_block if mem_block else "(none)"}

Matched entities:
{matched if matched else "(none)"}

Graph triples (structure hints; verify with chunks):
{triples_text if triples_text else "(none)"}

Evidence chunks (authoritative):
{chunks_text if chunks_text else "(none)"}

User question:
{question}

Rules:
- Use evidence chunks as primary source.
- Cite sources like: (Source: <file> | <chunk_id>)
- If you are unsure, say so.
- Provide step-by-step instructions when relevant.
"""
    return prompt.strip()
