#!/usr/bin/env python3
"""
Validate a customer demo SKU contract, optionally against an org snapshot.

Runs the mechanical half of the Integrator's checks (wave 5 of the onboarding flow)
before any dataset is authored or deployed. Catches the documented failure modes:
RateCardEntry/PricebookEntry selling model drift, empty CategoryCode, missing
ConfigureDuringSale on attribute SKUs, duplicate AttributePicklistValue codes,
Pack instead of Anchor on sellable usage SKUs, grant policies absent from the org,
Tier rate card entries carrying a Rate, and DRO step groups that do not exist.

Also guards the shared-org failure modes: a missing or invalid org.load_mode, a SKU
prefix another customer's demo already owns, a name that would Upsert over an existing
org record, and a UnitOfMeasure that already belongs to a different UnitOfMeasureClass.

Usage:
    python scripts/customer-demo/validate_sku_contract.py [contract.yaml] [--org-context org-context.json]
    python scripts/customer-demo/validate_sku_contract.py --emit-pricebook > scripts/customer-demo/customer-pricebook-entries.csv

Defaults:
    contract      datasets/sfdmu/customer-template/en-US/sku-contract.yaml
    org-context   datasets/sfdmu/customer-template/en-US/org-context.json (skipped if absent)

Exit codes:
    0  all checks passed
    1  one or more issues found
    2  bad input (missing file, unparseable, missing dependency)

Schema: docs/references/customer-demo-sku-contract.md
"""
import argparse
import json
import os
import sys
from collections import Counter

try:
    import yaml
except ImportError:
    sys.stderr.write(
        "PyYAML is required.\n"
        "Run with the CumulusCI environment, e.g.\n"
        "  ~/.local/pipx/venvs/cumulusci/bin/python3 scripts/customer-demo/validate_sku_contract.py\n"
        "or install it:  python3 -m pip install pyyaml\n"
    )
    sys.exit(2)

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_CONTRACT = os.path.join(
    REPO, "datasets/sfdmu/customer-template/en-US/sku-contract.yaml")
DEFAULT_ORG_CONTEXT = os.path.join(
    REPO, "datasets/sfdmu/customer-template/en-US/org-context.json")

PRICEBOOK_COLUMNS = [
    "SKU", "UnitPrice", "CurrencyIsoCode", "PSMName", "PSMSellingModelType", "IsActive",
    "CategoryCode", "ImageRequired", "BillingRequired", "BillingPolicyName",
    "ProductTypeExpected", "ExpectedPricingRules",
]

LOAD_MODES = ("additive", "clean")

# Contract paths that load via SFDMU Upsert on a name/code key: a value already present
# in the org silently mutates that record instead of creating a new one. Each entry maps
# the contract path to the org-context existingNames key holding the taken values.
NAME_COLLISION_PATHS = [
    ("billing.payment_terms[].name", "paymentTerms"),
    ("billing.policies[].name", "billingPolicies"),
    ("billing.policies[].treatment", "billingTreatments"),
    ("billing.legal_entity", "legalEntities"),
    ("attributes.definitions[].developer_name", "attributeDefinitions"),
    ("attributes.picklists[].values[].code", "attributePicklistValueCodes"),
]


class Report:
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.notes = []

    def fail(self, check, detail):
        self.issues.append((check, detail))

    def warn(self, check, detail):
        self.warnings.append((check, detail))

    def unverified(self, detail):
        self.notes.append(detail)

    def __len__(self):
        return len(self.issues)


def _org_sets(org):
    """Extract lookup sets from the org snapshot, or None when unavailable."""
    if not org or not org.get("reachable", True):
        return None
    g = org.get
    units = g("unitsOfMeasure", []) or []
    return {
        "psm": {(r["Name"], r["SellingModelType"]) for r in g("productSellingModels", [])},
        "psm_names": {r["Name"] for r in g("productSellingModels", [])},
        "uom": {r["UnitCode"] for r in g("unitsOfMeasure", [])},
        "proration": {r["Name"] for r in g("prorationPolicies", [])},
        "renewal": {r["Code"] for r in g("usageGrantRenewalPolicies", [])},
        "rollover": {r["Code"] for r in g("usageGrantRolloverPolicies", [])},
        "overage": {r["Name"] for r in g("usageOveragePolicies", [])},
        "groups": {r["Name"] for r in g("fulfillmentStepDefinitionGroups", [])},
        # Newer Org Discovery snapshots only. Absent keys stay None so the dependent
        # check reports itself unverified instead of passing on no evidence.
        "uom_records": {r["UnitCode"]: r for r in units},
        "uom_has_class": any("ClassCode" in r for r in units),
        "existing_names": g("existingNames"),
        "occupied_prefixes": g("occupiedSkuPrefixes"),
    }


