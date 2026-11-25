"""
Deploy the repo's expression sets, then read back which version each one executes.

``activate_and_deploy_expression_sets`` deploys ``force-app/.../expressionSetDefinition``
with the tracked Draft versions flipped to Active. A successful deploy does not prove
the deployed version is the one pricing runs:

- **A version chain.** An org can hold several versions of one definition, several of
  them active. The runtime runs one of them: the highest ``Rank`` among enabled
  versions whose date windows overlap, and among null Ranks the earliest created
  (``scripts/expression_sets/_guards.executing_version``, measured on 264). In an
  upgraded org (``ramp264``: v1 to v4, three active) the repo's
  ``_V1`` deploys and changes no price (todo packs 172, 175).
- **A VersionNumber mismatch.** The Metadata API deploy handler matches payload
  versions to org versions by VersionNumber, and its code path suggests a payload
  version whose DeveloperName exists in the org under another VersionNumber can be
  skipped silently [Platform behaviour, traced]. The one construction measured (264,
  2026-11-24: the lower version deleted, ``_V1`` redeployed at the freed number)
  failed the deploy loudly instead ("We couldn't find a record with the ID …
  (ExpressionSetDefinitionVersion)").

So after the deploy this task reads every deployed procedure's ExpressionSetVersion
rows and checks, for each version the deploy sent:

- a version with that ApiName exists, under the deployed VersionNumber (reports any
  VersionNumber mismatch, silent or not);
- when the deploy activates it, it is active and it is the executing version
  (catches the version chain).

**What "deployed" means.** The expected versions are read from the package this task
actually built and sent — after ``sf project convert source`` (which honours
``.forceignore``: ``Salesforce_Pricing_Discovery_Procedure`` is in the repo but
ignored, so it is never deployed) and after the task's ``transforms`` (which flip
Draft to Active). Nothing here re-implements either.

``version_check`` decides what a finding does. ``fail`` (the default) fails the task:
a deployed change that pricing does not run produces plausible prices with no other
signal, so the build is stopped at the step that found it. The deploy has already
been applied by then, and re-running this step on a built org is refused by the
platform (measured), so the remedy is to run the build's remaining steps after this one,
in order (``cci flow info prepare_rlm_org`` lists them; a build-harness ``resume``
restarts at the failed step, so it would re-run it) and, if
the wrong version executes, edit or re-rank the executing version
(``scripts/expression_sets/set_step_formula.py`` for formulas). ``warn`` logs the same
findings and lets the build go on; set it for future builds on an org whose version
chain is known and accepted.
"""
import base64
import io
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Dict, List, Optional

try:
    from cumulusci.tasks.salesforce import Deploy
    from cumulusci.core.exceptions import CumulusCIFailure, TaskOptionsError
    from simple_salesforce import Salesforce
except ImportError:
    Deploy = object
    Salesforce = None

    class CumulusCIFailure(Exception):
        pass

    class TaskOptionsError(Exception):
        pass

# Bootstrap the repo root so the stdlib-only shared resolver imports when CCI loads
# this task module (same pattern as tasks/rlm_ux_assembly.py).
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.expression_sets._guards import (  # noqa: E402
    VERSION_FIELDS,
    executing_version,
    rank_order_warning,
    version_rows,
)

# The last line of every read-back failure. The build harness classifies a failed
# step by one line of its output (scripts/build_harness/harness/failure.py: the
# last line with an error keyword) and retries "transient" and "unknown" ones,
# which here would re-run a deploy the platform refuses on a built org. This line
# has a deterministic token ("validation error") and no transient one, and is short
# enough not to wrap, so the step is never retried whatever the message above it
# says (a read-back error can quote "timed out" or "503").
READBACK_FAILURE_SIGNATURE = "Expression set read-back failed: validation error."
MDAPI_SUFFIX = ".expressionSetDefinition"
_MD_NS = "{http://soap.sforce.com/2006/04/metadata}"
VERSION_CHECK_MODES = ("fail", "warn")
_ACTIVE = "Active"


def version_check_mode(value) -> str:
    """Parse the ``version_check`` option: ``fail`` (default) or ``warn``."""
    mode = str(value or "fail").strip().lower()
    if mode not in VERSION_CHECK_MODES:
        raise TaskOptionsError(
            f"version_check must be one of {', '.join(VERSION_CHECK_MODES)}; got {value!r}."
        )
    return mode


