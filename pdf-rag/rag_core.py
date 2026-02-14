import os
from typing import List, Dict, Any, Optional
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_community.vectorstores import Chroma

# Embeddings (choose one)
from langchain_community.embeddings import HuggingFaceEmbeddings

# Optional OpenAI (only used if enabled)
try:
    from langchain_openai import OpenAIEmbeddings, ChatOpenAI
except Exception:
    OpenAIEmbeddings = None
    ChatOpenAI = None

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document


PERSIST_DIR = "chroma_db"
COLLECTION_NAME = "pdf_rag"


def get_embeddings(backend: str = "hf"):
    """
    backend: "hf" or "openai"
    """
    if backend == "openai":
        if OpenAIEmbeddings is None:
            raise ImportError("langchain-openai not installed. Install it or switch to hf embeddings.")
        if not os.getenv("OPENAI_API_KEY"):
            raise EnvironmentError("OPENAI_API_KEY missing in environment (.env).")
        return OpenAIEmbeddings()
    # HuggingFace local embeddings (good starter)
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


def load_pdf(pdf_path: str) -> List[Document]:
    loader = PyPDFLoader(pdf_path)
    return loader.load()  # one Document per page


def split_docs(docs: List[Document], chunk_size: int = 1500, chunk_overlap: int = 300) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return splitter.split_documents(docs)


def get_vectorstore(embeddings_backend: str = "hf") -> Chroma:
    embeddings = get_embeddings(embeddings_backend)
    vs = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=PERSIST_DIR,
        embedding_function=embeddings,
    )
    return vs


def ingest_pdf(
    pdf_path: str,
    embeddings_backend: str = "hf",
    chunk_size: int = 1000,
    chunk_overlap: int = 150,
) -> Dict[str, Any]:
    docs = load_pdf(pdf_path)
    chunks = split_docs(docs, chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    vs = get_vectorstore(embeddings_backend)
    vs.add_documents(chunks)
    vs.persist()

    return {
        "pdf_path": pdf_path,
        "pages_loaded": len(docs),
        "chunks_added": len(chunks),
        "persist_dir": str(Path(PERSIST_DIR).resolve()),
        "collection": COLLECTION_NAME,
    }


def retrieve(
    question: str,
    embeddings_backend: str = "hf",
    k: int = 4,
    use_mmr: bool = False,
):
    vs = get_vectorstore(embeddings_backend)

    if use_mmr:
        retriever = vs.as_retriever(
            search_type="mmr",
            search_kwargs={"k": k, "fetch_k": max(10, k * 3)}
        )
    else:
        retriever = vs.as_retriever(search_kwargs={"k": k})

    # ✅ NEW LangChain uses .invoke()
    if hasattr(retriever, "invoke"):
        return retriever.invoke(question)

    # ✅ Older LangChain uses get_relevant_documents()
    if hasattr(retriever, "get_relevant_documents"):
        return retriever.get_relevant_documents(question)

    # Fallback
    raise AttributeError("Retriever has neither invoke() nor get_relevant_documents().")



def similarity_with_scores(
    question: str,
    embeddings_backend: str = "hf",
    k: int = 4,
):
    vs = get_vectorstore(embeddings_backend)
    return vs.similarity_search_with_score(question, k=k)


def answer_question(
    question: str,
    embeddings_backend: str = "hf",
    model_backend: str = "openai",   # simplest LLM path for beginners
    model_name: str = "gpt-4o-mini",
    k: int = 4,
    use_mmr: bool = False,
) -> Dict[str, Any]:
    context_docs = retrieve(question, embeddings_backend=embeddings_backend, k=k, use_mmr=use_mmr)

    # Build a clean context string
    context_text = "\n\n".join(
        [f"[source={d.metadata.get('source','unknown')}, page={d.metadata.get('page', 'n/a')}] {d.page_content}"
         for d in context_docs]
    )

    # Prompt: answer only from context (as guide recommends to reduce hallucination)
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a helpful assistant. Answer ONLY using the given context. "
         "If the answer is not present in the context, say: 'I don't know based on the provided PDF.'"),
        ("human", "Question: {question}\n\nContext:\n{context}")
    ])

    if model_backend != "openai":
        raise ValueError("This sample uses OpenAI chat model for generation. (Easy to swap later.)")

    if ChatOpenAI is None:
        raise ImportError("langchain-openai not installed. Install it to use OpenAI chat models.")
    if not os.getenv("OPENAI_API_KEY"):
        raise EnvironmentError("OPENAI_API_KEY missing in environment (.env).")

    llm = ChatOpenAI(model=model_name, temperature=0)
    chain = prompt | llm

    response = chain.invoke({"question": question, "context": context_text})

    # Return answer + sources
    sources = []
    for d in context_docs:
        sources.append({
            "source": d.metadata.get("source", "unknown"),
            "page": (d.metadata.get("page", None) + 1) if isinstance(d.metadata.get("page", None), int) else d.metadata.get("page", None),
        })

    # de-dupe sources
    unique_sources = []
    seen = set()
    for s in sources:
        key = (s["source"], s["page"])
        if key not in seen:
            unique_sources.append(s)
            seen.add(key)

    return {
        "question": question,
        "answer": response.content,
        "top_k": k,
        "use_mmr": use_mmr,
        "sources": unique_sources,
    }
