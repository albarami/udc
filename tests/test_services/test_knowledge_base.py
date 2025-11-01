"""Tests for the UDCCompleteKnowledgeBase service."""

from __future__ import annotations

from typing import Dict, List

import pytest


def _sample_pdf_documents() -> List[Dict]:
    return [
        {
            "source": "Annual Report 2024.pdf",
            "category": "finance",
            "total_pages": 1,
            "pages": [
                {
                    "page_number": 1,
                    "text": (
                        "UDC recorded strong revenue growth in 2024. "
                        "The debt to equity ratio improved to 0.42. "
                        "Investments in Gewan Island continued to accelerate."
                    ),
                }
            ],
        }
    ]


def _sample_excel_documents() -> List[Dict]:
    return [
        {
            "source": "financials.xlsx",
            "sheets": {
                "Summary": {
                    "columns": ["Metric", "Value"],
                    "rows": 2,
                    "column_count": 2,
                    "data": [
                        {"Metric": "Debt to Equity", "Value": "0.42"},
                        {"Metric": "Revenue", "Value": "QAR 500M"},
                    ],
                    "summary": {"statistics": {"Debt to Equity": 0.42}},
                }
            },
        }
    ]


def test_statistics_empty_collection(knowledge_base):
    """Knowledge base statistics default to zero when empty."""
    stats = knowledge_base.get_statistics()

    assert stats["total_documents"] == 0
    assert stats["pdf_chunks"] == 0
    assert stats["excel_sheets"] == 0
    assert stats["collection_name"] == "udc_intelligence"


def test_ingest_pdf_documents_populates_collection(knowledge_base):
    """PDF ingestion stores chunk metadata and documents."""
    knowledge_base.ingest_pdf_documents(_sample_pdf_documents())

    results = knowledge_base.collection.get(where={"type": "pdf"}, limit=10)

    assert knowledge_base.collection.count() == 1
    assert results["ids"][0].startswith("pdf_annual_report_2024")
    assert results["metadatas"][0]["page"] == 1
    assert results["metadatas"][0]["category"] == "finance"


def test_ingest_excel_data_populates_collection(knowledge_base):
    """Excel ingestion stores sheet summaries."""
    knowledge_base.ingest_excel_data(_sample_excel_documents())

    results = knowledge_base.collection.get(where={"type": "excel"}, limit=10)

    assert len(results["ids"]) == 1
    metadata = results["metadatas"][0]
    assert metadata["sheet"] == "Summary"
    assert metadata["rows"] == 2
    assert metadata["columns"] == 2


def test_search_returns_results_with_citations(knowledge_base):
    """Semantic search returns formatted results with metadata."""
    knowledge_base.ingest_pdf_documents(_sample_pdf_documents())
    knowledge_base.ingest_excel_data(_sample_excel_documents())

    results = knowledge_base.search(
        "What is the debt to equity ratio?", n_results=2
    )

    assert results, "Expected at least one search result"
    first = results[0]
    assert first["citation"].startswith("Annual Report 2024.pdf")
    assert first["metadata"]["type"] == "pdf"
    assert 0 <= first["relevance_score"] <= 100


def test_clear_collection_resets_store(knowledge_base):
    """Clearing the collection removes all stored data."""
    knowledge_base.ingest_pdf_documents(_sample_pdf_documents())
    assert knowledge_base.collection.count() > 0

    knowledge_base.clear_collection()

    assert knowledge_base.collection.count() == 0


def test_smart_chunk_respects_word_limit(knowledge_base):
    """Smart chunking splits long text while respecting the word limit."""
    long_text = (
        "UDC invested heavily in infrastructure during 2024. "
        "Revenue diversification remained a strategic priority. "
        "The management team monitored liquidity and leverage closely. "
        "Shareholder value initiatives continued throughout the year. "
        "Sustainability projects advanced across multiple business units."
    )

    chunks = knowledge_base._smart_chunk(long_text, max_words=12)

    assert len(chunks) >= 2
    assert all(len(chunk.split()) <= 12 for chunk in chunks)

