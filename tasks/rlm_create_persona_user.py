"""
CumulusCI task to create a scratch org user from a definition file.

Wraps `sf org create user --definition-file <path> --set-alias <alias>
--set-unique-username --target-org <username>`.
"""
import subprocess

try:
    from cumulusci.core.tasks import BaseTask
    from cumulusci.core.exceptions import TaskOptionsError
except ImportError:
    BaseTask = object
    TaskOptionsError = Exception


class CreatePersonaUser(BaseTask):
    """Create a scratch org user from a JSON definition file via the sf CLI."""

    task_options = {
        "definition_file": {
            "description": "Path to the user definition JSON file (relative to repo root).",
            "required": True,
        },
        "alias": {
            "description": "SF CLI alias to assign to the new user.",
            "required": True,
        },
        "set_unique_username": {
            "description": "Append a unique suffix to the username to avoid conflicts. Defaults to True.",
            "required": False,
            "type": bool,
        },
    }

    def _run_task(self):
        definition_file = self.options.get("definition_file")
        alias = self.options.get("alias")
        set_unique = self.options.get("set_unique_username", True)

        if not definition_file:
            raise TaskOptionsError("definition_file is required.")
        if not alias:
            raise TaskOptionsError("alias is required.")

        cmd = [
            "sf", "org", "create", "user",
            "--definition-file", definition_file,
            "--set-alias", alias,
            "--target-org", self.org_config.username,
        ]
        if set_unique:
            cmd.append("--set-unique-username")

        self.logger.info(f"Creating user from {definition_file} with alias '{alias}' ...")
        self.logger.info(f"  Target org: {self.org_config.username}")

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.stdout:
            self.logger.info(result.stdout.strip())
        if result.stderr:
            (self.logger.warning if result.returncode == 0 else self.logger.error)(
                result.stderr.strip()
            )

        if result.returncode != 0:
            raise TaskOptionsError(
                f"sf org create user failed (exit {result.returncode}).\n{result.stderr}"
            )

        self.logger.info(f"User created successfully with alias '{alias}'.")
