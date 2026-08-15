"""
CumulusCI task for managing CustomFulfillmentScopeCnfg via Tooling API.

CustomFulfillmentScopeCnfg is a DRO/Industries Fulfillment setup object
introduced in API v65.0. It is inaccessible via standard SOAP/REST APIs
(apiAccess="never") and must be accessed through the Tooling API at:
  /services/data/v{api_version}/tooling/sobjects/CustomFulfillmentScopeCnfg

Supported operations:
  list     — query records and log to console
  extract  — query records and write to output_file (JSON array)
  upsert   — read records from input_file and create/update in target org
"""
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from cumulusci.core.tasks import BaseTask
    from cumulusci.core.exceptions import TaskOptionsError
except ImportError:
    BaseTask = object
    TaskOptionsError = Exception

OBJECT_NAME = "CustomFulfillmentScopeCnfg"
DEFAULT_OUTPUT_FILE = "datasets/tooling/CustomFulfillmentScopeCnfg.json"
MIN_API_VERSION = "65.0"

# Release 264 ships the standard SalesTransactionItemGroup context attribute typed
# `lookup`, while this object's own validation demands String -- two platform-shipped
# things disagreeing, so no repo-side data change can satisfy both. A 262 org (and any
# org upgraded from one) has it typed `string` and is unaffected.
#
# The tolerance below is deliberately narrow. It is not "continue on error": a record is
# skipped only when the org itself confirms the referenced tag resolves to a non-String
# attribute. A misspelled or missing tag still fails, which is the distinction that makes
# this a workaround for a platform defect rather than a mask over a repo defect. It also
# self-retires -- once the attribute is typed String the create simply succeeds and this
# code never runs.
_CONTEXT_TAG_TYPE_ERROR_CODE = "INVALID_INPUT"
_CONTEXT_TAG_TYPE_MARKERS = ("item context tag", "string")
_CONTEXT_TAG_FIELD = "ItemContextTag"

# The tolerance is pinned to the one platform defect it was written for: 264 ships the
# SalesTransactionItemGroup context tag against a lookup-typed attribute, while
# CustomFulfillmentScopeCnfg still requires String. Both halves are asserted, so a
# different tag, or this tag typed anything else, re-raises instead of being skipped.
# Widening either half would let genuine repo data errors pass silently.
_TOLERATED_CONTEXT_TAG = "salestransactionitemgroup"
_TOLERATED_CONTEXT_TAG_DATA_TYPE = "lookup"


class ToolingWriteError(TaskOptionsError):
    """A Tooling API write was rejected. Carries the response for classification.

    Subclasses TaskOptionsError and keeps the same message text, so any caller that
    does not catch it behaves exactly as before.
    """

    def __init__(self, message: str, status_code: int = 0, body: str = ""):
        super().__init__(message)
        self.status_code = status_code
        self.body = body


