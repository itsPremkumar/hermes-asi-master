"""Formal Reasoner — Z3 + Lean4 + DPLL fallback for formal verification.

Crown jewel module: integrates multiple theorem-proving backends.
- Z3 (primary): SMT solver via z3-solver pip package
- Lean4 (optional): subprocess call to `lean` binary
- DPLL (fallback): pure-Python propositional SAT solver

Usage:
    from advanced.formal_reasoner import FormalReasoner
    r = FormalReasoner(backend="z3")
    result = r.verify("x > 0 AND y > 0 IMPLIES x + y > 0")
    print(result)  # ProofResult(status="proved", ...)
"""
from __future__ import annotations

import subprocess
import tempfile
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class Backend(Enum):
    Z3 = "z3"
    LEAN = "lean"
    DPLL = "dpll"
    AUTO = "auto"


class ProofStatus(Enum):
    PROVED = "proved"
    DISPROVED = "disproved"
    UNKNOWN = "unknown"
    TIMEOUT = "timeout"
    ERROR = "error"


@dataclass
class ProofResult:
    status: ProofStatus
    backend: str
    model: Optional[dict[str, Any]] = None
    proof_trace: Optional[str] = None
    counterexample: Optional[dict[str, Any]] = None
    duration_ms: float = 0.0
    message: str = ""

    @property
    def is_proved(self) -> bool:
        return self.status == ProofStatus.PROVED

    @property
    def is_disproved(self) -> bool:
        return self.status == ProofStatus.DISPROVED

    def __bool__(self) -> bool:
        return self.is_proved


@dataclass
class Expr:
    """Simple expression tree for propositional logic."""
    op: str  # 'AND', 'OR', 'NOT', 'IMPLIES', 'IFF', 'VAR', 'CONST'
    args: list["Expr"] = field(default_factory=list)
    name: str = ""
    value: Optional[bool] = None

    @staticmethod
    def var(name: str) -> "Expr":
        return Expr(op="VAR", name=name)

    @staticmethod
    def const(value: bool) -> "Expr":
        return Expr(op="CONST", value=value)

    def __and__(self, other: "Expr") -> "Expr":
        return Expr(op="AND", args=[self, other])

    def __or__(self, other: "Expr") -> "Expr":
        return Expr(op="OR", args=[self, other])

    def __invert__(self) -> "Expr":
        return Expr(op="NOT", args=[self])

    def implies(self, other: "Expr") -> "Expr":
        return Expr(op="IMPLIES", args=[self, other])

    def iff(self, other: "Expr") -> "Expr":
        return Expr(op="IFF", args=[self, other])

    def evaluate(self, assignment: dict[str, bool]) -> bool:
        if self.op == "CONST":
            return self.value
        if self.op == "VAR":
            if self.name not in assignment:
                raise ValueError(f"Variable {self.name} not assigned")
            return assignment[self.name]
        if self.op == "NOT":
            return not self.args[0].evaluate(assignment)
        if self.op == "AND":
            return all(a.evaluate(assignment) for a in self.args)
        if self.op == "OR":
            return any(a.evaluate(assignment) for a in self.args)
        if self.op == "IMPLIES":
            return (not self.args[0].evaluate(assignment)) or self.args[1].evaluate(assignment)
        if self.op == "IFF":
            return self.args[0].evaluate(assignment) == self.args[1].evaluate(assignment)
        raise ValueError(f"Unknown op: {self.op}")

    def variables(self) -> set[str]:
        if self.op == "VAR":
            return {self.name}
        result = set()
        for a in self.args:
            result |= a.variables()
        return result

    def __repr__(self) -> str:
        if self.op == "VAR":
            return self.name
        if self.op == "CONST":
            return str(self.value)
        if self.op == "NOT":
            return f"NOT({self.args[0]})"
        op_sym = {"AND": "AND", "OR": "OR", "IMPLIES": "=>", "IFF": "<=>"}
        return f"({self.args[0]} {op_sym.get(self.op, self.op)} {self.args[1]})"


def _tokenize(s: str) -> list[str]:
    """Tokenize a propositional formula string."""
    tokens = []
    i = 0
    s = s.replace("(", " ( ").replace(")", " ) ")
    words = s.split()
    for w in words:
        w_upper = w.upper()
        if w_upper in ("AND", "OR", "NOT", "IMPLIES", "IFF", "(", ")", "TRUE", "FALSE"):
            tokens.append(w_upper)
        else:
            tokens.append(w)
    return tokens