def _key(value):
    """Fold a name/code to the form Upsert matching effectively compares on."""
    return str(value).strip().casefold()


def _bare_prefix(value):
    """'SF-' and 'SF' both reduce to 'SF' so occupied prefixes compare either way."""
    return str(value or "").strip().rstrip("-").upper()


def _self_owned(value, c):
    """True when a name sits inside this customer's own namespace.

    An org snapshot captured after a previous load of this same contract reports the
    contract's own records as existing. A value carrying the customer prefix or the
    customer name is that case, not a foreign record about to be overwritten.
    """
    v = _key(value)
    prefix = _key(c["customer"]["prefix"])
    name = _key(c["customer"].get("name"))
    return bool(prefix and prefix in v) or bool(len(name) >= 4 and name in v)


def _snapshot_postdates_load(c, org):
    """True when the org snapshot already contains this contract's own records.

    Org Discovery is meant to run before the load. When it runs after one — the normal
    case on a re-run — every name this contract owns comes back as 'existing'. Those are
    not collisions, so the collision checks report them as one informational warning
    instead of failing the contract on its own output.
    """
    existing = (org or {}).get("existing_names") or {}
    return any(_self_owned(v, c) for values in existing.values() for v in values or [])


def check_org(c, rep):
    org_block = c.get("org") or {}
    mode = str(org_block.get("load_mode") or "").strip()
    if not mode:
        rep.fail("load-mode-missing",
                 "org.load_mode is required — set 'clean' when the org is dedicated to this "
                 "customer (prepare_customer_demo_catalog runs, its scoped deletes are safe) "
                 "or 'additive' when the org already holds another customer's demo data "
                 "(prepare_customer_demo_catalog_additive runs, every delete and purge step "
                 "removed)")
    elif mode not in LOAD_MODES:
        rep.fail("load-mode-invalid",
                 f"org.load_mode '{mode}' is not one of {', '.join(LOAD_MODES)}")


def check_prefix(c, org, rep):
    prefix = c["customer"]["prefix"]
    mine = _bare_prefix(prefix)
    if org is None:
        return
    occupied = org["occupied_prefixes"]
    if occupied is None:
        rep.unverified("SKU prefix collision — org context has no 'occupiedSkuPrefixes'")
        return
    for occ in occupied:
        theirs = _bare_prefix(occ)
        if not theirs:
            continue
        if theirs == mine:
            rep.fail("prefix-collision",
                     f"customer.prefix '{prefix}' produces {mine}-* SKUs and '{occ}' is already "
                     "in use in this org. If another demo owns it, pick an unused prefix — "
                     f"scoped deletes and verify queries (WHERE Name LIKE '{mine}-%') cannot "
                     "tell the two catalogs apart. If it is this contract's own catalog from an "
                     "earlier load, re-capture org-context.json before the load so the snapshot "
                     "reflects pre-load state")
        elif mine.startswith(theirs) or theirs.startswith(mine):
            rep.warn("prefix-near-miss",
                     f"customer.prefix '{prefix}' overlaps occupied prefix '{occ}' — the SKUs "
                     f"do not collide, but a scoped LIKE pattern written against the shorter of "
                     "the two will match both catalogs")


