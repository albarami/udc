"""
Reinforcement System - Ensures expert behavior throughout conversation
Multiple checkpoints that reinforce veteran thinking

This system provides dynamic monitoring and reinforcement:
1. Checks each response for expert quality
2. Detects when agents slip into "analyst mode"
3. Re-injects expert prompting if needed
4. Maintains coherence across multi-agent conversations
"""

from typing import Dict, List, Any, Optional
import re


class ExpertBehaviorReinforcer:
    """
    Monitors agent output and reinforces expert behavior
    If agent slips into analyst mode, reinjects expert prompting
    """
    
    def __init__(self):
        # Red flags indicate analyst/consultant mode (BAD)
        self.analyst_red_flags = [
            "based on analysis",
            "the data shows",
            "it is recommended",
            "one could consider",
            "further research",
            "additional analysis",
            "in conclusion",
            "to summarize",
            "comprehensive assessment",
            "strategic evaluation",
            "it would be prudent",
            "consideration should be given"
        ]
        
        # Green flags indicate veteran expert mode (GOOD)
        self.expert_green_flags = [
            "i've seen this before",
            "let me think",
            "here's what i'd do",
            "don't do it",
            "my first thought",
            "wait",
            "hmm",
            "in my experience",
            "reminds me of",
            "quick calculation",
            "let me check",
            "my call",
            "here's the play"
        ]
    
    def check_expert_quality(self, response: str) -> Dict[str, Any]:
        """
        Check if response shows expert-level thinking
        
        Args:
            response: Agent response text to check
            
        Returns:
            Dict with quality assessment and recommendations
        """
        
        response_lower = response.lower()
        
        # Count red flags (analyst behavior)
        red_flags_found = [flag for flag in self.analyst_red_flags 
                          if flag in response_lower]
        
        # Count green flags (expert behavior)
        green_flags_found = [flag for flag in self.expert_green_flags 
                            if flag in response_lower]
        
        # Check for mental math
        has_math = bool(re.search(r'\d+\s*[×x]\s*\d+|=\s*QAR|IRR|NPV|\d+%\s*(?:return|margin|IRR)', response))
        
        # Check for historical references
        has_history = bool(re.search(r'20\d{2}|Dubai|Abu Dhabi|Saudi|Qatar|2008|crisis|boom|cycle', response, re.IGNORECASE))
        
        # Check for thinking out loud
        has_thinking = bool(re.search(r'let me|wait|hmm|first thought|searches?:', 
                                     response_lower))
        
        # Check for scenarios/self-challenge
        has_scenarios = bool(re.search(r'scenario \d+|what if|probability|downside|worst case', 
                                      response_lower))
        
        # Calculate score
        score = (
            len(green_flags_found) * 2  # Green flags worth 2 points each
            - len(red_flags_found) * 3  # Red flags penalize 3 points each
            + (5 if has_math else 0)
            + (5 if has_history else 0)
            + (5 if has_thinking else 0)
            + (5 if has_scenarios else 0)
        )
        
        # Determine if expert level (needs good score AND few red flags)
        is_expert_level = score >= 10 and len(red_flags_found) < 2
        
        return {
            'is_expert_level': is_expert_level,
            'score': score,
            'red_flags': red_flags_found,
            'green_flags': green_flags_found,
            'has_math': has_math,
            'has_history': has_history,
            'has_thinking': has_thinking,
            'has_scenarios': has_scenarios,
            'feedback': self._generate_feedback(score, red_flags_found, 
                                               green_flags_found, has_math,
                                               has_history, has_thinking)
        }
    
    def _generate_feedback(self, score: int, red_flags: List[str], 
                          green_flags: List[str], has_math: bool,
                          has_history: bool, has_thinking: bool) -> str:
        """
        Generate feedback for improving response
        
        Args:
            score: Calculated quality score
            red_flags: List of analyst phrases found
            green_flags: List of expert phrases found
            has_math: Whether mental math was shown
            has_history: Whether historical references used
            has_thinking: Whether thinking process shown
            
        Returns:
            Feedback string with recommendations
        """
        
        if score >= 20:
            return "🏆 EXCELLENT - True PhD expert-level thinking"
        elif score >= 15:
            return "✅ VERY GOOD - Strong veteran perspective"
        elif score >= 10:
            return "✅ GOOD - Expert-level with minor improvements possible"
        elif score >= 5:
            return "⚠️ ACCEPTABLE - Some expert thinking but too analytical"
        else:
            feedback = "❌ NEEDS IMPROVEMENT - Too much analyst mode. Need:\n"
            
            if not has_thinking:
                feedback += "  • Show thinking process ('Let me think...', 'Hmm...')\n"
            if not has_history:
                feedback += "  • Add historical references ('I've seen this in Dubai 2014...')\n"
            if not has_math:
                feedback += "  • Show mental math ('Quick calc: 150K × QAR 9,500 = ...')\n"
            if not green_flags:
                feedback += "  • Use veteran language ('Don't do it', 'Here's my call')\n"
            if red_flags:
                feedback += f"  • Remove analyst phrases: {', '.join(red_flags[:3])}\n"
            
            return feedback


