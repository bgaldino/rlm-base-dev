#!/usr/bin/env python3
"""Offline checks for scripts/ui_check/ui_check.py: no browser, org or network.

Run:  python tests/test_ui_check.py
"""
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("ui_check", ROOT / "scripts" / "ui_check" / "ui_check.py")
ui_check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ui_check)

URL = "https://example.my.salesforce.com/secur/frontdoor.jsp?otp=SECRETOTP&cshc=abc&sid=SECRETSID"


class UiCheckTest(unittest.TestCase):
    def test_scrub_redacts_session_values(self):
        out = ui_check._scrub("failed at " + URL)
        for secret in ("SECRETOTP", "SECRETSID", "abc"):
            self.assertNotIn(secret, out)

    def test_frontdoor_url_is_read_from_sf_json(self):
        done = subprocess.CompletedProcess([], 0, json.dumps({"result": {"url": URL}}), "")
        with mock.patch.object(ui_check.subprocess, "run", return_value=done) as run:
            self.assertEqual(ui_check._frontdoor_url("alias"), URL)
        self.assertIn("--url-only", run.call_args[0][0])

    def test_missing_url_exits_without_echoing_output(self):
        done = subprocess.CompletedProcess([], 1, "not json " + URL, "")
        with mock.patch.object(ui_check.subprocess, "run", return_value=done):
            with self.assertRaises(SystemExit) as ctx:
                ui_check._frontdoor_url("alias")
        self.assertNotIn("SECRET", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
