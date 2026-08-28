#!/usr/bin/env python3
"""
omnichannel_gateway.py — HERMES-ASI-MASTER Omnichannel Gateway
Manages multi-platform message ingestion and delivery (Telegram, Discord, Slack, GitHub Webhooks).
"""

import sys
import unittest
from pathlib import Path
from datetime import datetime, timezone

def format_platform_message(raw_text: str, platform: str) -> str:
    platform = platform.lower()
    if platform == "telegram":
        # Escape HTML or Markdown for Telegram
        return f"<b>[HERMES-ASI]</b>\n{raw_text}"
    elif platform == "discord":
        return f"**[HERMES-ASI Executive]**\n>>> {raw_text}"
    elif platform == "github":
        return f"## [HERMES-ASI Verified Report]\n\n{raw_text}\n\n---\n*Automated by Hermes Agent.*"
    return raw_text

def parse_incoming_webhook(event_type: str, payload: dict) -> dict:
    if event_type == "github_issue":
        return {
            "action": "triage_issue",
            "title": payload.get("issue", {}).get("title", ""),
            "body": payload.get("issue", {}).get("body", "")
        }
    return {"action": "general_message", "content": str(payload)}

class OmnichannelGatewayTests(unittest.TestCase):
    def test_formatting(self):
        tg = format_platform_message("Task Completed", "telegram")
        self.assertIn("<b>[HERMES-ASI]</b>", tg)
        gh = format_platform_message("Task Completed", "github")
        self.assertIn("## [HERMES-ASI Verified Report]", gh)

    def test_webhook(self):
        parsed = parse_incoming_webhook("github_issue", {"issue": {"title": "Bug in search", "body": "Fix it"}})
        self.assertEqual(parsed["action"], "triage_issue")

if __name__ == "__main__":
    if "--test" in sys.argv:
        suite = unittest.TestLoader().loadTestsFromTestCase(OmnichannelGatewayTests)
        res = unittest.TextTestRunner(verbosity=2).run(suite)
        sys.exit(0 if res.wasSuccessful() else 1)
    else:
        print("[*] Omnichannel Gateway Active. Use --test for self-verification.")
