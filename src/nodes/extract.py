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
        extracted = {}
        
        # Revenue patterns (handle negatives and billions, with optional sign before currency)
        revenue_patterns = [
            r"revenue[:\s]+([-+])?(?:QR|QAR|$)?\s*([-+]?[\d,\.]+)\s*(million|m|bn|billion)?",
            r"total revenue[:\s]+([-+])?(?:QR|QAR|$)?\s*([-+]?[\d,\.]+)\s*(million|m|bn|billion)?",
            r"revenues?[:\s]+([-+])?(?:QR|QAR|$)?\s*([-+]?[\d,\.]+)\s*(million|m|bn|billion)?"
        ]
        
        for pattern in revenue_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Handle prefix sign and number
                prefix_sign = match.group(1) if match.group(1) else ''
                number = match.group(2).replace(',', '')
                unit = match.group(3).lower() if match.group(3) else 'million'
                
                # Apply prefix sign if present and number doesn't already have one
                if prefix_sign and not number.startswith(('-', '+')):
                    value_str = prefix_sign + number
                else:
                    value_str = number
                
                # Convert to millions consistently
                float_value = float(value_str)
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
        
        # Profit patterns (handle negatives and billions, with optional minus before currency)
        profit_patterns = [
            r"net profit[:\s]+([-+])?(?:QR|QAR|$)?\s*([-+]?[\d,\.]+)\s*(million|m|bn|billion)?",
            r"profit[:\s]+([-+])?(?:QR|QAR|$)?\s*([-+]?[\d,\.]+)\s*(million|m|bn|billion)?",
        ]
        
        for pattern in profit_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Handle prefix sign and number
                prefix_sign = match.group(1) if match.group(1) else ''
                number = match.group(2).replace(',', '')
                unit = match.group(3).lower() if match.group(3) else 'million'
                
                # Apply prefix sign if present and number doesn't already have one
                if prefix_sign and not number.startswith(('-', '+')):
                    value_str = prefix_sign + number
                else:
                    value_str = number
                
                # Convert to millions consistently
                float_value = float(value_str)
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
    
    # For Phase 2 testing, we'll use sample data
    # In production, this would call your data tools
    sample_data = """
UDC Financial Report FY24

Revenue: QR 1,032.1 million
Net Profit: QR 89.5 million
Operating Cash Flow: -QR 460.5 million
Total Assets: QR 8,500 million

The company reported a challenging year with declining revenues from the 
previous year's QR 1,150 million. Despite reporting profits, the negative 
cash flow indicates cash burn.
"""
    
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
