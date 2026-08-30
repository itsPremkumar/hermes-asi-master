"""
Tests for DAG Engine.
Test count: 14
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from v9.horizon.dag_engine import (
    DAG, DAGEngine, Task, TaskStatus, TaskResult
)


def async_run(coro):
    """Helper to run async functions in tests."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


class TestDAG:
    def test_create_empty_dag(self):
        dag = DAG()
        assert len(dag.tasks) == 0

    def test_add_task(self):
        dag = DAG()
        task = Task(id="t1", name="test", func=lambda: asyncio.sleep(0))
        dag.add_task(task)
        assert "t1" in dag.tasks

    def test_add_duplicate_task_raises(self):
        dag = DAG()
        task = Task(id="t1", name="test", func=lambda: asyncio.sleep(0))
        dag.add_task(task)
        with pytest.raises(ValueError):
            dag.add_task(task)

    def test_add_task_with_dependencies(self):
        dag = DAG()
        t1 = Task(id="t1", name="first", func=lambda: asyncio.sleep(0))
        t2 = Task(id="t2", name="second", func=lambda: asyncio.sleep(0), dependencies=["t1"])
        dag.add_task(t1)
        dag.add_task(t2)
        assert dag.get_dependencies("t2") == ["t1"]
        assert dag.get_dependents("t1") == ["t2"]

    def test_topological_sort(self):
        dag = DAG()
        t1 = Task(id="t1", name="a", func=lambda: asyncio.sleep(0))
        t2 = Task(id="t2", name="b", func=lambda: asyncio.sleep(0), dependencies=["t1"])
        t3 = Task(id="t3", name="c", func=lambda: asyncio.sleep(0), dependencies=["t1"])
        dag.add_task(t1)
        dag.add_task(t2)
        dag.add_task(t3)
        order = dag.topological_sort()
        assert order[0] == "t1"
        assert set(order[1:]) == {"t2", "t3"}

    def test_cycle_detection(self):
        dag = DAG()
        t1 = Task(id="t1", name="a", func=lambda: asyncio.sleep(0), dependencies=["t2"])
        t2 = Task(id="t2", name="b", func=lambda: asyncio.sleep(0), dependencies=["t1"])
        dag.add_task(t1)
        with pytest.raises(ValueError):
            dag.add_task(t2)

    def test_remove_task(self):
        dag = DAG()
        t1 = Task(id="t1", name="a", func=lambda: asyncio.sleep(0))
        dag.add_task(t1)
        removed = dag.remove_task("t1")
        assert removed is not None
        assert len(dag.tasks) == 0

    def test_get_ready_tasks(self):
        dag = DAG()
        t1 = Task(id="t1", name="a", func=lambda: asyncio.sleep(0))
        t2 = Task(id="t2", name="b", func=lambda: asyncio.sleep(0), dependencies=["t1"])
        dag.add_task(t1)
        dag.add_task(t2)
        ready = dag.get_ready_tasks(set())
        assert len(ready) == 1
        assert ready[0].id == "t1"


class TestDAGEngine:
    def test_create_engine(self):
        engine = DAGEngine(max_parallel=2)
        assert engine.max_parallel == 2

    async def _simple_task(self, x, y):
        return x + y

    def test_execute_single_task(self):
        async def run():
            engine = DAGEngine()
            task = Task(id="t1", name="add", func=self._simple_task, args=(2, 3))
            engine.add_task(task)
            results = await engine.execute()
            assert "t1" in results
            assert results["t1"].status == TaskStatus.COMPLETED
            assert results["t1"].output == 5
        async_run(run())

    def test_execute_parallel_tasks(self):
        async def task_a():
            await asyncio.sleep(0.01)
            return "a"

        async def task_b():
            await asyncio.sleep(0.01)
            return "b"

        async def run():
            engine = DAGEngine(max_parallel=4)
            engine.add_task(Task(id="a", name="a", func=task_a))
            engine.add_task(Task(id="b", name="b", func=task_b))
            results = await engine.execute()
            assert results["a"].status == TaskStatus.COMPLETED
            assert results["b"].status == TaskStatus.COMPLETED
        async_run(run())

    def test_execute_with_dependencies(self):
        async def task_a():
            return 10

        async def task_b(context=None):
            return 20

        async def run():
            engine = DAGEngine()
            engine.add_task(Task(id="a", name="a", func=task_a))
            engine.add_task(Task(id="b", name="b", func=task_b, dependencies=["a"]))
            results = await engine.execute()
            assert results["a"].status == TaskStatus.COMPLETED
            assert results["b"].status == TaskStatus.COMPLETED
        async_run(run())

    def test_task_failure_with_retry(self):
        call_count = 0

        async def flaky_task():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Flaky!")
            return "success"

        async def run():
            engine = DAGEngine()
            engine.add_task(Task(id="t1", name="flaky", func=flaky_task, max_retries=3))
            results = await engine.execute()
            assert results["t1"].status == TaskStatus.COMPLETED
            assert results["t1"].output == "success"
        async_run(run())

    def test_task_failure_exhausts_retries(self):
        async def always_fail():
            raise RuntimeError("Always fails")

        async def run():
            engine = DAGEngine()
            engine.add_task(Task(id="t1", name="fail", func=always_fail, max_retries=2))
            results = await engine.execute()
            assert results["t1"].status == TaskStatus.FAILED
            assert results["t1"].attempts == 3
        async_run(run())

    def test_skip_on_dependency_failure(self):
        async def fail_task():
            raise RuntimeError("Fail")

        async def dependent_task():
            return "should not run"

        async def run():
            engine = DAGEngine()
            engine.add_task(Task(id="a", name="fail", func=fail_task, max_retries=0))
            engine.add_task(Task(id="b", name="dep", func=dependent_task, dependencies=["a"]))
            results = await engine.execute()
            assert results["a"].status == TaskStatus.FAILED
            assert results["b"].status == TaskStatus.SKIPPED
        async_run(run())

    def test_task_result_duration(self):
        result = TaskResult(task_id="t1", status=TaskStatus.COMPLETED)
        result.started_at = 100.0
        result.completed_at = 105.5
        assert result.duration == 5.5

    def test_task_result_to_dict(self):
        result = TaskResult(task_id="t1", status=TaskStatus.COMPLETED, output=42)
        d = result.to_dict()
        assert d["task_id"] == "t1"
        assert d["status"] == "completed"
        assert d["output"] == 42
