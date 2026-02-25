"""
CumulusCI task to validate the local developer setup for rlm-base-dev.

Checks Python, CumulusCI, Salesforce CLI, SFDMU plugin version, Node.js,
and Robot Framework dependencies (Robot, SeleniumLibrary, webdriver-manager,
urllib3). Optionally auto-fixes an outdated or missing SFDMU plugin.

Run without an org:
    cci task run validate_setup

Options:
    auto_fix                Auto-update SFDMU if outdated (default: true)
    required_sfdmu_version  Minimum SFDMU version (default: 5.0.0)
    fail_on_error           Raise on required check failures (default: true)
"""
import json
import re
import subprocess
import sys
from typing import Any, Dict, List, Optional, Tuple

try:
    from cumulusci.core.exceptions import TaskOptionsError
    from cumulusci.core.tasks import BaseTask
except ImportError:
    BaseTask = object  # type: ignore[assignment,misc]
    TaskOptionsError = Exception  # type: ignore[assignment,misc]

# ── minimum required versions ────────────────────────────────────────────────
MIN_PYTHON: Tuple[int, ...] = (3, 8)
MIN_CCI: Tuple[int, ...] = (4, 0, 0)
MIN_SF_MAJOR: int = 2
MIN_SFDMU_DEFAULT: str = "5.0.0"

# ── status tokens ────────────────────────────────────────────────────────────
PASS = "PASS"
WARN = "WARN"
FAIL = "FAIL"
FIXED = "FIXED"


def _parse_version(version_str: str) -> Tuple[int, ...]:
    """Parse '4.38.0' → (4, 38, 0). Non-numeric segments stop the parse."""
    parts: List[int] = []
    for segment in version_str.strip().lstrip("v").split("."):
        try:
            parts.append(int(segment))
        except ValueError:
            break
    return tuple(parts) if parts else (0,)


