"""
Expression Set structural management via the BRE Connect API.

Provides four CCI tasks:
  - ExportExpressionSet: GET full definition → JSON file
  - ApplyExpressionSetOverlay: Declarative step/variable manipulation
  - ImportExpressionSet: Full replacement from JSON file
  - DeleteExpressionSet: Delete an expression set (or just an old version)

BRE Connect API endpoint (v58.0+):
  /services/data/v{version}/connect/business-rules/expression-set/{id}
  where {id} is the ExpressionSet runtime record Id (key prefix 9QL).

Connect mutation behavior (verified live on 262 / v67.0 — see
docs/references/expression-set-connect-api-reference.md for the full reference):

  * HTML-entity normalization: the Connect GET serializer escapes JSON-in-string
    content (customElement.parameters[].value, advancedCondition.criteria[].value,
    formula text) as &quot;/&#39;. The engine rejects those entities on input
    (flat: "Syntax error. Found '&'"; nested: an opaque "Error processing JSON"),
    so every mutation HTML-unescapes the payload (_normalize_html_entities)
    immediately before the Connect call. Pass `normalize_html_entities: false`
    to send the payload as-is.
  * PATCH requires an inactive/disabled version. An enabled version rejects PATCH
    with "An enabled Expression Set Version cannot be updated/deleted." Every
    mutation runs deactivate→PATCH→reactivate. Reactivation is idempotent (see
    _set_version_active) because a PATCH body carrying enabled=true reactivates
    the version itself.
  * PATCH is NOT atomic: a failed (400) PATCH still commits the parts it
    accepted. On failure we DO NOT reactivate — a half-mutated pricing procedure
    must never be re-enabled silently. We leave it deactivated and raise loudly.
  * Version `id` differs by verb: a PATCH body KEEPS the version-level `id` (the
    server matches it in place); a POST-create body OMITS it. Top-level
    `id`/`error` are always stripped (output-only).
  * ResourceInitializationType is immutable once set, and the PATCH body must
    equal the stored ExpressionSet.ResourceInitializationType (enum Default|Off).
    GET reports "Off" even when the stored field is null (seeded procedures), so
    we align the stored field once before patching (_ensure_resource_initialization_type).
  * Version identity comes from the ExpressionSetVersion sObject (source of
    truth), not GET — GET can transiently serve a stale clone version apiName
    (_check_version_name_consistency warns on divergence).

Overlays and import payloads are schema-validated BEFORE any Connect call (see
tasks/expression_set_schema.py) so a malformed step graph fails locally with an
actionable message instead of as the opaque server response the PATCH/POST
handler can produce. The validator also WARNS when a value still
carries HTML entities (i.e. un-normalized GET output). Pass
`skip_validation: true` to bypass.
"""
import html
import json
import time
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

try:
    from cumulusci.tasks.salesforce import BaseSalesforceTask
    from cumulusci.core.tasks import BaseTask
    from cumulusci.core.exceptions import TaskOptionsError
except ImportError:
    BaseSalesforceTask = object
    BaseTask = object
    TaskOptionsError = Exception

from tasks.expression_set_schema import (
    OVERLAY_OPS,
    RESOURCE_INIT_TYPES,
    validate_definition,
    validate_overlay,
    validate_overlay_against_definition,
)


_REQUEST_TIMEOUT = 120


