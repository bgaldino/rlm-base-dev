"""
Configure PricingRecipeTableMapping records via Tooling API.

This task ensures recipe-to-table mappings exist for pricing recipes (for example,
NGPDefaultRecipe) without requiring metadata deployment of the recipe itself.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Tuple

import requests

try:
    from cumulusci.core.tasks import BaseTask
    from cumulusci.core.exceptions import TaskOptionsError
except ImportError:
    BaseTask = object
    TaskOptionsError = Exception


OBJECT_NAME = "PricingRecipeTableMapping"
DEFAULT_INPUT_FILE = "datasets/tooling/PricingRecipeTableMappings/prm_ngp_default.json"


class ConfigurePricingRecipeTableMappings(BaseTask):
    task_options = {
        "operation": {
            "description": "Operation to perform: 'ensure' (default) or 'list'.",
            "required": False,
        },
        "input_file": {
            "description": (
                "Path to JSON array with mapping records. "
                f"Default: {DEFAULT_INPUT_FILE}"
            ),
            "required": False,
        },
        "api_version": {
            "description": "Salesforce API version override.",
            "required": False,
        },
        "dry_run": {
            "description": "If true, log intended changes without writing to org.",
            "required": False,
        },
        "skip_missing_tables": {
            "description": (
                "If true (default), warn and skip mappings whose DecisionTable "
                "DeveloperName is not found in the org."
            ),
            "required": False,
        },
    }

    def _run_task(self):
        operation = (self.options.get("operation") or "ensure").strip().lower()
        if operation not in {"ensure", "list"}:
            raise TaskOptionsError("operation must be 'ensure' or 'list'")

        mappings = self._load_mappings()
        if not mappings:
            self.logger.info("No mapping records provided. Nothing to do.")
            return

        access_token, instance_url, api_version = self._get_api_context()
        recipe_ids = self._get_recipe_ids(access_token, instance_url, api_version, mappings)
        table_ids = self._get_table_ids(access_token, instance_url, api_version, mappings)

        if operation == "list":
            self._list_current_mappings(
                access_token,
                instance_url,
                api_version,
                recipe_ids,
                table_ids,
            )
            return

        self._ensure_mappings(
            access_token,
            instance_url,
            api_version,
            mappings,
            recipe_ids,
            table_ids,
        )

    def _load_mappings(self) -> List[Dict[str, str]]:
        input_file = self.options.get("input_file") or DEFAULT_INPUT_FILE
        if not os.path.isfile(input_file):
            raise TaskOptionsError(f"input_file not found: {input_file}")

        with open(input_file, "r", encoding="utf-8") as handle:
            payload = json.load(handle)

        if not isinstance(payload, list):
            raise TaskOptionsError("input_file must contain a JSON array")

        normalized: List[Dict[str, str]] = []
        required = {
            "pricingRecipeDeveloperName",
            "decisionTableDeveloperName",
            "pricingComponentType",
        }
        for idx, row in enumerate(payload, start=1):
            if not isinstance(row, dict):
                raise TaskOptionsError(f"Row {idx} must be an object")
            missing = sorted(required - set(row))
            if missing:
                raise TaskOptionsError(f"Row {idx} missing required keys: {missing}")

            normalized.append(
                {
                    "pricingRecipeDeveloperName": str(
                        row["pricingRecipeDeveloperName"]
                    ).strip(),
                    "decisionTableDeveloperName": str(
                        row["decisionTableDeveloperName"]
                    ).strip(),
                    "pricingComponentType": str(row["pricingComponentType"]).strip(),
                }
            )
        return normalized

    def _get_api_context(self) -> Tuple[str, str, str]:
        if not hasattr(self, "org_config") or not self.org_config:
            raise TaskOptionsError("No org_config available — pass --org <alias>")

        access_token = self.org_config.access_token
        instance_url = self.org_config.instance_url
        api_version = (
            self.options.get("api_version")
            or getattr(self.org_config, "api_version", None)
            or getattr(self.project_config, "project__package__api_version", "66.0")
        )
        return access_token, instance_url, api_version

    def _headers(self, access_token: str) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    @staticmethod
    def _soql_escape(value: str) -> str:
        return value.replace("\\", "\\\\").replace("'", "\\'")

    def _query_tooling(
        self,
        access_token: str,
        instance_url: str,
        api_version: str,
        soql: str,
    ) -> List[Dict[str, Any]]:
        url = f"{instance_url}/services/data/v{api_version}/tooling/query"
        response = requests.get(
            url,
            headers=self._headers(access_token),
            params={"q": soql},
            timeout=30,
        )
        if not response.ok:
            raise TaskOptionsError(
                f"Tooling query failed ({response.status_code}): {response.text}"
            )
        body = response.json()
        records = body.get("records", [])
        while not body.get("done", True) and body.get("nextRecordsUrl"):
            next_url = f"{instance_url}{body['nextRecordsUrl']}"
            response = requests.get(
                next_url, headers=self._headers(access_token), timeout=30
            )
            if not response.ok:
                raise TaskOptionsError(
                    "Tooling query pagination failed "
                    f"({response.status_code}): {response.text}"
                )
            body = response.json()
            records.extend(body.get("records", []))
        for rec in records:
            rec.pop("attributes", None)
        return records

    def _post_tooling(
        self,
        access_token: str,
        instance_url: str,
        api_version: str,
        body: Dict[str, Any],
    ) -> str:
        url = f"{instance_url}/services/data/v{api_version}/tooling/sobjects/{OBJECT_NAME}"
        response = requests.post(
            url,
            headers=self._headers(access_token),
            json=body,
            timeout=30,
        )
        if not response.ok:
            raise TaskOptionsError(
                f"Create {OBJECT_NAME} failed ({response.status_code}): {response.text}"
            )
        return response.json()["id"]

    def _patch_tooling(
        self,
        access_token: str,
        instance_url: str,
        api_version: str,
        record_id: str,
        body: Dict[str, Any],
    ):
        url = (
            f"{instance_url}/services/data/v{api_version}/tooling/sobjects/"
            f"{OBJECT_NAME}/{record_id}"
        )
        response = requests.patch(
            url,
            headers=self._headers(access_token),
            json=body,
            timeout=30,
        )
        if response.status_code not in (200, 204):
            raise TaskOptionsError(
                f"Update {OBJECT_NAME} failed ({response.status_code}): {response.text}"
            )

    def _get_recipe_ids(
        self,
        access_token: str,
        instance_url: str,
        api_version: str,
        mappings: List[Dict[str, str]],
    ) -> Dict[str, str]:
        names = sorted({row["pricingRecipeDeveloperName"] for row in mappings})
        escaped = [f"'{self._soql_escape(name)}'" for name in names]
        soql = (
            "SELECT Id, DeveloperName FROM PricingRecipe "
            f"WHERE DeveloperName IN ({', '.join(escaped)})"
        )
        rows = self._query_tooling(access_token, instance_url, api_version, soql)
        by_name = {row["DeveloperName"]: row["Id"] for row in rows}

        missing = [name for name in names if name not in by_name]
        if missing:
            raise TaskOptionsError(
                "Missing PricingRecipe record(s): " + ", ".join(missing)
            )
        return by_name

    def _get_table_ids(
        self,
        access_token: str,
        instance_url: str,
        api_version: str,
        mappings: List[Dict[str, str]],
    ) -> Dict[str, str]:
        names = sorted({row["decisionTableDeveloperName"] for row in mappings})
        escaped = [f"'{self._soql_escape(name)}'" for name in names]
        soql = (
            "SELECT Id, DeveloperName FROM DecisionTable "
            f"WHERE DeveloperName IN ({', '.join(escaped)})"
        )
        rows = self._query_tooling(access_token, instance_url, api_version, soql)
        return {row["DeveloperName"]: row["Id"] for row in rows}

    def _get_existing_mappings(
        self,
        access_token: str,
        instance_url: str,
        api_version: str,
        recipe_ids: List[str],
    ) -> Dict[Tuple[str, str], Dict[str, Any]]:
        escaped = [f"'{self._soql_escape(recipe_id)}'" for recipe_id in recipe_ids]
        soql = (
            "SELECT Id, PricingRecipeId, LookupTableId, PricingComponentType "
            f"FROM {OBJECT_NAME} WHERE PricingRecipeId IN ({', '.join(escaped)})"
        )
        rows = self._query_tooling(access_token, instance_url, api_version, soql)
        return {(row["PricingRecipeId"], row["LookupTableId"]): row for row in rows}

    def _list_current_mappings(
        self,
        access_token: str,
        instance_url: str,
        api_version: str,
        recipe_ids: Dict[str, str],
        table_ids: Dict[str, str],
    ):
        existing = self._get_existing_mappings(
            access_token, instance_url, api_version, list(recipe_ids.values())
        )
        reverse_recipes = {v: k for k, v in recipe_ids.items()}
        reverse_tables = {v: k for k, v in table_ids.items()}

        if not existing:
            self.logger.info("No existing PricingRecipeTableMapping records found.")
            return

        self.logger.info("Current PricingRecipeTableMapping records for requested recipes:")
        for key in sorted(existing.keys()):
            row = existing[key]
            recipe_name = reverse_recipes.get(row["PricingRecipeId"], row["PricingRecipeId"])
            table_name = reverse_tables.get(row["LookupTableId"], row["LookupTableId"])
            self.logger.info(
                "- %s :: %s :: %s",
                recipe_name,
                table_name,
                row.get("PricingComponentType"),
            )

    def _ensure_mappings(
        self,
        access_token: str,
        instance_url: str,
        api_version: str,
        mappings: List[Dict[str, str]],
        recipe_ids: Dict[str, str],
        table_ids: Dict[str, str],
    ):
        dry_run = str(self.options.get("dry_run", "")).lower() in {"1", "true", "yes"}
        skip_missing_tables = (
            str(self.options.get("skip_missing_tables", "true")).lower()
            in {"1", "true", "yes"}
        )

        existing = self._get_existing_mappings(
            access_token, instance_url, api_version, list(recipe_ids.values())
        )
        creates = 0
        updates = 0
        skips = 0

        for mapping in mappings:
            recipe_name = mapping["pricingRecipeDeveloperName"]
            table_name = mapping["decisionTableDeveloperName"]
            component_type = mapping["pricingComponentType"]

            recipe_id = recipe_ids[recipe_name]
            table_id = table_ids.get(table_name)

            if not table_id:
                message = (
                    f"DecisionTable '{table_name}' not found; cannot map "
                    f"{recipe_name}::{table_name}."
                )
                if skip_missing_tables:
                    self.logger.warning("%s Skipping.", message)
                    skips += 1
                    continue
                raise TaskOptionsError(message)

            key = (recipe_id, table_id)
            current = existing.get(key)
            if not current:
                body = {
                    "PricingRecipeId": recipe_id,
                    "LookupTableId": table_id,
                    "PricingComponentType": component_type,
                }
                if dry_run:
                    self.logger.info(
                        "[dry-run] Would create mapping %s :: %s -> %s",
                        recipe_name,
                        table_name,
                        component_type,
                    )
                else:
                    self._post_tooling(access_token, instance_url, api_version, body)
                    self.logger.info(
                        "Created mapping %s :: %s -> %s",
                        recipe_name,
                        table_name,
                        component_type,
                    )
                creates += 1
                continue

            if current.get("PricingComponentType") == component_type:
                self.logger.info(
                    "No change for mapping %s :: %s (PricingComponentType=%s)",
                    recipe_name,
                    table_name,
                    component_type,
                )
                skips += 1
                continue

            patch_body = {"PricingComponentType": component_type}
            if dry_run:
                self.logger.info(
                    "[dry-run] Would update mapping %s :: %s from %s -> %s",
                    recipe_name,
                    table_name,
                    current.get("PricingComponentType"),
                    component_type,
                )
            else:
                self._patch_tooling(
                    access_token,
                    instance_url,
                    api_version,
                    current["Id"],
                    patch_body,
                )
                self.logger.info(
                    "Updated mapping %s :: %s from %s -> %s",
                    recipe_name,
                    table_name,
                    current.get("PricingComponentType"),
                    component_type,
                )
            updates += 1

        self.logger.info(
            "PricingRecipeTableMapping ensure complete: %s created, %s updated, %s unchanged/skipped.",
            creates,
            updates,
            skips,
        )
