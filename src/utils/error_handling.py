"""
Production Error Handling - Phase 5
Graceful degradation and error recovery.
"""
import asyncio
import inspect
from datetime import datetime
from typing import Any, Callable, Optional

from src.utils.logging_config import logger


class ErrorHandler:
    """
    Robust error handling with retry logic and graceful degradation.
    """
    
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
    
    async def execute_with_retry(
        self,
        func: Callable,
        *args,
        node_name: str = "unknown",
        **kwargs
    ) -> Any:
        """
        Execute a function with retry logic.
        
        Args:
            func: Async function to execute
            node_name: Name of the node (for logging)
            *args, **kwargs: Arguments to pass to func
        
        Returns:
            Function result or error dict if all retries fail
        """
        last_exception: Optional[Exception] = None
        for attempt in range(self.max_retries):
            try:
                result = func(*args, **kwargs)
                if inspect.isawaitable(result):
                    result = await result
                if attempt > 0:
                    logger.info(f"✅ {node_name} succeeded on attempt {attempt + 1}")
                return result
            
            except asyncio.TimeoutError as exc:
                last_exception = exc
                attempt_index = attempt + 1
                logger.warning(
                    f"⏱️ {node_name} timed out on attempt {attempt_index}/{self.max_retries}"
                )
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
            
            except Exception as exc:
                last_exception = exc
                attempt_index = attempt + 1
                logger.error(
                    f"❌ {node_name} failed on attempt {attempt_index}/{self.max_retries}: {exc}"
                )
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
        
        # All retries failed - return error dict
        logger.error(f"💀 {node_name} failed after {self.max_retries} attempts")
        message = f"Node failed after {self.max_retries} retries"
        if last_exception:
            message += f" (last error: {last_exception})"
        return {
            'error': True,
            'node': node_name,
            'message': message
        }
    
    def handle_partial_failure(
        self,
        state: dict,
        failed_node: str,
        error: Exception
    ) -> dict:
        """
        Handle partial system failure gracefully.
        Updates state to reflect failure but allows system to continue.
        """
        logger.warning(f"🔧 Graceful degradation: {failed_node} failed, continuing without it")
        
        # Add to errors
        if 'errors' not in state:
            state['errors'] = []
        
        state['errors'].append({
            'node': failed_node,
            'error': str(error),
            'timestamp': datetime.now().isoformat()
        })
        
        # Add warning to reasoning chain
        if 'reasoning_chain' not in state:
            state['reasoning_chain'] = []
        
        state['reasoning_chain'].append(
            f"⚠️ {failed_node} unavailable - proceeding with partial analysis"
        )
        
        # Reduce confidence
        if 'confidence_score' in state:
            state['confidence_score'] *= 0.8  # 20% confidence reduction
        
        return state


# Global instance
error_handler = ErrorHandler(max_retries=3)
