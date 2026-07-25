#!/usr/bin/env python3
"""Inspect and drive the QuantumBit usage-rating pipeline in a live org.

Three subcommands, matching the three questions you actually ask when a usage
demo misbehaves:

    audit        is the DESIGN-TIME data right?      (products, policies, rates)
    report       what did the RUNTIME actually do?   (buckets, drawdown, rating)
    orchestrate  drive rating to completion          (loop until journals settle)

Auth is delegated to the sf CLI -- pass an sf alias or username with --org. No
access token is handled here.

    python scripts/qb_usage.py audit --org rlm-base__pr308
    python scripts/qb_usage.py report --org rlm-base__pr308 --accounts "Robot Resellers"
    python scripts/qb_usage.py orchestrate --org rlm-base__pr308

The companion Apex lives in scripts/apex/:
    consumeUsageProfile.apex  record usage        (run BEFORE orchestrating)
    validateRatedUsage.apex   assert the results  (run AFTER)
    clearUsageData.apex       drain the graph     (run before an account reset)

ORDER MATTERS AND IS NOT RECOVERABLE. A UsageSummary that has reached
RatableSummaryComplete never reopens, and the first orchestration pass on an
account closes every past period empty -- so record usage BEFORE orchestrating
that period, and book it into a PAST period, because drawdown and final rating
only settle once a period completes. See
datasets/sfdmu/qb/en-US/qb-rating/README.md.

Exit codes (orchestrate):
    0  every journal was processed
    1  journals still pending after the requested number of passes
    2  orchestration stalled with journals still pending -- usually stranded
       behind a period that closed before the usage was recorded
A failed Apex run raises ApexRunError rather than being reported as success.
"""
import argparse
import json
import os
import subprocess
import tempfile
import sys
import time
from collections import defaultdict

CURRENCIES = {"USD", "GBP", "EUR", "AUD", "CAD", "CHF", "JPY"}
BILLING_PERIOD = "Monthly"
PERIOD_RANK = {"Daily": 1, "Weekly": 2, "Monthly": 3, "Quarterly": 4, "Yearly": 5}

QB_USAGE_SKUS = [
    "QB-DB", "QB-DB-TOKEN", "QB-CMT-TKN-FLAT", "QB-CMT-TKN-BND",
    "QB-CMT-TKN-EACH", "QB-CMT-TKN-TIER", "QB-QTY-CMT", "QB-MTY-CMT",
    "QB-TOKENS-PACK", "QB-DAT-THPT",
]

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ----------------------------------------------------------------------
# sf CLI plumbing
# ----------------------------------------------------------------------
def sf_query(org, soql):
    """Run SOQL and return records, or [] with a message on failure."""
    proc = subprocess.run(
        ["sf", "data", "query", "-q", soql, "--target-org", org, "--json"],
        capture_output=True, text=True,
        # Scratch orgs need this with CCI 4.10 + newer sf CLI, else INVALID_AUTH_HEADER.
        env={**os.environ, "SF_TEMP_SHOW_SECRETS": "true"})
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        print(f"  query failed: {soql[:70]}\n    {(proc.stderr or proc.stdout)[:200]}")
        return []
    if "result" not in data:
        print(f"  query failed: {soql[:70]}\n    {str(data.get('message'))[:200]}")
        return []
    return data["result"]["records"]


class ApexRunError(RuntimeError):
    """Anonymous Apex failed to compile or threw. Raised so a failed orchestration
    pass can never be mistaken for a successful one."""


def sf_apex(org, path):
    proc = subprocess.run(
        ["sf", "apex", "run", "--file", path, "--target-org", org],
        capture_output=True, text=True,
        env={**os.environ, "SF_TEMP_SHOW_SECRETS": "true"})
    blob = proc.stdout + proc.stderr
    # Check BOTH signals. `sf apex run` can exit non-zero on a compile failure, and
    # can also exit zero while the anonymous block threw -- in which case the log
    # carries the failure instead. Silently returning [] on either makes a broken
    # orchestration pass look like a clean one.
    failed = proc.returncode != 0 or "EXECUTION_FAILED" in blob or (
        "Error (execute" in blob)
    if failed:
        detail = "\n".join(
            l for l in blob.splitlines()
            if "Error" in l or "EXCEPTION_THROWN" in l or "FATAL_ERROR" in l
        )[:2000]
        raise ApexRunError(
            f"apex run failed for {path} (exit {proc.returncode}):\n"
            f"{detail or blob[-2000:]}")
    # A log line is ...|USER_DEBUG|[1]|DEBUG|MESSAGE -- split from the RIGHT, because
    # "USER_DEBUG|" itself contains "DEBUG|" and a left split returns the wrong half.
    return [l.rsplit("|DEBUG|", 1)[-1].strip()
            for l in blob.splitlines()
            if "USER_DEBUG" in l and "|DEBUG|" in l]


