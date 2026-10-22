#!/usr/bin/env python3
"""Rentokil residential pest demo driver (Michael Reyes / Bloomingdale).

Places a field Quote (Home Protection + Initial Service + optional Mosquito) via
Place Sales Transaction with location zone pricing, converts to Order, activates,
and optionally drives Initial Treatment DRO / Work Order completion.

Usage:
    python scripts/place_pest_demo_order.py --target-org fsl-rc
    python scripts/place_pest_demo_order.py --target-org fsl-rc --activate --complete-initial
"""

from __future__ import annotations

import argparse
import datetime
import json
import subprocess
import sys
import tempfile
import time

API = "v66.0"
DEFAULT_ACCOUNT = "Michael Reyes"
DEFAULT_PLAN = "RTK-HOME-PROT"
INITIAL_SKU = "RTK-INITIAL"
MOSQUITO_SKU = "RTK-MOSQUITO"
TERMITE_SKU = "RTK-TERMITE"
CREATE_WO_STEP = "Create Initial Treatment Work Order"


def sf(args, target_org):
    cmd = ["sf", *args, "--target-org", target_org]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 and not result.stdout.strip().startswith(("{", "[")):
        raise RuntimeError(f"{' '.join(cmd)} failed:\n{result.stderr or result.stdout}")
    return result.stdout


def query(soql, target_org):
    out = sf(["data", "query", "-q", soql, "--json"], target_org)
    return json.loads(out)["result"]["records"]


def rest(path, body, target_org, method="POST"):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump(body, fh)
        name = fh.name
    out = sf(
        ["api", "request", "rest", f"/services/data/{API}{path}", "--method", method, "--body", f"@{name}"],
        target_org,
    )
    return json.loads(out) if out.strip() else {}


def create(sobject, values, target_org):
    out = sf(["data", "create", "record", "-s", sobject, "-v", values, "--json"], target_org)
    return json.loads(out)["result"]["id"]


def ensure_michael(target_org):
    rows = query(
        f"SELECT Id, Name FROM Account WHERE Name = '{DEFAULT_ACCOUNT}' LIMIT 1",
        target_org,
    )
    if rows:
        return rows[0]["Id"]
    return create(
        "Account",
        "Name='Michael Reyes' BillingStreet='316 Ridgewood Dr' BillingCity='Bloomingdale' "
        "BillingState=IL BillingPostalCode=60108 BillingCountry='United States' "
        "ShippingStreet='316 Ridgewood Dr' ShippingCity='Bloomingdale' ShippingState=IL "
        "ShippingPostalCode=60108 ShippingCountry='United States'",
        target_org,
    )


def ensure_contact(account_id, target_org):
    rows = query(
        f"SELECT Id FROM Contact WHERE AccountId = '{account_id}' ORDER BY CreatedDate LIMIT 1",
        target_org,
    )
    if rows:
        return rows[0]["Id"]
    return create(
        "Contact",
        f"AccountId={account_id} FirstName=Michael LastName=Reyes Email=michael.reyes@example.com",
        target_org,
    )


def zone_multiplier(postal_code, target_org):
    rows = query(
        "SELECT Zone_Code__c, Zone_Multiplier__c, Postal_Code_Prefix__c FROM RLM_RTK_Service_Zone__c "
        f"WHERE Postal_Code_Prefix__c = '{postal_code}' OR Postal_Code_Prefix__c = '{postal_code[:3]}' "
        "ORDER BY Postal_Code_Prefix__c DESC LIMIT 1",
        target_org,
    )
    if not rows:
        return 1.0, "Suburb"
    return float(rows[0]["Zone_Multiplier__c"]), rows[0]["Zone_Code__c"]


def price_entry(sku, target_org):
    rows = query(
        "SELECT Id, UnitPrice, Product2Id, Pricebook2Id, ProductSellingModel.SellingModelType "
        f"FROM PricebookEntry WHERE Product2.StockKeepingUnit = '{sku}' AND Pricebook2.IsStandard = true "
        "AND CurrencyIsoCode = 'USD' AND IsActive = true LIMIT 1",
        target_org,
    )
    if not rows:
        sys.exit(f"No active USD standard PricebookEntry for {sku} (run setup_rtk_revenue)")
    return rows[0]


def wait_for(fn, timeout, interval=10):
    deadline = time.time() + timeout
    while time.time() < deadline:
        value = fn()
        if value:
            return value
        time.sleep(interval)
    return None


