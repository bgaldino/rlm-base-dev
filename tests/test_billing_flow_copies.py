#!/usr/bin/env python3
"""
The Invoice "Apply Payment" flows ship in three bundles that can each be deployed on their own
(post_billing, post_payments, post_collections), so each carries its own copy. Whichever bundle
deploys last wins, so a fix made in one copy and not the others silently reverts. This fails
when the copies drift.

    python tests/test_billing_flow_copies.py

Stdlib only.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BUNDLES = ("post_billing", "post_payments", "post_collections")
FLOWS = ("RLM_Apply_Payments_on_Invoice", "RLM_Apply_Payment_To_Invoice_Lines")

failures = []
for flow in FLOWS:
    paths = [REPO / "unpackaged" / b / "flows" / f"{flow}.flow-meta.xml" for b in BUNDLES]
    missing = [str(p.relative_to(REPO)) for p in paths if not p.is_file()]
    if missing:
        failures.append(f"{flow}: missing {', '.join(missing)}")
        continue
    texts = {p: p.read_bytes() for p in paths}
    reference = texts[paths[0]]
    drifted = [str(p.relative_to(REPO)) for p in paths[1:] if texts[p] != reference]
    if drifted:
        failures.append(f"{flow}: differs from unpackaged/post_billing/flows/: {', '.join(drifted)}")
    print(f"  {'FAIL' if missing or drifted else 'PASS'}  {flow} is identical in {', '.join(BUNDLES)}")

if failures:
    print("\n".join(failures))
    print("Edit the post_billing copy, then copy it to the other bundles.")
    sys.exit(1)
print("All checks passed.")