class ExpressionSetConnectBase(BaseSalesforceTask):
    """Base class with BRE Connect API helpers and lifecycle methods."""

    task_options: Dict[str, Dict[str, Any]] = {}

    # -- Auth / URL properties -----------------------------------------

    @property
    def _api_version(self) -> str:
        return (
            self.options.get("api_version")
            or getattr(self.org_config, "api_version", None)
            or getattr(
                self.project_config,
                "project__package__api_version",
                "67.0",
            )
        )

    @property
    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.org_config.access_token}",
            "Content-Type": "application/json",
        }

    @property
    def _base_url(self) -> str:
        return f"{self.org_config.instance_url}/services/data/v{self._api_version}"

    @property
    def _connect_url(self) -> str:
        return f"{self._base_url}/connect/business-rules/expression-set"

    # -- SOQL helpers --------------------------------------------------

    @staticmethod
    def _soql_escape(value: str) -> str:
        return value.replace("\\", "\\\\").replace("'", "\\'")

    def _soql_query(self, soql: str) -> List[dict]:
        url = f"{self._base_url}/query"
        resp = requests.get(
            url, headers=self._headers, params={"q": soql}, timeout=_REQUEST_TIMEOUT
        )
        if resp.status_code != 200:
            self.logger.error("SOQL failed (%s): %s", resp.status_code, resp.text)
            return []
        body = resp.json()
        records: List[dict] = body.get("records", [])
        while not body.get("done", True) and body.get("nextRecordsUrl"):
            nurl = f"{self.org_config.instance_url}{body['nextRecordsUrl']}"
            resp = requests.get(nurl, headers=self._headers, timeout=_REQUEST_TIMEOUT)
            if resp.status_code != 200:
                break
            body = resp.json()
            records.extend(body.get("records", []))
        return records

    # -- REST helpers --------------------------------------------------

    def _patch_sobject(self, sobject: str, record_id: str, payload: dict) -> None:
        url = f"{self._base_url}/sobjects/{sobject}/{record_id}"
        max_attempts = 4
        for attempt in range(1, max_attempts + 1):
            resp = requests.patch(
                url, headers=self._headers, json=payload, timeout=_REQUEST_TIMEOUT
            )
            if resp.status_code in (200, 204):
                return
            resp_text = resp.text or ""
            if "UNABLE_TO_LOCK_ROW" in resp_text and attempt < max_attempts:
                wait = attempt * 2
                self.logger.warning(
                    "Row lock on %s/%s (attempt %s/%s). Retrying in %ss.",
                    sobject, record_id, attempt, max_attempts, wait,
                )
                time.sleep(wait)
                continue
            raise TaskOptionsError(
                f"PATCH {sobject}/{record_id} failed ({resp.status_code}): {resp_text}"
            )

    def _delete_sobject(self, sobject: str, record_id: str) -> None:
        url = f"{self._base_url}/sobjects/{sobject}/{record_id}"
        resp = requests.delete(url, headers=self._headers, timeout=_REQUEST_TIMEOUT)
        if resp.status_code not in (200, 204):
            raise TaskOptionsError(
                f"DELETE {sobject}/{record_id} failed "
                f"({resp.status_code}): {resp.text}"
            )

    # -- BRE Connect API helpers ---------------------------------------

    def _get_expression_set_definition_id(self, api_name: str) -> str:
        safe = self._soql_escape(api_name)
        records = self._soql_query(
            f"SELECT Id FROM ExpressionSetDefinition WHERE DeveloperName = '{safe}'"
        )
        if not records:
            raise TaskOptionsError(
                f"ExpressionSetDefinition '{api_name}' not found in org."
            )
        return records[0]["Id"]

    def _get_expression_set_id(self, api_name: str) -> str:
        """Get the ExpressionSet runtime record ID (used by the Connect API)."""
        safe = self._soql_escape(api_name)
        records = self._soql_query(
            "SELECT Id FROM ExpressionSet "
            f"WHERE ExpressionSetDefinition.DeveloperName = '{safe}'"
        )
        if not records:
            raise TaskOptionsError(
                f"ExpressionSet for '{api_name}' not found in org."
            )
        return records[0]["Id"]

    def _resolve_version_by_es_id(self, es_id: str) -> dict:
        """Resolve the runtime ExpressionSetVersion from the ExpressionSet Id.

        The ExpressionSetVersion sObject is the source of truth for the
        version's Id / ApiName / IsActive — unlike the Connect GET payload,
        whose version identity can be a transiently stale clone name. We match
        on the ExpressionSetId FK rather than guessing by naming convention.

        Prefer the ACTIVE version (the one actually executing) over a merely
        higher VersionNumber: mutating/deactivating the latest-numbered draft
        while a different version is live would target the wrong record. Order
        by IsActive then VersionNumber so the active (or, absent any active one,
        the highest-numbered) version is first.
        """
        safe = self._soql_escape(es_id)
        records = self._soql_query(
            "SELECT Id, ApiName, IsActive, VersionNumber "
            f"FROM ExpressionSetVersion WHERE ExpressionSetId = '{safe}' "
            "ORDER BY IsActive DESC, VersionNumber DESC"
        )
        if not records:
            raise TaskOptionsError(
                f"No ExpressionSetVersion found for ExpressionSet {es_id}."
            )
        chosen = records[0]
        active = [r for r in records if r.get("IsActive")]
        if len(active) > 1:
            self.logger.warning(
                "ExpressionSet %s has %d active versions; operating on the "
                "highest-numbered active one (%s).",
                es_id, len(active), chosen.get("ApiName"),
            )
        return chosen

    def _check_version_name_consistency(
        self, es_id: str, esv: dict, definition: Optional[dict] = None
    ) -> None:
        """Warn if Connect GET's version apiName disagrees with the sObject.

        A stale clone apiName served by GET breaks PATCH. This is usually
        transient and resolves on re-GET; surface it so a failure is
        diagnosable rather than mysterious. Pass ``definition`` to reuse an
        already-fetched GET payload instead of issuing another round-trip.
        """
        try:
            if definition is None:
                definition = self._get_expression_set_via_connect(es_id)
            versions = definition.get("versions", [])
            get_api = versions[0].get("apiName") if versions else None
        except Exception:
            return
        sobject_api = esv.get("ApiName")
        if get_api and sobject_api and get_api != sobject_api:
            self.logger.warning(
                "Connect GET version apiName '%s' disagrees with the "
                "ExpressionSetVersion sObject ApiName '%s' (stale clone name). "
                "PATCH may fail; re-run to let the GET cache settle.",
                get_api, sobject_api,
            )

    def _ensure_resource_initialization_type(
        self, es_id: str, dry_run: bool, desired: Optional[str] = None
    ) -> None:
        """Align stored ExpressionSet.ResourceInitializationType before PATCH.

        Connect GET reports "Off" while the sObject stores null on seeded
        procedures; PATCH validates the body against the stored value and
        rejects with "resourceInitializationType is set to null and cannot be
        changed." Writing the stored field to the value the PATCH body carries
        aligns the two so the PATCH is accepted.

        ``desired`` is the value the PATCH body will carry (the payload's
        ``resourceInitializationType``). It defaults to "Off" — the value GET
        serializes over a stored null, which is what an overlay or a GET-derived
        export sends. A payload that declares "Default" must pass it here, or the
        stored field would be aligned to "Off" and then mismatch the body.

        The field is immutable once set: if it already holds a value, this only
        warns on a conflict (the caller cannot change it) and never rewrites it.
        """
        target = desired or "Off"
        if target not in RESOURCE_INIT_TYPES:
            self.logger.warning(
                "Ignoring unrecognized resourceInitializationType '%s'; "
                "valid values are %s.",
                target, sorted(RESOURCE_INIT_TYPES),
            )
            target = "Off"
        safe = self._soql_escape(es_id)
        records = self._soql_query(
            "SELECT Id, ResourceInitializationType "
            f"FROM ExpressionSet WHERE Id = '{safe}'"
        )
        if not records:
            return
        current = records[0].get("ResourceInitializationType")
        if current:
            # Immutable once set. If the body wants a different value the PATCH
            # would be rejected — surface it rather than silently mismatching.
            if desired and desired != current:
                self.logger.warning(
                    "ExpressionSet %s ResourceInitializationType is already '%s' "
                    "and is immutable; the payload's '%s' cannot be applied and "
                    "the PATCH body must match the stored value.",
                    es_id, current, desired,
                )
            return
        if dry_run:
            self.logger.info(
                "[dry-run] Would set ExpressionSet %s "
                "ResourceInitializationType=%s (currently null).",
                es_id, target,
            )
            return
        self.logger.info(
            "ExpressionSet %s has null ResourceInitializationType; "
            "setting it to '%s' so the Connect PATCH is accepted.",
            es_id, target,
        )
        self._patch_sobject(
            "ExpressionSet", es_id, {"ResourceInitializationType": target}
        )

    def _connect_error(self, verb: str, es_id: str, resp) -> TaskOptionsError:
        """Build a TaskOptionsError surfacing the Connect errorCode/message."""
        detail = resp.text or ""
        try:
            body = resp.json()
            if isinstance(body, list) and body:
                body = body[0]
            if isinstance(body, dict):
                detail = (
                    f"{body.get('errorCode', '')}: {body.get('message', detail)}"
                ).strip(": ")
        except Exception:
            pass
        return TaskOptionsError(
            f"{verb} expression set {es_id} failed ({resp.status_code}): {detail}"
        )

    def _get_expression_set_via_connect(self, es_id: str) -> dict:
        url = f"{self._connect_url}/{es_id}"
        resp = requests.get(url, headers=self._headers, timeout=_REQUEST_TIMEOUT)
        if not resp.ok:
            raise self._connect_error("GET", es_id, resp)
        return resp.json()

    def _patch_expression_set_via_connect(self, es_id: str, payload: dict) -> dict:
        url = f"{self._connect_url}/{es_id}"
        resp = requests.patch(
            url, headers=self._headers, json=payload, timeout=_REQUEST_TIMEOUT
        )
        if not resp.ok:
            raise self._connect_error("PATCH", es_id, resp)
        return resp.json() if resp.content else {}

    def _post_expression_set_via_connect(self, payload: dict) -> dict:
        resp = requests.post(
            self._connect_url, headers=self._headers, json=payload,
            timeout=_REQUEST_TIMEOUT,
        )
        if resp.status_code not in (200, 201):
            raise self._connect_error("POST", "(new)", resp)
        return resp.json()

    def _delete_expression_set_via_connect(self, es_id: str) -> None:
        url = f"{self._connect_url}/{es_id}"
        resp = requests.delete(url, headers=self._headers, timeout=_REQUEST_TIMEOUT)
        if resp.status_code not in (200, 204):
            raise self._connect_error("DELETE", es_id, resp)

    # -- Version lifecycle helpers -------------------------------------

    def _set_version_active(self, version_id: str, active: bool, dry_run: bool):
        if dry_run:
            self.logger.info(
                "[dry-run] Would set ExpressionSetVersion %s IsActive=%s",
                version_id, active,
            )
            return
        # Idempotent: skip the sObject PATCH if the version is already in the
        # desired state. A Connect full-graph PATCH whose body carries
        # `enabled: true` re-activates the version itself, so a subsequent
        # explicit reactivation would otherwise hit the "An enabled Expression
        # Set Version cannot be updated/deleted." guardrail and fail a
        # genuinely-successful mutation.
        records = self._soql_query(
            "SELECT Id, IsActive FROM ExpressionSetVersion "
            f"WHERE Id = '{self._soql_escape(version_id)}'"
        )
        if records and bool(records[0].get("IsActive")) is active:
            self.logger.info(
                "ExpressionSetVersion %s already IsActive=%s; no change needed.",
                version_id, active,
            )
            return
        self._patch_sobject("ExpressionSetVersion", version_id, {"IsActive": active})
        self.logger.info(
            "Set ExpressionSetVersion %s IsActive=%s.", version_id, active
        )

    def _wait_for_version_state(self, version_id: str, active: bool):
        max_wait = self._int_option("max_wait_seconds", 45)
        interval = self._int_option("poll_interval_seconds", 3, minimum=1)
        waited = 0
        while waited <= max_wait:
            records = self._soql_query(
                "SELECT Id, IsActive FROM ExpressionSetVersion "
                f"WHERE Id = '{self._soql_escape(version_id)}'"
            )
            if records and bool(records[0].get("IsActive")) is active:
                self.logger.info(
                    "Confirmed ExpressionSetVersion %s IsActive=%s after %ss.",
                    version_id, active, waited,
                )
                return
            time.sleep(interval)
            waited += interval
        raise TaskOptionsError(
            f"ExpressionSetVersion {version_id} did not reach "
            f"IsActive={active} within {max_wait}s."
        )

    # -- Cascade deactivation (procedure plan references) --------------

    def _find_referencing_procedure_plans(self, es_def_id: str) -> List[dict]:
        safe = self._soql_escape(es_def_id)
        return self._soql_query(
            "SELECT Id, ProcedurePlanSection.ProcedurePlanVersionId "
            "FROM ProcedurePlanOption "
            f"WHERE ExpressionSetDefinitionId = '{safe}'"
        )

    def _cascade_deactivate_procedure_plans(
        self, es_def_id: str, dry_run: bool
    ) -> List[str]:
        """Deactivate any active procedure plan versions referencing this ES.
        Returns list of version IDs that were deactivated.

        If setup fails partway through, rollback only the procedure-plan
        versions this cascade already deactivated. Connect PATCH failures later
        in the lifecycle intentionally keep cascaded versions deactivated for
        inspection; this rollback is only for pre-mutation cascade setup.
        """
        options = self._find_referencing_procedure_plans(es_def_id)
        if not options:
            return []
        version_ids = set()
        for opt in options:
            section = opt.get("ProcedurePlanSection") or {}
            vid = section.get("ProcedurePlanVersionId")
            if vid:
                version_ids.add(vid)
        deactivated = []
        try:
            for vid in sorted(version_ids):
                records = self._soql_query(
                    "SELECT Id, IsActive FROM ProcedurePlanDefinitionVersion "
                    f"WHERE Id = '{self._soql_escape(vid)}'"
                )
                if records and records[0].get("IsActive"):
                    if dry_run:
                        self.logger.info(
                            "[dry-run] Would deactivate ProcedurePlanDefinitionVersion %s",
                            vid,
                        )
                    else:
                        self._patch_sobject(
                            "ProcedurePlanDefinitionVersion", vid, {"IsActive": False}
                        )
                        self.logger.info(
                            "Deactivated ProcedurePlanDefinitionVersion %s (cascade).",
                            vid,
                        )
                    deactivated.append(vid)
        except Exception as exc:
            if deactivated and not dry_run:
                try:
                    self._cascade_reactivate_procedure_plans(deactivated, False)
                except Exception as rollback_exc:
                    raise TaskOptionsError(
                        "Cascade deactivation failed after deactivating "
                        f"ProcedurePlanDefinitionVersion(s) {deactivated}, and "
                        f"rollback also failed: {rollback_exc}"
                    ) from exc
                raise TaskOptionsError(
                    "Cascade deactivation failed after deactivating "
                    f"ProcedurePlanDefinitionVersion(s) {deactivated}; "
                    "rolled them back before aborting."
                ) from exc
            raise
        return deactivated

    def _cascade_reactivate_procedure_plans(
        self, version_ids: List[str], dry_run: bool
    ):
        for vid in version_ids:
            if dry_run:
                self.logger.info(
                    "[dry-run] Would reactivate ProcedurePlanDefinitionVersion %s", vid
                )
            else:
                self._patch_sobject(
                    "ProcedurePlanDefinitionVersion", vid, {"IsActive": True}
                )
                self.logger.info(
                    "Reactivated ProcedurePlanDefinitionVersion %s.", vid
                )

    # -- Shared mutation lifecycle -------------------------------------

    def _run_connect_mutation(
        self,
        *,
        es_def_id: str,
        esv: dict,
        mutate,
        dry_run: bool,
        activate_after: bool,
        cascade: bool,
        verb: str = "mutation",
    ) -> None:
        """Run the safety-critical deactivate→mutate→reactivate lifecycle.

        Shared by ApplyExpressionSetOverlay and ImportExpressionSet's
        replace path so the guarantees below live in ONE place and cannot drift:

          * A Connect mutation requires the version inactive, so an active
            version (and any referencing procedure-plan versions, when
            ``cascade``) is deactivated first.
          * ``mutate`` is the verb-specific body (Apply: GET→overlay→validate→
            PATCH→verify; Import: strip→PATCH). It runs while the version is
            deactivated and is responsible for its own dry-run handling.
          * Reactivation is governed by the explicit ``activate_after`` (NOT by
            the prior active state — an explicit false must win, leaving the
            version inactive for inspection).
          * PATCH is NOT atomic: a failed PATCH can leave a half-mutated,
            deactivated version. It is NEVER reactivated — re-enabling a
            corrupted pricing procedure is worse than leaving it offline. So
            reactivation happens only when ``activate_after`` AND the mutate body
            succeeded (or in dry-run, where nothing changed).

        Re-raises the original failure (chaining a reactivation failure onto it
        when both happen) so the caller surfaces it.
        """
        esv_id = esv["Id"]
        was_active = bool(esv.get("IsActive"))
        deactivated = False
        cascaded_ppvs: List[str] = []
        failure: Optional[Exception] = None
        mutate_succeeded = False

        try:
            if was_active:
                if cascade:
                    cascaded_ppvs = self._cascade_deactivate_procedure_plans(
                        es_def_id, dry_run
                    )
                self._set_version_active(esv_id, False, dry_run)
                if not dry_run:
                    self._wait_for_version_state(esv_id, False)
                deactivated = True
            else:
                self.logger.info(
                    "ExpressionSetVersion %s already inactive.", esv_id
                )

            mutate()
            mutate_succeeded = True
        except Exception as exc:
            failure = exc
        finally:
            should_activate = activate_after and (mutate_succeeded or dry_run)
            if should_activate:
                try:
                    self._set_version_active(esv_id, True, dry_run)
                    if not dry_run:
                        self._wait_for_version_state(esv_id, True)
                    if cascaded_ppvs:
                        self._cascade_reactivate_procedure_plans(
                            cascaded_ppvs, dry_run
                        )
                except Exception as reactivate_exc:
                    if failure:
                        raise TaskOptionsError(
                            f"{verb} failed, and reactivation also failed: "
                            f"{reactivate_exc}"
                        ) from failure
                    raise
            elif failure and deactivated and not dry_run:
                self.logger.error(
                    "%s failed and may have partially applied. Leaving "
                    "ExpressionSetVersion %s DEACTIVATED to avoid re-enabling a "
                    "corrupted definition. Inspect/restore it manually, then "
                    "reactivate (cascaded procedure plans %s remain "
                    "deactivated).",
                    verb, esv_id, cascaded_ppvs or "(none)",
                )
            elif deactivated and not dry_run:
                # Success, but activate_after=false: leave the version (and any
                # cascaded procedure plans) deactivated as the caller requested.
                self.logger.info(
                    "activate_after=false; leaving ExpressionSetVersion %s and "
                    "cascaded procedure plans %s DEACTIVATED as requested.",
                    esv_id, cascaded_ppvs or "(none)",
                )

        if failure:
            raise failure

    # -- Payload sanitization -----------------------------------------
    #
    # Deny-list, not allow-list. The Connect Input representation accepts almost
    # every field the Output representation returns; the only fields that MUST
    # be removed are the output-only ones the parser rejects. The TOP-LEVEL
    # `id`/`error` are output-only and rejected on input for both verbs.
    #
    # The version-level `id` is verb-dependent:
    #   * PATCH (replace) KEEPS it — the server matches the version in place;
    #     stripping it makes the server treat the version as new and gack.
    #   * POST (create) OMITS it — a create body carrying a source-org version
    #     id (a 9QM from `export_expression_set`) makes the server reject or
    #     mis-bind the new version. `for_create=True` strips versions[].id.

    _TOP_LEVEL_DENY = {"id", "error"}

    @classmethod
    def _strip_readonly_fields(cls, payload: dict, for_create: bool = False) -> dict:
        """Remove output-only fields the Connect API rejects on PATCH/POST.

        Keeps everything else, including top-level interfaceSourceType /
        resourceInitializationType / contextDefinitions. The version-level `id`
        is kept for a PATCH (which needs it to match in place) and stripped when
        ``for_create`` is set (a POST-create must not carry a source-org id).
        """
        stripped = {k: v for k, v in payload.items() if k not in cls._TOP_LEVEL_DENY}
        if for_create:
            versions = stripped.get("versions")
            if isinstance(versions, list):
                stripped["versions"] = [
                    {k: v for k, v in version.items() if k != "id"}
                    if isinstance(version, dict)
                    else version
                    for version in versions
                ]
        return stripped

    # -- HTML-entity normalization -------------------------------------
    #
    # The Connect GET serializer HTML-escapes JSON-in-string content: a pricing
    # procedure export stores customElement.parameters[].value as escaped JSON
    # (e.g. "{&quot;whereConditions&quot;:[]}") and advancedCondition.criteria[].value
    # as escaped literals (e.g. "&#39;Evergreen&#39;"). JSON — unlike the XML
    # Metadata path, where the XML parser decodes &quot;→" before the engine sees
    # the value — carries no entity layer, so json.loads returns the literal
    # `&quot;`/`&#39;` characters and the engine's value sub-parser rejects them
    # on input ("Syntax error. Found '&'" on a flat formula; an opaque parse
    # failure on a nested blob). html.unescape() is the exact inverse of a single
    # escape pass and a no-op on entity-free strings, so a full recursive walk
    # over string leaves is safe and correct.

    @staticmethod
    def _unescape_value(value):
        """Recursively HTML-unescape every string leaf in a JSON-like value.

        Returns a new structure; does not mutate the input.
        """
        if isinstance(value, str):
            return html.unescape(value)
        if isinstance(value, list):
            return [ExpressionSetConnectBase._unescape_value(v) for v in value]
        if isinstance(value, dict):
            return {
                k: ExpressionSetConnectBase._unescape_value(v)
                for k, v in value.items()
            }
        return value  # int / float / bool / None pass through unchanged

    def _normalize_html_entities(self, payload: dict) -> dict:
        """HTML-unescape all string leaves before a Connect PATCH/POST.

        Off only when `normalize_html_entities: false` is passed (a probe
        escape hatch to reproduce the un-normalized gack on demand).
        """
        if not self._bool_option(self.options.get("normalize_html_entities"), True):
            self.logger.info(
                "normalize_html_entities=false — sending payload WITHOUT "
                "HTML-entity normalization (escaped GET output may gack)."
            )
            return payload
        return self._unescape_value(payload)

    # -- Schema pre-flight validation ----------------------------------
    #
    # Validate payloads BEFORE the Connect call. The PATCH/POST handler can
    # swallow real errors into opaque gacks, so a malformed step graph
    # otherwise surfaces as "Something went wrong" with no actionable detail.
    # Blocking by default; pass `skip_validation: true` to bypass (e.g. to probe
    # a payload the validator is too strict about).

    def _skip_validation(self) -> bool:
        return self._bool_option(self.options.get("skip_validation"), False)

    def _raise_on_validation_errors(self, result, what: str) -> None:
        for issue in result.warnings:
            self.logger.warning("Schema %s: %s — %s", what, issue.location, issue.message)
        if result.errors:
            detail = "; ".join(f"{i.location}: {i.message}" for i in result.errors)
            raise TaskOptionsError(
                f"Schema validation failed for the {what} ({len(result.errors)} "
                f"error(s)): {detail}. Fix the payload, or pass "
                f"skip_validation:true to bypass."
            )

    def _preflight_validate_definition(self, definition: dict) -> None:
        if self._skip_validation():
            self.logger.info("skip_validation=true — skipping definition schema check.")
            return
        self._raise_on_validation_errors(validate_definition(definition), "definition")

    def _preflight_validate_overlay(self, overlay: dict) -> None:
        if self._skip_validation():
            self.logger.info("skip_validation=true — skipping overlay schema check.")
            return
        self._raise_on_validation_errors(validate_overlay(overlay), "overlay")

    def _preflight_validate_overlay_against_definition(
        self, overlay: dict, definition: dict, version_api_name: Optional[str]
    ) -> None:
        """Cross-check overlay targets against the live definition BEFORE any
        deactivation, so a typo'd placement/update/reorder/remove target fails
        locally instead of after the version has been toggled off (which would
        leave a live procedure deactivated)."""
        if self._skip_validation():
            self.logger.info(
                "skip_validation=true — skipping overlay/definition cross-check."
            )
            return
        self._raise_on_validation_errors(
            validate_overlay_against_definition(
                overlay, definition, version_api_name
            ),
            "overlay against the live definition",
        )

    # -- Utility -------------------------------------------------------

    @staticmethod
    def _bool_option(value: Any, default: bool) -> bool:
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        return str(value).lower() in ("true", "1", "yes")

    def _int_option(self, name: str, default: int, minimum: int = 0) -> int:
        """Read an int option, raising a clear TaskOptionsError on a non-numeric
        value rather than letting int() throw an opaque ValueError mid-run."""
        value = self.options.get(name)
        if value is None:
            return max(minimum, default)
        try:
            return max(minimum, int(value))
        except (TypeError, ValueError):
            raise TaskOptionsError(
                f"Option '{name}' must be an integer (got {value!r})."
            )


