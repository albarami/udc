"""Quick smoke test for the UDC knowledge base.

Run this script to print high-level statistics and optionally execute a semantic
search query against the persisted ChromaDB instance.

Example:
    python scripts/test_knowledge_base.py --query "Gewan Island strategy"
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_PATH = PROJECT_ROOT / "backend"
if str(BACKEND_PATH) not in sys.path:
    sys.path.insert(0, str(BACKEND_PATH))

from app.services.knowledge_base_complete import UDCCompleteKnowledgeBase


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Smoke test the UDC knowledge base."
    )
    parser.add_argument(
        "-q",
        "--query",
        default="What is UDC's debt-to-equity ratio in 2024?",
        help="Semantic search query to run after printing statistics.",
    )
    parser.add_argument(
        "-n",
        "--n-results",
        type=int,
        default=3,
        help="Number of search results to display.",
    )
    parser.add_argument(
        "--stats-only",
        action="store_true",
        help="Only print knowledge base statistics without running a search.",
    )
    return parser.parse_args(argv)


def run_smoke_test(query: str | None, n_results: int) -> int:
    """Execute the smoke test workflow."""
    try:
        kb = UDCCompleteKnowledgeBase()
    except Exception as exc:  # pragma: no cover - diagnostic output
        print("=" * 80)
        print("ERROR: Failed to initialize the knowledge base.")
        print(f"Reason: {exc}")
        print("Tip: Verify torch / transformers compatibility and embeddings.")
        print("=" * 80)
        return 1

    stats = kb.get_statistics()

    print("=" * 80)
    print("KNOWLEDGE BASE STATUS")
    print("=" * 80)
    print(f"Total Documents: {stats.get('total_documents', 'unknown')}")
    print(f"PDF Chunks: {stats.get('pdf_chunks', 'unknown')}")
    print(f"Excel Sheets: {stats.get('excel_sheets', 'unknown')}")
    print(f"Storage: {stats.get('storage_path', 'unknown')}")
    print(f"Collection: {stats.get('collection_name', 'unknown')}")
    print(f"Last Updated: {stats.get('last_updated', 'unknown')}")
    print("=" * 80)

    if not query:
        return 0

    print("\nTesting semantic search...")
    try:
        results = kb.search(query, n_results=n_results)
    except Exception as exc:  # pragma: no cover - diagnostic output
        print("=" * 80)
        print("ERROR: Semantic search failed.")
        print(f"Query: {query}")
        print(f"Reason: {exc}")
        print("=" * 80)
        return 1

    print(f"\nFound {len(results)} results for: '{query}'")
    if not results:
        print("No results returned. Try a broader or different query.")
        return 0

    for idx, result in enumerate(results, start=1):
        citation = result.get("citation", "unknown source")
        relevance = result.get("relevance_score")
        relevance_display = f"{relevance}%" if relevance is not None else "n/a"
        print(f"\n[{idx}] {citation} (relevance: {relevance_display})")

        content = result.get("content", "")
        preview = (content[:200] + "...") if len(content) > 200 else content
        print(f"    {preview}")

    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Script entry point."""
    args = parse_args(argv)
    query = None if args.stats_only else args.query.strip()
    return run_smoke_test(query, args.n_results)


if __name__ == "__main__":
    raise SystemExit(main())

