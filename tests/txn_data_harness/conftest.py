"""Pytest bootstrap and shared fakes for Transaction Data Harness tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from scripts.txn_data_harness.discovery import Account, OrgContext, Product

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


@pytest.fixture
def billable_account() -> Account:
    return Account(id="001BILLABLE", name="Infinitech", billing_account_id="BA-1")


@pytest.fixture
def pipeline_account() -> Account:
    return Account(id="001PIPE", name="Global Media", billing_account_id=None)


@pytest.fixture
def term_product() -> Product:
    """Monthly TermDefined product (12 × Months default from the PSM)."""
    return Product(
        id="01tTERM",
        name="Additional API Flex",
        sku="QB-API-FLEX",
        pricebook_entry_id="01uTERM",
        unit_price=450.0,
        selling_model_type="TermDefined",
        selling_model_name="Term Monthly",
        pricing_term=12,
        pricing_term_unit="Months",
    )


@pytest.fixture
def annual_term_product() -> Product:
    """Annual TermDefined product (default term 1 × Annual). Used by tests
    exercising the non-month PricingTermUnit code path."""
    return Product(
        id="01tANNUAL",
        name="Cloud License",
        sku="QB-LIC-CLOUD",
        pricebook_entry_id="01uANNUAL",
        unit_price=1200.0,
        selling_model_type="TermDefined",
        selling_model_name="Term Annual",
        pricing_term=1,
        pricing_term_unit="Annual",
    )


@pytest.fixture
def quarterly_term_product() -> Product:
    """Quarterly TermDefined product (default term 4 × Quarterly)."""
    return Product(
        id="01tQTR",
        name="Quarterly License",
        sku="QB-LIC-QTR",
        pricebook_entry_id="01uQTR",
        unit_price=300.0,
        selling_model_type="TermDefined",
        selling_model_name="Term Quarterly",
        pricing_term=4,
        pricing_term_unit="Quarterly",
    )


@pytest.fixture
def evergreen_product() -> Product:
    return Product(
        id="01tEVER",
        name="Additional API",
        sku="QB-API",
        pricebook_entry_id="01uEVER",
        unit_price=2000.0,
        selling_model_type="Evergreen",
        selling_model_name="Evergreen",
    )


@pytest.fixture
def org_context(billable_account, term_product) -> OrgContext:
    return OrgContext(
        pricebook_id="01sSTANDARD",
        pricebook_name="Standard Price Book",
        legal_entity_id="LE-1",
        legal_entity_name="Default Legal Entity - US",
        opportunity_stage="Prospecting",
        billing_ready_accounts=[billable_account],
        products=[term_product],
    )


class FakeClient:
    """Small REST client fake that records calls and returns queued responses."""

    api_version = "67.0"

    def __init__(self):
        self.posts: list[tuple[str, object]] = []
        self.patches: list[tuple[str, object]] = []
        self.gets: list[str] = []
        self.queries: list[str] = []
        self.post_responses: list[object] = []
        self.query_responses: list[list[dict]] = []
        self.get_responses: list[object] = []

    def post(self, path: str, body: object):
        self.posts.append((path, body))
        return self.post_responses.pop(0) if self.post_responses else {"success": True, "id": "NEWID"}

    def patch(self, path: str, body: object):
        self.patches.append((path, body))
        return None

    def query(self, soql: str):
        self.queries.append(soql)
        return self.query_responses.pop(0) if self.query_responses else []

    def get(self, path: str):
        self.gets.append(path)
        return self.get_responses.pop(0) if self.get_responses else {"Status": "Completed"}


@pytest.fixture
def fake_client() -> FakeClient:
    return FakeClient()
