"""Dependency-free text chunking and lexical retrieval."""

import re
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Chunk:
    source: str
    index: int
    text: str


def chunk_text(text: str, source: str = "text", size: int = 800, overlap: int = 100) -> list[Chunk]:
    """Split text into bounded overlapping chunks, retaining whitespace content."""
    if size <= 0:
        raise ValueError("chunk size must be greater than zero")
    if overlap < 0 or overlap >= size:
        raise ValueError("overlap must be non-negative and smaller than chunk size")
    if not text.strip():
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            boundary = text.rfind(" ", start, end)
            if boundary > start:
                end = boundary
        content = text[start:end].strip()
        if content:
            chunks.append(Chunk(source=source, index=len(chunks), text=content))
        if end >= len(text):
            break
        next_start = max(start + 1, end - overlap)
        if next_start > 0 and not text[next_start - 1].isspace():
            previous_boundary = text.rfind(" ", start, next_start)
            if previous_boundary >= start:
                next_start = previous_boundary + 1
            else:
                next_boundary = text.find(" ", next_start, end)
                if next_boundary >= 0:
                    next_start = next_boundary + 1
        if next_start <= start:
            raise ValueError("chunking made no progress; reduce overlap")
        start = next_start
    return chunks


def _tokens(text: str) -> set[str]:
    return {token.lower() for token in re.findall(r"\w+", text) if len(token) > 1}


def retrieve(query: str, chunks: Iterable[Chunk], limit: int = 3) -> list[Chunk]:
    """Rank chunks by query-term coverage, returning deterministic top matches."""
    if limit <= 0:
        raise ValueError("result limit must be greater than zero")
    query_tokens = _tokens(query)
    if not query_tokens:
        raise ValueError("query must contain at least one searchable term")
    scored = []
    for chunk in chunks:
        chunk_tokens = _tokens(chunk.text)
        score = len(query_tokens & chunk_tokens)
        if score:
            scored.append((score, chunk.source, chunk.index, chunk))
    scored.sort(key=lambda item: (-item[0], item[1], item[2]))
    return [item[3] for item in scored[:limit]]
