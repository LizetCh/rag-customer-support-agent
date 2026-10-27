"""Structure-aware chunking: one chunk per `## ` section of a Markdown doc."""


def chunk_markdown(text: str) -> list[str]:
    """Split a Markdown doc at each `## ` heading.

    Each chunk starts with "<doc title> > <section heading>" so a short chunk
    like "Orders under $75: flat rate of $12." still says what it is about.
    Text between the `# ` title and the first `## ` becomes its own chunk.
    """
    title = ""
    sections: list[tuple[str, list[str]]] = [("", [])]

    for line in text.splitlines():
        if line.startswith("# ") and not title:
            title = line[2:].strip()
        elif line.startswith("## "):
            sections.append((line[3:].strip(), []))
        else:
            sections[-1][1].append(line)

    chunks = []
    for heading, lines in sections:
        body = "\n".join(lines).strip()
        if not body:
            continue
        header = f"{title} > {heading}" if heading else title
        chunks.append(f"{header}\n\n{body}")
    return chunks