def versions_from_xml(definition: str, xml_bytes: bytes) -> List[Dict]:
    """One dict per ``<versions>`` entry of an expressionSetDefinition XML:
    ``{"definition", "apiName", "versionNumber", "status"}``. Raises ValueError on
    XML it cannot parse."""
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        raise ValueError(f"Could not parse {definition}: {exc}") from exc
    out = []
    for version in root.findall(f"{_MD_NS}versions"):
        number = (version.findtext(f"{_MD_NS}versionNumber") or "").strip()
        out.append({
            "definition": definition,
            "apiName": version.findtext(f"{_MD_NS}fullName"),
            "versionNumber": int(number) if number.isdigit() else None,
            "status": (version.findtext(f"{_MD_NS}status") or "").strip(),
        })
    return out


def deployed_versions(package_zip_b64: Optional[str]) -> List[Dict]:
    """The expression set versions in the package the deploy sent.

    ``package_zip_b64`` is the base64 Metadata API zip ``Deploy._get_package_zip``
    built, already converted from source format (``.forceignore`` applied) and
    transformed. Each ``expressionSetDefinitions/<Name>.expressionSetDefinition``
    member contributes its ``<versions>``; the status is the deployed one.
    """
    if not package_zip_b64:
        return []
    out: List[Dict] = []
    with zipfile.ZipFile(io.BytesIO(base64.b64decode(package_zip_b64))) as zf:
        for name in sorted(zf.namelist()):
            leaf = name.rsplit("/", 1)[-1]
            if not leaf.endswith(MDAPI_SUFFIX):
                continue
            definition = leaf[: -len(MDAPI_SUFFIX)]
            out.extend(v for v in versions_from_xml(definition, zf.read(name))
                       if v.get("apiName"))
    return out


def version_findings(expected: List[Dict], org_versions: Dict[str, List[Dict]],
                     now=None) -> List[str]:
    """Compare what the deploy sent with the org's ExpressionSetVersion rows.

    ``org_versions`` maps a definition DeveloperName to its rows (the
    ``_guards.VERSION_FIELDS``). Returns one message per problem; an empty list means
    every deployed version exists under its VersionNumber and every version the
    deploy activated is the executing one. Pure.
    """
    findings: List[str] = []
    for version in expected:
        definition, api_name = version["definition"], version["apiName"]
        rows = org_versions.get(definition) or []
        table = version_rows(rows) or "(none)"
        match = [r for r in rows if r.get("ApiName") == api_name]
        if not match:
            findings.append(
                f"{definition}: no ExpressionSetVersion named {api_name} after the deploy. "
                f"Versions in the org: {table}."
            )
            continue
        row = match[0]
        if version.get("versionNumber") is not None and \
                row.get("VersionNumber") != version["versionNumber"]:
            findings.append(
                f"{definition}: {api_name} is VersionNumber {row.get('VersionNumber')} in "
                f"the org but {version['versionNumber']} in the deployed package; the "
                "deploy matches versions by VersionNumber, so the repo's change may not "
                f"have reached this version. Versions in the org: {table}."
            )
            continue
        if version.get("status") != _ACTIVE:
            continue
        if not row.get("IsActive"):
            findings.append(
                f"{definition}: {api_name} was deployed Active but is inactive. "
                f"Versions in the org: {table}."
            )
            continue
        running = executing_version(rows, now)
        if running is None or running.get("ApiName") != api_name:
            runs = (f"{running.get('ApiName')} (v{running.get('VersionNumber')}) is the "
                    "executing version (highest Rank among active versions in their "
                    "date window; earliest created among null Ranks)" if running else
                    f"{api_name}'s date window does not cover now, so it is not running")
            findings.append(
                f"{definition}: the deployed {api_name} is active but does not execute; "
                f"{runs}, so pricing runs it and the repo change has no effect. "
                f"Versions in the org: {table}. Edit or re-rank the executing version "
                "(scripts/expression_sets/set_step_formula.py for formulas)."
            )
    return findings


