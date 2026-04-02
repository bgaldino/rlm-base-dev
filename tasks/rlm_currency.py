import csv
import json
import os
import urllib.request
from typing import Any, Dict

try:
    from cumulusci.tasks.salesforce import BaseSalesforceApiTask
    from cumulusci.core.tasks import BaseTask
    from cumulusci.core.exceptions import TaskOptionsError
except ImportError:
    BaseSalesforceApiTask = object
    BaseTask = object
    TaskOptionsError = Exception

RATES_API_URL = "https://open.er-api.com/v6/latest/USD"
DEFAULT_CURRENCY_CSV = "datasets/sfdmu/qb/en-US/qb-pricing/CurrencyType.csv"


def _fetch_rates(logger) -> Dict[str, float]:
    """Fetch live USD-based exchange rates from ExchangeRate-API (open.er-api.com, no auth required)."""
    logger.info(f"Fetching exchange rates from {RATES_API_URL}")
    try:
        with urllib.request.urlopen(RATES_API_URL, timeout=10) as resp:
            data = json.loads(resp.read().decode())
    except Exception as e:
        raise TaskOptionsError(f"Failed to fetch exchange rates: {e}")
    if data.get("result") != "success":
        raise TaskOptionsError(f"Exchange rate API returned non-success: {data}")
    logger.info(f"Received rates for {len(data['rates'])} currencies.")
    return data["rates"]  # {ISO_CODE: units_per_usd}


class UpdateCurrencyRatesCsv(BaseTask):
    """Fetch live exchange rates and update CurrencyType.csv in the SFDMU plan.

    Updates the plan CSV so future scratch org builds use current rates.
    Rates are expressed as units of the currency per 1 USD (Salesforce convention).
    """

    task_options: Dict[str, Dict[str, Any]] = {
        "csv_path": {
            "description": f"Path to CurrencyType.csv. Defaults to {DEFAULT_CURRENCY_CSV}.",
            "required": False,
        },
        "iso_codes": {
            "description": (
                "Optional comma-separated list of ISO codes to update (e.g. 'EUR,GBP'). "
                "If omitted, all non-corporate currencies in the CSV are updated."
            ),
            "required": False,
        },
        "dry_run": {
            "description": "If True, log the rates that would be applied without writing the CSV.",
            "required": False,
        },
    }

    def _run_task(self) -> None:
        dry_run = self.options.get("dry_run", False)
        if isinstance(dry_run, str):
            dry_run = dry_run.lower() in ("true", "1", "yes")

        iso_filter = self.options.get("iso_codes")
        if iso_filter:
            iso_filter = {c.strip().upper() for c in iso_filter.split(",")}

        csv_path = self.options.get("csv_path", DEFAULT_CURRENCY_CSV)
        if not os.path.isfile(csv_path):
            raise TaskOptionsError(f"CurrencyType CSV not found: {csv_path}")

        rates = _fetch_rates(self.logger)

        rows = []
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for row in reader:
                rows.append(row)

        updated = 0
        for row in rows:
            iso = row.get("IsoCode", "")
            if row.get("IsCorporate", "").lower() == "true":
                continue
            if iso_filter and iso not in iso_filter:
                continue
            if iso not in rates:
                self.logger.warning(f"No rate available for {iso} — skipping.")
                continue
            new_rate = round(rates[iso], 6)
            old_rate = row["ConversionRate"]
            self.logger.info(f"{iso}: {old_rate} -> {new_rate}")
            if not dry_run:
                row["ConversionRate"] = str(new_rate)
            updated += 1

        if not dry_run:
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            self.logger.info(f"Updated {updated} rate(s) in {csv_path}")
        else:
            self.logger.info(f"Dry run — would update {updated} rate(s) in {csv_path}")


class UpdateCurrencyRates(BaseSalesforceApiTask):
    """Fetch live exchange rates and update CurrencyType.ConversionRate in the org.

    Patches each active non-corporate CurrencyType record via the Salesforce REST API.
    Use this to refresh a running org without a full rebuild.
    """

    task_options: Dict[str, Dict[str, Any]] = {
        "iso_codes": {
            "description": (
                "Optional comma-separated list of ISO codes to update (e.g. 'EUR,GBP'). "
                "If omitted, all active non-corporate currencies in the org are updated."
            ),
            "required": False,
        },
        "dry_run": {
            "description": "If True, log the rates that would be applied without updating the org.",
            "required": False,
        },
    }

    def _run_task(self) -> None:
        dry_run = self.options.get("dry_run", False)
        if isinstance(dry_run, str):
            dry_run = dry_run.lower() in ("true", "1", "yes")

        iso_filter = self.options.get("iso_codes")
        if iso_filter:
            iso_filter = {c.strip().upper() for c in iso_filter.split(",")}

        rates = _fetch_rates(self.logger)

        soql = "SELECT Id, IsoCode, ConversionRate FROM CurrencyType WHERE IsActive = true AND IsCorporate = false"
        records = self.sf.query(soql).get("records", [])
        if not records:
            self.logger.warning("No active non-corporate CurrencyType records found in org.")
            return

        updated = 0
        for record in records:
            iso = record["IsoCode"]
            if iso_filter and iso not in iso_filter:
                continue
            if iso not in rates:
                self.logger.warning(f"No rate available for {iso} — skipping.")
                continue
            new_rate = round(rates[iso], 6)
            old_rate = record["ConversionRate"]
            self.logger.info(f"{iso}: {old_rate} -> {new_rate}")
            if not dry_run:
                self.sf.CurrencyType.update(record["Id"], {"ConversionRate": new_rate})
            updated += 1

        action = "Would update" if dry_run else "Updated"
        self.logger.info(f"{action} {updated} currency rate(s) in org.")
