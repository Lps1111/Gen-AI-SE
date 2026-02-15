import streamlit as st
from src.chat.memory_store import init_memory
from src.chat.chat_orchestrator import answer_question
from src.ocr.ocr_engine import ocr_image_to_text

init_memory()

st.set_page_config(page_title="Hybrid KG-RAG Helpdesk", layout="wide")
st.title("Hybrid KG-RAG Helpdesk (Neo4j + Chroma + OpenAI) — Project B")

tab1, tab2 = st.tabs(["Ask (Text)", "Ask (Image OCR)"])

with tab1:
    q = st.text_area("Ask your helpdesk question:", height=120)
    if st.button("Answer", type="primary"):
        with st.spinner("Thinking..."):
            ans = answer_question(q)
        st.markdown(ans)

with tab2:
    st.write("Upload an image (screenshot/photo). We'll OCR it and ask the bot.")
    img = st.file_uploader("Upload image", type=["png", "jpg", "jpeg"])
    if img is not None:
        temp_path = "storage/memory/_uploaded.png"
        with open(temp_path, "wb") as f:
            f.write(img.getbuffer())

        try:
            extracted = ocr_image_to_text(temp_path)
        except Exception as e:
            st.error(f"OCR failed: {e}")
            extracted = ""

        st.subheader("Extracted text")
        st.code(extracted or "(no text extracted)")

        if st.button("Ask using extracted text"):
            with st.spinner("Thinking..."):
                ans = answer_question(extracted)
            st.markdown(ans)
