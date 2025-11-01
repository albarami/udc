"""
Forcing Functions for Expert Behavior Validation & Enhancement
Ensures agents produce PhD-level expert output, not generic consulting speak

Two types of forcing functions:
1. PROMPT ENHANCERS (applied before LLM call) - Force veteran thinking during generation
2. OUTPUT VALIDATORS (applied after LLM call) - Validate expert patterns in output

These functions ensure that agent responses demonstrate:
1. Veteran thinking patterns (mental models, experience references)
2. Iterative reasoning (search, cross-check, pattern recognition)
3. Risk quantification (scenarios with probabilities)
4. Cross-domain connections
5. Specific recommendations (not generic)
"""

from typing import Dict, List, Any
import re


# ═══════════════════════════════════════════════════════════
# PART 1: PROMPT ENHANCERS (Real-time forcing during generation)
# ═══════════════════════════════════════════════════════════

def force_expert_thinking(base_prompt: str, query: str, context: str) -> str:
    """
    Wrap expert prompt with forcing functions that ensure veteran thinking
    
    This is applied BEFORE sending to the LLM to force veteran behavior
    during generation, not just validate after.
    
    Args:
        base_prompt: The expert embodiment prompt
        query: The CEO's question
        context: Available data context
        
    Returns:
        Enhanced prompt that forces veteran thinking patterns
    """
    
    forcing_prompt = f"""
{base_prompt}

═══════════════════════════════════════════════════════════
CRITICAL INSTRUCTIONS FOR THIS SPECIFIC QUERY
═══════════════════════════════════════════════════════════

The CEO just asked you: "{query}"

You have access to this data:
{context[:2000]}... [more data available]

NOW - THINK OUT LOUD. SHOW YOUR PROCESS.

You must:

1. START WITH YOUR GUT REACTION
   "Hmm, [question]? My first thought is..."
   NOT: "Based on analysis of the data..."

2. SHOW YOUR SEARCH PROCESS  
   "Let me look at... [searches: X]"
   "Okay, I see... But let me check..."
   "Wait, that's interesting. Let me dig deeper..."
   NOT: Just presenting conclusions

3. REFERENCE YOUR EXPERIENCE
   "I've seen this before in [place] [year]..."
   "This reminds me of when..."
   "In my experience, when X happens, Y follows..."
   NOT: Generic statements

4. DO MENTAL MATH OUT LOUD
   "Quick calculation: 150K sqm × QAR 9,500 = QAR 1.4B..."
   "Let me estimate construction costs... QAR 6,000/sqm..."
   NOT: Just final numbers

5. CHALLENGE YOURSELF
   "But wait, what if I'm wrong? If [scenario], then..."
   "Let me think about the downside... Probability: X%, Impact: Y"
   NOT: Only presenting upside

6. MAKE CROSS-DOMAIN CONNECTIONS
   "This connects to what I'm seeing in [other domain]..."
   "If real estate is X, that probably means hotels are Y because..."
   NOT: Staying only in your domain

7. END WITH CLEAR RECOMMENDATION
   "Here's what I'd do: [specific action]"
   "Why: [3-4 sentences]"
   "Risk: [what could go wrong]"
   NOT: "Further analysis is recommended"

8. TALK LIKE A PEER
   Use "I" and "you" - this is a conversation
   "Don't do it. Here's why..."
   "I'd go with X over Y because..."
   NOT: "It is recommended that..." or "One could consider..."

═══════════════════════════════════════════════════════════
EXAMPLES OF CORRECT VS WRONG THINKING
═══════════════════════════════════════════════════════════

❌ WRONG (Analyst Report Style):
"Analysis of transaction data indicates 12% YoY volume growth with 
stable pricing. Market segmentation reveals bifurcation between luxury 
and mid-market segments. Based on these findings, a strategic pivot 
toward mid-market residential development is recommended."

✅ CORRECT (Veteran Thinking Out Loud):
"Hmm, volumes up 12% but prices flat? That's weird. Let me check 
segmentation... [searches: luxury vs mid-market]

Okay, there it is. Luxury inventory at 36 months, mid at 8 months. 
I've seen this before - Dubai 2014. Same pattern.

Why? GCC investors pulling back. I know these buyers - when Saudis 
leave, pricing pressure follows 6 months later.

My call: Don't touch luxury. Go mid-market. Here's why..."

═══════════════════════════════════════════════════════════

NOW: Answer the CEO's question using the CORRECT style.

Think out loud. Show your process. Be the veteran you are.

GO:
"""
    
    return forcing_prompt


