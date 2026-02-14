import os
from pathlib import Path
from flask import Flask, request, jsonify
from dotenv import load_dotenv

from rag_core import ingest_pdf, answer_question, similarity_with_scores

load_dotenv()

app = Flask(__name__)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Choose embeddings backend: "hf" (local) or "openai"
EMBEDDINGS_BACKEND = os.getenv("EMBEDDINGS_BACKEND", "hf")

@app.get("/health")
def health():
    return jsonify({"status": "ok", "embeddings_backend": EMBEDDINGS_BACKEND})

@app.post("/upload")
def upload_pdf():
    """
    Form-data:
      file: PDF
    """
    if "file" not in request.files:
        return jsonify({"error": "No file field provided. Use form-data key 'file'."}), 400

    f = request.files["file"]
    if not f.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files supported."}), 400

    save_path = UPLOAD_DIR / f.filename
    f.save(save_path)

    stats = ingest_pdf(
        pdf_path=str(save_path),
        embeddings_backend=EMBEDDINGS_BACKEND,
        chunk_size=1000,
        chunk_overlap=150,
    )
    return jsonify({"message": "PDF ingested", "stats": stats})


@app.post("/ask")
def ask():
    """
    JSON body:
      {
        "question": "...",
        "k": 4,
        "use_mmr": false
      }
    """
    data = request.get_json(silent=True) or {}
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error": "Missing 'question'"}), 400

    k = int(data.get("k", 4))
    use_mmr = bool(data.get("use_mmr", False))

    # Answer (generation uses OpenAI chat model in this starter)
    result = answer_question(
        question=question,
        embeddings_backend=EMBEDDINGS_BACKEND,
        model_backend="openai",
        model_name=os.getenv("CHAT_MODEL", "gpt-4o-mini"),
        k=k,
        use_mmr=use_mmr
    )
    return jsonify(result)

@app.post("/search_scores")
def search_scores():
    """
    JSON body:
      { "question": "...", "k": 4 }
    Returns similarity results with scores (debug/quality tuning).
    """
    data = request.get_json(silent=True) or {}
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error": "Missing 'question'"}), 400
    k = int(data.get("k", 4))

    results = similarity_with_scores(question, embeddings_backend=EMBEDDINGS_BACKEND, k=k)
    payload = []
    for doc, score in results:
        payload.append({
            "score": float(score),
            "source": doc.metadata.get("source", "unknown"),
            "page": (doc.metadata.get("page", None) + 1) if isinstance(doc.metadata.get("page", None), int) else doc.metadata.get("page", None),
            "snippet": doc.page_content[:300]
        })
    return jsonify({"question": question, "results": payload})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
