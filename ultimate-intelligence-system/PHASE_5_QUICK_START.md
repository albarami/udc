# Phase 5 Quick Start Guide

**Optimization & Production Readiness**

---

## 🚀 Quick Start

### 1. Run the Optimization Demo
```bash
cd ultimate-intelligence-system
python main.py
```

This runs the Phase 5 demo showing:
- Simple query optimization (4 nodes, ~15s)
- Medium query optimization (5 nodes, ~25s)
- Complex query with full pipeline (10 nodes)

### 2. Run Performance Tests
```bash
python tests/test_phase5.py
```

Tests:
- ✅ Conditional routing logic
- ✅ Parallel agent execution
- ✅ Performance monitoring

### 3. Compare Execution Modes
Edit `main.py` and uncomment:
```python
# await compare_execution_modes()
```

Then run:
```bash
python main.py
```

This compares:
- Sequential with routing (optimized)
- Parallel execution (fastest)
- Shows speedup and time saved

---

## 📊 Usage Examples

### Simple Query (Fast)
```python
from main import process_query

result = await process_query(
    "What is UDC's revenue?",
    use_parallel=False,
    use_routing=True
)
# Expected: 4 nodes, ~15s, simple path
```

### Medium Query (Balanced)
```python
result = await process_query(
    "How is UDC's financial performance?",
    use_parallel=False,
    use_routing=True
)
# Expected: 5 nodes, ~25s, medium path
```

### Complex Query (Comprehensive)
```python
result = await process_query(
    "Should we invest in UDC given market conditions and risks?",
    use_parallel=False,
    use_routing=True
)
# Expected: 10 nodes, full pipeline
```

### Complex Query (Fast Parallel)
```python
result = await process_query(
    "Comprehensive analysis of UDC",
    use_parallel=True,
    use_routing=False
)
# Expected: 7 nodes with parallel agents, ~25s
```

---

## 🎛️ Configuration Options

### Execution Modes

**1. Sequential with Routing (Default)**
```python
use_parallel=False, use_routing=True
```
- Skips unnecessary nodes based on complexity
- Best for: Most queries, balanced performance

**2. Parallel Execution**
```python
use_parallel=True, use_routing=False
```
- All 4 agents run concurrently
- Best for: Time-critical complex queries
- Trade-off: Less context sharing between agents

**3. Full Sequential (Phase 4)**
```python
use_parallel=False, use_routing=False
```
- All nodes execute sequentially
- Best for: Maximum quality, thoroughness
- Slowest but most context-aware

---

## 📈 Performance Monitoring

### View Performance Metrics
Performance metrics are automatically logged:

```python
result = await process_query(query)

# Check execution details
print(f"Time: {result['total_time_seconds']:.2f}s")
print(f"Cost: ${result['cumulative_cost']:.4f}")
print(f"Nodes: {result['nodes_executed']}")
print(f"Confidence: {result['confidence_score']:.0%}")
```

### Access Performance Monitor
```python
from src.utils.performance import performance_monitor

# After query execution
summary = performance_monitor.get_summary()
print(summary['total_time'])
print(summary['total_cost'])
print(summary['node_times'])  # Per-node breakdown
```

---

## 🎯 Optimization Strategies

### When to Use Each Mode

**Sequential with Routing** ⭐ RECOMMENDED
- ✅ Simple questions (revenue, specific metrics)
- ✅ Medium complexity (performance analysis)
- ✅ Most business queries
- ✅ Cost-conscious scenarios

**Parallel Execution** ⚡ FASTEST
- ✅ Time-critical queries
- ✅ Complex analyses needing speed
- ✅ High-throughput scenarios
- ⚠️ Slightly higher cost (4 concurrent LLM calls)

**Full Sequential** 🎓 THOROUGH
- ✅ Research-grade analysis
- ✅ Maximum quality requirements
- ✅ Scenarios where time is not critical
- ⚠️ Slowest option (~53s)

---

## 🔧 Advanced Usage

### Custom Routing Logic

Edit `src/graph/routing.py` to customize routing:

```python
def route_after_financial(state: IntelligenceState) -> str:
    complexity = state["complexity"]
    
    # Add custom logic here
    if complexity == "simple":
        return "synthesis"
    else:
        return "market"
```

