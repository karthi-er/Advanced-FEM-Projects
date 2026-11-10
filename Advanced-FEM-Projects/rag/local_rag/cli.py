"""CLI for local retrieval and optional Anthropic answer generation."""

import argparse
import os
import sys
from pathlib import Path

from .index import chunk_text, retrieve


def _read_document(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ValueError(f"cannot read document '{path}': {exc}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description="Retrieve relevant passages from local text files.")
    parser.add_argument("question", help="Question or search phrase")
    parser.add_argument("documents", nargs="+", help="Plain-text documents")
    parser.add_argument("--limit", type=int, default=3, help="Maximum passages to show")
    parser.add_argument("--answer", action="store_true", help="Ask Anthropic to answer using retrieved passages")
    args = parser.parse_args()
    try:
        chunks = []
        for name in args.documents:
            path = Path(name)
            chunks.extend(chunk_text(_read_document(path), source=str(path)))
        matches = retrieve(args.question, chunks, limit=args.limit)
        if not matches:
            print("No matching passages found.")
            return 0
        print("Retrieved passages (lexical matching):")
        for match in matches:
            print(f"\n[{match.source}#{match.index}]\n{match.text}")
        if args.answer:
            if not os.environ.get("ANTHROPIC_API_KEY"):
                raise ValueError("--answer requires ANTHROPIC_API_KEY")
            try:
                import anthropic
            except ImportError as exc:
                raise ValueError("install the optional dependency with: pip install -e .[claude]") from exc
            context = "\n\n".join(match.text for match in matches)
            try:
                response = anthropic.Anthropic().messages.create(
                    model="claude-3-5-haiku-latest",
                    max_tokens=500,
                    messages=[{"role": "user", "content": (
                        f"Answer using only this context. Say when it is insufficient.\n\n"
                        f"Context:\n{context}\n\nQuestion: {args.question}"
                    )}],
                )
            except anthropic.APIError as exc:
                raise ValueError(f"Anthropic request failed: {exc}") from exc
            print("\nClaude answer:")
            for block in response.content:
                if getattr(block, "type", None) == "text":
                    print(block.text)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
