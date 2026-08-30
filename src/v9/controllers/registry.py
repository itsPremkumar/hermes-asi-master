"""v9 · Engineering Control Plane — Controller Registry.

Discovers, loads, and manages controller plugins.
Provides lifecycle management: register, get, list, discover.
"""

from __future__ import annotations

import importlib
import inspect
import pkgutil
import time
from typing import Any, Optional

from . import ControllerBase, ControllerMetadata


class ControllerRegistry:
    """Discovers and manages controller plugins.

    Usage:
        registry = ControllerRegistry()
        registry.discover()  # auto-discover in the controllers package
        controllers = registry.list_controllers()
        ctrl = registry.get("loop")
    """

    def __init__(self) -> None:
        self._controllers: dict[str, type[ControllerBase]] = {}
        self._instances: dict[str, ControllerBase] = {}

    def register(self, controller_class: type[ControllerBase]) -> None:
        """Register a controller class."""
        if not issubclass(controller_class, ControllerBase):
            raise TypeError(f"{controller_class} must be a subclass of ControllerBase")
        if controller_class.METADATA is None:
            raise ValueError(f"{controller_class.__name__} must define METADATA")
        name = controller_class.METADATA.name
        self._controllers[name] = controller_class

    def unregister(self, name: str) -> bool:
        """Unregister a controller by name."""
        if name in self._controllers:
            del self._controllers[name]
            self._instances.pop(name, None)
            return True
        return False

    def get(self, name: str) -> Optional[ControllerBase]:
        """Get a controller instance by name."""
        if name not in self._instances and name in self._controllers:
            self._instances[name] = self._controllers[name]()
        return self._instances.get(name)

    def get_class(self, name: str) -> Optional[type[ControllerBase]]:
        """Get a controller class by name."""
        return self._controllers.get(name)

    def list_controllers(self) -> list[ControllerMetadata]:
        """List metadata for all registered controllers."""
        return [cls.METADATA for cls in self._controllers.values()]

    def list_by_level(self, level: int) -> list[ControllerMetadata]:
        """List controllers at a specific level."""
        return [m for m in self.list_controllers() if m.level == level]

    def list_requires_approval(self) -> list[ControllerMetadata]:
        """List controllers that require human approval (level >= 10)."""
        return [m for m in self.list_controllers() if m.requires_approval]

    def discover(self, package: str = "v9.controllers") -> int:
        """Auto-discover controllers in the given package.

        Returns the number of controllers discovered.
        """
        count = 0
        try:
            pkg = importlib.import_module(package)
            for _, modname, ispkg in pkgutil.iter_modules(pkg.__path__):
                if ispkg:
                    continue
                try:
                    mod = importlib.import_module(f"{package}.{modname}")
                    for name, obj in inspect.getmembers(mod, inspect.isclass):
                        if (
                            issubclass(obj, ControllerBase)
                            and obj is not ControllerBase
                            and obj.METADATA is not None
                        ):
                            self.register(obj)
                            count += 1
                except Exception:
                    continue
        except ImportError:
            pass
        return count

    def clear(self) -> None:
        """Clear all registered controllers."""
        self._controllers.clear()
        self._instances.clear()

    def __len__(self) -> int:
        return len(self._controllers)

    def __contains__(self, name: str) -> bool:
        return name in self._controllers

    def __iter__(self):
        return iter(self._controllers.keys())
