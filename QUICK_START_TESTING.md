# UDC Polaris - Quick Start Testing Guide

**Get testing in 5 minutes!**

---

## Prerequisites

- Python 3.11+
- UDC Polaris project cloned locally
- Basic familiarity with pytest

---

## 1. Install Test Dependencies (2 minutes)

```bash
# Navigate to project root
cd /path/to/udc

# Install test dependencies
pip install pytest pytest-asyncio pytest-cov pytest-mock
```

**Verify Installation:**
```bash
pytest --version
# Should show: pytest 7.4.0 or higher
```

---

## 2. Run Your First Test (1 minute)

```bash
# Run simple smoke tests (4 tests, ~5 seconds)
pytest tests/test_simple.py -v
```

**Expected Output:**
```
tests/test_simple.py::test_settings_load PASSED
tests/test_simple.py::test_udc_tools_available PASSED  
tests/test_simple.py::test_sample_data_access PASSED
tests/test_simple.py::test_search_functionality PASSED

======================== 4 passed in 2.1s ========================
```

✅ **Success!** Your test environment is working.

---

## 3. Run Full Test Suite (1 minute)

```bash
# Run all tests (10 tests total)
pytest -v
```

**What Happens:**
- **Simple tests**: 4 tests, ~5 seconds ✅ 
- **Knowledge base tests**: 6 tests, ~3m 44s ⏳

**Expected Output:**
```
tests/test_simple.py::test_settings_load PASSED
tests/test_simple.py::test_udc_tools_available PASSED
tests/test_simple.py::test_sample_data_access PASSED  
tests/test_simple.py::test_search_functionality PASSED
tests/test_services/test_knowledge_base.py::test_statistics_empty_collection PASSED
tests/test_services/test_knowledge_base.py::test_ingest_pdf_documents_populates_collection PASSED
tests/test_services/test_knowledge_base.py::test_ingest_excel_data_populates_collection PASSED
tests/test_services/test_knowledge_base.py::test_search_returns_results_with_citations PASSED
tests/test_services/test_knowledge_base.py::test_clear_collection_resets_store PASSED
tests/test_services/test_knowledge_base.py::test_smart_chunk_respects_word_limit PASSED

======================== 10 passed in 3m 44s ========================
```

✅ **Perfect!** All tests are passing.

---

## 4. Common Test Commands (1 minute)

### Quick Commands
```bash
# Run only fast tests
pytest tests/test_simple.py

# Run with coverage report
pytest --cov=app

# Stop at first failure  
pytest -x

# Show detailed output
pytest -vvs
```

### Debugging Tests
```bash
# Drop into debugger on failure
pytest --pdb

# Run specific test
pytest tests/test_simple.py::test_settings_load

# Show print statements
pytest -s
```

---

## 5. Understanding Test Results

### ✅ **PASSED** - Test succeeded
```
tests/test_simple.py::test_settings_load PASSED
```

### ❌ **FAILED** - Test failed
```
tests/test_simple.py::test_something FAILED

> AssertionError: Expected 'UDC Polaris' but got 'Unknown'
```

### ⚠️ **SKIPPED** - Test skipped (usually missing dependencies)
```
tests/test_simple.py::test_sample_data_access SKIPPED
# Reason: Sample data not available
```

---

## 6. What Each Test File Does

### `tests/test_simple.py` (4 tests, ~5 seconds)
- ✅ **Settings Load**: Configuration system works
- ✅ **Tools Available**: Data tools are accessible  
- ✅ **Sample Data**: Basic data access works
- ✅ **Search**: Simple search functionality works

### `tests/test_services/test_knowledge_base.py` (6 tests, ~3m 44s)
- ✅ **Empty Statistics**: Knowledge base initializes correctly
- ✅ **PDF Ingestion**: Documents can be processed and stored
- ✅ **Excel Ingestion**: Spreadsheet data can be processed  
- ✅ **Search Results**: Semantic search returns proper citations
- ✅ **Clear Collection**: Data can be removed properly
- ✅ **Smart Chunking**: Text is split intelligently

---

## 7. Troubleshooting

### ❌ **Import Errors**
```bash
# Error: ModuleNotFoundError: No module named 'app'
# Solution: Run from project root directory
cd /path/to/udc
pytest
```

### ❌ **Slow Tests**
```bash
# Problem: Knowledge base tests take 3+ minutes
# Solution: Run only fast tests during development
pytest tests/test_simple.py
```

### ❌ **Missing Dependencies**
```bash
# Error: No module named 'pytest'
# Solution: Install test dependencies
pip install pytest pytest-asyncio pytest-cov
```

### ❌ **All Tests Skip**
```bash
# Problem: "Sample data not available" 
# Expected: This is normal in fresh environments
# Tests will still verify core functionality
```

---

## 8. Next Steps

### For Developers
1. **Read**: [Full Testing Guide](TESTING_GUIDE.md)
2. **Write**: Add tests for new features
3. **Run**: `pytest` before every commit

### For Contributors  
1. **Coverage**: Aim for >80% test coverage
2. **Speed**: Keep tests fast and focused
3. **Documentation**: Update tests with code changes

### For CI/CD
```yaml
# Add to GitHub Actions
- name: Run Tests
  run: pytest --cov=app --cov-report=xml
```

---

## Quick Reference Card

```bash
# Most Common Commands
pytest                    # Run all tests
pytest -v                 # Verbose output
pytest tests/test_simple.py  # Fast tests only
pytest -x                 # Stop at first failure
pytest --cov=app          # With coverage
```

**Test Files:**
- `tests/test_simple.py` → 4 tests, ~5 seconds  
- `tests/test_services/test_knowledge_base.py` → 6 tests, ~3m 44s

**Total:** 10 tests, ~3m 50s execution time

---

**🎉 You're ready to test UDC Polaris!**

For detailed information, see [TESTING_GUIDE.md](TESTING_GUIDE.md)