class DeployExpressionSets(Deploy):
    """Deploy expression sets, then fail (or warn) when a deployed version is not the one that executes."""

    task_options = {
        **getattr(Deploy, "task_options", {}),
        "version_check": {
            "description": (
                "What a post-deploy version finding does: 'fail' (default) fails the "
                "task, 'warn' logs it and continues. A finding is a deployed version "
                "that is missing, under a different VersionNumber than deployed, "
                "inactive when the deploy activates it, or not the version that "
                "executes (highest Rank among active versions in their date window; "
                "earliest created among null Ranks). Set warn for future builds on an "
                "org whose version chain is known and accepted."
            ),
            "required": False,
        },
    }

    def _init_options(self, kwargs):
        super()._init_options(kwargs)
        self.version_check = version_check_mode(self.options.get("version_check"))

    def _get_package_zip(self, path):
        # Keep the exact package sent (converted with .forceignore applied, then
        # transformed), so the read-back expects only what was deployed.
        package_zip = super()._get_package_zip(path)
        self._deployed_package = package_zip if isinstance(package_zip, str) else None
        return package_zip

    def _run_task(self):
        self._deployed_package = None
        result = super()._run_task()
        if getattr(self, "check_only", False):
            self.logger.info("check_only deploy; skipping the version read-back.")
            return result
        self._check_versions()
        return result

    def _check_versions(self):
        expected = deployed_versions(getattr(self, "_deployed_package", None))
        if not expected:
            self.logger.info("No expression set versions were deployed; nothing to read back.")
            return
        definitions = sorted({v["definition"] for v in expected})
        try:
            org_versions = self._org_versions(definitions)
            findings = version_findings(expected, org_versions)
            notes = {d: rank_order_warning(org_versions.get(d) or []) for d in definitions}
        except Exception as exc:  # noqa: BLE001 — a query or an unreadable version date
            # The read-back could not run: same fail/warn decision as a finding, so
            # warn mode never fails the build on the check itself.
            self._conclude([f"Version read-back could not run: {exc}"],
                           "The version read-back could not run; the deployed change "
                           "is unverified.")
            return
        for definition, note in notes.items():
            if note:
                self.logger.warning(f"{definition}: {note}")
        if not findings:
            self.logger.info(
                f"Version read-back: all {len(expected)} deployed version(s) exist under "
                "their deployed VersionNumber, and each one the deploy activated is the "
                "version that executes."
            )
            return
        self._conclude(findings, (
            f"{len(findings)} expression set version finding(s) after the deploy; the "
            "deployed change may not be what pricing runs."
        ))

    def _conclude(self, findings: List[str], message: str) -> None:
        """Log ``findings``, then fail (``version_check: fail``) or warn and go on."""
        log = self.logger.error if self.version_check == "fail" else self.logger.warning
        for finding in findings:
            log(finding)
        if self.version_check == "fail":
            raise CumulusCIFailure(
                message + " The deploy has already been applied, and re-running this "
                "step on a built org is refused by the platform, so do not re-run it "
                "(a build-harness resume restarts at the failed step, so it would re-run "
                "it too): run the prepare_rlm_org steps after this one, in order (cci "
                "flow info prepare_rlm_org lists them), and if the wrong "
                "version executes, edit or re-rank the executing version "
                "(scripts/expression_sets/set_step_formula.py for formulas). "
                "version_check warn is for future builds on an org whose version chain "
                "is known (cci flow run prepare_rlm_org -o "
                "activate_and_deploy_expression_sets__version_check warn).\n"
                + READBACK_FAILURE_SIGNATURE
            )
        self.logger.warning(message + " Continuing (version_check: warn).")

    def _org_versions(self, definitions: List[str]) -> Dict[str, List[Dict]]:
        """``{definition DeveloperName: [ExpressionSetVersion rows]}``, two queries."""
        names = "', '".join(d.replace("\\", "\\\\").replace("'", "\\'") for d in definitions)
        sets = self._sf.query_all(
            "SELECT Id, ExpressionSetDefinition.DeveloperName FROM ExpressionSet "
            f"WHERE ExpressionSetDefinition.DeveloperName IN ('{names}')"
        ).get("records", [])
        by_set = {
            r["Id"]: (r.get("ExpressionSetDefinition") or {}).get("DeveloperName")
            for r in sets
        }
        out: Dict[str, List[Dict]] = {d: [] for d in definitions}
        if not by_set:
            return out
        ids = "', '".join(by_set)
        rows = self._sf.query_all(
            f"SELECT {VERSION_FIELDS}, ExpressionSetId "
            f"FROM ExpressionSetVersion WHERE ExpressionSetId IN ('{ids}')"
        ).get("records", [])
        for row in rows:
            definition = by_set.get(row.get("ExpressionSetId"))
            if definition in out:
                out[definition].append(row)
        return out

    @property
    def _sf(self):
        """A Salesforce client on the project's API version, built once per run.

        ``org_config.salesforce_client`` follows the org's newest API version, which
        drifts once an org is upgraded ahead of the project (same as
        DeactivateChangedDecisionTables._sf).
        """
        if getattr(self, "_sf_client", None) is None:
            api_version = self.project_config.project__package__api_version
            if not api_version or Salesforce is None:
                self._sf_client = self.org_config.salesforce_client
            else:
                self._sf_client = Salesforce(
                    instance=self.org_config.instance_url.replace("https://", ""),
                    session_id=self.org_config.access_token,
                    version=api_version,
                )
        return self._sf_client
