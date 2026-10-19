"""CumulusCI wrapper for scripts/recycle_bin/empty_recycle_bin.py.

Permanently purges deleted records from the org's Recycle Bin. All logic lives in
the script, which also runs ad hoc; this class only hands it the org's session.

    cci task run empty_recycle_bin --org beta
"""
import sys
from pathlib import Path

try:
    from cumulusci.core.tasks import BaseTask
    from cumulusci.core.exceptions import CommandException
except ImportError:
    BaseTask = object
    CommandException = Exception

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "recycle_bin"))
import empty_recycle_bin as erb  # noqa: E402


class EmptyRecycleBin(BaseTask):
    """Purge deleted records from the Recycle Bin (dry run unless execute=true)."""

    salesforce_task = True

    task_options = {
        "objects": {"description": "Comma-separated sObjects to purge; default is every object with a Recycle Bin", "required": False},
        "exclude": {"description": "Comma-separated sObjects to leave alone", "required": False},
        "execute": {"description": "Actually purge; false is a dry run. Default true", "required": False},
        "fatal": {"description": "Fail the task if records could not be purged. Default false: log a warning so a finished flow is never broken", "required": False},
    }

    def _run_task(self):
        split = lambda v: [x.strip() for x in str(v or "").split(",") if x.strip()]  # noqa: E731
        flag = lambda k, d: str(self.options.get(k, d)).lower() == "true"  # noqa: E731
        try:
            org = erb.Org(self.org_config.instance_url, self.org_config.access_token)
            rc = erb.run(org, split(self.options.get("objects")), split(self.options.get("exclude")),
                         flag("execute", True), self.logger.info)
        except Exception as exc:  # non-fatal unless fatal=true
            if flag("fatal", False):
                raise CommandException(f"Recycle Bin purge failed: {exc}") from exc
            self.logger.warning(f"Recycle Bin purge failed (non-fatal): {exc}")
            return
        if rc and flag("fatal", False):
            raise CommandException("Some Recycle Bin records could not be purged.")
        if rc:
            self.logger.warning("Some Recycle Bin records could not be purged (non-fatal).")
