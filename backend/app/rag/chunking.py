"""Markdown chunking for SRD ingestion — pure, dependency-free, unit-tested.

Chunks by logical unit (heading sections), not fixed token windows: one spell or
one class feature per chunk retrieves far better for rules lookups.
"""
from __future__ import annotations

import re

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
MIN_CHUNK_CHARS = 40


def parse_markdown_chunks(text: str, file_label: str) -> list[dict]:
    """Split markdown into ``[{section, content}]`` keyed on heading hierarchy.

    Each chunk's ``section`` is a breadcrumb like 'Spells > Fireball'; the body
    is the text under that heading until the next heading of equal/higher level.
    The breadcrumb is prepended to the content so retrieval and the LLM both see
    the section label.
    """
    chunks: list[dict] = []
    breadcrumb: list[str] = []
    levels: list[int] = []
    current: list[str] = []

    def flush() -> None:
        body = "\n".join(current).strip()
        if body and len(body) >= MIN_CHUNK_CHARS:
            section = " > ".join(breadcrumb) or file_label
            chunks.append({"section": section, "content": f"{section}\n\n{body}"})

    for line in text.splitlines():
        m = HEADING_RE.match(line)
        if m:
            flush()
            current = []
            level = len(m.group(1))
            title = m.group(2).strip()
            while levels and levels[-1] >= level:
                levels.pop()
                breadcrumb.pop()
            levels.append(level)
            breadcrumb.append(title)
        else:
            current.append(line)
    flush()
    return chunks
