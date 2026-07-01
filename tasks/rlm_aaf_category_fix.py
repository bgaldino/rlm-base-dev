"""Fix Category__r.Code in mfg-aaf extraction output.

SFDMU v5 extraction returns #N/A for custom relationship traversal fields like
Category__r.Code even when the org has the data. This task queries the org for
AdvAccountForecastFact records (Name, Category__r.Code), then merges the values
into the extracted AdvAccountForecastFact.csv files (raw and processed).
"""

import csv
import json
import os
import subprocess

from cumulusci.core.exceptions import CommandException
from cumulusci.tasks.salesforce import BaseSalesforceTask

from tasks.rlm_sfdmu import strip_ansi_codes


class FixAAFCategoryExtraction(BaseSalesforceTask):
    """Fix Category__r.Code in mfg-aaf extraction output.

    Queries the org for AdvAccountForecastFact.Name and Category__r.Code, then
    replaces #N/A in the extracted AdvAccountForecastFact.csv with the org values.
    Updates both the raw extraction CSV and the processed/ copy if present.
    """

    task_options = {
        "extraction_dir": {
            "description": (
                "Path to the extraction output directory (e.g. datasets/sfdmu/extractions/mfg-aaf/2026-03-15T131820). "
                "If omitted, uses the most recent extraction in datasets/sfdmu/extractions/mfg-aaf/."
            ),
            "required": False,
        },
        "sourceusername": {
            "description": "Username or alias of the org to query for Category__r.Code. Defaults to the current CCI org.",
            "required": False,
        },
    }

    def _run_task(self) -> None:
        extraction_dir = self.options.get("extraction_dir")
        if not extraction_dir:
            extraction_dir = self._find_latest_extraction()
        if not extraction_dir or not os.path.isdir(extraction_dir):
            raise CommandException(f"Extraction directory not found: {extraction_dir}")

        org_alias = self.options.get("sourceusername") or getattr(
            self.org_config, "username", None
        )
        if not org_alias:
            raise CommandException(
                "No org specified. Provide sourceusername or run with an org context."
            )

        # Query org for Name -> Category__r.Code
        name_to_code = self._query_category_codes(org_alias)
        if not name_to_code:
            self.logger.info("No AdvAccountForecastFact records with Category found in org")
            return

        self.logger.info(f"Queried {len(name_to_code)} AdvAccountForecastFact records with Category__r.Code")

        # Fix raw AdvAccountForecastFact.csv
        raw_csv = os.path.join(extraction_dir, "AdvAccountForecastFact.csv")
        if os.path.isfile(raw_csv):
            fixed = self._fix_csv(raw_csv, name_to_code)
            self.logger.info(f"Fixed raw AdvAccountForecastFact.csv: {fixed} rows updated")
        else:
            self.logger.warning(f"Raw AdvAccountForecastFact.csv not found: {raw_csv}")

        # Fix processed/AdvAccountForecastFact.csv if present
        processed_csv = os.path.join(extraction_dir, "processed", "AdvAccountForecastFact.csv")
        if os.path.isfile(processed_csv):
            fixed = self._fix_csv(processed_csv, name_to_code)
            self.logger.info(f"Fixed processed/AdvAccountForecastFact.csv: {fixed} rows updated")

    def _find_latest_extraction(self) -> str | None:
        """Return the most recent extraction dir in datasets/sfdmu/extractions/mfg-aaf/."""
        repo_root = getattr(self.project_config, "repo_root", None) or os.getcwd()
        base = os.path.join(repo_root, "datasets", "sfdmu", "extractions", "mfg-aaf")
        if not os.path.isdir(base):
            return None
        subdirs = [d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d))]
        if not subdirs:
            return None
        subdirs.sort(reverse=True)  # Timestamps sort lexicographically
        return os.path.join(base, subdirs[0])

    def _query_category_codes(self, org_alias: str) -> dict:
        """Query org for AdvAccountForecastFact Name and Category__r.Code. Returns {Name: Code}."""
        result = subprocess.run(
            [
                "sf", "data", "query",
                "-q", "SELECT Name, Category__r.Code FROM AdvAccountForecastFact WHERE Category__c != null",
                "-o", org_alias,
                "--json",
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise CommandException(
                f"AdvAccountForecastFact query failed: {strip_ansi_codes(result.stderr or result.stdout)}"
            )
        data = json.loads(result.stdout)
        records = data.get("result", {}).get("records") or []
        return {r["Name"]: r["Category__r"]["Code"] for r in records if r.get("Category__r", {}).get("Code")}

    def _fix_csv(self, csv_path: str, name_to_code: dict) -> int:
        """Replace #N/A in Category__r.Code column with org values. Returns count of rows updated."""
        with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            fieldnames = list(reader.fieldnames or [])

        # Find Category__r.Code and Name columns (handle BOM/quoted headers)
        def _norm(h: str) -> str:
            s = h.strip().lstrip("\ufeff").strip()
            while len(s) >= 2 and s[0] == '"' and s[-1] == '"':
                s = s[1:-1].strip()
            return s

        cat_col = name_col = None
        for fn in fieldnames:
            n = _norm(fn)
            if n == "Category__r.Code":
                cat_col = fn
            elif n == "Name":
                name_col = fn
        if not cat_col:
            self.logger.warning(f"Category__r.Code column not found in {csv_path}")
            return 0
        if not name_col:
            self.logger.warning(f"Name column not found in {csv_path}")
            return 0

        fixed = 0
        for row in rows:
            if row.get(cat_col) in ("#N/A", ""):
                name = row.get(name_col, "")
                code = name_to_code.get(name)
                if code:
                    row[cat_col] = code
                    fixed += 1

        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)

        return fixed
