"""Scientific Discovery Engine — full discovery pipeline.

Implements the complete scientific method loop:
  literature_search -> hypothesis -> experiment_design -> simulation ->
  execution -> measurement -> critique -> replication -> conclusion

Usage:
    from advanced.scientific_discovery import DiscoveryPipeline
    p = DiscoveryPipeline()
    result = p.run("Why do some alloys resist corrosion?")
    print(result.conclusion)
"""
from __future__ import annotations

import random
import statistics
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional


class Confidence(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

    def __ge__(self, other):
        order = [Confidence.LOW, Confidence.MEDIUM, Confidence.HIGH, Confidence.VERY_HIGH]
        return order.index(self) >= order.index(other)


@dataclass
class Paper:
    title: str
    authors: list[str]
    year: int
    abstract: str
    findings: list[str] = field(default_factory=list)
    doi: str = ""
    relevance_score: float = 0.0


@dataclass
class Hypothesis:
    statement: str
    rationale: str
    predictions: list[str] = field(default_factory=list)
    confidence: Confidence = Confidence.LOW
    evidence_for: list[str] = field(default_factory=list)
    evidence_against: list[str] = field(default_factory=list)
    falsifiable: bool = True

    def __str__(self) -> str:
        return f"Hypothesis: {self.statement} [{self.confidence.value}]"


@dataclass
class Experiment:
    name: str
    hypothesis: str
    independent_vars: list[str] = field(default_factory=list)
    dependent_vars: list[str] = field(default_factory=list)
    controls: list[str] = field(default_factory=list)
    procedure: list[str] = field(default_factory=list)
    materials: list[str] = field(default_factory=list)
    sample_size: int = 30
    replications: int = 3


@dataclass
class Measurement:
    variable: str
    value: float
    unit: str
    uncertainty: float = 0.0
    replicate_id: int = 0

    def __str__(self) -> str:
        return f"{self.variable} = {self.value} +/- {self.uncertainty} {self.unit}"


@dataclass
class Dataset:
    name: str
    measurements: list[Measurement] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add(self, m: Measurement) -> None:
        self.measurements.append(m)

    def mean(self, variable: str) -> Optional[float]:
        vals = [m.value for m in self.measurements if m.variable == variable]
        return statistics.mean(vals) if vals else None

    def stdev(self, variable: str) -> Optional[float]:
        vals = [m.value for m in self.measurements if m.variable == variable]
        return statistics.stdev(vals) if len(vals) >= 2 else None

    def summary(self, variable: str) -> dict[str, Any]:
        vals = [m.value for m in self.measurements if m.variable == variable]
        if not vals:
            return {"variable": variable, "n": 0}
        return {
            "variable": variable,
            "n": len(vals),
            "mean": statistics.mean(vals),
            "stdev": statistics.stdev(vals) if len(vals) >= 2 else 0.0,
            "min": min(vals),
            "max": max(vals),
        }


@dataclass
class Critique:
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    threats_to_validity: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    overall_quality: float = 0.5  # 0 to 1


@dataclass
class ReplicationResult:
    original_finding: str
    replicated: bool
    effect_size_original: float = 0.0
    effect_size_replication: float = 0.0
    notes: str = ""


@dataclass
class Conclusion:
    hypothesis: str
    supported: bool
    confidence: Confidence
    evidence_summary: str
    limitations: list[str] = field(default_factory=list)
    future_work: list[str] = field(default_factory=list)
    replication_results: list[ReplicationResult] = field(default_factory=list)

    def __str__(self) -> str:
        status = "SUPPORTED" if self.supported else "NOT SUPPORTED"
        return f"Conclusion: {self.hypothesis} -> {status} [{self.confidence.value}]"


@dataclass
class DiscoveryResult:
    query: str
    papers: list[Paper] = field(default_factory=list)
    hypotheses: list[Hypothesis] = field(default_factory=list)
    experiments: list[Experiment] = field(default_factory=list)
    datasets: list[Dataset] = field(default_factory=list)
    critiques: list[Critique] = field(default_factory=list)
    conclusion: Optional[Conclusion] = None
    iterations: int = 0

    def summary(self) -> str:
        lines = [
            f"Discovery Result for: {self.query}",
            f"  Papers reviewed: {len(self.papers)}",
            f"  Hypotheses tested: {len(self.hypotheses)}",
            f"  Experiments conducted: {len(self.experiments)}",
            f"  Iterations: {self.iterations}",
        ]
        if self.conclusion:
            lines.append(f"  {self.conclusion}")
        return "\n".join(lines)


class LiteratureSearch:
    """Simulated literature search engine."""

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self._corpus: list[Paper] = []

    def index(self, papers: list[Paper]) -> None:
        self._corpus.extend(papers)

    def search(self, query: str, max_results: int = 10) -> list[Paper]:
        """Search papers by keyword overlap."""
        query_words = set(query.lower().split())
        scored = []
        for paper in self._corpus:
            title_words = set(paper.title.lower().split())
            abstract_words = set(paper.abstract.lower().split())
            overlap = len(query_words & (title_words | abstract_words))
            if overlap > 0:
                scored.append((overlap, paper))
        scored.sort(key=lambda x: x[0], reverse=True)
        results = [p for _, p in scored[:max_results]]
        for p in results:
            p.relevance_score = self.rng.uniform(0.5, 1.0)
        return results

    def synthesize(self, papers: list[Paper]) -> str:
        """Generate a synthesis of findings."""
        if not papers:
            return "No relevant literature found."
        all_findings = []
        for p in papers:
            all_findings.extend(p.findings)
        if not all_findings:
            return f"Reviewed {len(papers)} papers. No consistent findings extracted."
        return (
            f"Synthesis of {len(papers)} papers ({len(all_findings)} findings): "
            + "; ".join(all_findings[:5])
        )


class HypothesisGenerator:
    """Generate hypotheses from literature synthesis."""

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)

    def generate(self, synthesis: str, n: int = 3) -> list[Hypothesis]:
        """Generate n candidate hypotheses."""
        templates = [
            "Factor X positively correlates with outcome Y",
            "Mechanism Z mediates the relationship between A and B",
            "Intervention W reduces the occurrence of phenomenon V",
            "Variable U moderates the effect of T on S",
            "Process R is necessary for phenomenon Q to occur",
        ]
        hypotheses = []
        for i in range(min(n, len(templates))):
            h = Hypothesis(
                statement=templates[i],
                rationale=f"Inferred from: {synthesis[:100]}...",
                predictions=[f"Prediction {i+1}: measurable outcome" for a in range(1, 3)],
                confidence=Confidence.LOW,
                falsifiable=True,
            )
            hypotheses.append(h)
        return hypotheses

    def refine(self, hypothesis: Hypothesis, evidence: str) -> Hypothesis:
        """Refine a hypothesis based on new evidence."""
        hypothesis.evidence_for.append(evidence)
        if len(hypothesis.evidence_for) >= 3:
            hypothesis.confidence = Confidence.MEDIUM
        if len(hypothesis.evidence_for) >= 5:
            hypothesis.confidence = Confidence.HIGH
        return hypothesis


