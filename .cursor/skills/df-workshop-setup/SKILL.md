# DF Hands-On Workshop Setup — capture, replay & template org drift

Use this skill to make a fresh Revenue Cloud clone **workshop-ready** for a DF
Hands-On lab: capture the workshop-specific "drift" (seeded quotes, ramps,
anchors + config toggles) from a working org and replay it into a clone, then
verify and hand the clone off to be templated (TrialForce/OrgFarm). The toolkit
lives in `scripts/df_workshop/`; its detailed script/dataset reference is
`scripts/df_workshop/README.md` — read it for the file-level schema.

This skill teaches the **mechanism** (capture → replay → verify-by-query →
template). The specific quote/opp/account names below are the **DF26 (Sept 2026)
recorded state**, a worked example; rediscover the current set from the canvas +
exercise guide for any other release (see **Discovery**).

## Quick Rules

1. **The drift has three buckets.** A = platform provisioning (Data Cloud,
   Einstein/Agentforce) — NOT handled by scripts, enabled by the attendee
   post-clone. B = config toggles: the perm-set assign is scriptable + idempotent;
   the DISTI pricing-procedure state is *detected* (an active version fails with
   manual deactivation instructions, not auto-deactivated). C = transactional data
   (quotes/ramps/anchors) — the extract/replay core.
2. **Quotes are replayed, never DML'd.** Re-create each quote through Place Sales
   Transaction (`POST /connect/rev/sales-transaction/actions/place`) so the
   platform generates and prices line items, attributes, and ramp segments.
   Direct `QuoteLineItem` DML is rejected/inconsistent for TermDefined products.
3. **Build ramps the platform way.** Place the primary (Year-1) segment, then
   **Create Ramp Deal**
   (`POST /connect/revenue-management/sales-transaction-contexts/{lineId}/actions/ramp-deal-create`,
   `subscriptionTerm = 12×N` MONTHS, `segmentType=YEARLY`), then place-with-context
   to reprice later segments. The platform mints fresh `RampIdentifier`s — never
   copy the source org's opaque tokens.
4. **Capture seeded records the quotes don't reference.** The extractor is
   quote-driven; scenario opps/accounts with no quote link are captured via
   `--seed-opps` / `--seed-accounts`. Exclude randomly-generated bulk data
   (e.g. `CustomerX - $NNK #NN` PRM pipeline) — the canvas wants "specific data …
   not randomly created", small counts.
5. **Verify by query — never enable features to test the template org.** See
   **DO NOT**. Confirm bucket-C economics + bucket-B state with SOQL; run live
   Coworker/Data-Cloud exercises only on a **separate disposable clone**.
6. **Everything ships through a feature branch + PR.** Never commit to `264` /
   `main` / `release/*`. Credentials from the Slack canvas are never committed.

## DO NOT

- **DO NOT provision Data Cloud on the org you intend to TrialForce/template.**
  Provisioning Data Cloud breaks TrialForce snapshot creation. The TSO must be
  captured with Data Cloud **off**; the attendee enables it post-clone. As a
  consequence, **do not enable features to smoke-test the template org** — that
  ruins the TSO. Any live end-to-end validation happens on a throwaway clone.
- **DO NOT** deploy the `DocAI_CreateQuote` flow / "DocAI Package" (apex
  `de_DataCloudIDPFlowAction` etc., `NavigateToRecord` aura,
  `AddQuoteLineItemRequest__e`). It is **not** referenced by the exercise guide —
  leftover build drift. (Evidence + rationale in `scripts/df_workshop/README.md`.)
- **DO NOT** copy source-org `RampIdentifier` / `SegmentIdentifier` tokens or DML
  ramp segment rows — build ramps via Create Ramp Deal (Quick Rule 3).
- **DO NOT** change SFDMU/DML `Upsert` to `Insert` + `deleteOldData` — not
  applicable here anyway (replay, not SFDMU), but the repo-wide rule stands.
- **DO NOT** commit the credentials or org URLs from the canvas (`F0BU8CSKNU8`).

## Entry Conditions

| Situation | Use this skill? |
|-----------|-----------------|
| Prep a clone as a DF Hands-On workshop org (seed quotes/anchors + toggles) | Yes |
| Capture new workshop drift from the working org into the replay spec | Yes |
| Confirm a clone is complete before it is templated (TrialForce/OrgFarm) | Yes — the verify-by-query audit |
| Generic SFDMU data plan (not the workshop) | No → `sfdmu-data-plans/SKILL.md` |
| Ramp-quote demo outside the workshop | No → ramp-demo-kit (artifacts) / `usage-consumption` |
| Add/CRUD a pricing Expression Set (e.g. deactivate a procedure) | Use `expression-sets/SKILL.md` for the mechanism; this skill only decides *whether* to |

## Discovery — find the current release's drift set

The seeded set is defined by two sources, not by this file:

1. **The Slack canvas** ("DF Hands On Working/Dev Org", `F0BU8CSKNU8`) — names the
   quotes, the objects to copy, and the config toggles; states record counts are
   "very small" and "not randomly created".
