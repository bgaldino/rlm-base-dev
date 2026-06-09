"""
CumulusCI task to repair scratch-org identity in the local Salesforce CLI auth file.

Works around an SF CLI v2.x bug where Enterprise-Edition ("ent"/workspace)
scratch orgs created via the DevHub API are written to the local auth file
(``~/.sfdx/<username>.json``) with ``isScratch: false`` even though they are real
scratch orgs (valid ``devHubUsername``, present in ``sf org list`` scratchOrgs).
The SF CLI then rejects scratch-only commands against them with
NonScratchOrgError, e.g.:

* ``sf org create user``        (this repo: the create_persona_user task)
* ``sf org generate password``  (a developer running it manually)

This task reads the org's auth file(s), and when ``isScratch`` is false/missing
*but* a ``devHubUsername`` is present (i.e. it really is a scratch org), flips
``isScratch`` to true and writes the file back atomically (preserving 0600
permissions). It is idempotent (a no-op when the flag is already correct) and
non-fatal by default (warns and continues), so it is safe to run as the first
step of a build flow or standalone.

Usage:
    In cumulusci.yml (as the first step of prepare_core, gated on scratch):
        fix_scratch_org_identity:
            class_path: tasks.rlm_fix_scratch_identity.FixScratchOrgIdentity

    Command line (one-off repair before `sf org create user` etc.):
        cci task run fix_scratch_org_identity --org ent-r1
"""
import glob
import json
import os
import tempfile
from pathlib import Path

try:
    from cumulusci.core.tasks import BaseTask
    from cumulusci.core.exceptions import TaskOptionsError
except ImportError:
    BaseTask = object
    TaskOptionsError = Exception


