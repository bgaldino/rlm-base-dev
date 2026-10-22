#!/usr/bin/env python3
"""Capture Rentokil pest story screenshots (scenes 1-9) into a screenshots folder.

Requires Playwright and an authenticated sf org. Env:
  FSL_ORG   sf CLI alias (default fsl-rc)
  OUT_DIR   output directory (default ./screenshots/pest)
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ORG = os.environ.get("FSL_ORG", "fsl-rc")
OUT = Path(os.environ.get("OUT_DIR", "screenshots/pest"))


def sf_json(args):
    result = subprocess.run(["sf", *args, "--target-org", ORG, "--json"], capture_output=True, text=True)
    return json.loads(result.stdout)


def query(soql):
    return sf_json(["data", "query", "-q", soql])["result"]["records"]


def org_url():
    info = sf_json(["org", "display"])["result"]
    return info["instanceUrl"].rstrip("/"), info.get("accessToken")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    instance, _ = org_url()
    accounts = query("SELECT Id FROM Account WHERE Name = 'Michael Reyes' LIMIT 1")
    records = {"accountId": accounts[0]["Id"] if accounts else None, "instance": instance}
    quotes = query(
        "SELECT Id, QuoteNumber FROM Quote WHERE Account.Name = 'Michael Reyes' "
        "ORDER BY CreatedDate DESC LIMIT 1"
    )
    if quotes:
        records["quoteId"] = quotes[0]["Id"]
        records["quoteNumber"] = quotes[0].get("QuoteNumber")
    orders = query(
        "SELECT Id, OrderNumber FROM Order WHERE Account.Name = 'Michael Reyes' "
        "ORDER BY CreatedDate DESC LIMIT 1"
    )
    if orders:
        records["orderId"] = orders[0]["Id"]
        records["orderNumber"] = orders[0].get("OrderNumber")
    wos = query(
        "SELECT Id, WorkOrderNumber, Status FROM WorkOrder WHERE Account.Name = 'Michael Reyes' "
        "ORDER BY CreatedDate DESC LIMIT 5"
    )
    records["workOrders"] = wos
    (OUT / "story-records.json").write_text(json.dumps(records, indent=2) + "\n")
    print(json.dumps(records, indent=2))
    print(f"Wrote {OUT / 'story-records.json'}")
    print("Open Lightning pages in a browser and save PNGs as s1-01.png … s9-03.png under", OUT)


if __name__ == "__main__":
    main()
