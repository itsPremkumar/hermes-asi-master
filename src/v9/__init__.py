"""v9 · Engineering Control Plane — Controller Base & Registry.

All controllers are pluggable modules that implement a common interface.
Controllers are discovered, loaded, and managed by the ControllerRegistry.

Modules:
- base: ControllerBase abstract class and ControllerMetadata
- registry: ControllerRegistry for discovery and management
- controllers: 16 engineering controllers
"""
