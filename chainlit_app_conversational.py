"""
UDC Strategic Intelligence - CrewAI Multi-Agent System
Natural conversation with multi-agent collaboration
"""

import sys
sys.path.insert(0, 'D:/udc')

import chainlit as cl
from typing import Dict, List, Optional
import time
from datetime import datetime
import json
from pathlib import Path
import asyncio

# Import CrewAI orchestrator
from backend.app.agents.crewai_base import DrOmarOrchestrator

# Initialize CrewAI orchestrator
dr_omar = DrOmarOrchestrator()

# Conversation memory file
CONVERSATION_MEMORY_FILE = Path("data/ceo_conversation_memory.json")


class ConversationalMemory:
    """
    Stores CEO-provided information for future queries
    """
    def __init__(self):
        self.memory = self._load_memory()
    
    def _load_memory(self) -> Dict:
        """Load existing conversation memory"""
        if CONVERSATION_MEMORY_FILE.exists():
            with open(CONVERSATION_MEMORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'ceo_provided_info': {},
            'conversation_history': [],
            'clarifications': {}
        }
    
    def save(self):
        """Persist memory to disk"""
        CONVERSATION_MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CONVERSATION_MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, indent=2)
    
    def add_ceo_info(self, topic: str, information: str):
        """Store information provided by CEO"""
        self.memory['ceo_provided_info'][topic] = {
            'info': information,
            'timestamp': datetime.now().isoformat()
        }
        self.save()
    
    def get_ceo_info(self, topic: str) -> Optional[str]:
        """Retrieve CEO-provided information"""
        return self.memory['ceo_provided_info'].get(topic, {}).get('info')
    
    def add_to_history(self, query: str, response: str):
        """Add to conversation history"""
        self.memory['conversation_history'].append({
            'query': query,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        # Keep last 50 exchanges
        self.memory['conversation_history'] = self.memory['conversation_history'][-50:]
        self.save()


# Global memory instance
conversation_memory = ConversationalMemory()


@cl.on_chat_start
async def start():
    """
    Welcome with multi-agent team introduction
    """
    msg = cl.Message(content="")
    await msg.send()
    
    welcome = """Hello! I'm Dr. Omar Habib, leading a team of specialist agents to provide you with comprehensive strategic intelligence.

**My team includes:**
- 🏦 **Dr. James Chen** - Financial Intelligence (Revenue, profits, financial analysis)
- 📊 **Dr. Fatima Al-Mansoori** - Market Analysis (Qatar/GCC markets, trends)
- 🏢 **Dr. Sarah Williams** - Operations (Property performance, efficiency)
- 🔬 **Research Specialists** - External intelligence and academic research

When you ask a question, we collaborate to dig deep and provide you with multi-perspective insights backed by real data.

**What we can analyze:**
- UDC's financial performance and metrics
- Property portfolio and operations
- Qatar and GCC market intelligence
- Strategic opportunities and risks

What would you like to know?"""
    
    # Stream the welcome message
    for word in welcome.split():
        await msg.stream_token(word + " ")
        await asyncio.sleep(0.02)
    
    await msg.update()
    
    # Initialize session
    cl.user_session.set("conversation_memory", conversation_memory)
    cl.user_session.set("queries_count", 0)
    cl.user_session.set("awaiting_clarification", None)


@cl.on_message
async def main(message: cl.Message):
    """
    Handle conversational queries with streaming responses
    """
    query = message.content
    memory = cl.user_session.get("conversation_memory")
    
    # Check if we're waiting for CEO to provide missing information
    awaiting = cl.user_session.get("awaiting_clarification")
    if awaiting:
        # CEO is answering our question
        await handle_ceo_answer(query, awaiting)
        cl.user_session.set("awaiting_clarification", None)
        return
    
    # Create streaming message
    response_msg = cl.Message(content="")
    await response_msg.send()
    
    try:
        # Route and analyze query
        await response_msg.stream_token("*Analyzing your question...*\n\n")
        await asyncio.sleep(0.3)
        
        # Check if we have the data
        data_check = await check_data_availability(query)
        
        if not data_check['has_data']:
            # We don't have this data - ask CEO conversationally
            await handle_missing_data(response_msg, query, data_check)
            return
        
        # We have the data - retrieve and respond
        await stream_answer_with_data(response_msg, query, memory)
        
    except Exception as e:
        await response_msg.stream_token(
            f"\n\n*I encountered an issue: {str(e)}*\n\n"
            "Could you rephrase your question, or let me know if you'd like me to explain what happened?"
        )
        await response_msg.update()


async def check_data_availability(query: str) -> Dict:
    """
    Check if we have data to answer this query
    """
    # Check if query is about UDC-specific info we might not have
    udc_specific_queries = [
        'strategy', 'plan', 'goal', 'target', 'forecast', 
        'future', 'next', 'upcoming', 'pipeline', 'roadmap',
        'expansion', 'vision', 'mission', 'initiative'
    ]
    
    query_lower = query.lower()
    
    # If asking about future plans, we probably need CEO input
    if any(term in query_lower for term in udc_specific_queries):
        if 'udc' in query_lower or 'our' in query_lower or 'we' in query_lower:
            return {
                'has_data': False,
                'reason': 'future_plans',
                'suggested_question': "Could you share more about this plan or goal?"
            }
    
    return {'has_data': True}


async def handle_missing_data(msg: cl.Message, query: str, data_check: Dict):
    """
    Conversationally ask CEO for missing information
    """
    # Clear the analyzing message
    msg.content = ""
    
    conversational_responses = {
        'future_plans': [
            "I don't have information about future plans or strategies in my database. ",
            "\n\nThis is something only you would know! ",
            "\n\nCould you share what you're thinking? I'll remember it for our future conversations."
        ],
        'no_data_source': [
            "I don't seem to have data on this specific topic in my knowledge base. ",
            "\n\nBut I'm always learning! ",
            "\n\nCan you tell me more about it? I'll save it and use it to help you better in the future."
        ]
    }
    
    reason = data_check.get('reason', 'no_data_source')
    response_parts = conversational_responses.get(
        reason, 
        conversational_responses['no_data_source']
    )
    
    # Stream the response
    for part in response_parts:
        for word in part.split():
            await msg.stream_token(word + " ")
            await asyncio.sleep(0.02)
    
    await msg.update()
    
    # Mark that we're waiting for CEO input
    cl.user_session.set("awaiting_clarification", {
        'original_query': query,
        'reason': reason,
        'timestamp': datetime.now().isoformat()
    })


async def handle_ceo_answer(answer: str, context: Dict):
    """
    CEO provided information we didn't have
    """
    memory = cl.user_session.get("conversation_memory")
    
    # Store the CEO's answer
    original_query = context['original_query']
    memory.add_ceo_info(original_query, answer)
    
    # Acknowledge receipt
    msg = cl.Message(content="")
    await msg.send()
    
    acknowledgment = "Got it! I've saved this information. "
    
    # Stream acknowledgment
    for word in acknowledgment.split():
        await msg.stream_token(word + " ")
        await asyncio.sleep(0.02)
    
    # Now provide follow-up
    await msg.stream_token("\n\nBased on what you just told me")
    
    # Generate follow-up
    follow_up = await generate_follow_up_with_context(original_query, answer, memory)
    
    for word in follow_up.split():
        await msg.stream_token(" " + word)
        await asyncio.sleep(0.02)
    
    await msg.update()


async def stream_answer_with_data(
    msg: cl.Message, 
    query: str, 
    memory: ConversationalMemory
):
    """
    Stream a conversational answer using CrewAI multi-agent system
    """
    # Clear analyzing message
    msg.content = ""
    
    # Show collaboration happening
    await msg.stream_token("🤔 Analyzing your question...\n\n")
    await asyncio.sleep(0.5)
    
    await msg.stream_token("👥 Consulting specialist agents...\n")
    await asyncio.sleep(0.5)
    
    await msg.stream_token("💬 Agents are collaborating...\n\n")
    await asyncio.sleep(0.5)
    
    # Execute multi-agent system
    response = await dr_omar.handle_ceo_query(query)
    
    # Show which agents contributed
    if response.get('agent_contributions'):
        await msg.stream_token("**🎯 Agent Insights:**\n")
        for agent_type, agent_name in response['agent_contributions'].items():
            await msg.stream_token(f"• {agent_name}\n")
        await msg.stream_token("\n---\n\n")
        await asyncio.sleep(0.5)
    
    # Check confidence
    confidence = response.get('confidence', 0)
    
    # Conversational opening based on confidence  
    if confidence >= 80:
        opening = "Based on our multi-agent analysis, "
    elif confidence >= 60:
        opening = "From what our team found, "
    else:
        opening = "Our agents found some information, though we're not entirely certain: "
    
    # Stream opening
    for word in opening.split():
        await msg.stream_token(word + " ")
        await asyncio.sleep(0.02)
    
    # Stream main answer
    answer = response['answer']
    
    # Make it more conversational
    answer = make_conversational(answer)
    
    # Stream word by word for natural feel
    words = answer.split()
    for i, word in enumerate(words):
        await msg.stream_token(word + " ")
        
        # Natural pauses at punctuation
        if word.endswith(('.', '!', '?')):
            await asyncio.sleep(0.15)
        elif word.endswith(','):
            await asyncio.sleep(0.08)
        else:
            await asyncio.sleep(0.02)
    
    # Add context from memory if relevant
    ceo_context = memory.get_ceo_info(query)
    if ceo_context:
        await msg.stream_token(
            f"\n\n*Also, based on what you told me earlier:* {ceo_context}"
        )
    
    # Add sources conversationally
    sources = response.get('data_sources_used', [])
    if sources:
        await msg.stream_token(
            f"\n\n---\n*Sources used: {format_sources_conversational(sources)}*"
        )
    
    # Add verification status
    verification = response.get('verification_status', 'verified')
    await msg.stream_token(
        f"\n*Confidence: {confidence}% | Verification: {verification}*"
    )
    
    # Add confidence note if low
    if confidence < 70:
        await msg.stream_token(
            f"\n\n*Note: Our team is about {confidence}% confident. "
            "If you have more specific information, we'd love to learn from you!*"
        )
    
    # Suggest follow-up questions
    follow_ups = generate_follow_up_questions(query, response)
    if follow_ups:
        await msg.stream_token("\n\n**You might also want to ask:**\n")
        for follow_up in follow_ups[:2]:
            await msg.stream_token(f"- {follow_up}\n")
    
    await msg.update()
    
    # Save to conversation history
    memory.add_to_history(query, answer)


def make_conversational(answer: str) -> str:
    """
    Make technical answers more conversational
    """
    # Add conversational connectors
    conversational_patterns = {
        'The data shows': "Here's what the data tells us:",
        'According to': 'Looking at',
        'The results indicate': 'It looks like',
        'Analysis reveals': 'From what I can see,',
        'In summary': 'To sum up,',
        'Therefore': 'So basically,',
        'However': "But here's the thing:",
        'Additionally': 'Also,',
        'Furthermore': 'And another thing:',
    }
    
    for formal, casual in conversational_patterns.items():
        answer = answer.replace(formal, casual)
    
    return answer


def format_sources_conversational(sources: List[str]) -> str:
    """
    Format sources in a conversational way
    """
    source_names = {
        'udc_financial_json': 'your financial records',
        'udc_financial_pdfs': 'your financial statements',
        'udc_property_json': 'your property portfolio data',
        'qatar_economic_csvs': "Qatar's economic statistics",
        'qatar_tourism_csvs': "Qatar's tourism data",
        'world_bank_api': 'the World Bank',
        'semantic_scholar_api': 'academic research',
        'udc_salary_surveys': 'salary survey data',
        'qatar_employment_csvs': 'Qatar employment statistics',
        'udc_strategy_documents': 'your strategy documents',
    }
    
    readable = [source_names.get(s, s) for s in sources]
    
    if len(readable) == 1:
        return readable[0]
    elif len(readable) == 2:
        return f"{readable[0]} and {readable[1]}"
    else:
        return f"{', '.join(readable[:-1])}, and {readable[-1]}"


def generate_follow_up_questions(query: str, response: Dict) -> List[str]:
    """
    Generate contextual follow-up questions
    """
    query_lower = query.lower()
    
    follow_ups = []
    
    # Context-aware suggestions
    if 'revenue' in query_lower:
        follow_ups.extend([
            "What's our profit margin?",
            "How does this compare to last year?"
        ])
    
    elif 'gdp' in query_lower or 'economy' in query_lower:
        follow_ups.extend([
            "What's driving this growth?",
            "How does the tourism sector contribute?"
        ])
    
    elif 'hotel' in query_lower or 'occupancy' in query_lower:
        follow_ups.extend([
            "How does this compare to other GCC countries?",
            "What's the trend over the last year?"
        ])
    
    elif 'property' in query_lower or 'portfolio' in query_lower:
        follow_ups.extend([
            "What's the occupancy rate for these properties?",
            "How is Pearl-Qatar performing?"
        ])
    
    elif 'salary' in query_lower or 'pay' in query_lower:
        follow_ups.extend([
            "How does this compare to regional averages?",
            "What about other senior positions?"
        ])
    
    # Default follow-ups
    if not follow_ups:
        follow_ups = [
            "Can you give me more context on this?",
            "How does this compare to our competitors?"
        ]
    
    return follow_ups


async def generate_follow_up_with_context(
    original_query: str, 
    ceo_answer: str, 
    memory: ConversationalMemory
) -> str:
    """
    Generate a follow-up response incorporating CEO's answer
    """
    # Simple contextual response
    return (
        f" and combining it with my data, "
        f"I'll be able to give you better insights on '{original_query}' in the future. "
        f"Is there anything else related to this you'd like to explore?"
    )


# Session management
@cl.on_chat_end
async def on_chat_end():
    """
    Save session when CEO ends chat
    """
    memory = cl.user_session.get("conversation_memory")
    if memory:
        memory.save()
        print(f"Session ended. Conversation saved.")


if __name__ == "__main__":
    from chainlit.cli import run_chainlit
    run_chainlit(__file__)
