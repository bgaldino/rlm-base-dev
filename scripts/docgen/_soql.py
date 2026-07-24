"""Shared SOQL utilities for docgen helper scripts."""


def soql_escape(value):
    """Escape a string value for safe interpolation into a SOQL WHERE clause.

    Handles single quotes (the primary injection vector in SOQL) and backslashes.
    Use for Name/Id values in queries — NOT for constructing arbitrary SOQL.
    """
    if not isinstance(value, str):
        return str(value)
    return value.replace("\\", "\\\\").replace("'", "\\'")