### Adjust Performance Limits

Edit `src/utils/performance.py`:

```python
class PerformanceMonitor:
    MAX_COST_PER_QUERY = 2.00  # Change cost limit
    MAX_TIME_PER_QUERY = 120   # Change time limit
```

### Add Custom Metrics

```python
from src.utils.performance import performance_monitor

# Track custom events
performance_monitor.start_node("custom_node")
# ... your code ...
performance_monitor.end_node("custom_node")
```

---

## 🧪 Testing

### Run All Tests
```bash
python tests/test_phase5.py
```

### Test Specific Features

**Test Routing:**
```bash
python -c "
from tests.test_phase5 import test_routing
import asyncio
asyncio.run(test_routing())
"
```

**Test Parallel Execution:**
```bash
python -c "
from tests.test_phase5 import test_parallel_execution
import asyncio
asyncio.run(test_parallel_execution())
"
```

**Test Performance Monitoring:**
```bash
python -c "
from tests.test_phase5 import test_performance_monitoring
test_performance_monitoring()
"
```

---

## 📊 Expected Performance

### Execution Time by Complexity

| Complexity | Nodes | Time (Sequential) | Time (Parallel) |
|-----------|-------|------------------|-----------------|
| Simple    | 4     | ~15s             | N/A             |
| Medium    | 5     | ~25s             | N/A             |
| Complex   | 10    | ~50-60s          | ~25-35s         |
| Critical  | 8     | ~40s             | ~20-30s         |

### Cost Estimates (Claude 3.5 Sonnet)

| Query Type | Approximate Cost |
|-----------|-----------------|
| Simple    | $0.03 - $0.05   |
| Medium    | $0.05 - $0.08   |
| Complex   | $0.10 - $0.20   |
| Parallel  | $0.15 - $0.25   |

*Actual costs vary based on query length and response complexity*

---

## 🚨 Troubleshooting

### Issue: Import Errors
```
ImportError: cannot import name 'create_parallel_graph'
```

**Solution:** Ensure you're in the correct directory:
```bash
cd ultimate-intelligence-system
python main.py
```

### Issue: Performance Monitor Not Working
```
KeyError: 'total_time'
```

**Solution:** Ensure `start_query()` is called:
```python
performance_monitor.start_query()
# ... run query ...
summary = performance_monitor.get_summary()
```

### Issue: Routing Not Applied
Queries run all nodes regardless of complexity.

**Solution:** Check `use_routing=True` in `process_query()`:
```python
result = await process_query(query, use_routing=True)
```

---

## 📚 File Reference

### Core Files
- `src/graph/routing.py` - Conditional routing logic
- `src/graph/parallel.py` - Parallel agent execution
- `src/graph/workflow.py` - Optimized graph definitions
- `src/utils/performance.py` - Performance monitoring
- `src/utils/error_handling.py` - Error handling & retry logic

### Test Files
- `tests/test_phase5.py` - Phase 5 test suite

### Documentation
- `PHASE_5_COMPLETION_REPORT.md` - Full implementation details
- `PHASE_5_QUICK_START.md` - This guide

---

## 🎯 Next Steps

1. **Run the demo** - See optimization in action
2. **Compare modes** - Understand performance trade-offs
3. **Test with your queries** - Adapt to your use cases
4. **Customize routing** - Tune for your requirements
5. **Monitor costs** - Track and optimize spending

---

## 💡 Tips for Best Results

1. **Start with routing** - Most queries benefit from conditional routing
2. **Use parallel for critical queries** - When speed is essential
3. **Monitor performance** - Check logs for timing and costs
4. **Iterate on routing** - Adjust complexity thresholds as needed
5. **Test thoroughly** - Verify optimizations don't reduce quality

---

## 📞 Need Help?

Check the following resources:
- Full documentation: `PHASE_5_COMPLETION_REPORT.md`
- Code examples: `main.py`
- Test cases: `tests/test_phase5.py`
- Architecture: Phase 1-4 documentation

---

**Phase 5 is ready! Start optimizing your queries now.** 🚀
