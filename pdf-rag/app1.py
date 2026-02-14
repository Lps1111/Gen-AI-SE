import os
import tempfile
import streamlit as st
from dotenv import load_dotenv

from rag_core import ingest_pdf, answer_question

load_dotenv()

st.set_page_config(page_title="PDF RAG (LangChain)", layout="wide")

# --- Settings ---
DEFAULT_K = 4
DEFAULT_USE_MMR = False

# Choose embeddings backend:
# "hf" = local sentence-transformers embeddings (no API key needed)
# "openai" = OpenAI embeddings (needs OPENAI_API_KEY)
EMBEDDINGS_BACKEND = os.getenv("EMBEDDINGS_BACKEND", "hf")

# Chat model for answering (this starter uses OpenAI Chat model in rag_core.answer_question)
CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4o-mini")


st.title("📄 PDF Q&A (RAG) — LangChain + Chroma")
st.caption("Upload a PDF → it gets indexed → ask questions grounded in your PDF.")

# --- Sidebar controls ---
with st.sidebar:
    st.header("Settings")
    k = st.slider("Top-k chunks to retrieve", 1, 10, DEFAULT_K)
    use_mmr = st.checkbox("Use MMR (diverse retrieval)", value=DEFAULT_USE_MMR)
    st.write("Embeddings backend:", f"`{EMBEDDINGS_BACKEND}`")
    st.write("Chat model:", f"`{CHAT_MODEL}`")

    st.divider()
    st.subheader("Notes")
    st.write("- `/` (root) 404 is normal in API mode, but Streamlit gives UI.")
    st.write("- For scanned PDFs (image-only), you need OCR loaders later.")


# --- Upload section ---
st.subheader("1) Upload & Index PDF")

uploaded_file = st.file_uploader("Choose a PDF", type=["pdf"])

colA, colB = st.columns([1, 2])

if "indexed" not in st.session_state:
    st.session_state.indexed = False

if "last_ingest_stats" not in st.session_state:
    st.session_state.last_ingest_stats = None

if uploaded_file is not None:
    with colA:
        if st.button("📥 Ingest / Index this PDF", use_container_width=True):
            # Save uploaded PDF to a temp path
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.getbuffer())
                pdf_path = tmp.name

            with st.spinner("Indexing PDF into ChromaDB..."):
                stats = ingest_pdf(
                    pdf_path=pdf_path,
                    embeddings_backend=EMBEDDINGS_BACKEND,
                    chunk_size=1000,
                    chunk_overlap=150,
                )
                st.session_state.indexed = True
                st.session_state.last_ingest_stats = stats

            st.success("✅ PDF indexed successfully!")

    with colB:
        if st.session_state.last_ingest_stats:
            st.json(st.session_state.last_ingest_stats)
else:
    st.info("Upload a PDF to begin.")

st.divider()

# --- Q&A section ---
st.subheader("2) Ask Questions")

if not st.session_state.indexed:
    st.warning("Please upload and ingest a PDF first.")
else:
    question = st.text_input("Type your question here:", placeholder="e.g., What is the eligibility criteria?")
    ask_col1, ask_col2 = st.columns([1, 1])

    with ask_col1:
        if st.button("🤖 Get Answer", use_container_width=True) and question.strip():
            with st.spinner("Retrieving context and generating answer..."):
                result = answer_question(
                    question=question.strip(),
                    embeddings_backend=EMBEDDINGS_BACKEND,
                    model_backend="openai",
                    model_name=CHAT_MODEL,
                    k=k,
                    use_mmr=use_mmr
                )

            st.markdown("### Answer")
            st.write(result["answer"])

            st.markdown("### Sources")
            if result.get("sources"):
                for s in result["sources"]:
                    st.write(f"- {s.get('source', 'unknown')} (page {s.get('page', 'n/a')})")
            else:
                st.write("No sources returned.")

    with ask_col2:
        st.markdown("### Quick prompts")
        if st.button("Summarize in 5 bullets", use_container_width=True):
            st.session_state.quick_q = "Summarize this PDF in 5 bullet points."
        if st.button("List key definitions", use_container_width=True):
            st.session_state.quick_q = "List the key definitions mentioned in the document."
        if st.button("Extract eligibility criteria", use_container_width=True):
            st.session_state.quick_q = "What are the eligibility criteria mentioned in the document?"

        if "quick_q" in st.session_state and st.session_state.quick_q:
            st.info(f"Click **Get Answer** after pasting: {st.session_state.quick_q}")
            st.code(st.session_state.quick_q)