def check_name_collisions(c, org, rep):
    if org is None:
        return
    existing = org["existing_names"]
    if existing is None:
        rep.unverified("name collisions with existing org records — org context has no "
                       "'existingNames'")
        return
    prefix = c["customer"]["prefix"]
    billing = c.get("billing") or {}
    attrs = c.get("attributes") or {}
    declared = {
        "paymentTerms": [t.get("name") for t in billing.get("payment_terms", []) or []],
        "billingPolicies": [p.get("name") for p in billing.get("policies", []) or []],
        "billingTreatments": [p.get("treatment") for p in billing.get("policies", []) or []],
        "legalEntities": [billing.get("legal_entity")],
        "attributeDefinitions": [d.get("developer_name")
                                 for d in attrs.get("definitions", []) or []],
        "attributePicklistValueCodes": [v.get("code")
                                        for p in attrs.get("picklists", []) or []
                                        for v in p.get("values", []) or []],
    }
    for path, key in NAME_COLLISION_PATHS:
        if key not in existing:
            rep.unverified(f"{path} — org context existingNames has no '{key}'")
            continue
        taken = {_key(v): v for v in existing[key] or []}
        for value in declared[key]:
            if not value:
                continue
            hit = taken.get(_key(value))
            if hit is None:
                continue
            if _self_owned(value, c):
                rep.warn("name-collision-self",
                         f"{path} '{value}' already exists in the org as '{hit}'. It is inside "
                         "this customer's namespace, so it is almost certainly this contract's "
                         "own record from an earlier load and the Upsert will update it in "
                         "place — confirm that, or rename if it belongs to someone else")
            else:
                rep.fail("name-collision",
                         f"{path} '{value}' already exists in the org and is outside this "
                         "customer's namespace — it loads via Upsert on the name key, so the "
                         "load would silently overwrite that record; prefix it with the "
                         f"customer prefix '{prefix}'")


def check_unprefixed_names(c, rep):
    prefix = str(c["customer"]["prefix"] or "").strip()
    if not prefix:
        return
    billing = c.get("billing") or {}
    targets = [("billing.payment_terms[].name", t.get("name"))
               for t in billing.get("payment_terms", []) or []]
    targets += [("billing.policies[].name", p.get("name"))
                for p in billing.get("policies", []) or []]
    targets.append(("catalog.name", (c.get("catalog") or {}).get("name")))
    for path, value in targets:
        if value and prefix.casefold() not in str(value).casefold():
            rep.warn("name-unprefixed",
                     f"{path} '{value}' does not carry the customer prefix '{prefix}' — this "
                     "record upserts on its name, so a generic name can land on an unrelated "
                     "record that already exists in the org")


def check_skus(c, org, rep):
    cats = {x["code"] for x in c.get("categories", [])}
    for s in c["skus"]:
        sku = s["sku"]
        if not s.get("category_code"):
            rep.fail("category-empty", f"{sku}: CategoryCode empty (verify reports a missing "
                                       "ProductCategoryProduct on every SKU)")
        elif s["category_code"] not in cats:
            rep.fail("category-unknown", f"{sku}: {s['category_code']} not in categories")

        if (s.get("product_type_expected") or "") != (s.get("type") or ""):
            rep.fail("type-expected",
                     f"{sku}: type={s.get('type') or ''!r} vs "
                     f"product_type_expected={s.get('product_type_expected') or ''!r}")

        if s.get("type") == "Bundle" and s.get("configure_during_sale") != "Allowed":
            rep.fail("cds-bundle", f"{sku}: Type=Bundle requires ConfigureDuringSale=Allowed")

        if org:
            if s["psm_name"] not in org["psm_names"]:
                rep.fail("psm-exists", f"{sku}: ProductSellingModel '{s['psm_name']}' not in org")
            elif (s["psm_name"], s["psm_selling_model_type"]) not in org["psm"]:
                rep.fail("psm-type", f"{sku}: '{s['psm_name']}' is not "
                                     f"{s['psm_selling_model_type']} in org")


