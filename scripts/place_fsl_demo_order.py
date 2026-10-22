#!/usr/bin/env python3
"""Run the QuantumBit Quote -> Install -> Service -> Bill demo up to the
installation Work Order.

Creates an Opportunity and a Quote (hardware bundle + Installation and
Assembly + optional Gold support) through the Place Sales Transaction API,
converts the Quote to an Order, activates it and waits for DRO. With --ship
the manual "Ship Hardware" step is completed so the installation Work Order
and Service Appointment are created.

The quote path matters: orders converted from quotes carry the Revenue
Lifecycle Management AppUsageAssignment, which is what triggers asset
creation, DRO submission and billing schedules on activation. Records must
be priced by the API; DML-inserted lines fail activation with "prices aren't
currently up to date".

Usage:
    python scripts/place_fsl_demo_order.py --target-org fsl-rc --ship
    python scripts/place_fsl_demo_order.py --target-org rlm-base__beta --sku QB-BDL-RAXS --no-support
"""

import argparse
import datetime
import json
import subprocess
import sys
import tempfile
import time

API = "v66.0"
DEFAULT_ACCOUNT = "Infinitech"
INSTALL_SKU = "QB-INST-1000"
SUPPORT_SKU = "QB-SUPP-1005"
SHIP_STEP = "Ship Hardware"


def sf(args, target_org):
    cmd = ["sf", *args, "--target-org", target_org]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 and not result.stdout.strip().startswith(("{", "[")):
        raise RuntimeError(f"{' '.join(cmd)} failed:\n{result.stderr or result.stdout}")
    return result.stdout


def query(soql, target_org):
    out = sf(["data", "query", "-q", soql, "--json"], target_org)
    return json.loads(out)["result"]["records"]


def rest(path, body, target_org):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump(body, fh)
    out = sf(
        ["api", "request", "rest", f"/services/data/{API}{path}", "--method", "POST", "--body", f"@{fh.name}"],
        target_org,
    )
    return json.loads(out)


def create(sobject, values, target_org):
    out = sf(["data", "create", "record", "-s", sobject, "-v", values, "--json"], target_org)
    return json.loads(out)["result"]["id"]


def ensure_account(name, target_org):
    rows = query(f"SELECT Id FROM Account WHERE Name = '{name}' LIMIT 1", target_org)
    if rows:
        return rows[0]["Id"]
    return create(
        "Account",
        f"Name='{name}' BillingStreet='415 Mission St' BillingCity='San Francisco' BillingState=CA "
        "BillingPostalCode=94105 BillingCountry='United States' ShippingStreet='415 Mission St' "
        "ShippingCity='San Francisco' ShippingState=CA ShippingPostalCode=94105 "
        "ShippingCountry='United States'",
        target_org,
    )


def price_entry(sku, target_org):
    rows = query(
        "SELECT Id, UnitPrice, Product2Id, Pricebook2Id FROM PricebookEntry "
        f"WHERE Product2.StockKeepingUnit = '{sku}' AND Pricebook2.IsStandard = true "
        "AND CurrencyIsoCode = 'USD' AND IsActive = true LIMIT 1",
        target_org,
    )
    if not rows:
        sys.exit(f"No active USD standard PricebookEntry for {sku} (run setup_fsl_revenue)")
    return rows[0]