def force_orchestrator_synthesis(
    base_prompt: str, 
    query: str, 
    agent_analyses: List[Dict[str, Any]]
) -> str:
    """
    Force orchestrator to see cross-domain patterns specialists miss
    
    Applied before orchestrator synthesis to ensure cross-domain thinking.
    
    Args:
        base_prompt: The master orchestrator embodiment prompt
        query: The CEO's original question
        agent_analyses: List of expert analyses to synthesize
        
    Returns:
        Enhanced prompt that forces cross-domain synthesis
    """
    
    # Format agent analyses
    analyses_text = ""
    for analysis in agent_analyses:
        analyses_text += f"\n--- {analysis.get('agent', 'Expert')} ({analysis.get('role', 'Specialist')}) ---\n"
        analyses_text += f"{analysis.get('response', analysis.get('answer', ''))[:1000]}...\n"
    
    forcing_prompt = f"""
{base_prompt}

═══════════════════════════════════════════════════════════
CRITICAL: YOUR JOB IS TO SEE WHAT SPECIALISTS MISSED
═══════════════════════════════════════════════════════════

CEO asked: "{query}"

The domain experts gave their analyses. Here they are:

{analyses_text}

YOUR JOB: Find the pattern they're all missing.

You must:

1. LOOK FOR CONTRADICTIONS
   "Wait - Expert A says X, but Expert B says Y. Why?"
   "Real estate weak BUT hotels weak too? That's not random..."

2. FIND THE HIDDEN PATTERN
   "AHA! It's not a demand problem. It's a SEGMENT problem."
   "I see it now - this is capital flight, not demand weakness."

3. CONNECT ACROSS DOMAINS
   "If luxury real estate is weak AND luxury hotels are weak,
   but government spending is strong, then..."

4. REFERENCE HISTORICAL PATTERNS
   "This is exactly what happened in [place] [year]"
   "I've seen this cycle before. Here's what happens next..."

5. THINK ABOUT SEQUENCING
   "They're recommending A, B, and C. But you can't do all three.
   Here's the right sequence: First A (because...), then B (because...), 
   then C (because...)."

6. IDENTIFY SECOND-ORDER EFFECTS
   "If we do X, competitors will do Y, which means market will do Z."
   "Everyone's focused on the direct effect. But the real impact is..."

7. CHALLENGE THE CONSENSUS
   "All four experts lean toward X. But let me challenge that.
   What if they're all missing [specific risk/opportunity]?"

8. PROVIDE DEFINITIVE GUIDANCE
   "Here's what the CEO should do: [specific, sequenced actions]"
   "Not: Consider these options"
   "But: DO THIS. Don't do that. Here's why."

═══════════════════════════════════════════════════════════
EXAMPLE OF CORRECT SYNTHESIS:
═══════════════════════════════════════════════════════════

"Wait. Let me look at what all four experts are saying...

Omar: Luxury oversupplied
Fatima: Hotels weak  
James: Government spending strong
Sarah: Infrastructure capacity available

They're each right in their domain. But they're missing the connection.

Luxury real estate weak + Luxury hotels weak = Not a demand problem.
It's a CAPITAL FLIGHT problem.

Where's the capital going? Saudi Vision 2030. NEOM. Riyadh.

Meanwhile, government spending is strong. That's creating MIDDLE-CLASS 
jobs. They don't buy luxury - they buy mid-market.

So the strategy isn't 'wait for luxury to recover.' It's 'PIVOT to 
mid-market NOW before competitors figure this out.'

But here's the sequencing issue:

Can't do Pearl immediately (infrastructure upgrades needed).
Can't do Lusail luxury (wrong segment).

Answer: Gewan Island mid-market FIRST. Infrastructure is ready.
Prove concept. Then Pearl Phase 2.

That's the play."

═══════════════════════════════════════════════════════════

NOW: Synthesize like this. Find what they missed. Show the pattern.
Provide definitive strategic guidance.

GO:
"""
    
    return forcing_prompt