def nested(record, *path):
    """Walk a SOQL relationship path, tolerating nulls at any level."""
    cur = record
    for key in path:
        if cur is None:
            return None
        cur = cur.get(key)
    return cur


# ----------------------------------------------------------------------
# audit -- design time
# ----------------------------------------------------------------------
def cmd_audit(args):
    org = args.org
    products = sf_query(org, "SELECT StockKeepingUnit, Name, UsageModelType FROM Product2 "
                             "WHERE UsageModelType != null ORDER BY StockKeepingUnit")
    if not products:
        print("No usage products found — is qb-rating loaded?")
        return 1

    pur_active, pur_draft = defaultdict(set), defaultdict(set)
    for r in sf_query(org, "SELECT Product.StockKeepingUnit, UsageResource.Code, Status "
                           "FROM ProductUsageResource"):
        sku = nested(r, "Product", "StockKeepingUnit")
        code = nested(r, "UsageResource", "Code")
        (pur_active if r["Status"] == "Active" else pur_draft)[sku].add(code)

    purp_by = defaultdict(list)
    for r in sf_query(org,
            "SELECT ProductUsageResource.Product.StockKeepingUnit, "
            "ProductUsageResource.UsageResource.Code, ProductUsageResource.Status, "
            "RatingFrequencyPolicy.RatingPeriod, UsageAggregationPolicy.Code, "
            "UsageAggregationPolicy.UsageAccumulationPeriod, "
            "UsageCommitmentPolicy.Name, UsageOveragePolicy.Name "
            "FROM ProductUsageResourcePolicy"):
        purp_by[nested(r, "ProductUsageResource", "Product", "StockKeepingUnit")].append({
            "res": nested(r, "ProductUsageResource", "UsageResource", "Code"),
            "purStatus": nested(r, "ProductUsageResource", "Status"),
            "rating": nested(r, "RatingFrequencyPolicy", "RatingPeriod"),
            "accumCode": nested(r, "UsageAggregationPolicy", "Code"),
            "accum": nested(r, "UsageAggregationPolicy", "UsageAccumulationPeriod"),
            "commit": nested(r, "UsageCommitmentPolicy", "Name"),
            "overage": nested(r, "UsageOveragePolicy", "Name"),
        })

    grant_by = defaultdict(list)
    for r in sf_query(org, "SELECT Product.StockKeepingUnit, UsageRsrc.Code, Status, Quantity "
                           "FROM ProductUsageGrant"):
        grant_by[nested(r, "Product", "StockKeepingUnit")].append(
            f"{nested(r, 'UsageRsrc', 'Code')}={r['Quantity']:g}({r['Status']})")

    rce_by = defaultdict(lambda: defaultdict(set))
    rce_ids = defaultdict(list)
    for r in sf_query(org, "SELECT Id, Product.StockKeepingUnit, UsageResource.Code, "
                           "RateCard.Name, RateCard.Type, RateUnitOfMeasure.UnitCode, Status "
                           "FROM RateCardEntry"):
        if r["Status"] != "Active":
            continue
        sku = nested(r, "Product", "StockKeepingUnit")
        key = (nested(r, "RateCard", "Name"), nested(r, "RateCard", "Type"),
               nested(r, "UsageResource", "Code"))
        rce_by[sku][key].add(nested(r, "RateUnitOfMeasure", "UnitCode"))
        rce_ids[sku].append((key, r["Id"]))

    tiered = {r["RateCardEntryId"] for r in sf_query(
        org, "SELECT RateCardEntryId FROM RateAdjustmentByTier WHERE RateCardEntryId != null")}

    print("=" * 96)
    print("QUANTUMBIT USAGE — DESIGN-TIME AUDIT")
    print("=" * 96)

    total = 0
    for p in products:
        sku = p["StockKeepingUnit"]
        print(f"\n{sku}  [{p['UsageModelType']}]  {p['Name']}")
        issues = []

        active, draft = sorted(pur_active.get(sku, [])), sorted(pur_draft.get(sku, []))
        print(f"  resources (Active) : {', '.join(active) if active else 'NONE'}")
        if draft:
            print(f"  resources (Draft)  : {', '.join(draft)}   <- duplicate/unactivated")
        if not active:
            issues.append("no Active ProductUsageResource")

        seen = set()
        for row in sorted(purp_by.get(sku, []), key=lambda x: str(x["res"])):
            if row["purStatus"] != "Active":
                continue
            seen.add(row["res"])
            bits = []
            if row["rating"] or row["accum"]:
                bits.append(f"rating={row['rating']} accum={row['accum']}({row['accumCode']})")
                if row["rating"] and row["accum"]:
                    ok = (PERIOD_RANK[BILLING_PERIOD] >= PERIOD_RANK.get(row["rating"], 0)
                          > PERIOD_RANK.get(row["accum"], 0))
                    if not ok:
                        issues.append(f"{row['res']}: period order billing={BILLING_PERIOD} "
                                      f"rating={row['rating']} accum={row['accum']} "
                                      f"— Create Empty Summaries will reject this")
                elif row["rating"]:
                    issues.append(f"{row['res']}: rating set but no accumulation policy")
            if row["commit"]:
                bits.append(f"commit={row['commit']}")
            if row["overage"]:
                bits.append(f"overage={row['overage']}")
            print(f"  policy {str(row['res']):<20} {' | '.join(bits) or '(no policies)'}")

            # The platform rejects both period fields on a commitment product.
            if p["UsageModelType"] in ("Commit", "CommitmentQuantity", "CommitmentSpend"):
                if row["rating"] or row["accum"]:
                    issues.append(f"{row['res']}: commitment products must carry ONLY a "
                                  f"commitment policy (rating/accumulation are rejected)")

        unpolicied = [r for r in active if r not in seen]
        if unpolicied:
            print(f"  no policy for      : {', '.join(unpolicied)}")
        if grant_by.get(sku):
            print(f"  grants             : {', '.join(sorted(grant_by[sku]))}")

        if rce_by.get(sku):
            for (card, ctype, res), ccys in sorted(rce_by[sku].items(), key=lambda x: str(x[0])):
                missing, token = CURRENCIES - ccys, ccys - CURRENCIES
                label = f"{card}/{res}"
                if token:
                    print(f"  rates {label:<34} token-denominated ({', '.join(sorted(token))})")
                else:
                    flag = f"  MISSING {','.join(sorted(missing))}" if missing else ""
                    print(f"  rates {label:<34} {len(ccys)} currencies{flag}")
                    if missing:
                        issues.append(f"{label}: missing {','.join(sorted(missing))}")
                if ctype == "Tier":
                    without = [i for k, i in rce_ids[sku]
                               if k == (card, ctype, res) and i not in tiered]
                    if without:
                        issues.append(f"{label}: {len(without)} Tier entry(ies) with no tier "
                                      f"adjustment — activate_rates will fail the build")
        else:
            if [r for r in active if r != "QB-TOKEN"]:
                issues.append("no Active RateCardEntry for any resource")
            else:
                print("  rates              : none (token/pack product)")

        total += len(issues)
        for i in issues:
            print(f"  ISSUE  {i}")
        if not issues:
            print("  OK")

    print("\n" + "=" * 96)
    print(f"{total} issue(s) across {len(products)} product(s)")
    return 1 if total else 0


