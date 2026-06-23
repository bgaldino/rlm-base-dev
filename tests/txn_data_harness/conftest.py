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
    return Product(
        id="01tTERM",
        name="Additional API Flex",
        sku="QB-API-FLEX",
        pricebook_entry_id="01uTERM",
        unit_price=450.0,
        selling_model_type="TermDefined",
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
