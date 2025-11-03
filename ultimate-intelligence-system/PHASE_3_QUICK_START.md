# Phase 3 Quick Start Guide

**Four PhD-level specialist agents providing expert analysis**

---

## 🚀 Quick Start (3 Steps)

### 1. Run Agent Tests
```bash
cd ultimate-intelligence-system
python tests/test_agents.py
```

**Expected Output:**
```
PHASE 3 AGENT TESTS
================================================================================

1. Testing Financial Economist...
   ✅ Financial agent: 1247 chars, 3 red flags, 85% confidence

2. Testing Market Economist...
   ✅ Market agent: 1156 chars, 2 opportunities, 80% confidence

3. Testing Operations Expert...
   ✅ Operations agent: 1089 chars, 4 risks, 85% confidence

4. Testing Research Scientist...
   ✅ Research agent: 1203 chars, 3 hypotheses, 75% confidence

✅ ALL AGENT TESTS PASSED
```

### 2. Run Full System
```bash
python main.py
```

**Expected Output:**
```
PHASE 3 DEMO: FULL MULTI-AGENT SYSTEM
================================================================================

Query: How is UDC's financial performance and should we be concerned?

MULTI-AGENT INTELLIGENCE REPORT
================================================================================

💼 FINANCIAL ECONOMIST ANALYSIS
--------------------------------------------------------------------------------
[Detailed financial analysis with citations]

📊 MARKET ECONOMIST ANALYSIS
--------------------------------------------------------------------------------
[Market context and competitive analysis]

⚙️ OPERATIONS EXPERT ANALYSIS
--------------------------------------------------------------------------------
[Operational feasibility assessment]

🔬 RESEARCH SCIENTIST ANALYSIS
--------------------------------------------------------------------------------
[Academic grounding and hypothesis generation]

✅ FINAL SYNTHESIS
--------------------------------------------------------------------------------
[CEO-ready integrated intelligence]
```

### 3. Use in Your Code
```python
from src.agents.financial_agent import FinancialEconomist

# Create agent
agent = FinancialEconomist()

# Analyze with extracted facts
result = await agent.analyze(
    query="What is UDC's revenue trend?",
    extracted_facts={
        'revenue': {
            'value': 1032.1,
            'unit': 'QR millions',
            'quote': 'Revenue: QR 1,032.1 million',
            'confidence': 0.95
        }
    },
    complexity="medium"
)

# Access results
print(result['analysis'])           # Full analysis
print(result['red_flags'])          # Critical issues
print(result['confidence'])         # Confidence score
```

---

## 👥 The Four Agents

### 1. 💼 Financial Economist (Dr. Fatima Al-Mansouri)
- **Expertise:** GCC corporate finance, financial statement analysis
- **Output:** Financial health, red flags, ratio analysis
- **Use When:** Financial performance questions

### 2. 📊 Market Economist (Dr. Khalid bin Ahmed)
- **Expertise:** GCC markets, competitive intelligence
- **Output:** Market position, opportunities, threats
- **Use When:** Market dynamics, competitive questions

### 3. ⚙️ Operations Expert (Sarah Mitchell)
- **Expertise:** GCC operations, execution, feasibility
- **Output:** Operational risks, resource requirements, timelines
- **Use When:** Implementation, execution questions

### 4. 🔬 Research Scientist (Dr. James Chen)
- **Expertise:** Strategic theory, evidence-based analysis
- **Output:** Theoretical frameworks, hypotheses, assumptions
- **Use When:** Need academic rigor, challenge assumptions

---

## 🔍 Key Features

### Zero Fabrication
- All agents receive ONLY extracted facts
- Forced citation: "Per extraction: [quote]"
- Missing data explicitly labeled
- No hallucination or estimation

### PhD-Level Expertise
- Each agent: 20-25 years experience
- Deep domain knowledge
- Professional analytical frameworks
- GCC market context

### Diverse Perspectives
- Financial: Numbers and ratios
- Market: Competitive and strategic
- Operations: Execution and feasibility
- Research: Theory and evidence

### CEO-Ready Output
- Direct and actionable
- Strategic focus
- Honest about limitations
- Multiple viewpoints integrated

---

## 📊 Sample Queries

### Financial Questions:
```python
"What is UDC's revenue?"
"How is UDC's profitability?"
"Should we be concerned about cash flow?"
"Is UDC financially healthy?"
```

### Market Questions:
```python
"What is UDC's market position?"
"Who are UDC's competitors?"
"What are the market opportunities?"
"What threats does UDC face?"
```

### Operations Questions:
```python
"Can UDC execute this strategy?"
"What resources does UDC need?"
"What are the operational risks?"
"How long will this take?"
```

### Research Questions:
```python
"What theory explains this?"
"What assumptions are we making?"
"What alternative explanations exist?"
"What should we investigate further?"
```

---

## 🎯 Success Criteria

Each agent produces:
- ✅ **500+ characters** of substantive analysis
- ✅ **Cited facts** with "Per extraction: [quote]"
- ✅ **Domain expertise** applied to the question
- ✅ **Actionable insights** for decision-makers
- ✅ **High confidence** (70-90% depending on data)

---

## 🔧 Troubleshooting

### "Agent returns short analysis"
- Check that `extracted_facts` has data
- Verify facts have 'value', 'quote', 'confidence' fields
- Try increasing complexity level

### "No citations in output"
- This is expected for market/research agents using domain knowledge
- Financial agent MUST have citations
- Check "Based on market knowledge" for differentiation

### "Low confidence scores"
- Normal if little data available
- Check `extracted_facts` dictionary
- Add more data sources in Phase 2

---

## 📈 Performance

**Typical Execution Times:**
- Financial Economist: 8-12 seconds
- Market Economist: 8-12 seconds
- Operations Expert: 8-12 seconds
- Research Scientist: 8-12 seconds
- **Total: 32-48 seconds** (sequential)

**Phase 4 will parallelize:** Financial + Market simultaneously (16-24 seconds)

---

## 🧪 Testing

### Test Individual Agent:
```bash
python tests/test_agents.py
```

### Test Full System:
```bash
python main.py
```

### Test with No Data (Edge Case):
The test suite includes edge case testing - agents handle missing data gracefully.

---

## 📚 Learn More

- **Phase 3 Complete:** See `PHASE_3_COMPLETE.md` for full documentation
- **Agent Code:** See `src/agents/` for implementation details
- **State Model:** See `src/models/state.py` for state structure
- **Workflow:** See `src/graph/workflow.py` for graph topology

---

## 🚀 Next Phase

**Phase 4 will add:**
1. Parallel agent execution (faster)
2. Conditional routing (smarter)
3. Agent debate (deeper)
4. Devil's advocate (critical)
5. Fact verification (validated)

---

**Ready to use! Run `python main.py` to see it in action.**
