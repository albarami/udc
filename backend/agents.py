#!/usr/bin/env python3
"""
Phase 2.3: Strategic Agent Framework

4 specialized agents for UDC Strategic Council:
1. Dr. Omar Al-Rashid - Real Estate & Construction Expert
2. Dr. Fatima Al-Kuwari - Tourism & Hospitality Director
3. Dr. James Mitchell - Chief Financial Officer
4. Dr. Sarah Chen - Infrastructure & Utilities Director

Each agent has:
- Expertise domain
- Personality/analysis style
- Category filtering for relevant datasets
- Custom prompts reflecting their perspective
"""

from typing import Dict, Any, Optional
from rag_system import retrieve_datasets, assemble_context, openai_client, openai_available
# Using enhanced adaptive prompts (Phase 2.6)
from agent_prompts import AGENT_PROMPTS

# Model configuration for different components
MODEL_CONFIG = {
    'agent_analysis': 'gpt-4o',  # High-quality strategic analysis
    'query_classification': 'gpt-3.5-turbo',  # Fast, cheap classification
    'temperature': 0.3,  # Balance creativity and factuality
    'max_tokens': 2000  # Comprehensive analysis
}


class StrategicAgent:
    """
    Base class for UDC Strategic Council agents
    
    Each agent is a domain expert that analyzes queries from their
    specialized perspective using category-filtered RAG retrieval.
    """
    
    def __init__(
        self,
        name: str,
        title: str,
        expertise: str,
        category: str,
        personality: str,
        background: str = "",
        prompt_key: Optional[str] = None
    ):
        """
        Initialize a strategic agent
        
        Args:
            name: Agent's full name (e.g., "Dr. Omar Al-Rashid")
            title: Professional title (e.g., "Chief Real Estate Strategist")
            expertise: Domain expertise description
            category: Primary category for dataset filtering
            personality: Analysis style and approach
            background: Optional additional context
            prompt_key: Key for expert prompt in AGENT_PROMPTS dict
        """
        self.name = name
        self.title = title
        self.expertise = expertise
        self.category = category
        self.personality = personality
        self.background = background
        self.prompt_key = prompt_key
        
        # Get expert prompt if available
        self.expert_prompt = AGENT_PROMPTS.get(prompt_key) if prompt_key else None
    
    def analyze(
        self,
        query: str,
        top_k: int = 5,
        include_sources: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze a query from this agent's expert perspective
        
        Args:
            query: User's question
            top_k: Number of datasets to retrieve
            include_sources: Include source datasets in response
            
        Returns:
            Dictionary with analysis and optional sources
        """
        # 1. Retrieve datasets filtered by agent's category
        retrieval_results = retrieve_datasets(
            query=query,
            category=self.category,
            top_k=top_k
        )
        
        # 2. Assemble context
        context = assemble_context(retrieval_results)
        
        # 3. Build agent-specific prompt
        prompt = self._build_prompt(query, context)
        
        # 4. Generate answer
        answer = self._generate_answer(prompt)
        
        # 5. Prepare response
        response = {
            'agent_name': self.name,
            'agent_title': self.title,
            'agent_expertise': self.expertise,
            'query': query,
            'analysis': answer,
            'num_sources': retrieval_results['num_results']
        }
        
        if include_sources:
            response['sources'] = retrieval_results['results']
        
        return response
    
    def _build_prompt(self, query: str, context: str) -> str:
        """Build agent-specific prompt with personality and expertise"""
        
        # Use expert prompt if available, otherwise use basic prompt
        if self.expert_prompt:
            # Expert prompt format: System prompt + Context + Query
            prompt = f"""{self.expert_prompt}

═══════════════════════════════════════════════════════════
UDC CONTEXT
═══════════════════════════════════════════════════════════
United Development Company (UDC) is Qatar's master developer, operating:
- The Pearl-Qatar: Luxury waterfront development
- Lusail: Smart city development
- UDC Tower: Premium commercial real estate
- Various hospitality and retail assets

═══════════════════════════════════════════════════════════
RELEVANT DATA SOURCES
═══════════════════════════════════════════════════════════
{context}

═══════════════════════════════════════════════════════════
CEO'S STRATEGIC QUESTION
═══════════════════════════════════════════════════════════
{query}

═══════════════════════════════════════════════════════════
YOUR EXPERT ANALYSIS (Use the 5-section structure defined above)
═══════════════════════════════════════════════════════════
"""
        else:
            # Fallback to basic prompt
            prompt = f"""You are {self.name}, {self.title} at United Development Company (UDC).

=== YOUR PROFILE ===
Expertise: {self.expertise}
Analysis Style: {self.personality}
"""
            
            if self.background:
                prompt += f"Background: {self.background}\n"
            
            prompt += f"""
=== UDC CONTEXT ===
United Development Company (UDC) is Qatar's master developer, operating:
- The Pearl-Qatar: Luxury waterfront development with residential, retail, and hospitality
- Lusail: Smart city development north of Doha
- UDC Tower: Premium commercial real estate
- Various hospitality and retail assets

=== RELEVANT DATA ===
{context}

=== STRATEGIC QUESTION ===
{query}

=== YOUR TASK ===
Provide strategic analysis from your expert perspective:

1. **Data Analysis**: What do the datasets tell us?
2. **Strategic Insights**: What are the implications for UDC?
3. **Opportunities**: What opportunities do you identify?
4. **Risks/Limitations**: What data gaps or risks exist?
5. **Recommendations**: What specific actions should UDC consider?

Guidelines:
- Analyze from YOUR specialized perspective ({self.expertise})
- Cite specific datasets using [1], [2], [3]
- Be concise and actionable
- Acknowledge data limitations transparently
- Focus on strategic value for UDC's business

=== YOUR STRATEGIC ANALYSIS ===
"""
        
        return prompt
    
    def _generate_answer(self, prompt: str) -> str:
        """Generate answer using LLM (GPT-4o for expert-level analysis)"""
        
        if not openai_available or openai_client is None:
            return "[LLM NOT AVAILABLE] OpenAI API key not configured."
        
        try:
            # Use GPT-4o for high-quality strategic analysis
            model = MODEL_CONFIG['agent_analysis']
            
            response = openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": f"You are {self.name}, {self.title} for UDC. Provide expert-level strategic analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=MODEL_CONFIG['max_tokens'],
                temperature=MODEL_CONFIG['temperature']
            )
            
            return response.choices[0].message.content or ""
            
        except Exception as e:
            return f"Error generating analysis: {str(e)}"
    
    def __repr__(self):
        return f"<Agent: {self.name} ({self.title})>"


# ============================================================================
# AGENT DEFINITIONS: The 4 Core Strategic Council Members
# ============================================================================

# 1. Dr. Omar Al-Rashid - Real Estate Expert
dr_omar = StrategicAgent(
    name="Dr. Omar Al-Rashid",
    title="Chief Real Estate Strategist",
    expertise="Real estate market analysis, property development strategies, GCC investment trends, urban development economics",
    category="Real Estate & Construction",
    personality="Data-driven and analytical. Focused on ROI, market positioning, and long-term asset value. Direct communication style with emphasis on financial metrics and competitive advantage.",
    background="20+ years experience in GCC real estate markets. Previously led major developments in Dubai and Riyadh. Holds PhD in Urban Economics from LSE.",
    prompt_key="dr_omar"  # Use expert prompt
)

# 2. Dr. Fatima Al-Kuwari - Tourism & Hospitality Expert  
dr_fatima = StrategicAgent(
    name="Dr. Fatima Al-Kuwari",
    title="Tourism & Hospitality Director",
    expertise="Tourism sector analysis, hospitality performance metrics, visitor experience optimization, destination marketing strategy",
    category="Tourism & Hospitality",
    personality="Customer-focused and trend-aware. Emphasizes guest satisfaction, market positioning, and revenue optimization. Balances quantitative metrics with qualitative experience factors.",
    background="15+ years in Qatar's hospitality sector. Led tourism strategy for major Qatari developments. Expert in luxury hospitality and destination branding.",
    prompt_key="dr_fatima"  # Use expert prompt
)

# 3. Dr. James Mitchell - Chief Financial Officer
dr_james = StrategicAgent(
    name="Dr. James Mitchell",
    title="Chief Financial Officer",
    expertise="Economic analysis, financial modeling, macroeconomic trends, investment climate assessment, risk management",
    category="Economic & Financial",
    personality="Analytical and risk-aware. Focused on financial performance, economic stability, and strategic financial planning. Conservative approach with emphasis on data-driven decision making.",
    background="25+ years in corporate finance and economic analysis. Previously CFO of major GCC developers. Chartered Financial Analyst (CFA) and MBA from INSEAD.",
    prompt_key="dr_james"  # Use expert prompt
)

# 4. Dr. Sarah Chen - Infrastructure Expert
dr_sarah = StrategicAgent(
    name="Dr. Sarah Chen",
    title="Infrastructure & Utilities Director",
    expertise="Infrastructure development, utilities management, construction project analysis, sustainable urban systems, smart city technologies",
    category="Infrastructure & Utilities",
    personality="Technical and detail-oriented. Focused on sustainability, operational efficiency, and long-term infrastructure resilience. Systems-thinking approach with emphasis on integration.",
    background="18+ years in infrastructure development across Asia and Middle East. Led smart city initiatives. PhD in Civil Engineering from MIT, specialization in sustainable urban systems.",
    prompt_key="dr_sarah"  # Use expert prompt
)


# ============================================================================
# AGENT REGISTRY
# ============================================================================

STRATEGIC_COUNCIL = {
    'real_estate': dr_omar,
    'tourism': dr_fatima,
    'finance': dr_james,
    'infrastructure': dr_sarah
}

# Category to agent mapping for routing
CATEGORY_TO_AGENT = {
    'Real Estate & Construction': dr_omar,
    'Tourism & Hospitality': dr_fatima,
    'Economic & Financial': dr_james,
    'Infrastructure & Utilities': dr_sarah,
    'Population & Demographics': dr_james,  # Default to CFO for demographics
    'Employment & Labor': dr_james,  # Default to CFO for employment
    'Energy & Sustainability': dr_sarah,  # Infrastructure handles energy
}


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def get_agent(domain: str) -> Optional[StrategicAgent]:
    """
    Get agent by domain key
    
    Args:
        domain: One of 'real_estate', 'tourism', 'finance', 'infrastructure'
        
    Returns:
        StrategicAgent or None if not found
    """
    return STRATEGIC_COUNCIL.get(domain.lower())


def get_agent_by_category(category: str) -> Optional[StrategicAgent]:
    """
    Get appropriate agent for a category
    
    Args:
        category: Category name (e.g., "Tourism & Hospitality")
        
    Returns:
        StrategicAgent or None if no mapping exists
    """
    return CATEGORY_TO_AGENT.get(category)


def list_agents() -> Dict[str, StrategicAgent]:
    """Get all available agents"""
    return STRATEGIC_COUNCIL


# ============================================================================
# Main execution (for testing)
# ============================================================================

if __name__ == "__main__":
    print("="*100)
    print("UDC STRATEGIC COUNCIL - AGENT FRAMEWORK")
    print("="*100)
    print()
    
    print("Available Agents:")
    print("-" * 100)
    for key, agent in STRATEGIC_COUNCIL.items():
        print(f"{key:15s} | {agent.name:30s} | {agent.title}")
    print()
    
    print("Agent Details:")
    print("-" * 100)
    for agent in STRATEGIC_COUNCIL.values():
        print(f"\n{agent.name} - {agent.title}")
        print(f"Expertise: {agent.expertise}")
        print(f"Category: {agent.category}")
        print(f"Style: {agent.personality[:80]}...")
    print()
