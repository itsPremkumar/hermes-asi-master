---
name: hermes-computer-use-gui
description: Full-spectrum GUI and desktop computer-use automation via OmniParser and Playwright coordinate grounding.
version: "1.0.0"
author: Hermes Advanced Team
license: MIT
metadata:
  hermes:
    tags: [hermes, computer-use, gui, omniparser, os-world, desktop-automation]
    category: hermes-advanced
    requires_toolsets: [computer-use, browser]
---

# SKILL 13 — FULL-SPECTRUM COMPUTER USE & GUI

> **Load this skill when:** Task requires direct desktop interaction, multi-window GUI navigation, CAD/IDE automation, or visual coordinate interaction.

---

## 1. GUI Perception Pipeline

```
Desktop Screen -> Screenshot Capture -> OmniParser Bounding Boxes -> Coordinate Mapping -> Action Dispatch -> Verification Screenshot
```

## 2. Operating Procedures
1. **Coordinate Verification:** Never blind-click. Always verify element bounding box coordinates from the latest screen snapshot.
2. **Key Action Safety:** Gated by R2–R4 tiers. Never send keyboard macro commands without focus verification.
3. **Reversibility:** Capture a screenshot before and after every destructive action.
