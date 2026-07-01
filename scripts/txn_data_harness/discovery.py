"""Org introspection for the demo data generator.

With no pinned config, ``discover()`` queries the target org for a known-good
combination of account / product / pricebook / legal entity / opportunity stage
so the generator can run against a fresh org with zero configuration.

All field names here are verified live against a Revenue Cloud R262 scratch
org (API v67.0):

* Billing-ready accounts come from ``BillingAccount.AccountId`` -> ``Account``.
  (In the bundled QB demo dataset, ``Infinitech`` is the billing-ready account
  and ``Global Media`` is pipeline-only; other datasets will have different
  names.) ``BillingAccount`` has **no** ``Status`` field -- do not query one.
* Billable products: active ``PricebookEntry`` on the **standard** pricebook
  with an active ``Product2``. ``QB-`` SKUs are the known-good catalog in the
  bundled QB demo dataset; any active SKU works.
* Standard pricebook: ``Pricebook2 WHERE IsStandard = true``.
* Legal entity default: ``Default Legal Entity - US``.
* Opportunity stage: first open (``IsClosed = false``) active stage.

Note: a clean PricebookEntry is necessary but not sufficient for every product.
Default-configured bundles (example: ``QB-COMPLETE``) place cleanly -- PST
expands the bundle's component graph server-side from defaults. Bundles whose
mandatory slots require user choice will fail to place. The optional PST probe
is reserved for a future hardening pass; today this module surfaces candidates
and the first live transaction proves placement.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

from .auth import SfRestClient
from .term import Term

log = logging.getLogger("txn_data_harness.discovery")

DEFAULT_LEGAL_ENTITY = "Default Legal Entity - US"
# Known-good QB catalog prefix; preferred when picking a default product.
QB_SKU_PREFIX = "QB-"


class DiscoveryError(RuntimeError):
    """The org lacks a prerequisite for the requested lifecycle stage."""


@dataclass
class PostalAddress:
    """One billing- or shipping-address tuple lifted off an Account.

    Carries the five fields the InvoiceAddressGroup graph record marks as
    Required (street/city/state/postalCode/country). The ingest API rejects
    addresses with any of those five null, so a partial address on the
    Account propagates a clear ``LifecycleError`` rather than a 400 from
    the org -- see the call site in :func:`lifecycle.ingest_invoice`.
    """

    street: Optional[str]
    city: Optional[str]
    state: Optional[str]
    postal_code: Optional[str]
    country: Optional[str]

    # Mapping from dataclass attr -> Salesforce field suffix (PascalCase).
    _SF_FIELD_MAP = {
        "street": "Street",
        "city": "City",
        "state": "State",
        "postal_code": "PostalCode",
        "country": "Country",
    }

    @property
    def is_complete(self) -> bool:
        return all(
            v is not None and str(v).strip()
            for v in (
                self.street, self.city, self.state, self.postal_code, self.country,
            )
        )

    def to_sf_fields(self, prefix: str) -> dict[str, str]:
        """Build a ``{PrefixField: value}`` dict for non-null fields.

        Example: ``addr.to_sf_fields("Shipping")`` →
        ``{"ShippingStreet": "...", "ShippingCity": "...", ...}``.
        """
        return {
            f"{prefix}{suffix}": getattr(self, attr)
            for attr, suffix in self._SF_FIELD_MAP.items()
            if getattr(self, attr)
        }


@dataclass
class Account:
    id: str
    name: str
    billing_account_id: Optional[str] = None  # None => cannot reach invoice/post
    # First Contact discovered on the account, used as the default
    # ``Invoice.BillToContactId`` on the ingestion path. The dev guide marks
    # this field Required on the Invoice graph record and the live ingest API
    # rejects payloads that omit it (INVALID_API_INPUT). None when the account
    # has no Contacts -- ingestion will surface a clear error rather than
    # silently produce a partial invoice.
    bill_to_contact_id: Optional[str] = None
    # Account-level ``CurrencyIsoCode`` on multi-currency orgs (the field
    # only exists when multi-currency is enabled). The ingest API rejects
    # the payload with INVALID_API_INPUT on multi-currency orgs when
    # ``currencyIsoCode`` is absent, so the handler stamps this on the
    # Invoice header by default. ``None`` on single-currency orgs (the
    # discovery SOQL returns INVALID_FIELD and the resolver falls through).
    currency_iso_code: Optional[str] = None
    # Billing + shipping address tuples discovered off the Account. The
    # ingestion path materialises both as ``InvoiceAddressGroup`` graph
    # records, then references their ids from each InvoiceLine's
    # ``billingAddressId`` / ``shippingAddressId`` (both fields marked
    # Required in the dev guide). ``None`` when discovery hasn't populated
    # the field; ``ingest_invoice`` raises a clear error in that case.
    billing_address: Optional[PostalAddress] = None
    shipping_address: Optional[PostalAddress] = None

    @property
    def is_billing_ready(self) -> bool:
        return self.billing_account_id is not None


@dataclass
class UsageResourceBinding:
    """One ProductUsageResource row: a usage resource a product grants.

    A usage product carries 1..N bindings (e.g. QB-DB grants UR-DATASTORAGE and
    UR-CPUTIME). ``resource_code`` is the user-facing identifier surfaced in
    scenario YAML; ``uom_class_id`` enables overriding the default UoM by
    UnitCode the same way RLM_UsageUploaderController validates it.
    """

    resource_id: str
    resource_code: str
    resource_name: Optional[str]
    uom_class_id: Optional[str]
    default_uom_id: Optional[str]
    default_uom_code: Optional[str]
    default_uom_name: Optional[str]


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
    # ProductSellingModel.Name -- what scenarios pin via ``selling_model:`` to
    # disambiguate when a SKU has multiple active PBEs (one per model).
    selling_model_name: Optional[str] = None
    # The selling model's declared default term. Used as the per-line fallback
    # when neither the scenario nor the product option overrides it.
    pricing_term: Optional[int] = None
    pricing_term_unit: Optional[str] = None
    # ProductUsageResource bindings (empty for non-usage products); populated
    # lazily by ``attach_usage_bindings`` once the caller knows which products
    # need them (avoids extra SOQL on non-usage scenarios).
    usage_bindings: list[UsageResourceBinding] = field(default_factory=list)

    @property
    def is_qb(self) -> bool:
        return bool(self.sku and self.sku.startswith(QB_SKU_PREFIX))

    @property
    def needs_end_date(self) -> bool:
        """Only term-defined products take an EndDate (verified live, CONTRACTS.md)."""
        return self.selling_model_type == "TermDefined"

    @property
    def default_term(self) -> Optional[Term]:
        """The PSM's declared term, or ``None`` if either half is missing."""
        if self.pricing_term and self.pricing_term_unit:
            return Term(count=int(self.pricing_term), unit=self.pricing_term_unit)
        return None


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
    # Non-taxable TaxTreatment id, or ``None`` if no such row exists. Posted
    # ingestion (``actions/ingest`` with ``status: Posted``) requires every
    # InvoiceLine to reference a non-taxable TaxTreatment when no
    # InvoiceLineTax records are present (current tax invariant); see the
    # invoice-ingestion contracts. Draft ingest stamps the same id so the
    # Draft -> Posted resume path doesn't fall back to the org's default
    # taxable treatment.
    non_taxable_tax_treatment_id: Optional[str] = None
    # Default taxable ``TaxTreatment`` id, or ``None``. Stamped on
    # ``InvoiceLine`` graph records that carry ``taxable: true`` and an
    # accompanying ``InvoiceLineTax`` record on Posted ingestion. A scenario
    # may pin a specific taxable treatment via
    # ``invoice.taxable_tax_treatment_name``; the handler resolves that
    # override directly and does not rely on this default.
    taxable_tax_treatment_id: Optional[str] = None

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
    rows = client.query(soql)
    if not rows:
        log.info("discovered 0 billing-ready account(s)")
        return []
    account_ids = [r["AccountId"] for r in rows]
    addresses = _resolve_account_addresses(client, account_ids)
    contact_by_account = _resolve_default_contact_id(client, account_ids)
    currency_by_account = _account_currency_map(client, account_ids)
    accounts: list[Account] = []
    for r in rows:
        acct = r.get("Account") or {}
        acct_id = r["AccountId"]
        billing_addr, shipping_addr = addresses.get(acct_id, (None, None))
        accounts.append(Account(
            id=acct_id,
            name=acct.get("Name", acct_id),
            billing_account_id=r["Id"],
            bill_to_contact_id=contact_by_account.get(acct_id),
            currency_iso_code=currency_by_account.get(acct_id),
            billing_address=billing_addr,
            shipping_address=shipping_addr,
        ))
    log.info("discovered %d billing-ready account(s)", len(accounts))
    return accounts