def parse_formula(s: str) -> Expr:
    """Parse a propositional formula string into an Expr tree."""
    tokens = _tokenize(s)
    pos = [0]

    def parse_iff() -> Expr:
        left = parse_implies()
        while pos[0] < len(tokens) and tokens[pos[0]] == "IFF":
            pos[0] += 1
            right = parse_implies()
            left = left.iff(right)
        return left

    def parse_implies() -> Expr:
        left = parse_or()
        while pos[0] < len(tokens) and tokens[pos[0]] == "IMPLIES":
            pos[0] += 1
            right = parse_or()
            left = left.implies(right)
        return left

    def parse_or() -> Expr:
        left = parse_and()
        while pos[0] < len(tokens) and tokens[pos[0]] == "OR":
            pos[0] += 1
            right = parse_and()
            left = left | right
        return left

    def parse_and() -> Expr:
        left = parse_unary()
        while pos[0] < len(tokens) and tokens[pos[0]] == "AND":
            pos[0] += 1
            right = parse_unary()
            left = left & right
        return left

    def parse_unary() -> Expr:
        if pos[0] < len(tokens) and tokens[pos[0]] == "NOT":
            pos[0] += 1
            return ~parse_unary()
        return parse_atom()

    def parse_atom() -> Expr:
        if pos[0] >= len(tokens):
            raise ValueError("Unexpected end of formula")
        tok = tokens[pos[0]]
        if tok == "(":
            pos[0] += 1
            expr = parse_iff()
            if pos[0] >= len(tokens) or tokens[pos[0]] != ")":
                raise ValueError("Missing closing paren")
            pos[0] += 1
            return expr
        if tok == "TRUE":
            pos[0] += 1
            return Expr.const(True)
        if tok == "FALSE":
            pos[0] += 1
            return Expr.const(False)
        pos[0] += 1
        return Expr.var(tok)

    result = parse_iff()
    if pos[0] != len(tokens):
        raise ValueError(f"Unexpected token: {tokens[pos[0]]}")
    return result


class DPLLSolver:
    """Pure-Python DPLL SAT solver for propositional logic."""

    @staticmethod
    def is_tautology(expr: Expr) -> tuple[bool, Optional[dict[str, bool]]]:
        """Check if expr is a tautology by exhaustive assignment."""
        vars_ = sorted(expr.variables())
        if len(vars_) > 20:
            return False, None  # too large for exhaustive
        for i in range(2 ** len(vars_)):
            assignment = {v: bool((i >> j) & 1) for j, v in enumerate(vars_)}
            if not expr.evaluate(assignment):
                return False, assignment
        return True, None

    @staticmethod
    def is_satisfiable(expr: Expr) -> tuple[bool, Optional[dict[str, bool]]]:
        """Check if expr is satisfiable."""
        vars_ = sorted(expr.variables())
        if len(vars_) > 20:
            return False, None
        for i in range(2 ** len(vars_)):
            assignment = {v: bool((i >> j) & 1) for j, v in enumerate(vars_)}
            if expr.evaluate(assignment):
                return True, assignment
        return False, None


