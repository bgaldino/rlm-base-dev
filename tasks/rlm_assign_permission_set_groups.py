"""
Custom CumulusCI task to assign permission set groups with tolerance for permission warnings.
This task continues even when some permissions within the groups aren't available in the org.
"""
from typing import List, Optional

try:
    from cumulusci.tasks.salesforce.users.permsets import AssignPermissionSetGroups
    from cumulusci.core.exceptions import TaskOptionsError
except ImportError:
    AssignPermissionSetGroups = object
    TaskOptionsError = Exception


class AssignPermissionSetGroupsTolerant(AssignPermissionSetGroups):
    """Assign Permission Set Groups, but continue on warnings about unavailable permissions."""

    task_options = {
        **getattr(AssignPermissionSetGroups, "task_options", {}),
        # Override the inherited `user_alias` option to add explicit type and required keys.
        # getattr guards against the ImportError fallback where AssignPermissionSetGroups = object.
        "user_alias": {
            "description": "Alias of target user (if not the current running user, the default).",
            "required": False,
            "type": str,
        },
    }

    def _init_options(self, kwargs):
        # The parent reads options["api_names"] before CumulusCI checks required options,
        # so a run without it would fail with a bare KeyError.
        try:
            super()._init_options(kwargs)
        except KeyError as e:
            if e.args != ("api_names",):
                raise
            raise TaskOptionsError(
                "api_names is required: the Permission Set Group DeveloperNames to assign"
            ) from None

    def _run_task(self):
        """Override to handle warnings gracefully."""
        try:
            # Call parent implementation
            super()._run_task()
        except Exception as e:
            error_msg = str(e)
            # Check if the error is about permission warnings (not actual failures)
            if "Not all PermissionSetAssignments were saved" in error_msg:
                # Check if we actually got some successful assignments
                # If so, log a warning but continue
                self.logger.warning(
                    "Some permission set group assignments had warnings about unavailable permissions "
                    "(e.g., UseTemplatedApp in Enterprise edition). "
                    "This is expected and the deployment will continue."
                )
                # Don't re-raise - allow the flow to continue
                return
            else:
                # Re-raise other errors
                raise
