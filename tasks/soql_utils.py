"""Small helpers shared by the management tasks that build SOQL strings."""
import re
from typing import List, Optional


def soql_quote(value) -> str:
    """Return `value` as a single-quoted SOQL string literal, escaped."""
    text = str(value).replace("\\", "\\\\").replace("'", "\\'")
    text = text.replace("\n", "\\n").replace("\r", "\\r")
    return f"'{text}'"


def option_text(value, option: str = "option", exc=ValueError) -> Optional[str]:
    """An option as stripped text; None, blank or whitespace means not set (0 and False are values).

    A list, tuple, set or dict is refused: stringifying it would build a filter that matches nothing.
    """
    if isinstance(value, (list, tuple, set, dict)):
        raise exc(f"{option} must be a single value, got {value!r}")
    text = "" if value is None else str(value).strip()
    return text or None


def requested_names(value, option: str, exc=ValueError) -> List[str]:
    """`split_names`, except None, blank, whitespace-only or an empty list means no names were asked for."""
    if value is None or value == [] or value == () or (isinstance(value, str) and not value.strip()):
        return []
    return split_names(value, option, exc)


def split_names(value, option: str, exc=ValueError) -> List[str]:
    """Normalize a comma-separated string or a list into a de-duplicated list.

    Raises `exc` when the option is neither, or yields no names.
    """
    if isinstance(value, str):
        raw = value.split(",")
    elif isinstance(value, (list, tuple)):
        raw = []
        for item in value:
            raw.extend(str(item).split(","))
    else:
        raise exc(f"{option} must be a comma-separated string, or a list or tuple of strings")
    names = list(dict.fromkeys(n.strip() for n in raw if n and n.strip()))
    if not names:
        raise exc(f"{option} contains no names")
    return names


def require_identifier(value, option: str, exc=ValueError) -> str:
    """Accept only a plain SOQL field path (letters, digits, underscore, dot)."""
    text = str(value).strip()
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*(\.[A-Za-z][A-Za-z0-9_]*)*", text):
        raise exc(f"{option} must be a field name, got {value!r}")
    return text


def positive_int(value, option: str, exc=ValueError) -> int:
    """Parse a LIMIT value; reject anything but a positive integer."""
    try:
        number = int(str(value).strip())
    except ValueError:
        number = 0
    if number <= 0:
        raise exc(f"{option} must be a positive integer, got {value!r}")
    return number


def project_api_version(project_config, error_cls=ValueError, default: Optional[str] = None) -> str:
    """The project's API version (`project.package.api_version`) as bare text, e.g. `68.0`.

    Not `org_config.api_version`: OrgConfig has no such attribute (BaseConfig.__getattr__ warns on every
    read and raises AssertionError under CumulusCI STRICT_GETATTR, which `getattr(..., None)` does not catch).
    When the project sets none, return `default` if given, else raise `error_cls`.
    """
    version = getattr(project_config, "project__package__api_version", None)
    text = str(version).strip().lstrip("v") if version else ""
    if text:
        return text
    if default is not None:
        return default
    raise error_cls("No API version: set project.package.api_version in cumulusci.yml")