# Module-level cache keyed by stable org identity. True if that org has
# CurrencyIsoCode on Account (multi-currency enabled), False if SOQL returned
# INVALID_FIELD. Missing key means not probed yet.
_MULTI_CURRENCY_BY_ORG: dict[str, bool] = {}

# Module-level cache keyed by stable org identity. Holds the resolved
# non-taxable TaxTreatment id (or ``None`` if the org has no such row).
# A missing key means the org has not been probed yet; an explicit ``None``
# value records a probe that returned zero rows so the second call does not
# re-query.
_NON_TAXABLE_TAX_TREATMENT_BY_ORG: dict[str, Optional[str]] = {}

# Same shape, taxable variant. Populated lazily by
# :func:`resolve_taxable_tax_treatment`; Posted ingestion with any
# ``taxable: true`` line stamps the treatment on those InvoiceLine rows so
# the related ``InvoiceLineTax`` records are accepted (the action otherwise
# rejects with ``INVALID_API_INPUT: You can't specify a tax treatment with
# the isTaxable value as false when the invoice line has a related
# InvoiceLineTax record``).
_TAXABLE_TAX_TREATMENT_BY_ORG: dict[str, Optional[str]] = {}
# Same cache shape, keyed by ``(cache_key, name)`` so a scenario can pin a
# specific taxable TaxTreatment via ``invoice.taxable_tax_treatment_name``.
_TAXABLE_TAX_TREATMENT_BY_NAME: dict[tuple[str, str], Optional[str]] = {}