2. **The exercise guide** (`DF … Hands-On Workshop Exercise Guide … .md`) — the
   authoritative signal for which opportunities/accounts are *used*. Grep it:
   ```bash
   rg -in "opportunit|new quote|create a quote" "<exercise-guide>.md"
   ```
   Opportunities the guide references by literal name but that hang off no
   captured quote are `--seed-opps`; accounts whose opp is created *live* in the
   exercise are `--seed-accounts`.

Inspect the working org for candidate quotes/opps and their economics with
`sf data query` before deciding scope. Treat any bulk, patterned, auto-generated
records as excluded.

## Workflow

### 1. Extract (read-only, from the working org)
```bash
python scripts/df_workshop/extract_workshop_quotes.py --org <working-org>
  # --quotes "A,B,C"        override the quote names
  # --seed-opps "X,Y"       opps to capture even if no quote references them
  # --seed-accounts "Z"     accounts to capture even if no opp references them
```
Writes `datasets/df_workshop/workshop_quotes.json` (portable spec: every Id
resolved to a natural key). Commit the spec.

### 2. Replay (into the clone)
```bash
python scripts/df_workshop/insert_workshop_quotes.py --org <clone> \
  [--apply-config] [--replace] [--dry-run] [--skip-quotes] [--quote "<name>"]
```
- Upserts anchors by Name (idempotent), resolves each SKU/selling-model to the
  clone's own PricebookEntry, replays quotes via Place (ramps via Create Ramp
  Deal), and replays configured `QuoteLineItemAttribute`s.
- `--apply-config` applies bucket B: assign the Coworker-admin perm set. It does
  **not** auto-deactivate the DISTI pricing procedure — it *detects* an active
  version and **fails** with manual `scripts/expression_sets/` deactivation
  instructions (deactivate, don't delete), so a partial setup is never certified.

### 3. Verify by query (the template gate)
Confirm, with SOQL against the clone (see **Validation Checks**): each quote's
line count / `CalculationStatus` / `GrandTotal` matches source, ramp segments
carry the right qty/discount under one minted RampIdentifier, configured-attribute
count matches, all anchor accounts/contacts/opps exist with expected amounts, and
bucket-B state is correct.

### 4. Template
With bucket A (Data Cloud/Einstein) **off**, hand the clone to TrialForce/OrgFarm.
Live end-to-end validation, if wanted, runs on a **separate disposable clone**.

## Examples

**DF26 (Sept 2026) recorded state — the worked example.** Substitute your own via
**Discovery** for another release.

- Quotes: `Quote PDF` (15 lines, 6 configured attributes, GrandTotal 129,395.95);
  `3 Year Ramp - AI Licenses` (segs 4000/6000/10000 @ 15/10/10%, total 2,669,822);
  `4 Year Ramp - AI Licenses` (segs 2500/5000/7500/10000 @ 10/10/15/25%, total
  3,093,543.75).
- Anchors: accounts Global Media, Infinitech, Acme, Apex Dynamics; contact Carol
  White; opps Proposal PDF & QuantumBit Licenses (quote-linked), Starter ($29K) &
  Target ($129K) on Acme (seeded — the guide's "New Quote"/"Target Quote" steps).
- Excluded: the `CustomerX - $NNK #NN` partner pipeline (randomly generated).
- Out of scope: `DocAI_CreateQuote` / DocAI Package.
- Source working org `df26-ws`; test clone `df26-ws-test`.

## Validation Checks

Before templating (run against the clone; compare to the working org):

```bash
# quotes: lines / calc / total
sf data query --target-org <clone> -q "SELECT Name, LineItemCount, CalculationStatus, GrandTotal FROM Quote WHERE Name IN ('<q1>','<q2>','<q3>')"
# ramp segments per ramp quote
sf data query --target-org <clone> -q "SELECT SegmentName, IsPrimarySegment, Quantity, Discount, TotalPrice, RampIdentifier FROM QuoteLineItem WHERE Quote.Name='<ramp quote>' ORDER BY StartDate"
# configured attributes on the attribute-bearing quote
sf data query --target-org <clone> -q "SELECT COUNT() FROM QuoteLineItemAttribute WHERE QuoteLineItem.Quote.Name='<quote>'"
# anchors (include Pricebook2 — opps must carry their pricebook lookup for quoting/Coworker context)
sf data query --target-org <clone> -q "SELECT Name, Account.Name, Amount, StageName, Pricebook2.Name FROM Opportunity WHERE Name IN (...)"
# bucket B: perm-set assignment + no active DefaultPricing procedure that breaks orders
sf data query --target-org <clone> -q "SELECT PermissionSet.Name FROM PermissionSetAssignment WHERE PermissionSet.Name='<coworker-admin PSet>' AND Assignee.Username='<running user>'"
sf data query --target-org <clone> -q "SELECT ExpressionSet.ApiName, VersionNumber, IsActive FROM ExpressionSetVersion WHERE ExpressionSet.UsageType='DefaultPricing' AND IsActive=true"
```
(`IsActive` is on `ExpressionSetVersion`, not `ExpressionSet` — query the active
version through its `ExpressionSet` relationship.)

Also confirm the extract/insert scripts still compile
(`python -m py_compile scripts/df_workshop/*.py`), re-run the extractor idempotently
if the spec changed, and follow `doc-consistency/SKILL.md` before the PR.