class ConversationReinforcer:
    """
    Maintains expert persona throughout multi-turn conversations
    Injects reinforcement prompts if agents slip into analyst mode
    """
    
    def __init__(self):
        self.reinforcer = ExpertBehaviorReinforcer()
        self.conversation_history: List[Dict[str, Any]] = []
        self.reinforcement_count = 0
    
    def check_and_reinforce(self, agent_name: str, response: str, 
                           base_prompt: str) -> Optional[str]:
        """
        Check response quality and generate reinforcement if needed
        
        Args:
            agent_name: Name of the agent
            response: Agent's response to check
            base_prompt: Base expert embodiment prompt
            
        Returns:
            Reinforcement prompt if needed, None otherwise
        """
        
        quality = self.reinforcer.check_expert_quality(response)
        
        # Track conversation history
        self.conversation_history.append({
            'agent': agent_name,
            'quality_score': quality['score'],
            'is_expert_level': quality['is_expert_level'],
            'timestamp': len(self.conversation_history)
        })
        
        # If quality is poor, generate reinforcement
        if not quality['is_expert_level']:
            self.reinforcement_count += 1
            
            reinforcement = self._generate_reinforcement_prompt(
                agent_name, quality, base_prompt
            )
            
            return reinforcement
        
        return None  # No reinforcement needed
    
    def _generate_reinforcement_prompt(self, agent_name: str, 
                                       quality: Dict[str, Any],
                                       base_prompt: str) -> str:
        """
        Generate reinforcement prompt to bring agent back to expert mode
        
        Args:
            agent_name: Name of the agent
            quality: Quality assessment dict
            base_prompt: Base embodiment prompt
            
        Returns:
            Reinforcement prompt string
        """
        
        reinforcement = f"""

═══════════════════════════════════════════════════════════
⚠️ REMINDER: YOU'RE {agent_name.upper()}, NOT AN ANALYST
═══════════════════════════════════════════════════════════

Your last response was too formal/analytical. You used phrases like:
{', '.join(f'"{flag}"' for flag in quality['red_flags'][:3]) if quality['red_flags'] else 'generic analyst language'}

REMEMBER: You're a VETERAN with 30 years of real-world experience.

You need to:

1. THINK OUT LOUD
   Show your process: "Hmm, let me think..." "Wait, that's interesting..."

2. REFERENCE YOUR EXPERIENCE  
   "I've seen this before in [place] [year]..."
   "This reminds me of when..."

3. DO MENTAL MATH
   "Quick calculation: 150K sqm × QAR 9,500 = QAR 1.4B..."

4. CHALLENGE YOURSELF
   "What if I'm wrong? Scenario 1: If [X], then [Y]..."

5. BE SPECIFIC & DIRECT
   Not: "It is recommended that..."
   But: "Don't do it. Here's why..."

═══════════════════════════════════════════════════════════
EXAMPLE OF CORRECT STYLE:
═══════════════════════════════════════════════════════════

"Hmm, [question]? Let me think about this...

[searches: relevant data]

Okay, I see [observation]. But wait, that's unusual because...

I've seen this pattern before - [place] [year]. When [X] happened, 
[Y] followed 6 months later.

Quick math: [show calculation]

What if I'm wrong? Probability: [X]%. Downside: [Y].

My call: [specific recommendation]. Here's why..."

═══════════════════════════════════════════════════════════

Now continue with your veteran perspective. Show your thinking.
"""
        
        return reinforcement
    
    def get_conversation_stats(self) -> Dict[str, Any]:
        """
        Get statistics on conversation quality over time
        
        Returns:
            Dict with conversation statistics
        """
        
        if not self.conversation_history:
            return {
                'total_turns': 0,
                'average_score': 0,
                'expert_level_rate': 0,
                'reinforcements_needed': 0
            }
        
        scores = [turn['quality_score'] for turn in self.conversation_history]
        expert_level = [turn['is_expert_level'] for turn in self.conversation_history]
        
        return {
            'total_turns': len(self.conversation_history),
            'average_score': sum(scores) / len(scores),
            'expert_level_rate': sum(expert_level) / len(expert_level),
            'reinforcements_needed': self.reinforcement_count,
            'latest_score': scores[-1] if scores else 0,
            'trend': self._analyze_trend(scores)
        }
    
    def _analyze_trend(self, scores: List[int]) -> str:
        """
        Analyze trend in conversation quality
        
        Args:
            scores: List of quality scores over time
            
        Returns:
            Trend description string
        """
        
        if len(scores) < 3:
            return "Insufficient data"
        
        recent = scores[-3:]
        earlier = scores[:-3] if len(scores) > 3 else [scores[0]]
        
        recent_avg = sum(recent) / len(recent)
        earlier_avg = sum(earlier) / len(earlier)
        
        if recent_avg > earlier_avg + 5:
            return "📈 IMPROVING - Quality increasing"
        elif recent_avg < earlier_avg - 5:
            return "📉 DECLINING - Quality decreasing (needs attention)"
        else:
            return "➡️ STABLE - Consistent quality"


