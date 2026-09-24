"""Streamlit chat UI for Kiro, the local document RAG app.

Run with: streamlit run app.py
"""

import streamlit as st

from kiro import config, rag, vectorstore

st.set_page_config(page_title="Kiro — Local Document RAG", page_icon="📚")
st.title("📚 Kiro")
st.caption(
    "Chat with documents stored on your own device. Documents and the search "
    "index stay on this machine; only your question and the matching excerpts "
    "are sent to the LLM you've configured."
)

with st.sidebar:
    st.header("Documents")

    uploaded = st.file_uploader(
        "Upload documents",
        type=["txt", "md", "pdf", "docx"],
        accept_multiple_files=True,
    )
    if uploaded and st.button("Index uploaded files"):
        total_docs = total_chunks = 0
        with st.spinner("Indexing..."):
            for f in uploaded:
                dest = config.DATA_DIR / f.name
                dest.write_bytes(f.getbuffer())
                docs, chunks = rag.ingest_path(dest)
                total_docs += docs
                total_chunks += chunks
        st.success(f"Indexed {total_docs} document(s), {total_chunks} chunk(s).")

    folder = st.text_input("...or index a local folder/file path", placeholder="/path/to/docs")
    if folder and st.button("Index path"):
        with st.spinner("Indexing..."):
            try:
                docs, chunks = rag.ingest_path(folder)
                st.success(f"Indexed {docs} document(s), {chunks} chunk(s).")
            except Exception as exc:
                st.error(str(exc))

    st.divider()
    try:
        indexed = vectorstore.count()
    except Exception:
        indexed = 0
    st.metric("Chunks indexed", indexed)
    st.caption(f"LLM backend: `{config.LLM_PROVIDER}`")

    if st.button("Clear index", type="secondary"):
        vectorstore.reset_collection()
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

question = st.chat_input("Ask about your documents...")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                answer_text, sources = rag.answer(question)
            except Exception as exc:
                answer_text, sources = f"Error: {exc}", []
        st.markdown(answer_text)
        if sources:
            st.caption("Sources: " + ", ".join(sources))

    st.session_state.messages.append({"role": "assistant", "content": answer_text})