class FixScratchOrgIdentity(BaseTask):
    """Ensure a CCI-created scratch org is marked ``isScratch: true`` locally.

    Safe and idempotent: only flips ``false -> true`` when the auth file has a
    ``devHubUsername`` and is not itself a DevHub or sandbox. Never flips
    ``true -> false``. Non-fatal by default.
    """

    task_options = {
        "raise_on_failure": {
            "description": (
                "Raise if no auth file is found or a file cannot be read/written. "
                "Defaults to False (warn and continue) so a healthy build is never "
                "broken by this best-effort repair."
            ),
            "required": False,
            "type": bool,
        },
    }

    def _run_task(self):
        if not getattr(self, "org_config", None):
            self._fail_or_warn("No org config available; nothing to repair.")
            return

        # CCI's own scratch flag is independent of the CLI's isScratch flag.
        # If CCI doesn't consider this a scratch org, do nothing (the flow gate
        # should already prevent this, but guard defensively).
        if not getattr(self.org_config, "scratch", False):
            self.logger.info(
                "Org is not a CCI scratch org (org_config.scratch is false); "
                "skipping scratch-identity repair."
            )
            return

        username = getattr(self.org_config, "username", None)
        if not username:
            self._fail_or_warn("Org config has no username; cannot locate auth file.")
            return

        auth_files = self._find_auth_files(username)
        if not auth_files:
            self._fail_or_warn(
                f"No local SF CLI auth file found for {username} "
                f"(looked in ~/.sfdx and ~/.sf)."
            )
            return

        patched, errors = 0, 0
        for path in auth_files:
            try:
                if self._repair_file(path):
                    patched += 1
            except Exception as exc:  # noqa: BLE001 - report per-file, keep going
                errors += 1
                # _fail_or_warn raises when raise_on_failure is set; otherwise
                # warns so an unreadable auth file is never swallowed silently.
                self._fail_or_warn(f"Could not process auth file {path}: {exc}")

        if errors:
            # Errors were already warned per-file above; make the summary reflect
            # them too, even when some files were patched, so a partial repair is
            # never mistaken for a full one.
            if patched:
                self.logger.warning(
                    f"Scratch-org identity PARTIALLY repaired for {username}: "
                    f"set isScratch=true in {patched} file(s), but {errors} "
                    f"file(s) could not be processed (see warnings above)."
                )
            else:
                self.logger.warning(
                    f"Scratch-org identity NOT verified for {username}: "
                    f"{errors} auth file(s) could not be processed (see warnings above)."
                )
        elif patched:
            self.logger.info(
                f"Scratch-org identity repaired: set isScratch=true in "
                f"{patched} auth file(s) for {username}."
            )
        else:
            self.logger.info(
                f"Scratch-org identity already correct for {username}; no changes made."
            )

    # ------------------------------------------------------------------
    # Auth-file discovery
    # ------------------------------------------------------------------

    def _find_auth_files(self, username):
        """Return existing auth files for ``username`` in ~/.sfdx and ~/.sf.

        The legacy ``~/.sfdx/<username>.json`` is the primary location the SF
        CLI's StateAggregator reads. ``~/.sf`` is scanned defensively in case a
        newer CLI version stores a per-org auth file there too.
        """
        home = Path.home()
        candidates = [home / ".sfdx" / f"{username}.json"]
        sf_dir = home / ".sf"
        if sf_dir.is_dir():
            candidates += [
                Path(p)
                for p in glob.glob(str(sf_dir / "**" / f"{username}.json"), recursive=True)
            ]
        # De-dupe while preserving order; keep only files that exist.
        seen, found = set(), []
        for path in candidates:
            rp = str(path)
            if rp in seen:
                continue
            seen.add(rp)
            if path.is_file():
                found.append(path)
        return found

    # ------------------------------------------------------------------
    # Per-file repair
    # ------------------------------------------------------------------

    def _repair_file(self, path):
        """Patch a single auth file. Returns True if it was changed.

        Raises on an unreadable / non-JSON / non-object auth file so the caller
        can surface it (warn, or raise when raise_on_failure is set) instead of
        silently reporting "already correct" when the repair never actually ran.
        """
        try:
            raw = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            raise RuntimeError(f"cannot read auth file: {exc}") from exc
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"auth file is not valid JSON: {exc}") from exc
        if not isinstance(data, dict):
            raise RuntimeError("auth file is not a JSON object")

        if data.get("isScratch") is True:
            self.logger.debug(f"{path}: isScratch already true.")
            return False

        # Only flip when this really looks like a scratch org. A scratch org has
        # a DevHub and is neither a DevHub nor a sandbox itself.
        if not data.get("devHubUsername"):
            self.logger.warning(
                f"{path}: isScratch is not true but no devHubUsername is present; "
                "leaving it unchanged (does not look like a scratch org)."
            )
            return False
        if data.get("isDevHub") or data.get("isSandbox"):
            self.logger.warning(
                f"{path}: looks like a DevHub/sandbox, not a scratch org; "
                "leaving isScratch unchanged."
            )
            return False

        previous = data.get("isScratch")
        data["isScratch"] = True
        self._atomic_write(path, data)
        self.logger.info(
            f"{path}: isScratch {previous!r} -> True "
            f"(devHubUsername={data.get('devHubUsername')})."
        )
        return True

    @staticmethod
    def _atomic_write(path, data):
        """Write JSON to ``path`` atomically with 0600 (owner-only) permissions.

        Auth files hold credentials, so the result is forced to exactly 0600
        (owner read/write — no group/other access and no execute bit)
        regardless of the file's prior (possibly lax, e.g. 0644 or 0700) mode.
        """
        # Force exactly 0600; never carry over the prior mode for a creds file.
        mode = 0o600
        directory = os.path.dirname(str(path)) or "."
        fd, tmp = tempfile.mkstemp(prefix=".rlm_auth_", dir=directory)
        try:
            os.fchmod(fd, mode)
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2)
                fh.write("\n")
            os.replace(tmp, str(path))
        except BaseException:
            # Clean up the temp file on any failure; never leave a stray.
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise

    # ------------------------------------------------------------------
    # Error handling
    # ------------------------------------------------------------------

    def _fail_or_warn(self, message):
        if self.options.get("raise_on_failure"):
            raise TaskOptionsError(message)
        self.logger.warning(message)
