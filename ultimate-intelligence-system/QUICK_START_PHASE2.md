# Quick Start - Phase 2 Data Extraction Layer

## Prerequisites

Ensure you have your Anthropic API key configured:

```bash
# Create or edit .env file
ANTHROPIC_API_KEY=your_api_key_here
```

## Run Everything

### **Method 1: Run All Tests (Recommended)**
```bash
cd d:\udc\ultimate-intelligence-system
python run_phase2_tests.py
```

**Expected Output**:
```
✅ Python extraction test passed
✅ LLM extraction test passed
✅ Extraction node test passed
✅ Synthesis test passed
✅ Synthesis without facts test passed
✅ Synthesis node integration test passed

🎉 ALL PHASE 2 TESTS PASSED SUCCESSFULLY
```

### **Method 2: Run Live Demo**
```bash
cd d:\udc\ultimate-intelligence-system
python main.py
```

**Expected Output**:
```
📝 Query: How is UDC's financial performance?
📊 Complexity: medium
⏱️  Time: 5.88s
🎯 Confidence: 95%

📈 Extracted Facts:
  • revenue: 1032.1 QR millions (95% confidence)
  • net_profit: 89.5 QR millions (95% confidence)
  • operating_cash_flow: -460.5 QR millions (95% confidence)

💡 Key Insights:
  • Revenue was [Per extraction: QR 1,032.1m]
  • Net Profit was [Per extraction: QR 89.5m]
  • Operating Cash Flow was [Per extraction: -QR 460.5m]
```

### **Method 3: Run Individual Tests**
```bash
# Test extraction only
python -m pytest tests/test_extraction.py -v

# Test synthesis only
python -m pytest tests/test_synthesis.py -v

# Run all tests with pytest
python -m pytest tests/ -v
```

## Verify Installation

If you encounter import errors, install dependencies:

```bash
pip install -r requirements.txt
```

## What to Look For

### ✅ **Success Indicators**

1. **All tests pass** (6/6 tests green)
2. **Extractions work**: Python finds 3 metrics (revenue, profit, cash flow)
3. **Citations present**: All numbers have `[Per extraction: ...]`
4. **No fabrication**: System says "NOT IN DATA" when info missing
5. **Confidence scores**: 95-98% for validated facts

### ❌ **Potential Issues**

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'src'` | Run from project root: `cd d:\udc\ultimate-intelligence-system` |
| `No module named 'langchain_anthropic'` | Install dependencies: `pip install -r requirements.txt` |
| `API key not found` | Create `.env` file with `ANTHROPIC_API_KEY=...` |
| `Model not found error` | Check `src/config/settings.py` - should use `claude-3-haiku-20240307` |

## File Structure

```
ultimate-intelligence-system/
├── src/
│   ├── nodes/
│   │   ├── classify.py      # Phase 1: Query classification
│   │   ├── extract.py       # Phase 2: Data extraction ⭐
│   │   └── synthesis.py     # Phase 2: Citation-enforcing synthesis ⭐
│   ├── graph/
│   │   └── workflow.py      # Graph: classify → extract → synthesis
│   ├── models/
│   │   └── state.py         # State schema
│   └── config/
│       └── settings.py      # Model config
├── tests/
│   ├── test_extraction.py   # Extraction tests ⭐
│   └── test_synthesis.py    # Synthesis tests ⭐
├── main.py                  # End-to-end demo
├── run_phase2_tests.py      # Test runner ⭐
└── requirements.txt         # Dependencies
```

⭐ = New in Phase 2

## Key Commands

```bash
# Full test suite
python run_phase2_tests.py

# Live demo
python main.py

# Check logs
tail -f logs/intelligence_*.log

# Run with verbose output
python main.py -v
```

## What Each Component Does

### **1. Extract Node** (`src/nodes/extract.py`)
- **Layer 1**: Python regex finds numbers (fast, deterministic)
- **Layer 2**: LLM extracts with context (accurate, structured)
- **Layer 3**: Cross-validates both (resolves conflicts)
- **Output**: Validated facts with confidence scores

### **2. Synthesis Node** (`src/nodes/synthesis.py`)
- **Input**: Extracted facts only (never raw data)
- **Process**: LLM creates CEO-ready intelligence
- **Enforcement**: Must cite every number as `[Per extraction: ...]`
- **Output**: Strategic analysis with mandatory citations

### **3. Workflow** (`src/graph/workflow.py`)
- **Flow**: classify → extract → synthesis → end
- **State**: Passes through graph immutably
- **Tracking**: Logs every node execution

## Quick Verification

Run this to verify everything works:

```bash
cd d:\udc\ultimate-intelligence-system
python run_phase2_tests.py && python main.py
```

If you see:
```
✅ ALL PHASE 2 TESTS PASSED SUCCESSFULLY
```

...and then query results with proper citations → **You're ready!**

## Next Steps

- ✅ Phase 1: Basic graph (classify node)
- ✅ Phase 2: Data extraction layer ⭐ **YOU ARE HERE**
- 🔜 Phase 3: Specialized agent nodes
- 🔜 Phase 4: Debate & critique layer
- 🔜 Phase 5: Verification layer
- 🔜 Phase 6: Final synthesis

---

**Questions?** Check `PHASE_2_COMPLETE.md` for detailed documentation or `PHASE_2_SUCCESS_SUMMARY.md` for results.