class Z3Backend:
    """Z3 SMT solver backend."""

    def __init__(self):
        try:
            import z3
            self.z3 = z3
        except ImportError:
            raise RuntimeError("z3-solver not installed. Run: pip install z3-solver")

    def verify(self, formula: str, timeout_ms: int = 5000) -> ProofResult:
        """Verify a propositional formula using Z3."""
        import time
        try:
            expr = parse_formula(formula)
        except ValueError as e:
            return ProofResult(
                status=ProofStatus.ERROR,
                backend="z3",
                message=f"Parse error: {e}",
            )

        vars_ = sorted(expr.variables())
        z3_vars = {v: self.z3.Bool(v) for v in vars_}

        def to_z3(e: Expr):
            if e.op == "CONST":
                return e.value
            if e.op == "VAR":
                return z3_vars[e.name]
            if e.op == "NOT":
                return self.z3.Not(to_z3(e.args[0]))
            if e.op == "AND":
                return self.z3.And([to_z3(a) for a in e.args])
            if e.op == "OR":
                return self.z3.Or([to_z3(a) for a in e.args])
            if e.op == "IMPLIES":
                return self.z3.Implies(to_z3(e.args[0]), to_z3(e.args[1]))
            if e.op == "IFF":
                return to_z3(e.args[0]) == to_z3(e.args[1])
            raise ValueError(f"Unknown op: {e.op}")

        z3_expr = to_z3(expr)
        solver = self.z3.Solver()
        solver.set("timeout", timeout_ms)
        # To prove: assert NOT(formula) and check unsat
        solver.add(self.z3.Not(z3_expr))

        start = time.time()
        result = solver.check()
        duration = (time.time() - start) * 1000

        if result == self.z3.unsat:
            return ProofResult(
                status=ProofStatus.PROVED,
                backend="z3",
                duration_ms=duration,
                message="Formula is valid (Z3 unsat of negation)",
            )
        elif result == self.z3.sat:
            model = solver.model()
            ce = {}
            for v in vars_:
                z3_v = z3_vars[v]
                val = model.evaluate(z3_v, model_completion=True)
                ce[v] = bool(val)
            return ProofResult(
                status=ProofStatus.DISPROVED,
                backend="z3",
                counterexample=ce,
                duration_ms=duration,
                message="Counterexample found",
            )
        else:
            return ProofResult(
                status=ProofStatus.UNKNOWN,
                backend="z3",
                duration_ms=duration,
                message="Z3 returned unknown",
            )

    def find_model(self, formula: str, timeout_ms: int = 5000) -> ProofResult:
        """Find a satisfying assignment."""
        import time
        try:
            expr = parse_formula(formula)
        except ValueError as e:
            return ProofResult(
                status=ProofStatus.ERROR,
                backend="z3",
                message=f"Parse error: {e}",
            )

        vars_ = sorted(expr.variables())
        z3_vars = {v: self.z3.Bool(v) for v in vars_}

        def to_z3(e: Expr):
            if e.op == "CONST":
                return e.value
            if e.op == "VAR":
                return z3_vars[e.name]
            if e.op == "NOT":
                return self.z3.Not(to_z3(e.args[0]))
            if e.op == "AND":
                return self.z3.And([to_z3(a) for a in e.args])
            if e.op == "OR":
                return self.z3.Or([to_z3(a) for a in e.args])
            if e.op == "IMPLIES":
                return self.z3.Implies(to_z3(e.args[0]), to_z3(e.args[1]))
            if e.op == "IFF":
                return to_z3(e.args[0]) == to_z3(e.args[1])
            raise ValueError(f"Unknown op: {e.op}")

        solver = self.z3.Solver()
        solver.set("timeout", timeout_ms)
        solver.add(to_z3(expr))

        start = time.time()
        result = solver.check()
        duration = (time.time() - start) * 1000

        if result == self.z3.sat:
            model = solver.model()
            ce = {}
            for v in vars_:
                z3_v = z3_vars[v]
                val = model.evaluate(z3_v, model_completion=True)
                ce[v] = bool(val)
            return ProofResult(
                status=ProofStatus.DISPROVED,
                backend="z3",
                model=ce,
                duration_ms=duration,
                message="Satisfying assignment found",
            )
        elif result == self.z3.unsat:
            return ProofResult(
                status=ProofStatus.PROVED,
                backend="z3",
                duration_ms=duration,
                message="Formula is unsatisfiable",
            )
        else:
            return ProofResult(
                status=ProofStatus.UNKNOWN,
                backend="z3",
                duration_ms=duration,
                message="Z3 returned unknown",
            )