def _org_cache_key(client: SfRestClient) -> Optional[str]:
    """Return a stable-enough cache key for org-scoped discovery probes.

    Prefer instance URL because it is resolved by ``sf org display`` and does
    not depend on which local alias the operator used. Test fakes may not carry
    it, so fall back to an explicit alias. If neither is present, return None
    so callers probe without caching instead of relying on recyclable object ids.
    """
    instance_url = getattr(client, "instance_url", None)
    if instance_url:
        return f"instance:{str(instance_url).rstrip('/')}"
    alias = getattr(client, "alias", None)
    if alias:
        return f"alias:{alias}"
    return None


def _account_currency_map(
    client: SfRestClient, account_ids: list[str]
) -> dict[str, str]:
    """Map Account.Id -> CurrencyIsoCode on multi-currency orgs.

    On single-currency orgs ``Account.CurrencyIsoCode`` does not exist and the
    SOQL fails with INVALID_FIELD; we cache that response so the second call
    on the same run doesn't re-probe. Multi-currency orgs require
    ``Invoice.currencyIsoCode`` on every ingest payload (verified live
    2026-06-25 on rlm-base__jun17_1: missing field returns INVALID_API_INPUT
    "The currencyIsoCode is required in multi-currency organizations").
    """
    if not account_ids:
        return {}
    cache_key = _org_cache_key(client)
    if cache_key is not None and _MULTI_CURRENCY_BY_ORG.get(cache_key) is False:
        return {}
    quoted = ",".join(f"'{_sql_escape(a)}'" for a in account_ids)
    try:
        rows = client.query(
            f"SELECT Id, CurrencyIsoCode FROM Account WHERE Id IN ({quoted})"
        )
    except Exception as exc:  # noqa: BLE001
        if "INVALID_FIELD" in str(exc):
            if cache_key is not None:
                _MULTI_CURRENCY_BY_ORG[cache_key] = False
            return {}
        raise
    if cache_key is not None:
        _MULTI_CURRENCY_BY_ORG[cache_key] = True
    return {r["Id"]: r.get("CurrencyIsoCode") for r in rows if r.get("CurrencyIsoCode")}


