import os
import json
from typing import List
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL_EXTRACT = os.getenv("OPENAI_MODEL_EXTRACT", "gpt-4o-mini")

ENTITY_SCHEMA = {
    "name": "entities",
    "schema": {
        "type": "object",
        "properties": {"entities": {"type": "array", "items": {"type": "string"}}},
        "required": ["entities"],
        "additionalProperties": False,
    },
}

def extract_entities(question: str) -> List[str]:
    question = (question or "").strip()
    if not question:
        return []

    system = (
        "Extract key entities (products, processes, policies, systems, departments, error codes). "
        "Return short phrases. Do not include irrelevant words."
    )
    user = f"Question: {question}"

    try:
        resp = client.chat.completions.create(
            model=MODEL_EXTRACT,
            messages=[{"role": "system", "content": system},
                      {"role": "user", "content": user}],
            temperature=0,
            response_format={"type": "json_schema", "json_schema": ENTITY_SCHEMA},
        )
        data = json.loads(resp.choices[0].message.content)
        entities = [e.strip() for e in data.get("entities", []) if e and e.strip()]
        seen = set()
        out = []
        for e in entities:
            el = e.lower()
            if el not in seen:
                seen.add(el)
                out.append(e)
        return out[:10]
    except Exception:
        return []
