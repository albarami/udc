# UDC Polaris Testing Guide

**Version:** 1.0  
**Last Updated:** October 31, 2025

---

## Overview

This guide covers the comprehensive testing strategy for the UDC Polaris Multi-Agent Strategic Intelligence System. Our testing approach ensures reliability, performance, and correctness of all system components.

## Testing Philosophy

### Core Principles
1. **Test-Driven Development**: Write tests before implementing features
2. **Comprehensive Coverage**: Unit, integration, and end-to-end testing
3. **Fast Feedback**: Quick test execution for rapid development
4. **Reliable Tests**: Deterministic, isolated, and maintainable tests

### Testing Pyramid
```
    /\
   /  \    End-to-End Tests (Few, High-Value)
  /____\
 /      \   Integration Tests (More, Key Workflows)  
/________\
|        |  Unit Tests (Many, Fast, Isolated)
|________|
```

## Test Suite Structure

### Directory Organization
```
tests/
├── conftest.py                 # Shared fixtures and test utilities
├── test_simple.py             # Simple smoke tests (4 tests)
├── test_services/             # Service layer tests
│   └── test_knowledge_base.py # Knowledge base tests (6 tests)
├── test_agents/               # Agent-specific tests [Future]
├── test_api/                  # API endpoint tests [Future]
└── test_integration/          # Integration tests [Future]
```

### Current Test Coverage

#### 1. Simple Smoke Tests (`test_simple.py`)
- **Purpose**: Basic functionality verification
- **Tests Count**: 4 tests
- **Execution Time**: ~5 seconds
- **Scope**:
  - Configuration loading
  - Data tools availability
  - Sample data access
  - Basic search functionality

#### 2. Knowledge Base Tests (`test_services/test_knowledge_base.py`)  
- **Purpose**: Comprehensive knowledge base testing
- **Tests Count**: 6 tests
- **Execution Time**: ~3m 44s
- **Scope**:
  - Document ingestion (PDF, Excel)
  - Semantic search accuracy
  - Collection management
  - Statistics and metadata
  - Text chunking algorithms

## Running Tests

### Prerequisites
```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov pytest-mock

# Ensure you're in the project root
cd /path/to/udc
```

### Basic Test Execution
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_simple.py

# Run specific test
pytest tests/test_simple.py::test_settings_load
```

### Advanced Options
```bash
# Run with coverage reporting
pytest --cov=app --cov-report=html

# Run tests in parallel
pytest -n auto

# Run only fast tests (skip slow knowledge base tests)
pytest -m "not slow"

# Stop at first failure
pytest -x
```

## Test Categories

### Unit Tests
- **Focus**: Individual functions and classes
- **Isolation**: Mock external dependencies
- **Speed**: < 1 second per test
- **Coverage**: Business logic, calculations, validations

### Integration Tests
- **Focus**: Component interactions
- **Dependencies**: Real services (ChromaDB, Redis)
- **Speed**: 1-30 seconds per test
- **Coverage**: Data flows, API contracts

### System Tests
- **Focus**: End-to-end workflows
- **Environment**: Full system deployment
- **Speed**: 30+ seconds per test
- **Coverage**: User scenarios, performance

## Testing Best Practices

### Writing Good Tests
1. **Arrange, Act, Assert** pattern
2. **Descriptive test names** that explain intent
3. **Single responsibility** per test
4. **Independent tests** that don't rely on each other
5. **Meaningful assertions** with clear error messages

### Test Data Management
```python
# Good: Use fixtures for reusable test data
@pytest.fixture
def sample_financial_data():
    return {
        "revenue": 1000000,
        "debt_ratio": 0.42
    }

# Good: Use parametrized tests for multiple scenarios
@pytest.mark.parametrize("debt_ratio,expected", [
    (0.30, "GREEN"),
    (0.45, "YELLOW"),
    (0.60, "RED")
])
def test_debt_status(debt_ratio, expected):
    assert calculate_debt_status(debt_ratio) == expected
```

### Mocking and Stubbing
```python
# Mock external API calls
@patch('app.services.anthropic_client.create')
def test_agent_response(mock_create):
    mock_create.return_value = Mock(content="Test response")
    # Test logic here

# Use test doubles for expensive operations
def test_knowledge_base_with_stub(knowledge_base_stub):
    # Test without hitting real ChromaDB
    pass
```

## Performance Testing

### Benchmarks
- **Agent Response Time**: < 10 seconds
- **Knowledge Base Search**: < 1 second
- **Document Processing**: < 5 minutes for full corpus
- **API Response Time**: < 2 seconds

### Load Testing
```bash
# API load testing with pytest-benchmark
pytest --benchmark-only tests/test_performance/
```

## Test Environment Setup

### Local Development
```bash
# Set test environment variables
export ENV=test
export DATABASE_URL=sqlite:///test.db
export ANTHROPIC_API_KEY=test_key

# Initialize test database
alembic upgrade head

# Run tests
pytest
```

### CI/CD Pipeline
- **Trigger**: On every pull request and merge
- **Environment**: Isolated container
- **Steps**:
  1. Install dependencies
  2. Setup test database
  3. Run linting (black, ruff)
  4. Execute test suite
  5. Generate coverage report
  6. Archive test results

## Debugging Failed Tests

### Common Issues
1. **Import Errors**: Check Python path and dependencies
2. **Database Conflicts**: Use separate test database
3. **Async Test Failures**: Ensure pytest-asyncio is configured
4. **Flaky Tests**: Check for race conditions and external dependencies

### Debug Commands
```bash
# Run with detailed output
pytest -vvs

# Drop into debugger on failure
pytest --pdb

# Show local variables in traceback
pytest --tb=long -l

# Run only failed tests from last run
pytest --lf
```

## Test Maintenance

### Regular Tasks
- **Weekly**: Review test coverage reports
- **Monthly**: Update test data and scenarios
- **Per Release**: Performance benchmark validation
- **Quarterly**: Test architecture review

### Quality Metrics
- **Code Coverage**: > 80% for critical paths
- **Test Success Rate**: > 95% on main branch
- **Test Performance**: No regression in execution time
- **Test Maintainability**: Regular refactoring of test code

## Future Enhancements

### Planned Additions
1. **Agent Behavior Tests**: Verify agent decision-making
2. **Multi-Agent Debate Tests**: Test agent interactions
3. **API Contract Tests**: Ensure API compatibility
4. **Performance Regression Tests**: Automated benchmarking
5. **Security Tests**: Vulnerability and penetration testing

---

**For more information:**
- [Quick Start Testing Guide](QUICK_START_TESTING.md)
- [Test Suite Documentation](TEST_SUITE_COMPLETE.md)
- [Contributing Guidelines](CONTRIBUTING.md)