# ======================================================================
# ExportExpressionSet
# ======================================================================


class ExportExpressionSet(ExpressionSetConnectBase):
    """Export an expression set definition from the org to a JSON file."""

    task_options = {
        **ExpressionSetConnectBase.task_options,
        "expression_set_api_name": {
            "description": "DeveloperName of the expression set to export.",
            "required": True,
        },
        "output_file": {
            "description": "Path to write the exported JSON.",
            "required": True,
        },
    }

    def _run_task(self):
        api_name = self.options["expression_set_api_name"]
        output_path = Path(self.options["output_file"])

        es_id = self._get_expression_set_id(api_name)
        self.logger.info("Exporting expression set %s (Id: %s)...", api_name, es_id)

        definition = self._get_expression_set_via_connect(es_id)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(definition, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        self.logger.info("Exported to %s", output_path)


# ======================================================================
# ApplyExpressionSetOverlay
# ======================================================================


class ApplyExpressionSetOverlay(ExpressionSetConnectBase):
    """Apply a declarative overlay to an expression set via BRE Connect API.

    Supports: addSteps, removeSteps, updateSteps, reorderSteps,
              addVariables, removeVariables.
    """

    task_options = {
        **ExpressionSetConnectBase.task_options,
        "overlay_file": {
            "description": "Path to the overlay JSON file.",
            "required": True,
        },
        "expression_set_api_name": {
            "description": (
                "Override expression set API name (default: from overlay file)."
            ),
            "required": False,
        },
        "version_api_name": {
            "description": (
                "Override version API name (default: from overlay file)."
            ),
            "required": False,
        },
        "dry_run": {
            "description": "Log changes without modifying the org.",
            "required": False,
        },
        "verify": {
            "description": "GET definition after apply to verify changes.",
            "required": False,
        },
        "skip_validation": {
            "description": (
                "Skip the schema pre-flight on the overlay and merged definition "
                "(default: false — validation blocks on errors)."
            ),
            "required": False,
        },
        "normalize_html_entities": {
            "description": (
                "HTML-unescape (&quot;->\", &#39;->', etc.) all string leaves in "
                "the payload before the Connect call (default: true). Required to "
                "round-trip real GET output, whose serializer escapes "
                "JSON-in-string param/criteria/formula values. Set false only to "
                "reproduce the escape gack."
            ),
            "required": False,
        },
        "activate_after_apply": {
            "description": "Reactivate version after overlay (default: true).",
            "required": False,
        },
        "cascade_deactivate_procedure_plan": {
            "description": (
                "Deactivate referencing procedure plan versions if needed (default: true)."
            ),
            "required": False,
        },
        "max_wait_seconds": {
            "description": "Max seconds to poll for activation state changes.",
            "required": False,
        },
        "poll_interval_seconds": {
            "description": "Seconds between activation state polls.",
            "required": False,
        },
    }

    def _run_task(self):
        overlay = self._load_overlay()
        # Validate the overlay shape up front — before any deactivation — so a
        # malformed overlay never leaves a version toggled off.
        self._preflight_validate_overlay(overlay)
        es_api_name = (
            self.options.get("expression_set_api_name")
            or overlay.get("expressionSetApiName")
        )
        if not es_api_name:
            raise TaskOptionsError(
                "expression_set_api_name required in options or overlay file."
            )

        dry_run = self._bool_option(self.options.get("dry_run"), False)
        verify = self._bool_option(self.options.get("verify"), True)
        activate_after = self._bool_option(
            self.options.get("activate_after_apply"), True
        )
        cascade = self._bool_option(
            self.options.get("cascade_deactivate_procedure_plan"), True
        )

        es_id = self._get_expression_set_id(es_api_name)
        es_def_id = self._get_expression_set_definition_id(es_api_name)
        esv = self._resolve_version_by_es_id(es_id)

        version_api_name = (
            self.options.get("version_api_name")
            or overlay.get("versionApiName")
        )

        # Fetch the live definition up front (before any deactivation) for the
        # read-only pre-flights: the overlay/definition cross-check — which
        # rejects a typo'd placement/update/reorder/remove target locally so a
        # bad overlay never leaves a live version toggled off — and the
        # version-name consistency warning. The actual overlay is applied to a
        # fresh post-deactivation GET inside the mutate body below so the PATCH
        # payload reflects the deactivated state.
        preflight_definition = self._get_expression_set_via_connect(es_id)
        self._preflight_validate_overlay_against_definition(
            overlay, preflight_definition, version_api_name
        )
        self._check_version_name_consistency(es_id, esv, preflight_definition)

        # Align ResourceInitializationType to the value the PATCH body will
        # carry (GET fabricates "Off" over a stored null), before touching
        # activation state.
        self._ensure_resource_initialization_type(
            es_id, dry_run, preflight_definition.get("resourceInitializationType")
        )

        def mutate():
            definition = self._get_expression_set_via_connect(es_id)
            modified = self._apply_overlay(definition, overlay)

            # Pre-flight: validate the merged definition before PATCH so a
            # malformed step graph fails locally with a clear message rather
            # than as an opaque server gack.
            self._preflight_validate_definition(modified)

            # Send the WHOLE definition (sanitized), not a reconstructed thin
            # object, so identity/structural fields (interfaceSourceType,
            # resourceInitializationType, contextDefinitions) and the
            # version-level `id` PATCH requires are preserved. The Connect PATCH
            # is a full-graph replace. Normalize HTML entities LAST (after
            # validation, which must see the escaped form to warn) so the bytes
            # on the wire are valid JSON inside the param/criteria value strings.
            patch_payload = self._strip_readonly_fields(modified)
            patch_payload = self._normalize_html_entities(patch_payload)

            if dry_run:
                self.logger.info("[dry-run] Would PATCH expression set %s.", es_id)
            else:
                self._patch_expression_set_via_connect(es_id, patch_payload)
                self.logger.info("PATCHed expression set %s.", es_id)

            if verify and not dry_run:
                self._verify_overlay(es_id, overlay)

        self._run_connect_mutation(
            es_def_id=es_def_id,
            esv=esv,
            mutate=mutate,
            dry_run=dry_run,
            activate_after=activate_after,
            cascade=cascade,
            verb="Overlay apply",
        )

        self.logger.info(
            "Successfully applied overlay %s to %s.",
            self.options["overlay_file"], es_api_name,
        )

    # -- Overlay loading -----------------------------------------------

    def _load_overlay(self) -> dict:
        path = Path(self.options["overlay_file"])
        if not path.exists():
            raise TaskOptionsError(f"Overlay file not found: {path}")
        return json.loads(path.read_text(encoding="utf-8"))

    # -- Overlay transformation (pure function) ------------------------

    def _apply_overlay(self, definition: dict, overlay: dict) -> dict:
        """Apply overlay transformations to the definition. Returns modified copy."""
        result = deepcopy(definition)
        versions = result.get("versions", [])
        if not versions:
            raise TaskOptionsError("Expression set has no versions to modify.")

        version_api_name = (
            self.options.get("version_api_name")
            or overlay.get("versionApiName")
        )
        version = self._find_version(versions, version_api_name)
        steps = version.get("steps", [])
        variables = version.get("variables", [])

        if overlay.get("removeSteps"):
            steps = self._remove_steps(steps, overlay["removeSteps"])
        if overlay.get("addSteps"):
            steps = self._add_steps(steps, overlay["addSteps"])
        if overlay.get("updateSteps"):
            steps = self._update_steps(steps, overlay["updateSteps"])
        if overlay.get("reorderSteps"):
            steps = self._reorder_steps(steps, overlay["reorderSteps"])

        if overlay.get("removeVariables"):
            variables = self._remove_variables(variables, overlay["removeVariables"])
        if overlay.get("addVariables"):
            variables = self._add_variables(variables, overlay["addVariables"])

        version["steps"] = steps
        version["variables"] = variables
        return result

    def _find_version(self, versions: list, version_api_name: Optional[str]) -> dict:
        if version_api_name:
            for v in versions:
                if v.get("apiName") == version_api_name:
                    return v
            raise TaskOptionsError(
                f"Version '{version_api_name}' not found in definition."
            )
        return versions[0]

    # -- Step operations -----------------------------------------------

    def _remove_steps(self, steps: list, to_remove: list) -> list:
        names_to_remove = {s["name"] for s in to_remove}
        present = {s.get("name") for s in steps}
        steps = [s for s in steps if s.get("name") not in names_to_remove]
        # Log per name against that name's actual presence — not a batch-wide
        # count, which would mislabel every name once any one was removed.
        for name in names_to_remove:
            if name in present:
                self.logger.info("Removed step '%s'.", name)
            else:
                self.logger.warning("Step '%s' not found for removal.", name)
        steps = self._renumber_top_level_steps(steps)
        return steps

    def _add_steps(self, steps: list, to_add: list) -> list:
        for step_def in to_add:
            existing = next(
                (s for s in steps if s.get("name") == step_def["name"]), None
            )
            if existing:
                self.logger.info(
                    "Step '%s' already exists, skipping add.", step_def["name"]
                )
                continue

            # Read placement WITHOUT mutating the caller's overlay dict: the
            # verification pass (_verify_step_placement) reads placement back off
            # the same overlay, so popping it here would silently disable the
            # placement check. _build_step copies only the fields it needs.
            placement = step_def.get("placement")
            new_step = self._build_step(step_def)

            # Child steps (parentStep set) are ordered by their own
            # sequenceNumber scoped WITHIN the parent (children restart at 1).
            # They take no top-level placement and must not trigger the
            # top-level renumber/bump logic below, which would overwrite their
            # per-parent sequenceNumber with max_top_level + 1 (colliding
            # siblings onto the same slot). _build_step already copied the
            # provided sequenceNumber, so just append.
            if step_def.get("parentStep"):
                steps.append(new_step)
                self.logger.info(
                    "Added child step '%s' (parent '%s') at sequence %s.",
                    new_step["name"], step_def["parentStep"],
                    new_step["sequenceNumber"],
                )
                continue

            if placement and placement.get("afterStep"):
                target_name = placement["afterStep"]
                target_seq = self._find_step_sequence(steps, target_name)
                new_step["sequenceNumber"] = target_seq + 1
                for s in steps:
                    if (
                        s.get("parentStep") is None
                        and s.get("sequenceNumber", 0) > target_seq
                    ):
                        s["sequenceNumber"] = s["sequenceNumber"] + 1
            elif placement and placement.get("beforeStep"):
                target_name = placement["beforeStep"]
                target_seq = self._find_step_sequence(steps, target_name)
                new_step["sequenceNumber"] = target_seq
                for s in steps:
                    if (
                        s.get("parentStep") is None
                        and s.get("sequenceNumber", 0) >= target_seq
                    ):
                        s["sequenceNumber"] = s["sequenceNumber"] + 1
            elif placement and placement.get("sequenceNumber") is not None:
                seq = placement["sequenceNumber"]
                new_step["sequenceNumber"] = seq
                for s in steps:
                    if (
                        s.get("parentStep") is None
                        and s.get("sequenceNumber", 0) >= seq
                    ):
                        s["sequenceNumber"] = s["sequenceNumber"] + 1
            else:
                max_seq = max(
                    (
                        s.get("sequenceNumber", 0)
                        for s in steps
                        if s.get("parentStep") is None
                    ),
                    default=0,
                )
                new_step["sequenceNumber"] = max_seq + 1

            steps.append(new_step)
            self.logger.info(
                "Added step '%s' at sequence %s.",
                new_step["name"], new_step["sequenceNumber"],
            )
        return steps

    def _update_steps(self, steps: list, to_update: list) -> list:
        for update_def in to_update:
            name = update_def["name"]
            target = next((s for s in steps if s.get("name") == name), None)
            if not target:
                # Raise rather than warn-and-continue: a missing target means the
                # edit silently does nothing, yet the PATCH still succeeds and is
                # reported as success. Fail loudly so a typo'd name is caught.
                raise TaskOptionsError(
                    f"updateSteps target '{name}' not found in the definition."
                )
            for key, value in update_def.items():
                if key == "name":
                    continue
                target[key] = value
            self.logger.info("Updated step '%s'.", name)
        return steps

    def _reorder_steps(self, steps: list, reorder_defs: list) -> list:
        for reorder in reorder_defs:
            name = reorder["name"]
            target = next((s for s in steps if s.get("name") == name), None)
            if not target:
                raise TaskOptionsError(
                    f"reorderSteps target '{name}' not found in the definition."
                )
            target["sequenceNumber"] = reorder["sequenceNumber"]
            self.logger.info(
                "Reordered step '%s' to sequence %s.",
                name, reorder["sequenceNumber"],
            )
        return steps

    def _build_step(self, step_def: dict) -> dict:
        step = {
            "name": step_def["name"],
            "description": step_def.get("description", ""),
            "sequenceNumber": step_def.get("sequenceNumber", 1),
            "stepType": step_def.get("stepType", "BusinessKnowledgeModel"),
            "resultIncluded": step_def.get("resultIncluded", False),
            "shouldExposeExecPathMsgOnly": step_def.get(
                "shouldExposeExecPathMsgOnly", True
            ),
            "shouldExposeConditionDetails": step_def.get(
                "shouldExposeConditionDetails", False
            ),
            "shouldShowExplExternally": step_def.get(
                "shouldShowExplExternally", False
            ),
        }
        if step_def.get("parentStep"):
            step["parentStep"] = step_def["parentStep"]
        if step_def.get("label"):
            step["label"] = step_def["label"]
        if step_def.get("customElement"):
            step["customElement"] = step_def["customElement"]
        if step_def.get("lookupTable"):
            step["lookupTable"] = step_def["lookupTable"]
        if step_def.get("conditionExpression"):
            step["conditionExpression"] = step_def["conditionExpression"]
        if step_def.get("advancedCondition"):
            step["advancedCondition"] = step_def["advancedCondition"]
        if step_def.get("actionType"):
            step["actionType"] = step_def["actionType"]
        if step_def.get("aggregation"):
            step["aggregation"] = step_def["aggregation"]
        if step_def.get("assignment"):
            step["assignment"] = step_def["assignment"]
        if step_def.get("subExpression"):
            step["subExpression"] = step_def["subExpression"]
        return step

    def _find_step_sequence(self, steps: list, name: str) -> int:
        for s in steps:
            if s.get("name") == name and s.get("parentStep") is None:
                return s.get("sequenceNumber", 0)
        raise TaskOptionsError(
            f"Placement target step '{name}' not found in definition."
        )

    def _renumber_top_level_steps(self, steps: list) -> list:
        top_level = [s for s in steps if s.get("parentStep") is None]
        top_level.sort(key=lambda s: s.get("sequenceNumber", 0))
        for i, s in enumerate(top_level, start=1):
            s["sequenceNumber"] = i
        return steps

    # -- Variable operations -------------------------------------------

    def _add_variables(self, variables: list, to_add: list) -> list:
        existing_names = {v.get("name") for v in variables}
        for var_def in to_add:
            if var_def["name"] in existing_names:
                self.logger.info(
                    "Variable '%s' already exists, skipping.", var_def["name"]
                )
                continue
            variables.append(var_def)
            self.logger.info("Added variable '%s'.", var_def["name"])
        return variables

    def _remove_variables(self, variables: list, to_remove: list) -> list:
        names = {v["name"] for v in to_remove}
        original_count = len(variables)
        variables = [v for v in variables if v.get("name") not in names]
        removed = original_count - len(variables)
        if removed:
            self.logger.info("Removed %d variable(s).", removed)
        return variables

    # -- Verification --------------------------------------------------

    def _verify_overlay(self, es_id: str, overlay: dict):
        post_state = self._get_expression_set_via_connect(es_id)
        versions = post_state.get("versions", [])
        if not versions:
            raise TaskOptionsError("Verification failed: no versions found.")

        version_api_name = (
            self.options.get("version_api_name")
            or overlay.get("versionApiName")
        )
        version = self._find_version(versions, version_api_name)
        steps = version.get("steps", [])
        step_names = {s.get("name") for s in steps}

        # NOTE: the Connect GET serializes top-level steps in alphabetical
        # name order, NOT execution (sequenceNumber) order. Never infer
        # ordering from the array index of the GET response — always read
        # sequenceNumber, which is what the engine executes on.
        seq_by_name = {
            s.get("name"): s.get("sequenceNumber")
            for s in steps
            if s.get("parentStep") is None
        }

        for added in overlay.get("addSteps", []):
            if added["name"] not in step_names:
                raise TaskOptionsError(
                    f"Verification failed: step '{added['name']}' not found after apply."
                )
            self._verify_step_placement(added, seq_by_name)
        for removed in overlay.get("removeSteps", []):
            if removed["name"] in step_names:
                raise TaskOptionsError(
                    f"Verification failed: step '{removed['name']}' still present after removal."
                )
        # updateSteps / reorderSteps must still be present after apply (a missing
        # target would have raised during _apply_overlay, but verify the result
        # against the org too); reorderSteps must also land on its sequenceNumber.
        for updated in overlay.get("updateSteps", []):
            if updated["name"] not in step_names:
                raise TaskOptionsError(
                    f"Verification failed: updated step '{updated['name']}' not "
                    "found after apply."
                )
        for reordered in overlay.get("reorderSteps", []):
            name = reordered["name"]
            if name not in step_names:
                raise TaskOptionsError(
                    f"Verification failed: reordered step '{name}' not found "
                    "after apply."
                )
            want = reordered.get("sequenceNumber")
            got = seq_by_name.get(name)
            # Only top-level steps carry a checkable sequence here (children are
            # scoped per parent and absent from seq_by_name).
            if got is not None and want is not None and got != want:
                raise TaskOptionsError(
                    f"Verification failed: reordered step '{name}' has "
                    f"sequenceNumber {got}, expected {want}."
                )
        self.logger.info("Verification passed.")

    @staticmethod
    def _verify_step_placement(added: dict, seq_by_name: dict):
        """Assert an added top-level step landed in the right sequence slot.

        Validates against sequenceNumber (the engine's execution order), not
        the GET response array order (which is alphabetical by name).
        """
        placement = added.get("placement") or {}
        name = added["name"]
        added_seq = seq_by_name.get(name)
        if added_seq is None:
            # Child step (has a parentStep) or no sequence to check.
            return

        if placement.get("afterStep"):
            target = placement["afterStep"]
            target_seq = seq_by_name.get(target)
            if target_seq is not None and added_seq != target_seq + 1:
                raise TaskOptionsError(
                    f"Verification failed: step '{name}' has sequenceNumber "
                    f"{added_seq}, expected {target_seq + 1} (immediately after "
                    f"'{target}' at {target_seq})."
                )
        elif placement.get("beforeStep"):
            target = placement["beforeStep"]
            target_seq = seq_by_name.get(target)
            if target_seq is not None and added_seq != target_seq - 1:
                raise TaskOptionsError(
                    f"Verification failed: step '{name}' has sequenceNumber "
                    f"{added_seq}, expected {target_seq - 1} (immediately before "
                    f"'{target}' at {target_seq})."
                )
        elif placement.get("sequenceNumber") is not None:
            want = placement["sequenceNumber"]
            if added_seq != want:
                raise TaskOptionsError(
                    f"Verification failed: step '{name}' has sequenceNumber "
                    f"{added_seq}, expected {want}."
                )


# ======================================================================
# ImportExpressionSet
# ======================================================================


class ImportExpressionSet(ExpressionSetConnectBase):
    """Import (create or replace) an expression set from a JSON file."""

    task_options = {
        **ExpressionSetConnectBase.task_options,
        "input_file": {
            "description": "Path to the full expression set definition JSON.",
            "required": True,
        },
        "dry_run": {
            "description": "Log changes without modifying the org.",
            "required": False,
        },
        "skip_validation": {
            "description": (
                "Skip the schema pre-flight on the input definition "
                "(default: false — validation blocks on errors)."
            ),
            "required": False,
        },
        "normalize_html_entities": {
            "description": (
                "HTML-unescape (&quot;->\", &#39;->', etc.) all string leaves in "
                "the payload before the Connect call (default: true). Required to "
                "round-trip real GET output, whose serializer escapes "
                "JSON-in-string param/criteria/formula values. Set false only to "
                "reproduce the escape gack."
            ),
            "required": False,
        },
        "activate_after_import": {
            "description": "Activate version after import (default: true).",
            "required": False,
        },
        "cascade_deactivate_procedure_plan": {
            "description": (
                "Deactivate referencing procedure plan versions if needed (default: true)."
            ),
            "required": False,
        },
        "max_wait_seconds": {
            "description": "Max seconds to poll for activation state changes.",
            "required": False,
        },
        "poll_interval_seconds": {
            "description": "Seconds between activation state polls.",
            "required": False,
        },
    }

    def _run_task(self):
        input_path = Path(self.options["input_file"])
        if not input_path.exists():
            raise TaskOptionsError(f"Input file not found: {input_path}")

        payload = json.loads(input_path.read_text(encoding="utf-8"))
        api_name = payload.get("apiName")
        if not api_name:
            raise TaskOptionsError("Input JSON must contain 'apiName' field.")

        # Pre-flight: validate the full definition before any create/replace.
        self._preflight_validate_definition(payload)

        dry_run = self._bool_option(self.options.get("dry_run"), False)
        activate_after = self._bool_option(
            self.options.get("activate_after_import"), True
        )
        cascade = self._bool_option(
            self.options.get("cascade_deactivate_procedure_plan"), True
        )

        # Check if expression set already exists
        safe = self._soql_escape(api_name)
        existing = self._soql_query(
            f"SELECT Id FROM ExpressionSetDefinition WHERE DeveloperName = '{safe}'"
        )

        if existing:
            es_def_id = existing[0]["Id"]
            es_id = self._get_expression_set_id(api_name)
            self.logger.info("Expression set '%s' exists, updating...", api_name)
            esv = self._resolve_version_by_es_id(es_id)

            # Align ResourceInitializationType to the value the PATCH body will
            # carry, before touching activation state.
            self._ensure_resource_initialization_type(
                es_id, dry_run, payload.get("resourceInitializationType")
            )

            def mutate():
                if dry_run:
                    self.logger.info("[dry-run] Would PATCH expression set %s.", es_id)
                    return
                patch_payload = self._strip_readonly_fields(payload)
                patch_payload = self._normalize_html_entities(patch_payload)
                self._patch_expression_set_via_connect(es_id, patch_payload)
                self.logger.info("Imported (updated) expression set %s.", es_id)

            self._run_connect_mutation(
                es_def_id=es_def_id,
                esv=esv,
                mutate=mutate,
                dry_run=dry_run,
                activate_after=activate_after,
                cascade=cascade,
                verb="Import",
            )
        else:
            self.logger.info("Expression set '%s' does not exist, creating...", api_name)
            if dry_run:
                self.logger.info("[dry-run] Would POST new expression set.")
            else:
                # A POST-create must OMIT the version-level `id` (for_create):
                # a source-org id from a GET export makes the server reject or
                # mis-bind the new version.
                create_payload = self._strip_readonly_fields(payload, for_create=True)
                create_payload = self._normalize_html_entities(create_payload)
                result = self._post_expression_set_via_connect(create_payload)
                es_id = result.get("id")
                if not es_id:
                    raise TaskOptionsError(
                        "Connect POST returned no expression set id; the create "
                        f"may not have committed. Response: {result!r}"
                    )
                self.logger.info("Created expression set %s (Id: %s).", api_name, es_id)

                # The created version's active state comes from the payload's
                # `enabled` flag. Honor activate_after_import explicitly so the
                # option is meaningful on create, not just on replace.
                esv = self._resolve_version_by_es_id(es_id)
                if activate_after and not bool(esv.get("IsActive")):
                    self._set_version_active(esv["Id"], True, dry_run)
                    self._wait_for_version_state(esv["Id"], True)
                elif not activate_after and bool(esv.get("IsActive")):
                    self.logger.info(
                        "activate_after_import=false; leaving created "
                        "ExpressionSetVersion %s deactivated.", esv["Id"]
                    )
                    self._set_version_active(esv["Id"], False, dry_run)
                    self._wait_for_version_state(esv["Id"], False)

        self.logger.info("Import complete for '%s'.", api_name)


# ======================================================================
# DeleteExpressionSet
# ======================================================================


class DeleteExpressionSet(ExpressionSetConnectBase):
    """Delete an expression set, or just a single (old) version.

    Two modes:
      * Whole expression set (default): DELETE the Connect resource. Any
        enabled version must be deactivated first.
      * Single version (``version_api_name``): delete just that
        ExpressionSetVersion via the sObject API — used by the
        post-new-version → delete-old-version workflow, leaving the
        expression set and its other versions intact.

    Destructive: requires ``confirm: true`` (or ``dry_run: true``).
    """

    task_options = {
        **ExpressionSetConnectBase.task_options,
        "expression_set_api_name": {
            "description": "DeveloperName of the expression set to delete from.",
            "required": True,
        },
        "version_api_name": {
            "description": (
                "If set, delete only this ExpressionSetVersion (by ApiName) "
                "rather than the whole expression set."
            ),
            "required": False,
        },
        "confirm": {
            "description": "Must be true to actually delete (guard).",
            "required": False,
        },
        "dry_run": {
            "description": "Log what would be deleted without deleting.",
            "required": False,
        },
        "max_wait_seconds": {
            "description": "Max seconds to poll for activation state changes.",
            "required": False,
        },
        "poll_interval_seconds": {
            "description": "Seconds between activation state polls.",
            "required": False,
        },
    }

    def _run_task(self):
        api_name = self.options["expression_set_api_name"]
        version_api_name = self.options.get("version_api_name")
        dry_run = self._bool_option(self.options.get("dry_run"), False)
        confirm = self._bool_option(self.options.get("confirm"), False)

        if not confirm and not dry_run:
            raise TaskOptionsError(
                "Refusing to delete without confirmation. Pass -o confirm true "
                "(or -o dry_run true to preview)."
            )

        es_id = self._get_expression_set_id(api_name)

        if version_api_name:
            self._delete_single_version(version_api_name, dry_run)
            return

        # Whole expression set: deactivate any enabled version first.
        esv = self._resolve_version_by_es_id(es_id)
        if bool(esv.get("IsActive")):
            self._set_version_active(esv["Id"], False, dry_run)
            if not dry_run:
                self._wait_for_version_state(esv["Id"], False)

        if dry_run:
            self.logger.info(
                "[dry-run] Would DELETE expression set %s (%s).", api_name, es_id
            )
            return
        self._delete_expression_set_via_connect(es_id)
        self.logger.info("Deleted expression set %s (%s).", api_name, es_id)

    def _delete_single_version(self, version_api_name: str, dry_run: bool):
        safe = self._soql_escape(version_api_name)
        records = self._soql_query(
            "SELECT Id, IsActive FROM ExpressionSetVersion "
            f"WHERE ApiName = '{safe}'"
        )
        if not records:
            raise TaskOptionsError(
                f"ExpressionSetVersion '{version_api_name}' not found."
            )
        version_id = records[0]["Id"]
        if bool(records[0].get("IsActive")):
            # An enabled version cannot be deleted; deactivate first.
            self._set_version_active(version_id, False, dry_run)
            if not dry_run:
                self._wait_for_version_state(version_id, False)
        if dry_run:
            self.logger.info(
                "[dry-run] Would delete ExpressionSetVersion %s (%s).",
                version_api_name, version_id,
            )
            return
        self._delete_sobject("ExpressionSetVersion", version_id)
        self.logger.info(
            "Deleted ExpressionSetVersion %s (%s).", version_api_name, version_id
        )


# ======================================================================
# ValidateExpressionSet (org-less)
# ======================================================================


class ValidateExpressionSet(BaseTask):
    """Validate an expression set definition or overlay JSON against the schema.

    Org-less: runs the same pre-flight validator the apply/import tasks use
    (tasks/expression_set_schema.py). Auto-detects overlay vs definition shape
    unless ``kind`` is given. Fails the task on schema errors (and on warnings
    when ``strict`` is true).
    """

    task_options = {
        "file": {
            "description": "Path to the definition or overlay JSON to validate.",
            "required": True,
        },
        "kind": {
            "description": "Force 'overlay' or 'definition' (default: auto-detect).",
            "required": False,
        },
        "strict": {
            "description": "Treat warnings as failures (default: false).",
            "required": False,
        },
    }

    @staticmethod
    def _bool_option(value, default):
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        return str(value).lower() in ("true", "1", "yes")

    def _run_task(self):
        path = Path(self.options["file"])
        if not path.exists():
            raise TaskOptionsError(f"File not found: {path}")
        data = json.loads(path.read_text(encoding="utf-8"))

        kind = self.options.get("kind")
        if not kind:
            kind = "overlay" if (isinstance(data, dict) and data.keys() & OVERLAY_OPS) \
                else ("definition" if isinstance(data, dict) and "versions" in data
                      else "overlay")

        result = validate_definition(data) if kind == "definition" else validate_overlay(data)

        for issue in result.warnings:
            self.logger.warning("%s: %s", issue.location, issue.message)
        for issue in result.errors:
            self.logger.error("%s: %s", issue.location, issue.message)

        strict = self._bool_option(self.options.get("strict"), False)
        if result.errors or (strict and result.warnings):
            raise TaskOptionsError(
                f"Schema validation failed for {path} as {kind}: "
                f"{len(result.errors)} error(s), {len(result.warnings)} warning(s)."
            )
        self.logger.info(
            "Schema validation passed for %s as %s (%d warning(s)).",
            path, kind, len(result.warnings),
        )
