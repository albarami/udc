#!/usr/bin/env python3
"""
Adaptive Expert Agent Prompts - Phase 2.6 Enhancement

Upgraded prompts with 30-year veteran thinking:
- Adaptive data retrieval (iterative search)
- Cross-domain pattern recognition
- Historical context and experience
- Assumption challenging
- Strategic synthesis
"""

# Import adaptive prompts
from adaptive_prompts import (
    DR_OMAR_ADAPTIVE_PROMPT,
    DR_FATIMA_ADAPTIVE_PROMPT,
    DR_JAMES_ADAPTIVE_PROMPT,
    DR_SARAH_ADAPTIVE_PROMPT,
    MASTER_ORCHESTRATOR_PROMPT
)

# ============================================================================
# Agent Prompt Assignments - Using Adaptive Versions
# ============================================================================

# Dr. Omar Al-Rashid - Real Estate & Property Director
AGENT_PROMPT_OMAR = DR_OMAR_ADAPTIVE_PROMPT

# Dr. Fatima Al-Kuwari - Tourism & Hospitality Director
AGENT_PROMPT_FATIMA = DR_FATIMA_ADAPTIVE_PROMPT

# Dr. James Mitchell - Chief Financial Officer
AGENT_PROMPT_JAMES = DR_JAMES_ADAPTIVE_PROMPT

# Dr. Sarah Chen - Infrastructure & Utilities Director
AGENT_PROMPT_SARAH = DR_SARAH_ADAPTIVE_PROMPT

# Master Orchestrator - Cross-Domain Synthesis
ORCHESTRATOR_PROMPT = MASTER_ORCHESTRATOR_PROMPT

# ============================================================================
# Agent Prompt Registry
# ============================================================================

AGENT_PROMPTS = {
    'dr_omar': AGENT_PROMPT_OMAR,
    'dr_fatima': AGENT_PROMPT_FATIMA,
    'dr_james': AGENT_PROMPT_JAMES,
    'dr_sarah': AGENT_PROMPT_SARAH
}
