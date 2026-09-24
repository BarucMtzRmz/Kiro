"""The retrieve-then-generate pipeline tying loaders, the index and the LLM together."""

from pathlib import Path
from typing import List, Optional, Tuple

from . import config, llm, vectorstore
from .chunking import chunk_text
from .loaders import iter_documents


def ingest_path(path) -> Tuple[int, int]:
    """Load, chunk and index every supported document under `path`.

    Returns (documents_indexed, chunks_indexed).
    """
    collection = vectorstore.get_collection()
    total_docs = 0
    total_chunks = 0

    for doc in iter_documents(Path(path)):
        chunks = chunk_text(doc.text, config.CHUNK_SIZE, config.CHUNK_OVERLAP)
        if not chunks:
            continue
        vectorstore.add_chunks(chunks, doc.source, collection=collection)
        total_docs += 1
        total_chunks += len(chunks)

    return total_docs, total_chunks


def answer(question: str, top_k: Optional[int] = None) -> Tuple[str, List[str]]:
    """Answer `question` using the indexed documents. Returns (answer, sources)."""
    collection = vectorstore.get_collection()
    if vectorstore.count(collection) == 0:
        return (
            "No documents have been indexed yet. Run `kiro ingest <path>` "
            "(or use the sidebar in the web app) to add some first.",
            [],
        )

    contexts = vectorstore.query(question, top_k=top_k, collection=collection)
    response = llm.generate(question, contexts)
    sources = sorted({meta.get("source", "unknown") for _, meta, _ in contexts})
    return response, sources
