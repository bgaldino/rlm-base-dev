"""Robot Framework keyword library for Salesforce REST API operations.

Provides keywords for creating, querying, and deleting Salesforce records
via the REST API. Used by E2E tests to set up test data, poll async
operations, and verify record state without relying on the UI.

Authentication is obtained via ``sf org display --json`` using the
ORG_ALIAS variable, which provides an access token and instance URL.
"""

import json
import logging
import subprocess
import time

import requests
from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn

_logger = logging.getLogger(__name__)


class SalesforceAPI:
    """Keyword library for Salesforce REST API operations in E2E tests."""

    ROBOT_LIBRARY_SCOPE = "TEST"

    # API version matching the project (Spring '26 / v66.0)
    API_VERSION = "v66.0"

    def __init__(self):
        self._access_token = None
        self._instance_url = None
        self._created_record_ids = []

    # ── Authentication ───────────────────────────────────────────────

    def _ensure_authenticated(self):
        """Authenticate via sf org display if not already authenticated."""
        if self._access_token and self._instance_url:
            return
        org_alias = BuiltIn().get_variable_value("${ORG_ALIAS}", "")
        if not org_alias:
            raise AssertionError(
                "ORG_ALIAS variable must be set "
                "(e.g. -v ORG_ALIAS:my-scratch)"
            )
        result = subprocess.run(
            ["sf", "org", "display", "-o", org_alias, "--json"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise AssertionError(
                f"sf org display failed (rc={result.returncode}): {result.stderr}"
            )
        data = json.loads(result.stdout)
        org_result = data.get("result", {})
        self._access_token = org_result.get("accessToken")
        self._instance_url = (org_result.get("instanceUrl") or "").rstrip("/")
        if not self._access_token or not self._instance_url:
            raise AssertionError(
                "sf org display did not return accessToken or instanceUrl. "
                f"Keys present: {list(org_result.keys())}"
            )
        _logger.info("Authenticated to %s", self._instance_url)

    def _headers(self):
        """Return HTTP headers for REST API calls."""
        return {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _sobject_url(self, sobject, record_id=""):
        """Return the SObject REST API URL."""
        base = f"{self._instance_url}/services/data/{self.API_VERSION}/sobjects/{sobject}"
        if record_id:
            base = f"{base}/{record_id}"
        return base

    def _query_url(self):
        """Return the SOQL query REST API URL."""
        return f"{self._instance_url}/services/data/{self.API_VERSION}/query"

    # ── Record Creation ──────────────────────────────────────────────

    @keyword
    def create_account_via_api(self, name):
        """Create an Account record and return its Id.

        Args:
            name: Account name.

        Returns:
            The new Account record Id.
        """
        return self._create_record("Account", {"Name": name})

    @keyword
    def create_opportunity_via_api(self, name, account_id, stage="Prospecting",
                                   close_date=None):
        """Create an Opportunity record and return its Id.

        Args:
            name: Opportunity name.
            account_id: Parent Account Id.
            stage: Stage name (default: Prospecting).
            close_date: Close date in YYYY-MM-DD format. Defaults to 90 days from now.

        Returns:
            The new Opportunity record Id.
        """
        if not close_date:
            close_date = time.strftime(
                "%Y-%m-%d", time.localtime(time.time() + 90 * 86400)
            )
        return self._create_record(
            "Opportunity",
            {
                "Name": name,
                "AccountId": account_id,
                "StageName": stage,
                "CloseDate": close_date,
            },
        )

    @keyword
    def create_quote_via_api(self, name, opportunity_id):
        """Create a Quote record and return its Id.

        Args:
            name: Quote name.
            opportunity_id: Parent Opportunity Id.

        Returns:
            The new Quote record Id.
        """
        return self._create_record(
            "Quote",
            {"Name": name, "OpportunityId": opportunity_id},
        )

    @keyword
    def add_quote_line_item_via_api(self, quote_id, product2_id, quantity=1,
                                     unit_price=None, pricebook_entry_id=None):
        """Add a QuoteLineItem to a Quote.

        Args:
            quote_id: Quote Id.
            product2_id: Product2 Id.
            quantity: Quantity (default: 1).
            unit_price: Unit price. Required if no PricebookEntryId.
            pricebook_entry_id: PricebookEntryId. If not provided, looks it up.

        Returns:
            The new QuoteLineItem record Id.
        """
        fields = {
            "QuoteId": quote_id,
            "Product2Id": product2_id,
            "Quantity": int(quantity),
        }
        if pricebook_entry_id:
            fields["PricebookEntryId"] = pricebook_entry_id
        if unit_price is not None:
            fields["UnitPrice"] = float(unit_price)
        return self._create_record("QuoteLineItem", fields)

    def _create_record(self, sobject, fields):
        """Create a record and track its Id for cleanup."""
        self._ensure_authenticated()
        resp = requests.post(
            self._sobject_url(sobject),
            headers=self._headers(),
            json=fields,
        )
        if resp.status_code not in (200, 201):
            raise AssertionError(
                f"Failed to create {sobject}: {resp.status_code} {resp.text}"
            )
        record_id = resp.json().get("id")
        self._created_record_ids.append((sobject, record_id))
        _logger.info("Created %s: %s", sobject, record_id)
        return record_id

    # ── Querying ─────────────────────────────────────────────────────

    @keyword
    def query_records(self, soql):
        """Execute a SOQL query and return the list of records.

        Args:
            soql: SOQL query string.

        Returns:
            List of record dictionaries.
        """
        self._ensure_authenticated()
        resp = requests.get(
            self._query_url(),
            headers=self._headers(),
            params={"q": soql},
        )
        if resp.status_code != 200:
            raise AssertionError(
                f"SOQL query failed: {resp.status_code} {resp.text}"
            )
        return resp.json().get("records", [])

    @keyword
    def query_record_by_id(self, sobject, record_id, fields="Id,Name"):
        """Query a single record by Id.

        Args:
            sobject: SObject API name.
            record_id: Record Id.
            fields: Comma-separated field list.

        Returns:
            Record dictionary.
        """
        self._ensure_authenticated()
        resp = requests.get(
            self._sobject_url(sobject, record_id),
            headers=self._headers(),
            params={"fields": fields},
        )
        if resp.status_code != 200:
            raise AssertionError(
                f"GET {sobject}/{record_id} failed: {resp.status_code} {resp.text}"
            )
        return resp.json()

    @keyword
    def query_field_value(self, sobject, record_id, field_name):
        """Query a single field value from a record.

        Args:
            sobject: SObject API name.
            record_id: Record Id.
            field_name: API name of the field to query.

        Returns:
            The field value as a string.
        """
        record = self.query_record_by_id(sobject, record_id, fields=field_name)
        value = record.get(field_name)
        return str(value) if value is not None else ""

    @keyword
    def get_order_status(self, order_id):
        """Get the Status field of an Order.

        Args:
            order_id: Order record Id.

        Returns:
            Order status string.
        """
        return self.query_field_value("Order", order_id, "Status")

    @keyword
    def get_asset_count_for_account(self, account_id):
        """Count Asset records linked to an Account.

        Args:
            account_id: Account record Id.

        Returns:
            Integer count of assets.
        """
        records = self.query_records(
            f"SELECT COUNT(Id) cnt FROM Asset WHERE AccountId = '{account_id}'"
        )
        if records:
            return int(records[0].get("cnt", 0))
        return 0

    @keyword
    def find_product_by_name(self, product_name):
        """Find a Product2 record by Name.

        Args:
            product_name: Product name to search for.

        Returns:
            Product2 record Id, or raises if not found.
        """
        records = self.query_records(
            f"SELECT Id, Name FROM Product2 WHERE Name = '{product_name}' LIMIT 1"
        )
        if not records:
            raise AssertionError(f"Product2 not found: {product_name}")
        return records[0]["Id"]

    @keyword
    def find_pricebook_entry(self, product2_id, pricebook_name="Standard Price Book"):
        """Find a PricebookEntry for a product in a pricebook.

        Args:
            product2_id: Product2 Id.
            pricebook_name: Pricebook name (default: Standard Price Book).

        Returns:
            PricebookEntry Id, or raises if not found.
        """
        records = self.query_records(
            f"SELECT Id, UnitPrice FROM PricebookEntry "
            f"WHERE Product2Id = '{product2_id}' "
            f"AND Pricebook2.Name = '{pricebook_name}' "
            f"AND IsActive = true LIMIT 1"
        )
        if not records:
            raise AssertionError(
                f"PricebookEntry not found for Product2 {product2_id} "
                f"in pricebook '{pricebook_name}'"
            )
        return records[0]["Id"]

    # ── Record Deletion ──────────────────────────────────────────────

    @keyword
    def delete_record_by_id(self, sobject, record_id):
        """Delete a single record by Id.

        Args:
            sobject: SObject API name.
            record_id: Record Id.
        """
        self._ensure_authenticated()
        resp = requests.delete(
            self._sobject_url(sobject, record_id),
            headers=self._headers(),
        )
        if resp.status_code not in (200, 204):
            _logger.warning(
                "Failed to delete %s/%s: %s %s",
                sobject, record_id, resp.status_code, resp.text,
            )
        else:
            _logger.info("Deleted %s: %s", sobject, record_id)

    @keyword
    def cleanup_test_data(self):
        """Delete all records created during this test session.

        Deletes in reverse creation order (child records first).
        Errors are logged but do not fail the keyword.
        """
        self._ensure_authenticated()
        for sobject, record_id in reversed(self._created_record_ids):
            try:
                resp = requests.delete(
                    self._sobject_url(sobject, record_id),
                    headers=self._headers(),
                )
                if resp.status_code in (200, 204):
                    _logger.info("Cleanup: deleted %s %s", sobject, record_id)
                else:
                    _logger.warning(
                        "Cleanup: failed to delete %s %s: %s",
                        sobject, record_id, resp.status_code,
                    )
            except Exception as e:
                _logger.warning(
                    "Cleanup: error deleting %s %s: %s", sobject, record_id, e
                )
        self._created_record_ids.clear()

    # ── Verification helpers ─────────────────────────────────────────

    @keyword
    def verify_field_value_via_api(self, sobject, record_id, field_name,
                                    expected_value):
        """Assert that a record field matches the expected value.

        Raises AssertionError if the value does not match (useful with
        ``Wait Until Keyword Succeeds`` for polling).

        Args:
            sobject: SObject API name.
            record_id: Record Id.
            field_name: API name of the field.
            expected_value: Expected value (compared as strings).
        """
        actual = self.query_field_value(sobject, record_id, field_name)
        if str(actual) != str(expected_value):
            raise AssertionError(
                f"{sobject}.{field_name} = '{actual}', "
                f"expected '{expected_value}'"
            )

    @keyword
    def verify_related_record_exists(self, soql):
        """Assert that a SOQL query returns at least one record.

        Raises AssertionError if no records found (useful with
        ``Wait Until Keyword Succeeds`` for polling).

        Args:
            soql: SOQL query that should return at least one record.
        """
        records = self.query_records(soql)
        if not records:
            raise AssertionError(f"No records found for: {soql}")
        return records[0].get("Id", records[0].get("id", ""))
