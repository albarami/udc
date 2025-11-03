# 🚀 Phase 6 Quick Start Guide

## Get Running in 3 Minutes

### Step 1: Install Chainlit
```bash
pip install chainlit==1.3.1 aiofiles==23.2.1
```

### Step 2: Run the App
```bash
chainlit run app.py
```

### Step 3: Open Browser
Navigate to: **http://localhost:8000**

---

## ✅ What You Should See

### 1. Welcome Screen
Beautiful landing page with:
- System overview
- Core capabilities
- Usage examples
- Performance benchmarks

### 2. Query Input
Type your question in the chat box at the bottom.

### 3. Real-Time Streaming
Watch as the system processes your query:
```
📊 Classify: Query complexity is medium
🔍 Extract: Extracted 15 facts (confidence: 95%)
💼 Financial Economist: Analysis complete
📈 Market Economist: Analysis complete
🤝 Multi-Agent Debate: Found 2 contradictions
😈 Devil's Advocate: Challenged 3 assumptions
✅ Verify: All claims verified (98% confidence)
📄 Synthesis: Creating final intelligence report...
```

### 4. Intelligence Report
Beautiful formatted report with:
- Executive summary
- Key insights
- Recommendations
- Expandable sections for detailed analysis

---

## 🧪 Test Queries

### Simple Query (Fast)
```
What was UDC's revenue in FY24?
```
**Expected**: ~10 seconds, 4 nodes, direct answer

### Medium Query
```
How is UDC's financial performance?
```
**Expected**: ~20 seconds, 5 nodes, multi-perspective analysis

### Complex Query (Full Power)
```
Should we invest in UDC given current market conditions?
```
**Expected**: ~50 seconds, 10 nodes, comprehensive strategic analysis

---

## 🎯 Features to Try

### 1. Real-Time Updates
Watch each agent work in real-time as nodes execute.

### 2. Expandable Sections
Click on agent names in the sidebar to see detailed analyses:
- 💼 Financial Analysis
- 📈 Market Analysis
- ⚙️ Operations Analysis
- 🔬 Research Analysis
- 🤝 Multi-Agent Debate
- 😈 Devil's Advocate Critique

### 3. Performance Metrics
Check "📊 Performance Metrics" to see:
- Execution time
- LLM calls
- Cost per query
- Confidence breakdown

---

## ⚙️ Configuration

Edit `app.py` to adjust:

```python
ENABLE_PARALLEL = False  # Toggle parallel execution
SHOW_DEBUG_INFO = True   # Show performance metrics
STREAM_UPDATES = True    # Stream node updates
```

---

## 🐳 Docker Quick Start

### Option 1: Docker Run
```bash
docker build -t intelligence-system .
docker run -p 8000:8000 -e ANTHROPIC_API_KEY=your_key intelligence-system
```

### Option 2: Docker Compose
```bash
# Set API key
echo "ANTHROPIC_API_KEY=your_key" > .env

# Start all services
docker-compose up -d

# Access at http://localhost:8000
```

---

## 🔧 Troubleshooting

### Issue: Import Errors
**Solution**: Ensure you're in the `d:\udc` directory when running.

### Issue: Module Not Found
**Solution**: 
```bash
cd d:\udc
pip install -r requirements.txt
```

### Issue: API Key Error
**Solution**: Set your Anthropic API key:
```bash
# Windows PowerShell
$env:ANTHROPIC_API_KEY="your_key_here"

# Linux/Mac
export ANTHROPIC_API_KEY="your_key_here"
```

### Issue: Port Already in Use
**Solution**: Change port in app.py or kill process on port 8000:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

---

## 📊 Expected Performance

Based on Phase 5 benchmarks:

| Query Type | Time | Cost | Nodes |
|------------|------|------|-------|
| Simple     | 10s  | $0.05 | 4     |
| Medium     | 20s  | $0.10 | 5     |
| Complex    | 50s  | $0.25 | 10    |

**UI Overhead**: < 100ms (negligible)

---

## ✅ Success Checklist

- [ ] Chainlit app starts without errors
- [ ] Welcome screen displays correctly
- [ ] Can submit queries
- [ ] Real-time updates appear
- [ ] Final report displays beautifully
- [ ] Expandable sections work
- [ ] Performance metrics visible
- [ ] Zero fabrications detected

---

## 🎉 You're Ready!

The Ultimate Multi-Agent Intelligence System is now running with a beautiful production UI.

**Next Steps:**
1. Try different query types
2. Explore expandable sections
3. Monitor performance metrics
4. Deploy to production when ready

---

## 📚 More Information

- **Full Deployment Guide**: See `DEPLOYMENT.md`
- **Phase 6 Details**: See `PHASE_6_COMPLETE.md`
- **System Architecture**: See Phase 1-5 documentation

**Questions?** Check logs in `logs/` directory.

---

**Built with Phase 6 - Production Ready** 🚀
