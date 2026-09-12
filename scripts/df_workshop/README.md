# DF Hands-On Workshop — org drift capture & replay

Toolkit that captures the **workshop-specific drift** on the DF working org
(`df26-ws`, TSO source `sb0-264upgrade`) and reinserts it into any fresh clone,
until the OrgFarm template process absorbs it. Source of truth is the Slack
canvas *"DF Hands On Working/Dev Org"* (`F0BU8CSKNU8`).

> **This is a stopgap.** The canvas asks for this data to live in the OrgFarm
> **template**. This toolkit exists so a clone is usable *today*; it is not the
> long-term home.

## The drift — three buckets

Stock 264 pre-release clone → workshop-ready org differs in three ways. Only
bucket C is data; A and B are org config.

### A. Platform provisioning — **attendee post-clone step, NOT handled here**
Q-Branch setup that "won't be available at DF":
- **Data Cloud**
- **Agentforce**

A data/config skill cannot provision these, and this toolkit does **not** validate
or gate on their presence — a clone either has them or it does not. Per the
exercise guide, the *attendee* enables Data Cloud + Einstein during lab setup
("Data Cloud Setup" → "Turn on Einstein", ~15 min), so this is a lab step for the
**Coworker agent**, not a pre-spin baking requirement for any flow below — and it
must **not** be done on the org headed for TrialForce (see the warning below).

> **⚠ Data Cloud must NOT be provisioned on the TrialForce source (TSO) org.**
> Provisioning Data Cloud breaks TrialForce snapshot creation — so the org you
> template must be captured with Data Cloud **off**, and the attendee enables it
> post-clone (as the guide already directs). **Consequence for verification:** do
> **not** enable features to smoke-test the *template* org — that ruins the TSO.
> The seeded data/config is verified by **query** (see the audit below); any live
> end-to-end run of the Coworker/Data-Cloud exercises must happen on a **separate,
> disposable clone**, never on the org headed for TrialForce.

#### Explicitly OUT OF SCOPE — `DocAI_CreateQuote` (a.k.a. the "DocAI Package")
The `df26-ws` source org carries a screen flow **`DocAI_CreateQuote`** (Flow API
name `CreateQuote`, active v3) and its supporting bundle — the unmanaged **"DocAI
Package"**: apex `de_DataCloudIDPFlowAction` / `de_Extract_Document_AI_Details` /
`de_LineItem`, the `NavigateToRecord` Aura component, and the
`AddQuoteLineItemRequest__e` platform event. The flow runs Data Cloud IDP
document extraction (`/services/data/vXX/ssot/document-processing/…` callouts),
creates a Contact + Opportunity, and quotes via `quotingAI__createInitialQuoteOnOpp`.

**It is NOT part of the workshop and is deliberately not captured or deployed.**
Evidence: the Sept-2026 exercise guide has zero references to DocAI / Document AI
/ IDP / document upload / the `CreateQuote` flow. The guide's "PDF" scene (Act 2,
Scene 1) does **not** extract a PDF — it reads an *existing quote literally named*
`Quote PDF` (the guide warns to quote the string so Coworker doesn't hunt for a
file), then has the Coworker agent copy its 15 lines onto a new **Target Quote**
on the **Target Opportunity / Acme** (both seeded in bucket C). So the workshop's
document→quote story is served entirely by the `Quote PDF` quote + the Target
Opportunity — the DocAI flow is leftover build/experiment drift on `df26-ws`.
(Recorded here so it is not re-investigated: the apex is deploy-safe pre-Data-Cloud
— it reaches SSOT only via HTTP callout, not Apex types — but there is no reason
to deploy it.)

### B. Config toggles — scriptable (insert step, idempotent)
| Change | Grounded target | Mechanism |
|---|---|---|
| Assign perm set **Agentforce Coworker Admin** to the running admin | PermissionSet API name **`AISearchAdmin`** (Standard) | `PermissionSetAssignment` upsert (perm sets assign to *users*, not profiles) |
| Deactivate pricing procedure **RLM PRM DISTI Pricing Procedure** (breaks order creation) | ExpressionSet `RLM_PRM_DISTI_Pricing_Procedure`, `UsageType=DefaultPricing` | Deactivate active version / clear the default-pricing assignment via the `expression-sets` toolkit — **deactivate, don't delete** (reversible). It breaks orders precisely because `DefaultPricing` applies it globally. |

