import os
import json
from typing import List, Dict
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL_EXTRACT = os.getenv("OPENAI_MODEL_EXTRACT", "gpt-4o-mini")

TRIPLE_SCHEMA = {
    "name": "triples",
    "schema": {
        "type": "object",
        "properties": {
            "triples": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "subject": {"type": "string"},
                        "relation": {"type": "string"},
                        "object": {"type": "string"},
                    },
                    "required": ["subject", "relation", "object"],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["triples"],
        "additionalProperties": False,
    },
}

def _clean(s: str, max_len: int) -> str:
    s = (s or "").strip()
    if len(s) > max_len:
        s = s[:max_len].strip()
    return s

def extract_triples(chunk_text: str, source: str, chunk_id: str) -> List[Dict[str, str]]:
    chunk_text = (chunk_text or "").strip()
    if not chunk_text:
        return []

    system = (
        "Extract knowledge-graph triples from helpdesk documents. "
        "Prefer concrete factual relations. Avoid vague relations."
    )

    user = f"""
SOURCE: {source}
CHUNK_ID: {chunk_id}

TEXT:
{chunk_text}

Return JSON: {{ "triples": [{{"subject": "...", "relation": "...", "object": "..."}}] }}
"""

    try:
        resp = client.chat.completions.create(
            model=MODEL_EXTRACT,
            messages=[{"role": "system", "content": system},
                      {"role": "user", "content": user}],
            temperature=0,
            response_format={"type": "json_schema", "json_schema": TRIPLE_SCHEMA},
        )
        data = json.loads(resp.choices[0].message.content)
        triples = data.get("triples", [])
    except Exception as e:
        print(f"[WARN] Triple extraction failed ({source} / {chunk_id}): {e}")
        return []

    out = []
    for t in triples:
        subj = _clean(t.get("subject"), 120)
        rel = _clean(t.get("relation"), 80)
        obj = _clean(t.get("object"), 120)
        if subj and rel and obj and subj.lower() != obj.lower():
            out.append({"subject": subj, "relation": rel, "object": obj})

    uniq = {(x["subject"], x["relation"], x["object"]) for x in out}
    return [{"subject": a, "relation": b, "object": c} for (a, b, c) in sorted(uniq)]
