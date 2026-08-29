"""Computer Use — GUI planner -> visual perception -> action -> observe -> verify loop.

Implements an agentic computer-use loop where an AI agent can:
  1. Plan a sequence of GUI actions to accomplish a goal
  2. Perceive the screen (screenshot + element detection)
  3. Execute actions (click, type, scroll, etc.)
  4. Observe the result
  5. Verify progress toward the goal

Usage:
    from advanced.computer_use import GUIAgent, Screen, Action
    agent = GUIAgent()
    result = agent.execute("Open settings and enable dark mode")
    print(result.success, result.steps_taken)
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional
from uuid import uuid4


class ActionType(Enum):
    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    RIGHT_CLICK = "right_click"
    TYPE = "type"
    KEYPRESS = "keypress"
    SCROLL = "scroll"
    DRAG = "drag"
    HOVER = "hover"
    WAIT = "wait"
    SCREENSHOT = "screenshot"
    FOCUS = "focus"
    CLOSE = "close"


class ElementType(Enum):
    BUTTON = "button"
    TEXT_FIELD = "text_field"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    DROPDOWN = "dropdown"
    LINK = "link"
    ICON = "icon"
    MENU = "menu"
    WINDOW = "window"
    DIALOG = "dialog"
    LABEL = "label"
    IMAGE = "image"
    UNKNOWN = "unknown"


class GoalStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_INFO = "needs_info"


@dataclass
class UIElement:
    """A detected UI element on screen."""
    element_id: str
    element_type: ElementType
    label: str
    bbox: tuple[int, int, int, int]  # x, y, w, h
    confidence: float = 1.0
    clickable: bool = False
    text: str = ""
    enabled: bool = True
    visible: bool = True
    attributes: dict[str, Any] = field(default_factory=dict)

    @property
    def center(self) -> tuple[int, int]:
        x, y, w, h = self.bbox
        return (x + w // 2, y + h // 2)

    @property
    def area(self) -> int:
        return self.bbox[2] * self.bbox[3]

    def contains_point(self, px: int, py: int) -> bool:
        x, y, w, h = self.bbox
        return x <= px <= x + w and y <= py <= y + h

    def to_dict(self) -> dict[str, Any]:
        return {
            "element_id": self.element_id,
            "element_type": self.element_type.value,
            "label": self.label,
            "bbox": self.bbox,
            "confidence": self.confidence,
            "clickable": self.clickable,
            "text": self.text,
            "enabled": self.enabled,
            "visible": self.visible,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "UIElement":
        return cls(
            element_id=d["element_id"],
            element_type=ElementType(d.get("element_type", "unknown")),
            label=d.get("label", ""),
            bbox=tuple(d.get("bbox", [0, 0, 0, 0])),
            confidence=d.get("confidence", 1.0),
            clickable=d.get("clickable", False),
            text=d.get("text", ""),
            enabled=d.get("enabled", True),
            visible=d.get("visible", True),
            attributes=d.get("attributes", {}),
        )


@dataclass
class Action:
    """A GUI action to execute."""
    action_type: ActionType
    target: Optional[str] = None  # element_id or text description
    text: str = ""  # for TYPE actions
    key: str = ""  # for KEYPRESS
    dx: int = 0  # for SCROLL/DRAG
    dy: int = 0
    duration_ms: int = 100
    metadata: dict[str, Any] = field(default_factory=dict)
    action_id: str = field(default_factory=lambda: str(uuid4())[:8])

    def __str__(self) -> str:
        if self.action_type == ActionType.CLICK:
            return f"Click({self.target})"
        elif self.action_type == ActionType.TYPE:
            return f"Type('{self.text}' into {self.target})"
        elif self.action_type == ActionType.KEYPRESS:
            return f"KeyPress({self.key})"
        elif self.action_type == ActionType.SCROLL:
            return f"Scroll(dx={self.dx}, dy={self.dy})"
        elif self.action_type == ActionType.WAIT:
            return f"Wait({self.duration_ms}ms)"
        return f"{self.action_type.value}({self.target})"

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_type": self.action_type.value,
            "target": self.target,
            "text": self.text,
            "key": self.key,
            "dx": self.dx,
            "dy": self.dy,
            "duration_ms": self.duration_ms,
            "metadata": self.metadata,
            "action_id": self.action_id,
        }


@dataclass
class Screen:
    """Represents a screen state."""
    elements: list[UIElement] = field(default_factory=list)
    width: int = 1920
    height: int = 1080
    screenshot_path: str = ""
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def find_element(self, label: str) -> Optional[UIElement]:
        """Find element by label (fuzzy)."""
        label_lower = label.lower()
        for el in self.elements:
            if label_lower in el.label.lower() or label_lower in el.text.lower():
                return el
        return None

    def find_by_id(self, element_id: str) -> Optional[UIElement]:
        for el in self.elements:
            if el.element_id == element_id:
                return el
        return None

    def find_clickable(self) -> list[UIElement]:
        return [el for el in self.elements if el.clickable and el.visible]

    def find_by_type(self, element_type: ElementType) -> list[UIElement]:
        return [el for el in self.elements if el.element_type == element_type]

    def find_at(self, x: int, y: int) -> Optional[UIElement]:
        """Topmost element at point."""
        for el in reversed(self.elements):
            if el.contains_point(x, y) and el.visible:
                return el
        return None

    def diff(self, other: "Screen") -> dict[str, Any]:
        """Compare two screen states."""
        self_ids = {e.element_id for e in self.elements}
        other_ids = {e.element_id for e in other.elements}
        return {
            "added": len(self_ids - other_ids),
            "removed": len(other_ids - self_ids),
            "common": len(self_ids & other_ids),
            "screen_changed": self_ids != other_ids,
        }


@dataclass
class Step:
    """One step in the agent's execution."""
    step_number: int
    action: Action
    screen_before: Optional[Screen] = None
    screen_after: Optional[Screen] = None
    observation: str = ""
    success: bool = True
    duration_ms: float = 0.0


