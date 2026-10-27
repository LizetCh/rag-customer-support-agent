from app.rag.chunking import chunk_markdown

DOC = """# Shipping

We ship fresh bread.

## Shipping costs

Orders under $75: flat rate of $12.

## Empty section

## Local delivery

We deliver within 10 miles.
"""


def test_one_chunk_per_section_plus_intro():
    assert chunk_markdown(DOC) == [
        "Shipping\n\nWe ship fresh bread.",
        "Shipping > Shipping costs\n\nOrders under $75: flat rate of $12.",
        "Shipping > Local delivery\n\nWe deliver within 10 miles.",
    ]


def test_doc_without_intro_has_no_title_only_chunk():
    chunks = chunk_markdown("# Hours\n\n## Regular hours\n\nOpen 7 AM.\n")
    assert chunks == ["Hours > Regular hours\n\nOpen 7 AM."]
