"""
Apply JSON-defined Procedure Plan overlays using resolved Salesforce IDs.

The task is intended for feature overlays that need to patch active runtime
procedure plans without relying on SFDMU relationship-traversal upserts.
"""
from __future__ import annotations

import json
import os
import time
from typing import Any, Dict, Iterable, List, Optional

import requests

try:
    from cumulusci.core.exceptions import TaskOptionsError
    from cumulusci.tasks.salesforce import BaseSalesforceTask
except ImportError:
    BaseSalesforceTask = object
    TaskOptionsError = Exception


class ApplyProcedurePlanOverlay(BaseSalesforceTask):
    """Apply a ProcedurePlan overlay and restore activation state safely."""

    task_options: Dict[str, Dict[str, object]] = {
        "overlay_file": {
            "description": "Path to the JSON procedure-plan overlay declaration.",
            "required": True,
        },
        "developerName": {
            "description": "Optional ProcedurePlanDefinitionVersion DeveloperName override.",
            "required": False,
        },
        "api_version": {
            "description": "Salesforce API version override.",
            "required": False,
        },
        "dry_run": {
            "description": "If true, log intended changes without writing to the org.",
            "required": False,
        },
        "verify": {
            "description": "If true (default), verify exact overlay row counts after apply.",
            "required": False,
        },
        "activate_after_apply": {
            "description": (
                "If true (default), activate the target ProcedurePlanDefinitionVersion "
                "after overlay is applied. The try/finally block restores the original "
                "activation state on failure regardless of this setting."
            ),
            "required": False,
        },
        "max_wait_seconds": {
            "description": "Maximum seconds to wait for activation and verification.",
            "required": False,
        },
        "poll_interval_seconds": {
            "description": "Polling interval in seconds.",
            "required": False,
        },
    }

    @property
    def _api_version(self) -> str:
        return (
            self.options.get("api_version")
            or getattr(self.org_config, "api_version", None)
            or getattr(self.project_config, "project__package__api_version", "66.0")
        )

    @property
    def _base_url(self) -> str:
        return f"{self.org_config.instance_url}/services/data/v{self._api_version}"

    @property
    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.org_config.access_token}",
            "Content-Type": "application/json",
        }

    @staticmethod
    def _bool_option(value: Any, default: bool) -> bool:
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in {"1", "true", "yes", "y"}

    @staticmethod
    def _soql_escape(value: str) -> str:
        return value.replace("\\", "\\\\").replace("'", "\\'")

    @staticmethod
    def _clean_body(
        body: Dict[str, Any],
        preserve_null_fields: Iterable[str] = (),
    ) -> Dict[str, Any]:
        preserve_nulls = set(preserve_null_fields)
        return {
            key: value
            for key, value in body.items()
            if value is not None or key in preserve_nulls
        }

    @staticmethod
    def _values_equal(current: Any, desired: Any) -> bool:
        if current in (None, "") and desired in (None, ""):
            return True
        if isinstance(desired, int) and str(current) == str(desired):
            return True
        return current == desired

    def _query(self, soql: str) -> List[Dict[str, Any]]:
        response = requests.get(
            f"{self._base_url}/query",
            headers=self._headers,
            params={"q": soql},
            timeout=60,
        )
        if not response.ok:
            raise TaskOptionsError(f"SOQL query failed ({response.status_code}): {response.text}")

        body = response.json()
        records = body.get("records", [])
        while not body.get("done", True) and body.get("nextRecordsUrl"):
            response = requests.get(
                f"{self.org_config.instance_url}{body['nextRecordsUrl']}",
                headers=self._headers,
                timeout=60,
            )
            if not response.ok:
                raise TaskOptionsError(
                    f"SOQL pagination failed ({response.status_code}): {response.text}"
                )
            body = response.json()
            records.extend(body.get("records", []))

        for record in records:
            record.pop("attributes", None)
        return records

    def _patch_sobject(self, sobject: str, record_id: str, body: Dict[str, Any]):
        response = requests.patch(
            f"{self._base_url}/sobjects/{sobject}/{record_id}",
            headers=self._headers,
            json=body,
            timeout=60,
        )
        if response.status_code not in (200, 204):
            raise TaskOptionsError(
                f"Update {sobject} {record_id} failed ({response.status_code}): {response.text}"
            )

    def _post_sobject(self, sobject: str, body: Dict[str, Any]) -> str:
        response = requests.post(
            f"{self._base_url}/sobjects/{sobject}",
            headers=self._headers,
            json=body,
            timeout=60,
        )
        if not response.ok:
            raise TaskOptionsError(
                f"Create {sobject} failed ({response.status_code}): {response.text}"
            )
        return response.json()["id"]

    def _load_overlay(self) -> Dict[str, Any]:
        overlay_file = self.options["overlay_file"]
        if not os.path.isfile(overlay_file):
            raise TaskOptionsError(f"overlay_file not found: {overlay_file}")
        with open(overlay_file, "r", encoding="utf-8") as handle:
            overlay = json.load(handle)
        if not isinstance(overlay, dict):
            raise TaskOptionsError("overlay_file must contain a JSON object")
        return overlay

    def _get_version(self, developer_name: str) -> Dict[str, Any]:
        safe_name = self._soql_escape(developer_name)
        records = self._query(
            "SELECT Id, DeveloperName, IsActive, Rank, EffectiveFrom "
            "FROM ProcedurePlanDefinitionVersion "
            f"WHERE DeveloperName = '{safe_name}' "
            "ORDER BY IsActive DESC, Rank DESC, EffectiveFrom DESC "
            "LIMIT 1"
        )
        if not records:
            raise TaskOptionsError(
                f"No ProcedurePlanDefinitionVersion found for DeveloperName '{developer_name}'"
            )
        return records[0]

    def _set_version_active(self, version_id: str, active: bool, dry_run: bool):
        if dry_run:
            self.logger.info("[dry-run] Would set ProcedurePlanDefinitionVersion %s IsActive=%s", version_id, active)
            return
        self._patch_sobject(
            "ProcedurePlanDefinitionVersion",
            version_id,
            {"IsActive": active},
        )
        self.logger.info(
            "Set ProcedurePlanDefinitionVersion %s IsActive=%s.",
            version_id,
            active,
        )

    def _wait_for_active_state(self, version_id: str, active: bool):
        max_wait = int(self.options.get("max_wait_seconds", 45))
        interval = max(1, int(self.options.get("poll_interval_seconds", 3)))
        waited = 0
        while waited <= max_wait:
            records = self._query(
                "SELECT Id, IsActive FROM ProcedurePlanDefinitionVersion "
                f"WHERE Id = '{self._soql_escape(version_id)}'"
            )
            if records and bool(records[0].get("IsActive")) is active:
                self.logger.info(
                    "Confirmed ProcedurePlanDefinitionVersion %s IsActive=%s after %ss.",
                    version_id,
                    active,
                    waited,
                )
                return
            time.sleep(interval)
            waited += interval
        raise TaskOptionsError(
            f"ProcedurePlanDefinitionVersion {version_id} did not report "
            f"IsActive={active} within {max_wait}s."
        )

    def _get_section_records(self, version_id: str, sub_section_type: str) -> List[Dict[str, Any]]:
        safe_version_id = self._soql_escape(version_id)
        safe_sub_section = self._soql_escape(sub_section_type)
        return self._query(
            "SELECT Id, Description, Phase, ResolutionType, SectionType, Sequence, SubSectionType "
            "FROM ProcedurePlanSection "
            f"WHERE ProcedurePlanVersionId = '{safe_version_id}' "
            f"AND SubSectionType = '{safe_sub_section}'"
        )

    def _get_all_section_records(self, version_id: str) -> List[Dict[str, Any]]:
        safe_version_id = self._soql_escape(version_id)
        return self._query(
            "SELECT Id, Description, Phase, ResolutionType, SectionType, Sequence, SubSectionType "
            "FROM ProcedurePlanSection "
            f"WHERE ProcedurePlanVersionId = '{safe_version_id}' "
            "ORDER BY Sequence ASC, SubSectionType ASC"
        )

    def _require_unique_section(self, version_id: str, sub_section_type: str) -> Dict[str, Any]:
        records = self._get_section_records(version_id, sub_section_type)
        if len(records) != 1:
            raise TaskOptionsError(
                f"Expected exactly one ProcedurePlanSection for {sub_section_type}; "
                f"found {len(records)}."
            )
        return records[0]

    def _upsert_section(self, version_id: str, section: Dict[str, Any], dry_run: bool):
        sub_section_type = section["subSectionType"]
        if "sequence" in section and "placement" in section:
            raise TaskOptionsError(
                f"ProcedurePlanSection {sub_section_type} cannot define both "
                "sequence and placement."
            )
        records = self._get_section_records(version_id, sub_section_type)
        if len(records) > 1:
            raise TaskOptionsError(
                f"Expected at most one ProcedurePlanSection for {sub_section_type}; found {len(records)}."
            )

        sequence = section.get("sequence")
        if sequence is None and not records:
            existing_sequences = [
                int(record["Sequence"])
                for record in self._get_all_section_records(version_id)
                if record.get("Sequence") is not None
            ]
            sequence = (max(existing_sequences) + 1) if existing_sequences else 1

        body = {
            "Description": section.get("description"),
            "Phase": section.get("phase"),
            "ProcedurePlanVersionId": version_id,
            "ResolutionType": section.get("resolutionType"),
            "SectionType": section.get("sectionType"),
            "SubSectionType": sub_section_type,
        }
        if sequence is not None:
            body["Sequence"] = sequence

        body = self._clean_body(
            {
                key: value
                for key, value in body.items()
            },
            preserve_null_fields=("Description",),
        )

        if not records:
            if dry_run:
                self.logger.info("[dry-run] Would create ProcedurePlanSection %s.", sub_section_type)
                return
            record_id = self._post_sobject("ProcedurePlanSection", body)
            self.logger.info("Created ProcedurePlanSection %s (%s).", sub_section_type, record_id)
            return

        record = records[0]
        patch_body = {
            key: value
            for key, value in body.items()
            if key != "ProcedurePlanVersionId"
            and not self._values_equal(record.get(key), value)
        }
        if not patch_body:
            self.logger.info("No change for ProcedurePlanSection %s.", sub_section_type)
            return
        if dry_run:
            self.logger.info("[dry-run] Would update ProcedurePlanSection %s: %s", sub_section_type, patch_body)
            return
        self._patch_sobject("ProcedurePlanSection", record["Id"], patch_body)
        self.logger.info("Updated ProcedurePlanSection %s.", sub_section_type)

    def _move_section(self, version_id: str, move: Dict[str, Any], dry_run: bool):
        sub_section_type = move["subSectionType"]
        section = self._require_unique_section(version_id, sub_section_type)
        sequence = move["sequence"]
        if section.get("Sequence") == sequence:
            self.logger.info("No change for ProcedurePlanSection %s sequence.", sub_section_type)
            return
        if dry_run:
            self.logger.info(
                "[dry-run] Would move ProcedurePlanSection %s to sequence %s.",
                sub_section_type,
                sequence,
            )
            return
        self._patch_sobject("ProcedurePlanSection", section["Id"], {"Sequence": sequence})
        self.logger.info("Moved ProcedurePlanSection %s to sequence %s.", sub_section_type, sequence)

    def _resequence_sections(
        self,
        version_id: str,
        sections: List[Dict[str, Any]],
        dry_run: bool,
    ):
        if not sections:
            return

        current_sequences = [
            int(section["Sequence"])
            for section in sections
            if section.get("Sequence") is not None
        ]
        start = min(current_sequences) if current_sequences else 1
        max_sequence = max(current_sequences) if current_sequences else start

        desired_by_id = {
            section["Id"]: start + idx for idx, section in enumerate(sections)
        }
        changed = [
            section
            for section in sections
            if not self._values_equal(
                section.get("Sequence"),
                desired_by_id[section["Id"]],
            )
        ]
        if not changed:
            self.logger.info("No section resequencing required.")
            return

        if dry_run:
            for section in changed:
                self.logger.info(
                    "[dry-run] Would resequence ProcedurePlanSection %s from %s to %s.",
                    section["SubSectionType"],
                    section.get("Sequence"),
                    desired_by_id[section["Id"]],
                )
            return

        # Move changed sections out of the active range first so final sequence
        # patches do not collide with sections that have not moved yet.
        temp_start = max_sequence + 1000
        for idx, section in enumerate(changed):
            self._patch_sobject(
                "ProcedurePlanSection",
                section["Id"],
                {"Sequence": temp_start + idx},
            )

        for section in changed:
            desired_sequence = desired_by_id[section["Id"]]
            self._patch_sobject(
                "ProcedurePlanSection",
                section["Id"],
                {"Sequence": desired_sequence},
            )
            self.logger.info(
                "Resequenced ProcedurePlanSection %s from %s to %s.",
                section["SubSectionType"],
                section.get("Sequence"),
                desired_sequence,
            )

    def _apply_section_placements(
        self,
        version_id: str,
        overlay: Dict[str, Any],
        dry_run: bool,
    ):
        placed_sections = [
            section for section in overlay.get("sections", []) if section.get("placement")
        ]
        if not placed_sections:
            return

        section_order = self._get_all_section_records(version_id)
        section_by_type = {}
        for section in section_order:
            sub_section_type = section["SubSectionType"]
            if sub_section_type in section_by_type:
                raise TaskOptionsError(
                    "Cannot place overlay sections because duplicate "
                    f"ProcedurePlanSection SubSectionType exists: {sub_section_type}"
                )
            section_by_type[sub_section_type] = section

        last_insert_for_anchor: Dict[str, str] = {}
        for section_spec in placed_sections:
            sub_section_type = section_spec["subSectionType"]
            placement = section_spec["placement"]
            anchor = placement.get("afterSubSectionType") or placement.get("after")
            if not anchor:
                raise TaskOptionsError(
                    f"ProcedurePlanSection {sub_section_type} placement requires "
                    "afterSubSectionType."
                )
            if sub_section_type == anchor:
                raise TaskOptionsError(
                    f"ProcedurePlanSection {sub_section_type} cannot be placed after itself."
                )
            if sub_section_type not in section_by_type:
                raise TaskOptionsError(
                    f"Cannot place missing ProcedurePlanSection {sub_section_type}."
                )
            if anchor not in section_by_type:
                raise TaskOptionsError(
                    f"Cannot place {sub_section_type}; anchor section {anchor} was not found."
                )

            insertion_anchor = last_insert_for_anchor.get(anchor, anchor)
            section_order = [
                section
                for section in section_order
                if section["SubSectionType"] != sub_section_type
            ]
            anchor_indexes = [
                idx
                for idx, section in enumerate(section_order)
                if section["SubSectionType"] == insertion_anchor
            ]
            if len(anchor_indexes) != 1:
                raise TaskOptionsError(
                    f"Cannot place {sub_section_type}; insertion anchor "
                    f"{insertion_anchor} was not found exactly once."
                )
            section_order.insert(
                anchor_indexes[0] + 1,
                section_by_type[sub_section_type],
            )
            last_insert_for_anchor[anchor] = sub_section_type

        self._resequence_sections(version_id, section_order, dry_run)

    def _get_expression_set_id(self, developer_name: str) -> str:
        safe_name = self._soql_escape(developer_name)
        records = self._query(
            "SELECT Id, DeveloperName FROM ExpressionSetDefinition "
            f"WHERE DeveloperName = '{safe_name}'"
        )
        if len(records) != 1:
            raise TaskOptionsError(
                f"Expected exactly one ExpressionSetDefinition for {developer_name}; found {len(records)}."
            )
        return records[0]["Id"]

    def _get_option_records(self, section_id: str, priority: Any) -> List[Dict[str, Any]]:
        safe_section_id = self._soql_escape(section_id)
        return self._query(
            "SELECT Id, CriteriaLogic, ExpressionSetDefinitionId, Priority, "
            "ReadContextMapping, SaveContextMapping "
            "FROM ProcedurePlanOption "
            f"WHERE ProcedurePlanSectionId = '{safe_section_id}' "
            f"AND Priority = {int(priority)}"
        )

    def _require_unique_option(self, version_id: str, option: Dict[str, Any]) -> Dict[str, Any]:
        section = self._require_unique_section(version_id, option["sectionSubSectionType"])
        records = self._get_option_records(section["Id"], option["priority"])
        if len(records) != 1:
            raise TaskOptionsError(
                "Expected exactly one ProcedurePlanOption for "
                f"{option['sectionSubSectionType']} priority {option['priority']}; found {len(records)}."
            )
        return records[0]

    def _upsert_option(self, version_id: str, option: Dict[str, Any], dry_run: bool):
        section = self._require_unique_section(version_id, option["sectionSubSectionType"])
        expression_set_id = self._get_expression_set_id(option["expressionSetDeveloperName"])
        records = self._get_option_records(section["Id"], option["priority"])
        if len(records) > 1:
            raise TaskOptionsError(
                "Expected at most one ProcedurePlanOption for "
                f"{option['sectionSubSectionType']} priority {option['priority']}; found {len(records)}."
            )

        body = self._clean_body(
            {
                "CriteriaLogic": option.get("criteriaLogic"),
                "ExpressionSetDefinitionId": expression_set_id,
                "Priority": option.get("priority"),
                "ProcedurePlanSectionId": section["Id"],
                "ReadContextMapping": option.get("readContextMapping"),
                "SaveContextMapping": option.get("saveContextMapping"),
            }
        )

        if not records:
            if dry_run:
                self.logger.info(
                    "[dry-run] Would create ProcedurePlanOption %s priority %s.",
                    option["sectionSubSectionType"],
                    option["priority"],
                )
                return
            record_id = self._post_sobject("ProcedurePlanOption", body)
            self.logger.info(
                "Created ProcedurePlanOption %s priority %s (%s).",
                option["sectionSubSectionType"],
                option["priority"],
                record_id,
            )
            return

        record = records[0]
        patch_body = {
            key: value
            for key, value in body.items()
            if key != "ProcedurePlanSectionId"
            and not self._values_equal(record.get(key), value)
        }
        if not patch_body:
            self.logger.info(
                "No change for ProcedurePlanOption %s priority %s.",
                option["sectionSubSectionType"],
                option["priority"],
            )
            return
        if dry_run:
            self.logger.info(
                "[dry-run] Would update ProcedurePlanOption %s priority %s: %s",
                option["sectionSubSectionType"],
                option["priority"],
                patch_body,
            )
            return
        self._patch_sobject("ProcedurePlanOption", record["Id"], patch_body)
        self.logger.info(
            "Updated ProcedurePlanOption %s priority %s.",
            option["sectionSubSectionType"],
            option["priority"],
        )

    def _get_criterion_records(self, option_id: str, sequence: Any) -> List[Dict[str, Any]]:
        safe_option_id = self._soql_escape(option_id)
        return self._query(
            "SELECT Id, ActualValue, DataType, FieldPath, ObjectField, Operator, Sequence "
            "FROM ProcedurePlanCriterion "
            f"WHERE ProcedurePlanOptionId = '{safe_option_id}' "
            f"AND Sequence = {int(sequence)}"
        )

    def _upsert_criterion(self, version_id: str, criterion: Dict[str, Any], dry_run: bool):
        option = self._require_unique_option(
            version_id,
            {
                "sectionSubSectionType": criterion["sectionSubSectionType"],
                "priority": criterion["optionPriority"],
            },
        )
        records = self._get_criterion_records(option["Id"], criterion["sequence"])
        if len(records) > 1:
            raise TaskOptionsError(
                "Expected at most one ProcedurePlanCriterion for "
                f"{criterion['sectionSubSectionType']} priority {criterion['optionPriority']} "
                f"sequence {criterion['sequence']}; found {len(records)}."
            )

        body = self._clean_body(
            {
                "ActualValue": criterion.get("actualValue"),
                "DataType": criterion.get("dataType"),
                "FieldPath": criterion.get("fieldPath"),
                "ObjectField": criterion.get("objectField"),
                "Operator": criterion.get("operator"),
                "ProcedurePlanOptionId": option["Id"],
                "Sequence": criterion.get("sequence"),
            },
            preserve_null_fields=("ActualValue",),
        )

        if not records:
            if dry_run:
                self.logger.info(
                    "[dry-run] Would create ProcedurePlanCriterion %s priority %s sequence %s.",
                    criterion["sectionSubSectionType"],
                    criterion["optionPriority"],
                    criterion["sequence"],
                )
                return
            record_id = self._post_sobject("ProcedurePlanCriterion", body)
            self.logger.info(
                "Created ProcedurePlanCriterion %s priority %s sequence %s (%s).",
                criterion["sectionSubSectionType"],
                criterion["optionPriority"],
                criterion["sequence"],
                record_id,
            )
            return

        record = records[0]
        patch_body = {
            key: value
            for key, value in body.items()
            if key != "ProcedurePlanOptionId"
            and not self._values_equal(record.get(key), value)
        }
        if not patch_body:
            self.logger.info(
                "No change for ProcedurePlanCriterion %s priority %s sequence %s.",
                criterion["sectionSubSectionType"],
                criterion["optionPriority"],
                criterion["sequence"],
            )
            return
        if dry_run:
            self.logger.info(
                "[dry-run] Would update ProcedurePlanCriterion %s priority %s sequence %s: %s",
                criterion["sectionSubSectionType"],
                criterion["optionPriority"],
                criterion["sequence"],
                patch_body,
            )
            return
        self._patch_sobject("ProcedurePlanCriterion", record["Id"], patch_body)
        self.logger.info(
            "Updated ProcedurePlanCriterion %s priority %s sequence %s.",
            criterion["sectionSubSectionType"],
            criterion["optionPriority"],
            criterion["sequence"],
        )

    def _apply_overlay(self, version_id: str, overlay: Dict[str, Any], dry_run: bool):
        for move in overlay.get("sectionMoves", []):
            self._move_section(version_id, move, dry_run)
        for section in overlay.get("sections", []):
            self._upsert_section(version_id, section, dry_run)
        self._apply_section_placements(version_id, overlay, dry_run)
        for option in overlay.get("options", []):
            self._upsert_option(version_id, option, dry_run)
        for criterion in overlay.get("criteria", []):
            self._upsert_criterion(version_id, criterion, dry_run)

    def _section_placements_valid(
        self,
        version_id: str,
        overlay: Dict[str, Any],
    ) -> bool:
        placed_sections = [
            section for section in overlay.get("sections", []) if section.get("placement")
        ]
        if not placed_sections:
            return True

        ordered_types = [
            section["SubSectionType"]
            for section in self._get_all_section_records(version_id)
        ]
        last_insert_for_anchor: Dict[str, str] = {}
        for section_spec in placed_sections:
            sub_section_type = section_spec["subSectionType"]
            placement = section_spec["placement"]
            anchor = placement.get("afterSubSectionType") or placement.get("after")
            if not anchor:
                return False
            insertion_anchor = last_insert_for_anchor.get(anchor, anchor)
            try:
                anchor_index = ordered_types.index(insertion_anchor)
            except ValueError:
                return False
            expected_index = anchor_index + 1
            if (
                expected_index >= len(ordered_types)
                or ordered_types[expected_index] != sub_section_type
            ):
                self.logger.info(
                    "Procedure-plan overlay placement not valid: expected %s "
                    "immediately after %s.",
                    sub_section_type,
                    insertion_anchor,
                )
                return False
            last_insert_for_anchor[anchor] = sub_section_type
        return True

    def _all_counts_valid(self, version_id: str, overlay: Dict[str, Any]) -> bool:
        expected_counts: Dict[str, int] = {}

        for section in overlay.get("sections", []):
            key = f"section:{section['subSectionType']}"
            expected_counts[key] = len(
                self._get_section_records(version_id, section["subSectionType"])
            )

        for option in overlay.get("options", []):
            section = self._require_unique_section(version_id, option["sectionSubSectionType"])
            expression_set_id = self._get_expression_set_id(option["expressionSetDeveloperName"])
            records = [
                row
                for row in self._get_option_records(section["Id"], option["priority"])
                if row.get("ExpressionSetDefinitionId") == expression_set_id
            ]
            key = f"option:{option['sectionSubSectionType']}:{option['priority']}"
            expected_counts[key] = len(records)

        for criterion in overlay.get("criteria", []):
            option = self._require_unique_option(
                version_id,
                {
                    "sectionSubSectionType": criterion["sectionSubSectionType"],
                    "priority": criterion["optionPriority"],
                },
            )
            records = [
                row
                for row in self._get_criterion_records(option["Id"], criterion["sequence"])
                if row.get("FieldPath") == criterion.get("fieldPath")
                and row.get("Operator") == criterion.get("operator")
            ]
            key = (
                f"criterion:{criterion['sectionSubSectionType']}:"
                f"{criterion['optionPriority']}:{criterion['sequence']}"
            )
            expected_counts[key] = len(records)

        if not self._section_placements_valid(version_id, overlay):
            return False

        invalid = {key: count for key, count in expected_counts.items() if count != 1}
        if invalid:
            self.logger.info(
                "Procedure-plan overlay verification counts not ready/valid: %s",
                invalid,
            )
            return False

        self.logger.info("Procedure-plan overlay verification passed: %s", expected_counts)
        return True

    def _verify_overlay(self, version_id: str, overlay: Dict[str, Any]):
        max_wait = int(self.options.get("max_wait_seconds", 45))
        interval = max(1, int(self.options.get("poll_interval_seconds", 3)))
        attempts = max(1, (max_wait // interval) + 1)
        for attempt in range(1, attempts + 1):
            if self._all_counts_valid(version_id, overlay):
                return
            if attempt < attempts:
                time.sleep(interval)
        raise TaskOptionsError("Procedure-plan overlay verification failed.")

    def _run_task(self):
        overlay = self._load_overlay()
        developer_name = self.options.get("developerName") or overlay.get("developerName")
        if not developer_name:
            raise TaskOptionsError("developerName is required in options or overlay_file")

        dry_run = self._bool_option(self.options.get("dry_run"), False)
        verify = self._bool_option(self.options.get("verify"), True)
        activate_after_apply = self._bool_option(
            self.options.get("activate_after_apply"),
            True,
        )

        version = self._get_version(str(developer_name))
        version_id = version["Id"]
        was_active = bool(version.get("IsActive"))
        deactivated = False
        failure: Optional[Exception] = None

        try:
            if was_active:
                self._set_version_active(version_id, False, dry_run)
                if not dry_run:
                    self._wait_for_active_state(version_id, False)
                deactivated = True
            else:
                self.logger.info(
                    "ProcedurePlanDefinitionVersion %s is already inactive before overlay.",
                    version_id,
                )

            self._apply_overlay(version_id, overlay, dry_run)
            if verify and not dry_run:
                self._verify_overlay(version_id, overlay)
        except Exception as exc:
            failure = exc
        finally:
            should_activate = activate_after_apply or (was_active and deactivated)
            if should_activate:
                try:
                    self._set_version_active(version_id, True, dry_run)
                    if not dry_run:
                        self._wait_for_active_state(version_id, True)
                except Exception as reactivate_exc:
                    if failure:
                        raise TaskOptionsError(
                            "Procedure-plan overlay failed, and reactivation also "
                            f"failed: {reactivate_exc}"
                        ) from failure
                    raise

        if failure:
            raise failure

        self.logger.info(
            "Applied procedure-plan overlay %s to %s.",
            self.options["overlay_file"],
            developer_name,
        )