# ═══════════════════════════════════════════════════════════
# PART 2: OUTPUT VALIDATORS (Post-generation quality checks)
# ═══════════════════════════════════════════════════════════


class ExpertBehaviorValidator:
    """
    Validates that agent responses demonstrate true expert thinking
    vs generic AI output
    """
    
    # Patterns that indicate expert-level thinking
    EXPERT_PATTERNS = {
        'mental_math': [
            r'\d+\s*[×x]\s*\d+\s*=',  # Mental calculations
            r'QAR\s+[\d,]+M?\s+[×x÷/]\s+',  # QAR calculations
            r'\d+%\s+of\s+QAR'  # Percentage calculations
        ],
        'pattern_recognition': [
            r'I\'?ve seen this before',
            r'reminds me of',
            r'same pattern',
            r'exactly what happened in',
            r'this is like',
            r'similar to.*\d{4}'  # Reference to historical year
        ],
        'iterative_search': [
            r'\[searches?:',
            r'let me check',
            r'let me pull',
            r'let me cross-check',
            r'wait.*let me'
        ],
        'self_challenge': [
            r'what if I\'?m wrong',
            r'let me challenge',
            r'but wait',
            r'scenario \d+:',
            r'probability:?\s*\d+'
        ],
        'cross_domain': [
            r'but.*says',  # Connecting different data points
            r'this connects to',
            r'when I see.*but also',
            r'that tells me'
        ],
        'quantified_risk': [
            r'probability:?\s*\d+[-–]?\d*%',
            r'expected value',
            r'worst case.*\d+%',
            r'IRR.*\d+[-–]?\d*%'
        ],
        'veteran_language': [
            r'don\'?t do it',
            r'that\'?s bullshit',
            r'here\'?s the play',
            r'slam dunk',
            r'no contest',
            r'absolutely not'
        ]
    }
    
    # Anti-patterns (generic consulting speak to AVOID)
    ANTI_PATTERNS = {
        'consulting_speak': [
            r'based on (?:our )?analysis',
            r'comprehensive assessment',
            r'strategic evaluation',
            r'it is recommended',
            r'further research is needed',
            r'additional analysis required'
        ],
        'generic_language': [
            r'various (?:options|factors)',
            r'multiple considerations',
            r'potential (?:benefits|risks)',
            r'could potentially',
            r'may suggest that'
        ],
        'ai_tells': [
            r'as an AI',
            r'I apologize',
            r'I don\'?t have personal',
            r'it\'?s important to note'
        ]
    }
    
    def validate_expert_thinking(self, response: str, agent_role: str) -> Dict[str, Any]:
        """
        Validate that response demonstrates expert-level thinking
        
        Args:
            response: Agent response text
            agent_role: Role of agent (e.g., "Real Estate", "CFO")
            
        Returns:
            Dict with validation results and scores
        """
        results = {
            'is_expert_level': False,
            'score': 0.0,
            'expert_signals': [],
            'anti_patterns_found': [],
            'missing_elements': [],
            'recommendations': []
        }
        
        # Count expert patterns
        expert_count = 0
        for category, patterns in self.EXPERT_PATTERNS.items():
            matches = []
            for pattern in patterns:
                found = re.findall(pattern, response, re.IGNORECASE)
                matches.extend(found)
            
            if matches:
                expert_count += len(matches)
                results['expert_signals'].append({
                    'category': category,
                    'count': len(matches),
                    'examples': matches[:3]  # First 3 examples
                })
        
        # Check for anti-patterns
        anti_pattern_count = 0
        for category, patterns in self.ANTI_PATTERNS.items():
            matches = []
            for pattern in patterns:
                found = re.findall(pattern, response, re.IGNORECASE)
                matches.extend(found)
            
            if matches:
                anti_pattern_count += len(matches)
                results['anti_patterns_found'].append({
                    'category': category,
                    'count': len(matches),
                    'examples': matches[:3]
                })
        
        # Check for missing critical elements
        if not any(cat == 'mental_math' for cat in [s['category'] for s in results['expert_signals']]):
            results['missing_elements'].append('mental_math')
        
        if not any(cat == 'self_challenge' for cat in [s['category'] for s in results['expert_signals']]):
            results['missing_elements'].append('self_challenge')
        
        if not any(cat == 'quantified_risk' for cat in [s['category'] for s in results['expert_signals']]):
            results['missing_elements'].append('quantified_risk')
        
        # Calculate score (0-100)
        # Expert signals: +10 each, capped at 80
        # Anti-patterns: -15 each
        # Missing elements: -10 each
        score = min(expert_count * 10, 80)
        score -= anti_pattern_count * 15
        score -= len(results['missing_elements']) * 10
        score = max(0, min(100, score))
        
        results['score'] = score
        results['is_expert_level'] = score >= 60  # 60+ is expert level
        
        # Generate recommendations
        if anti_pattern_count > 0:
            results['recommendations'].append(
                "Remove consulting speak - talk like a veteran, not a consultant"
            )
        
        if 'mental_math' in results['missing_elements']:
            results['recommendations'].append(
                "Show mental calculations - demonstrate quick feasibility math"
            )
        
        if 'self_challenge' in results['missing_elements']:
            results['recommendations'].append(
                "Challenge yourself - 'What if I'm wrong? Here are scenarios...'"
            )
        
        if 'pattern_recognition' not in [s['category'] for s in results['expert_signals']]:
            results['recommendations'].append(
                "Reference historical patterns - 'I've seen this in Dubai 2014...'"
            )
        
        return results
    
    def validate_thinking_process(self, response: str) -> Dict[str, bool]:
        """
        Validate that response shows explicit thinking process
        (not just conclusions)
        """
        checks = {
            'shows_iterative_search': False,
            'shows_data_interpretation': False,
            'shows_cross_checking': False,
            'shows_mental_model': False,
            'shows_scenario_thinking': False
        }
        
        # Check for iterative search
        if re.search(r'\[search', response, re.IGNORECASE):
            checks['shows_iterative_search'] = True
        
        # Check for data interpretation
        interpretation_patterns = [
            r'(?:volumes|prices|occupancy).*but',
            r'that\'?s unusual',
            r'something\'?s off',
            r'that tells me'
        ]
        if any(re.search(p, response, re.IGNORECASE) for p in interpretation_patterns):
            checks['shows_data_interpretation'] = True
        
        # Check for cross-checking
        cross_check_patterns = [
            r'let me cross[- ]check',
            r'but.*also.*shows?',
            r'compare.*to'
        ]
        if any(re.search(p, response, re.IGNORECASE) for p in cross_check_patterns):
            checks['shows_cross_checking'] = True
        
        # Check for mental model
        if re.search(r'three possibilities|when I see.*three', response, re.IGNORECASE):
            checks['shows_mental_model'] = True
        
        # Check for scenario thinking
        if re.search(r'scenario \d+:|base case|downside|worst case', response, re.IGNORECASE):
            checks['shows_scenario_thinking'] = True
        
        return checks
    
    def validate_recommendation_quality(self, response: str) -> Dict[str, Any]:
        """
        Validate that recommendations are specific and actionable
        (not generic)
        """
        quality = {
            'has_clear_recommendation': False,
            'is_quantified': False,
            'has_conditions': False,
            'has_risk_acknowledgment': False,
            'has_sequencing': False,
            'score': 0
        }
        
        # Check for clear recommendation
        rec_patterns = [
            r'(?:my |here\'?s my )?recommendation:?',
            r'(?:here\'?s what|this is what) I\'?d do',
            r'(?:GO|NO GO) on'
        ]
        if any(re.search(p, response, re.IGNORECASE) for p in rec_patterns):
            quality['has_clear_recommendation'] = True
            quality['score'] += 25
        
        # Check for quantification
        quant_patterns = [
            r'QAR \d+[.,]?\d*[BMK]',
            r'\d+%\s+(?:IRR|margin|return)',
            r'\d+[-–]\d+\s+months'
        ]
        if any(re.search(p, response, re.IGNORECASE) for p in quant_patterns):
            quality['is_quantified'] = True
            quality['score'] += 25
        
        # Check for conditions
        cond_patterns = [
            r'(?:BUT|IF) (?:conditional on|only if)',
            r'YES.*BUT',
            r'NO.*UNLESS'
        ]
        if any(re.search(p, response, re.IGNORECASE) for p in cond_patterns):
            quality['has_conditions'] = True
            quality['score'] += 20
        
        # Check for risk acknowledgment
        risk_patterns = [
            r'risk:?\s+what if',
            r'what could go wrong',
            r'downside:?'
        ]
        if any(re.search(p, response, re.IGNORECASE) for p in risk_patterns):
            quality['has_risk_acknowledgment'] = True
            quality['score'] += 20
        
        # Check for sequencing
        seq_patterns = [
            r'phase \d+',
            r'first.*then.*finally',
            r'step \d+:',
            r'Q[1-4] \d{4}'
        ]
        if any(re.search(p, response, re.IGNORECASE) for p in seq_patterns):
            quality['has_sequencing'] = True
            quality['score'] += 10
        
        return quality


