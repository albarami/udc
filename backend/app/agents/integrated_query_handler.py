"""
Integrated CEO Query Handler
Complete pipeline: Query → Routing → Retrieval → Synthesis → Response
"""

import sys
sys.path.insert(0, 'D:/udc')

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import time

from backend.app.ontology.intelligent_router import IntelligentQueryRouter
from backend.app.agents.data_retrieval_layer import DataRetrievalExecutor
from backend.app.agents.answer_synthesizer import AnswerSynthesizer
from backend.app.agents.crewai_base import DrOmarOrchestrator


class CEOResponseSynthesizer:
    """
    Synthesizes CEO responses from retrieved data
    Connects to Dr. Omar agent or provides structured synthesis
    """
    
    def __init__(self):
        self.synthesis_templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        """Load response templates for different question types"""
        return {
            'udc_revenue': """Based on UDC's financial data:

{data_summary}

**Key Points:**
{key_points}

**Source:** {sources}""",
            
            'udc_property_performance': """UDC Property Portfolio Analysis:

{data_summary}

**Properties:**
{properties_list}

**Performance Metrics:**
{metrics}

**Sources:** {sources}""",
            
            'qatar_gdp': """Qatar Economic Data:

{data_summary}

**Key Findings:**
{findings}

**Sources:** {sources}""",
            
            'gcc_economic_benchmark': """GCC Economic Comparison:

{comparison_table}

**Analysis:**
{analysis}

**Sources:** {sources}""",
            
            'academic_market_research': """Research Findings:

{papers_summary}

**Key Studies:**
{top_papers}

**Sources:** {sources}""",
            
            'default': """Answer:

{data_summary}

**Details:**
{details}

**Sources:** {sources}"""
        }
    
    async def synthesize_response(
        self,
        query: str,
        retrieved_data: Dict,
        question_type: str,
        requires_synthesis: bool
    ) -> Dict:
        """
        Synthesize a CEO-ready response from retrieved data
        """
        start_time = time.time()
        
        # Extract data
        data_items = retrieved_data.get('data_retrieved', [])
        sources = retrieved_data.get('sources_queried', [])
        
        if not data_items:
            return self._create_no_data_response(query, sources)
        
        # Choose synthesis method
        if requires_synthesis and len(data_items) > 1:
            answer = await self._synthesize_multi_source(query, data_items, question_type)
        else:
            answer = await self._synthesize_single_source(query, data_items[0], question_type)
        
        # Add metadata
        answer['sources'] = sources
        answer['execution_time'] = time.time() - start_time
        answer['timestamp'] = datetime.now().isoformat()
        
        return answer
    
    async def _synthesize_multi_source(
        self,
        query: str,
        data_items: List[Dict],
        question_type: str
    ) -> Dict:
        """Synthesize answer from multiple data sources"""
        
        # Collect all data
        all_data = []
        for item in data_items:
            data = item.get('data', {})
            source = item.get('source', 'unknown')
            all_data.append({'source': source, 'data': data})
        
        # Format based on question type
        if question_type == 'gcc_economic_benchmark':
            return self._format_gcc_comparison(query, all_data)
        elif question_type.startswith('udc_'):
            return self._format_udc_analysis(query, all_data, question_type)
        elif question_type == 'academic_market_research':
            return self._format_research_summary(query, all_data)
        else:
            return self._format_general_synthesis(query, all_data)
    
    async def _synthesize_single_source(
        self,
        query: str,
        data_item: Dict,
        question_type: str
    ) -> Dict:
        """Synthesize answer from single data source"""
        
        data = data_item.get('data', {})
        source = data_item.get('source', 'unknown')
        
        # Format based on data type
        data_type = data.get('type', 'unknown')
        
        if data_type == 'structured_json':
            return self._format_json_data(query, data, question_type)
        elif data_type == 'chromadb_search':
            return self._format_document_search(query, data)
        elif data_type == 'world_bank_api':
            return self._format_world_bank_data(query, data)
        elif data_type == 'semantic_scholar_api':
            return self._format_research_papers(query, data)
        else:
            return self._format_generic_data(query, data)
    
    def _format_gcc_comparison(self, query: str, all_data: List[Dict]) -> Dict:
        """Format GCC comparison data"""
        
        # Extract World Bank data
        wb_data = None
        for item in all_data:
            if 'world_bank' in item['source']:
                wb_data = item['data'].get('data', [])
                break
        
        if not wb_data:
            return {'text': 'No GCC comparison data available.', 'confidence': 0}
        
        # Group by country
        by_country = {}
        for point in wb_data:
            country = point.get('country', 'Unknown')
            if country not in by_country:
                by_country[country] = []
            by_country[country].append(point)
        
        # Create comparison table
        comparison = []
        for country, points in by_country.items():
            if points:
                latest = points[0]
                comparison.append(
                    f"**{country}:** {latest.get('value', 'N/A'):,.0f} {latest.get('unit', '')} ({latest.get('year', 'N/A')})"
                )
        
        answer = f"""# GCC Economic Comparison

{chr(10).join(comparison)}

**Data Points:** {len(wb_data)} across {len(by_country)} countries
**Most Recent Year:** {wb_data[0].get('year', 'N/A') if wb_data else 'N/A'}
"""
        
        return {
            'text': answer,
            'confidence': 95,
            'data_points': len(wb_data)
        }
    
    def _format_udc_analysis(self, query: str, all_data: List[Dict], question_type: str) -> Dict:
        """Format UDC internal analysis"""
        
        summary_parts = []
        
        for item in all_data:
            source = item['source']
            data = item['data']
            
            if data.get('type') == 'structured_json':
                file = data.get('file', 'unknown')
                content = data.get('data', {})
                
                summary_parts.append(f"**From {file}:**")
                
                # Extract key information
                if isinstance(content, dict):
                    for key, value in list(content.items())[:5]:
                        if isinstance(value, (dict, list)):
                            summary_parts.append(f"  - {key}: [Complex data structure]")
                        else:
                            summary_parts.append(f"  - {key}: {value}")
            
            elif data.get('type') == 'chromadb_search':
                docs = data.get('documents', [])
                if docs:
                    summary_parts.append(f"**From PDF documents ({len(docs)} relevant sections):**")
                    # Show first document preview
                    preview = docs[0].get('content', '')[:200]
                    summary_parts.append(f"  {preview}...")
        
        answer = f"""# UDC Analysis

{chr(10).join(summary_parts)}

**Note:** This is raw data. For detailed analysis, please review the source documents.
"""
        
        return {
            'text': answer,
            'confidence': 85,
            'sources_count': len(all_data)
        }
    
    def _format_research_summary(self, query: str, all_data: List[Dict]) -> Dict:
        """Format academic research summary"""
        
        papers = []
        for item in all_data:
            data = item['data']
            if data.get('type') == 'semantic_scholar_api':
                papers.extend(data.get('papers', []))
        
        if not papers:
            return {'text': 'No research papers found.', 'confidence': 0}
        
        summary_parts = [f"# Research on: {query}\n"]
        summary_parts.append(f"**Found {len(papers)} relevant papers:**\n")
        
        for i, paper in enumerate(papers[:5], 1):
            title = paper.get('title', 'No title')
            year = paper.get('year', 'N/A')
            citations = paper.get('citations', 0)
            authors = paper.get('authors', [])
            author_str = ', '.join(authors[:2]) if authors else 'Unknown'
            
            summary_parts.append(f"{i}. **{title}** ({year})")
            summary_parts.append(f"   Authors: {author_str}")
            summary_parts.append(f"   Citations: {citations}")
            summary_parts.append("")
        
        answer = chr(10).join(summary_parts)
        
        return {
            'text': answer,
            'confidence': 90,
            'papers_count': len(papers)
        }
    
    def _format_json_data(self, query: str, data: Dict, question_type: str) -> Dict:
        """Format structured JSON data"""
        
        content = data.get('data', {})
        file = data.get('file', 'unknown')
        
        if not content:
            return {'text': f'No data found in {file}', 'confidence': 0}
        
        # Create summary
        summary = f"# Data from {file}\n\n"
        
        if isinstance(content, dict):
            for key, value in list(content.items())[:10]:
                if isinstance(value, dict):
                    summary += f"**{key}:** {len(value)} items\n"
                elif isinstance(value, list):
                    summary += f"**{key}:** {len(value)} entries\n"
                else:
                    summary += f"**{key}:** {value}\n"
        
        return {
            'text': summary,
            'confidence': 80,
            'file': file
        }
    
    def _format_document_search(self, query: str, data: Dict) -> Dict:
        """Format ChromaDB document search results"""
        
        documents = data.get('documents', [])
        collection = data.get('collection', 'unknown')
        
        if not documents:
            return {'text': f'No relevant documents found in {collection}', 'confidence': 0}
        
        summary = f"# Relevant Information from {collection}\n\n"
        
        for i, doc in enumerate(documents[:3], 1):
            content = doc.get('content', '')
            distance = doc.get('distance', 0)
            relevance = max(0, 100 - (distance * 100))
            
            summary += f"**Result {i}** (Relevance: {relevance:.0f}%):\n"
            summary += f"{content[:300]}...\n\n"
        
        return {
            'text': summary,
            'confidence': 75,
            'documents_count': len(documents)
        }
    
    def _format_world_bank_data(self, query: str, data: Dict) -> Dict:
        """Format World Bank API data"""
        
        status = data.get('status')
        if status != 'success':
            return {'text': f'World Bank API error: {data.get("error", "Unknown")}', 'confidence': 0}
        
        data_points = data.get('data', [])
        countries = data.get('countries', [])
        
        if not data_points:
            return {'text': 'No data returned from World Bank', 'confidence': 0}
        
        summary = f"# World Bank Economic Data\n\n"
        summary += f"**Countries:** {', '.join(countries)}\n"
        summary += f"**Data Points:** {len(data_points)}\n\n"
        
        # Group by country
        by_country = {}
        for point in data_points:
            country = point.get('country', 'Unknown')
            if country not in by_country:
                by_country[country] = []
            by_country[country].append(point)
        
        for country, points in by_country.items():
            summary += f"**{country}:**\n"
            for point in points[:3]:
                year = point.get('year', 'N/A')
                value = point.get('value', 0)
                unit = point.get('unit', '')
                summary += f"  - {year}: {value:,.2f} {unit}\n"
            summary += "\n"
        
        return {
            'text': summary,
            'confidence': 95,
            'data_points': len(data_points)
        }
    
    def _format_research_papers(self, query: str, data: Dict) -> Dict:
        """Format Semantic Scholar papers"""
        
        status = data.get('status')
        if status != 'success':
            return {'text': f'Semantic Scholar error: {data.get("error", "Unknown")}', 'confidence': 0}
        
        papers = data.get('papers', [])
        
        if not papers:
            return {'text': 'No research papers found', 'confidence': 0}
        
        summary = f"# Academic Research Papers\n\n"
        summary += f"**Found {len(papers)} papers**\n\n"
        
        for i, paper in enumerate(papers, 1):
            title = paper.get('title', 'No title')
            year = paper.get('year', 'N/A')
            citations = paper.get('citations', 0)
            
            summary += f"{i}. **{title}** ({year})\n"
            summary += f"   Citations: {citations}\n\n"
        
        return {
            'text': summary,
            'confidence': 90,
            'papers_count': len(papers)
        }
    
    def _format_general_synthesis(self, query: str, all_data: List[Dict]) -> Dict:
        """General synthesis for any data type"""
        
        summary = f"# Results for: {query}\n\n"
        summary += f"**Data from {len(all_data)} sources:**\n\n"
        
        for i, item in enumerate(all_data, 1):
            source = item['source']
            summary += f"{i}. {source}\n"
        
        return {
            'text': summary,
            'confidence': 70,
            'sources_count': len(all_data)
        }
    
    def _format_generic_data(self, query: str, data: Dict) -> Dict:
        """Generic data formatter"""
        
        data_type = data.get('type', 'unknown')
        
        return {
            'text': f"Data retrieved (type: {data_type})\n\nRaw data available for processing.",
            'confidence': 50
        }
    
    def _create_no_data_response(self, query: str, sources: List[str]) -> Dict:
        """Create response when no data is retrieved"""
        
        return {
            'text': f"I searched {len(sources)} data sources but couldn't find specific information to answer: '{query}'",
            'sources': sources,
            'confidence': 0,
            'execution_time': 0,
            'timestamp': datetime.now().isoformat()
        }