def place_quote(account_id, contact_id, plan_sku, include_mosquito, include_termite, severity, sqft, target_org):
    account = query(
        "SELECT Name, ShippingStreet, ShippingCity, ShippingState, ShippingPostalCode, ShippingCountry, "
        "BillingStreet, BillingCity, BillingState, BillingPostalCode, BillingCountry "
        f"FROM Account WHERE Id = '{account_id}'",
        target_org,
    )[0]
    mult, zone = zone_multiplier(account["ShippingPostalCode"] or "60108", target_org)
    uplift = 0
    if severity == "Moderate":
        uplift += 10
    elif severity == "Heavy":
        uplift += 25
    if sqft == "2000to3500":
        uplift += 10
    elif sqft == "Over3500":
        uplift += 20

    today = datetime.date.today()
    start = today.isoformat()
    opp_id = create(
        "Opportunity",
        f"Name='{account['Name']} - Home Protection' AccountId={account_id} "
        f"StageName=Qualification CloseDate={(today + datetime.timedelta(days=14)).isoformat()}",
        target_org,
    )

    skus = [plan_sku, INITIAL_SKU]
    if include_mosquito:
        skus.append(MOSQUITO_SKU)
    if include_termite:
        skus.append(TERMITE_SKU)
    entries = {sku: price_entry(sku, target_org) for sku in skus}

    records = [
        {
            "referenceId": "refQuote",
            "record": {
                "attributes": {"type": "Quote", "method": "POST"},
                "Name": f"{account['Name']} Residential Pest",
                "OpportunityId": opp_id,
                "Pricebook2Id": entries[plan_sku]["Pricebook2Id"],
                "RLM_Line_of_Business__c": "Residential Pest",
                "ShippingStreet": account.get("ShippingStreet"),
                "ShippingCity": account.get("ShippingCity"),
                "ShippingState": account.get("ShippingState"),
                "ShippingPostalCode": account.get("ShippingPostalCode"),
                "ShippingCountry": account.get("ShippingCountry"),
                "BillingStreet": account.get("BillingStreet"),
                "BillingCity": account.get("BillingCity"),
                "BillingState": account.get("BillingState"),
                "BillingPostalCode": account.get("BillingPostalCode"),
                "BillingCountry": account.get("BillingCountry"),
            },
        }
    ]
    for i, sku in enumerate(skus, start=1):
        pbe = entries[sku]
        unit = round(float(pbe["UnitPrice"]) * mult, 2)
        if sku == plan_sku:
            unit = round(unit + uplift, 2)
        line = {
            "attributes": {"type": "QuoteLineItem", "method": "POST"},
            "QuoteId": "@{refQuote.id}",
            "Product2Id": pbe["Product2Id"],
            "PricebookEntryId": pbe["Id"],
            "Quantity": 1,
            "UnitPrice": unit,
            "StartDate": start,
        }
        selling = (pbe.get("ProductSellingModel") or {}).get("SellingModelType")
        if selling == "Evergreen":
            line["PeriodBoundary"] = "Anniversary"
            line["BillingFrequency"] = "Monthly"
        records.append({"referenceId": f"refLine{i}", "record": line})

    body = {
        "pricingPref": "System",
        "catalogRatesPref": "Skip",
        "taxPref": "Skip",
        "graph": {"graphId": "pestDemoQuote", "records": records},
    }
    # New PricebookEntries are invisible to Place Sales Transaction until
    # Price_Book_Entry_Decision_Table_v2 finishes refreshing (often 2–5 minutes).
    place = {}
    for attempt in range(12):
        place = rest("/connect/rev/sales-transaction/actions/place", body, target_org)
        if place.get("isSuccess"):
            break
        err = ((place.get("errorResponse") or [{}])[0] or {}).get("message", "")
        print(f"PST attempt {attempt + 1}/12: {err or place}")
        time.sleep(20 if "Could not find product" in err else 10)
    quote_id = place.get("salesTransactionId")
    if not place.get("isSuccess") or not quote_id:
        sys.exit(
            f"Place Sales Transaction failed (refresh pricing decision tables and retry): "
            f"{json.dumps(place, indent=2)}"
        )
    print(f"Quote placed: {quote_id} (zone={zone} x{mult})")
    return quote_id, opp_id, zone, mult


