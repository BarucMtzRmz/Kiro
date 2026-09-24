from kiro.chunking import chunk_text


def test_empty_text_returns_no_chunks():
    assert chunk_text("") == []
    assert chunk_text("   \n\n  ") == []


def test_short_text_returns_single_chunk():
    text = "This is a short document."
    assert chunk_text(text, chunk_size=1000, chunk_overlap=150) == [text]


def test_long_text_is_split_into_multiple_chunks():
    paragraphs = [f"Paragraph {i} " + ("word " * 30) for i in range(10)]
    text = "\n\n".join(paragraphs)

    chunks = chunk_text(text, chunk_size=200, chunk_overlap=50)

    assert len(chunks) > 1
    assert all(len(c) <= 200 + 50 for c in chunks)  # allow a little slack from overlap join
    # every paragraph's distinctive marker should show up somewhere
    for i in range(10):
        assert any(f"Paragraph {i} " in c for c in chunks)


def test_oversized_single_paragraph_is_hard_split():
    text = "x" * 5000
    chunks = chunk_text(text, chunk_size=1000, chunk_overlap=100)

    assert len(chunks) > 1
    assert all(len(c) <= 1000 for c in chunks)
    assert "".join(chunks).replace("", "") != ""
