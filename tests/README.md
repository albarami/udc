# Knowledge Base Test Suite

This directory contains unit tests for the `UDCCompleteKnowledgeBase` service.

Key details:
- Tests run against lightweight in-memory fakes for ChromaDB and the sentence transformer embedding function, so they do not require torch or external services.
- Fixtures are provided via `tests/conftest.py`; import paths for the backend package are set up automatically.
- Run the suite with `pytest` from the repository root.

