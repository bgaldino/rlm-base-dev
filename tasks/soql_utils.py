"""Small helpers shared by the management tasks that build SOQL strings."""
import re
from typing import List


def soql_quote(value) -> str:
    """Return `value` as a single-quoted SOQL string literal, escaped."""
    text = str(value).replace("\\", "\\\\").replace("'", "\\'")
    text = text.replace("\n", "\\n").replace("\r", "\\r")
    return f"'{text}'"


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
        raise exc(f"{option} must be a comma-separated string or a list of strings")
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
