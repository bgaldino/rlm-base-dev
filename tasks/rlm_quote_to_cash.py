"""CCI wrapper for the Transaction Data Harness quote-to-cash check.

``cci task run verify_quote_to_cash --org <cci-alias>`` runs

    python -m scripts.txn_data_harness.cli quote-to-cash --org <username>

from the repo root with CumulusCI's own interpreter: one transaction from quote
to an applied payment, then the read-only balance checks. The task fails when
that command exits non-zero. It is opt-in and in no flow: it writes records,
and Posted invoices cannot be deleted.
"""

import subprocess
import sys

try:
    from cumulusci.core.exceptions import CommandException
    from cumulusci.core.tasks import BaseTask
except ImportError:  # importable for offline tests without CumulusCI
    BaseTask = object
    CommandException = Exception


def harness_command(python: str, username: str, config=None) -> list:
    """The harness command line the task runs."""
    cmd = [python, "-m", "scripts.txn_data_harness.cli", "quote-to-cash",
           "--org", username]
    if config:
        cmd += ["--config", str(config)]
    return cmd


class VerifyQuoteToCash(BaseTask):
    """Carry one quote to an applied payment and verify the balances."""

    # Shells out to the harness, which authenticates through `sf` with the
    # username; no OAuth refresh is needed, but --org must be accepted.
    salesforce_task = True

    task_options = {
        "config": {
            "description": (
                "Scenario config whose scenarios target payment_applied, relative "
                "to the repo root (default: the harness's "
                "scenarios/sales_txn_quote/20-quote-to-cash.yaml)."
            ),
            "required": False,
        },
    }

    def _run_task(self):
        cmd = harness_command(sys.executable, self.org_config.username,
                              self.options.get("config"))
        self.logger.info("Running: %s", " ".join(cmd[1:]))
        returncode = subprocess.run(cmd, cwd=self.project_config.repo_root).returncode
        if returncode:
            raise CommandException(
                f"quote-to-cash check failed (exit {returncode}); the FAIL or "
                "ERROR lines above say why. Exit codes: "
                "docs/guides/quote-to-cash-runbook.md."
            )