### C. Transactional data — the extract/replay core (this toolkit)
The three canvas quotes, captured from `df26-ws`:

| Quote | Shape |
|---|---|
| `Quote PDF` | 15 lines (mixed OneTime hardware + TermDefined subscriptions); 6 configured-product attributes. **Name must be exactly `Quote PDF`** — the workshop guide has the Coworker agent look it up by that literal string (Ex. 6). |
| `3 Year Ramp - AI Licenses` | 1 product (`QB-GEN-AI-LIC`), 3 yearly ramp segments (qty 4000→6000→10000) |
| `4 Year Ramp - AI Licenses` | 1 product (`QB-GEN-AI-LIC`), 4 yearly ramp segments (qty 2500→5000→7500→10000) |

Plus their anchors — the accounts/contacts/opportunities the quotes hang off,
**and** the seeded scenario records the exercise guide drives quotes *from* that
no captured quote references:

| Anchor | Records | Source |
|---|---|---|
| Accounts | Global Media, Infinitech (quote anchors); Acme, Apex Dynamics (seeded) | quote refs + `--seed-opps`/`--seed-accounts` |
| Contacts | Carol White | quote anchor |
| Opportunities | Proposal PDF (Global Media), QuantumBit Licenses (Infinitech) — quote anchors; **Starter Opportunity** & **Target Opportunity** (Acme) — seeded | quote refs + `--seed-opps` |

