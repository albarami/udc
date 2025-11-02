# Quick Start Guide

## Installation

```bash
cd ultimate-intelligence-system
pip install -r requirements.txt
```

## Configuration

1. Copy environment template:
```bash
cp .env.example .env
```

2. Add your Anthropic API key to `.env`:
```
ANTHROPIC_API_KEY=your_actual_api_key_here
```

## Run the System

```bash
python main.py
```

Expected output: 3 test queries processed with classifications

## Run Tests

```bash
# All tests
pytest

# Verbose output
pytest -v

# Specific test file
pytest tests/test_nodes.py -v
```

## Project Structure

```
src/
├── config/          Configuration & settings
├── models/          State schema (IntelligenceState)
├── nodes/           Graph nodes (classify, extract, synthesis)
├── utils/           Logging & helpers
└── graph/           LangGraph workflow

tests/               Unit & integration tests
data/                Sample queries
logs/                Auto-generated execution logs
```

## Current Capabilities

### Query Classification ✅
- **Simple**: "What was the revenue?"
- **Medium**: "How is financial performance?"
- **Complex**: "Should we enter the market?"
- **Critical**: "Stock dropped - urgent!"

### Graph Execution ✅
- State-driven architecture
- Transparent reasoning chains
- Comprehensive logging
- Error tracking

## Phase 1 Status

✅ Foundation complete
✅ All tests passing (8/8)
✅ Logging working
✅ Classification working

## Next Steps

**Phase 2 (Days 2-5):** Data extraction layer
- Python-based numeric extraction
- LLM fact extraction
- Zero fabrication enforcement
- Cross-source validation

## Troubleshooting

### Import Warnings in IDE
The IDE may show import resolution warnings. These are expected and won't affect runtime. The code runs successfully as verified by passing tests.

### Missing API Key
If you see errors about ANTHROPIC_API_KEY, ensure you've:
1. Created `.env` file from `.env.example`
2. Added your actual API key

### Dependencies
If tests fail, reinstall dependencies:
```bash
pip install -r requirements.txt --force-reinstall
```

## Documentation

- `README.md` - Project overview
- `PHASE1_DAY1_COMPLETE.md` - Detailed completion report
- `ULTIMATE_SYSTEM_IMPLEMENTATION_PLAN.md` - Full system plan (in parent directory)

## Support

For issues or questions, refer to:
1. Test files in `tests/` for usage examples
2. Log files in `logs/` for execution details
3. Implementation plan for architecture details

---

**Phase 1 Complete** ✅ | **Ready for Phase 2** 🚀
