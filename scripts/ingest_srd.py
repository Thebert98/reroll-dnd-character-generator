#!/usr/bin/env python3
"""One-off SRD 5.1 ingestion (not a deployed worker).

Parses a directory of SRD 5.1 markdown files, splits them into semantically
clean chunks (one spell / one class feature per chunk — *not* fixed token
windows, which retrieve far worse for rules), embeds each chunk with
text-embedding-3-small, and inserts into ``documents`` / ``document_chunks``.

Usage:
    python scripts/ingest_srd.py --srd-dir path/to/srd-markdown
    python scripts/ingest_srd.py --srd-dir scripts/sample_srd   # small demo corpus

The SRD 5.1 markdown is available under CC-BY-4.0 (e.g. github.com/OldManUmby/
DND.SRD.Wiki). Never ingest the PHB or other copyrighted books.

Requires SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY and OPENAI_API_KEY in env
(the service-role key bypasses RLS to write the shared corpus).
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# Make the backend package importable when run from the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.db import service_client            # noqa: E402
from app.rag.chunking import parse_markdown_chunks  # noqa: E402
from app.rag.embeddings import embed_batch    # noqa: E402

EMBED_BATCH = 96


def gather_chunks(srd_dir: Path) -> list[dict]:
    all_chunks: list[dict] = []
    md_files = sorted(srd_dir.rglob("*.md"))
    if not md_files:
        raise SystemExit(f"No .md files found under {srd_dir}")
    for path in md_files:
        label = path.stem.replace("-", " ").replace("_", " ").title()
        text = path.read_text(encoding="utf-8")
        all_chunks.extend(parse_markdown_chunks(text, label))
    return all_chunks


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--srd-dir", required=True, type=Path)
    ap.add_argument("--title", default="SRD 5.1")
    ap.add_argument("--license", default="CC-BY-4.0")
    ap.add_argument("--reset", action="store_true",
                    help="Delete existing chunks for this document title first.")
    args = ap.parse_args()

    if not os.getenv("SUPABASE_SERVICE_ROLE_KEY") or not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("Set SUPABASE_SERVICE_ROLE_KEY and OPENAI_API_KEY in env.")

    db = service_client()
    chunks = gather_chunks(args.srd_dir)
    print(f"Parsed {len(chunks)} chunks from {args.srd_dir}")

    # Upsert the document row.
    if args.reset:
        db.table("documents").delete().eq("title", args.title).execute()
    doc = db.table("documents").insert(
        {"title": args.title, "license": args.license}
    ).execute()
    document_id = doc.data[0]["id"]

    inserted = 0
    for i in range(0, len(chunks), EMBED_BATCH):
        batch = chunks[i : i + EMBED_BATCH]
        embeddings = embed_batch([c["content"] for c in batch])
        rows = [
            {
                "document_id": document_id,
                "section": c["section"],
                "content": c["content"],
                "embedding": emb,
            }
            for c, emb in zip(batch, embeddings)
        ]
        db.table("document_chunks").insert(rows).execute()
        inserted += len(rows)
        print(f"  inserted {inserted}/{len(chunks)}")

    print(f"Done. Ingested {inserted} chunks as document '{args.title}'.")


if __name__ == "__main__":
    main()
