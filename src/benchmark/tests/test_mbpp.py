import pytest
import os
import tempfile
import json

from benchmark.mbpp_benchmark import (
    MBPPProblem, MBPPResult, MBPPLoader, MBPPEvaluator, MBPPBenchmark
)


class TestMBPPProblem:
    def test_create(self):
        p = MBPPProblem(id="p1", description="Add two numbers", code="def add(a,b): return a+b", test_cases=["assert add(1,2)==3"])
        assert p.id == "p1"
        assert p.difficulty == "medium"

    def test_to_dict(self):
        p = MBPPProblem(id="p1", description="Test", code="x=1", test_cases=[])
        d = p.to_dict()
        assert d["id"] == "p1"
        assert d["code"] == "x=1"

    def test_from_dict(self):
        d = {"id": "p2", "description": "T", "code": "y=2", "test_cases": [], "difficulty": "easy", "tags": ["math"]}
        p = MBPPProblem.from_dict(d)
        assert p.id == "p2"
        assert p.difficulty == "easy"


class TestMBPPResult:
    def test_create(self):
        r = MBPPResult(id="r1", problem_id="p1", success=True)
        assert r.accuracy == 0.0

    def test_accuracy(self):
        r = MBPPResult(id="r1", problem_id="p1", success=True,
                       test_results={"t1": True, "t2": True, "t3": False})
        assert r.accuracy == 2 / 3

    def test_accuracy_empty(self):
        r = MBPPResult(id="r1", problem_id="p1", success=False)
        assert r.accuracy == 0.0


def _create_temp_json(data):
    """Create a temp JSON file that can be deleted on Windows."""
    fd, path = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, "w") as f:
        json.dump(data, f)
    return path


class TestMBPPLoader:
    def test_create(self):
        loader = MBPPLoader()
        assert len(loader.problems) == 0

    def test_load_problems(self):
        path = _create_temp_json([
            {"id": "1", "description": "Add", "code": "def add(a,b): return a+b", "test_cases": ["assert add(1,2)==3"]},
            {"id": "2", "description": "Sub", "code": "def sub(a,b): return a-b", "test_cases": ["assert sub(5,3)==2"]},
        ])
        loader = MBPPLoader()
        problems = loader.load_problems(path)
        assert len(problems) == 2
        os.unlink(path)

    def test_load_problems_missing_file(self):
        loader = MBPPLoader()
        assert loader.load_problems("/nonexistent/path.json") == []

    def test_get_problem(self):
        path = _create_temp_json([{"id": "p1", "description": "T", "code": "x=1", "test_cases": []}])
        loader = MBPPLoader()
        loader.load_problems(path)
        assert loader.get_problem("p1") is not None
        assert loader.get_problem("nonexistent") is None
        os.unlink(path)

    def test_get_all(self):
        path = _create_temp_json([
            {"id": "1", "description": "A", "code": "a=1", "test_cases": []},
            {"id": "2", "description": "B", "code": "b=2", "test_cases": []},
        ])
        loader = MBPPLoader()
        loader.load_problems(path)
        assert len(loader.get_all()) == 2
        os.unlink(path)


class TestMBPPEvaluator:
    def test_create(self):
        ev = MBPPEvaluator()
        assert ev is not None

    def test_evaluate_correct(self):
        ev = MBPPEvaluator()
        p = MBPPProblem(id="p1", description="Add", code="def add(a,b): return a+b", test_cases=["assert add(1,2)==3"])
        r = ev.evaluate(p, "def add(a,b): return a+b")
        assert r.success is True

    def test_evaluate_incorrect(self):
        ev = MBPPEvaluator()
        p = MBPPProblem(id="p1", description="Add", code="def add(a,b): return a+b", test_cases=["assert add(1,2)==3"])
        r = ev.evaluate(p, "def add(a,b): return a-b")
        assert r.success is False

    def test_evaluate_runtime_error(self):
        ev = MBPPEvaluator()
        p = MBPPProblem(id="p1", description="Div", code="def div(a,b): return a/b", test_cases=["assert div(1,0)==0"])
        r = ev.evaluate(p, "def div(a,b): return a/b")
        assert r.success is False
        assert r.error is not None

    def test_evaluate_no_tests(self):
        ev = MBPPEvaluator()
        p = MBPPProblem(id="p1", description="T", code="x=1", test_cases=[])
        r = ev.evaluate(p, "x=1")
        assert r.success is True
        assert len(r.test_results) == 0


class TestMBPPBenchmark:
    def test_create(self):
        b = MBPPBenchmark()
        assert len(b.results) == 0

    def test_load_problems(self):
        path = _create_temp_json([{"id": "1", "description": "T", "code": "x=1", "test_cases": []}])
        b = MBPPBenchmark()
        problems = b.load_problems(path)
        assert len(problems) == 1
        os.unlink(path)

    def test_run_problem(self):
        path = _create_temp_json([{"id": "p1", "description": "Add", "code": "def add(a,b): return a+b", "test_cases": ["assert add(1,2)==3"]}])
        b = MBPPBenchmark()
        b.load_problems(path)
        r = b.run_problem("p1", "def add(a,b): return a+b")
        assert r.success is True
        os.unlink(path)

    def test_run_problem_not_found(self):
        b = MBPPBenchmark()
        r = b.run_problem("nonexistent", "x=1")
        assert r.success is False
        assert r.error == "Problem not found"

    def test_run_sample(self):
        path = _create_temp_json([
            {"id": "1", "description": "A", "code": "def f(): return 1", "test_cases": ["assert f()==1"]},
            {"id": "2", "description": "B", "code": "def g(): return 2", "test_cases": ["assert g()==2"]},
        ])
        b = MBPPBenchmark()
        b.load_problems(path)
        results = b.run_sample(2)
        assert len(results) == 2
        os.unlink(path)

    def test_run_sample_n_larger(self):
        path = _create_temp_json([{"id": "1", "description": "A", "code": "x=1", "test_cases": []}])
        b = MBPPBenchmark()
        b.load_problems(path)
        results = b.run_sample(10)
        assert len(results) == 1
        os.unlink(path)

    def test_get_accuracy(self):
        path = _create_temp_json([
            {"id": "1", "description": "A", "code": "def f(): return 1", "test_cases": ["assert f()==1"]},
            {"id": "2", "description": "B", "code": "def g(): return 2", "test_cases": ["assert g()==2"]},
        ])
        b = MBPPBenchmark()
        b.load_problems(path)
        b.run_problem("1", "def f(): return 1")
        b.run_problem("2", "def g(): return 999")  # wrong
        acc = b.get_accuracy()
        assert acc["overall"] == 0.5
        assert acc["total"] == 2
        os.unlink(path)

    def test_get_accuracy_empty(self):
        b = MBPPBenchmark()
        acc = b.get_accuracy()
        assert acc["overall"] == 0.0
        assert acc["total"] == 0

    def test_get_results_filter(self):
        path = _create_temp_json([
            {"id": "1", "description": "A", "code": "def f(): return 1", "test_cases": ["assert f()==1"]},
            {"id": "2", "description": "B", "code": "def g(): return 2", "test_cases": ["assert g()==2"]},
        ])
        b = MBPPBenchmark()
        b.load_problems(path)
        b.run_problem("1", "def f(): return 1")
        b.run_problem("2", "def g(): return 999")
        assert len(b.get_results(success=True)) == 1
        assert len(b.get_results(success=False)) == 1
        os.unlink(path)
