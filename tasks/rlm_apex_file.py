"""
Custom CumulusCI task for executing anonymous Apex via file-based approach.

This task wraps the Salesforce CLI's `sf apex run --file` command to execute
Apex scripts without URI length limitations. It maintains full compatibility
with the standard AnonymousApexTask options while avoiding the 414 URI Too Long
error that occurs when large Apex scripts are passed via the Tooling API.

Usage:
    In cumulusci.yml:
        my_task:
            class_path: tasks.rlm_apex_file.FileBasedAnonymousApexTask
            options:
                path: scripts/apex/myScript.apex

    Command line:
        cci task run my_task --org my_org

Key Differences from AnonymousApexTask:
    - Uses sf apex run --file instead of Tooling API's executeAnonymous endpoint
    - No URI length limitations (handles scripts >100KB)
    - Requires sf CLI to be installed and org to have a username
    - Slightly different error message format from sf CLI vs Tooling API

Security Notes:
    - All file paths are validated to be within the project repository
    - Temporary files are created with restricted permissions and cleaned up
    - Command execution uses subprocess list args (not shell=True) to prevent injection
    - Org credentials are passed via SF CLI's built-in auth, not in command args

Performance Notes:
    - Similar execution time to AnonymousApexTask for small scripts
    - May be slightly slower for very small scripts due to file I/O overhead
    - Scales better for large scripts (no network overhead from large URI params)
    - 5-minute timeout prevents hanging on infinite loops or long-running scripts
"""
import json
import os
import shlex
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional

# Constants
APEX_EXECUTION_TIMEOUT_SECONDS = 300  # 5 minutes - sufficient for most scripts
MAX_LOG_OUTPUT_CHARS = 1000  # Truncate log output to prevent log spam
MAX_DEBUG_LOG_LINES = 50  # Limit debug log output lines

try:
    from cumulusci.tasks.sfdx import SFDXBaseTask
    from cumulusci.core.exceptions import (
        TaskOptionsError,
        CommandException,
        ApexCompilationException,
        ApexException,
    )
    from cumulusci.core.keychain import BaseProjectKeychain
    from cumulusci.core.utils import process_bool_arg
    from cumulusci.utils import in_directory, inject_namespace
except ImportError:
    # Graceful degradation if CumulusCI is not installed
    print("CumulusCI not found. Please install it for this task to work.")
    SFDXBaseTask = object
    TaskOptionsError = Exception
    CommandException = Exception
    ApexCompilationException = Exception
    ApexException = Exception
    BaseProjectKeychain = object


