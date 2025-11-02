"""
Answer Synthesizer - Converts raw data into conversational answers
Uses LLM to synthesize natural language from retrieved data
"""

import json
from typing import Dict, List, Optional
import os


class AnswerSynthesizer:
    """
    Takes retrieved data and synthesizes natural language answers using LLM
    """
    
    def __init__(self, use_anthropic: bool = True):
        """
        Initialize synthesizer with LLM client
        
        Args:
            use_anthropic: If True, use Claude. If False, use OpenAI
        """
        self.use_anthropic = use_anthropic
        
        if use_anthropic:
            try:
                from anthropic import Anthropic
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    print("Warning: ANTHROPIC_API_KEY not found. Using fallback synthesis.")
                    self.client = None
                else:
                    self.client = Anthropic(api_key=api_key)
            except ImportError:
                print("Warning: anthropic package not installed. Using fallback synthesis.")
                self.client = None
        else:
            try:
                from openai import OpenAI
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    print("Warning: OPENAI_API_KEY not found. Using fallback synthesis.")
                    self.client = None
                else:
                    self.client = OpenAI(api_key=api_key)
            except ImportError:
                print("Warning: openai package not installed. Using fallback synthesis.")
                self.client = None
    
    def synthesize_answer(
        self, 
        query: str, 
        retrieved_data: List[Dict],
        sources: List[str]
    ) -> Dict:
        """
        Convert raw data into natural language answer
        
        Args:
            query: The CEO's question
            retrieved_data: List of data retrieved from various sources
            sources: List of source names
            
        Returns:
            Dict with answer, confidence, sources, and raw_data
        """
        
        # If no LLM client, use fallback
        if self.client is None:
            return self._fallback_synthesis(query, retrieved_data, sources)
        
        # Prepare data context
        data_context = self._format_data_for_llm(retrieved_data)
        
        # If no data, return early
        if not data_context or len(data_context) < 20:
            return {
                'answer': "I couldn't find specific data to answer this question. Could you provide more context or rephrase?",
                'confidence': 30,
                'sources': sources,
                'raw_data': retrieved_data
            }
        
        # Create synthesis prompt
        prompt = f"""You are a Strategic Intelligence Assistant for UDC (United Development Company).

The CEO asked: "{query}"

You have retrieved the following data:

{data_context}

Your task:
1. Extract the specific information needed to answer the CEO's question
2. Present it in a clear, conversational way (like speaking to the CEO directly)
3. Include relevant numbers, percentages, and comparisons
4. Be direct and executive-friendly (no fluff, no jargon)
5. If the data doesn't contain a clear answer, say so honestly
6. Keep it concise (2-4 sentences maximum)

Important:
- Use actual numbers from the data (don't make them up)
- Speak naturally: "UDC's Q2 revenue was..." not "The data shows..."
- If comparing, use clear language: "higher than", "increased by", etc.
- Don't repeat the question back to them

Provide a natural, conversational answer now:"""

        try:
            # Call LLM
            if self.use_anthropic:
                answer = self._call_claude(prompt)
            else:
                answer = self._call_openai(prompt)
            
            # Calculate confidence based on data quality
            confidence = self._calculate_confidence(retrieved_data, answer)
            
            return {
                'answer': answer,
                'confidence': confidence,
                'sources': sources,
                'raw_data': retrieved_data
            }
        
        except Exception as e:
            print(f"LLM synthesis error: {str(e)}")
            return self._fallback_synthesis(query, retrieved_data, sources)
    
    def _call_claude(self, prompt: str) -> str:
        """Call Claude API"""
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            temperature=0.3,  # Lower temperature for factual accuracy
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        return response.content[0].text
    
    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API"""
        response = self.client.chat.completions.create(
            model="gpt-4o",  # or "gpt-4-turbo"
            temperature=0.3,
            max_tokens=500,
            messages=[
                {
                    "role": "system", 
                    "content": "You are a Strategic Intelligence Assistant for UDC. Be direct, conversational, and executive-friendly. Answer in 2-4 sentences maximum."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ]
        )
        return response.choices[0].message.content
    
    def _fallback_synthesis(
        self, 
        query: str, 
        retrieved_data: List[Dict],
        sources: List[str]
    ) -> Dict:
        """
        Fallback synthesis when no LLM available
        Extracts key information heuristically
        """
        
        # Simple heuristic extraction
        answer_parts = []
        
        for data in retrieved_data[:3]:  # Top 3 sources
            if 'data' in data and isinstance(data['data'], dict):
                # Try to extract key metrics
                json_data = data['data']
                
                # Look for revenue, performance, numbers
                if 'quarterly_performance' in json_data:
                    qp = json_data['quarterly_performance']
                    if isinstance(qp, dict):
                        for period, values in qp.items():
                            if 'Q2 2024' in period or 'q2_2024' in period.lower():
                                if isinstance(values, dict) and 'revenue' in values:
                                    answer_parts.append(f"Q2 2024 revenue was {values['revenue']}")
                
                # Look for summary data
                if 'annual_summary' in json_data:
                    summary = json_data['annual_summary']
                    if isinstance(summary, dict):
                        for key, value in list(summary.items())[:2]:
                            answer_parts.append(f"{key}: {value}")
            
            elif 'documents' in data and data['documents']:
                # Extract from document text
                doc_text = data['documents'][0] if data['documents'] else ""
                if len(doc_text) > 50:
                    # Extract first meaningful sentence
                    sentences = doc_text.split('.')
                    if sentences:
                        answer_parts.append(sentences[0][:200])
        
        if answer_parts:
            answer = " ".join(answer_parts[:2])  # Max 2 parts
        else:
            answer = "I found data related to your question, but it requires manual review. The raw data is available in the sources listed."
        
        return {
            'answer': answer,
            'confidence': 60,
            'sources': sources,
            'raw_data': retrieved_data
        }
    
    def _format_data_for_llm(self, retrieved_data: List[Dict]) -> str:
        """
        Format retrieved data into readable context for LLM
        """
        formatted = []
        
        for i, data in enumerate(retrieved_data, 1):
            source = data.get('source', 'Unknown')
            
            if 'data' in data and isinstance(data['data'], dict):
                # JSON data - full structure
                formatted.append(f"=== Source {i}: {source} ===")
                formatted.append(json.dumps(data['data'], indent=2)[:2000])  # Limit to 2000 chars
            
            elif 'documents' in data and data['documents']:
                # ChromaDB results - top results
                formatted.append(f"=== Source {i}: {source} ===")
                docs = data['documents'][:3]  # Top 3 documents
                for j, doc in enumerate(docs, 1):
                    formatted.append(f"Document {j}:")
                    formatted.append(doc[:800] if len(doc) > 800 else doc)  # Limit length
                    formatted.append("")
            
            elif 'text' in data:
                # Text data
                formatted.append(f"=== Source {i}: {source} ===")
                formatted.append(data['text'][:1500])
            
            elif 'results' in data:
                # API results (World Bank, etc.)
                formatted.append(f"=== Source {i}: {source} ===")
                formatted.append(json.dumps(data['results'], indent=2)[:2000])
        
        return "\n\n".join(formatted)
    
    def _calculate_confidence(self, retrieved_data: List[Dict], answer: str) -> int:
        """
        Calculate confidence score based on data quality and answer
        """
        confidence = 70  # Base confidence
        
        # Increase confidence if we have multiple sources
        if len(retrieved_data) > 1:
            confidence += 10
        
        # Increase if answer contains specific numbers
        if any(char.isdigit() for char in answer):
            confidence += 10
        
        # Decrease if answer is very short (might be uncertain)
        if len(answer) < 50:
            confidence -= 15
        
        # Decrease if answer mentions uncertainty
        uncertainty_words = ['might', 'possibly', 'unclear', 'not sure', "don't have"]
        if any(word in answer.lower() for word in uncertainty_words):
            confidence -= 10
        
        # Cap at 95% (never 100% certain) and min at 40%
        return min(95, max(40, confidence))


# Convenience function for quick synthesis
def synthesize_quick(query: str, data: List[Dict], sources: List[str]) -> str:
    """
    Quick synthesis - returns just the answer text
    """
    synthesizer = AnswerSynthesizer()
    result = synthesizer.synthesize_answer(query, data, sources)
    return result['answer']
