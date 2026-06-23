"""Org introspection for the demo data generator.

With no pinned config, ``discover()`` queries the target org for a known-good
combination of account / product / pricebook / legal entity / opportunity stage
so the generator can run against a fresh org with zero configuration.

All field names here are verified live against ``rlm-base__jun17_1`` (v67.0):

* Billing-ready accounts come from ``BillingAccount.AccountId`` -> ``Account``
  (only Infinitech is pre-wired in QB; Global Media has no BillingAccount).
  ``BillingAccount`` has **no** ``Status`` field -- do not query one.
* Billable products: active ``PricebookEntry`` on the **standard** pricebook
  with an active ``Product2``. ``QB-`` SKUs are the known-good QB catalog.
* Standard pricebook: ``Pricebook2 WHERE IsStandard = true``.
* Legal entity default: ``Default Legal Entity - US``.
* Opportunity stage: first open (``IsClosed = false``) active stage.

Note: a clean PricebookEntry is necessary but not sufficient for a complex
bundle to *place* (bundles also need component/attribute/selling-model wiring).
The optional PST probe is reserved for a future hardening pass; today this
module surfaces candidates and the first live transaction proves placement.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

from .auth import SfRestClient

log = logging.getLogger("txn_data_harness.discovery")

DEFAULT_LEGAL_ENTITY = "Default Legal Entity - US"
# Known-good QB catalog prefix; preferred when picking a default product.
QB_SKU_PREFIX = "QB-"


class DiscoveryError(RuntimeError):
    """The org lacks a prerequisite for the requested lifecycle stage."""


@dataclass
class Account:
    id: str
    name: str
    billing_account_id: Optional[str] = None  # None => cannot reach invoice/post

    @property
    def is_billing_ready(self) -> bool:
        return self.billing_account_id is not None


@dataclass
class Product:
    id: str
    name: str
    sku: Optional[str]
    pricebook_entry_id: str
    unit_price: Optional[float]
    # SellingModelType of the PBE's bound ProductSellingModel: 'TermDefined',
    # 'Evergreen', or 'OneTime'. Drives the line's date fields -- only
    # TermDefined accepts (and requires) EndDate; Evergreen/OneTime reject it
    # at createOrderFromQuote. None if the org didn't return it.
    selling_model_type: Optional[str] = None

    @property
    def is_qb(self) -> bool:
        return bool(self.sku and self.sku.startswith(QB_SKU_PREFIX))

    @property
    def needs_end_date(self) -> bool:
        """Only term-defined products take an EndDate (verified live, CONTRACTS.md)."""
        return self.selling_model_type == "TermDefined"


@dataclass
class OrgContext:
    """Everything the generator needs to build a transaction, discovered once."""

    pricebook_id: str
    pricebook_name: str
    legal_entity_id: Optional[str]
    legal_entity_name: Optional[str]
    opportunity_stage: Optional[str]
    billing_ready_accounts: list[Account] = field(default_factory=list)
    products: list[Product] = field(default_factory=list)

    def default_account(self) -> Account:
        if not self.billing_ready_accounts:
            raise DiscoveryError(
                "No billing-ready accounts found (no BillingAccount records). "
                "Create a BillingAccount for an Account, or pin one in config."
            )
        return self.billing_ready_accounts[0]

    def default_product(self) -> Product:
        if not self.products:
            raise DiscoveryError(
                "No billable products found (no active PricebookEntry on the "
                "standard pricebook). Check product/pricebook setup."
            )
        # Prefer a QB known-good SKU; else first available.
        for p in self.products:
            if p.is_qb:
                return p
        return self.products[0]


def _sql_escape(value: str) -> str:
    """Escape single quotes for literal interpolation into SOQL."""
    return value.replace("\\", "\\\\").replace("'", "\\'")


def discover_accounts(client: SfRestClient, account_name: Optional[str] = None) -> list[Account]:
    """Return billing-ready accounts (those with a BillingAccount).

    If ``account_name`` is given, restrict to that account and surface whether
    it is billing-ready (so the caller can warn / cap the stage).
    """
    soql = "SELECT Id, Name, AccountId, Account.Name FROM BillingAccount"
    if account_name:
        soql += f" WHERE Account.Name = '{_sql_escape(account_name)}'"
    accounts: list[Account] = []
    for r in client.query(soql):
        acct = r.get("Account") or {}
        accounts.append(Account(
            id=r["AccountId"],
            name=acct.get("Name", r["AccountId"]),
            billing_account_id=r["Id"],
        ))
    log.info("discovered %d billing-ready account(s)", len(accounts))
    return accounts


def resolve_account(client: SfRestClient, name: str) -> Account:
    """Resolve any account by Name, billing-ready or not.

    Unlike :func:`discover_accounts` (which lists only accounts that *have* a
    BillingAccount), this resolves an account the user pinned in config even
    when it has no BillingAccount -- a quote-only "pipeline" account such as
    Global Media. We look up the Account, then check for a BillingAccount so the
    returned ``Account.is_billing_ready`` correctly caps the stage downstream.
    """
    rows = client.query(
        f"SELECT Id, Name FROM Account WHERE Name = '{_sql_escape(name)}' LIMIT 1"
    )
    if not rows:
        raise DiscoveryError(f"account '{name}' not found in the org")
    acct_id = rows[0]["Id"]
    ba = client.query(
        f"SELECT Id FROM BillingAccount WHERE AccountId = '{acct_id}' LIMIT 1"
    )
    return Account(
        id=acct_id,
        name=rows[0].get("Name", name),
        billing_account_id=ba[0]["Id"] if ba else None,
    )


def discover_products(
    client: SfRestClient,
    sku: Optional[str] = None,
    limit: int = 25,
) -> list[Product]:
    """Return billable products (active PBE on the standard pricebook)."""
    soql = (
        "SELECT Id, UnitPrice, Product2Id, Product2.Name, "
        "Product2.StockKeepingUnit, ProductSellingModel.SellingModelType "
        "FROM PricebookEntry "
        "WHERE Pricebook2.IsStandard = true AND IsActive = true "
        "AND Product2.IsActive = true"
    )
    if sku:
        soql += f" AND Product2.StockKeepingUnit = '{_sql_escape(sku)}'"
    soql += f" LIMIT {int(limit)}"
    products: list[Product] = []
    for r in client.query(soql):
        p = r.get("Product2") or {}
        psm = r.get("ProductSellingModel") or {}
        products.append(Product(
            id=r["Product2Id"],
            name=p.get("Name", r["Product2Id"]),
            sku=p.get("StockKeepingUnit"),
            pricebook_entry_id=r["Id"],
            unit_price=r.get("UnitPrice"),
            selling_model_type=psm.get("SellingModelType"),
        ))
    log.info("discovered %d billable product(s)%s", len(products),
             f" for SKU {sku}" if sku else "")
    return products


def resolve_product(client: SfRestClient, sku: str) -> Product:
    """Resolve a single billable product by SKU (active PBE on standard PB)."""
    products = discover_products(client, sku=sku, limit=1)
    if not products:
        raise DiscoveryError(
            f"product SKU '{sku}' has no active PricebookEntry on the standard "
            f"pricebook (check the product/pricebook setup)"
        )
    return products[0]


def _discover_standard_pricebook(client: SfRestClient) -> tuple[str, str]:
    recs = client.query("SELECT Id, Name FROM Pricebook2 WHERE IsStandard = true LIMIT 1")
    if not recs:
        raise DiscoveryError("No standard pricebook (Pricebook2 IsStandard=true) found.")
    return recs[0]["Id"], recs[0].get("Name", "Standard Price Book")


def _discover_legal_entity(client: SfRestClient) -> tuple[Optional[str], Optional[str]]:
    recs = client.query(
        f"SELECT Id, Name FROM LegalEntity WHERE Name = '{_sql_escape(DEFAULT_LEGAL_ENTITY)}' LIMIT 1"
    )
    if not recs:  # fall back to any legal entity
        recs = client.query("SELECT Id, Name FROM LegalEntity LIMIT 1")
    if not recs:
        return None, None
    return recs[0]["Id"], recs[0].get("Name")


def _discover_open_stage(client: SfRestClient, pinned: Optional[str] = None) -> Optional[str]:
    recs = client.query(
        "SELECT MasterLabel, IsClosed FROM OpportunityStage WHERE IsActive = true"
    )
    open_stages = [r["MasterLabel"] for r in recs if not r.get("IsClosed")]
    if pinned:
        if pinned in open_stages:
            return pinned
        raise DiscoveryError(
            f"Opportunity stage '{pinned}' is not a valid open stage in this org. "
            f"Valid open stages: {', '.join(open_stages)}"
        )
    return open_stages[0] if open_stages else None


def discover(
    client: SfRestClient,
    account_name: Optional[str] = None,
    sku: Optional[str] = None,
    opportunity_stage: Optional[str] = None,
) -> OrgContext:
    """Resolve a full org context for the generator (read-only)."""
    pricebook_id, pricebook_name = _discover_standard_pricebook(client)
    legal_entity_id, legal_entity_name = _discover_legal_entity(client)
    stage = _discover_open_stage(client, opportunity_stage)
    ctx = OrgContext(
        pricebook_id=pricebook_id,
        pricebook_name=pricebook_name,
        legal_entity_id=legal_entity_id,
        legal_entity_name=legal_entity_name,
        opportunity_stage=stage,
        billing_ready_accounts=discover_accounts(client, account_name),
        products=discover_products(client, sku),
    )
    return ctx
