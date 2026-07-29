#!/usr/bin/env python3
"""
Set up (or reuse) the Home Services milestone Billing Schedule in Salesforce RLM.

Idempotent: queries for existing records before creating, and only activates
records that are not already active. Prints the billing policy ID on the last
line as `BILLING_POLICY_ID=<id>` so callers can capture it.

Confirmed field requirements (do not "simplify" these — the API rejects the
records without them):
  BillingPolicy         : Status must be inserted as 'Draft'; BillingTreatmentSelection required.
                          Activation requires DefaultBillingTreatmentId + an active treatment.
  BillingTreatment      : Status='Draft', ExcludeFromBilling='No', IsMilestoneBilling=true,
                          CanChangeBillingFrequency=false.
  BillingTreatmentItem  : field is 'Percentage' (NOT 'Percent'); BillingType MUST be 'None'
                          for milestone billing; 'Remainder' Type is rejected — every item
                          is Type='Percentage' and the 12 percentages sum to 100.
Activation order: items -> treatment -> policy.
"""

import json, subprocess, sys, urllib.request, urllib.error, urllib.parse

POLICY_NAME    = "Monthly Service - Home Services"
TREATMENT_NAME = "Home Services Billing Treatment"

# 11 x 8.333 + 8.337 = 100.000
MONTH_PERCENTAGES = [8.333] * 11 + [8.337]


def get_org_info():
    result = subprocess.run(["sf", "org", "display", "--json"],
                            capture_output=True, text=True)
    data = json.loads(result.stdout)["result"]
    api = data.get("apiVersion", "66.0")
    return data["accessToken"], data["instanceUrl"], api


ACCESS_TOKEN, INSTANCE_URL, API_VERSION = get_org_info()
BASE_URL = f"{INSTANCE_URL}/services/data/v{API_VERSION}"


def sf_query(soql):
    url = f"{BASE_URL}/query?q={urllib.parse.quote(soql)}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {ACCESS_TOKEN}"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read()).get("records", [])


def sf_post(sobject, body):
    url = f"{BASE_URL}/sobjects/{sobject}"
    payload = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=payload, method="POST",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}",
                 "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            result = json.loads(r.read())
            if not result.get("success"):
                print(f"  ERROR creating {sobject}: {result}", file=sys.stderr); sys.exit(1)
            return result["id"]
    except urllib.error.HTTPError as e:
        print(f"  HTTP {e.code} creating {sobject}: {e.read().decode()}", file=sys.stderr); sys.exit(1)


def sf_patch(sobject, record_id, body):
    url = f"{BASE_URL}/sobjects/{sobject}/{record_id}"
    payload = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=payload, method="PATCH",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}",
                 "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            r.read()  # 204 No Content on success
    except urllib.error.HTTPError as e:
        print(f"  HTTP {e.code} updating {sobject} {record_id}: {e.read().decode()}", file=sys.stderr); sys.exit(1)


# ── Billing Policy ───────────────────────────────────────────────────────────
existing = sf_query(f"SELECT Id, Status FROM BillingPolicy WHERE Name='{POLICY_NAME}'")
if existing:
    policy_id = existing[0]["Id"]
    policy_status = existing[0]["Status"]
    print(f"BillingPolicy: {policy_id} (existing, {policy_status})")
else:
    policy_id = sf_post("BillingPolicy", {
        "Name": POLICY_NAME,
        "Status": "Draft",                       # cannot insert as Active
        "BillingTreatmentSelection": "Default",
    })
    policy_status = "Draft"
    print(f"BillingPolicy: {policy_id} (created, Draft)")

# ── Billing Treatment ────────────────────────────────────────────────────────
existing = sf_query(
    f"SELECT Id, Status FROM BillingTreatment "
    f"WHERE Name='{TREATMENT_NAME}' AND BillingPolicyId='{policy_id}'")
if existing:
    treatment_id = existing[0]["Id"]
    treatment_status = existing[0]["Status"]
    print(f"BillingTreatment: {treatment_id} (existing, {treatment_status})")
else:
    treatment_id = sf_post("BillingTreatment", {
        "Name": TREATMENT_NAME,
        "BillingPolicyId": policy_id,
        "Status": "Draft",
        "ExcludeFromBilling": "No",
        "IsMilestoneBilling": True,
        "CanChangeBillingFrequency": False,
    })
    treatment_status = "Draft"
    print(f"BillingTreatment: {treatment_id} (created, Draft)")

# ── Billing Treatment Items (12) ─────────────────────────────────────────────
existing_items = sf_query(
    f"SELECT Id, ProcessingOrder, Status FROM BillingTreatmentItem "
    f"WHERE BillingTreatmentId='{treatment_id}'")
items_by_order = {int(i["ProcessingOrder"]): i for i in existing_items}

for n in range(1, 13):
    pct = MONTH_PERCENTAGES[n - 1]
    if n in items_by_order:
        print(f"  Item month {n}: {items_by_order[n]['Id']} (existing)")
        continue
    item_id = sf_post("BillingTreatmentItem", {
        "Name": f"Month {n} Service",
        "BillingTreatmentId": treatment_id,
        "ProcessingOrder": n,
        "Type": "Percentage",       # 'Remainder' is rejected for milestone billing
        "Percentage": pct,          # field is 'Percentage', NOT 'Percent'
        "BillingType": "None",      # required = None for milestone billing
        "Sequencing": "None",
        "Controller": "None",
        "Handling0Amount": "None",
        "MilestoneType": "Event",
        "Status": "Draft",
    })
    items_by_order[n] = {"Id": item_id, "Status": "Draft"}
    print(f"  Item month {n}: {item_id} (created, {pct}%)")

# ── Activation: items -> treatment -> policy ─────────────────────────────────
for n in range(1, 13):
    item = items_by_order[n]
    if item.get("Status") != "Active":
        sf_patch("BillingTreatmentItem", item["Id"], {"Status": "Active"})
print("  All 12 items Active")

if treatment_status != "Active":
    sf_patch("BillingTreatment", treatment_id, {"Status": "Active"})
    print("  BillingTreatment activated")

if policy_status != "Active":
    sf_patch("BillingPolicy", policy_id,
             {"DefaultBillingTreatmentId": treatment_id, "Status": "Active"})
    print("  BillingPolicy activated")

print(f"\nBILLING_POLICY_ID={policy_id}")
