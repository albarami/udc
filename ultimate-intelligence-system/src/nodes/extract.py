"""
Data Extraction Node - Phase 2
Extracts structured facts from raw data using Python + LLM verification.
This is the ONLY node that sees raw data.
"""
import re
from typing import Dict, Any, List
from datetime import datetime
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from src.models.state import IntelligenceState
from src.config.settings import settings
from src.utils.logging_config import logger


class DataExtractor:
    """
    Three-layer extraction system:
    1. Python regex/parsing (fast, deterministic)
    2. LLM extraction with low temp (accurate, structured)
    3. Cross-validation (verify consistency)
    """
    
    def __init__(self):
        self.llm = ChatAnthropic(
            model=settings.EXTRACTION_MODEL,
            temperature=settings.EXTRACTION_TEMP,
            api_key=settings.ANTHROPIC_API_KEY
        )
    
    def extract_numeric_data(self, text: str) -> Dict[str, Any]:
        """
        Layer 1: Python-based numeric extraction
        Fast, deterministic, no LLM needed for obvious numbers
        """
        logger.info("Layer 1: Python numeric extraction")

        # FIXED: Handle text with words separated by newlines (PDF extraction artifact)
        # Join lines and normalize whitespace for better pattern matching
        text = ' '.join(text.split())

        extracted = {}
        
        # Revenue patterns (handle negatives and billions, with optional sign before currency)
        revenue_patterns = [
            r"revenues?\s+(?:of\s+)?(?:QR|QAR|\$)?\s*([-+]?[\d,\.]+)\s*(million|m|bn|billion)",
            r"total\s+revenues?\s+(?:of\s+)?(?:QR|QAR|\$)?\s*([-+]?[\d,\.]+)\s*(million|m|bn|billion)",
            r"revenue[:\s]+(?:QR|QAR|\$)?\s*([-+]?[\d,\.]+)\s*(million|m|bn|billion)?",
        ]
        
        for pattern in revenue_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Extract number and unit (groups are now: number, unit)
                number = match.group(1).replace(',', '')
                unit = match.group(2).lower() if len(match.groups()) >= 2 and match.group(2) else 'million'

                # Convert to millions consistently
                float_value = float(number)
                if unit in ['bn', 'billion']:
                    float_value *= 1000  # Convert billions to millions

                extracted['revenue'] = {
                    'value': float_value,
                    'unit': 'QR millions',
                    'source': 'python_extraction',
                    'confidence': 0.95,
                    'raw_text': match.group(0)
                }
                break
        
        # Profit patterns (handle negatives and billions)
        profit_patterns = [
            r"net\s+profit\s+(?:of\s+)?(?:QR|QAR|\$)?\s*([-+]?[\d,\.]+)\s*(million|m|bn|billion)",
            r"profit\s+(?:of\s+)?(?:QR|QAR|\$)?\s*([-+]?[\d,\.]+)\s*(million|m|bn|billion)",
        ]

        for pattern in profit_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Extract number and unit
                number = match.group(1).replace(',', '')
                unit = match.group(2).lower() if len(match.groups()) >= 2 and match.group(2) else 'million'

                # Convert to millions consistently
                float_value = float(number)
                if unit in ['bn', 'billion']:
                    float_value *= 1000  # Convert billions to millions

                extracted['net_profit'] = {
                    'value': float_value,
                    'unit': 'QR millions',
                    'source': 'python_extraction',
                    'confidence': 0.95,
                    'raw_text': match.group(0)
                }
                break
        
        # Cash flow patterns (handles both "-QR 460" and "QR -460" and billions)
        cash_flow_patterns = [
            r"operating cash flow[:\s]+(-)?(?:QR|QAR|$)?\s*([-+]?[\d,\.]+)\s*(million|m|bn|billion)?",
            r"cash flow from operations[:\s]+(-)?(?:QR|QAR|$)?\s*([-+]?[\d,\.]+)\s*(million|m|bn|billion)?",
            r"OCF[:\s]+(-)?(?:QR|QAR|$)?\s*([-+]?[\d,\.]+)\s*(million|m|bn|billion)?"
        ]
        
        for pattern in cash_flow_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Handle both "-QR 460" (group 1 is -, group 2 is number) 
                # and "QR -460" (group 1 is None, group 2 is -number)
                prefix_minus = match.group(1) if match.group(1) else ''
                number = match.group(2).replace(',', '')
                unit = match.group(3).lower() if match.group(3) else 'million'
                
                # If there's a prefix minus, apply it
                if prefix_minus and not number.startswith('-'):
                    value = '-' + number
                else:
                    value = number
                
                # Convert to millions consistently
                float_value = float(value)
                if unit in ['bn', 'billion']:
                    float_value *= 1000  # Convert billions to millions
                    
                extracted['operating_cash_flow'] = {
                    'value': float_value,
                    'unit': 'QR millions',
                    'source': 'python_extraction',
                    'confidence': 0.95,
                    'raw_text': match.group(0)
                }
                break
        
        logger.info(f"Python extraction found {len(extracted)} metrics")
        return extracted
    
    async def extract_with_llm(self, text: str, query: str) -> Dict[str, Any]:
        """
        Layer 2: LLM-based extraction with strict prompting
        Used when Python extraction misses things or needs context
        """
        logger.info("Layer 2: LLM extraction with verification")
        
        system_prompt = """You are a precise data extraction specialist.

CRITICAL RULES:
1. Extract ONLY factual data explicitly stated in the text
2. Never estimate, infer, or use external knowledge
3. If a number is not in the text, return null for that field
4. Always include the exact quote from the text as proof
5. Format numbers consistently (use millions as base unit)

Output format (JSON):
{
  "metric_name": {
    "value": <number or null>,
    "unit": "QR millions",
    "quote": "exact text from source",
    "confidence": <0.0-1.0>,
    "fiscal_period": "FY24" or "Q3-24" etc
  }
}

Example:
Text: "Revenue for FY24 was QR 1,032.1 million"
Output:
{
  "revenue": {
    "value": 1032.1,
    "unit": "QR millions",
    "quote": "Revenue for FY24 was QR 1,032.1 million",
    "confidence": 1.0,
    "fiscal_period": "FY24"
  }
}

NEVER fabricate numbers. If not in text, use null."""

        user_prompt = f"""Query: {query}

Text to extract from:
{text[:3000]}

Extract all financial metrics (revenue, profit, cash flow, assets, liabilities, etc.) in JSON format.
Remember: ONLY extract what is explicitly stated. Use null for missing data."""

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            
            # Parse JSON response
            import json
            response_text = response.content
            
            # Extract JSON from response (might be wrapped in markdown)
            if "```json" in response_text:
                json_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                json_text = response_text.split("```")[1].split("```")[0]
            else:
                json_text = response_text
            
            extracted = json.loads(json_text.strip())
            
            # Add source metadata
            for metric, data in extracted.items():
                if data and isinstance(data, dict):
                    data['source'] = 'llm_extraction'
            
            logger.info(f"LLM extraction found {len(extracted)} metrics")
            return extracted
            
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            return {}
    
    def cross_validate(
        self,
        python_extracted: Dict[str, Any],
        llm_extracted: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Layer 3: Cross-validation
        Compare Python and LLM extractions, resolve conflicts
        """
        logger.info("Layer 3: Cross-validation")
        
        validated = {}
        conflicts = []
        
        # Get all unique metrics
        all_metrics = set(python_extracted.keys()) | set(llm_extracted.keys())
        
        for metric in all_metrics:
            python_data = python_extracted.get(metric)
            llm_data = llm_extracted.get(metric)
            
            if python_data and llm_data:
                # Both extracted - check agreement
                py_value = python_data.get('value')
                llm_value = llm_data.get('value')
                
                # Use 'is not None' to handle legitimate zero values
                if py_value is not None and llm_value is not None:
                    # Check if values are close (within 1%)
                    # Use abs() to handle negative values correctly
                    denominator = max(abs(py_value), abs(llm_value), 1e-9)  # Avoid division by zero
                    diff = abs(py_value - llm_value) / denominator
                    
                    if diff < 0.01:  # Within 1%
                        # Agreement - high confidence
                        validated[metric] = python_data.copy()
                        validated[metric]['confidence'] = 0.98
                        validated[metric]['verified_by'] = 'python_and_llm'
                    else:
                        # Conflict - prefer Python (more reliable)
                        validated[metric] = python_data.copy()
                        validated[metric]['confidence'] = 0.75
                        conflicts.append({
                            'metric': metric,
                            'python_value': py_value,
                            'llm_value': llm_value,
                            'resolution': 'used_python'
                        })
                        logger.warning(f"Conflict in {metric}: Python={py_value}, LLM={llm_value}")
                elif py_value is not None:
                    # Only Python has value
                    validated[metric] = python_data
                elif llm_value is not None:
                    # Only LLM has value
                    validated[metric] = llm_data
                    
            elif python_data:
                # Only Python extracted (LLM didn't find this metric)
                validated[metric] = python_data
            elif llm_data:
                # Only LLM extracted (Python didn't find this metric)
                validated[metric] = llm_data
        
        logger.info(f"Validation complete: {len(validated)} metrics, {len(conflicts)} conflicts")
        
        # Determine actual sources used
        sources_used = set()
        if python_extracted:
            sources_used.add('python_extraction')
        if llm_extracted:
            sources_used.add('llm_extraction')
        
        return {
            'facts': validated,
            'conflicts': conflicts,
            'sources': list(sources_used) if sources_used else []
        }


async def data_extraction_node(state: IntelligenceState) -> IntelligenceState:
    """
    Main extraction node that orchestrates the three-layer extraction.
    
    This is the ONLY node that has access to raw data.
    All other nodes will receive ONLY the extracted facts.
    """
    logger.info("=" * 80)
    logger.info("DATA EXTRACTION NODE: Starting extraction process")
    
    query = state["query"]
    
    # FIXED: Connect to actual knowledge base instead of using fake data
    try:
        import sys
        from pathlib import Path
        # From extract.py: ultimate-intelligence-system/src/nodes/extract.py
        # Go up 4 levels to reach d:\udc, then add backend
        backend_path = Path(__file__).parents[3] / "backend"
        if str(backend_path) not in sys.path:
            sys.path.insert(0, str(backend_path))
        
        from app.services.knowledge_base_complete import UDCCompleteKnowledgeBase
        
        logger.info("Connecting to knowledge base...")
        kb = UDCCompleteKnowledgeBase()
        
        # Search for relevant documents
        logger.info(f"Searching for: {query}")
        search_results = kb.search(query, n_results=10)
        
        if not search_results:
            logger.warning("No relevant documents found in knowledge base")
            sample_data = f"No data found for query: {query}"
        else:
            # Combine top results into context
            logger.info(f"Found {len(search_results)} relevant documents")
            sample_data = "\n\n".join([
                f"[Source: {r['citation']}]\n{r['content']}"
                for r in search_results
            ])
            logger.info(f"Retrieved {len(sample_data)} characters of context")
    
    except Exception as e:
        logger.error(f"Failed to connect to knowledge base: {e}")
        logger.warning("Falling back to empty extraction")
        sample_data = f"Error accessing knowledge base: {e}"
    
    # Initialize extractor
    extractor = DataExtractor()
    
    # Layer 1: Python extraction
    python_extracted = extractor.extract_numeric_data(sample_data)
    
    # Layer 2: LLM extraction
    llm_extracted = await extractor.extract_with_llm(sample_data, query)
    
    # Layer 3: Cross-validation
    validation_result = extractor.cross_validate(python_extracted, llm_extracted)
    
    # Update state
    state["extracted_facts"] = validation_result['facts']
    state["data_conflicts"] = validation_result['conflicts']
    state["extraction_sources"] = validation_result['sources']
    state["extraction_timestamp"] = datetime.now()
    
    # Calculate overall extraction confidence
    if validation_result['facts']:
        confidences = [
            fact.get('confidence', 0.5) 
            for fact in validation_result['facts'].values() 
            if isinstance(fact, dict)
        ]
        state["extraction_confidence"] = sum(confidences) / len(confidences)
    else:
        state["extraction_confidence"] = 0.0
    
    # Update tracking
    state["nodes_executed"].append("extract")
    state["reasoning_chain"].append(
        f"📊 Extracted {len(validation_result['facts'])} facts with "
        f"{state['extraction_confidence']:.0%} confidence"
    )
    
    if validation_result['conflicts']:
        state["reasoning_chain"].append(
            f"⚠️ {len(validation_result['conflicts'])} conflicts detected and resolved"
        )
    
    logger.info(f"Extraction complete: {len(validation_result['facts'])} facts")
    logger.info(f"Extraction confidence: {state['extraction_confidence']:.2%}")
    logger.info("DATA EXTRACTION NODE: Complete")
    logger.info("=" * 80)
    
    return state