@dataclass
class ExecutionResult:
    """Result of executing a goal."""
    goal: str
    status: GoalStatus
    steps: list[Step] = field(default_factory=list)
    final_screen: Optional[Screen] = None
    message: str = ""
    duration_ms: float = 0.0

    @property
    def success(self) -> bool:
        return self.status == GoalStatus.COMPLETED

    @property
    def steps_taken(self) -> int:
        return len(self.steps)

    def summary(self) -> str:
        return (
            f"Goal: {self.goal}\n"
            f"Status: {self.status.value}\n"
            f"Steps: {self.steps_taken}\n"
            f"Duration: {self.duration_ms:.0f}ms\n"
            f"Message: {self.message}"
        )


class VisualPerceiver:
    """Perceive and parse screen content."""

    def __init__(self):
        self._detectors: list[Callable] = []

    def add_detector(self, detector: Callable) -> None:
        self._detectors.append(detector)

    def perceive(self, screen: Screen) -> dict[str, Any]:
        """Analyze a screen and return structured perception."""
        perception = {
            "clickable_elements": screen.find_clickable(),
            "text_fields": screen.find_by_type(ElementType.TEXT_FIELD),
            "buttons": screen.find_by_type(ElementType.BUTTON),
            "labels": screen.find_by_type(ElementType.LABEL),
            "has_dialog": bool(screen.find_by_type(ElementType.DIALOG)),
            "has_window": bool(screen.find_by_type(ElementType.WINDOW)),
            "element_count": len(screen.elements),
        }
        for detector in self._detectors:
            try:
                extra = detector(screen)
                if extra:
                    perception.update(extra)
            except Exception:
                pass
        return perception

    def find_target(self, screen: Screen,
                    description: str) -> Optional[UIElement]:
        """Find an element matching a description."""
        return screen.find_element(description)


