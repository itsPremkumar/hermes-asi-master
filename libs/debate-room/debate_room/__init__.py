"""
debate-room: A multi-agent debate & consensus framework.

Core components:
- roles: Proposer, Critic, Judge agent roles
- debate: k-round debate loop with consensus scoring
- cli: Command-line interface
- mock: Mock LLM for testing
"""

from debate_room.roles import Proposer, Critic, Judge, BaseRole
from debate_room.debate import Debate, DebateResult, ConsensusScore
from debate_room.mock import MockLLM

__version__ = "1.0.0"
__all__ = [
    "Proposer",
    "Critic",
    "Judge",
    "BaseRole",
    "Debate",
    "DebateResult",
    "ConsensusScore",
    "MockLLM",
]