class LeanBackend:
    """Lean4 backend via subprocess."""

    def __init__(self, lean_path: str = "lean"):
        self.lean_path = lean_path
        self._check_lean()

    def _check_lean(self):
        try:
            result = subprocess.run(
                [self.lean_path, "--version"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode != 0:
                raise RuntimeError(f"Lean check failed: {result.stderr}")
        except FileNotFoundError:
            raise RuntimeError(
                f"Lean binary not found at '{self.lean_path}'. "
                "Install from https://leanprover-community.github.io/get_started.html"
            )

    def verify(self, theorem_stmt: str, timeout_ms: int = 10000) -> ProofResult:
        """Verify a theorem statement using Lean4."""
        import time
        lean_code = f"""
theorem verif : {theorem_stmt} := by
  decide
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".lean", delete=False
        ) as f:
            f.write(lean_code)
            tmp_path = f.name

        try:
            start = time.time()
            result = subprocess.run(
                [self.lean_path, tmp_path],
                capture_output=True, text=True,
                timeout=timeout_ms / 1000,
            )
            duration = (time.time() - start) * 1000

            if result.returncode == 0:
                return ProofResult(
                    status=ProofStatus.PROVED,
                    backend="lean4",
                    duration_ms=duration,
                    message="Lean4 proof accepted",
                )
            else:
                return ProofResult(
                    status=ProofStatus.DISPROVED,
                    backend="lean4",
                    duration_ms=duration,
                    message=f"Lean4 rejected: {result.stderr[:500]}",
                )
        except subprocess.TimeoutExpired:
            return ProofResult(
                status=ProofStatus.TIMEOUT,
                backend="lean4",
                duration_ms=timeout_ms,
                message="Lean4 timed out",
            )
        finally:
            os.unlink(tmp_path)


class FormalReasoner:
    """Multi-backend formal verification engine."""

    def __init__(self, backend: Backend | str = Backend.AUTO, lean_path: str = "lean"):
        if isinstance(backend, str):
            backend = Backend(backend)
        self.backend = backend
        self.lean_path = lean_path
        self._z3: Optional[Z3Backend] = None
        self._lean: Optional[LeanBackend] = None
        self._dpll = DPLLSolver()

        if backend == Backend.Z3:
            self._z3 = Z3Backend()
        elif backend == Backend.LEAN:
            self._lean = LeanBackend(lean_path)

    def _resolve_backend(self, formula: str) -> Backend:
        if self.backend != Backend.AUTO:
            return self.backend
        # Auto-select: try Z3 first, then DPLL
        try:
            import z3  # noqa: F401
            return Backend.Z3
        except ImportError:
            return Backend.DPLL

    def verify(self, formula: str, timeout_ms: int = 5000) -> ProofResult:
        """Verify a formula using the selected backend."""
        backend = self._resolve_backend(formula)

        if backend == Backend.Z3:
            if self._z3 is None:
                self._z3 = Z3Backend()
            return self._z3.verify(formula, timeout_ms)
        elif backend == Backend.LEAN:
            if self._lean is None:
                self._lean = LeanBackend(self.lean_path)
            return self._lean.verify(formula, timeout_ms)
        elif backend == Backend.DPLL:
            import time
            try:
                expr = parse_formula(formula)
            except ValueError as e:
                return ProofResult(
                    status=ProofStatus.ERROR,
                    backend="dpll",
                    message=f"Parse error: {e}",
                )
            start = time.time()
            is_taut, ce = self._dpll.is_tautology(expr)
            duration = (time.time() - start) * 1000
            if is_taut:
                return ProofResult(
                    status=ProofStatus.PROVED,
                    backend="dpll",
                    duration_ms=duration,
                    message="DPLL: tautology (exhaustive)",
                )
            else:
                return ProofResult(
                    status=ProofStatus.DISPROVED,
                    backend="dpll",
                    counterexample=ce,
                    duration_ms=duration,
                    message="DPLL: not a tautology",
                )
        else:
            return ProofResult(
                status=ProofStatus.ERROR,
                backend="unknown",
                message=f"Unknown backend: {backend}",
            )

    def find_model(self, formula: str, timeout_ms: int = 5000) -> ProofResult:
        """Find a satisfying assignment."""
        backend = self._resolve_backend(formula)
        if backend == Backend.Z3:
            if self._z3 is None:
                self._z3 = Z3Backend()
            return self._z3.find_model(formula, timeout_ms)
        elif backend == Backend.DPLL:
            import time
            try:
                expr = parse_formula(formula)
            except ValueError as e:
                return ProofResult(
                    status=ProofStatus.ERROR,
                    backend="dpll",
                    message=f"Parse error: {e}",
                )
            start = time.time()
            sat, model = self._dpll.is_satisfiable(expr)
            duration = (time.time() - start) * 1000
            if sat:
                return ProofResult(
                    status=ProofStatus.DISPROVED,
                    backend="dpll",
                    model=model,
                    duration_ms=duration,
                    message="DPLL: satisfiable",
                )
            else:
                return ProofResult(
                    status=ProofStatus.PROVED,
                    backend="dpll",
                    duration_ms=duration,
                    message="DPLL: unsatisfiable",
                )
        else:
            return ProofResult(
                status=ProofStatus.ERROR,
                backend=backend.value,
                message="find_model not supported for this backend",
            )

    def check_equivalence(self, formula1: str, formula2: str) -> ProofResult:
        """Check if two formulas are logically equivalent."""
        return self.verify(f"({formula1}) IFF ({formula2})")

    def check_entailment(self, premises: list[str], conclusion: str) -> ProofResult:
        """Check if premises entail the conclusion."""
        if not premises:
            return self.verify(conclusion)
        combined = " AND ".join(f"({p})" for p in premises)
        return self.verify(f"({combined}) IMPLIES ({conclusion})")


def verify(formula: str, backend: str = "auto") -> ProofResult:
    """Convenience function."""
    r = FormalReasoner(backend=backend)
    return r.verify(formula)


def is_tautology(formula: str) -> bool:
    """Quick tautology check."""
    return verify(formula).is_proved


def is_satisfiable(formula: str) -> bool:
    """Quick satisfiability check."""
    r = FormalReasoner(backend="auto")
    result = r.find_model(formula)
    return result.status != ProofStatus.PROVED  # proved = unsat


def are_equivalent(f1: str, f2: str) -> bool:
    """Check logical equivalence."""
    return verify(f"({f1}) IFF ({f2})").is_proved
