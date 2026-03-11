#!/usr/bin/env python3
"""
ingest.py — Simple document ingestion script.
Reads all .txt files from a folder and simulates indexing them.
"""

import os
import sys
import hashlib
from pathlib import Path
from datetime import datetime

TEXTS_DIR = Path(__file__).parent / "texts"


def load_document(path: Path) -> dict:
    content = path.read_text(encoding="utf-8").strip()
    doc_id = hashlib.md5(content.encode()).hexdigest()[:8]
    return {
        "id": doc_id,
        "filename": path.name,
        "content": content,
        "chars": len(content),
        "lines": content.count("\n") + 1,
    }


def chunk_text(text: str, chunk_size: int = 200, overlap: int = 40) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def simulate_index(doc: dict) -> list[dict]:
    chunks = chunk_text(doc["content"])
    return [
        {
            "doc_id": doc["id"],
            "chunk_index": i,
            "preview": chunk[:60].replace("\n", " ") + "...",
        }
        for i, chunk in enumerate(chunks)
    ]


def main():
    print(f"[{datetime.now().isoformat()}] Starting ingestion")
    print(f"Reading from: {TEXTS_DIR}\n")

    if not TEXTS_DIR.exists():
        print(f"ERROR: Directory '{TEXTS_DIR}' not found.", file=sys.stderr)
        sys.exit(1)

    txt_files = sorted(TEXTS_DIR.glob("*.txt"))
    if not txt_files:
        print("No .txt files found. Nothing to ingest.")
        sys.exit(0)

    total_chunks = 0

    for path in txt_files:
        doc = load_document(path)
        chunks = simulate_index(doc)
        total_chunks += len(chunks)

        print(f"  [{doc['id']}] {doc['filename']}")
        print(
            f"    {doc['chars']} chars | {doc['lines']} lines | {len(chunks)} chunk(s)"
        )
        for chunk in chunks:
            print(f"      chunk {chunk['chunk_index']}: \"{chunk['preview']}\"")
        print()

    print(
        f"[{datetime.now().isoformat()}] Done — {len(txt_files)} doc(s), {total_chunks} total chunk(s) indexed."
    )


if __name__ == "__main__":
    main()
