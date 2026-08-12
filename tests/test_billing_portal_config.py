"""Offline regression coverage for Billing Portal flow gating."""

import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent.parent
FLAG_PATTERN = re.compile(
    r"project_config\.project__custom__([A-Za-z_][A-Za-z0-9_]*)"
)


def _flags(condition):
    return set(FLAG_PATTERN.findall(condition))


def test_every_billing_portal_task_requires_billing_and_portal_flags():
    data = yaml.safe_load((ROOT / "cumulusci.yml").read_text(encoding="utf-8"))
    steps = data["flows"]["prepare_billing_portal"]["steps"]

    assert len(steps) == 5
    for step_number, step in steps.items():
        flags = _flags(step.get("when", ""))
        assert "billing" in flags, step_number
        assert "billing_portal" in flags, step_number


def test_only_bundle_deploy_steps_require_billing_portal_deploy():
    data = yaml.safe_load((ROOT / "cumulusci.yml").read_text(encoding="utf-8"))
    steps = data["flows"]["prepare_billing_portal"]["steps"]

    for step_number in (2, 3, 4):
        assert "billing_portal_deploy" in _flags(steps[step_number]["when"])
    for step_number in (1, 5):
        assert "billing_portal_deploy" not in _flags(steps[step_number]["when"])
