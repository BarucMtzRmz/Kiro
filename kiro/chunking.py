"""Paragraph-aware text chunking with overlap, for embedding/retrieval."""

from typing import List


def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 150) -> List[str]:
    """Split `text` into overlapping chunks no larger than `chunk_size` chars.

    Tries to break on paragraph boundaries first, falling back to a hard
    character split for paragraphs longer than `chunk_size`.
    """
    text = text.strip()
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not paragraphs:
        paragraphs = [text]

    chunks: List[str] = []
    current = ""

    def flush():
        nonlocal current
        if current:
            chunks.append(current)
            current = ""

    for para in paragraphs:
        if len(para) > chunk_size:
            flush()
            step = max(chunk_size - chunk_overlap, 1)
            for i in range(0, len(para), step):
                chunks.append(para[i : i + chunk_size])
            continue

        candidate = f"{current}\n\n{para}" if current else para
        if len(candidate) <= chunk_size:
            current = candidate
        else:
            overlap_text = current[-chunk_overlap:] if chunk_overlap else ""
            flush()
            current = f"{overlap_text}\n\n{para}".strip() if overlap_text else para

    flush()
    return chunks
