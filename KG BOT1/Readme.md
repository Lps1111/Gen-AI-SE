# 📚 Knowledge Graph RAG Bot (KG-RAG)

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Neo4j](https://img.shields.io/badge/neo4j-5.x-brightgreen)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-experimental-orange)

A **Knowledge Graph–powered Retrieval Augmented Generation (KG-RAG) bot** that answers questions **strictly from your PDF documents** by combining **Neo4j knowledge graphs + LLMs**.

---

## 🧭 Table of Contents

* [Overview](#overview)
* [Problem & Motivation](#problem--motivation)
* [Key Features](#key-features)
* [Architecture](#architecture)
* [Demo](#demo)
* [Prerequisites](#prerequisites)
* [Installation](#installation)
* [Configuration](#configuration)
* [Usage](#usage)
* [Project Structure](#project-structure)
* [Roadmap](#roadmap)
* [Contributing](#contributing)
* [License](#license)
* [Author & Contact](#author--contact)
* [Acknowledgements](#acknowledgements)

---

## 📌 Overview

**Knowledge Graph RAG Bot** transforms unstructured PDFs into a **structured knowledge graph** and enables **accurate, explainable question answering** using:

* Entity–Relationship extraction
* Graph-based reasoning
* Evidence-backed answers from original documents

This is **not just vector search** — it’s **relationship-aware AI**.

---

## ❓ Problem & Motivation

Traditional RAG systems rely only on vector similarity, which often:

* Misses multi-hop relationships
* Hallucinates answers
* Struggles with “why” and “how are these related?” questions

This project solves that by:

* Converting PDFs into a **Knowledge Graph**
* Querying **entities, facts, and relationships**
* Grounding answers with **exact supporting text (citations)**

---

## ✨ Key Features

* 📄 **PDF → Knowledge Graph ingestion**
* 🧠 **Entity & relationship extraction using LLMs**
* 🕸️ **Neo4j graph storage (nodes, facts, edges)**
* 🔍 **Graph + evidence retrieval (KG-RAG)**
* 📎 **Cited answers backed by PDF chunks**
* 🧪 **Terminal-based Q&A (easy to extend to Streamlit/UI)**

---

## 🏗️ Architecture

```
PDF
 ↓
Text Extraction & Chunking
 ↓
LLM-based Entity & Relation Extraction
 ↓
Neo4j Knowledge Graph
 (Entities • Facts • Relationships)
 ↓
User Question
 ↓
Subgraph Retrieval + Evidence Chunks
 ↓
LLM Answer (Grounded + Cited)
```

---

## 🎥 Demo

> Demo UI coming soon

Current interaction via terminal:

```
python kg_rag_answer_v1.py
```

---

## 🔧 Prerequisites

* **Python**: 3.10+
* **Neo4j**: 5.x (Docker recommended)
* **Docker Desktop**
* **OpenAI API key**
* **OS**: Windows / macOS / Linux

---

## ⚙️ Installation

### 1️⃣ Clone the repository

```
git clone https://github.com/yourusername/kg-rag-bot.git
cd kg-rag-bot
```

### 2️⃣ Create and activate virtual environment

```
python -m venv venv
venv\\Scripts\\activate      # Windows
# source venv/bin/activate   # macOS/Linux
```

### 3️⃣ Install dependencies

```
pip install -r requirements.txt
```

### 4️⃣ Start Neo4j (Docker)

```
docker run -d --name neo4j-graphrag \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password123 \
  neo4j:5
```

Access Neo4j Browser at:
👉 [http://localhost:7474](http://localhost:7474)

---

## 🔐 Configuration

### Environment Variables (`.env`)

```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
```

### Config Files

* `.env` – API keys (ignored by git)
* `requirements.txt` – Python dependencies
* `.gitignore` – ignores venv, cache, secrets

---

## ▶️ Usage

### 1️⃣ Build Knowledge Graph from PDF

Edit in `pdftoKG.py`:

```
PDF_PATH = "your_document.pdf"
```

Run:

```
python pdftoKG.py
```

This will:

* Extract text
* Chunk content
* Build entities, facts, and relationships in Neo4j

---

### 2️⃣ Ask Questions (KG-RAG)

```
python kg_rag_answer_v1.py
```

Example:

```
You: What is the role of RBI in this document?
Bot: RBI regulates banking policies and sets interest rates... [pdf::chunk::12]
```

---

## 🗂️ Project Structure

```
kg-rag-bot/
│
├── pdftoKG.py              # PDF → Knowledge Graph ingestion
├── kg_rag_answer_v1.py     # KG-RAG question answering
├── requirements.txt
├── README.md
├── .gitignore
├── .env                   # (ignored)
└── data/
    └── sample.pdf
```

---

## 🛣️ Roadmap

* [ ] Streamlit web UI
* [ ] Multi-PDF ingestion
* [ ] OCR support for scanned PDFs
* [ ] LLM-based question entity extraction
* [ ] On-demand KG expansion
* [ ] Graph visualization in UI

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repo
2. Create a feature branch
3. Commit changes
4. Open a Pull Request

For major changes, please open an issue first.

---

## 📄 License

This project is licensed under the **MIT License**.

---

## 👤 Author & Contact

**Lalith Prasad S**

* GitHub: [https://github.com/yourusername](https://github.com/yourusername)
* LinkedIn: [https://linkedin.com/in/yourprofile](https://linkedin.com/in/yourprofile)

---

## 🙏 Acknowledgements

* LangChain community
* Neo4j GraphRAG resources
* OpenAI API
* Open-source contributors and educators

---

⭐ If you find this project useful, consider starring the repo!