class ExperimentDesigner:
    """Design experiments to test hypotheses."""

    def design(self, hypothesis: Hypothesis) -> Experiment:
        """Create an experiment for the given hypothesis."""
        return Experiment(
            name=f"Test: {hypothesis.statement[:50]}",
            hypothesis=hypothesis.statement,
            independent_vars=["treatment"],
            dependent_vars=["outcome"],
            controls=["control_group", "placebo"],
            procedure=[
                "1. Randomize subjects into treatment and control",
                "2. Apply treatment",
                "3. Measure outcome after fixed interval",
                "4. Analyze with t-test",
            ],
            materials=["subjects", "treatment_agent", "measurement_tools"],
            sample_size=30,
            replications=3,
        )

    def power_analysis(self, effect_size: float = 0.5, alpha: float = 0.05,
                       power: float = 0.8) -> int:
        """Estimate required sample size (simplified)."""
        # Simplified: n = 16 / effect_size^2 (for 80% power, two-tailed)
        if effect_size <= 0:
            return 100
        n = int(16 / (effect_size ** 2))
        return max(n, 10)


class Simulator:
    """Simulate experiment outcomes."""

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)

    def run_trial(self, experiment: Experiment,
                  treatment_effect: float = 0.5) -> Dataset:
        """Simulate one trial."""
        ds = Dataset(name=experiment.name)
        for rep in range(experiment.replications):
            for i in range(experiment.sample_size):
                is_treatment = i >= experiment.sample_size // 2
                base = self.rng.gauss(10.0, 2.0)
                if is_treatment:
                    base += treatment_effect + self.rng.gauss(0, 0.5)
                ds.add(Measurement(
                    variable="outcome",
                    value=base,
                    unit="units",
                    uncertainty=0.1,
                    replicate_id=rep,
                ))
        return ds

    def run_monte_carlo(self, experiment: Experiment,
                        n_simulations: int = 100,
                        treatment_effect: float = 0.5) -> list[Dataset]:
        """Run multiple simulations."""
        return [self.run_trial(experiment, treatment_effect)
                for _ in range(n_simulations)]


