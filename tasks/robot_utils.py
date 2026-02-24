"""Shared utilities for CCI tasks that invoke Robot Framework setup tests."""

try:
    from cumulusci.core.exceptions import TaskOptionsError
except ImportError:
    TaskOptionsError = Exception  # type: ignore

_URLLIB3_FIX = (
    "Pin urllib3 to 1.x in this environment "
    "(e.g. pip install \"urllib3>=1.26,<2\" or pip install -r robot/requirements.txt). "
    "See README Troubleshooting for details."
)

_URLLIB3_ROOT_CAUSE = (
    "urllib3 2.x is installed; it causes the "
    "'Timeout value connect was <object object at ...>' error "
    "when running Robot setup tests."
)


def _urllib3_error(prefix: str = "") -> "TaskOptionsError":
    msg = f"{prefix}: {_URLLIB3_ROOT_CAUSE}" if prefix else _URLLIB3_ROOT_CAUSE
    return TaskOptionsError(f"{msg} {_URLLIB3_FIX}")


def check_urllib3_for_robot(task_name: str = "") -> None:
    """Raise TaskOptionsError if urllib3 2.x is detected.

    Pass ``task_name`` (e.g. ``"EnableDocumentBuilderToggle"``) to include the
    failing task in the error message for faster diagnosis.

    Uses packaging.version when available for robust semver parsing. Falls back
    to a manual major-version split, and raises conservatively if the version
    string cannot be parsed at all (rather than silently skipping the check).
    """
    try:
        import urllib3
    except ImportError:
        return

    ver_str = getattr(urllib3, "__version__", None)
    if ver_str is None:
        raise TaskOptionsError(
            f"{task_name + ': ' if task_name else ''}"
            f"Cannot determine urllib3 version (missing __version__). "
            f"To be safe, pin urllib3 to 1.x. {_URLLIB3_FIX}"
        )

    try:
        from packaging.version import Version

        if Version(ver_str) >= Version("2.0"):
            raise _urllib3_error(task_name)
        return
    except Exception:
        pass  # packaging not available or version string unparseable; fall back to manual parse

    # Manual parse - fail conservatively on any parse error
    try:
        major = int(ver_str.split(".")[0])
    except (ValueError, IndexError, AttributeError):
        raise TaskOptionsError(
            f"{task_name + ': ' if task_name else ''}"
            f"Cannot parse urllib3 version {ver_str!r}. "
            f"To be safe, pin urllib3 to 1.x. {_URLLIB3_FIX}"
        )

    if major >= 2:
        raise _urllib3_error(task_name)