class FileBasedAnonymousApexTask(SFDXBaseTask):
    """
    Executes anonymous Apex from a file or string using sf apex run --file.

    This task is functionally equivalent to CumulusCI's built-in AnonymousApexTask
    but uses file-based execution instead of the Tooling API's executeAnonymous
    endpoint. This avoids HTTP 414 URI Too Long errors for large Apex scripts.

    Execution Flow:
        1. Validate org configuration and username
        2. Read Apex code from path and/or string option
        3. Process namespace injection and parameter token replacement
        4. Write processed Apex to a secure temporary file
        5. Execute via sf apex run --file --json
        6. Parse JSON response and check for compilation/runtime errors
        7. Clean up temporary file

    Task Options:
        path: The path to an Apex file to run.
        apex: A string of Apex to run (concatenated after the file, if specified).
        managed: If True, will insert the project's namespace prefix.
        namespaced: If True, %%%NAMESPACED_RT%%% and %%%namespaced%%% tokens
                    will be replaced with the namespace prefix for Record Types.
        param1: Parameter to pass to the Apex (use as %%%PARAM_1%%% in code).
        param2: Parameter to pass to the Apex (use as %%%PARAM_2%%% in code).

    Raises:
        TaskOptionsError: If required options are missing or invalid
        CommandException: If the sf CLI command fails
        ApexCompilationException: If the Apex code fails to compile
        ApexException: If the Apex code throws a runtime exception
    """

    keychain_class = BaseProjectKeychain

    task_options: Dict[str, Dict[str, Any]] = {
        "path": {
            "description": "The path to an Apex file to run.",
            "required": False
        },
        "apex": {
            "description": "A string of Apex to run (after the file, if specified).",
            "required": False
        },
        "managed": {
            "description": (
                "If True, will insert the project's namespace prefix. "
                "Defaults to False or no namespace."
            ),
            "required": False
        },
        "namespaced": {
            "description": (
                "If True, the tokens %%%NAMESPACED_RT%%% and %%%namespaced%%% "
                "will get replaced with the namespace prefix for Record Types."
            ),
            "required": False
        },
        "param1": {
            "description": (
                "Parameter to pass to the Apex. Use as %%%PARAM_1%%% in the Apex code. "
                "Defaults to an empty value."
            ),
            "required": False
        },
        "param2": {
            "description": (
                "Parameter to pass to the Apex. Use as %%%PARAM_2%%% in the Apex code. "
                "Defaults to an empty value."
            ),
            "required": False
        },
    }

    def _validate_options(self):
        """Validate that at least one of path or apex is provided."""
        super()._validate_options()

        if not self.options.get("path") and not self.options.get("apex"):
            raise TaskOptionsError(
                "You must specify either the `path` or `apex` option."
            )

    def _run_task(self):
        """Execute the anonymous Apex via sf apex run --file."""
        # Validate org config exists
        if not hasattr(self, 'org_config') or not self.org_config:
            raise TaskOptionsError("No org config available. This task requires a connected org.")

        # Validate org has a username (required for SF CLI)
        # The sf apex run command requires a valid org alias/username to target.
        # JWT orgs, scratch orgs, and connected orgs all have usernames.
        # Token-only auth without username is not supported by sf apex run.
        org_username = getattr(self.org_config, 'username', None)
        if not org_username:
            raise TaskOptionsError(
                "Org config has no username. This task requires an org with a username "
                "(scratch org or connected org with sf org login)."
            )

        self.logger.debug(f"Target org: {org_username}")

        # Read and prepare the Apex code
        apex = self._process_apex_from_path(self.options.get("path"))
        apex += self._process_apex_string(self.options.get("apex"))

        # Log Apex size for debugging
        apex_size = len(apex.encode('utf-8'))
        self.logger.debug(f"Prepared Apex code size: {apex_size:,} bytes ({len(apex.splitlines())} lines)")

        apex = self._prepare_apex(apex)

        # Write to temporary file with restricted permissions
        # mkstemp creates the file with mode 0600 (owner read/write only) for security
        # Returns (file_descriptor, path) - we must close the fd or use fdopen
        temp_fd, temp_path = tempfile.mkstemp(suffix='.apex', text=True)
        try:
            # Write the prepared Apex to the temp file
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                f.write(apex)

            self.logger.debug(f"Wrote Apex to temporary file: {temp_path}")

            # Execute via sf apex run --file
            self.logger.info("Executing anonymous Apex")
            result = self._run_sf_apex(temp_path)

            # Parse and check the result
            self._check_result(result)

            self.logger.info("Anonymous Apex Executed Successfully!")

        except Exception as e:
            # Log the error with context before re-raising
            self.logger.error(f"Anonymous Apex execution failed: {str(e)}")
            raise
        finally:
            # Clean up temporary file
            try:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    self.logger.debug(f"Cleaned up temporary file: {temp_path}")
            except OSError as e:
                # Log cleanup failure but don't fail the task
                self.logger.warning(f"Failed to clean up temporary file {temp_path}: {e}")

    def _process_apex_from_path(self, apex_path: Optional[str]) -> str:
        """
        Process apex given via the --path task option.

        Args:
            apex_path: Path to the Apex file to read

        Returns:
            The Apex code from the file, or empty string if no path provided

        Raises:
            TaskOptionsError: If the path is invalid, outside repo, or unreadable
        """
        if not apex_path:
            return ""

        # Security: Validate path is within project repository
        if not in_directory(apex_path, self.project_config.repo_root):
            raise TaskOptionsError(
                "Please specify a path inside your project repository. "
                f"You specified: {apex_path}"
            )

        # Validate file exists and is a regular file
        apex_file = Path(apex_path)
        if not apex_file.exists():
            raise TaskOptionsError(f"Apex file not found: {apex_path}")

        if not apex_file.is_file():
            raise TaskOptionsError(f"Path is not a file: {apex_path}")

        self.logger.info(f"Processing Apex from path: {apex_path}")

        try:
            with open(apex_path, "r", encoding="utf-8") as f:
                apex = f.read()
        except IOError as e:
            raise TaskOptionsError(f"Could not read file {apex_path}: {e}")
        except UnicodeDecodeError as e:
            raise TaskOptionsError(f"File {apex_path} is not valid UTF-8: {e}")

        # Validate we actually got content
        if not apex or not apex.strip():
            self.logger.warning(f"Apex file {apex_path} is empty or contains only whitespace")

        return apex

    def _process_apex_string(self, apex_string: Optional[str]) -> str:
        """
        Process the string of apex given via the --apex task option.

        Args:
            apex_string: Apex code provided as a string

        Returns:
            The Apex code with a leading newline, or empty string if None
        """
        if not apex_string:
            return ""

        self.logger.info("Processing Apex from '--apex' option")
        # Append a newline so that we don't clash if apex was also
        # given via the --path option
        return "\n" + apex_string

    def _prepare_apex(self, apex: str) -> str:
        """
        Prepare Apex code by injecting namespace and replacing parameter tokens.

        This method replicates the logic from AnonymousApexTask._prepare_apex()
        to maintain full compatibility with existing task configurations.

        Args:
            apex: The raw Apex code

        Returns:
            The prepared Apex code with namespace and parameters replaced
        """
        # Process namespace tokens
        # This logic matches AnonymousApexTask to ensure compatibility:
        # - managed=True: inject namespace for a managed package
        # - namespaced=True: replace %%%NAMESPACED_RT%%% tokens with namespace
        # - Both default to auto-detection based on project and org config
        namespace = self.project_config.project__package__namespace

        if "managed" in self.options:
            managed = process_bool_arg(self.options["managed"])
        else:
            managed = (
                bool(namespace) and namespace in self.org_config.installed_packages
            )

        if "namespaced" in self.options:
            namespaced = process_bool_arg(self.options["namespaced"])
        else:
            namespaced = bool(namespace) and namespace == self.org_config.namespace

        if managed or namespaced:
            self.logger.debug(
                f"Injecting namespace: namespace={namespace}, managed={managed}, namespaced={namespaced}"
            )

        _, apex = inject_namespace(
            "",
            apex,
            namespace=namespace,
            managed=managed,
            namespaced_org=namespaced,
        )

        # This is an extra token which is not handled by inject_namespace
        apex = apex.replace(
            "%%%NAMESPACED_RT%%%", namespace + "." if namespaced else ""
        )

        # Process optional parameter token replacement
        for param_num in [1, 2]:
            param_key = f"param{param_num}"
            param_value = self.options.get(param_key) or ""
            if param_value:
                token = f"%%%PARAM_{param_num}%%%"
                self.logger.debug(f"Replacing {token} token")
                apex = apex.replace(token, param_value)

        return apex

    def _run_sf_apex(self, apex_file_path: str) -> Dict[str, Any]:
        """
        Execute the Apex file using sf apex run --file.

        Args:
            apex_file_path: Path to the temporary Apex file

        Returns:
            Parsed JSON result from the sf command

        Raises:
            CommandException: If the sf command fails to execute or returns invalid JSON
        """
        # Get the org alias or username
        org_alias = self.org_config.username

        # Build the command (using list to prevent shell injection)
        command = [
            "sf",
            "apex",
            "run",
            "--target-org",
            org_alias,
            "--file",
            apex_file_path,
            "--json"
        ]

        # Log the command at debug level (for troubleshooting)
        self.logger.debug(f"Executing command: {shlex.join(command)}")

        # Execute the command
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,  # Don't raise on non-zero exit; we'll handle it
                timeout=APEX_EXECUTION_TIMEOUT_SECONDS
            )
        except subprocess.TimeoutExpired:
            raise CommandException(
                f"sf apex run command timed out after {APEX_EXECUTION_TIMEOUT_SECONDS} seconds. "
                f"This may indicate an infinite loop or very long-running operation. "
                f"Consider splitting large Apex scripts into smaller chunks or optimizing the code."
            )
        except FileNotFoundError:
            raise CommandException(
                "sf command not found. Please ensure Salesforce CLI is installed and in PATH."
            )
        except Exception as e:
            raise CommandException(
                f"Failed to execute sf apex run command: {type(e).__name__}: {str(e)}"
            )

        # Log stderr if present (may contain warnings even on success)
        if result.stderr:
            self.logger.debug(f"sf apex run stderr: {result.stderr}")

        # Parse the JSON output
        try:
            output = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            # If JSON parsing fails, provide detailed error with truncated output
            self.logger.error(f"sf apex run returned invalid JSON: {e}")
            self.logger.error(f"Command exit code: {result.returncode}")
            self.logger.error(f"Stdout: {result.stdout[:MAX_LOG_OUTPUT_CHARS]}")
            self.logger.error(f"Stderr: {result.stderr[:MAX_LOG_OUTPUT_CHARS]}")

            raise CommandException(
                f"Failed to parse sf apex run output as JSON: {e}\n"
                f"Status: {result.returncode}\n"
                f"Stdout preview: {result.stdout[:MAX_LOG_OUTPUT_CHARS]}\n"
                f"Stderr preview: {result.stderr[:MAX_LOG_OUTPUT_CHARS]}"
            )

        return output

    def _check_result(self, result: Dict[str, Any]) -> None:
        """
        Check the sf apex run result for errors.

        The sf apex run --json output has a different structure than the
        Tooling API's executeAnonymous response, so we need to adapt.

        Args:
            result: Parsed JSON from sf apex run --json

        Raises:
            ApexCompilationException: If the Apex code failed to compile
            ApexException: If the Apex code threw a runtime exception
            CommandException: If the sf command failed
        """
        # Check for command-level errors (status != 0)
        # The sf CLI returns status=0 for success, non-zero for failures
        # Status can be None if the JSON structure is unexpected
        status = result.get("status")
        if status is not None and status != 0:
            message = result.get("message", "Unknown error")
            self.logger.error(f"sf apex run command failed with status {status}: {message}")

            # Check if it's a compilation error in the message
            if "compiled successfully: false" in message.lower():
                apex_result = result.get("result", {})
                line = apex_result.get("line", 0)
                problem = apex_result.get("compileProblem", message)
                raise ApexCompilationException(line, problem)

            # Otherwise it's a general command error
            raise CommandException(f"sf apex run failed: {message}")

        # Get the Apex execution result
        apex_result = result.get("result", {})

        if not apex_result:
            raise CommandException(
                "sf apex run returned no result. This may indicate an internal error."
            )

        # Check compilation status
        compiled = apex_result.get("compiled", False)
        if not compiled:
            line = apex_result.get("line", 0)
            problem = apex_result.get("compileProblem", "Unknown compilation error")
            column = apex_result.get("column")

            error_msg = f"Line {line}"
            if column:
                error_msg += f", column {column}"
            error_msg += f": {problem}"

            self.logger.error(f"Apex compilation failed: {error_msg}")
            raise ApexCompilationException(line, problem)

        # Check execution success
        success = apex_result.get("success", False)
        if not success:
            exception_message = apex_result.get("exceptionMessage", "Unknown exception")
            exception_trace = apex_result.get("exceptionStackTrace", "")

            self.logger.error(f"Apex execution failed: {exception_message}")
            if exception_trace:
                self.logger.error(f"Stack trace:\n{exception_trace}")

            raise ApexException(exception_message, exception_trace)

        # Log success details at debug level
        # Note: Apex execution logs from sf CLI contain System.debug output
        # and platform debug information. These are useful for troubleshooting
        # but can be verbose, so we log at debug level and truncate.
        logs = apex_result.get("logs")
        if logs:
            log_lines = logs.split('\n')
            self.logger.debug(f"Apex execution logs ({len(log_lines)} total lines, showing first {MAX_DEBUG_LOG_LINES}):")
            for log_line in log_lines[:MAX_DEBUG_LOG_LINES]:
                self.logger.debug(f"  {log_line}")
