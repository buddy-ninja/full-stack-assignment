"""Loads the knowledge pack. Retrieval over it is yours to build."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Article:
    id: str
    title: str
    species: tuple[str, ...]
    topics: tuple[str, ...]
    body: str


def _parse_list(value: str) -> tuple[str, ...]:
    return tuple(v.strip() for v in value.strip().strip("[]").split(",") if v.strip())


def parse_article(text: str) -> Article:
    if not text.startswith("---\n"):
        raise ValueError("article must start with a front-matter block")
    header, body = text[4:].split("\n---\n", 1)
    meta = dict(line.split(":", 1) for line in header.splitlines() if line.strip())
    meta = {k.strip(): v.strip() for k, v in meta.items()}
    return Article(
        id=meta["id"],
        title=meta["title"],
        species=_parse_list(meta["species"]),
        topics=_parse_list(meta["topics"]),
        body=body.strip(),
    )


def load_articles(directory: str | Path | None = None) -> list[Article]:
    root = Path(directory or os.getenv("KNOWLEDGE_DIR", "../knowledge"))
    return [parse_article(p.read_text()) for p in sorted(root.glob("*.md"))]
