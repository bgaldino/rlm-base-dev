"""
Deploy the repo's expression sets, then read back which version each one executes.

``activate_and_deploy_expression_sets`` deploys ``force-app/.../expressionSetDefinition``
with the tracked Draft versions flipped to Active. A successful deploy does not prove
the deployed version is the one pricing runs, for two reasons, both silent:

- **A version chain.** An org can hold several versions of one definition, several of
  them active, and the runtime executes the highest-numbered ACTIVE one. In an upgraded
  org (``ramp264``: v1 to v4, three active) the repo's ``_V1`` deploys and changes no
  price (todo packs 172, 175).
- **A no-op deploy.** The Metadata API deploy handler matches payload versions to org
  versions by VersionNumber. A payload version whose DeveloperName exists in the org
  under a different VersionNumber is neither updated nor inserted, and the deploy still
  succeeds (read from the Core deploy handler; not yet reproduced live).

So after the deploy this task reads every repo procedure's ExpressionSetVersion rows
and checks, for each version the repo deploys:

- a version with that ApiName exists, under the repo's VersionNumber (catches the
  no-op);
- when the deploy activates it, it is active and it is the highest-numbered active
  version, so it is the one that executes (catches the version chain).

``version_check`` decides what a finding does. ``fail`` (the default) fails the task:
a deploy that changed nothing, or changed a version that does not run, produces
plausible prices with no other signal, so the build is stopped at the step that caused
it. ``warn`` logs the same findings and lets the build go on, for an org whose foreign
version chain is known and accepted (edit the executing version with
``scripts/expression_sets/set_step_formula.py``).
"""
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Iterable, List, Optional

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


DEFINITION_SUFFIX = ".expressionSetDefinition-meta.xml"
_MD_NS = "{http://soap.sforce.com/2006/04/metadata}"
VERSION_CHECK_MODES = ("fail", "warn")

# The status the deploy leaves a version in. A version whose source status is Draft
# deploys as Active when the task's transforms flip it (see draft_deploys_active).
_ACTIVE = "Active"


def repo_versions(path: Path) -> List[Dict]:
    """The versions the repo deploys from ``path``: one dict per ``<versions>`` entry.

    ``{"definition", "apiName", "versionNumber", "status", "file"}``; the definition
    name is the file name (source format carries no top-level fullName). Pure apart
    from reading the files; raises ValueError on a file it cannot parse.
    """
    out: List[Dict] = []
    if not path.is_dir():
        return out
    for file in sorted(path.glob(f"*{DEFINITION_SUFFIX}")):
        definition = file.name[: -len(DEFINITION_SUFFIX)]
        try:
            root = ET.parse(file).getroot()
        except ET.ParseError as exc:
            raise ValueError(f"Could not parse {file}: {exc}") from exc
        for version in root.findall(f"{_MD_NS}versions"):
            number = version.findtext(f"{_MD_NS}versionNumber")
            out.append({
                "definition": definition,
                "apiName": version.findtext(f"{_MD_NS}fullName"),
                "versionNumber": int(number) if number and number.strip().isdigit() else None,
                "status": (version.findtext(f"{_MD_NS}status") or "").strip(),
                "file": file.name,
            })
    return out


def draft_deploys_active(transforms: Optional[Iterable]) -> bool:
    """Whether the task's ``transforms`` turn a Draft version status into Active.

    ``activate_and_deploy_expression_sets`` carries a ``find_replace`` pattern on
    ``versions/status[text()="Draft"]`` replacing it with ``Active``; that is the
    "activate" in its name. Reading the option rather than assuming it keeps the
    check honest if the transform is ever removed. Pure.
    """
    for transform in transforms or []:
        if not isinstance(transform, dict) or transform.get("transform") != "find_replace":
            continue
        for pattern in (transform.get("options") or {}).get("patterns") or []:
            xpath = str(pattern.get("xpath") or "")
            if ("versions/status" in xpath and '"Draft"' in xpath
                    and pattern.get("replace") == _ACTIVE):
                return True
    return False