_ADDRESS_FIELDS = (
    "BillingStreet",
    "BillingCity",
    "BillingState",
    "BillingPostalCode",
    "BillingCountry",
    "ShippingStreet",
    "ShippingCity",
    "ShippingState",
    "ShippingPostalCode",
    "ShippingCountry",
)


def _resolve_account_addresses(
    client: SfRestClient, account_ids: list[str]
) -> dict[str, tuple[Optional["PostalAddress"], Optional["PostalAddress"]]]:
    """Map Account.Id -> (billing_address, shipping_address) tuples.

    Used by the ingestion path: ``InvoiceLine.billingAddressId`` and
    ``InvoiceLine.shippingAddressId`` are both Required by the ingest API
    (verified live 2026-06-25 on rlm-base__jun17_1: missing fields return
    INVALID_API_INPUT). The handler materialises both as
    ``InvoiceAddressGroup`` graph records and the line points at each by
    ``referenceId``. An Account with a partial address (e.g. no
    ``BillingState``) lands as ``PostalAddress(... state=None ...)`` whose
    ``is_complete`` is False; ingest_invoice surfaces a clear error in
    that case rather than letting the org reject the payload.
    """
    if not account_ids:
        return {}
    quoted = ",".join(f"'{_sql_escape(a)}'" for a in account_ids)
    rows = client.query(
        f"SELECT Id, {', '.join(_ADDRESS_FIELDS)} FROM Account WHERE Id IN ({quoted})"
    )
    out: dict[str, tuple[Optional[PostalAddress], Optional[PostalAddress]]] = {}
    for r in rows:
        billing = PostalAddress(
            street=r.get("BillingStreet"),
            city=r.get("BillingCity"),
            state=r.get("BillingState"),
            postal_code=r.get("BillingPostalCode"),
            country=r.get("BillingCountry"),
        )
        shipping = PostalAddress(
            street=r.get("ShippingStreet"),
            city=r.get("ShippingCity"),
            state=r.get("ShippingState"),
            postal_code=r.get("ShippingPostalCode"),
            country=r.get("ShippingCountry"),
        )
        out[r["Id"]] = (
            billing if any(vars(billing).values()) else None,
            shipping if any(vars(shipping).values()) else None,
        )
    return out


def _resolve_default_contact_id(
    client: SfRestClient, account_ids: list[str]
) -> dict[str, str]:
    """Map Account.Id -> first Contact.Id for the given accounts.

    Used to populate ``Account.bill_to_contact_id``. The ingest API requires
    ``Invoice.BillToContactId`` (verified live 2026-06-25 on rlm-base__jun17_1:
    a payload without the field is rejected with ``INVALID_API_INPUT: The
    BillToContactId field of the Invoice record is required``), and the dev
    guide marks it Required in the Invoice graph record table. We pick the
    most-recently-created Contact on the account; deterministic enough for
    demo data, and any specific Contact override remains a future scenario
    knob.
    """
    if not account_ids:
        return {}
    quoted = ",".join(f"'{_sql_escape(a)}'" for a in account_ids)
    rows = client.query(
        f"SELECT Id, AccountId FROM Contact WHERE AccountId IN ({quoted}) "
        f"ORDER BY CreatedDate DESC"
    )
    by_account: dict[str, str] = {}
    for r in rows:
        # First row wins per account (most recent CreatedDate).
        by_account.setdefault(r["AccountId"], r["Id"])
    return by_account