def check_attributes(c, rep):
    skus = {s["sku"] for s in c["skus"]}
    by_sku = {s["sku"]: s for s in c["skus"]}
    attrs = c.get("attributes", {}) or {}

    codes = [v["code"] for p in attrs.get("picklists", []) for v in p.get("values", [])]
    for code, n in Counter(codes).items():
        if n > 1:
            rep.fail("apv-dup", f"AttributePicklistValue.Code '{code}' used {n}x — Code is a "
                                "GLOBAL externalId and collisions cascade-fail PCM")

    prefix = c["customer"]["prefix"]
    for d in attrs.get("definitions", []):
        if not d["developer_name"].startswith(prefix):
            rep.fail("attrdef-prefix",
                     f"AttributeDefinition.DeveloperName '{d['developer_name']}' is not "
                     f"prefixed with '{prefix}' (org-unique namespace)")
        for sku in d.get("applies_to_skus", []):
            if sku not in skus:
                rep.fail("attr-sku-unknown", f"attribute {d['code']} references unknown SKU {sku}")
            elif by_sku[sku].get("configure_during_sale") != "Allowed":
                rep.fail("cds-attr", f"{sku}: has attributes but ConfigureDuringSale != Allowed "
                                     "(attribute panel never renders; pricing never fires)")


def check_pricing(c, rep):
    counts = Counter(r["sku"] for r in c.get("pricing_rules", []) or [])
    attr_codes = {d["code"] for d in (c.get("attributes", {}) or {}).get("definitions", [])}
    for s in c["skus"]:
        declared = s.get("expected_pricing_rules", 0) or 0
        actual = counts.get(s["sku"], 0)
        if actual != declared:
            rep.fail("pricing-count", f"{s['sku']}: {actual} pricing_rules vs "
                                      f"expected_pricing_rules={declared}")
    for r in c.get("pricing_rules", []) or []:
        if r.get("operator") != "equals":
            rep.fail("operator", f"{r['rule_name']}: Operator must be the word 'equals', "
                                 f"got {r.get('operator')!r}")
        if r.get("attribute_code") not in attr_codes:
            rep.fail("rule-attr", f"{r['rule_name']}: attribute_code "
                                  f"'{r.get('attribute_code')}' not in attributes.definitions")


def check_billing(c, rep):
    billing = c.get("billing") or {}
    policies = {p["name"] for p in billing.get("policies", [])}
    terms = {t["name"] for t in billing.get("payment_terms", [])}
    if not billing:
        rep.fail("billing-missing", "contract has no billing section; the Billing builder "
                                    "cannot create LegalEntity/PaymentTerm/BillingPolicy")
        return
    for s in c["skus"]:
        if not s.get("billing_required"):
            continue
        name = s.get("billing_policy_name") or ""
        if not name:
            rep.fail("billing-policy-empty", f"{s['sku']}: billing_required but no policy name")
        elif name not in policies:
            rep.fail("billing-policy-unknown",
                     f"{s['sku']}: billing_policy_name '{name}' not in billing.policies")
    for p in billing.get("policies", []):
        if p.get("payment_term") and p["payment_term"] not in terms:
            rep.fail("payment-term-unknown",
                     f"policy '{p['name']}': payment_term '{p['payment_term']}' "
                     "not in billing.payment_terms")


