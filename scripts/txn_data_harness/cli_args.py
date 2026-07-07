"""Shared argparse helpers for Transaction Data Harness command surfaces.

The legacy ``generate`` module and the composable ``cli`` subcommands expose
overlapping flags. Keep the definitions here categorized by purpose so help text
doesn't drift, while resume commands avoid accepting run-only knobs by accident.
"""

from __future__ import annotations

import argparse

from .auth import DEFAULT_API_VERSION
from .models import STAGES_QUOTE
from .runner import DEFAULT_MAX_RETRIES


def add_connection_args(p: argparse.ArgumentParser) -> None:
    """Target-org and REST transport options used by live commands."""
    p.add_argument(
        "--org",
        required=True,
        help="Target org: sf CLI alias or username (NOT a CCI alias).",
    )
    p.add_argument(
        "--api-version",
        default=DEFAULT_API_VERSION,
        help=f"API version (default: {DEFAULT_API_VERSION}; 'latest' to query).",
    )
    p.add_argument(
        "--transport",
        choices=["requests", "cli"],
        default="requests",
        help="REST transport (default: requests; cli = sf api proxy).",
    )


def add_scenario_args(p: argparse.ArgumentParser, *, include_target_stage: bool = True) -> None:
    """Config and discovery overrides that shape one or more scenarios."""
    p.add_argument("--config", help="YAML/JSON config file (all fields optional).")
    p.add_argument("--count", type=int, help="Number of transactions to generate.")
    if include_target_stage:
        p.add_argument(
            "--target-stage",
            choices=STAGES_QUOTE,
            help="How far through the lifecycle to run.",
        )
    p.add_argument("--account", help="Pin the account by Name.")
    p.add_argument("--product", help="Pin the product by SKU.")
    p.add_argument(
        "--with-opportunity",
        action="store_true",
        help="Prepend an Opportunity the quote links to.",
    )
    p.add_argument("--opportunity-stage", help="Pin the Opportunity StageName.")


def add_execution_args(p: argparse.ArgumentParser) -> None:
    """Run/plan execution controls. Not appropriate for ``cli step``."""
    p.add_argument(
        "--concurrency",
        type=int,
        default=4,
        help="Parallel scenario workers (default: 4).",
    )
    p.add_argument(
        "--poll-timeout",
        type=int,
        default=180,
        help="Async poll timeout in seconds (default: 180).",
    )
    p.add_argument(
        "--max-retries",
        type=int,
        default=DEFAULT_MAX_RETRIES,
        help=(
            f"Retries for transient scenario failures "
            f"(default: {DEFAULT_MAX_RETRIES}; 0 disables)."
        ),
    )
    p.add_argument(
        "--no-probe",
        action="store_true",
        help="Reserved for future PST probes; currently no-op.",
    )
    p.add_argument(
        "--keep-probes",
        action="store_true",
        help="Reserved for future PST probes; currently no-op.",
    )


def add_resume_args(p: argparse.ArgumentParser) -> None:
    """Options needed to resume a manifest through ``cli step``."""
    p.add_argument("--config", help="YAML/JSON config file (optional fallback for lines).")
    p.add_argument("--account", help="Pin the account by Name.")
    p.add_argument("--product", help="Pin the product by SKU.")
    p.add_argument(
        "--with-opportunity",
        action="store_true",
        help="Resume a manifest whose original PST run prepended an Opportunity.",
    )
    p.add_argument("--opportunity-stage", help="Pin the Opportunity StageName.")
    p.add_argument(
        "--poll-timeout",
        type=int,
        default=180,
        help="Async poll timeout in seconds (default: 180).",
    )


def add_verbosity_arg(p: argparse.ArgumentParser) -> None:
    p.add_argument("-v", "--verbose", action="count", default=0, help="-v for INFO, -vv for DEBUG.")


def add_generate_args(p: argparse.ArgumentParser) -> None:
    """Full run/plan argument contract for ``generate`` and ``cli run/plan``."""
    add_connection_args(p)
    add_scenario_args(p)
    add_execution_args(p)
    add_verbosity_arg(p)
