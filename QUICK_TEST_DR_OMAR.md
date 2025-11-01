# Quick Test: Dr. Omar Agent

**Time Required:** 5 minutes  
**Result:** Talk to your first AI agent! 🚀

---

## Step 1: Add Your Anthropic API Key (2 minutes)

### Get API Key:
1. Visit: https://console.anthropic.com/
2. Sign up or log in
3. Go to "API Keys"
4. Create a new key
5. Copy the key

### Add to Project:
Edit `backend/.env`:
```bash
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

**Note:** The `.env` file may be in `.gitignore`. If it doesn't exist, copy from `.env.template`:
```bash
cd backend
cp .env.template .env
# Then edit .env and add your key
```

---

## Step 2: Install Dependencies (1 minute)

```bash
cd backend
pip install fastapi uvicorn anthropic pydantic pydantic-settings python-dotenv
```

---

## Step 3: Test Dr. Omar! (2 minutes)

### Option A: Quick Test Script (Easiest)

```bash
# From project root (D:\udc)
python test_dr_omar.py
```

Select option `1` for automated tests or `2` for interactive mode.

### Option B: Start FastAPI Server

```bash
# Terminal 1: Start server
cd backend
uvicorn app.main:app --reload

# Terminal 2: Test with curl
curl -X POST "http://localhost:8000/api/v1/agent/chat" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is our debt-to-equity ratio?"}'
```

### Option C: Use Interactive API Docs

1. Start server: `uvicorn app.main:app --reload`
2. Open browser: http://localhost:8000/docs
3. Find `POST /api/v1/agent/chat`
4. Click "Try it out"
5. Enter: `{"question": "What is our debt-to-equity ratio?"}`
6. Click "Execute"

---

## Sample Questions to Try

### Financial Health:
- "What is our current debt-to-equity ratio and should I be concerned?"
- "What were our Q3 2024 revenues?"
- "What are our major capital commitments?"

### Property Performance:
- "How is Gewan Island Phase 1 performing?"
- "What is the occupancy rate at The Pearl?"
- "Should we accelerate or delay Gewan Phase 2?"

### Qatar Cool:
- "How is Qatar Cool performing financially?"
- "What efficiency improvements could we make at Qatar Cool?"
- "Should we invest in Qatar Cool expansion?"

### Strategic Decisions:
- "What should we do with HDC hospitality losses?"
- "What are our biggest financial risks?"
- "Should we sell Costa Malaz?"

---

## What to Expect

**Response Time:** 5-10 seconds  
**Response Length:** 200-400 words  
**Cost:** QAR 0.25-0.45 per question  
**Quality:** Professional, data-backed analysis

**Example Output:**
```
Mr. CEO,

According to UDC Q3 2024 financial statements, our debt-to-equity 
ratio is 0.48.

ASSESSMENT: ⚠️ APPROACHING CONCERN THRESHOLD

KEY METRICS:
- Total Debt: QAR 5.4B
- Total Equity: QAR 7.8B
- Debt-to-Equity: 0.48
- Yellow Flag Threshold: 0.50

[... detailed analysis continues ...]

RECOMMENDED ACTIONS:
1. Complete Gewan Phase 1 efficiently
2. Accelerate Costa Malaz sale
3. Consider HDC divestment
```

---

## Troubleshooting

### Error: "Anthropic API key not set"
**Solution:** Make sure you edited `backend/.env` with your actual API key

### Error: "Module not found: anthropic"
**Solution:** Run `pip install anthropic` in backend directory

### Error: "File not found: data/sample_data/..."
**Solution:** Make sure you're running from project root (`D:\udc`)

### Dr. Omar's responses seem generic
**Check:** Is your API key correct? Try a different question.

---

## Success Indicators

✅ Dr. Omar responds within 10 seconds  
✅ Response includes specific UDC data (QAR amounts, percentages)  
✅ Data citations are present  
✅ Recommendations are actionable  
✅ Token usage is displayed  
✅ Cost is shown in QAR  

---

## After Testing

### Share Feedback:
- How was the response quality? (1-10)
- Were the recommendations helpful?
- What would you improve?
- What questions should we test next?

### Next Steps:
1. Try 5-10 different questions
2. Note which responses are excellent vs. good
3. Identify any missing data
4. Think about what Dr. James (CFO) should add

---

## 🎉 You're Now Talking to AI!

This is just the beginning. Soon you'll have:
- 7 specialized agents
- Multi-agent debates
- Real-time tension identification
- Board-ready decision sheets

**But today:** You're talking to Dr. Omar! 🚀

---

**Quick Start Commands:**

```bash
# Test Dr. Omar (recommended)
python test_dr_omar.py

# Or start API server
cd backend && uvicorn app.main:app --reload

# Then open: http://localhost:8000/docs
```

**Have fun chatting with Dr. Omar!** 🎯

