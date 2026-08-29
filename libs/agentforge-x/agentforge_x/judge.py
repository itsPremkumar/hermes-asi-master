"""
Rubric-based judge for agentforge-x.

Reuses the debate-room consensus scoring pattern: the judge evaluates
work against a rubric and returns a structured verdict with score 0-1,
evidence quotes, and improvement suggestions.

Output format (strict JSON, matching debate-room's ConsensusScore):
{"verdict": "accept"|"reject", "score": <float 0-1>, "explanation": "<string>"}
"""

from __future__ import annotations
import json
import re
from dataclasses import dataclass, field
from typing import Callable, Optional

from .agent import JudgeResult


@dataclass
class RubricCriterion:
    """A single criterion in the evaluation rubric."""
    name: str
    description: str
    weight: float = 1.0  # Relative importance (0-1)


@dataclass
class Verdict:
    """Final verdict from the judge."""
    verdict: str  # "accept" or "reject"
    score: float  # 0.0 to 1.0
    explanation: str
    evidence: list[str] = field(default_factory=list)  # Quotes from the work

    @classmethod
    def from_json_str(cls, json_str: str) -> "Verdict":
        """Parse a JSON verdict string (same interface as debate-room ConsensusScore)."""
        data = json.loads(json_str)
        return cls(
            verdict=data["verdict"],
            score=float(data["score"]),
            explanation=data.get("explanation", ""),
            evidence=data.get("evidence", []),
        )

    def to_json_str(self) -> str:
        """Serialize to JSON string matching the judge output format."""
        return json.dumps({
            "verdict": self.verdict,
            "score": self.score,
            "explanation": self.explanation,
            "evidence": self.evidence,
        })

    def to_consensus_score(self) -> "ConsensusScore":
        """Convert to the debate-room ConsensusScore format for compatibility."""
        try:
            from debate_room.debate import ConsensusScore
            return ConsensusScore(
                verdict=self.verdict,
                score=self.score,
                explanation=self.explanation,
            )
        except ImportError:
            # debate-room not installed — return a simple namespace object
            from types import SimpleNamespace
            return SimpleNamespace(
                verdict=self.verdict,
                score=self.score,
                explanation=self.explanation,
            )


@dataclass
class RubricScore:
    """Detailed scoring result from rubric evaluation."""
    criterion_scores: dict[str, float]  # criterion_name -> score (0-1)
    overall_score: float
    verdict: str
    feedback: str
    evidence: list[str] = field(default_factory=list)


class Judge:
    """
    Rubric-based judge that evaluates agent work.

    Reuses the debate-room pattern: the judge receives work output + context,
    evaluates against criteria, and returns a structured verdict.
    """

    # Default rubric criteria
    DEFAULT_CRITERIA = [
        RubricCriterion(name="correctness", description="Is the work factually and logically correct?", weight=0.3),
        RubricCriterion(name="clarity", description="Is the work clear and well-structured?", weight=0.2),
        RubricCriterion(name="completeness", description="Does the work address all requirements?", weight=0.25),
        RubricCriterion(name="quality", description="Is the quality high — well-written, thorough, professional?", weight=0.25),
    ]

    JUDGE_PROMPT_TEMPLATE = """\
You are an impartial judge evaluating agent work. Score the work against
the following criteria and produce a verdict.

Rubric:
{criteria}

Evidence quotes must be drawn directly from the work being evaluated.

Respond ONLY in strict JSON:
{{"verdict": "accept"|"reject", "score": <float 0-1>, "explanation": "<string>", "evidence": ["<quote1>", "<quote2>"]}}

Work to evaluate:
{work}

Context:
{context}"""

    def __init__(
        self,
        criteria: list[RubricCriterion] | None = None,
        llm: Optional[Callable[[str], str]] = None,
        score_threshold: float = 0.7,
    ):
        self.criteria = criteria or list(self.DEFAULT_CRITERIA)
        self.llm = llm
        self.score_threshold = score_threshold

    def _build_prompt(self, work: str, context: str = "") -> str:
        """Build the judge prompt with rubric criteria."""
        criteria_text = "\n".join(
            f"  - {c.name} (weight {c.weight}): {c.description}"
            for c in self.criteria
        )
        return self.JUDGE_PROMPT_TEMPLATE.format(
            criteria=criteria_text,
            work=work,
            context=context or "No additional context provided.",
        )

    def evaluate(self, work: str, context: str = "") -> Verdict:
        """
        Evaluate agent work and return a structured verdict.

        Args:
            work: The agent's output to evaluate
            context: Additional context (e.g., the original task)

        Returns:
            Verdict with verdict, score, explanation, and evidence quotes
        """
        prompt = self._build_prompt(work, context)

        if self.llm is None:
            # Placeholder evaluation
            return Verdict(
                verdict="accept",
                score=0.5,
                explanation="Placeholder judgment — no LLM configured.",
                evidence=[],
            )

        response = self.llm(prompt)
        return Verdict.from_json_str(response)

    def evaluate_with_critique(self, critique: JudgeResult) -> Verdict:
        """
        Convert a Critique (from the agent's own critic step) into a Verdict.

        This bridges the agent's internal self-critique with the external
        judge's verdict format.
        """
        score = critique.score
        verdict = "accept" if score >= self.score_threshold else "reject"
        evidence = critique.strengths + critique.weaknesses
        return Verdict(
            verdict=verdict,
            score=score,
            explanation=critique.feedback,
            evidence=evidence,
        )

    def score_against_rubric(self, work: str, context: str = "") -> RubricScore:
        """
        Score work against each rubric criterion individually.

        Returns per-criterion scores plus an overall score and verdict.
        """
        # For mock testing, we can evaluate each criterion separately
        criterion_scores = {}
        all_evidence = []

        for criterion in self.criteria:
            prompt = (
                f"Evaluate the following work against one criterion.\n\n"
                f"Criterion: {criterion.name} (weight {criterion.weight})\n"
                f"Description: {criterion.description}\n\n"
                f"Work: {work}\n"
                f"Context: {context or 'N/A'}\n\n"
                f"Output as: SCORE: <float 0-1> | FEEDBACK: <text> | EVIDENCE: <quote from work>"
            )

            if self.llm is None:
                score = 0.5
                evidence = "No LLM configured"
            else:
                response = self.llm(prompt)
                score_match = re.search(r'SCORE:\s*([0-9.]+)', response)
                score = float(score_match.group(1)) if score_match else 0.5
                evidence_match = re.search(r'EVIDENCE:\s*(.+)', response)
                evidence = evidence_match.group(1).strip() if evidence_match else ""

            criterion_scores[criterion.name] = score
            if evidence:
                all_evidence.append(evidence)

        # Compute weighted overall score
        total_weight = sum(c.weight for c in self.criteria)
        overall = sum(
            criterion_scores[c.name] * c.weight
            for c in self.criteria
        ) / total_weight if total_weight > 0 else 0.5

        verdict = "accept" if overall >= self.score_threshold else "reject"

        return RubricScore(
            criterion_scores=criterion_scores,
            overall_score=overall,
            verdict=verdict,
            feedback=f"Weighted score: {overall:.2f}",
            evidence=all_evidence,
        )