def activate_order(quote_id, contact_id, target_org, timeout):
    convert = rest("/actions/standard/createOrdersFromQuote", {"inputs": [{"quoteId": quote_id}]}, target_org)
    if not convert or not convert[0].get("isSuccess"):
        sys.exit(f"createOrdersFromQuote failed: {json.dumps(convert, indent=2)}")
    order = wait_for(
        lambda: query(f"SELECT Id, OrderNumber FROM Order WHERE QuoteId = '{quote_id}' LIMIT 1", target_org),
        timeout,
    )
    if not order:
        sys.exit(f"No Order created from {quote_id}")
    order_id = order[0]["Id"]
    if contact_id:
        sf(
            ["data", "update", "record", "-s", "Order", "-i", order_id, "-v", f"BillToContactId={contact_id}"],
            target_org,
        )
    rlm_usage = wait_for(
        lambda: query(
            f"SELECT Id FROM AppUsageAssignment WHERE RecordId = '{order_id}' "
            "AND AppUsageType = 'RevenueLifecycleManagement' LIMIT 1",
            target_org,
        ),
        timeout,
        interval=5,
    )
    if not rlm_usage:
        sys.exit(f"Order {order_id} has no RLM usage assignment")
    sf(["data", "update", "record", "-s", "Order", "-i", order_id, "-v", "Status=Activated"], target_org)
    print(f"Order {order[0]['OrderNumber']} activated: {order_id}")
    return order_id, order[0]["OrderNumber"]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--target-org", required=True)
    parser.add_argument("--plan-sku", default=DEFAULT_PLAN)
    parser.add_argument("--no-mosquito", action="store_true")
    parser.add_argument("--with-termite", action="store_true")
    parser.add_argument("--severity", default="Moderate", choices=["Light", "Moderate", "Heavy"])
    parser.add_argument("--sqft", default="Under2000", choices=["Under2000", "2000to3500", "Over3500"])
    parser.add_argument("--activate", action="store_true")
    parser.add_argument("--complete-initial", action="store_true")
    parser.add_argument("--timeout", type=int, default=240)
    args = parser.parse_args()
    org = args.target_org

    account_id = ensure_michael(org)
    contact_id = ensure_contact(account_id, org)
    print(f"Account {DEFAULT_ACCOUNT}: {account_id}")

    quote_id, opp_id, zone, mult = place_quote(
        account_id,
        contact_id,
        args.plan_sku,
        not args.no_mosquito,
        args.with_termite,
        args.severity,
        args.sqft,
        org,
    )
    print(f"Opportunity: {opp_id}")

    if not args.activate:
        print("Pass --activate to convert and activate the order")
        return

    order_id, order_number = activate_order(quote_id, contact_id, org, args.timeout)
    plan = wait_for(
        lambda: query(f"SELECT Id FROM FulfillmentPlan WHERE SourceIdentifier = '{order_id}' LIMIT 1", org),
        args.timeout,
        interval=15,
    )
    if not plan:
        rest("/actions/standard/submitOrder", {"inputs": [{"orderId": order_id}]}, org)
        plan = wait_for(
            lambda: query(f"SELECT Id FROM FulfillmentPlan WHERE SourceIdentifier = '{order_id}' LIMIT 1", org),
            args.timeout,
            interval=15,
        )
    if not plan:
        print("No FulfillmentPlan yet; DRO may still be processing")
        return
    print(f"FulfillmentPlan: {plan[0]['Id']}")

    if not args.complete_initial:
        return

    wo = wait_for(
        lambda: query(
            "SELECT Id, WorkOrderNumber, Status FROM WorkOrder "
            f"WHERE RLM_Order__c = '{order_id}' LIMIT 1",
            org,
        ),
        args.timeout,
    )
    if not wo:
        # AutoTask may create WO; otherwise leave for demo narration
        print("No Work Order yet; complete Create Initial Treatment Work Order step if needed")
        return
    print(f"Work Order {wo[0]['WorkOrderNumber']}: {wo[0]['Id']}")
    if wo[0]["Status"] != "Completed":
        sf(
            ["data", "update", "record", "-s", "WorkOrder", "-i", wo[0]["Id"], "-v", "Status='In Progress'"],
            org,
        )
        sf(
            ["data", "update", "record", "-s", "WorkOrder", "-i", wo[0]["Id"], "-v", "Status=Completed"],
            org,
        )
        print("Initial treatment Work Order completed (starts milestone billing)")


if __name__ == "__main__":
    main()
