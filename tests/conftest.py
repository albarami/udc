"""Shared fixtures and utilities for the test suite."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

import pytest


class DummyEmbeddingFunction:
    """Lightweight embedding function stub used for tests."""

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name

    def __call__(self, texts: Sequence[str]) -> List[List[float]]:
        return [[float(len(text))] for text in texts]


@dataclass
class StoredRecord:
    """Container for stored collection data."""

    id: str
    document: str
    metadata: Dict[str, Any]


class InMemoryCollection:
    """Minimal Chroma-like collection for deterministic tests."""

    def __init__(self, name: str) -> None:
        self.name = name
        self._records: Dict[str, StoredRecord] = {}

    def count(self) -> int:
        return len(self._records)

    def upsert(
        self,
        *,
        documents: Sequence[str],
        metadatas: Sequence[Dict[str, Any]],
        ids: Sequence[str],
    ) -> None:
        for doc, metadata, key in zip(documents, metadatas, ids):
            self._records[key] = StoredRecord(key, doc, dict(metadata))

    def get(
        self,
        *,
        where: Dict[str, Any] | None = None,
        limit: int | None = None,
    ) -> Dict[str, List[Any]]:
        filtered = [
            record
            for record in self._records.values()
            if self._match(record.metadata, where)
        ]
        if limit is not None:
            filtered = filtered[:limit]

        return {
            "ids": [record.id for record in filtered],
            "metadatas": [record.metadata for record in filtered],
            "documents": [record.document for record in filtered],
        }

    def query(
        self,
        *,
        query_texts: Sequence[str],
        n_results: int,
        where: Dict[str, Any] | None = None,
    ) -> Dict[str, List[List[Any]]]:
        query = query_texts[0].lower()
        candidates: List[Tuple[float, StoredRecord]] = []
        for record in self._records.values():
            if not self._match(record.metadata, where):
                continue
            distance = self._distance(query, record.document.lower())
            candidates.append((distance, record))

        candidates.sort(key=lambda item: item[0])
        selected = candidates[:n_results]

        if not selected:
            empty = [[]]
            return {"ids": empty, "documents": empty, "metadatas": empty, "distances": empty}

        ids = [[record.id for _, record in selected]]
        documents = [[record.document for _, record in selected]]
        metadatas = [[record.metadata for _, record in selected]]
        distances = [[distance for distance, _ in selected]]

        return {
            "ids": ids,
            "documents": documents,
            "metadatas": metadatas,
            "distances": distances,
        }

    @staticmethod
    def _match(metadata: Dict[str, Any], criteria: Dict[str, Any] | None) -> bool:
        if not criteria:
            return True
        return all(metadata.get(key) == value for key, value in criteria.items())

    @staticmethod
    def _distance(query: str, document: str) -> float:
        if not document:
            return 1.0
        overlap = sum(1 for token in query.split() if token and token in document)
        if overlap == 0:
            return 0.95
        score = min(0.9, overlap / max(1, len(set(query.split()))))
        return round(1.0 - score, 4)


class FakePersistentClient:
    """Stub for chromadb.PersistentClient."""

    def __init__(self, path: str) -> None:
        self.path = path
        self._collections: Dict[str, InMemoryCollection] = {}

    def get_or_create_collection(
        self,
        name: str,
        embedding_function: Any | None = None,
        metadata: Dict[str, Any] | None = None,
    ) -> InMemoryCollection:
        if name not in self._collections:
            self._collections[name] = InMemoryCollection(name)
        return self._collections[name]

    def delete_collection(self, name: str) -> None:
        self._collections.pop(name, None)


@pytest.fixture
def knowledge_base(monkeypatch: pytest.MonkeyPatch, tmp_path):
    """Return a knowledge base instance backed by in-memory stubs."""
    repo_root = Path(__file__).resolve().parents[1]
    backend_path = repo_root / "backend"
    if str(backend_path) not in sys.path:
        sys.path.insert(0, str(backend_path))

    from app.services import knowledge_base_complete

    monkeypatch.setattr(
        knowledge_base_complete.embedding_functions,
        "SentenceTransformerEmbeddingFunction",
        DummyEmbeddingFunction,
    )
    monkeypatch.setattr(
        knowledge_base_complete.chromadb,
        "PersistentClient",
        FakePersistentClient,
    )

    kb = knowledge_base_complete.UDCCompleteKnowledgeBase(
        persist_directory=str(tmp_path / "chromadb")
    )
    return kb