class MultiAgentCoherence:
    """
    Ensures agents maintain expertise when responding to each other
    Checks quality across all agents in multi-agent discussions
    """
    
    def __init__(self):
        self.reinforcer = ExpertBehaviorReinforcer()
    
    def check_cross_agent_quality(self, agent_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Check if agents are maintaining expert level across the board
        
        Args:
            agent_analyses: List of dicts with 'agent', 'role', 'analysis' keys
            
        Returns:
            Dict with multi-agent quality assessment
        """
        
        agent_scores = []
        for analysis in agent_analyses:
            response_text = analysis.get('analysis') or analysis.get('response') or analysis.get('answer', '')
            quality = self.reinforcer.check_expert_quality(response_text)
            
            agent_scores.append({
                'agent': analysis.get('agent', 'Unknown'),
                'role': analysis.get('role', 'Unknown'),
                'score': quality['score'],
                'is_expert': quality['is_expert_level'],
                'red_flags': len(quality['red_flags']),
                'green_flags': len(quality['green_flags'])
            })
        
        # Calculate aggregate metrics
        avg_score = sum(a['score'] for a in agent_scores) / len(agent_scores) if agent_scores else 0
        all_expert_level = all(a['is_expert'] for a in agent_scores)
        expert_count = sum(1 for a in agent_scores if a['is_expert'])
        
        return {
            'average_score': round(avg_score, 1),
            'all_expert_level': all_expert_level,
            'expert_count': expert_count,
            'total_agents': len(agent_scores),
            'expert_rate': expert_count / len(agent_scores) if agent_scores else 0,
            'agent_scores': agent_scores,
            'quality_rating': self._rate_quality(avg_score, all_expert_level, expert_count, len(agent_scores)),
            'recommendations': self._generate_multi_agent_recommendations(agent_scores)
        }
    
    def _rate_quality(self, avg_score: float, all_expert: bool, 
                     expert_count: int, total: int) -> str:
        """
        Rate overall quality of multi-agent response
        
        Args:
            avg_score: Average quality score across agents
            all_expert: Whether all agents are at expert level
            expert_count: Number of expert-level agents
            total: Total number of agents
            
        Returns:
            Quality rating string
        """
        
        if all_expert and avg_score >= 20:
            return "🏆 EXCEPTIONAL - All agents at PhD expert level"
        elif all_expert and avg_score >= 15:
            return "🏆 EXCELLENT - All agents at strong expert level"
        elif all_expert and avg_score >= 10:
            return "✅ GOOD - All agents showing veteran perspective"
        elif expert_count / total >= 0.75:
            return "✅ MOSTLY GOOD - Majority at expert level, some need reinforcement"
        elif expert_count / total >= 0.5:
            return "⚠️ MIXED - Half at expert level, half need improvement"
        else:
            return "❌ POOR - System needs recalibration and stronger forcing"
    
    def _generate_multi_agent_recommendations(self, agent_scores: List[Dict[str, Any]]) -> List[str]:
        """
        Generate recommendations for improving multi-agent quality
        
        Args:
            agent_scores: List of agent score dicts
            
        Returns:
            List of recommendation strings
        """
        
        recommendations = []
        
        # Check for agents that need improvement
        weak_agents = [a for a in agent_scores if not a['is_expert']]
        
        if not weak_agents:
            recommendations.append("✅ All agents performing at expert level")
        else:
            recommendations.append(f"⚠️ {len(weak_agents)} agent(s) need reinforcement:")
            for agent in weak_agents[:3]:  # Show top 3
                recommendations.append(f"  • {agent['agent']}: Score {agent['score']} (needs improvement)")
        
        # Check for excessive red flags across all agents
        total_red_flags = sum(a['red_flags'] for a in agent_scores)
        if total_red_flags > len(agent_scores) * 2:
            recommendations.append("⚠️ Too many analyst phrases across agents - strengthen forcing functions")
        
        # Check for insufficient green flags
        total_green_flags = sum(a['green_flags'] for a in agent_scores)
        if total_green_flags < len(agent_scores) * 2:
            recommendations.append("⚠️ Insufficient veteran language - ensure embodiment prompts are active")
        
        return recommendations


# Singleton instances for easy import
expert_reinforcer = ExpertBehaviorReinforcer()
conversation_reinforcer = ConversationReinforcer()
multi_agent_coherence = MultiAgentCoherence()


# Convenience functions
def check_expert_quality(response: str) -> Dict[str, Any]:
    """Quick function to check expert quality of a response."""
    return expert_reinforcer.check_expert_quality(response)


def reinforce_if_needed(agent_name: str, response: str, base_prompt: str) -> Optional[str]:
    """Quick function to check and generate reinforcement if needed."""
    return conversation_reinforcer.check_and_reinforce(agent_name, response, base_prompt)


def check_multi_agent_quality(agent_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Quick function to check quality across multiple agents."""
    return multi_agent_coherence.check_cross_agent_quality(agent_analyses)