class ActionExecutor:
    """Execute actions on the screen."""

    def __init__(self):
        self._action_log: list[dict[str, Any]] = []
        self._pre_hooks: list[Callable] = []
        self._post_hooks: list[Callable] = []

    def add_pre_hook(self, hook: Callable) -> None:
        self._pre_hooks.append(hook)

    def add_post_hook(self, hook: Callable) -> None:
        self._post_hooks.append(hook)

    def execute(self, action: Action, screen: Screen) -> tuple[bool, str]:
        """Execute an action. Returns (success, observation)."""
        for hook in self._pre_hooks:
            hook(action, screen)

        success = True
        observation = f"Executed: {action}"

        # Simulate action execution
        if action.action_type == ActionType.CLICK:
            el = screen.find_element(action.target) if action.target else None
            if el and el.clickable:
                observation = f"Clicked '{el.label}' at {el.center}"
            else:
                success = False
                observation = f"Click target not found: {action.target}"
        elif action.action_type == ActionType.TYPE:
            observation = f"Typed '{action.text}' into {action.target}"
        elif action.action_type == ActionType.KEYPRESS:
            observation = f"Pressed key: {action.key}"
        elif action.action_type == ActionType.SCROLL:
            observation = f"Scrolled by ({action.dx}, {action.dy})"
        elif action.action_type == ActionType.WAIT:
            observation = f"Waited {action.duration_ms}ms"

        self._action_log.append({
            "action": action.to_dict(),
            "success": success,
            "observation": observation,
            "timestamp": time.time(),
        })

        for hook in self._post_hooks:
            hook(action, screen, success)

        return success, observation

    def get_log(self) -> list[dict[str, Any]]:
        return list(self._action_log)


class Planner:
    """Plan a sequence of actions to achieve a goal."""

    def __init__(self):
        self._strategies: dict[str, Callable] = {}

    def register_strategy(self, name: str, strategy: Callable) -> None:
        self._strategies[name] = strategy

    def plan(self, goal: str, screen: Screen,
             perception: dict[str, Any]) -> list[Action]:
        """Generate an action plan."""
        # Simple heuristic planner
        actions: list[Action] = []
        goal_lower = goal.lower()

        # Check for registered strategies
        for name, strategy in self._strategies.items():
            if name in goal_lower:
                return strategy(goal, screen, perception)

        # Default: keyword-based planning
        if "click" in goal_lower or "press" in goal_lower or "select" in goal_lower:
            # Extract target from goal
            words = goal.split()
            for i, w in enumerate(words):
                if w.lower() in ("click", "press", "select", "tap"):
                    if i + 1 < len(words):
                        target = words[i + 1].strip("'.")
                        el = screen.find_element(target)
                        if el:
                            actions.append(Action(
                                action_type=ActionType.CLICK,
                                target=target,
                            ))
                        break

        if "type" in goal_lower or "enter" in goal_lower:
            # Extract text to type
            if "'" in goal:
                parts = goal.split("'")
                if len(parts) >= 2:
                    text = parts[1]
                    target = parts[2].strip() if len(parts) > 2 else "input"
                    actions.append(Action(
                        action_type=ActionType.TYPE,
                        target=target,
                        text=text,
                    ))

        if "scroll" in goal_lower:
            dy = -3 if "up" in goal_lower else 3
            actions.append(Action(
                action_type=ActionType.SCROLL,
                dy=dy,
            ))

        if not actions:
            # Fallback: take a screenshot to understand
            actions.append(Action(action_type=ActionType.SCREENSHOT))

        return actions


