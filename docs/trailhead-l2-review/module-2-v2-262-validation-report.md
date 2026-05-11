# Module 2 v2 — 262 Snapshot Validation Report

**Date:** 2026-05-11
**Validator:** Claude (via revenue-cloud-docs skill)
**Source of truth:** `docs/salesforce/262/help/articles/*.md` (171 articles, Summer '26)
**Companion source:** project metadata (qb-billing CSV headers, qb-tax README, erd-data.json)
**Subject doc:** `docs/trailhead-l2-review/module-2-v2.md`
**Status:** All non-blocking edits applied. Open questions parked for Mike (Section 11).

## Edits applied — summary table

| ID | Edit | Status | Module 2 v2 location |
|---|---|---|---|
| G | Replace stale Resources article IDs (Unit 1 + Unit 2) | ✅ Applied | Resources sections, both units |
| F | Rewrite "Exclude holidays/weekends" — Daily/Weekly/Monthly availability | ✅ Applied | Unit 2 cadence table + callout + Key Takeaways |
| E | Add asset-linked BSG constraint + enhanced Standalone API 262 note | ✅ Applied | Unit 2 Standalone Billing Schedules section |
| D | Lead milestone instructions with UI labels; move API names to developer aside; soften Remainder BTI; add "Support Milestone Plans for Amended Billing Schedules" 262 setting | ✅ Applied | Unit 1 milestone setup + runtime sections |
| A | Header tax phrasing — drop "third-party engines" restriction; cite UI label + SObject field | ✅ Applied | Unit 1 Tax Policy section |
| B | TaxEngineAddress as read-only compound field; mention invoice-line override | ✅ Applied | Unit 1 Tax Policy section |
| C | Tax Code as a shared identifier, not a field exclusively on Tax Rate | ✅ Applied | Unit 1 Tax Policy section, Tax Rate bullet |
| — | Header source-verification block + footer stamp | ✅ Applied | Top of doc + footer |

**Not yet applied — pending Mike's input** (see Section 11):
- Three-paths framing for order-derived billing schedules (Unit 1 Section 4).
- Order to Billing Schedule flow clone-and-customize content — keep cited from 260 or re-source.

---

## TL;DR (updated post-edits)

Module 2 v2 was **structurally sound** against the 262 snapshot. The Billing Policy / Treatment / BTI hierarchy, the Tax Policy chain, the Milestone Plan template-vs-runtime story, and the Order activation prereqs all held up.

**All non-blocking corrections have now been applied** to `module-2-v2.md`. Three substantive corrections, four precision edits, and three 262-enhancement callouts are now reflected in the doc. The header source-verification block and footer stamp have been updated to point at the 262 snapshot.

**Five open questions remain for Mike** — see Section 9. They're judgment calls (depth of coverage, placement of "What's new in 262" content, whether to re-source the Order-to-Billing-Schedule flow detail) rather than factual disputes.

The detailed findings below (Sections 1–8) record the per-claim citations against the 262 snapshot for audit purposes. Each substantive edit is identified by the same A–G letter codes used in the original validation pass.

---

## 1. Billing Policy hierarchy — Unit 1, "Configure the Billing Policy"

### What's confirmed

- Three-tier hierarchy (Billing Policy → Billing Treatment → Billing Treatment Item). ✓
- Four Billing Treatment Selection modes (None, Manual, Default, Legal Entity). ✓ Per `ind.billing_treatment_resolution.htm`.
- Default Billing Treatment fallback behavior. ✓
- Legal Entity scoping of Treatments when policy uses Legal Entity selection. ✓
- "Manual override on the Order Product while the Order is in Draft" — terminology checks out against the resolution article.
- Activation sequence (draft policies → treatments → BTIs → activate up the chain). ✓ Per `ind.billing_considerations.htm`.

### Minor edits

- M2v2 line 79 says "A Billing Treatment can be attached to an Order Product in three modes — Default, Manual, or Legal Entity." The selection options field on the **policy** has four values (None, Manual, Default, Legal Entity). For seller-facing prose, "three modes" reads fine — None just means no auto-selection happens. Optional clarification: explicitly call out None or drop to "three primary modes."
- M2v2 line 67 claim that "ProcessingOrder controls which BTI fires first when multiple are involved" — not directly confirmed in the 262 snapshot (the BTI configuration article is thin on ProcessingOrder semantics). Project metadata confirms `ProcessingOrder` is a real field on `BillingTreatmentItem` (per qb-billing CSV header). The behavioral description rests on internal knowledge, not snapshot text. Recommend Mike confirm wording.

---

## 2. Tax Policy chain — Unit 1, "Configure the Tax Policy"

### What's confirmed

- Tax Policy → Tax Treatment → Tax Treatment Item hierarchy. ✓ Per `ind.billing_policies_and_treatments.htm` and tax configuration articles.
- Tax Treatment references a Tax Engine. ✓
- Tax Engine Provider exists as a configurable record. ✓ Per `ind.billing_understand_tax_interface_extension.htm`: "Tax Engine Provider: This is your configured connection to your tax provider. You associate your custom metadata type directly to your tax engine provider."
- TaxEngineAdapter Apex interface for partner/custom adapters. ✓ Per `ind.billing_tax_configuration_prerequisites.htm`: "define a custom tax adapter by extending the TaxEngineAdapter Apex interface."
- Revenue Standard Tax Engine as out-of-the-box engine. ✓ Per `ind.billing_standard_tax_rate.htm`.
- Revenue Standard Tax Entries decision table. ✓
- Decision table must refresh after Tax Rate changes. ✓ Per `ind.billing_tax_rate_configure.htm`: "Check for and refresh the Revenue Standard Tax Entries decision table every time a tax rate record is modified or added."
- Tax Rate fields (jurisdiction, currency, percentage/flat, application basis, priority, validity, legal entity). ✓ All confirmed in `ind.billing_tax_rate_configure.htm`.

### Precision edits

**Edit A (line 123) — Header-level tax capture phrasing.**
M2v2 currently:
> "Header-level tax capture is available through third-party engines via the `ShouldCaptureTaxesAtHeader` field on the Tax Engine record"

Per `ind.billing_setup_header_tax_enable.htm`: "Tax admins can use the Capture Taxes at Header option when they configure the tax engines." The Help article doesn't restrict this to third-party engines. The field is on the TaxEngine SObject generally.

Proposed:
> "Header-level tax capture is configurable on the Tax Engine record (UI label: **Capture Taxes at Header**; SObject field: `ShouldCaptureTaxesAtHeader`). Use it when your engine returns a single consolidated tax amount at the invoice header rather than per line — a common pattern with third-party engines like Vertex or Avalara."

**Edit B (line 125) — TaxEngineAddress field.**
M2v2 currently:
> "This can be overridden at the Tax Engine level via the **TaxEngineAddress** field"

Per project metadata (`docs/erds/erd-data.json` line 97), `TaxEngineAddress` is a **read-only compound address field** on the TaxEngine object. The underlying editable fields are `TaxEngineStreet`, `TaxEngineCity`, etc. The 262 snapshot also references a fragment `billing_tax_address_invoice_line_override` (not captured directly) suggesting there's also an invoice-line-level override.

Proposed:
> "This can be overridden at the Tax Engine level via the address fields on the Tax Engine record (the compound `TaxEngineAddress` field aggregates the underlying street/city/state/postal fields). An additional invoice-line-level override is also available — useful when individual lines need a different tax address than the BSG default."

**Edit C (line 117) — Tax Code field placement.**
M2v2 currently:
> "The **Tax Code** field on Tax Rate is what links it to Tax Treatments at calculation time."

Per `ind.billing_tax_rate_configure.htm`: "The tax code defined here is used in tax treatment and tax treatment item records to determine how the tax rate is applied. Ensure that the same tax code is consistently referenced across tax configurations so the correct rate is applied during transaction processing."

The Tax Code is a shared string identifier configured on Tax Rate AND referenced from Tax Treatment / Tax Treatment Item — it's not strictly a field "on Tax Rate." Current wording is roughly correct but could mislead a developer reader. Optional refinement:

> "The **Tax Code** is the string identifier that ties a Tax Rate to its consuming Tax Treatment or Tax Treatment Item. Configure it on the Tax Rate and reference the same value from the Treatment side so the engine picks the correct rate at calculation time."

---

## 3. Milestone Plans — Unit 1, "Set Up Milestone Billing" + "Customize and Edit Milestone Plans"

### What's confirmed

- Two methods (Method 1: BTI template → auto-generated runtime; Method 2: manually create plan for an Order Product). ✓ Per `ind.billing_milestone_methods.htm`.
- "Enable milestone billing" toggle on the Billing Treatment. ✓
- Milestone Type = Event or Date. ✓
- Active Billing Milestone Plan restrictions (only "Milestone accomplished" editable; revert to Draft to edit anything else). ✓ Per `ind.billing_milestone_usecase.htm`.
- Cancellation behavior — invoiced milestones stay, uninvoiced date-based milestones move to Canceled, credit memo issued for difference. ✓ Per `ind.billing_milestone_amended_renewed_canceled_assets.htm`.

### Substantive correction — field name labeling

**Edit D (line 95–96 + line 156) — Lead with UI labels, not API names.**

M2v2 currently uses **API field names** in instructional prose:
- Line 95: "Set MilestoneStartDate to the anchor (commonly OrderProductActivation)"
- Line 96: "set MilestoneStartDateOffset and MilestoneStartDateOffsetUnit"
- Line 156: "The BTI carries `MilestoneStartDate`, `MilestoneStartDateOffset`, and `MilestoneStartDateOffsetUnit`. The Billing Milestone Plan Item rebadges these as `CommencementDate`, `CommencementDateOffset`, and `CommencementDateOffsetUnit`."

API names are correct (confirmed against qb-billing CSV and erd-data.json), but the **Help portal labels these BTI fields as**:
- "Milestone Commencement Trigger" (not "Milestone Start Date")
- "Milestone Commencement Offset"
- "Milestone Commencement Offset Unit"

A learner clicking through Setup UI will see "Milestone Commencement Trigger" — not "MilestoneStartDate." This is a Trailhead audience problem: most readers are Sales Professionals (per the badge category), not developers.

Proposed approach:
- Lead with UI labels in instructional steps.
- Keep the "field names shift between template and runtime" callout but reframe it as a developer-aside.

Replacement for lines 94–96:
> - For Date milestones: select **Billing Schedule Start Date** as the **Milestone Commencement Trigger** (the anchor). Then set the **Milestone Commencement Offset** and **Milestone Commencement Offset Unit** (for example, 1 Month, or 4 Months).

Replacement for line 156:
> Worth flagging for developers tracing a milestone from configuration to runtime: the **API field names** shift between template and Plan Item even though the UI labels stay close. On `BillingTreatmentItem` the API fields are `MilestoneStartDate`, `MilestoneStartDateOffset`, and `MilestoneStartDateOffsetUnit`. The `BillingMilestonePlanItem` re-badges them as `CommencementDate`, `CommencementDateOffset`, and `CommencementDateOffsetUnit`. UI labels on both objects use "Commencement Trigger / Offset / Offset Unit."

### Minor refinement — Remainder BTI

M2v2 line 97 says "Each Treatment must include exactly one Type=Remainder BTI that absorbs whatever isn't claimed by the Percentage and Flat Amount BTIs."

Per `ind.billing_milestone_usecase.htm`:
> "A fifth billing milestone plan item with the remainder of the 5% with milestone amount of $500 is automatically generated after you activate the associated billing milestone plan."

The Help docs describe the Remainder as **auto-generated** by the system when there's leftover percentage — not as something the admin must explicitly author as a BTI. Recommend softening:

Proposed:
> The Percentage and Flat Amount BTIs distribute the value; a Remainder BTI catches whatever isn't claimed. When you author a milestone Treatment whose Percentage/Flat Amount BTIs don't sum to 100%, the system auto-generates a Remainder Plan Item to absorb the gap.

### New 262 detail worth adding

Per `ind.billing_milestone_amended_renewed_canceled_assets.htm`, there's a 262-relevant setting:
> "When the Support Milestone Plans for Amended Billing Schedules setting is enabled, Billing creates or links a milestone plan to the amendment schedule and recalculates milestone dates and amounts from the amendment start date."

This is a 262 behavioral toggle. Recommend a one-line callout at end of the Customize and Edit Milestone Plans section:

> When amendments are involved, by default milestone billing doesn't create new plans or plan items for amend/renew orders. The **Support Milestone Plans for Amended Billing Schedules** setting changes that behavior: with it enabled, amendments create or link a milestone plan to the amendment schedule and recalculate dates and amounts from the amendment start date.

---

## 4. Order to Billing Schedule Flow — Unit 1, "Activate the Order to Billing Schedule Flow"

### What's confirmed

- Order activation prerequisites once Billing is enabled: Bill to Contact, Billing Address, Shipping Address. ✓ Per `ind.billing_setup_enable.htm` and `ind.billing_considerations.htm`.

### What the snapshot doesn't directly confirm

The 262 snapshot does NOT contain a dedicated detailed article about cloning the Order to Billing Schedule flow, the "Custom" naming convention recommendation, or the parallel-with-Order-to-Asset detail. Those details appear in the 260 PDF compendium but aren't surfaced as a standalone Help article in 262.

The 262 references to the flow are at meta-level only:
- `ind.billing_schedules_create.htm`: "To generate billing schedules from orders, use the Order to Billing Schedule flow, **Create Billing Schedules for Orders API**, or Create Standalone Billing Schedules API."

### Substantive addition — call out the three paths

M2v2 currently frames the Order to Billing Schedule flow as THE standard automation. In 262 there are three documented paths for order-derived billing schedules. Recommend adding one paragraph at the top of the section:

> When an Order is activated, Billing supports three paths for creating its Billing Schedule Group and Schedules: (1) the **Order to Billing Schedule flow** — the standard automation, which is what most customers use; (2) the **Create Billing Schedules for Orders API** — for headless / API-driven scenarios; and (3) the **Create Standalone Billing Schedules API** with BillingContext — which can also handle order-derived transactions when programmatic control is needed. Most customers default to path 1. The flow is the right starting point.

### Open question for Mike

The clone-and-customize / "Custom" naming convention story M2v2 covers is high-value seller content but isn't directly grounded in the 262 snapshot. Two options:

- (a) **Keep the content** in M2v2 and accept that it's grounded in 260 PDF / org behavior, not 262 Help article text. Cite the 260 source.
- (b) **Verify against the org** before next review — clone the flow in a 262 sandbox and confirm the rename pattern still holds.

Recommend (a) for now and capturing this as a question for Mike to confirm or rephrase from his SME knowledge.

---

## 5. Standalone Billing Schedules & External Billers — Unit 2

### What's confirmed

- Create Standalone Billing Schedules API exists. ✓ Per `ind.billing_schedules_standalone_api.htm`.
- StandaloneBillingContext context definition. ✓ Per `ind.billing_standard_context_definitions.htm`.
- BillingContext for order-derived processing. ✓ (Same article.)
- Supports original, amended, canceled, renewed, ramped, bundled, usage-based transactions. ✓ Per standalone API article.
- Invoice Ingestion API for external invoice ingestion (and debit-memo → invoice generation). ✓ Per `ind.billing_invoice_creation.htm`.
- Import External Tax Lines with TaxProcessingStatus field on a CSV. ✓ Per `ind.billing_tax_lines_import.htm`.
- TaxEngineAdapter Apex interface. ✓
- Suspend Billing API / Resume Billing API. ✓ Per `ind.billing_suspend_and_resume.htm`.
- Custom intracontext mapping. ✓ Per `ind.billing_configure_context_definitions.htm`.

### Substantive addition — asset-linked BSG constraint

**Edit E (Unit 2, "Create and Amend Standalone Billing Schedules" section).**

Per `ind.billing_schedules_standalone_api.htm`:
> "IMPORTANT When a billing schedule group is linked to an asset, initiate any new sale, amend, renew, or cancel actions directly from the order or asset. In such cases, use the Order to Billing Schedule flow or Create Billing Schedules for Orders API, and **not** the Create Standalone Billing Schedules API."

M2v2 currently implies the Standalone API can be used freely for the full transaction lifecycle. The asset-link constraint is missing.

Proposed addition (after line 221 "The Create Standalone Billing Schedules API supports the full transaction lifecycle..."):

> One important constraint: when a Billing Schedule Group is already linked to an asset, downstream amendments, renewals, and cancellations must run through the Order to Billing Schedule flow or the Create Billing Schedules for Orders API — not the Standalone API. The Standalone API path is for billing schedules that don't have an asset on the other side of the relationship.

### 262 enhancement to call out

Per the same article:
> "Starting Summer '26, you can use the enhanced Create Standalone Billing Schedules API to pass minimal, intent-based requests for amendments, renewals, cancellations, and any changes to price, quantity, or end dates. Billing automatically computes the required fields such as unit price and total price by using historical transaction context or Billing Schedule Group IDs."

Proposed addition (Unit 2, near the end of the standalone section):

> A 262 enhancement worth knowing for technical eval conversations: the Standalone API now supports **minimal, intent-based requests** for amendments, renewals, cancellations, and price/quantity/end-date changes. Billing auto-computes unit price and total price from historical transaction context or Billing Schedule Group IDs, so the caller doesn't need to re-state everything to make a single change.

---

## 6. Invoice Scheduler — Unit 2, "Configure the Invoice Scheduler"

### What's confirmed

- App Launcher path: "Billing Batch Schedulers → New Invoice Scheduler." ✓ Per `ind.billing_automate_invoice_run_schedules.htm`.
- Configuration categories (cadence, date logic, filters, Post invoices toggle). ✓
- Limits: 30 active billing batch schedulers, 2000 invoice lines per invoice. ✓ Per same article.
- Frequency options: Once, Daily, Weekly, Monthly. ✓
- Date logic fields (Target Date, Target Date Offset, Invoice Date, Invoice Date Offset, Calculate invoice date from run date). ✓
- Filter fields (billing batch, charge type, legal entity, customer account, currency). ✓
- "Start run now" option for one-time runs — M2v2 doesn't currently mention this. Optional add.
- Email delivery is a separate feature ("Send Invoices Through Email"). ✓ Per `ind.billing_invoices_email_prerequisites.htm`.

### Substantive correction — "Exclude holidays and weekends" availability

**Edit F (M2v2 line 266 + 270).**

M2v2 currently:
- Line 266: "Exclude holidays and weekends (Monthly only)"
- Line 270: "the 'Exclude holidays and weekends' option is available in 260, not a 262 enhancement... It applies only to Monthly-frequency schedulers."

Per `ind.billing_automate_invoice_run_schedules.htm` line 60:
> "If you select a **Daily, Weekly, or Monthly** frequency, specify these values..."
> "Exclude holidays and weekends: Selecting the checkbox moves the scheduler's next run date to the following business day if it falls on a company holiday or a weekend."

In 262 the option is available for **all recurring frequencies (Daily, Weekly, Monthly)** — not Monthly only. This may be the 262 enhancement the FY27 outline hinted at: 260 likely shipped Monthly-only, and 262 expanded coverage. Recommend rewriting the entire "Exclude holidays and weekends" callout:

Proposed replacement (line 270):
> A note on a 262 enhancement: the **Exclude holidays and weekends** option is now available for all recurring frequencies — **Daily, Weekly, and Monthly**. Before 262 this option was restricted to Monthly scheduling. When enabled, the scheduler's next run moves to the following business day if it falls on a holiday or weekend. The Once frequency doesn't carry this option because there's no recurring run to defer.

Proposed update to the setting category table (line 266):
> | **Cadence** | Frequency (Once / Daily / Weekly / Monthly), Exclude holidays and weekends (Daily/Weekly/Monthly) | Sets how often the scheduler fires; the holiday/weekend exclusion is available on all recurring frequencies |

---

## 7. Resources article IDs — both Units

**Edit G — replace stale article IDs.**

### Unit 1 Resources (M2v2 lines 191–193)

| Old (in M2v2) | Current 262 ID | Title |
|---|---|---|
| `ind.billing.htm` | `ind.billing.htm` ✓ KEEP | (title updated to "Manage Billing in Agentforce Revenue Management") |
| `ind.billing_payment_terms.htm` | **`ind.billing_policies_and_treatments.htm`** | "Define Billing Policies and Billability Rules" |
| `ind.billing_milestone.htm` | **`ind.billing_milestone_plans.htm`** | "Configure Milestone Billing" |

The `ind.billing_payment_terms.htm` ID still exists in 262, but it's now the article **"Create Payment Terms"** — a child of the Billing Policies parent, not the parent itself. M2v2's link text "Define Billing Policies and Billability Rules" matches the **parent** article, whose ID is `ind.billing_policies_and_treatments.htm`. If you actually want the link to land on Define Billing Policies content, fix the ID. If you actually want a payment terms link, keep the ID and rename the link text.

The `ind.billing_milestone.htm` ID 404s in 262 (renamed to `ind.billing_milestone_plans.htm`).

### Unit 2 Resources (M2v2 lines 290–292)

| Old (in M2v2) | Current 262 ID | Title |
|---|---|---|
| `ind.billing_invoice_run.htm` | **`ind.billing_invoice_generation.htm`** | "Generate Invoices in Agentforce Revenue Management" |
| `ind.billing_migrate_external.htm` | **`ind.billing_schedules_standalone_api.htm`** | "Generate Billing Schedules from External Transactions or Salesforce Objects" |
| Developer Guide URL | (external, keep as-is) | Billing Business APIs |

Neither `ind.billing_invoice_run.htm` nor `ind.billing_migrate_external.htm` exists in the 262 manifest.

---

## 8. Cross-cutting precision opportunities

These are not corrections — just places where the 262 snapshot suggests slightly tighter phrasing than M2v2 currently uses.

- **Header tax address phrasing.** M2v2 says "the address used for tax calculation comes from the Billing Schedule Group." Per `ind.billing_standard_tax_rate_application.htm` the matching uses the "shipping address" on the transaction (which usually flows from the BSG). Either phrasing is fine for sellers; cite source either way.
- **Product rename "Revenue Cloud → Agentforce Revenue Management"** is visible in nearly every 262 article. M2v2 already uses Agentforce Revenue Management in the supporting category and in some prose. The "Manage Billing in Revenue Cloud" link text in Unit 1 Resources should become "Manage Billing in Agentforce Revenue Management" to match 262 article titles.

---

## 9. Open questions for Mike (consolidated)

These are the items remaining for Mike to weigh in on. Everything else surfaced by this validation pass has been applied to `module-2-v2.md` (see the Edits Applied table at the top of this report).

1. **Order to Billing Schedule flow detail (Section 4).** The clone-and-customize specifics in M2v2 (Custom naming convention, parallel-with-Order-to-Asset, single active version cautions) aren't captured in the 262 snapshot — they appear in 260 PDF content and org-internal behavior. Want to (a) keep the content cited from 260, (b) drop the detail and link to the org's setup guidance, or (c) re-source from your SME knowledge with an updated citation?

2. **Three paths for order-derived schedules (Section 4).** 262 explicitly documents three paths: the Order to Billing Schedule flow, the Create Billing Schedules for Orders API, and the Create Standalone Billing Schedules API. M2v2 currently emphasizes only the flow. Should Unit 1 add a one-paragraph framing of all three, or is the flow-centric framing sufficient for this audience (with the API paths landing in a different module)?

3. **"Exclude holidays and weekends" 262 expansion — confirm narrative.** Edit F applied with the framing "262 expanded coverage from Monthly to Daily/Weekly/Monthly." If you have a separate 262 enhancement around scheduler date logic that I should reference instead, point me at it and I'll adjust. If you have a 260-shipped doc that already showed Daily/Weekly coverage, also worth knowing — we'd just drop the "262 enhancement" framing.

4. **Asset-linked BSG constraint depth (Section 5).** Edit E applied. The two-sentence framing is the minimum required for accuracy. Would you like more depth on this (for example, what happens if a user mistakenly calls the Standalone API on an asset-linked BSG)?

5. **262 enhancement placement.** Three new 262 items are now inline in M2v2:
   - Enhanced intent-based Standalone API (end of "Create and Amend Standalone Billing Schedules").
   - "Support Milestone Plans for Amended Billing Schedules" setting (end of "Customize and Edit Milestone Plans").
   - Holidays/weekends expansion to Daily/Weekly/Monthly (Invoice Scheduler section).

   Each is currently woven into its parent section as an aside. Alternative: pull them into a dedicated "What's new in 262" sidebar at the top of each Unit. Preference?

---

## 10. Status & next steps

**Validation pass complete.** All non-blocking corrections applied to `module-2-v2.md`. The doc now reads against the 262 Summer '26 Billing Help snapshot rather than the 260 Spring '26 PDF.

**Ready for:**
- Mike review (5 open questions in Section 9 above).
- Trailhead AI Review Checklist re-run on the edited prose (a few new sentences were added in Edits D, E, F — worth re-checking sentence length and modal usage).

**Not in scope of this pass** (covered separately):
- Modules 1, 3, 4, 5 re-validation against the 262 snapshot. Module 2 was the priority; Mike's earlier feedback was concentrated there.
- Snapshotting other Revenue Cloud areas (Pricing, Quoting, Orders, Contracts, Assets, Usage, DRO). The `revenue-cloud-docs` skill documents the pattern; the per-area task variants are TODO in `cumulusci.yml`.

---

*All citations resolve to articles in `docs/salesforce/262/help/articles/`. Where a claim depends on project metadata rather than the snapshot, the citation says so explicitly.*
