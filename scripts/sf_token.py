#!/usr/bin/env python3
"""Org instance URL and access token from the sf CLI, without SF_TEMP_SHOW_SECRETS.

Since sf 2.145 (forcedotcom/cli#3560), ``sf org display --json`` redacts
``result.accessToken`` to a placeholder unless ``SF_TEMP_SHOW_SECRETS=true`` is
set. :func:`org_auth` takes the instance URL from ``sf org display`` and, when
the token it returns is not a real one, fetches it with
``sf org auth show-access-token --json``, which sf never redacts. Scripts that
call Salesforce REST directly use this so they keep working once the variable is
gone. (CumulusCI still needs the variable for its own scratch-org token reads.)

A real token starts with the org's ``00D`` Id prefix. Matching that, rather than
the placeholder wording, keeps the check stable if sf changes its text. The same
rule is in ``robot/rlm-base/resources/SalesforceAPI.py``.

The token is never logged, printed, or put in an exception message, and a JSON
decode error from a command whose stdout may hold the token is never chained.

Stdlib only, so any script can import it after putting ``scripts/`` on
``sys.path``::

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from sf_token import org_auth
"""

import json
import subprocess
from typing import Tuple

_REAL_TOKEN_PREFIX = "00D"
DEFAULT_TIMEOUT = 60


class SfTokenError(RuntimeError):
    """The sf CLI could not provide an instance URL or a usable access token."""


def looks_like_a_real_token(token) -> bool:
    return isinstance(token, str) and token.startswith(_REAL_TOKEN_PREFIX)


def _run_json(args, alias: str, timeout: int) -> dict:
    """Run ``sf <args> --json`` and return the parsed ``result`` object."""
    label = "sf " + " ".join(args)
    try:
        proc = subprocess.run(
            ["sf", *args, "--json"], capture_output=True, text=True, timeout=timeout
        )
    except subprocess.TimeoutExpired as exc:
        raise SfTokenError(
            f"{label} timed out after {timeout} seconds for org '{alias}'."
        ) from exc
    if proc.returncode != 0:
        # A failed call's output is diagnostic (auth or usage errors) and holds
        # no token, so it is safe to surface.
        detail = (proc.stderr or proc.stdout or "").strip()
        raise SfTokenError(
            f"{label} failed for org '{alias}' (rc={proc.returncode}): {detail[:500]}"
        )
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        # `from None`: the decode error keeps the raw stdout in `.doc`.
        raise SfTokenError(f"{label} returned non-JSON output for org '{alias}'.") from None
    return data.get("result") or {}


def org_auth(alias: str, timeout: int = DEFAULT_TIMEOUT) -> Tuple[str, str]:
    """Return ``(instance_url, access_token)`` for an sf CLI alias or username."""
    if not alias:
        raise SfTokenError("An sf org alias or username is required.")
    info = _run_json(["org", "display", "--target-org", alias], alias, timeout)
    instance_url = (info.get("instanceUrl") or "").rstrip("/")
    if not instance_url:
        raise SfTokenError(f"sf org display did not return instanceUrl for org '{alias}'.")
    token = info.get("accessToken")
    if not looks_like_a_real_token(token):
        token = _run_json(
            ["org", "auth", "show-access-token", "--target-org", alias], alias, timeout
        ).get("accessToken")
        if not looks_like_a_real_token(token):
            raise SfTokenError(
                f"sf org auth show-access-token did not return a usable access "
                f"token for org '{alias}'."
            )
    return instance_url, token
