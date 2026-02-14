# 📄 PDF RAG Assistant  
### Streamlit + LangChain + ChromaDB

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Framework](https://img.shields.io/badge/LangChain-RAG-green)
![UI](https://img.shields.io/badge/Streamlit-Frontend-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🚀 One-Line Description

An interactive Streamlit-based RAG application that lets users upload PDFs and ask grounded questions using LangChain and vector search.

---

## 📚 Table of Contents

- [Overview](#-overview)
- [Problem / Motivation](#-problem--motivation)
- [Key Features](#-key-features)
- [Demo](#-demo)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Usage](#-usage)
- [Configuration](#-configuration)
- [Architecture](#-architecture)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)
- [Author & Contact](#-author--contact)
- [Acknowledgements](#-acknowledgements)

---

## 🧠 Overview

This project implements a **Retrieval-Augmented Generation (RAG)** system that allows users to:

1. Upload a PDF document  
2. Index it into a vector database  
3. Ask natural language questions  
4. Receive answers grounded strictly in the document  
5. View source page references  

Built using:
- **LangChain**
- **ChromaDB**
- **HuggingFace Embeddings**
- **OpenAI LLM**
- **Streamlit UI**

---

## ❓ Problem / Motivation

Large documents such as annual reports, financial statements, and policy manuals are difficult to query efficiently.

This project solves that problem by:

- Converting documents into searchable vector embeddings
- Retrieving relevant context intelligently
- Generating accurate, grounded responses
- Reducing hallucinations by restricting answers to document context

---

## ✨ Key Features

- 📄 PDF upload and automatic indexing  
- 🔎 Semantic similarity search  
- 🧠 RAG pipeline using LangChain  
- 🗂 Persistent ChromaDB storage  
- 📊 Optimized chunking for annual reports  
- 🎛 Adjustable retrieval parameters (k & MMR)  
- 📚 Source citation with page numbers  
- 💻 Clean Streamlit interface  

---

## 🎬 Demo

Run locally:

```bash
streamlit run app1.py
```

(Cloud demo can be deployed via Streamlit Cloud / Render.)

---

## 📦 Prerequisites

- Python 3.9+
- pip
- Virtual environment (recommended)
- OpenAI API key (for answer generation)

Libraries used:
- streamlit
- langchain
- langchain-community
- chromadb
- sentence-transformers
- langchain-openai
- pypdf
- python-dotenv

---

## ⚙️ Installation

### 1️⃣ Clone Repository

```bash
git clone https://github.com/yourusername/pdf-rag.git
cd pdf-rag
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv .venv
```

Activate:

**Windows**
```bash
.venv\Scripts\activate
```

**Mac/Linux**
```bash
source .venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install streamlit langchain langchain-community langchain-text-splitters chromadb sentence-transformers langchain-openai openai pypdf python-dotenv
```

### 4️⃣ Configure Environment

Create `.env` file:

```env
OPENAI_API_KEY=your_api_key_here
EMBEDDINGS_BACKEND=hf
CHAT_MODEL=gpt-4o-mini
```

---

## ▶️ Usage

### Start Application

```bash
streamlit run app1.py
```

### Workflow

1. Upload PDF
2. Click **Ingest / Index**
3. Ask question
4. Adjust:
   - `k` (retrieval depth)
   - Enable MMR if needed
5. View answer + sources

---

## 🔧 Configuration

### Environment Variables

| Variable | Description |
|-----------|------------|
| `OPENAI_API_KEY` | API key for answer generation |
| `EMBEDDINGS_BACKEND` | `hf` or `openai` |
| `CHAT_MODEL` | OpenAI model name |

---

### Config Files

| File | Purpose |
|-------|--------|
| `rag_core.py` | Core RAG logic |
| `app1.py` | Streamlit UI |
| `chroma_db/` | Persistent vector store |

---

## 🏗 Architecture

```
PDF → Text Extraction → Chunking → Embeddings → ChromaDB →
Retriever → LLM → Answer + Sources
```

### Recommended Settings for Annual Reports

```python
chunk_size = 1500
chunk_overlap = 250
k = 6
use_mmr = True
```

---

## 🛣 Roadmap

- Multi-PDF management
- Section-aware chunking
- Table-aware parsing
- Chat history memory
- Fully local LLM support (Ollama)
- Cloud deployment guide

---

## 🤝 Contributing

Contributions are welcome.

1. Fork the repo  
2. Create feature branch  
3. Submit Pull Request  

---

## 📜 License

MIT License

---

## 👤 Author & Contact

Your Name  
GitHub: https://github.com/yourusername  
LinkedIn: https://linkedin.com/in/yourprofile  

---

## 🙏 Acknowledgements

- LangChain community
- ChromaDB team
- HuggingFace sentence-transformers
- OpenAI API

---

### ⭐ If this project helped you, consider giving it a star!

