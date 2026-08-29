"""Tests for the ExperienceReplay module."""

import pytest
from phase7.experience_replay import ExperienceReplay, ReplayBuffer, Experience


class TestExperience:
    """Tests for the Experience dataclass."""

    def test_experience_fields(self):
        exp = Experience(
            state="initial state",
            action="take action",
            result="action result",
            reward=0.8,
        )
        assert exp.state == "initial state"
        assert exp.action == "take action"
        assert exp.result == "action result"
        assert exp.reward == 0.8
        assert exp.done is False

    def test_experience_id(self):
        exp = Experience(
            state="s",
            action="a",
            result="r",
            reward=0.5,
        )
        assert exp.id is not None
        assert len(exp.id) == 12

    def test_experience_to_dict(self):
        exp = Experience(
            state="s",
            action="a",
            result="r",
            reward=0.5,
        )
        d = exp.to_dict()
        assert d["state"] == "s"
        assert d["reward"] == 0.5

    def test_experience_from_dict(self):
        data = {
            "state": "s",
            "action": "a",
            "result": "r",
            "reward": 0.7,
            "next_state": "ns",
            "done": True,
            "timestamp": 1234567890.0,
            "metadata": {"key": "value"},
        }
        exp = Experience.from_dict(data)
        assert exp.state == "s"
        assert exp.reward == 0.7
        assert exp.done is True


class TestReplayBuffer:
    """Tests for the ReplayBuffer class."""

    def test_add_experience(self):
        buffer = ReplayBuffer(capacity=10)
        exp = Experience(state="s", action="a", result="r", reward=0.5)
        buffer.add(exp)
        assert len(buffer) == 1

    def test_sample_experience(self):
        buffer = ReplayBuffer(capacity=10)
        for i in range(5):
            buffer.add(Experience(state=f"s{i}", action=f"a{i}", result=f"r{i}", reward=0.1 * i))
        batch = buffer.sample(3)
        assert len(batch) == 3

    def test_sample_more_than_available(self):
        buffer = ReplayBuffer(capacity=10)
        buffer.add(Experience(state="s", action="a", result="r", reward=0.5))
        batch = buffer.sample(5)
        assert len(batch) == 1

    def test_buffer_capacity(self):
        buffer = ReplayBuffer(capacity=3)
        for i in range(5):
            buffer.add(Experience(state=f"s{i}", action=f"a{i}", result=f"r{i}", reward=0.1 * i))
        assert len(buffer) == 3

    def test_get_positive_experiences(self):
        buffer = ReplayBuffer(capacity=10)
        buffer.add(Experience(state="s", action="a", result="r", reward=0.8))
        buffer.add(Experience(state="s", action="a", result="r", reward=0.3))
        buffer.add(Experience(state="s", action="a", result="r", reward=-0.5))
        positive = buffer.get_positive_experiences(threshold=0.5)
        assert len(positive) == 1

    def test_get_negative_experiences(self):
        buffer = ReplayBuffer(capacity=10)
        buffer.add(Experience(state="s", action="a", result="r", reward=0.8))
        buffer.add(Experience(state="s", action="a", result="r", reward=-0.3))
        buffer.add(Experience(state="s", action="a", result="r", reward=-0.7))
        negative = buffer.get_negative_experiences(threshold=-0.5)
        assert len(negative) == 2

    def test_contains_experience(self):
        buffer = ReplayBuffer(capacity=10)
        exp = Experience(state="s", action="a", result="r", reward=0.5)
        buffer.add(exp)
        assert exp in buffer


class TestExperienceReplay:
    """Tests for the ExperienceReplay class."""

    def test_store_experience(self):
        replay = ExperienceReplay()
        exp = Experience(state="s", action="a", result="r", reward=0.5)
        replay.store(exp)
        assert len(replay.buffer) == 1

    def test_store_episode(self):
        replay = ExperienceReplay()
        experiences = [
            Experience(state=f"s{i}", action=f"a{i}", result=f"r{i}", reward=0.1 * i)
            for i in range(3)
        ]
        replay.store_episode(experiences)
        assert len(replay.buffer) == 3
        assert replay.episode_count == 1

    def test_sample_batch(self):
        replay = ExperienceReplay()
        for i in range(10):
            replay.store(Experience(state=f"s{i}", action=f"a{i}", result=f"r{i}", reward=0.1 * i))
        batch = replay.sample(5)
        assert len(batch) == 5

    def test_learn_from_batch(self):
        replay = ExperienceReplay()
        for i in range(10):
            replay.store(Experience(state=f"s{i}", action=f"a{i}", result=f"r{i}", reward=0.1 * i))
        batch = replay.sample(5)
        metrics = replay.learn_from_batch(batch)
        assert "avg_reward" in metrics
        assert "success_rate" in metrics
        assert metrics["batch_size"] == 5

    def test_get_best_experiences(self):
        replay = ExperienceReplay()
        for i in range(10):
            replay.store(Experience(state=f"s{i}", action=f"a{i}", result=f"r{i}", reward=0.1 * i))
        best = replay.get_best_experiences(n=3)
        assert len(best) == 3
        # Best should have highest rewards
        assert best[0].reward >= best[1].reward

    def test_get_worst_experiences(self):
        replay = ExperienceReplay()
        for i in range(10):
            replay.store(Experience(state=f"s{i}", action=f"a{i}", result=f"r{i}", reward=0.1 * i))
        worst = replay.get_worst_experiences(n=3)
        assert len(worst) == 3
        # Worst should have lowest rewards
        assert worst[0].reward <= worst[1].reward

    def test_get_statistics(self):
        replay = ExperienceReplay()
        for i in range(10):
            replay.store(Experience(state=f"s{i}", action=f"a{i}", result=f"r{i}", reward=0.1 * i))
        stats = replay.get_statistics()
        assert stats["total_experiences"] == 10
        assert "avg_reward" in stats
        assert "success_rate" in stats

    def test_clear(self):
        replay = ExperienceReplay()
        replay.store(Experience(state="s", action="a", result="r", reward=0.5))
        replay.clear()
        assert len(replay.buffer) == 0
        assert replay.episode_count == 0
        assert replay.total_reward == 0.0

    def test_total_reward_tracking(self):
        replay = ExperienceReplay()
        replay.store(Experience(state="s", action="a", result="r", reward=0.5))
        replay.store(Experience(state="s", action="a", result="r", reward=0.3))
        assert replay.total_reward == 0.8
