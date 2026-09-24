from pathlib import Path

from kiro.loaders import iter_documents, load_document


def test_load_txt_document(tmp_path: Path):
    f = tmp_path / "note.txt"
    f.write_text("Hello, world.")

    doc = load_document(f)

    assert doc is not None
    assert doc.text == "Hello, world."
    assert doc.source == str(f)


def test_load_document_skips_unsupported_extension(tmp_path: Path):
    f = tmp_path / "image.png"
    f.write_bytes(b"\x89PNG\r\n")

    assert load_document(f) is None


def test_load_document_skips_empty_file(tmp_path: Path):
    f = tmp_path / "empty.txt"
    f.write_text("   \n  ")

    assert load_document(f) is None


def test_iter_documents_over_directory(tmp_path: Path):
    (tmp_path / "a.txt").write_text("A content")
    (tmp_path / "b.md").write_text("# B content")
    (tmp_path / "skip.png").write_bytes(b"\x89PNG")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "c.txt").write_text("C content")

    docs = list(iter_documents(tmp_path))
    sources = {Path(d.source).name for d in docs}

    assert sources == {"a.txt", "b.md", "c.txt"}


def test_iter_documents_on_single_file(tmp_path: Path):
    f = tmp_path / "solo.txt"
    f.write_text("Solo content")

    docs = list(iter_documents(f))

    assert len(docs) == 1
    assert docs[0].text == "Solo content"