def check_usage(c, org, rep):
    if not (c.get("flags") or {}).get("customer_demo_usage"):
        return
    by_sku = {s["sku"]: s for s in c["skus"]}
    u = c.get("usage") or {}
    resources = {r["code"]: r for r in u.get("resources", [])}
    uom = c.get("uom", {}) or {}
    unit_names = {x["name"] for x in uom.get("units", [])}
    class_names = {x["name"] for x in uom.get("classes", [])}

    for s in c["skus"]:
        us = s.get("usage") or {}
        if us.get("role") == "sellable":
            if us.get("usage_model_type") != "Anchor":
                rep.fail("usage-model", f"{s['sku']}: sellable usage SKU must be "
                                        "UsageModelType=Anchor (Pack blocks "
                                        "ProductUsageResourcePolicy)")
            if us.get("usage_resource_code") not in resources:
                rep.fail("usage-ur", f"{s['sku']}: unknown usage_resource_code "
                                     f"'{us.get('usage_resource_code')}'")

    for r in u.get("resources", []):
        if r.get("definition_sku") not in by_sku:
            rep.fail("usage-def", f"{r['code']}: definition_sku "
                                  f"'{r.get('definition_sku')}' is not a contract SKU")
        if r.get("uom_class_name") not in class_names:
            rep.fail("usage-class", f"{r['code']}: uom_class_name "
                                    f"'{r.get('uom_class_name')}' not in uom.classes")
        if r.get("default_uom_name") not in unit_names:
            rep.fail("usage-uom", f"{r['code']}: default_uom_name "
                                  f"'{r.get('default_uom_name')}' not in uom.units")

    if org:
        gp = u.get("grant_policies", {}) or {}
        for key, bucket, label in (("renewal_code", "renewal", "UsageGrantRenewalPolicy"),
                                   ("rollover_code", "rollover", "UsageGrantRolloverPolicy"),
                                   ("overage_name", "overage", "UsageOveragePolicy")):
            val = gp.get(key)
            if val and val not in org[bucket]:
                rep.fail(f"grant-{bucket}", f"{label} '{val}' does not exist in the org — "
                                            "SFDMU silently fails to create these")
        # Units with no class_code are references to org-native UOMs (e.g. EACH) and must
        # already exist. Units with a class_code are created by the PCM builder — and a
        # UnitOfMeasure belongs to exactly one UnitOfMeasureClass, so one that already
        # exists under a different class cannot be reused.
        claiming = [un for un in uom.get("units", []) if un.get("class_code")]
        if claiming and not org["uom_has_class"]:
            rep.unverified("UnitOfMeasure class ownership — org context unitsOfMeasure "
                           "entries carry no 'ClassCode'")
        for un in uom.get("units", []):
            if not un.get("class_code"):
                if un["unit_code"] not in org["uom"]:
                    rep.fail("uom-exists", f"UnitOfMeasure '{un['unit_code']}' has no class_code "
                                           "(treated as an org-native reference) but does not "
                                           "exist in the org")
                continue
            existing = org["uom_records"].get(un["unit_code"]) or {}
            owner = str(existing.get("ClassCode") or "").strip()
            if owner and owner != un["class_code"]:
                rep.fail("uom-class-owned",
                         f"UnitOfMeasure '{un['unit_code']}' already exists in the org as "
                         f"'{existing.get('Name') or un['unit_code']}' under class '{owner}', "
                         f"but the contract assigns it to '{un['class_code']}' — a unit belongs "
                         "to exactly one class and cannot be moved; declare a new unit_code for "
                         "this customer")

    for card in u.get("rate_cards", []):
        for e in card.get("entries", []):
            tag = f"{card['name']}/{e.get('sku')}"
            if e.get("sku") not in by_sku:
                rep.fail("rce-sku", f"{tag}: unknown SKU")
                continue
            if e.get("psm_name") != by_sku[e["sku"]]["psm_name"]:
                rep.fail("rce-psm", f"{tag}: RateCardEntry PSM '{e.get('psm_name')}' != "
                                    f"PricebookEntry PSM '{by_sku[e['sku']]['psm_name']}'")
            declared_units = {x["unit_code"] for x in uom.get("units", [])}
            if e.get("rate_uom") not in declared_units and not (
                    org and e.get("rate_uom") in org["uom"]):
                rep.fail("rce-uom", f"{tag}: rate UOM '{e.get('rate_uom')}' is neither "
                                    "declared in uom.units nor present in the org")
            if card.get("type") == "Tier":
                if e.get("rate") not in ("", None):
                    rep.fail("tier-rate", f"{tag}: Tier RateCardEntry must leave Rate empty "
                                          "(bands live on RateAdjustmentByTier)")
                if not e.get("tiers"):
                    rep.fail("tier-bands", f"{tag}: Tier RateCardEntry has no tier bands")
            elif e.get("rate") in ("", None):
                rep.fail("base-rate", f"{tag}: Base RateCardEntry needs a Rate")


def check_dro(c, org, rep):
    if not (c.get("flags") or {}).get("customer_demo_dro"):
        return
    by_sku = {s["sku"] for s in c["skus"]}
    for sc in (c.get("dro") or {}).get("scenarios", []):
        if sc.get("sku") not in by_sku:
            rep.fail("dro-sku", f"DRO scenario references unknown SKU '{sc.get('sku')}'")
        if org and sc.get("step_group") not in org["groups"]:
            rep.fail("dro-group", f"{sc.get('sku')}: FulfillmentStepDefinitionGroup "
                                  f"'{sc.get('step_group')}' not in org — SFDMU would set "
                                  "FulfillmentStepDefnGroupId=null with no error")


