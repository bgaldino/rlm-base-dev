"""Load Advanced Account Forecast (AAF) data with Period lookup resolution.

AAF data plans use Period as a Readonly reference object. With excludeIdsFromCSVFiles
true, Period.csv has no Id column, so SFDMU cannot resolve Period.FullyQualifiedLabel
to PeriodId when inserting AdvAccountForecastFact. This task syncs Period Ids from
the target org, merges them into Period.csv, and injects PeriodId directly into
AdvAccountForecastFact.csv so SFDMU sends it on insert.
"""

import csv
import json
import os
import shutil
import subprocess
import tempfile

from tasks.rlm_sfdmu import LoadSFDMUData, strip_ansi_codes
from cumulusci.core.exceptions import CommandException


class LoadAAFData(LoadSFDMUData):
    """Load AAF data with Period Id sync from target org.

    Copies the plan to a temp dir, queries the target org for Period (Id, FullyQualifiedLabel),
    merges Id into Period.csv, injects PeriodId into AdvAccountForecastFact.csv, then runs
    SFDMU against the temp copy so the version-controlled dataset is not modified.
    """

    task_options = {
        **LoadSFDMUData.task_options,
        "debug_no_temp_copy": {
            "description": "If true, skip temp copy and run against plan dir directly. Leaves source/target for inspection. Modifies plan CSVs in place.",
            "required": False,
        },
    }

    def _prep_runtime(self) -> None:
        super()._prep_runtime()
        if not self.options.get("debug_no_temp_copy"):
            self._copy_plan_to_temp()
        self._sync_period_ids_from_org()

    def _copy_plan_to_temp(self) -> None:
        """Copy plan to temp dir so we can modify CSVs without touching the repo.
        Excludes source/ and target/ so SFDMU starts fresh (avoids stale working copies).
        """
        source_dir = self.pathtoexportjson
        self._temp_plan_dir = tempfile.mkdtemp(prefix="sfdmu_aaf_")
        exclude_dirs = {"source", "target"}
        for item in os.listdir(source_dir):
            if item in exclude_dirs:
                continue
            src = os.path.join(source_dir, item)
            dst = os.path.join(self._temp_plan_dir, item)
            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
        self.pathtoexportjson = self._temp_plan_dir
        self.logger.info(f"Copied AAF plan to temp dir for PeriodId injection")

    def _sync_period_ids_from_org(self) -> None:
        """Query target org for Period, Product2, and ProductCategory records, merge Ids
        into reference CSVs, and inject PeriodId, ProductId, and CategoryId into
        AdvAccountForecastFact.csv so SFDMU sends them directly on insert.
        """
        plan_dir = self.pathtoexportjson
        period_csv = os.path.join(plan_dir, "Period.csv")
        product_csv = os.path.join(plan_dir, "Product2.csv")
        category_csv = os.path.join(plan_dir, "ProductCategory.csv")
        fact_csv = os.path.join(plan_dir, "AdvAccountForecastFact.csv")

        if not os.path.isfile(period_csv):
            self.logger.info("Period.csv not found, skipping sync")
            return

        org_for_cli = str(getattr(self.org_config, "username", None) or self.targetusername)

        # Query Period
        result = subprocess.run(
            ["sf", "data", "query", "-q", "SELECT Id, FullyQualifiedLabel FROM Period", "-o", org_for_cli, "--json"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise CommandException(f"Period query failed: {strip_ansi_codes(result.stderr or result.stdout)}")
        records = json.loads(result.stdout).get("result", {}).get("records") or []
        fql_to_id = {r["FullyQualifiedLabel"]: r["Id"] for r in records if r.get("FullyQualifiedLabel")}
        self.logger.info(f"Queried {len(fql_to_id)} Period records from org")

        # Merge Id into Period.csv
        self._merge_id_into_csv(period_csv, "FullyQualifiedLabel", fql_to_id, "Period")

        # Query Product2
        result = subprocess.run(
            ["sf", "data", "query", "-q", "SELECT Id, StockKeepingUnit FROM Product2", "-o", org_for_cli, "--json"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise CommandException(f"Product2 query failed: {strip_ansi_codes(result.stderr or result.stdout)}")
        records = json.loads(result.stdout).get("result", {}).get("records") or []
        sku_to_id = {r["StockKeepingUnit"]: r["Id"] for r in records if r.get("StockKeepingUnit")}
        self.logger.info(f"Queried {len(sku_to_id)} Product2 records from org")

        # Merge Id into Product2.csv
        if os.path.isfile(product_csv):
            self._merge_id_into_csv(product_csv, "StockKeepingUnit", sku_to_id, "Product2")

        # Query ProductCategory and merge Id into ProductCategory.csv
        code_to_id = {}
        if os.path.isfile(category_csv):
            result = subprocess.run(
                ["sf", "data", "query", "-q", "SELECT Id, Code FROM ProductCategory", "-o", org_for_cli, "--json"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                records = json.loads(result.stdout).get("result", {}).get("records") or []
                code_to_id = {r["Code"]: r["Id"] for r in records if r.get("Code")}
                self.logger.info(f"Queried {len(code_to_id)} ProductCategory records from org")
                self._merge_id_into_csv(category_csv, "Code", code_to_id, "ProductCategory")
            else:
                self.logger.warning(f"ProductCategory query failed: {strip_ansi_codes(result.stderr or result.stdout)}")

        # Inject PeriodId, ProductId, and CategoryId into AdvAccountForecastFact.csv
        if not os.path.isfile(fact_csv):
            return

        with open(fact_csv, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            raw_rows = list(reader)
            raw_fieldnames = list(reader.fieldnames or [])

        # Normalize fieldnames (fix BOM/corrupted headers like '"Name"') so SFDMU gets clean "Name"
        fact_fieldnames = [self._normalize_fieldname(f) for f in raw_fieldnames]
        fact_rows = []
        for r in raw_rows:
            clean = {self._normalize_fieldname(k): v for k, v in r.items()}
            fact_rows.append(clean)

        period_col = "Period.FullyQualifiedLabel"
        product_col = "Product.StockKeepingUnit"
        category_col = "Category__r.Code"
        if period_col not in fact_fieldnames or product_col not in fact_fieldnames:
            self.logger.info("AdvAccountForecastFact.csv missing required columns, skipping injection")
            return

        # Add PeriodId, ProductId, and Category__c columns if needed
        # Category__c is the lookup API name (not CategoryId)
        injections = [
            ("PeriodId", period_col, fql_to_id),
            ("ProductId", product_col, sku_to_id),
        ]
        if category_col in fact_fieldnames and code_to_id:
            injections.append(("Category__c", category_col, code_to_id))

        for col, key_col, lookup in injections:
            if col not in fact_fieldnames:
                fact_fieldnames.insert(fact_fieldnames.index(key_col) + 1, col)
            for row in fact_rows:
                val = row.get(key_col, "")
                row[col] = lookup.get(val, "")

        with open(fact_csv, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fact_fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(fact_rows)

        period_injected = sum(1 for r in fact_rows if r.get("PeriodId"))
        product_injected = sum(1 for r in fact_rows if r.get("ProductId"))
        category_injected = sum(1 for r in fact_rows if r.get("Category__c")) if code_to_id else 0
        self.logger.info(
            f"Injected PeriodId: {period_injected}/{len(fact_rows)}, "
            f"ProductId: {product_injected}/{len(fact_rows)}, "
            f"Category__c: {category_injected}/{len(fact_rows)} rows"
        )

    @staticmethod
    def _normalize_fieldname(fn: str) -> str:
        """Strip BOM and surrounding quotes so '\\ufeff\"Name\"' -> 'Name'."""
        s = fn.strip().lstrip("\ufeff").strip()
        while s.startswith('"') and s.endswith('"') and len(s) > 1:
            s = s[1:-1].strip()
        return s

    def _get_actual_key(self, fieldnames: list[str], normalized_key: str) -> str:
        """Return the actual CSV header that normalizes to normalized_key."""
        for f in fieldnames:
            if self._normalize_fieldname(f) == normalized_key:
                return f
        return normalized_key

    def _merge_id_into_csv(self, csv_path: str, key_field: str, lookup: dict, label: str) -> None:
        """Merge Id into a reference CSV by matching key_field to the lookup map.
        Normalizes output headers so SFDMU recognizes externalId fields (e.g. StockKeepingUnit).
        """
        with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            raw_rows = list(reader)
            raw_fieldnames = list(reader.fieldnames or [])

        key_actual = self._get_actual_key(raw_fieldnames, key_field)
        # Normalize headers and rows so SFDMU gets clean column names
        fieldnames = [self._normalize_fieldname(f) for f in raw_fieldnames]
        if not any(f == "Id" for f in fieldnames):
            fieldnames = ["Id"] + fieldnames

        rows = []
        for r in raw_rows:
            clean = {self._normalize_fieldname(k): v for k, v in r.items()}
            key_val = clean.get(self._normalize_fieldname(key_actual), "")
            clean["Id"] = lookup.get(key_val, "")
            rows.append(clean)

        matched = sum(1 for r in rows if r.get("Id"))

        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)

        self.logger.info(f"Merged {label} Ids: {matched}/{len(rows)} rows matched")
