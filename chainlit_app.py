"""
Chainlit UI for Unbeatable Strategic Council
Beautiful chat interface for the PhD Expert System
"""

import chainlit as cl
import os
from dotenv import load_dotenv
from backend.app.agents.unbeatable_council import UnbeatableStrategicCouncil

# Load environment variables
load_dotenv()


@cl.on_chat_start
async def start():
    """Initialize the chat session"""
    
    # Welcome message
    await cl.Message(
        content="""# 🏆 Welcome to the Unbeatable Strategic Council

**Your PhD-Level Strategic Intelligence System**

I have assembled a team of 5 veteran experts for you:
- 👤 **Dr. Omar Al-Rashid** - Real Estate & Property Development (30 years)
- 👤 **Dr. Fatima Al-Thani** - Tourism & Hospitality (25 years)
- 👤 **Dr. James Mitchell** - Finance & Economics (25 years)
- 👤 **Dr. Sarah Al-Kuwari** - Infrastructure & Sustainability (20 years)
- 👤 **Master Orchestrator** - CEO Strategic Advisor (30+ years)

---

**Ask me any strategic question about:**
- Real estate investments
- Tourism & hospitality strategy
- Financial decisions
- Infrastructure projects
- Cross-domain strategic planning

*Example: "Should UDC invest in luxury residential at Lusail or mid-market at The Pearl?"*

**Note:** Each analysis takes 30-60 seconds as I consult all experts.
        """,
        author="System"
    ).send()
    
    # Initialize council
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        await cl.Message(
            content="❌ ERROR: ANTHROPIC_API_KEY not found. Please set it in your .env file.",
            author="System"
        ).send()
        return
    
    council = UnbeatableStrategicCouncil(
        anthropic_api_key=api_key,
        enable_reinforcement=True,
        enable_validation=True
    )
    
    # Store in session
    cl.user_session.set("council", council)
    
    await cl.Message(
        content="✅ **All systems ready!** Ask your strategic question below.",
        author="System"
    ).send()


@cl.on_message
async def main(message: cl.Message):
    """Handle user messages"""
    
    council = cl.user_session.get("council")
    
    if not council:
        await cl.Message(
            content="❌ Council not initialized. Please refresh the page.",
            author="System"
        ).send()
        return
    
    question = message.content
    
    # Show thinking message
    thinking_msg = cl.Message(
        content="🤔 **Consulting the Strategic Council...**\n\n"
                "⏳ Running 7-stage analysis pipeline:\n"
                "1. Data retrieval\n"
                "2. Expert analyses (4 experts in parallel)\n"
                "3. Quality validation\n"
                "4. Strategic reasoning\n"
                "5. Debate identification\n"
                "6. Master orchestrator synthesis\n"
                "7. Decision sheet generation\n\n"
                "*This takes 30-60 seconds. Please wait...*",
        author="System"
    )
    await thinking_msg.send()
    
    try:
        # Get analysis
        result = await council.analyze_ceo_question(question)
        
        # Update thinking message
        await thinking_msg.remove()
        
        # Show expert analyses
        elements = []
        
        for i, analysis in enumerate(result['expert_analyses'], 1):
            expert_content = f"""### 👤 {analysis['agent']}
**{analysis['domain']}**

{analysis['analysis']}
"""
            
            if analysis.get('validation'):
                val = analysis['validation']
                expert_content += f"\n\n**Quality Score:** {val['overall_score']}/100 ({val['overall_grade']})"
            
            elements.append(
                cl.Text(
                    name=f"expert_{i}",
                    content=expert_content,
                    display="side"
                )
            )
        
        # Show final recommendation
        final_content = f"""# 🎯 Final Strategic Recommendation

{result['final_recommendation']}

---

### 📊 Analysis Quality

**Overall Rating:** {result['quality_assessment']['quality_rating']}
**Average Expert Score:** {result['quality_assessment']['average_score']:.1f}/100
**Expert-Level Rate:** {result['quality_assessment'].get('expert_rate', 0)*100:.0f}%

---

### 💰 Analysis Metadata

- **Duration:** {result['metadata'].get('duration_seconds', 0):.1f} seconds
- **Cost:** QAR {result['metadata']['estimated_cost_qar']:.2f}
- **Models Used:** {result['metadata']['models_used']['experts']} (experts), {result['metadata']['models_used']['synthesis']} (synthesis)
- **Total Tokens:** {result['metadata']['total_tokens']:,}

---

### 📋 Executive Summary

{result['executive_summary']}
"""
        
        # Send final recommendation
        await cl.Message(
            content=final_content,
            author="Master Orchestrator",
            elements=elements
        ).send()
        
    except Exception as e:
        await cl.Message(
            content=f"❌ **Error during analysis:**\n\n```\n{str(e)}\n```\n\nPlease try again or check your configuration.",
            author="System"
        ).send()


if __name__ == "__main__":
    # This won't run directly - use: chainlit run chainlit_app.py
    pass