class ValidateSetup(BaseTask):
    """Validate the local developer setup for rlm-base-dev.

    Checks each required tool and version, logs a clear pass/warn/fail result
    for each, and prints a summary. When auto_fix=true the SFDMU plugin is
    automatically installed or updated if it is absent or below the required
    version. Robot Framework dependencies are never auto-installed (the
    required pipx inject command is logged instead).
    """

    task_options: Dict[str, Dict[str, Any]] = {
        "auto_fix": {
            "description": (
                "Automatically install or update the SFDMU plugin when it is "
                "missing or below required_sfdmu_version. Default: true."
            ),
            "required": False,
        },
        "required_sfdmu_version": {
            "description": (
                f"Minimum required SFDMU plugin version. Default: {MIN_SFDMU_DEFAULT}. "
                "SFDMU v5 is required — v4.x has been deprecated. The project's "
                "export.json files and CSV data are formatted for v5 compatibility."
            ),
            "required": False,
        },
        "fail_on_error": {
            "description": (
                "Raise a task exception when one or more required checks fail. "
                "Warnings (optional dependencies) never cause a failure. Default: true."
            ),
            "required": False,
        },
    }

    # ── entry point ───────────────────────────────────────────────────────────

    def _run_task(self) -> None:
        auto_fix = self._bool_option("auto_fix", default=True)
        fail_on_error = self._bool_option("fail_on_error", default=True)
        required_sfdmu = self.options.get("required_sfdmu_version") or MIN_SFDMU_DEFAULT

        self.logger.info("=" * 60)
        self.logger.info("Validating developer setup for rlm-base-dev...")
        self.logger.info("=" * 60)

        results: List[Dict[str, str]] = [
            self._check_python(),
            self._check_cumulusci(),
            self._check_node(),
            self._check_sf_cli(),
            self._check_sfdmu(required_sfdmu, auto_fix),
            self._check_robot(),
            self._check_selenium_library(),
            self._check_webdriver_manager(),
            self._check_urllib3(),
        ]

        self._log_summary(results)

        if fail_on_error:
            failures = [r for r in results if r["status"] == FAIL]
            if failures:
                labels = ", ".join(r["label"] for r in failures)
                raise TaskOptionsError(f"Setup validation failed for: {labels}")

    # ── individual checks ─────────────────────────────────────────────────────

    def _check_python(self) -> Dict[str, str]:
        label = "Python"
        current = sys.version_info[:3]
        ver_str = ".".join(str(x) for x in current)
        min_str = ".".join(str(x) for x in MIN_PYTHON)
        if current >= MIN_PYTHON:
            return self._ok(label, ver_str)
        return self._fail(label, f"{ver_str} — requires {min_str}+")

    def _check_cumulusci(self) -> Dict[str, str]:
        label = "CumulusCI"
        try:
            import cumulusci  # noqa: PLC0415

            ver_str = getattr(cumulusci, "__version__", "unknown")
            min_str = ".".join(str(x) for x in MIN_CCI)
            if _parse_version(ver_str) >= MIN_CCI:
                return self._ok(label, ver_str)
            return self._fail(label, f"{ver_str} — requires {min_str}+")
        except ImportError:
            return self._fail(label, "not importable in current environment")

    def _check_node(self) -> Dict[str, str]:
        label = "Node.js"
        try:
            result = subprocess.run(
                ["node", "--version"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return self._ok(label, result.stdout.strip())
            return self._warn(label, "installed but returned a non-zero exit code")
        except FileNotFoundError:
            return self._warn(
                label,
                "not found — Node.js is required if you install SFDMU via npm. "
                "Install from https://nodejs.org/",
            )
        except Exception as exc:
            return self._warn(label, f"check failed: {exc}")

    def _check_sf_cli(self) -> Dict[str, str]:
        label = "Salesforce CLI (sf)"
        try:
            result = subprocess.run(
                ["sf", "--version"], capture_output=True, text=True, timeout=20
            )
            if result.returncode != 0:
                detail = (result.stderr or result.stdout or "").strip()
                msg = f"command failed (exit {result.returncode})"
                if detail:
                    msg += f": {detail[:200]}"
                return self._fail(label, msg)
            first_line = result.stdout.strip().split("\n")[0]
            match = re.search(r"@salesforce/cli/(\d+)\.(\d+)\.(\d+)", first_line)
            if match:
                major = int(match.group(1))
                ver_str = f"{match.group(1)}.{match.group(2)}.{match.group(3)}"
                if major >= MIN_SF_MAJOR:
                    return self._ok(label, ver_str)
                return self._fail(label, f"{ver_str} — requires v{MIN_SF_MAJOR}+")
            return self._ok(label, first_line)
        except FileNotFoundError:
            return self._fail(
                label,
                "not found — install from https://developer.salesforce.com/tools/salesforcecli",
            )
        except Exception as exc:
            return self._fail(label, f"check failed: {exc}")

    def _check_sfdmu(self, required_version: str, auto_fix: bool) -> Dict[str, str]:
        label = "SFDMU plugin"
        installed_ver = self._get_sfdmu_version()

        if installed_ver is None:
            if auto_fix:
                self.logger.info("[SFDMU] Plugin not installed. Installing now...")
                return self._install_or_update_sfdmu(label)
            return self._fail(
                label,
                "not installed — run: sf plugins install sfdmu",
            )

        req_tuple = _parse_version(required_version)
        if _parse_version(installed_ver) >= req_tuple:
            return self._ok(label, installed_ver)

        if auto_fix:
            self.logger.info(
                f"[SFDMU] {installed_ver} is below required {required_version}. Updating..."
            )
            return self._install_or_update_sfdmu(label, old_ver=installed_ver)

        return self._fail(
            label,
            f"{installed_ver} — requires {required_version}+. "
            "Run: sf plugins install sfdmu",
        )

    def _check_robot(self) -> Dict[str, str]:
        label = "Robot Framework"
        try:
            import robot  # noqa: PLC0415

            ver_str = getattr(
                getattr(robot, "version", None), "VERSION", None
            ) or getattr(robot, "__version__", "unknown")
            return self._ok(label, ver_str)
        except ImportError:
            return self._warn(
                label,
                "not found in the CCI Python env — required for Document Builder automation.\n"
                "  Fix: pipx inject cumulusci robotframework robotframework-seleniumlibrary "
                'webdriver-manager "urllib3>=2.6.3"',
            )

    def _check_selenium_library(self) -> Dict[str, str]:
        label = "SeleniumLibrary"
        try:
            import SeleniumLibrary  # noqa: PLC0415,N813

            ver_str = getattr(SeleniumLibrary, "__version__", "unknown")
            return self._ok(label, ver_str)
        except ImportError:
            return self._warn(
                label,
                "not found in the CCI Python env — required for Document Builder automation.\n"
                "  Fix: pipx inject cumulusci robotframework-seleniumlibrary",
            )

    def _check_webdriver_manager(self) -> Dict[str, str]:
        label = "webdriver-manager (optional)"
        try:
            import webdriver_manager  # noqa: PLC0415

            ver_str = getattr(webdriver_manager, "__version__", "unknown")
            return self._ok(label, ver_str)
        except ImportError:
            return self._warn(
                label,
                "not installed — ChromeDriver must be on PATH when this is absent.\n"
                "  Fix: pipx inject cumulusci webdriver-manager",
            )

    def _check_urllib3(self) -> Dict[str, str]:
        label = "urllib3"
        try:
            import urllib3  # noqa: PLC0415

            ver_str = getattr(urllib3, "__version__", "unknown")
            if _parse_version(ver_str) >= (2, 6, 3):
                return self._ok(label, ver_str)
            return self._warn(
                label,
                f"{ver_str} is below the minimum 2.6.3 — older versions have known security vulnerabilities.\n"
                '  Fix: pipx inject cumulusci "urllib3>=2.6.3" --force',
            )
        except ImportError:
            return self._warn(label, "not found in the CCI Python env")

    # ── SFDMU helpers ─────────────────────────────────────────────────────────

    def _get_sfdmu_version(self) -> Optional[str]:
        """Return the installed SFDMU version string, or None if not found."""
        # Try JSON output first (structured, reliable)
        try:
            result = subprocess.run(
                ["sf", "plugins", "--json"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                plugins = json.loads(result.stdout)
                for plugin in plugins:
                    if "sfdmu" in plugin.get("name", "").lower():
                        return plugin.get("version")
        except Exception:
            pass

        # Fall back to plain text output
        try:
            result = subprocess.run(
                ["sf", "plugins"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    if "sfdmu" in line.lower():
                        match = re.search(r"(\d+\.\d+\.\d+)", line)
                        if match:
                            return match.group(1)
        except Exception:
            pass

        return None

    def _install_or_update_sfdmu(
        self, label: str, old_ver: Optional[str] = None
    ) -> Dict[str, str]:
        try:
            result = subprocess.run(
                ["sf", "plugins", "install", "sfdmu"],
                capture_output=True,
                text=True,
                timeout=180,
            )
            if result.returncode != 0:
                return self._fail(
                    label,
                    f"auto-install/update failed: {result.stderr.strip() or result.stdout.strip()}",
                )
            new_ver = self._get_sfdmu_version() or "unknown"
            detail = f"updated {old_ver} → {new_ver}" if old_ver else f"installed {new_ver}"
            return self._fixed(label, detail)
        except Exception as exc:
            return self._fail(label, f"auto-install/update failed: {exc}")

    # ── summary ───────────────────────────────────────────────────────────────

    def _log_summary(self, results: List[Dict[str, str]]) -> None:
        passed = [r for r in results if r["status"] == PASS]
        fixed = [r for r in results if r["status"] == FIXED]
        warned = [r for r in results if r["status"] == WARN]
        failed = [r for r in results if r["status"] == FAIL]

        self.logger.info("")
        self.logger.info("=" * 60)
        self.logger.info("Setup Validation Summary")
        self.logger.info("=" * 60)
        self.logger.info(f"  Passed   : {len(passed)}")
        if fixed:
            self.logger.info(f"  Fixed    : {len(fixed)}")
        if warned:
            self.logger.info(f"  Warnings : {len(warned)}")
        if failed:
            self.logger.error(f"  Failed   : {len(failed)}")
        self.logger.info("=" * 60)

        if fixed:
            self.logger.info("Auto-fixed:")
            for r in fixed:
                self.logger.info(f"  {r['label']}: {r['detail']}")

        if warned:
            self.logger.warning("Warnings (non-blocking):")
            for r in warned:
                self.logger.warning(f"  {r['label']}: {r['detail']}")

        if failed:
            self.logger.error("Failures (blocking):")
            for r in failed:
                self.logger.error(f"  {r['label']}: {r['detail']}")
        else:
            self.logger.info("All required checks passed.")

    # ── result constructors ───────────────────────────────────────────────────

    def _ok(self, label: str, detail: str) -> Dict[str, str]:
        self.logger.info(f"  [PASS]  {label}: {detail}")
        return {"label": label, "status": PASS, "detail": detail}

    def _warn(self, label: str, detail: str) -> Dict[str, str]:
        self.logger.warning(f"  [WARN]  {label}: {detail}")
        return {"label": label, "status": WARN, "detail": detail}

    def _fail(self, label: str, detail: str) -> Dict[str, str]:
        self.logger.error(f"  [FAIL]  {label}: {detail}")
        return {"label": label, "status": FAIL, "detail": detail}

    def _fixed(self, label: str, detail: str) -> Dict[str, str]:
        self.logger.info(f"  [FIXED] {label}: {detail}")
        return {"label": label, "status": FIXED, "detail": detail}

    # ── utility ───────────────────────────────────────────────────────────────

    def _bool_option(self, key: str, default: bool) -> bool:
        val = self.options.get(key)
        if val is None:
            return default
        if isinstance(val, bool):
            return val
        return str(val).lower() not in ("false", "0", "no")