def resolve_taxable_tax_treatment(
    client: SfRestClient, name: Optional[str] = None
) -> Optional[str]:
    """Return the id of an Active taxable ``TaxTreatment``, or ``None``.

    Mirrors :func:`resolve_non_taxable_tax_treatment`. Posted ingestion with
    any ``taxable: true`` line stamps the returned id on the affected
    ``InvoiceLine`` graph records so the related ``InvoiceLineTax`` records
    are accepted -- without a taxable treatment stamp the action falls back
    to the org's default treatment and rejects the payload with
    ``INVALID_API_INPUT`` when the default is non-taxable (verified live
    2026-06-25 on ``rlm-base__jun17_1``).

    ``name`` pins a specific TaxTreatment (e.g. for a regional VAT demo);
    when ``None`` we return the most-recently-created Active row so the
    org's "default" taxable treatment is picked deterministically. Cached
    per-(org, name) so repeat scenarios don't re-query.
    """
    cache_key = _org_cache_key(client)
    if name:
        if cache_key is not None and (cache_key, name) in _TAXABLE_TAX_TREATMENT_BY_NAME:
            return _TAXABLE_TAX_TREATMENT_BY_NAME[(cache_key, name)]
        rows = client.query(
            "SELECT Id FROM TaxTreatment "
            f"WHERE IsTaxable = true AND Status = 'Active' "
            f"AND Name = '{_sql_escape(name)}' LIMIT 1"
        )
        treatment_id = rows[0]["Id"] if rows else None
        if cache_key is not None:
            _TAXABLE_TAX_TREATMENT_BY_NAME[(cache_key, name)] = treatment_id
        return treatment_id
    if cache_key is not None and cache_key in _TAXABLE_TAX_TREATMENT_BY_ORG:
        return _TAXABLE_TAX_TREATMENT_BY_ORG[cache_key]
    rows = client.query(
        "SELECT Id FROM TaxTreatment "
        "WHERE IsTaxable = true AND Status = 'Active' "
        "ORDER BY CreatedDate DESC LIMIT 1"
    )
    treatment_id = rows[0]["Id"] if rows else None
    if cache_key is not None:
        _TAXABLE_TAX_TREATMENT_BY_ORG[cache_key] = treatment_id
    return treatment_id


def resolve_non_taxable_tax_treatment(client: SfRestClient) -> Optional[str]:
    """Return the id of an Active non-taxable TaxTreatment, or ``None``.

    Posted invoice ingestion requires every InvoiceLine to reference a
    non-taxable TaxTreatment when no InvoiceLineTax records are present:
    the action otherwise resolves the org's default taxable policy and
    rejects with ``INVALID_API_INPUT: You can't specify a tax treatment with
    the isTaxable value as true when the invoice line doesn't have a related
    InvoiceLineTax record`` (live-verified 2026-06-25 on rlm-base__jun17_1).

    ``TaxTreatment`` does not have an ``IsActive`` field; the active set is
    ``Status = 'Active'`` (verified via describe). Cached per org identity so
    repeat scenarios in the same run don't re-query.
    """
    cache_key = _org_cache_key(client)
    if cache_key is not None and cache_key in _NON_TAXABLE_TAX_TREATMENT_BY_ORG:
        return _NON_TAXABLE_TAX_TREATMENT_BY_ORG[cache_key]
    rows = client.query(
        "SELECT Id FROM TaxTreatment "
        "WHERE IsTaxable = false AND Status = 'Active' "
        "ORDER BY CreatedDate ASC LIMIT 1"
    )
    treatment_id = rows[0]["Id"] if rows else None
    if cache_key is not None:
        _NON_TAXABLE_TAX_TREATMENT_BY_ORG[cache_key] = treatment_id
    return treatment_id