The extractor is otherwise quote-driven, so the two Acme opportunities the
Coworker exercises look up by literal name (Ex.: *"the Starter Opportunity on the
Acme account"*, *"the Target Opportunity"*) are captured via `--seed-opps`
(default `Starter Opportunity,Target Opportunity`). **Apex Dynamics** carries no
seeded opportunity — the guide has the agent create *"New Opportunity for Apex
Dynamics"* live — so only the account is drift, captured via `--seed-accounts`
(default `Apex Dynamics`). The 60+ `CustomerX - $NNK #NN` partner-pipeline opps
are the randomly-generated PRM data the canvas excludes ("*not randomly
created*", "*record counts are very small*") and are **not** captured.

**All quote products are standard QuantumBit catalog SKUs** already seeded by
`insert_quantumbit_pricing_data` / the QB build. So this toolkit does **not**
re-seed the catalog — it depends on the QB foundation being present in the
clone, and reprices against it.

## Why replay, not DML

QuoteLineItem / QuoteLineItemAttribute / QuoteLineDetail / ramp segments are
**derived** — the platform generates them when a quote is created and priced.
Direct `QuoteLineItem` DML is rejected for TermDefined products
(BillingFrequency ⇄ BillingTreatment coupling) and produces un-priced,
inconsistent lines even where accepted. So the quotes must be **re-created
through `POST /connect/rev/sales-transaction/actions/place`** (Place Sales
Transaction) and priced (`pricingPref: system`), letting the org generate the
children. This mirrors `scripts/build_quote_to_asset.py`.

A **ramp** is N QuoteLineItems for the same product sharing a **`RampIdentifier`**,
each a segment (`SegmentName` Year-1/2/…, `IsPrimarySegment`, `SegmentType=Yearly`)
with its own date range and quantity. We do **not** copy the source org's opaque
`RampIdentifier`/`SegmentIdentifier` tokens or DML the segment rows. Instead the
insert side builds the ramp the platform way, so the org mints fresh identifiers.

A quote may carry **more than one ramp** (distinct `RampIdentifier`s) and may
**mix** ramp segments with ordinary non-ramp lines. The replay partitions a quote's
lines by `RampIdentifier` into ramp groups + plain lines, then:

1. **Place the quote once** with every plain line plus **each group's primary
   (Year-1) segment** as plain priced lines. Placement order == `LineNumber` order,
   so each placed primary is recovered by ordinal (SKU-verified) before segment
   generation grows the line set.
2. Per ramp group, call **Create Ramp Deal** off that group's primary line —
   `POST /connect/revenue-management/sales-transaction-contexts/{lineId}/actions/ramp-deal-create`
   with `subscriptionTerm = 12 × N` months, `subscriptionTermUnit=MONTHS`,
   `segmentType=YEARLY`. The platform generates the N yearly segments and returns
   a `transactionContextId` + a map of generated segment ids by `ItemSegmentName`.
3. **Place with context** (`contextDetails.contextId`) a PATCH graph that reprices
   each non-primary segment to its captured quantity + discount.

The shipped workshop quotes are each a single ramp (no plain lines), which is just
the one-group case of the above. See the 264 dev guide, *Create Ramp Deal (POST)*.

**Scope of the multi-ramp/mixed path.** The single-ramp, no-plain-lines case is
live-verified (the three shipped quotes). The multi-group and mixed shapes are
exercised by offline unit tests (`tests/test_df_workshop_replay.py`) but have **not**
been run against a live org — no such workshop quote exists yet. Two shapes are
refused up front rather than replayed incorrectly:

- A ramp/mixed quote that also carries **configured `QuoteLineItemAttribute`
  records** — the attribute→line ordinal match cannot survive segment generation,
  so attributes are not dropped silently; the replay fails and asks you to extend it.
- Two lines sharing the **same SKU** in one ramp replay (two same-SKU primaries, or a
  plain line sharing a primary's SKU) — the SKU-verified ordinal recovery of each
  primary would be ambiguous, so the replay fails rather than risk binding the wrong
  line. Give each ramp group a distinct product.

## What the extractor captures — a portable replay spec, not a data dump

`extract_workshop_quotes.py` emits `datasets/df_workshop/workshop_quotes.json`
capturing the **inputs** to the replay, with every Salesforce Id resolved to a
natural key (SKU, Account/Opp/Pricebook name) so the spec is portable into any
clone.

```
python scripts/df_workshop/extract_workshop_quotes.py --org df26-ws
  # --quotes "A,B,C"         override quote names
  # --seed-opps "X,Y"        Opportunity names to capture even if no quote refs them
  # --seed-accounts "Z"      Account names to capture even if no opp refs them
  # --out <path>             override output
```

Output schema (`workshop_quotes.json`):
- `anchors.{accounts,contacts,opportunities}` — full DML-safe records (upsert by Name on insert), including the seeded records above
- `quotes[]`
  - `quote` — header (account/opp/contact/pricebook/currency/status/dates), refs resolved under `_keys`
  - `lineItems[]` — per line: product SKU, quantity, unit price, selling model, dates, billing frequency/treatment, period boundary, and ramp fields
  - `childRecords.{QuoteLineItemAttribute,QuoteLinePriceAdjustment,QuoteLineDetail}` — manual configuration & adjustments, grouped by line
  - `rampSummary` — lines grouped by `RampIdentifier` for legibility

Every record keeps `_sourceId` for traceability; the insert side must never use it.

## Status

- [x] **Extract** — `extract_workshop_quotes.py` (read-only). Validated against `df26-ws`;
      captures the 3 quotes + their children and the seeded Acme/Apex Dynamics anchors.
- [x] **Insert / replay** — `insert_workshop_quotes.py`. Validated live against
      `df26-ws-test`: anchors upsert idempotently (incl. Starter/Target opps with their
      Amounts); all 3 quotes replay via Place Sales Transaction — the two ramps built the
      platform way (Create Ramp Deal → place-with-context reprice, fresh identifiers) and
      the Quote PDF's 6 configured attributes replayed — reproducing source economics.
- [x] **Bucket-B config** — verified on `df26-ws-test`: the `AISearchAdmin` (Agentforce
      Coworker Admin) perm set is assigned to the running admin. The DISTI item is a
      **no-op on this line**: neither `df26-ws` nor `df26-ws-test` has an *active* DISTI
      (or any active `DefaultPricing`) `ExpressionSet` — only the inert
      `ExpressionSetDefinition` metadata — so nothing applies globally to break order
      creation. Desired end-state already matches source; the `--apply-config`
      deactivation stub stays a stub because there is nothing to deactivate. (Re-check
      before templating if a build step ever activates a DISTI procedure.)
- [x] **Promoted to a registered skill** under `.cursor/skills/df-workshop-setup/`
      (routed in `AGENTS.md`, `.cursor/skills/README.md`, `.claude/skill-manifest.yml`).