# Singleton instance
expert_validator = ExpertBehaviorValidator()


def validate_expert_response(
    response: str,
    agent_role: str,
    include_thinking_check: bool = True,
    include_recommendation_check: bool = True
) -> Dict[str, Any]:
    """
    Comprehensive validation of expert-level response
    
    Args:
        response: Agent response text
        agent_role: Role of agent
        include_thinking_check: Whether to validate thinking process
        include_recommendation_check: Whether to validate recommendation quality
        
    Returns:
        Dict with comprehensive validation results
    """
    results = {
        'agent_role': agent_role,
        'expert_validation': expert_validator.validate_expert_thinking(response, agent_role),
        'overall_grade': 'PENDING'
    }
    
    if include_thinking_check:
        results['thinking_validation'] = expert_validator.validate_thinking_process(response)
    
    if include_recommendation_check:
        results['recommendation_validation'] = expert_validator.validate_recommendation_quality(response)
    
    # Calculate overall grade
    expert_score = results['expert_validation']['score']
    
    if include_recommendation_check:
        rec_score = results['recommendation_validation']['score']
        overall_score = (expert_score * 0.7) + (rec_score * 0.3)
    else:
        overall_score = expert_score
    
    # Grade
    if overall_score >= 85:
        results['overall_grade'] = 'PhD Expert (A+)'
    elif overall_score >= 70:
        results['overall_grade'] = 'Senior Expert (A)'
    elif overall_score >= 55:
        results['overall_grade'] = 'Expert (B+)'
    elif overall_score >= 40:
        results['overall_grade'] = 'Professional (B)'
    else:
        results['overall_grade'] = 'Generic (C or below)'
    
    results['overall_score'] = round(overall_score, 1)
    
    return results
