"""
Expert Embodiment Prompts v2.0
TRUE PhD-level expertise - Not instructions, but IDENTITY
Each agent BECOMES the expert through examples, not guidelines

This system transforms AI agents from instruction-followers to veteran experts
who think out loud, showing their reasoning process, pattern recognition,
and cross-domain connections.

Key Principles:
1. EMBODIMENT: Agents don't roleplay, they ARE the expert
2. EXAMPLES: Show thinking process, not just guidelines
3. FORCING FUNCTIONS: Structure that ensures expert-level output
4. VETERAN THINKING: 30+ years experience, real scars, real wins
"""

# Import individual embodiment modules
from .embodiments import (
    dr_omar,
    dr_fatima,
    dr_james,
    dr_sarah,
    master_orchestrator
)

# Export embodiment prompts
DR_OMAR_EMBODIMENT = dr_omar.EMBODIMENT_PROMPT
DR_FATIMA_EMBODIMENT = dr_fatima.EMBODIMENT_PROMPT
DR_JAMES_EMBODIMENT = dr_james.EMBODIMENT_PROMPT
DR_SARAH_EMBODIMENT = dr_sarah.EMBODIMENT_PROMPT
MASTER_ORCHESTRATOR_EMBODIMENT = master_orchestrator.EMBODIMENT_PROMPT

__all__ = [
    'DR_OMAR_EMBODIMENT',
    'DR_FATIMA_EMBODIMENT',
    'DR_JAMES_EMBODIMENT',
    'DR_SARAH_EMBODIMENT',
    'MASTER_ORCHESTRATOR_EMBODIMENT',
]
