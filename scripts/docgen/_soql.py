"""Shared SOQL utilities for docgen helper scripts."""


def soql_escape(value):
    """Escape a string value for safe interpolation into a SOQL WHERE clause.

    Handles single quotes (the primary injection vector in SOQL), backslashes and line breaks.
    Use for Name/Id values in queries — NOT for constructing arbitrary SOQL.
    """
    if not isinstance(value, str):
        return str(value)
    text = value.replace("\\", "\\\\").replace("'", "\\'")
    return text.replace("\n", "\\n").replace("\r", "\\r")


def soql_like_prefix(value):
    """A quoted LIKE literal matching values that start with `value`: its `_` and `%` match themselves.

    Same rule and shape as tasks.soql_utils.soql_like_prefix (measured live): `\\_`/`\\%` are the LIKE escapes
    in the literal, and a backslash keeps the ordinary literal escape.
    """
    return "'" + "".join("\\" + char if char in "_%" else soql_escape(char) for char in str(value)) + "%'"
