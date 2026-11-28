"""SOQL string literals for standalone scripts, escaped by one rule.

The same rule as `tasks/soql_utils.py::soql_quote`, for scripts that do not import `tasks/`
(todo 467, todo 502): a backslash, a single quote, a newline and a carriage return are escaped
with a backslash inside the quotes. The rule holds for an Apex string literal too.

Stdlib only. A script imports it with the repo root on ``sys.path``, the way other scripts
import the ``scripts`` package::

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from scripts.soql_literal import soql_quote

Named so that a bare ``import _soql`` (scripts/docgen's helper) never resolves here.
"""
import re

_RECORD_ID = re.compile(r"[A-Za-z0-9]{15}(?:[A-Za-z0-9]{3})?")


def soql_text(value) -> str:
    """`value` escaped for the inside of a single-quoted SOQL literal (backslash, quote, newline, CR)."""
    text = str(value).replace("\\", "\\\\").replace("'", "\\'")
    return text.replace("\n", "\\n").replace("\r", "\\r")


def soql_quote(value) -> str:
    """`value` as a single-quoted SOQL string literal, escaped."""
    return f"'{soql_text(value)}'"


def is_record_id(value) -> bool:
    """True for a 15- or 18-character Salesforce record Id: letters and digits only, nothing around them."""
    return isinstance(value, str) and _RECORD_ID.fullmatch(value) is not None
