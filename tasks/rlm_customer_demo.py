import csv
import json
import re
from typing import Dict, List, Tuple

import requests
from cumulusci.core.exceptions import TaskOptionsError
from cumulusci.tasks.salesforce import BaseSalesforceTask


def _escape_soql(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "\\'")


class RecreateCustomerDemoPricebookViaApi(BaseSalesforceTask):
    """Recreate Standard Pricebook rows with explicit ProductSellingModelId."""

    task_options = {
        "input_csv": {
            "description": "CSV with columns: SKU,UnitPrice,CurrencyIsoCode,PSMName,PSMSellingModelType,IsActive",
            "required": True,
        },
        "delete_first": {
            "description": "Delete existing Standard PricebookEntry rows for target SKUs before create (default true).",
            "required": False,
        },
    }

    def _api(self, method: str, path: str, body: Dict = None, params: Dict = None):
        url = f"{self.org_config.instance_url}/services/data/v66.0/{path.lstrip('/')}"
        headers = {
            "Authorization": f"Bearer {self.org_config.access_token}",
            "Content-Type": "application/json",
        }
        resp = requests.request(method, url, headers=headers, json=body, params=params, timeout=60)
        if resp.status_code >= 400:
            raise TaskOptionsError(f"API call failed ({resp.status_code}) {path}: {resp.text}")
        return resp.json() if resp.text else {}

    def _query(self, soql: str) -> List[Dict]:
        result = self._api("GET", "query", params={"q": soql})
        return result.get("records", [])

    def _read_rows(self) -> List[Dict]:
        input_csv = self.options["input_csv"]
        rows: List[Dict] = []
        with open(input_csv, "r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            required = {"SKU", "UnitPrice", "CurrencyIsoCode", "PSMName", "PSMSellingModelType"}
            missing = required - set(reader.fieldnames or [])
            if missing:
                raise TaskOptionsError(f"Missing required CSV columns: {sorted(missing)}")
            for row in reader:
                if not row.get("SKU"):
                    continue
                rows.append(row)
        if not rows:
            raise TaskOptionsError(f"No usable rows found in {input_csv}")
        return rows

    def _run_task(self):
        rows = self._read_rows()
        delete_first = str(self.options.get("delete_first", "true")).lower() not in {"0", "false", "no"}

        pb_records = self._query("SELECT Id FROM Pricebook2 WHERE IsStandard = true LIMIT 1")
        if not pb_records:
            raise TaskOptionsError("No Standard Pricebook found in target org.")
        standard_pricebook_id = pb_records[0]["Id"]

        sku_set = sorted({r["SKU"] for r in rows})
        sku_list = ",".join([f"'{_escape_soql(s)}'" for s in sku_set])
        products = self._query(
            f"SELECT Id, StockKeepingUnit FROM Product2 WHERE StockKeepingUnit IN ({sku_list})"
        )
        product_by_sku = {p["StockKeepingUnit"]: p["Id"] for p in products}

        missing_skus = [s for s in sku_set if s not in product_by_sku]
        if missing_skus:
            raise TaskOptionsError(f"Missing Product2 records for SKUs: {missing_skus}")

        psm_keys = sorted({(r["PSMName"], r["PSMSellingModelType"]) for r in rows})
        psm_by_key: Dict[str, str] = {}
        for name, model_type in psm_keys:
            name_esc = _escape_soql(name)
            type_esc = _escape_soql(model_type)
            recs = self._query(
                "SELECT Id, Name, SellingModelType FROM ProductSellingModel "
                f"WHERE Name = '{name_esc}' AND SellingModelType = '{type_esc}' LIMIT 1"
            )
            if not recs:
                raise TaskOptionsError(
                    f"Missing ProductSellingModel for Name={name}, SellingModelType={model_type}"
                )
            psm_by_key[f"{name}::{model_type}"] = recs[0]["Id"]

        if delete_first:
            product_ids = sorted(set(product_by_sku.values()))
            id_list = ",".join([f"'{_escape_soql(pid)}'" for pid in product_ids])
            existing = self._query(
                "SELECT Id FROM PricebookEntry "
                f"WHERE Pricebook2Id = '{standard_pricebook_id}' AND Product2Id IN ({id_list})"
            )
            existing_ids = [r["Id"] for r in existing]
            if existing_ids:
                self.logger.info(f"Deleting {len(existing_ids)} existing PricebookEntry rows.")
                for i in range(0, len(existing_ids), 200):
                    batch = existing_ids[i : i + 200]
                    self._api(
                        "DELETE",
                        "composite/sobjects",
                        params={"ids": ",".join(batch), "allOrNone": "false"},
                    )

        create_records: List[Dict] = []
        for row in rows:
            psm_id = psm_by_key[f"{row['PSMName']}::{row['PSMSellingModelType']}"]
            is_active_raw = str(row.get("IsActive", "true")).strip().lower()
            is_active = is_active_raw not in {"0", "false", "no"}
            create_records.append(
                {
                    "attributes": {"type": "PricebookEntry"},
                    "Pricebook2Id": standard_pricebook_id,
                    "Product2Id": product_by_sku[row["SKU"]],
                    "ProductSellingModelId": psm_id,
                    "UnitPrice": float(row["UnitPrice"]),
                    "CurrencyIsoCode": row["CurrencyIsoCode"],
                    "IsActive": is_active,
                }
            )

        self.logger.info(f"Creating {len(create_records)} PricebookEntry rows via API.")
        for i in range(0, len(create_records), 200):
            batch = create_records[i : i + 200]
            result = self._api("POST", "composite/sobjects", {"allOrNone": False, "records": batch})
            failures = [r for r in result if not r.get("success")]
            if failures:
                raise TaskOptionsError(f"Failed creating PricebookEntry batch: {json.dumps(failures, indent=2)}")

        self.logger.info("Pricebook recreation complete.")


class VerifyCustomerDemoCatalog(BaseSalesforceTask):
    """Verify go/no-go checks for customer demo catalog records."""

    task_options = {
        "input_csv": {
            "description": "CSV with columns: SKU,PSMName,PSMSellingModelType,CategoryCode",
            "required": True,
        },
        "product_type_field": {
            "description": "Product2 field API name that must be populated (default: Type).",
            "required": False,
        },
        "verify_images": {
            "description": "Require Product2.DisplayUrl when image is expected (default true).",
            "required": False,
        },
        "verify_billing": {
            "description": "Require Product2.BillingPolicyId when billing is expected (default true).",
            "required": False,
        },
        "require_internal_image_urls": {
            "description": "If true, require image URLs to use /resource/<StaticResourceName> for image-required rows.",
            "required": False,
        },
        "require_product_type": {
            "description": (
                "When input CSV has no ProductTypeExpected column: if true (default), Product2 Type "
                "must be non-blank. Ignored when ProductTypeExpected is present (per-row Bundle vs blank)."
            ),
            "required": False,
        },
    }

    def _api(self, path: str, soql: str) -> List[Dict]:
        url = f"{self.org_config.instance_url}/services/data/v66.0/{path}"
        headers = {"Authorization": f"Bearer {self.org_config.access_token}"}
        resp = requests.get(url, headers=headers, params={"q": soql}, timeout=60)
        if resp.status_code >= 400:
            raise TaskOptionsError(f"SOQL failed ({resp.status_code}): {resp.text}")
        return resp.json().get("records", [])

    def _query(self, soql: str) -> List[Dict]:
        return self._api("query", soql)

    def _read_rows(self) -> Tuple[List[Dict], bool]:
        input_csv = self.options["input_csv"]
        rows: List[Dict] = []
        with open(input_csv, "r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            fieldnames = set(reader.fieldnames or [])
            required = {"SKU", "PSMName", "PSMSellingModelType", "CategoryCode"}
            missing = required - fieldnames
            if missing:
                raise TaskOptionsError(f"Missing required CSV columns: {sorted(missing)}")
            has_product_type_expected = "ProductTypeExpected" in fieldnames
            for row in reader:
                if row.get("SKU"):
                    rows.append(row)
        return rows, has_product_type_expected

    @staticmethod
    def _is_truthy(value: str, default: bool = True) -> bool:
        if value is None:
            return default
        return str(value).strip().lower() not in {"0", "false", "no", "n"}

    def _run_task(self):
        rows, has_product_type_expected = self._read_rows()
        product_type_field = self.options.get("product_type_field", "Type")
        verify_images = self._is_truthy(self.options.get("verify_images"), default=True)
        verify_billing = self._is_truthy(self.options.get("verify_billing"), default=True)
        require_internal_image_urls = self._is_truthy(
            self.options.get("require_internal_image_urls"),
            default=False,
        )
        require_product_type = self._is_truthy(self.options.get("require_product_type"), default=True)
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", product_type_field):
            raise TaskOptionsError(f"Invalid product_type_field: {product_type_field}")

        pb_records = self._query("SELECT Id FROM Pricebook2 WHERE IsStandard = true LIMIT 1")
        if not pb_records:
            raise TaskOptionsError("No Standard Pricebook found in target org.")
        standard_pricebook_id = pb_records[0]["Id"]

        failures: List[str] = []
        for row in rows:
            sku = row["SKU"]
            psm_name = row["PSMName"]
            psm_type = row["PSMSellingModelType"]
            category_code = row["CategoryCode"]

            product = self._query(
                f"SELECT Id, IsActive, {product_type_field}, DisplayUrl, BillingPolicyId, BillingPolicy.Name FROM Product2 "
                f"WHERE StockKeepingUnit = '{_escape_soql(sku)}' LIMIT 1"
            )
            if not product:
                failures.append(f"{sku}: Product2 missing")
                continue
            product_id = product[0]["Id"]
            if not product[0].get("IsActive"):
                failures.append(f"{sku}: Product2 not active")
            actual_type = product[0].get(product_type_field)
            if has_product_type_expected:
                expected_raw = (row.get("ProductTypeExpected") or "").strip()
                if expected_raw.lower() == "bundle":
                    if actual_type != "Bundle":
                        failures.append(
                            f"{sku}: Product2.{product_type_field} must be Bundle (found {actual_type!r})"
                        )
                else:
                    if actual_type:
                        failures.append(
                            f"{sku}: Product2.{product_type_field} must be blank/null (found {actual_type!r})"
                        )
            elif require_product_type and not actual_type:
                failures.append(f"{sku}: Product type field {product_type_field} is blank")
            image_required = self._is_truthy(row.get("ImageRequired"), default=True)
            display_url = (product[0].get("DisplayUrl") or "").strip()
            if verify_images and image_required and not display_url:
                failures.append(f"{sku}: Product2.DisplayUrl is blank")
            if (
                verify_images
                and image_required
                and require_internal_image_urls
                and display_url
                and not display_url.startswith("/resource/")
            ):
                failures.append(
                    f"{sku}: Product2.DisplayUrl must use /resource/<StaticResourceName> (found {display_url})"
                )
            billing_required = self._is_truthy(row.get("BillingRequired"), default=True)
            if verify_billing and billing_required and not product[0].get("BillingPolicyId"):
                failures.append(f"{sku}: Product2.BillingPolicyId is blank")
            expected_billing_policy = (row.get("BillingPolicyName") or "").strip()
            if (
                verify_billing
                and billing_required
                and expected_billing_policy
                and product[0].get("BillingPolicy", {}).get("Name") != expected_billing_policy
            ):
                failures.append(
                    f"{sku}: BillingPolicy mismatch (expected {expected_billing_policy}, "
                    f"found {product[0].get('BillingPolicy', {}).get('Name') or 'blank'})"
                )

            psm = self._query(
                "SELECT Id FROM ProductSellingModel "
                f"WHERE Name = '{_escape_soql(psm_name)}' "
                f"AND SellingModelType = '{_escape_soql(psm_type)}' LIMIT 1"
            )
            if not psm:
                failures.append(f"{sku}: ProductSellingModel missing ({psm_name}/{psm_type})")
                continue
            psm_id = psm[0]["Id"]

            psmo = self._query(
                "SELECT Id FROM ProductSellingModelOption "
                f"WHERE Product2Id = '{product_id}' AND ProductSellingModelId = '{psm_id}' "
                "AND IsDefault = true LIMIT 1"
            )
            if not psmo:
                failures.append(f"{sku}: default ProductSellingModelOption missing")

            pbe = self._query(
                "SELECT Id, ProductSellingModelId, IsActive FROM PricebookEntry "
                f"WHERE Pricebook2Id = '{standard_pricebook_id}' AND Product2Id = '{product_id}' LIMIT 1"
            )
            if not pbe:
                failures.append(f"{sku}: Standard PricebookEntry missing")
            else:
                if not pbe[0].get("IsActive"):
                    failures.append(f"{sku}: Standard PricebookEntry not active")
                if pbe[0].get("ProductSellingModelId") != psm_id:
                    failures.append(f"{sku}: PricebookEntry ProductSellingModelId mismatch")

            mapping = self._query(
                "SELECT Id FROM ProductCategoryProduct "
                f"WHERE ProductId = '{product_id}' AND ProductCategory.Code = '{_escape_soql(category_code)}' LIMIT 1"
            )
            if not mapping:
                failures.append(f"{sku}: ProductCategoryProduct missing for category {category_code}")

        if failures:
            raise TaskOptionsError("Catalog verification failed:\n- " + "\n- ".join(failures))

        self.logger.info("Catalog verification passed for all SKUs.")