class StatisticalAnalyzer:
    """Analyze experimental data."""

    @staticmethod
    def t_test(dataset: Dataset, variable: str = "outcome") -> dict[str, float]:
        """Simple two-sample t-test (treatment vs control)."""
        vals = [m.value for m in dataset.measurements if m.variable == variable]
        n = len(vals) // 2
        if n < 2:
            return {"t_stat": 0.0, "p_value": 1.0, "significant": False}
        group_a = vals[:n]
        group_b = vals[n:]
        mean_a = statistics.mean(group_a)
        mean_b = statistics.mean(group_b)
        var_a = statistics.variance(group_a) if len(group_a) > 1 else 1.0
        var_b = statistics.variance(group_b) if len(group_b) > 1 else 1.0
        se = (var_a / n + var_b / n) ** 0.5
        if se == 0:
            return {"t_stat": 0.0, "p_value": 1.0, "significant": False}
        t_stat = (mean_a - mean_b) / se
        # Simplified p-value approximation
        p_value = max(0.001, min(1.0, 2 * (1 - _abs_t_cdf(abs(t_stat), 2 * n - 2))))
        return {
            "t_stat": t_stat,
            "p_value": p_value,
            "significant": p_value < 0.05,
            "mean_diff": mean_a - mean_b,
        }

    @staticmethod
    def effect_size(dataset: Dataset, variable: str = "outcome") -> float:
        """Cohen's d."""
        vals = [m.value for m in dataset.measurements if m.variable == variable]
        n = len(vals) // 2
        if n < 2:
            return 0.0
        group_a = vals[:n]
        group_b = vals[n:]
        mean_diff = statistics.mean(group_a) - statistics.mean(group_b)
        pooled_std = (
            (statistics.variance(group_a) + statistics.variance(group_b)) / 2
        ) ** 0.5
        if pooled_std == 0:
            return 0.0
        return mean_diff / pooled_std

    @staticmethod
def _abs_t_cdf(t: float, df: int) -> float:
    """Approximate CDF of t-distribution."""
    # Simple approximation for testing
    x = df / (df + t * t)
    # Incomplete beta approximation (rough)
    if t == 0:
        return 0.5
    # Use normal approximation for df > 30
    if df > 30:
        return _norm_cdf(t)
    # Rough approximation
    return 0.5 + 0.5 * (1 - x ** (df / 2)) * (1 if t > 0 else -1)


def _norm_cdf(x: float) -> float:
    """Approximate normal CDF."""
    import math
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


class Critiquer:
    """Critique experimental design and findings."""

    def critique(self, experiment: Experiment, dataset: Dataset,
                 analysis: dict[str, float]) -> Critique:
        c = Critique()
        # Strengths
        if experiment.sample_size >= 30:
            c.strengths.append("Adequate sample size")
        if experiment.replications >= 3:
            c.strengths.append("Multiple replications")
        if experiment.controls:
            c.strengths.append("Proper controls included")
        # Weaknesses
        if experiment.sample_size < 30:
            c.weaknesses.append("Small sample size")
        if not experiment.controls:
            c.weaknesses.append("No controls")
        # Threats
        if analysis.get("p_value", 1.0) > 0.05:
            c.threats_to_validity.append("Result not statistically significant")
        if analysis.get("p_value", 1.0) < 0.05:
            c.strengths.append("Statistically significant result")
        # Overall quality
        c.overall_quality = min(1.0, 0.3 + 0.1 * len(c.strengths)
                                - 0.1 * len(c.weaknesses))
        c.suggestions.append("Consider increasing sample size")
        c.suggestions.append("Replicate in independent lab")
        return c


