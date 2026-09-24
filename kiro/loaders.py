"""Load plain text out of documents living on the local filesystem."""

from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Optional

SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx"}


@dataclass
class Document:
    text: str
    source: str


def load_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def load_pdf(path: Path) -> str:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(pages)


def load_docx(path: Path) -> str:
    import docx

    doc = docx.Document(str(path))
    return "\n".join(p.text for p in doc.paragraphs)


def load_document(path: Path) -> Optional[Document]:
    ext = path.suffix.lower()
    if ext in {".txt", ".md"}:
        text = load_txt(path)
    elif ext == ".pdf":
        text = load_pdf(path)
    elif ext == ".docx":
        text = load_docx(path)
    else:
        return None

    text = text.strip()
    if not text:
        return None
    return Document(text=text, source=str(path))


def iter_documents(root: Path) -> Iterator[Document]:
    """Yield Document objects for every supported file under `root`.

    `root` may be a single file or a directory (searched recursively).
    Unreadable or unsupported files are skipped rather than raising.
    """
    root = Path(root)

    if root.is_file():
        doc = load_document(root)
        if doc:
            yield doc
        return

    if not root.is_dir():
        raise FileNotFoundError(f"No such file or directory: {root}")

    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            try:
                doc = load_document(path)
            except Exception:
                continue
            if doc:
                yield doc