def expected_active(version: Dict, draft_active: bool) -> bool:
    """Whether the deploy leaves ``version`` active. Pure."""
    status = version.get("status")
    return status == _ACTIVE or (status == "Draft" and draft_active)


def version_findings(
    expected: List[Dict], org_versions: Dict[str, List[Dict]], draft_active: bool
) -> List[str]:
    """Compare what the repo deployed with the org's ExpressionSetVersion rows.

    ``org_versions`` maps a definition DeveloperName to its rows
    (``ApiName``, ``VersionNumber``, ``IsActive``). Returns one message per problem;
    an empty list means every deployed version exists under its VersionNumber and
    every version the deploy activates is the one that executes. Pure.
    """
    findings: List[str] = []
    for version in expected:
        definition, api_name = version["definition"], version["apiName"]
        rows = org_versions.get(definition) or []
        table = ", ".join(
            f"{r.get('ApiName')} v{r.get('VersionNumber')}"
            f"{' active' if r.get('IsActive') else ''}"
            for r in sorted(rows, key=lambda r: r.get("VersionNumber") or 0)
        ) or "(none)"
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
                f"the org but {version['versionNumber']} in the repo. The deploy matches "
                "versions by VersionNumber, so it did not update this version (a silent "
                f"no-op). Versions in the org: {table}."
            )
            continue
        if not expected_active(version, draft_active):
            continue
        if not row.get("IsActive"):
            findings.append(
                f"{definition}: {api_name} should be active after the deploy but is "
                f"inactive. Versions in the org: {table}."
            )
            continue
        active = [r for r in rows if r.get("IsActive")]
        running = max(active, key=lambda r: r.get("VersionNumber") or 0)
        if running.get("ApiName") != api_name:
            findings.append(
                f"{definition}: the deployed {api_name} is active but does not execute; "
                f"{running.get('ApiName')} (v{running.get('VersionNumber')}) is the "
                "highest-numbered active version, so pricing runs it and the repo change "
                f"has no effect. Versions in the org: {table}. Edit the executing version "
                "with scripts/expression_sets/set_step_formula.py, or set version_check "
                "to warn if this org's version chain is intended."
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
                "that is missing, under a different VersionNumber (a silent no-op), "
                "inactive when the deploy activates it, or not the highest-numbered "
                "active version (so not the one that executes)."
            ),
            "required": False,
        },
    }

    def _init_options(self, kwargs):
        super()._init_options(kwargs)
        mode = str(self.options.get("version_check") or "fail").strip().lower()
        if mode not in VERSION_CHECK_MODES:
            raise TaskOptionsError(
                f"version_check must be one of {', '.join(VERSION_CHECK_MODES)}; got {mode!r}."
            )
        self.version_check = mode

    def _run_task(self):
        result = super()._run_task()
        if getattr(self, "check_only", False):
            self.logger.info("check_only deploy; skipping the version read-back.")
            return result
        self._check_versions()
        return result

    def _check_versions(self):
        path = Path(self.options["path"])
        expected = [v for v in repo_versions(path) if v.get("apiName")]
        if not expected:
            self.logger.info(f"No expression set versions under {path}; nothing to read back.")
            return
        draft_active = draft_deploys_active(self.options.get("transforms"))
        definitions = sorted({v["definition"] for v in expected})
        findings = version_findings(expected, self._org_versions(definitions), draft_active)
        if not findings:
            self.logger.info(
                f"Version read-back: all {len(expected)} deployed version(s) exist under "
                "their repo VersionNumber, and each one the deploy activates is the "
                "version that executes."
            )
            return
        log = self.logger.error if self.version_check == "fail" else self.logger.warning
        for finding in findings:
            log(finding)
        message = (
            f"{len(findings)} expression set version finding(s) after the deploy; the "
            "deployed change may not be what pricing runs."
        )
        if self.version_check == "fail":
            raise CumulusCIFailure(
                message + " Set -o version_check warn to continue anyway."
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
            "SELECT Id, ApiName, VersionNumber, IsActive, ExpressionSetId "
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