def wait_for(fn, timeout, interval=10):
    deadline = time.time() + timeout
    while time.time() < deadline:
        value = fn()
        if value:
            return value
        time.sleep(interval)
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--target-org", required=True, help="sf CLI alias or username")
    parser.add_argument("--sku", default="QB-BDL-R750", help="Hardware SKU with a Field Installation decomposition rule")
    parser.add_argument("--account-name", default=DEFAULT_ACCOUNT)
    parser.add_argument("--no-support", action="store_true", help=f"Leave {SUPPORT_SKU} (Gold support) off the quote")
    parser.add_argument("--ship", action="store_true", help=f"Complete the '{SHIP_STEP}' step and wait for the Work Order")
    parser.add_argument("--timeout", type=int, default=240, help="Seconds to wait for each DRO milestone")
    args = parser.parse_args()
    org = args.target_org
    today = datetime.date.today()
    start = today.isoformat()

    account_id = ensure_account(args.account_name, org)
    opp_id = create(
        "Opportunity",
        f"Name='{args.account_name} - SF Data Center Expansion {start}' AccountId={account_id} "
        f"StageName=Qualification CloseDate={(today + datetime.timedelta(days=30)).isoformat()}",
        org,
    )
    print(f"Opportunity created: {opp_id}")

    lines = [(price_entry(args.sku, org), {}), (price_entry(INSTALL_SKU, org), {})]
    if not args.no_support:
        end = (today.replace(year=today.year + 1) - datetime.timedelta(days=1)).isoformat()
        lines.append((price_entry(SUPPORT_SKU, org), {"EndDate": end, "PeriodBoundary": "Anniversary"}))

    records = [{"referenceId": "refQuote", "record": {
        "attributes": {"type": "Quote", "method": "POST"},
        "Name": f"{args.account_name} SF Expansion", "OpportunityId": opp_id,
        "Pricebook2Id": lines[0][0]["Pricebook2Id"]}}]
    for i, (pbe, extra) in enumerate(lines, start=1):
        records.append({"referenceId": f"refLine{i}", "record": {
            "attributes": {"type": "QuoteLineItem", "method": "POST"},
            "QuoteId": "@{refQuote.id}", "Product2Id": pbe["Product2Id"], "PricebookEntryId": pbe["Id"],
            "Quantity": 1, "UnitPrice": pbe["UnitPrice"], "StartDate": start, **extra}})

    body = {"pricingPref": "System", "catalogRatesPref": "Skip", "taxPref": "Skip",
            "graph": {"graphId": "fslDemoQuote", "records": records}}
    # The pricing engine intermittently rejects the first call after idle time with INVALID_API_INPUT.
    for attempt in range(3):
        place = rest("/connect/rev/sales-transaction/actions/place", body, org)
        if place.get("isSuccess"):
            break
        time.sleep(10)
    quote_id = place.get("salesTransactionId")
    if not place.get("isSuccess") or not quote_id:
        sys.exit(f"Place Sales Transaction failed: {json.dumps(place, indent=2)}")
    print(f"Quote placed: {quote_id}")

    convert = rest("/actions/standard/createOrdersFromQuote", {"inputs": [{"quoteId": quote_id}]}, org)
    if not convert or not convert[0].get("isSuccess"):
        sys.exit(f"createOrdersFromQuote failed: {json.dumps(convert, indent=2)}")
    order = wait_for(lambda: query(f"SELECT Id, OrderNumber FROM Order WHERE QuoteId = '{quote_id}' LIMIT 1", org),
                     args.timeout)
    if not order:
        sys.exit(f"No Order created from {quote_id} within {args.timeout}s")
    order_id = order[0]["Id"]
    print(f"Order {order[0]['OrderNumber']} created: {order_id}")

    # The activation flow only assetizes and submits orders that already carry the RLM
    # AppUsageAssignment, which quote conversion adds asynchronously.
    rlm_usage = wait_for(
        lambda: query(
            f"SELECT Id FROM AppUsageAssignment WHERE RecordId = '{order_id}' "
            "AND AppUsageType = 'RevenueLifecycleManagement' LIMIT 1", org),
        args.timeout, interval=5,
    )
    if not rlm_usage:
        sys.exit(f"Order {order_id} has no Revenue Lifecycle Management usage assignment")

    sf(["data", "update", "record", "-s", "Order", "-i", order_id, "-v", "Status=Activated"], org)
    print("Order activated")

    plan_soql = f"SELECT Id FROM FulfillmentPlan WHERE SourceIdentifier = '{order_id}' LIMIT 1"
    activated_at = time.time()

    def submitted():
        if query(plan_soql, org):
            return True
        if time.time() - activated_at > 90:
            rest("/actions/standard/submitOrder", {"inputs": [{"orderId": order_id}]}, org)
        return bool(query(plan_soql, org))

    if not wait_for(submitted, args.timeout, interval=15):
        sys.exit(f"No FulfillmentPlan created for {order_id} within {args.timeout}s")
    assets = wait_for(
        lambda: query(
            "SELECT Id FROM AssetActionSource WHERE ReferenceEntityItemId IN "
            f"(SELECT Id FROM OrderItem WHERE OrderId = '{order_id}') LIMIT 1", org),
        args.timeout,
    )
    if not assets:
        sys.exit(f"No assets created for {order_id} within {args.timeout}s")
    print("Submitted to DRO and assets created")

    if not args.ship:
        print(f"Complete the '{SHIP_STEP}' step in the fulfillment plan to create the installation Work Order")
        return

    plan_id = query(plan_soql, org)[0]["Id"]
    ship = wait_for(
        lambda: query(
            f"SELECT Id FROM FulfillmentStep WHERE FulfillmentPlanId = '{plan_id}' "
            f"AND Name = '{SHIP_STEP}' AND State = 'InProgress' LIMIT 1", org),
        args.timeout,
    )
    if not ship:
        sys.exit(f"'{SHIP_STEP}' step did not start within {args.timeout}s")
    sf(["data", "update", "record", "-s", "FulfillmentStep", "-i", ship[0]["Id"], "-v", "State=Completed"], org)
    print("Hardware shipped")

    work_order = wait_for(
        lambda: query(
            "SELECT Id, WorkOrderNumber, Status, Asset.Name FROM WorkOrder "
            f"WHERE RLM_Order__c = '{order_id}' LIMIT 1", org),
        args.timeout,
    )
    if not work_order:
        sys.exit(f"No Work Order created for {order_id} within {args.timeout}s")
    wo = work_order[0]
    asset = (wo.get("Asset") or {}).get("Name", "no asset")
    print(f"Work Order {wo['WorkOrderNumber']} ({wo['Id']}) created for {asset}, status {wo['Status']}")


if __name__ == "__main__":
    main()
