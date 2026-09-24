"""Local, persistent vector index backed by Chroma + sentence-transformers.

Everything here runs on-device: the embedding model is downloaded once from
Hugging Face and cached locally, and the index itself is a directory of
files on disk (KIRO_INDEX_DIR) — no external services involved.
"""

from typing import List, Optional, Tuple

import chromadb
from chromadb.utils import embedding_functions

from . import config

_collection = None


def get_client():
    return chromadb.PersistentClient(path=str(config.INDEX_DIR))


def get_collection():
    global _collection
    if _collection is not None:
        return _collection

    client = get_client()
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=config.EMBEDDING_MODEL
    )
    _collection = client.get_or_create_collection(
        name=config.COLLECTION_NAME,
        embedding_function=embedding_fn,
    )
    return _collection


def add_chunks(chunks: List[str], source: str, collection=None) -> None:
    if not chunks:
        return
    collection = collection or get_collection()
    ids = [f"{source}::{i}" for i in range(len(chunks))]
    metadatas = [{"source": source, "chunk": i} for i in range(len(chunks))]
    collection.upsert(documents=chunks, ids=ids, metadatas=metadatas)


def query(
    question: str, top_k: Optional[int] = None, collection=None
) -> List[Tuple[str, dict, float]]:
    collection = collection or get_collection()
    top_k = top_k or config.TOP_K
    results = collection.query(query_texts=[question], n_results=top_k)

    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]
    return list(zip(docs, metas, distances))


def count(collection=None) -> int:
    collection = collection or get_collection()
    return collection.count()


def reset_collection() -> None:
    global _collection
    client = get_client()
    try:
        client.delete_collection(config.COLLECTION_NAME)
    except Exception:
        pass
    _collection = None
