#!/usr/bin/env python3
"""
iot_controller.py — HERMES-ASI-MASTER Physical World & IoT Controller
Integrates Home Assistant and hardware sensor telemetry.
"""

import sys
import unittest
from pathlib import Path

def parse_sensor_telemetry(entity_id: str, state: str, attributes: dict) -> dict:
    return {
        "entity_id": entity_id,
        "state": state,
        "unit": attributes.get("unit_of_measurement", ""),
        "is_alert": state in ["unavailable", "critical", "overheating"]
    }

class IotControllerTests(unittest.TestCase):
    def test_telemetry_normal(self):
        res = parse_sensor_telemetry("sensor.gpu_temperature", "62", {"unit_of_measurement": "C"})
        self.assertFalse(res["is_alert"])

    def test_telemetry_alert(self):
        res = parse_sensor_telemetry("sensor.gpu_temperature", "critical", {"unit_of_measurement": "C"})
        self.assertTrue(res["is_alert"])

if __name__ == "__main__":
    if "--test" in sys.argv:
        suite = unittest.TestLoader().loadTestsFromTestCase(IotControllerTests)
        res = unittest.TextTestRunner(verbosity=2).run(suite)
        sys.exit(0 if res.wasSuccessful() else 1)
    else:
        print("[*] IoT Controller Active. Use --test for self-verification.")