def resolve_account(client: SfRestClient, name: str) -> Account:
    """Resolve any account by Name, billing-ready or not.

    Unlike :func:`discover_accounts` (which lists only accounts that *have* a
    BillingAccount), this resolves an account the user pinned in config even
    when it has no BillingAccount -- a quote-only "pipeline" account (example:
    ``Global Media`` in the bundled QB demo dataset). We look up the Account,
    then check for a BillingAccount so the returned ``Account.is_billing_ready``
    correctly caps the stage downstream. The default ``bill_to_contact_id`` is
    populated for downstream ingestion calls.
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
    contact_map = _resolve_default_contact_id(client, [acct_id])
    currency_map = _account_currency_map(client, [acct_id])
    address_map = _resolve_account_addresses(client, [acct_id])
    billing_addr, shipping_addr = address_map.get(acct_id, (None, None))
    return Account(
        id=acct_id,
        name=rows[0].get("Name", name),
        billing_account_id=ba[0]["Id"] if ba else None,
        bill_to_contact_id=contact_map.get(acct_id),
        currency_iso_code=currency_map.get(acct_id),
        billing_address=billing_addr,
        shipping_address=shipping_addr,
    )


def discover_products(
    client: SfRestClient,
    sku: Optional[str] = None,
    limit: int = 25,
) -> list[Product]:
    """Return billable products (active PBE on the standard pricebook)."""
    soql = (
        "SELECT Id, UnitPrice, Product2Id, Product2.Name, "
        "Product2.StockKeepingUnit, ProductSellingModel.SellingModelType, "
        "ProductSellingModel.Name, "
        "ProductSellingModel.PricingTerm, ProductSellingModel.PricingTermUnit "
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
            selling_model_name=psm.get("Name"),
            pricing_term=psm.get("PricingTerm"),
            pricing_term_unit=psm.get("PricingTermUnit"),
        ))
    log.info("discovered %d billable product(s)%s", len(products),
             f" for SKU {sku}" if sku else "")
    return products


def resolve_product(
    client: SfRestClient,
    sku: str,
    selling_model: Optional[str] = None,
) -> Product:
    """Resolve a single billable product by SKU (active PBE on standard PB).

    A SKU can carry multiple active PBEs -- one per ``ProductSellingModel``
    (e.g. a license sold under Annual, Quarterly, and Semi-Annual). When that
    happens and the caller hasn't pinned ``selling_model``, this fails with
    the candidate names rather than silently returning whichever PBE the SOQL
    happens to return first. Pass ``selling_model`` (matching
    ``ProductSellingModel.Name``) to disambiguate.
    """
    # Query without LIMIT so we can detect ambiguity. Bound generously to
    # protect against runaway SKU/PBE setups; real catalogs see < 5.
    candidates = discover_products(client, sku=sku, limit=25)
    if not candidates:
        raise DiscoveryError(
            f"product SKU '{sku}' has no active PricebookEntry on the standard "
            f"pricebook (check the product/pricebook setup)"
        )
    if selling_model is not None:
        matches = [p for p in candidates if p.selling_model_name == selling_model]
        if not matches:
            available = ", ".join(
                sorted({p.selling_model_name or "<unnamed>" for p in candidates})
            )
            raise DiscoveryError(
                f"product SKU '{sku}' has no PBE bound to ProductSellingModel "
                f"'{selling_model}' (available: {available})"
            )
        if len(matches) > 1:
            raise DiscoveryError(
                f"product SKU '{sku}' has {len(matches)} active PBEs bound to "
                f"ProductSellingModel '{selling_model}'; expected exactly one"
            )
        return matches[0]
    if len(candidates) > 1:
        names = ", ".join(
            sorted({p.selling_model_name or "<unnamed>" for p in candidates})
        )
        raise DiscoveryError(
            f"product SKU '{sku}' has {len(candidates)} active PBEs across "
            f"selling models ({names}); pin one with `selling_model:` in config"
        )
    return candidates[0]


@dataclass
class InvoiceLineProduct:
    """Slim Product reference for the Invoice Ingestion path.

    Used by ``kind: invoice_ingestion`` scenarios to optionally attach a
    ``product2Id`` to an ingested InvoiceLine. The ingestion API treats
    ``productId`` as optional; SKUs that do not match an active product
    simply create the line with the literal ``name`` from config and no
    product reference.

    Deliberately narrow: PBE/PSM/term/usage shape is irrelevant for an
    ingested invoice (``chargeAmount`` / ``unitPrice`` come from the
    request body, not a PricebookEntry). Discovered via
    :func:`resolve_invoice_line_product`, not via :func:`resolve_product`
    -- the PST resolver requires an active standard PBE that a
    billing-only org may not have.
    """

    id: str
    name: str
    sku: Optional[str]


def discover_any_accounts(
    client: SfRestClient, limit: int = 25
) -> list[Account]:
    """Return any accounts in the org (billing-ready or not).

    Counterpart to :func:`discover_accounts` for the Invoice Ingestion path,
    which has no BillingAccount prerequisite -- ``Invoice.BillingAccountId``
    on the Composite Graph is the FK to ``Account`` (the ``001...`` key
    prefix), not the ``BillingAccount`` sObject. ``discover_accounts``
    queries ``FROM BillingAccount`` and therefore returns zero rows in
    orgs without billing setup, which is precisely the case ingestion is
    designed to handle. Each row's ``billing_account_id`` is populated
    when an ``Account`` happens to have one (so callers can still inspect
    it), via a second query keyed on the discovered Account ids.
    """
    rows = client.query(
        f"SELECT Id, Name FROM Account ORDER BY Name LIMIT {int(limit)}"
    )
    if not rows:
        return []
    account_ids = [r["Id"] for r in rows]
    quoted = ",".join(f"'{_sql_escape(a)}'" for a in account_ids)
    ba_rows = client.query(
        f"SELECT Id, AccountId FROM BillingAccount WHERE AccountId IN ({quoted})"
    )
    ba_by_account: dict[str, str] = {r["AccountId"]: r["Id"] for r in ba_rows}
    contact_by_account = _resolve_default_contact_id(client, account_ids)
    currency_by_account = _account_currency_map(client, account_ids)
    addresses_by_account = _resolve_account_addresses(client, account_ids)
    accounts = [
        Account(
            id=r["Id"],
            name=r.get("Name", r["Id"]),
            billing_account_id=ba_by_account.get(r["Id"]),
            bill_to_contact_id=contact_by_account.get(r["Id"]),
            currency_iso_code=currency_by_account.get(r["Id"]),
            billing_address=addresses_by_account.get(r["Id"], (None, None))[0],
            shipping_address=addresses_by_account.get(r["Id"], (None, None))[1],
        )
        for r in rows
    ]
    log.info("discovered %d account(s) (any billing state)", len(accounts))
    return accounts


def resolve_invoice_line_product(
    client: SfRestClient, sku: str
) -> Optional[InvoiceLineProduct]:
    """Resolve a product SKU for the Invoice Ingestion path.

    Returns ``None`` (not raises) when the SKU does not match an active
    ``Product2`` -- ingestion treats ``productId`` as optional, so a miss
    means "ingest the line with the literal name and no product ref".
    Unlike :func:`resolve_product`, this does NOT require an active PBE
    on the standard pricebook, so it works in billing-only orgs that have
    no pricebook wired up.
    """
    rows = client.query(
        "SELECT Id, Name, StockKeepingUnit FROM Product2 "
        f"WHERE StockKeepingUnit = '{_sql_escape(sku)}' AND IsActive = true LIMIT 1"
    )
    if not rows:
        return None
    return InvoiceLineProduct(
        id=rows[0]["Id"],
        name=rows[0].get("Name", rows[0]["Id"]),
        sku=rows[0].get("StockKeepingUnit"),
    )


def discover_usage_bindings(
    client: SfRestClient, product_ids: list[str]
) -> dict[str, list[UsageResourceBinding]]:
    """Return per-product usage resource bindings keyed by Product2 Id.

    ``ProductUsageResource.ProductId`` is the FK (relationship name
    ``ProductOffer``) -- *not* ``Product2Id``. Status is not filtered: QB seed
    records ship as ``Draft`` and are still the bindings the org actually uses.
    """
    if not product_ids:
        return {}
    quoted = ",".join(f"'{_sql_escape(pid)}'" for pid in product_ids)
    soql = (
        "SELECT ProductId, UsageResourceId, "
        "UsageResource.Code, UsageResource.Name, "
        "UsageResource.UnitOfMeasureClassId, "
        "UsageResource.DefaultUnitOfMeasureId, "
        "UsageResource.DefaultUnitOfMeasure.UnitCode, "
        "UsageResource.DefaultUnitOfMeasure.Name "
        f"FROM ProductUsageResource WHERE ProductId IN ({quoted})"
    )
    by_product: dict[str, list[UsageResourceBinding]] = {}
    for r in client.query(soql):
        ur = r.get("UsageResource") or {}
        duom = ur.get("DefaultUnitOfMeasure") or {}
        binding = UsageResourceBinding(
            resource_id=r["UsageResourceId"],
            resource_code=ur.get("Code", r["UsageResourceId"]),
            resource_name=ur.get("Name"),
            uom_class_id=ur.get("UnitOfMeasureClassId"),
            default_uom_id=ur.get("DefaultUnitOfMeasureId"),
            default_uom_code=duom.get("UnitCode"),
            default_uom_name=duom.get("Name"),
        )
        by_product.setdefault(r["ProductId"], []).append(binding)
    log.info(
        "discovered usage bindings for %d/%d product(s)",
        len(by_product), len(product_ids),
    )
    return by_product


def attach_usage_bindings(
    client: SfRestClient, products: list[Product]
) -> None:
    """Populate ``Product.usage_bindings`` in place for the given products."""
    bindings = discover_usage_bindings(client, [p.id for p in products])
    for p in products:
        p.usage_bindings = bindings.get(p.id, [])


def resolve_uom_override(
    client: SfRestClient, binding: UsageResourceBinding, unit_code: str
) -> str:
    """Resolve a UoM UnitCode override against the resource's UoM class.

    Mirrors ``RLM_UsageUploaderController.validateUsageEntries``: the candidate
    UoM must share the resource's ``UnitOfMeasureClassId`` and be ``Active``.
    """
    if binding.uom_class_id is None:
        raise DiscoveryError(
            f"resource '{binding.resource_code}' has no UnitOfMeasureClassId; "
            f"cannot validate UoM override '{unit_code}'"
        )
    recs = client.query(
        "SELECT Id FROM UnitOfMeasure "
        f"WHERE UnitCode = '{_sql_escape(unit_code)}' "
        f"AND UnitOfMeasureClassId = '{_sql_escape(binding.uom_class_id)}' "
        "AND Status = 'Active' LIMIT 1"
    )
    if not recs:
        raise DiscoveryError(
            f"UoM '{unit_code}' is not an active unit in the UoM class for "
            f"resource '{binding.resource_code}'"
        )
    return recs[0]["Id"]


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
        non_taxable_tax_treatment_id=resolve_non_taxable_tax_treatment(client),
        taxable_tax_treatment_id=resolve_taxable_tax_treatment(client),
    )
    return ctx
