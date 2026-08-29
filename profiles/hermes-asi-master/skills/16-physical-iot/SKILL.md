---
name: hermes-physical-iot
description: Hardware environment integration, Home Assistant sensor telemetry, and ambient physical monitoring.
version: "1.0.0"
author: Hermes Advanced Team
license: MIT
metadata:
  hermes:
    tags: [hermes, physical-iot, home-assistant, hardware, sensors, telemetry]
    category: hermes-advanced
---

# SKILL 16 — PHYSICAL IOT & AMBIENT MONITORING

> **Load this skill when:** Interfacing with physical sensors, Home Assistant smart devices, or hardware status alerts.

---

## 1. Telemetry Loop

```
Hardware Sensors -> Home Assistant REST/WS -> Ingestion Parser -> Threshold Analysis -> Alert / Adjustment Trigger
```
