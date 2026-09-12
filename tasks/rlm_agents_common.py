"""Shared helpers for the Agentforce publish/activate CCI tasks.

``publish_agents`` and ``activate_agents`` both discover agents from disk and
invoke an ``sf agent ...`` subcommand with ``--json``, then interpret the
standard Salesforce CLI JSON envelope (``{status, result, warnings}``) the
same way. This module holds that common logic so the two task classes stay in
sync — in particular they share a single success contract (top-level
``status == 0``), removing the divergence where one task checked ``status``
and the other checked ``result.success``.
"""
import json
import subprocess

try:
    from cumulusci.core.exceptions import CommandException
except ImportError:
    CommandException = Exception


# Bundles present on disk but deliberately excluded from *compilation* — i.e.
# from ``publish_agents`` and ``activate_agents``.
# See todo pack 187: on v68/264, ``RLM_Revenue_Quote_Management``'s
# ``Configure_Product_Attributes`` action has five currency output params that
# ``sf agent publish`` no longer accepts as scalars, aborting ``prepare_agents``.
# The bundle is a standard agent template that changed 262→264 and has not yet
# been recaptured, so it is omitted rather than hand-patched. The source stays
# on disk (and is still deployed by ``deploy_agents``, which does not compile)
# as the capture target — remove the entry once the 264 template is captured and
# reintroduced.
#
# The exclusion is *operation-specific*, not applied at every call site.
# ``publish_agents``/``activate_agents`` skip the bundle (default), so nothing
# tries to compile or activate it. ``deactivate_agents`` deliberately keeps it
# (``include_excluded=True``): on a 262→264 *upgraded* org the old BotVersion may
# already be published and active, and skipping it there would leave it active
# indefinitely. Deactivation of a missing/inactive agent is a no-op, so including
# it is safe on a fresh org too. (``test_agents`` does not discover from disk; it
# maps a static suite list and never referenced this bundle. Its permission set's
# ``<agentAccesses>`` binding is separately removed in
# unpackaged/post_agents/permissionsets, since that deploys via a directory
# Deploy rather than this filter.)
EXCLUDED_BUNDLES = frozenset({"RLM_Revenue_Quote_Management"})


def discover_agent_bundles(bundles_root, *, include_excluded=False):
    """Return the sorted directory names under ``bundles_root`` (each is an
    agent api-name), or ``[]`` if the directory does not exist.

    By default, names in ``EXCLUDED_BUNDLES`` are omitted — the contract for
    the compiling operations (``publish_agents``, ``activate_agents``). Pass
    ``include_excluded=True`` for ``deactivate_agents``, which must be able to
    deactivate a bundle that was excluded from publish but may still be active
    from a prior (e.g. 262→264 upgraded) org; deactivating a missing/inactive
    agent is a no-op.

    The directory name is the agent api-name for both ``sf agent publish
    authoring-bundle --api-name`` and ``sf agent activate --api-name``; the
    repo keeps it in lockstep with the bundle's ``developer_name`` and the
    permission set ``<agentName>``.
    """
    if not bundles_root.is_dir():
        return []
    return sorted(
        p.name
        for p in bundles_root.iterdir()
        if p.is_dir() and (include_excluded or p.name not in EXCLUDED_BUNDLES)
    )


def run_sf_json(cmd, *, timeout, label, cwd=None):
    """Run an ``sf ... --json`` command and return its parsed payload.

    Raises ``CommandException`` on timeout, a missing ``sf`` binary, a
    non-zero exit code, or a non-zero ``status`` in the JSON envelope — the
    canonical Salesforce CLI success contract. When the command exits 0 but
    emits unparseable output, the raw stdout/stderr is surfaced in the error
    message so the failure is diagnosable rather than silently swallowed.

    ``label`` is the human-readable command name used in log/error messages.
    """
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise CommandException(f"{label} timed out after {timeout}s.") from exc
    except FileNotFoundError as exc:
        raise CommandException(
            f"{label} failed: the Salesforce CLI ('sf') was not found on PATH."
        ) from exc

    payload = {}
    if result.stdout:
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError:
            pass

    if result.returncode != 0 or payload.get("status", 1) != 0:
        raise CommandException(f"{label} failed: {_failure_detail(result, payload)}")

    return payload


def _strip_cli_noise(text):
    """Drop the CLI's own update-available notice from a captured stream.

    The npm-installed CLI writes `›   Warning: @salesforce/cli update available
    from X to Y.` to **stderr**, which is not part of any error. It cost a real
    diagnosis: a `sf agent activate` failure in CI reported nothing but that
    warning, because the fallback chain reached for stderr and found the notice
    sitting where the cause should have been.
    """
    keep = []
    for line in (text or "").splitlines():
        bare = line.strip().lstrip("›").strip()
        if not bare or "update available" in bare:
            continue
        keep.append(bare)
    return " ".join(keep)


_MAX_STREAM_CHARS = 600


def _failure_detail(result, payload):
    """Build a failure description that cannot come out empty or misleading.

    Every source is reported rather than the first non-empty one, because they
    carry different halves of the story: the JSON envelope names the error
    (`name`) and explains it (`message`), while an argument or plugin-resolution
    failure never reaches JSON at all and only shows up on a raw stream. The
    exit code is always included, so a silent non-zero still says something.
    """
    parts = []
    for key in ("name", "message"):
        value = str(payload.get(key) or "").strip()
        if value and value not in parts:
            parts.append(value)
    summarized = bool(parts)
    for label, stream in (("stderr", result.stderr), ("stdout", result.stdout)):
        # stdout is suppressed only when the envelope above actually produced a
        # summary; a full JSON dump alongside a real message is noise. Keying this
        # on `payload` being non-empty was a bug of exactly the kind this function
        # exists to prevent: a JSON envelope carrying its cause somewhere other
        # than `name`/`message` -- nested under `result`, say -- contributed
        # nothing, suppressed stdout anyway, and after the update notice was
        # stripped from stderr the whole report degraded to `exit 1`.
        if label == "stdout" and summarized:
            continue
        cleaned = _strip_cli_noise(stream)
        if cleaned:
            # Truncated because the alternative to a long line here is not a short
            # line, it is no information: an envelope that parsed but hid its cause
            # is reported through this path, and those can be large.
            if len(cleaned) > _MAX_STREAM_CHARS:
                cleaned = cleaned[:_MAX_STREAM_CHARS] + "… (truncated)"
            parts.append(f"{label}: {cleaned}")
    parts.append(f"exit {result.returncode}")
    return " | ".join(parts)