def check_catalog(c, rep):
    if not (c.get("catalog") or {}).get("name"):
        rep.fail("catalog-missing", "contract has no catalog.name; the PCM builder cannot "
                                    "create ProductCatalog deterministically")


def pricebook_rows(c):
    out = [",".join(PRICEBOOK_COLUMNS)]
    for s in c["skus"]:
        out.append(",".join([
            s["sku"], str(s["unit_price"]), s["currency"], s["psm_name"],
            s["psm_selling_model_type"], "true", s.get("category_code", ""),
            str(bool(s.get("image_required"))).lower(),
            str(bool(s.get("billing_required"))).lower(),
            s.get("billing_policy_name") or "",
            s.get("product_type_expected") or "",
            str(s.get("expected_pricing_rules", 0) or 0),
        ]))
    return out


def main():
    ap = argparse.ArgumentParser(description="Validate a customer demo SKU contract.")
    ap.add_argument("contract", nargs="?", default=DEFAULT_CONTRACT)
    ap.add_argument("--org-context", default=DEFAULT_ORG_CONTEXT)
    ap.add_argument("--emit-pricebook", action="store_true",
                    help="print the customer-pricebook-entries.csv projection and exit")
    args = ap.parse_args()

    if not os.path.exists(args.contract):
        sys.stderr.write(f"contract not found: {args.contract}\n")
        return 2
    try:
        contract = yaml.safe_load(open(args.contract))
    except yaml.YAMLError as e:
        sys.stderr.write(f"could not parse {args.contract}: {e}\n")
        return 2
    if not contract or "skus" not in contract:
        sys.stderr.write(f"{args.contract} has no 'skus' list\n")
        return 2

    if args.emit_pricebook:
        print("\n".join(pricebook_rows(contract)))
        return 0

    org_raw = None
    if os.path.exists(args.org_context):
        try:
            org_raw = json.load(open(args.org_context))
        except (json.JSONDecodeError, OSError) as e:
            sys.stderr.write(f"warning: could not read org context: {e}\n")
    org = _org_sets(org_raw)

    rep = Report()
    check_org(contract, rep)
    check_catalog(contract, rep)
    check_skus(contract, org, rep)
    check_attributes(contract, rep)
    check_pricing(contract, rep)
    check_billing(contract, rep)
    check_usage(contract, org, rep)
    check_dro(contract, org, rep)
    check_prefix(contract, org, rep)
    check_name_collisions(contract, org, rep)
    check_unprefixed_names(contract, rep)

    flags = contract.get("flags") or {}
    enabled = [k for k, v in flags.items() if v] or ["none"]
    load_mode = ((contract.get("org") or {}).get("load_mode") or "unset")
    print(f"contract: {contract['customer']['name']} (prefix {contract['customer']['prefix']})")
    print(f"  {len(contract['skus'])} SKUs, {len(contract.get('categories', []))} categories, "
          f"{len(contract.get('pricing_rules', []) or [])} pricing rules")
    print(f"  flags: {', '.join(enabled)}")
    print(f"  load mode: {load_mode}")
    print(f"  org context: {'loaded' if org else 'UNAVAILABLE — org-dependent checks skipped'}\n")

    if rep.issues:
        print(f"{len(rep)} issue(s):")
        for check, detail in rep.issues:
            print(f"  [{check}] {detail}")
    if rep.warnings:
        print(f"\n{len(rep.warnings)} warning(s):")
        for check, detail in rep.warnings:
            print(f"  [{check}] {detail}")
    if rep.notes:
        print(f"\n{len(rep.notes)} check(s) unverified — re-run Org Discovery to populate:")
        for detail in rep.notes:
            print(f"  {detail}")
    if rep.issues:
        return 1
    print("\nAll contract checks passed." if (rep.warnings or rep.notes)
          else "All contract checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
