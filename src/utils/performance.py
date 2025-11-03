"""
Performance Monitoring - Phase 5
Track execution time, cost, and performance metrics.
"""
import time
from typing import Dict

from src.utils.logging_config import logger


class PerformanceMonitor:
    """
    Monitor and track system performance metrics.
    """
    
    # Claude API Pricing (as of Nov 2024)
    PRICING = {
        "claude-3-5-sonnet-20241022": {
            "input": 3.00 / 1_000_000,   # $ per token
            "output": 15.00 / 1_000_000
        },
        "claude-3-haiku-20240307": {
            "input": 0.25 / 1_000_000,
            "output": 1.25 / 1_000_000
        }
    }
    
    # Cost and time limits
    MAX_COST_PER_QUERY = 2.00  # dollars
    MAX_TIME_PER_QUERY = 120   # seconds
    
    def __init__(self):
        self.start_time = None
        self.node_times: Dict[str, float] = {}
        self.node_start_times: Dict[str, float] = {}
        self.total_cost = 0.0
        self.llm_calls = 0
    
    def start_query(self):
        """Start tracking a new query"""
        self.start_time = time.time()
        self.node_times = {}
        self.node_start_times = {}
        self.total_cost = 0.0
        self.llm_calls = 0
        logger.info("Performance monitoring started")
    
    def start_node(self, node_name: str):
        """Start tracking a node"""
        start_time = time.time()
        self.node_start_times[node_name] = start_time
        logger.debug(f"Perf monitor: start node {node_name} at {start_time:.4f}")
    
    def end_node(self, node_name: str):
        """End tracking a node"""
        start_time = self.node_start_times.pop(node_name, None)
        if start_time is None:
            logger.debug(f"Perf monitor: end called for {node_name} without recorded start")
            return
        elapsed = time.time() - start_time
        self.node_times[node_name] = self.node_times.get(node_name, 0.0) + elapsed
        logger.info(f"Node {node_name}: {elapsed:.2f}s")
    
    def track_llm_call(
        self, 
        model: str, 
        input_tokens: int, 
        output_tokens: int
    ):
        """Track an LLM API call"""
        self.llm_calls += 1
        
        # Calculate cost
        pricing = self.PRICING.get(model, self.PRICING["claude-3-5-sonnet-20241022"])
        cost = (input_tokens * pricing["input"]) + (output_tokens * pricing["output"])
        self.total_cost += cost
        
        logger.debug(
            f"LLM call #{self.llm_calls}: {model}, "
            f"tokens={input_tokens}+{output_tokens}, "
            f"cost=${cost:.4f}, total=${self.total_cost:.4f}"
        )
        
        # Check limits
        if self.total_cost > self.MAX_COST_PER_QUERY:
            logger.warning(
                f"Cost limit exceeded: ${self.total_cost:.2f} > ${self.MAX_COST_PER_QUERY}"
            )
    
    def check_time_limit(self) -> bool:
        """Check if time limit exceeded"""
        if self.start_time:
            elapsed = time.time() - self.start_time
            if elapsed > self.MAX_TIME_PER_QUERY:
                logger.warning(
                    f"Time limit exceeded: {elapsed:.0f}s > {self.MAX_TIME_PER_QUERY}s"
                )
                return True
        return False
    
    def get_summary(self) -> dict:
        """Get performance summary"""
        if not self.start_time:
            logger.debug("Perf monitor: get_summary requested before start_query")
            return {}
        
        total_time = time.time() - self.start_time
        
        return {
            'total_time': total_time,
            'node_times': self.node_times,
            'total_cost': self.total_cost,
            'llm_calls': self.llm_calls,
            'avg_time_per_node': total_time / len(self.node_times) if self.node_times else 0,
            'avg_cost_per_call': self.total_cost / self.llm_calls if self.llm_calls > 0 else 0
        }
    
    def log_summary(self):
        """Log performance summary"""
        summary = self.get_summary()
        if not summary:
            logger.info("PERFORMANCE SUMMARY unavailable (monitor not started)")
            return
        
        logger.info("=" * 80)
        logger.info("PERFORMANCE SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total Time: {summary['total_time']:.2f}s")
        logger.info(f"Total Cost: ${summary['total_cost']:.4f}")
        logger.info(f"LLM Calls: {summary['llm_calls']}")
        logger.info(f"Avg Time/Node: {summary['avg_time_per_node']:.2f}s")
        logger.info(f"Avg Cost/Call: ${summary['avg_cost_per_call']:.4f}")
        logger.info("\nNode Breakdown:")
        for node, duration in sorted(summary['node_times'].items(), key=lambda x: x[1], reverse=True):
            logger.info(f"  {node}: {duration:.2f}s")
        logger.info("=" * 80)


# Global instance
performance_monitor = PerformanceMonitor()