class Replicator:
    """Attempt to replicate findings."""

    def __init__(self, seed: int = 123):
        self.rng = random.Random(seed)

    def replicate(self, original_effect: float, sample_size: int = 30) -> ReplicationResult:
        """Simulate a replication attempt."""
        # Replication with some noise
        replication_effect = original_effect + self.rng.gauss(0, 0.3)
        success = abs(replication_effect) > 0.2
        return ReplicationResult(
            original_finding=f"effect_size={original_effect:.2f}",
            replicated=success,
            effect_size_original=original_effect,
            effect_size_replication=replication_effect,
            notes="Replication " + ("succeeded" if success else "failed"),
        )


class DiscoveryPipeline:
    """Full scientific discovery pipeline."""

    def __init__(self, seed: int = 42):
        self.lit_search = LiteratureSearch(seed=seed)
        self.hypothesis_gen = HypothesisGenerator(seed=seed)
        self.experiment_designer = ExperimentDesigner()
        self.simulator = Simulator(seed=seed)
        self.analyzer = StatisticalAnalyzer()
        self.critiquer = Critiquer()
        self.replicator = Replicator(seed=seed + 1)
        self._observers: list[Callable] = []

    def add_observer(self, fn: Callable) -> None:
        self._observers.append(fn)

    def _notify(self, event: str, data: Any) -> None:
        for obs in self._observers:
            obs(event, data)

    def run(self, query: str, max_iterations: int = 3,
            papers: Optional[list[Paper]] = None) -> DiscoveryResult:
        """Run the full discovery pipeline."""
        result = DiscoveryResult(query=query)

        # Step 1: Literature search
        if papers:
            self.lit_search.index(papers)
        result.papers = self.lit_search.search(query)
        synthesis = self.lit_search.synthesize(result.papers)
        self._notify("literature", result.papers)

        # Step 2: Hypothesis generation
        result.hypotheses = self.hypothesis_gen.generate(synthesis)
        self._notify("hypotheses", result.hypotheses)

        for iteration in range(max_iterations):
            result.iterations += 1
            for hypothesis in result.hypotheses:
                # Step 3: Experiment design
                experiment = self.experiment_designer.design(hypothesis)
                result.experiments.append(experiment)

                # Step 4: Simulation
                dataset = self.simulator.run_trial(experiment)
                result.datasets.append(dataset)

                # Step 5: Measurement (already in dataset)
                # Step 6: Analysis
                analysis = self.analyzer.t_test(dataset)
                effect = self.analyzer.effect_size(dataset)

                # Step 7: Critique
                critique = self.critiquer.critique(experiment, dataset, analysis)
                result.critiques.append(critique)

                # Update hypothesis confidence
                if analysis.get("significant", False):
                    hypothesis.evidence_for.append(
                        f"Iteration {iteration+1}: significant result (p={analysis['p_value']:.3f})"
                    )
                    hypothesis.confidence = Confidence.MEDIUM
                else:
                    hypothesis.evidence_against.append(
                        f"Iteration {iteration+1}: not significant"
                    )

                self._notify("experiment", {
                    "hypothesis": hypothesis.statement,
                    "analysis": analysis,
                    "critique": critique,
                })

        # Step 8: Replication
        best_h = max(result.hypotheses, key=lambda h: h.confidence.value,
                     default=None)
        if best_h:
            repl_effect = 0.5  # simulated
            repl_result = self.replicator.replicate(repl_effect)
            # Step 9: Conclusion
            supported = (best_h.confidence >= Confidence.MEDIUM
                         and repl_result.replicated)
            result.conclusion = Conclusion(
                hypothesis=best_h.statement,
                supported=supported,
                confidence=best_h.confidence,
                evidence_summary=f"Tested in {len(result.experiments)} experiments",
                limitations=["Simulated data", "Simplified analysis"],
                future_work=["Real-world validation", "Larger samples"],
                replication_results=[repl_result],
            )

        self._notify("complete", result)
        return result


def discover(query: str, papers: Optional[list[Paper]] = None) -> DiscoveryResult:
    """Convenience function."""
    p = DiscoveryPipeline()
    return p.run(query, papers=papers)