# ----------------------------------------------------------------------
# report -- runtime
# ----------------------------------------------------------------------
def cmd_report(args):
    org = args.org
    accounts = args.accounts or [None]

    for acct in accounts:
        where_bucket = ("WHERE TransactionUsageEntitlement.Product.StockKeepingUnit IN "
                        f"({', '.join(repr(s) for s in QB_USAGE_SKUS)})")
        if acct:
            where_bucket += f" AND TransactionUsageEntitlement.Account.Name = '{acct}'"
            print(f"\n{'=' * 90}\n{acct}\n{'=' * 90}")
        else:
            print(f"\n{'=' * 90}\nALL ACCOUNTS\n{'=' * 90}")

        buckets = sf_query(org,
            "SELECT Id, ParentId, UsageResource.Code, BucketBalance, ConsumedEntitlement, "
            "TransactionUsageEntitlement.Product.StockKeepingUnit, "
            "TransactionUsageEntitlement.Account.Name, "
            "TransactionUsageEntitlement.EntitlementQuantity "
            f"FROM UsageEntitlementBucket {where_bucket}")

        # The tree is 3 levels and NO bucket has a null ParentId -- the wallet's
        # parent is a grant-binding target, the child's parent is the wallet. So a
        # child is identified by set membership, not by a null check.
        ids = {b["Id"] for b in buckets}
        if buckets:
            print("\n  buckets (child rows carry the balance)")
            print(f"    {'account':<32} {'product':<18} {'granted':>10} {'consumed':>10} "
                  f"{'balance':>10}  role")
            for b in sorted(buckets, key=lambda b: (
                    nested(b, "TransactionUsageEntitlement", "Account", "Name") or "",
                    b["ParentId"] in ids)):
                tue = b.get("TransactionUsageEntitlement") or {}
                print(f"    {(nested(tue, 'Account', 'Name') or '?'):<32} "
                      f"{(nested(tue, 'Product', 'StockKeepingUnit') or '?'):<18} "
                      f"{str(tue.get('EntitlementQuantity') or '-'):>10} "
                      f"{str(b['ConsumedEntitlement'] or 0):>10} "
                      f"{str(b['BucketBalance'] or 0):>10}  "
                      f"{'child' if b['ParentId'] in ids else 'wallet (rolled up)'}")
        else:
            print("\n  buckets: none")

        where_rated = ("WHERE Asset.Product2.StockKeepingUnit IN "
                       f"({', '.join(repr(s) for s in QB_USAGE_SKUS)})")
        if acct:
            where_rated += f" AND Account.Name = '{acct}'"
        rated = [r for r in sf_query(org,
            "SELECT Account.Name, UsageResource.Code, StartDateTime, TierQuantity, "
            "OverageQuantity, NetUnitRate, TotalAmount, Status "
            f"FROM UsageRatableSummary {where_rated}")
            if (r["TierQuantity"] or 0) > 0 or (r["TotalAmount"] or 0) > 0]

        print("\n  rated summaries")
        if rated:
            print(f"    {'account':<32} {'resource':<20} {'period':<10} {'quantity':>12} "
                  f"{'rate':>9} {'amount':>13}  status")
            for r in sorted(rated, key=lambda r: (nested(r, "Account", "Name") or "",
                                                  r["StartDateTime"] or "")):
                print(f"    {(nested(r, 'Account', 'Name') or '?'):<32} "
                      f"{(nested(r, 'UsageResource', 'Code') or '?'):<20} "
                      f"{(r['StartDateTime'] or '')[:10]:<10} "
                      f"{str(r['TierQuantity']):>12} {str(r['NetUnitRate']):>9} "
                      f"{str(r['TotalAmount']):>13}  {r['Status']}")
        else:
            print("    (none — orchestration may still be running, or the journals stranded)")

    # A stranded journal is the signature of a period that closed before the usage
    # was recorded. It never recovers, so surface it prominently.
    pending = sf_query(org, "SELECT COUNT(Id) c FROM TransactionJournal WHERE Status = 'Pending'")
    n = pending[0].get("c") if pending else 0
    if n:
        print(f"\n  ⚠ {n} TransactionJournal row(s) still Pending. If orchestration has "
              f"finished,\n    their period closed before the usage was recorded and they will "
              f"NEVER rate.")
    return 0