class IntegratedCEOQueryHandler:
    """
    Complete pipeline: Query → Routing → Retrieval → Synthesis → Response
    """
    
    def __init__(self, use_llm_synthesis: bool = False, use_crewai: bool = False):
        """
        Initialize handler with optional multi-agent CrewAI system
        
        Args:
            use_llm_synthesis: Use LLM for synthesis (single agent)
            use_crewai: Use CrewAI multi-agent system (overrides llm_synthesis)
        """
        self.router = IntelligentQueryRouter()
        self.retriever = DataRetrievalExecutor()
        
        # CrewAI multi-agent (highest priority)
        if use_crewai:
            self.crew_orchestrator = DrOmarOrchestrator()
            self.llm_synthesizer = None
            self.use_crewai = True
            print("✓ Initialized with CrewAI multi-agent system")
        # LLM synthesis (single agent)
        elif use_llm_synthesis:
            self.llm_synthesizer = AnswerSynthesizer()
            self.crew_orchestrator = None
            self.use_crewai = False
            print("✓ Initialized with LLM synthesis")
        # Template-based (fallback)
        else:
            self.llm_synthesizer = None
            self.crew_orchestrator = None
            self.use_crewai = False
            print("✓ Initialized with template synthesis")
        
        self.template_synthesizer = CEOResponseSynthesizer()
    
    async def handle_ceo_query(self, query: str) -> Dict:
        """
        End-to-end query handling
        
        Returns:
            Dict with:
                - query: Original question
                - answer: Synthesized response
                - sources: List of data sources used
                - confidence: 0-100 confidence score
                - execution_time: Time taken
                - routing_decision: Question type identified
                - data_sources_used: Sources queried
        """
        
        start_time = time.time()
        
        # If CrewAI enabled, use multi-agent system
        if self.use_crewai:
            print(f"\n[CREWAI MULTI-AGENT] Processing query...")
            crew_result = await self.crew_orchestrator.handle_ceo_query(query)
            
            total_time = time.time() - start_time
            
            return {
                'query': query,
                'answer': crew_result['answer'],
                'sources': crew_result.get('sources', []),
                'confidence': crew_result.get('confidence', 85),
                'execution_time': total_time,
                'routing_decision': 'multi_agent_crewai',
                'data_sources_used': crew_result.get('sources', []),
                'requires_synthesis': True,
                'agent_contributions': crew_result.get('agent_contributions', {}),
                'verification_status': crew_result.get('verification_status', 'verified'),
                'timestamp': datetime.now().isoformat()
            }
        
        # Otherwise, use single-agent pipeline
        # Step 1: Route query
        print(f"\n[ROUTING] {query}")
        routing = self.router.process_ceo_query(query)
        print(f"  → Type: {routing['question_type']}")
        print(f"  → Sources: {', '.join(routing['primary_sources'][:2])}")
        
        # Step 2: Retrieve actual data
        print(f"\n[RETRIEVAL] Fetching data...")
        retrieved_data = self.retriever.execute_retrieval(routing, query)
        print(f"  → Retrieved from {len(retrieved_data['sources_queried'])} sources")
        
        # Step 3: Synthesize answer
        print(f"\n[SYNTHESIS] Creating response...")
        
        # Use LLM synthesis if available, otherwise use templates
        if self.llm_synthesizer:
            # NEW: Use LLM-powered synthesis
            synthesis_result = self.llm_synthesizer.synthesize_answer(
                query=query,
                retrieved_data=retrieved_data['data_retrieved'],
                sources=retrieved_data['sources_queried']
            )
            answer = {
                'text': synthesis_result['answer'],
                'confidence': synthesis_result['confidence'],
                'sources': synthesis_result['sources']
            }
        else:
            # Fallback to template-based synthesis
            answer = await self.template_synthesizer.synthesize_response(
                query=query,
                retrieved_data=retrieved_data,
                question_type=routing['question_type'],
                requires_synthesis=routing['requires_synthesis']
            )
        
        # Step 4: Format final response
        total_time = time.time() - start_time
        
        response = {
            'query': query,
            'answer': answer['text'],
            'sources': answer.get('sources', []),
            'confidence': answer.get('confidence', 0),
            'execution_time': total_time,
            'routing_decision': routing['question_type'],
            'data_sources_used': retrieved_data['sources_queried'],
            'requires_synthesis': routing['requires_synthesis'],
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"\n[COMPLETE] Response ready in {total_time:.2f}s")
        print(f"  → Confidence: {response['confidence']}%")
        
        return response
    
    def handle_ceo_query_sync(self, query: str) -> Dict:
        """Synchronous version for non-async environments"""
        return asyncio.run(self.handle_ceo_query(query))


# Convenience function
async def process_ceo_query(query: str) -> Dict:
    """
    Process a CEO query end-to-end
    
    Usage:
        import asyncio
        from backend.app.agents.integrated_query_handler import process_ceo_query
        
        result = asyncio.run(process_ceo_query("What was UDC's revenue?"))
        print(result['answer'])
    """
    handler = IntegratedCEOQueryHandler()
    return await handler.handle_ceo_query(query)


def process_ceo_query_sync(query: str) -> Dict:
    """
    Synchronous version
    
    Usage:
        from backend.app.agents.integrated_query_handler import process_ceo_query_sync
        
        result = process_ceo_query_sync("What was UDC's revenue?")
        print(result['answer'])
    """
    handler = IntegratedCEOQueryHandler()
    return handler.handle_ceo_query_sync(query)