class ManageFulfillmentScopeCnfg(BaseTask):
    task_options = {
        "operation": {
            "description": (
                "Operation to perform: 'list' (log to console), "
                "'extract' (write to output_file), 'upsert' (import from input_file)."
            ),
            "required": True,
        },
        "output_file": {
            "description": (
                f"Path to write extracted records (JSON array). "
                f"Default: {DEFAULT_OUTPUT_FILE}. Used by 'extract' only."
            ),
            "required": False,
        },
        "input_file": {
            "description": (
                "Path to JSON file (array) with records to upsert. "
                "Required for 'upsert' operation."
            ),
            "required": False,
        },
        "key_field": {
            "description": (
                "Field used to match existing records during upsert. "
                "Default: DeveloperName."
            ),
            "required": False,
        },
        "api_version": {
            "description": (
                f"Salesforce API version override (minimum {MIN_API_VERSION}). "
                "Default: project/org version."
            ),
            "required": False,
        },
        "dry_run": {
            "description": "If true, log intended changes without writing to the org.",
            "required": False,
        },
        "on_invalid_context_tag": {
            "description": (
                "What to do when the org rejects a record because its "
                f"{_CONTEXT_TAG_FIELD} resolves to a context attribute that is not "
                "typed String: 'fail' (default) or 'skip'. 'skip' is verified against "
                "the org before it applies -- a missing or misspelled tag still fails. "
                "Note this is invisible under dry_run: no create is attempted, so a "
                "fresh 264 org logs 'Would CREATE' and looks healthy."
            ),
            "required": False,
        },
    }

    # Fields that are read-only / system-managed and must not be sent on write
    _READONLY_FIELDS = frozenset(
        {"Id", "CreatedDate", "LastModifiedDate", "CreatedById", "LastModifiedById",
         "SystemModstamp", "NamespacePrefix", "attributes"}
    )

    # Preferred display/export field order (subset; describe drives actual selection)
    _PREFERRED_FIELDS = [
        "Id", "DeveloperName", "MasterLabel", "Language", "NamespacePrefix",
        "Description", "IsActive",
    ]

    # ------------------------------------------------------------------ #
    # Entry point                                                           #
    # ------------------------------------------------------------------ #

    def _run_task(self):
        operation = self.options.get("operation", "").lower().strip()
        if operation == "list":
            self._list_records()
        elif operation == "extract":
            self._extract_records()
        elif operation == "upsert":
            self._upsert_records()
        else:
            raise TaskOptionsError(
                f"operation must be one of: 'list', 'extract', 'upsert'. Got: {operation!r}"
            )

    # ------------------------------------------------------------------ #
    # Shared helpers                                                        #
    # ------------------------------------------------------------------ #

    def _get_api_context(self):
        if not hasattr(self, "org_config") or not self.org_config:
            raise TaskOptionsError("No org_config available — pass --org <alias>")

        access_token = self.org_config.access_token
        instance_url = self.org_config.instance_url

        api_version = (
            self.options.get("api_version")
            or getattr(self.org_config, "api_version", None)
            or getattr(
                self.project_config, "project__package__api_version", "68.0"
            )
        )
        # Enforce minimum version
        try:
            if float(api_version) < float(MIN_API_VERSION):
                self.logger.warning(
                    f"api_version {api_version} is below the minimum {MIN_API_VERSION} "
                    f"required by {OBJECT_NAME}. Upgrading to {MIN_API_VERSION}."
                )
                api_version = MIN_API_VERSION
        except ValueError:
            raise TaskOptionsError(
                f"api_version '{api_version}' is not a valid numeric version. "
                f"Expected a value like '{MIN_API_VERSION}'."
            )

        return access_token, instance_url, api_version

    def _headers(self, access_token: str) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    def _describe(
        self, access_token: str, instance_url: str, api_version: str
    ) -> Dict[str, Any]:
        import requests

        url = (
            f"{instance_url}/services/data/v{api_version}"
            f"/tooling/sobjects/{OBJECT_NAME}/describe"
        )
        resp = requests.get(url, headers=self._headers(access_token))
        if not resp.ok:
            raise TaskOptionsError(
                f"Tooling describe failed for {OBJECT_NAME}: "
                f"{resp.status_code} — {resp.text}"
            )
        return resp.json()

    def _query(
        self, access_token: str, instance_url: str, api_version: str, soql: str
    ) -> List[Dict[str, Any]]:
        import requests

        url = f"{instance_url}/services/data/v{api_version}/tooling/query"
        resp = requests.get(
            url, headers=self._headers(access_token), params={"q": soql}
        )
        if not resp.ok:
            raise TaskOptionsError(
                f"Tooling query failed: {resp.status_code} — {resp.text}"
            )
        body = resp.json()
        records = body.get("records", [])
        # Handle pagination — follow nextRecordsUrl until all pages are fetched
        while not body.get("done", True) and body.get("nextRecordsUrl"):
            next_url = f"{instance_url}{body['nextRecordsUrl']}"
            resp = requests.get(next_url, headers=self._headers(access_token))
            if not resp.ok:
                self.logger.warning(
                    f"Pagination request failed: {resp.status_code} — {resp.text}; "
                    f"returning {len(records)} records fetched so far"
                )
                break
            body = resp.json()
            records.extend(body.get("records", []))
        for rec in records:
            rec.pop("attributes", None)
        return records

    def _build_select_fields(self, describe: Dict[str, Any]) -> List[str]:
        available = {f["name"] for f in describe.get("fields", [])}
        ordered = [f for f in self._PREFERRED_FIELDS if f in available]
        # Append any remaining fields not already in the ordered list
        for f in sorted(available - set(ordered)):
            ordered.append(f)
        return ordered

    # ------------------------------------------------------------------ #
    # Operations                                                            #
    # ------------------------------------------------------------------ #

    def _list_records(self):
        access_token, instance_url, api_version = self._get_api_context()
        describe = self._describe(access_token, instance_url, api_version)
        select_fields = self._build_select_fields(describe)

        soql = f"SELECT {', '.join(select_fields)} FROM {OBJECT_NAME}"
        records = self._query(access_token, instance_url, api_version, soql)

        if not records:
            self.logger.info(f"No {OBJECT_NAME} records found.")
            return

        self.logger.info(f"Found {len(records)} {OBJECT_NAME} record(s):")
        for rec in records:
            self.logger.info(json.dumps(rec, indent=2))

    def _extract_records(self):
        access_token, instance_url, api_version = self._get_api_context()
        describe = self._describe(access_token, instance_url, api_version)
        select_fields = self._build_select_fields(describe)

        soql = f"SELECT {', '.join(select_fields)} FROM {OBJECT_NAME}"
        records = self._query(access_token, instance_url, api_version, soql)

        output_file = self.options.get("output_file") or DEFAULT_OUTPUT_FILE
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as fh:
            json.dump(records, fh, indent=2)

        self.logger.info(
            f"Extracted {len(records)} {OBJECT_NAME} record(s) → {output_path}"
        )

    def _upsert_records(self):
        input_file = self.options.get("input_file")
        if not input_file:
            raise TaskOptionsError("input_file is required for upsert operation")
        if not os.path.isfile(input_file):
            raise TaskOptionsError(f"input_file not found: {input_file}")

        with open(input_file, "r", encoding="utf-8") as fh:
            payload = json.load(fh)
        if not isinstance(payload, list):
            raise TaskOptionsError("input_file must contain a JSON array of records")

        key_field = self.options.get("key_field") or "DeveloperName"
        dry_run = str(self.options.get("dry_run", "")).lower() in {"1", "true", "yes"}
        on_invalid_context_tag = (
            str(self.options.get("on_invalid_context_tag") or "fail").lower().strip()
        )
        if on_invalid_context_tag not in {"fail", "skip"}:
            raise TaskOptionsError(
                "on_invalid_context_tag must be 'fail' or 'skip'. "
                f"Got: {on_invalid_context_tag!r}"
            )

        access_token, instance_url, api_version = self._get_api_context()
        describe = self._describe(access_token, instance_url, api_version)
        available_fields = {f["name"] for f in describe.get("fields", [])}

        if key_field not in available_fields:
            raise TaskOptionsError(
                f"key_field '{key_field}' is not a field on {OBJECT_NAME}. "
                f"Available: {sorted(available_fields)}"
            )

        # Validate key_field is a text-like type suitable for SOQL string literals
        text_types = {"string", "textarea", "id", "reference", "url", "email", "phone", "picklist"}
        key_field_type = None
        for f in describe.get("fields", []):
            if f["name"] == key_field:
                key_field_type = f.get("type", "").lower()
                break
        if key_field_type and key_field_type not in text_types:
            raise TaskOptionsError(
                f"key_field '{key_field}' is type '{key_field_type}' — only text-like fields "
                f"({', '.join(sorted(text_types))}) are supported for upsert matching."
            )

        writable_fields = {
            f["name"]
            for f in describe.get("fields", [])
            if not f.get("calculated", False) and f.get("name") not in self._READONLY_FIELDS
        }

        created = updated = skipped = 0
        blocked: List[tuple] = []

        # Validate all records and collect key values up-front
        key_values = []
        seen_keys: Dict[str, int] = {}
        for idx, record in enumerate(payload):
            if not isinstance(record, dict):
                raise TaskOptionsError(f"Each record must be a JSON object, got: {record!r}")
            key_value = record.get(key_field)
            if key_value is None or key_value == "":
                raise TaskOptionsError(
                    f"Record is missing key_field '{key_field}': {record}"
                )
            key_str = str(key_value)
            if key_str in seen_keys:
                raise TaskOptionsError(
                    f"Duplicate key_field value '{key_str}' at records "
                    f"{seen_keys[key_str]} and {idx}"
                )
            seen_keys[key_str] = idx
            key_values.append(key_value)

        # Bulk-query existing records to build a key→Id lookup map
        # Process in chunks of 50 to stay within SOQL length limits
        existing_map: Dict[str, str] = {}
        chunk_size = 50
        for i in range(0, len(key_values), chunk_size):
            chunk = key_values[i : i + chunk_size]
            escaped = [str(v).replace(chr(39), chr(92) + chr(39)) for v in chunk]
            in_clause = ", ".join(f"'{v}'" for v in escaped)
            records = self._query(
                access_token,
                instance_url,
                api_version,
                f"SELECT Id, {key_field} FROM {OBJECT_NAME} WHERE {key_field} IN ({in_clause})",
            )
            for rec in records:
                existing_map[str(rec[key_field])] = rec["Id"]

        self.logger.info(
            f"Found {len(existing_map)} existing record(s) out of {len(key_values)} to upsert"
        )

        for record, key_value in zip(payload, key_values):
            # Strip read-only and unavailable fields before sending
            cleaned = {
                k: v
                for k, v in record.items()
                if k in writable_fields and k not in self._READONLY_FIELDS
            }

            record_id = existing_map.get(str(key_value))

            if record_id:
                # Remove key field from PATCH body — it's already matched
                patch_body = {k: v for k, v in cleaned.items() if k != key_field}
                if dry_run:
                    self.logger.info(
                        f"[dry-run] Would UPDATE {key_field}={key_value} ({record_id})"
                    )
                    skipped += 1
                    continue
                # The update path is deliberately intolerant: no try/except, and
                # _update_record raises TaskOptionsError rather than ToolingWriteError.
                # Today it is unreachable for the affected tag -- the create never
                # succeeds, so no record exists to update -- and an existing record
                # proves the org already accepted the tag. If the platform ever starts
                # re-validating ItemContextTag on PATCH, this is where it will surface
                # as a hard failure with no banner.
                self._update_record(access_token, instance_url, api_version, record_id, patch_body)
                self.logger.info(f"Updated {key_field}={key_value} ({record_id})")
                updated += 1
            else:
                if dry_run:
                    self.logger.info(f"[dry-run] Would CREATE {key_field}={key_value}")
                    skipped += 1
                    continue
                try:
                    new_id = self._create_record(
                        access_token, instance_url, api_version, cleaned
                    )
                except ToolingWriteError as exc:
                    if on_invalid_context_tag != "skip":
                        raise
                    try:
                        tolerated = self._is_platform_context_tag_defect(
                            exc, record, access_token, instance_url, api_version
                        )
                    except Exception as verify_exc:
                        # Verification queries the org, so it can fail on its own terms.
                        # If it does, the operator must still see the create rejection --
                        # otherwise the headline error becomes a ContextTag query problem
                        # and sends them to investigate Context Service instead of the
                        # record that actually failed. Being unable to verify must never
                        # change which error gets reported.
                        self.logger.warning(
                            f"  Could not verify whether {key_field}={key_value} hit the "
                            f"known platform defect ({verify_exc}). Reporting the "
                            "original create failure."
                        )
                        raise exc from verify_exc
                    if not tolerated:
                        raise
                    self.logger.warning(
                        f"SKIPPED {key_field}={key_value} — blocked by a platform "
                        "context-attribute type mismatch, not by anything in this repo."
                    )
                    blocked.append((str(key_value), str(record.get(_CONTEXT_TAG_FIELD))))
                    continue
                self.logger.info(f"Created {key_field}={key_value} ({new_id})")
                created += 1

        if dry_run:
            self.logger.info(f"[dry-run] {skipped} record(s) would be processed.")
        else:
            self.logger.info(
                f"Upsert complete — created: {created}, updated: {updated}"
                + (f", skipped: {len(blocked)}" if blocked else "")
            )

        # Loud on purpose. The task exits 0 so the build can proceed, which means this
        # banner is the only signal that the org is missing configuration -- a one-line
        # count would read as success in a 40-minute build log.
        if blocked:
            self.logger.warning("")
            self.logger.warning("=" * 72)
            self.logger.warning(
                f"{len(blocked)} {OBJECT_NAME} record(s) NOT created — platform defect"
            )
            self.logger.warning("=" * 72)
            for key_value, tag in blocked:
                self.logger.warning(f"  {key_value}  ({_CONTEXT_TAG_FIELD}: {tag})")
            self.logger.warning("")
            self.logger.warning(
                f"Each references a context attribute this org does not type as String, "
                f"which {OBJECT_NAME} requires. Both sides are platform-shipped, so no "
                "change to this repo can satisfy them at once."
            )
            self.logger.warning(
                "Fulfillment scoping on the affected tag(s) is unconfigured until the "
                "attribute is typed String; tolerated here via "
                "on_invalid_context_tag=skip. Remove that option once the platform "
                "agrees with itself and this will create normally."
            )
            self.logger.warning(
                "Downstream data still references the missing scope and will load "
                "without error, because CustomFulfillmentScope and "
                "CustomDecompositionScope are plain string fields rather than lookups: "
                "in datasets/sfdmu/qb/en-US/qb-dro, 8 Product2 rows "
                "(CustomDecompositionScope) and 1 FulfillmentStepDefinition row "
                "(CustomFulfillmentScope) name Group_Identifier. Those 9 records will "
                "look configured and behave as though they are not."
            )
            self.logger.warning("=" * 72)

    # ------------------------------------------------------------------ #
    # Tooling API write helpers                                             #
    # ------------------------------------------------------------------ #

    def _create_record(
        self,
        access_token: str,
        instance_url: str,
        api_version: str,
        body: Dict[str, Any],
    ) -> Optional[str]:
        import requests

        url = (
            f"{instance_url}/services/data/v{api_version}"
            f"/tooling/sobjects/{OBJECT_NAME}"
        )
        resp = requests.post(url, headers=self._headers(access_token), json=body)
        if not resp.ok:
            raise ToolingWriteError(
                f"Tooling create failed: {resp.status_code} — {resp.text}",
                status_code=resp.status_code,
                body=resp.text,
            )
        return resp.json().get("id")

    # ------------------------------------------------------------------ #
    # Platform context-tag type defect (264)                                #
    # ------------------------------------------------------------------ #

    def _data_query(
        self, access_token: str, instance_url: str, api_version: str, soql: str
    ) -> List[Dict[str, Any]]:
        """Query via the regular Data API.

        Separate from `_query`, which targets /tooling/query because this task's own
        object is Tooling-only. ContextTag and ContextAttribute are ordinary objects and
        are not addressable there.
        """
        import requests

        url = f"{instance_url}/services/data/v{api_version}/query"
        resp = requests.get(
            url, headers=self._headers(access_token), params={"q": soql}
        )
        if not resp.ok:
            raise TaskOptionsError(
                f"Data query failed: {resp.status_code} — {resp.text}"
            )
        return resp.json().get("records", [])

    @staticmethod
    def _looks_like_context_tag_type_error(exc: ToolingWriteError) -> bool:
        """True only if EVERY error in the response is the 'tag must be typed String'
        rejection.

        Deliberately all-not-any. The Tooling API returns an array, and a record can be
        rejected for the known type mismatch *and* something unrelated in the same
        response. Matching on any one entry would let the tolerance swallow the whole
        record and silently discard the second, genuine failure. Requiring every entry to
        match means a mixed response re-raises with both errors intact.

        An empty or unparseable array is not a match: absence of evidence is not evidence
        that this is the known defect.
        """
        try:
            errors = json.loads(exc.body)
        except (ValueError, TypeError):
            return False
        if isinstance(errors, dict):
            errors = [errors]
        if not isinstance(errors, list) or not errors:
            return False
        for err in errors:
            if not isinstance(err, dict):
                return False
            if err.get("errorCode") != _CONTEXT_TAG_TYPE_ERROR_CODE:
                return False
            message = str(err.get("message", "")).lower()
            if not all(marker in message for marker in _CONTEXT_TAG_TYPE_MARKERS):
                return False
        return True

    def _context_tag_data_type(
        self,
        access_token: str,
        instance_url: str,
        api_version: str,
        tag_title: str,
    ) -> Tuple[str, Optional[str]]:
        """Resolve the data type of the attribute behind a context tag.

        Returns a (status, value) pair rather than an Optional[str] because the four
        outcomes need different handling and collapsing them to None conflated two of
        them:

          ("ok", "<type>")        exactly one distinct type across all matching tags
          ("missing", None)       no ContextTag has this Title
          ("unreadable", None)    tag rows came back, but no DataType did -- what FLS on
                                  ContextAttribute.DataType looks like, which is a
                                  permissions problem and not a repo data defect
          ("ambiguous", "a, b")   matching tags disagree about the type

        The tag's name lives in ContextTag.Title, not Name -- ContextTag has no Name
        field at all.

        Ambiguity is a real possibility, not a hypothetical: tag titles are unique per
        context definition, not per org, and this repo itself ships a
        SalesTransactionItemGroup tag inside RLM_SalesTransactionContext. A first-hit
        read of an unordered, unscoped query would therefore let row order decide
        whether the tolerance fires. Reporting the disagreement instead turns a silent
        coin-flip into something an operator can act on.
        """
        # Escape backslash first, then quote: reversing the order would double-escape
        # the backslashes this very call introduces and terminate the literal early.
        escaped = str(tag_title).replace("\\", "\\\\").replace("'", "\\'")
        records = self._data_query(
            access_token,
            instance_url,
            api_version,
            "SELECT ContextAttribute.DataType FROM ContextTag "
            f"WHERE Title = '{escaped}'",
        )
        if not records:
            return ("missing", None)
        found = []
        for rec in records:
            attribute = rec.get("ContextAttribute") or {}
            data_type = attribute.get("DataType")
            if data_type and str(data_type) not in found:
                found.append(str(data_type))
        if not found:
            return ("unreadable", None)
        if len(found) > 1:
            return ("ambiguous", ", ".join(sorted(found)))
        return ("ok", found[0])

    def _is_platform_context_tag_defect(
        self,
        exc: ToolingWriteError,
        record: Dict[str, Any],
        access_token: str,
        instance_url: str,
        api_version: str,
    ) -> bool:
        """Confirm against the org that this rejection is the one known platform defect.

        Every gate must pass: the response must be entirely the type-mismatch rejection,
        the record's tag must be the specific tag the defect affects, and the org must
        report that tag as the specific type the defect produces. Anything else returns
        False so the caller re-raises, because a tolerance that fires on a rejection it
        was not written for hides real defects instead of documenting one.
        """
        if not self._looks_like_context_tag_type_error(exc):
            return False
        tag = record.get(_CONTEXT_TAG_FIELD)
        if not tag:
            return False
        if str(tag).lower() != _TOLERATED_CONTEXT_TAG:
            self.logger.error(
                f"  {_CONTEXT_TAG_FIELD} '{tag}' is not the tag the known 264 defect "
                f"affects ('{_TOLERATED_CONTEXT_TAG}') — not skipping."
            )
            return False
        status, data_type = self._context_tag_data_type(
            access_token, instance_url, api_version, tag
        )
        if status == "missing":
            self.logger.error(
                f"  {_CONTEXT_TAG_FIELD} '{tag}' does not resolve to a context tag on "
                "this org. That is a data defect, not the known platform type "
                "mismatch — not skipping."
            )
            return False
        if status == "unreadable":
            self.logger.error(
                f"  {_CONTEXT_TAG_FIELD} '{tag}' resolved to a context tag, but its "
                "attribute type was not readable. That usually means field-level "
                "security on ContextAttribute.DataType rather than a missing tag, so "
                "this cannot be confirmed as the known defect — not skipping."
            )
            return False
        if status == "ambiguous":
            self.logger.error(
                f"  {_CONTEXT_TAG_FIELD} '{tag}' matches context tags that disagree "
                f"about the attribute type ({data_type}). Tag titles are unique per "
                "context definition, not per org, so this cannot be resolved without "
                "knowing which definition applies — not skipping."
            )
            return False
        if data_type.lower() != _TOLERATED_CONTEXT_TAG_DATA_TYPE:
            self.logger.error(
                f"  {_CONTEXT_TAG_FIELD} '{tag}' resolves to a '{data_type}'-typed "
                f"attribute, not the '{_TOLERATED_CONTEXT_TAG_DATA_TYPE}' type the known "
                "defect produces, so the rejection is about something else — not skipping."
            )
            return False
        self.logger.warning(
            f"  {_CONTEXT_TAG_FIELD} '{tag}' resolves to a '{data_type}'-typed context "
            "attribute, but this object requires String. Confirmed against the org."
        )
        return True

    def _update_record(
        self,
        access_token: str,
        instance_url: str,
        api_version: str,
        record_id: str,
        body: Dict[str, Any],
    ):
        import requests

        url = (
            f"{instance_url}/services/data/v{api_version}"
            f"/tooling/sobjects/{OBJECT_NAME}/{record_id}"
        )
        resp = requests.patch(url, headers=self._headers(access_token), json=body)
        if resp.status_code not in (200, 204):
            raise TaskOptionsError(
                f"Tooling update failed: {resp.status_code} — {resp.text}"
            )