# ----------------------------------------------------------------------
# orchestrate
# ----------------------------------------------------------------------
START_ORCH = """
String status = RLM_UsageOrchestrationController.startOrchestration('RLM_OrchestrateUsageManagement');
System.debug('ORCH: ' + status);
"""


def cmd_orchestrate(args):
    org = args.org
    # Written to the system temp dir, NOT the repo. A scratch file inside the
    # working tree gets swept into commits by `git add -A` (it was, once), and
    # every later run then deletes a tracked file out from under the user.
    fd, tmp = tempfile.mkstemp(prefix="qb_start_orch_", suffix=".apex")
    with os.fdopen(fd, "w") as fh:
        fh.write(START_ORCH)

    def pending():
        rows = sf_query(org, "SELECT COUNT(Id) c FROM TransactionJournal WHERE Status = 'Pending'")
        return rows[0].get("c") if rows else 0

    try:
        print(f"driving orchestration on {org} "
              f"(up to {args.passes} passes, {args.interval}s apart)")
        # One pass is never enough: pass 1 seeds the empty summaries and only a later
        # pass aggregates the journals into them and rates the result.
        for p in range(1, args.passes + 1):
            before = pending()
            sf_apex(org, tmp)
            time.sleep(args.interval)
            after = pending()
            print(f"  pass {p}: pending journals {before} -> {after}")
            if after == 0:
                print("  all journals processed")
                return 0
            if after == before and p >= 3:
                # Exit 2, NOT 0. Journals still Pending means the run did not do
                # what this command promises; reporting success would let
                # automation treat a stranded orchestration as a good build.
                print(f"  no progress for a full pass and {after} journal(s) still pending "
                      "— either rating is\n  complete for every open period, or these "
                      "journals are stranded behind a period that\n  already closed "
                      "(unrecoverable: record usage BEFORE orchestrating that period).")
                return 2
        print(f"  still {pending()} pending after {args.passes} passes")
        return 1
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("audit", help="design-time audit of every usage product")
    a.add_argument("--org", required=True, help="sf CLI alias or username")
    a.set_defaults(func=cmd_audit)

    r = sub.add_parser("report", help="runtime buckets, drawdown and rated amounts")
    r.add_argument("--org", required=True)
    r.add_argument("--accounts", nargs="*", help="account names (default: all)")
    r.set_defaults(func=cmd_report)

    o = sub.add_parser("orchestrate", help="drive usage orchestration to convergence")
    o.add_argument("--org", required=True)
    o.add_argument("--passes", type=int, default=8)
    o.add_argument("--interval", type=int, default=90, help="seconds between passes")
    o.set_defaults(func=cmd_orchestrate)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
