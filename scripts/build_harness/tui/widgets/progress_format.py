"""Formatting helpers for TUI progress labels."""

from __future__ import annotations


def format_step_label(step_number: int, target_type: str, target_name: str) -> str:
    """Render consistent current-step labels."""
    return f"step {step_number} {target_type}:{target_name}"