class Verifier:
    """Verify progress toward the goal."""

    def __init__(self):
        self._checks: list[Callable] = []

    def add_check(self, check: Callable) -> None:
        self._checks.append(check)

    def verify(self, goal: str, screen: Screen,
               step: Step) -> tuple[bool, str]:
        """Verify if the step made progress."""
        if step.screen_before and step.screen_after:
            diff = step.screen_before.diff(step.screen_after)
            if diff["screen_changed"]:
                return True, f"Screen changed: +{diff['added']}/-{diff['removed']} elements"
            else:
                return False, "No visible change after action"

        for check in self._checks:
            try:
                result = check(goal, screen, step)
                if result is not None:
                    return result
            except Exception:
                pass

        return True, "Step appears valid"

    def is_goal_complete(self, goal: str, screen: Screen) -> tuple[bool, str]:
        """Check if the goal has been achieved."""
        goal_lower = goal.lower()
        # Heuristic: check if expected elements are present
        if "settings" in goal_lower:
            settings = screen.find_element("settings")
            if settings:
                return True, "Settings is visible"
        if "dark mode" in goal_lower:
            toggle = screen.find_element("dark mode")
            if toggle and toggle.attributes.get("enabled"):
                return True, "Dark mode toggle is enabled"
        return False, "Goal not yet achieved"


class GUIAgent:
    """Main computer-use agent."""

    def __init__(self, max_steps: int = 20):
        self.perceiver = VisualPerceiver()
        self.planner = Planner()
        self.executor = ActionExecutor()
        self.verifier = Verifier()
        self.max_steps = max_steps
        self._screen_provider: Optional[Callable] = None
        self._step_observers: list[Callable] = []

    def set_screen_provider(self, provider: Callable) -> None:
        """Set the function that provides current screen state."""
        self._screen_provider = provider

    def add_step_observer(self, observer: Callable) -> None:
        self._step_observers.append(observer)

    def _get_screen(self) -> Screen:
        if self._screen_provider:
            return self._screen_provider()
        return Screen()  # empty screen

    def execute(self, goal: str) -> ExecutionResult:
        """Execute a goal using the perceive-act-verify loop."""
        start_time = time.time()
        result = ExecutionResult(goal=goal, status=GoalStatus.IN_PROGRESS)
        screen = self._get_screen()

        for step_num in range(1, self.max_steps + 1):
            # 1. Perceive
            perception = self.perceiver.perceive(screen)

            # 2. Plan
            actions = self.planner.plan(goal, screen, perception)
            if not actions:
                result.status = GoalStatus.FAILED
                result.message = "Planner produced no actions"
                break

            # 3. Execute first action
            action = actions[0]
            screen_before = screen
            success, observation = self.executor.execute(action, screen)

            # 4. Observe
            screen_after = self._get_screen()

            # 5. Verify
            step = Step(
                step_number=step_num,
                action=action,
                screen_before=screen_before,
                screen_after=screen_after,
                observation=observation,
                success=success,
            )
            progress, verify_note = self.verifier.verify(goal, screen_after, step)
            step.observation += f" | {verify_note}"
            result.steps.append(step)

            for obs in self._step_observers:
                obs(step)

            screen = screen_after

            # Check completion
            complete, note = self.verifier.is_goal_complete(goal, screen)
            if complete:
                result.status = GoalStatus.COMPLETED
                result.message = note
                result.final_screen = screen
                break

            if not success:
                result.status = GoalStatus.FAILED
                result.message = f"Action failed: {observation}"
                break
        else:
            result.status = GoalStatus.FAILED
            result.message = f"Exceeded max steps ({self.max_steps})"

        result.duration_ms = (time.time() - start_time) * 1000
        if not result.final_screen:
            result.final_screen = screen
        return result

    def click(self, target: str) -> ExecutionResult:
        """Convenience: click a target."""
        return self.execute(f"click {target}")

    def type_text(self, target: str, text: str) -> ExecutionResult:
        """Convenience: type text into a target."""
        return self.execute(f"type '{text}' into {target}")


def run_gui_agent(goal: str, screen: Optional[Screen] = None) -> ExecutionResult:
    """Convenience function."""
    agent = GUIAgent()
    if screen:
        agent.set_screen_provider(lambda: screen)
    return agent.execute(goal)
