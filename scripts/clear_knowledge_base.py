"""
Utility to clear the persistent Chroma knowledge base.

Use this when you need to wipe the collection before a fresh ingestion run.
"""

import argparse
import sys
from pathlib import Path

# Ensure backend package is importable when running as a script
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.services.knowledge_base_complete import UDCCompleteKnowledgeBase


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Clear the UDC knowledge base collection."
    )
    parser.add_argument(
        "--persist-directory",
        default="D:/udc/data/chromadb",
        help="Path to the ChromaDB persistence directory (default: %(default)s)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Bypass the confirmation prompt.",
    )
    return parser.parse_args()


def main() -> int:
    """Entrypoint for the CLI utility."""
    args = parse_args()

    if not args.force:
        prompt = (
            f"This will delete all data in '{args.persist_directory}'. "
            "Type 'yes' to continue: "
        )
        if input(prompt).strip().lower() != "yes":
            print("Aborted.")
            return 1

    kb = UDCCompleteKnowledgeBase(persist_directory=args.persist_directory)
    kb.clear_collection()
    print("Knowledge base cleared.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
