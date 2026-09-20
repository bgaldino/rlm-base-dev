#!/usr/bin/env python3
"""
Validate a customer demo SKU contract, optionally against an org snapshot.

Runs the mechanical half of the Integrator's checks (wave 5 of the onboarding flow)
before any dataset is authored or deployed. Catches the documented failure modes:
RateCardEntry/PricebookEntry selling model drift, empty CategoryCode, missing
ConfigureDuringSale on attribute SKUs, duplicate AttributePicklistValue codes,
Pack instead of Anchor on sellable usage SKUs, grant policies absent from the org,
Tier rate card entries carrying a Rate, and DRO step groups that do not exist.

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


class Report:
    def __init__(self):
        self.issues = []

    def fail(self, check, detail):
        self.issues.append((check, detail))

    def __len__(self):
        return len(self.issues)


def _org_sets(org):
    """Extract lookup sets from the org snapshot, or None when unavailable."""
    if not org or not org.get("reachable", True):
        return None
    g = org.get
    return {
        "psm": {(r["Name"], r["SellingModelType"]) for r in g("productSellingModels", [])},
        "psm_names": {r["Name"] for r in g("productSellingModels", [])},
        "uom": {r["UnitCode"] for r in g("unitsOfMeasure", [])},
        "proration": {r["Name"] for r in g("prorationPolicies", [])},
        "renewal": {r["Code"] for r in g("usageGrantRenewalPolicies", [])},
        "rollover": {r["Code"] for r in g("usageGrantRolloverPolicies", [])},
        "overage": {r["Name"] for r in g("usageOveragePolicies", [])},
        "groups": {r["Name"] for r in g("fulfillmentStepDefinitionGroups", [])},
    }


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
        # already exist. Units with a class_code are created by the PCM builder.
        for un in uom.get("units", []):
            if not un.get("class_code") and un["unit_code"] not in org["uom"]:
                rep.fail("uom-exists", f"UnitOfMeasure '{un['unit_code']}' has no class_code "
                                       "(treated as an org-native reference) but does not "
                                       "exist in the org")

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
    check_catalog(contract, rep)
    check_skus(contract, org, rep)
    check_attributes(contract, rep)
    check_pricing(contract, rep)
    check_billing(contract, rep)
    check_usage(contract, org, rep)
    check_dro(contract, org, rep)

    flags = contract.get("flags") or {}
    enabled = [k for k, v in flags.items() if v] or ["none"]
    print(f"contract: {contract['customer']['name']} (prefix {contract['customer']['prefix']})")
    print(f"  {len(contract['skus'])} SKUs, {len(contract.get('categories', []))} categories, "
          f"{len(contract.get('pricing_rules', []) or [])} pricing rules")
    print(f"  flags: {', '.join(enabled)}")
    print(f"  org context: {'loaded' if org else 'UNAVAILABLE — org-dependent checks skipped'}\n")

    if rep.issues:
        print(f"{len(rep)} issue(s):")
        for check, detail in rep.issues:
            print(f"  [{check}] {detail}")
        return 1
    print("All contract checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
