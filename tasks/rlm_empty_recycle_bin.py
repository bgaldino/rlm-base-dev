"""CumulusCI wrapper for scripts/recycle_bin/empty_recycle_bin.py.

Permanently purges deleted records from the org's Recycle Bin. All logic lives in
the script, which also runs ad hoc; this class only hands it the org's session.

    cci task run empty_recycle_bin --org beta
"""
import sys
from pathlib import Path

# Import repo `tasks.*` before cumulusci: its project_config empties tasks.__path__, so a later `tasks.soql_utils` import fails.
from tasks.soql_utils import option_flag, requested_names

try:
    from cumulusci.core.tasks import BaseTask
    from cumulusci.core.exceptions import CommandException, TaskOptionsError
except ImportError:
    BaseTask = object
    CommandException = Exception
    TaskOptionsError = ValueError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "recycle_bin"))
import empty_recycle_bin as erb  # noqa: E402


class EmptyRecycleBin(BaseTask):
    """Purge deleted records from the Recycle Bin (dry run unless execute=true)."""

    salesforce_task = True

    task_options = {
        "objects": {"description": "sObjects to purge, a list or comma-separated; default (also when blank) is every object with a Recycle Bin", "required": False},
        "exclude": {"description": "sObjects to leave alone, a list or comma-separated", "required": False},
        "execute": {"description": "Actually purge; false is a dry run. Default true, also when blank; a list or an unparseable value is refused", "required": False},
        "fatal": {"description": "Fail the task if records could not be purged. Default false (also when blank): log a warning so a finished flow is never broken", "required": False},
    }

    def _run_task(self):
        # Read outside the try: a refused option must fail the task, not become a non-fatal warning,
        # and must stop it before any request. None, blank or whitespace is the default; a list item
        # that is not a string, a list for a boolean, or an unparseable boolean is a TaskOptionsError.
        objects = requested_names(self.options.get("objects"), "objects", TaskOptionsError)
        exclude = requested_names(self.options.get("exclude"), "exclude", TaskOptionsError)
        execute = option_flag(self.options.get("execute"), "execute", TaskOptionsError, default=True)
        fatal = option_flag(self.options.get("fatal"), "fatal", TaskOptionsError)
        try:
            org = erb.Org(self.org_config.instance_url, self.org_config.access_token)
            rc = erb.run(org, objects, exclude, execute, self.logger.info)
        except Exception as exc:  # non-fatal unless fatal=true
            if fatal:
                raise CommandException(f"Recycle Bin purge failed: {exc}") from exc
            self.logger.warning(f"Recycle Bin purge failed (non-fatal): {exc}")
            return
        if rc and fatal:
            raise CommandException("Some Recycle Bin records could not be purged.")
        if rc:
            self.logger.warning("Some Recycle Bin records could not be purged (non-fatal).")
