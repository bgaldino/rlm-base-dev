# Module 1 v2 — 262 Snapshot Validation Report

**Date:** 2026-05-11
**Validator:** Claude (via revenue-cloud-docs skill)
**Source of truth:** `docs/salesforce/262/help/articles/*.md` (171 articles, Summer '26)
**Companion source:** project metadata (qb-billing CSV headers, qb-tax README, erd-data.json)
**Subject doc:** `docs/trailhead-l2-review/module-1-v2.md` (pulled from Mike Aaron's "Copy of Module 1 v2" Google Doc on 2026-05-11)
**Status:** Substantive edits applied to `module-1-v2.md` (2026-05-12, after the full 838-article 262 snapshot completed). The Agentforce product names are now grounded against the captured `ind.rev_agent_*` agent suite area — every subagent name in the doc maps to a verified 262 Help article. Open questions for Mike (Section 12) on unsourced terms (High Scale Billing, Spring Batch, m3ter, National Satellite Service) and the voice-checklist re-pass are still pending.

## Edits applied — summary table

| ID | Edit | Status | Module 1 v2 location |
|---|---|---|---|
| A | Agentforce product taxonomy: "Invoice Explanation Agent / Billing Inquiries topic / Agentforce Collections Agent" → the actual 262 subagent names under "Agentforce for Revenue Management." Added Agentforce for Billing Service Assistance Agent for the Experience Cloud customer-facing surface. Anthropomorphism "Agentforce actively works on your behalf" replaced. | ✅ Applied | Unit 1 body + Key Takeaways + Video suggestion |
| B | "Bill Now" → "Generate Invoices" (quick action) | ✅ Applied | Unit 3 mechanics section + Key Takeaways + Audit Trails |
| C | "Billing Preview" → "Preview Invoices" + Invoice Preview API | ✅ Applied | Unit 3 mechanics section + Key Takeaways |
| D | "Usage Summaries" → Usage Entitlement chain (Account → Bucket → Entry) | ✅ Applied | Unit 1 body + Unit 2 Key Takeaways + Unit 3 DPE reference |
| F | Charge Frequency vs Charge Type — separate the two concepts | ✅ Applied | Unit 1 "When to charge" bullet |
| G | TaxEngineAdapter naming + Adapter/Adaptor spelling normalization | ✅ Applied | Unit 3 Tax Adapter bullet |
| — | Invoice Batch Run formal name | ✅ Applied | Unit 3 Batch Scheduler bullet + Key Takeaways + DPE paragraph |
| (evergreen) | Removed "Spring Batch removal," "now free of event consumption," "now with holiday/weekend exclusions" — prior commit | ✅ Applied | Unit 3 Key Takeaways |

**Not yet applied — pending Mike's input:**
- Edit E (Billing Profile / Billing Account framing) — optional precision, hold.
- Edit H (Dispute Management "invocable actions" → "automated resolution actions") — already addressed by the prior evergreen pass.
- Edit I (Unsourced terms: High Scale Billing, m3ter, National Satellite Service) — Mike's input on Section 12 Q5.
- Edit J (Voice checklist re-pass after factual edits) — best done after Mike sees the post-edit doc.

## TL;DR

Module 1 v2 is **less aligned with the 262 snapshot than Module 2 v2 was**. The structural framing (Unit 1: positioning, Unit 2: data model, Unit 3: invoice production) holds up, but several headline product names and a handful of object references in M1v2 don't match what the 262 Help docs actually call these things. There's also a cluster of voice patterns Mike has flagged before that survived the v2 pass.

**Substantive corrections (must fix before SME re-review):**

1. **Agentforce product names** — M1v2 uses "Invoice Explanation Agent," "Billing Inquiries topic," and "Agentforce Collections Agent." 262 Help calls the parent agent **"Agentforce for Billing Employee Assistance"** (internal users) with three subagents: **Invoice Line Explanation**, **Billing Collections Management**, and **Billing Inquiries**. There's also a separate **"Agentforce for Billing Service Assistance Agent"** for external Experience Cloud users — not mentioned in M1v2.
2. **"Bill Now" terminology is stale** — Unit 3 frames invoice production around three things: Billing Preview, Bill Now, Billing Batch Scheduler. The 262 feature is **"Generate Invoices"** (a quick action on Account/Order), not "Bill Now."
3. **"Billing Preview" is stale** — the 262 feature name is **"Preview Invoices"** (or "Invoice Preview API" for the programmatic surface).
4. **"Usage Summaries" is not a 262 object** — Unit 1 says Invoice Explanation Agent queries "Invoice Lines and Usage Summaries." Unit 2 Key Takeaways says "Usage Summaries allow businesses to handle complex, modern revenue models." The actual 262 usage objects are **Usage Entitlement Account / Usage Entitlement Bucket / Usage Entitlement Entry**.
5. **Charge Frequency vs Charge Type conflation** — Unit 1 says "Charge Frequency including one-time, recurring, milestone, and usage-based charge types." Frequency is one-time/recurring; milestone and usage are charge *types*. Unit 2 Key Takeaways gets the four types right ("One-Time, Recurring, Usage-Based, Milestone") but the Unit 1 conflation is misleading.

**Terms that don't appear in the 262 snapshot at all** (need source or removal):

- "High Scale Billing" — 0 hits.
- "Spring Batch removal" — 0 hits. May be a release-notes / marketing claim.
- "DocGen (now free of event consumption)" — 0 hits matching the "event consumption" phrasing.
- "m3ter" — 0 hits (this is a real partnership, but the Help docs don't reference it; partner-only content).
- "Invoice Explanation Agent" — 0 hits (see correction 1).
- "Bill Now" — 0 hits (see correction 2).

**Voice patterns to revisit** (per Mike's Module 2 feedback):

- "Agentforce actively works on your behalf" — direct anthropomorphism Mike has flagged before, still present in Unit 1 "Slow Cash Flow" bullet.
- "digital labor" used as a metaphor for manual data entry (3+ instances, including scare-quoted).
- "swivel chair," "leaks in the business bucket," "risky patchwork," "DNA" — metaphor saturation in Unit 1.
- The opening dominoes metaphor stretches over two paragraphs.

These are AI-Review-Checklist patterns Mike has corrected in M2v2; M1v2 hasn't yet had the same pass.

---

## What's confirmed against the 262 snapshot

These M1v2 claims hold up directly against the snapshot:

- **Order to Billing Schedule flow** as core automation. ✓ Per multiple articles, including `ind.billing_schedules_and_schedule_groups.htm`.
- **BSG → Billing Schedule → Invoice golden path.** ✓ Per `ind.billing_schedules_and_schedule_groups.htm`: "Billing schedules define when and how an order product is invoiced. Billing schedule groups contain one or more billing schedules."
- **Billing Profile concept.** ✓ Per `ind.billing_billing_profiles_create.htm`. *But see Section 5 below — the Billing Profile / Billing Account naming is more nuanced than M1v2 states.*
- **Legal Entity governs tax + GL context.** ✓ Per `ind.billing_legal_entities_manage.htm` and `ind.billing_legal_entity_default.htm`.
- **Data Processing Engine (DPE) as the engine behind invoice generation.** ✓ Per `ind.billing_invoice_batch_run.htm` (which references DPE) and `ind.billing_automate_invoice_run_schedules.htm` (which calls out Data Pipelines / DPE dependencies).
- **Billing Period Items as the granular per-billing-period charges.** ✓ Per `ind.billing_invoice_scheduler_amended_bundle_schedule_groups.htm` (the only article where the term appears, but the concept is confirmed).
- **TaxEngineAdapter Apex interface** as the path to Avalara / Vertex / custom tax engines. ✓ Per `ind.billing_tax_configuration_prerequisites.htm`. *But see Section 8 below — M1v2 says "Tax Adapter," the formal name is `TaxEngineAdapter`.*
- **Refunds Orchestration** exists as a feature. ✓ Per `ind.billing_refund_orchestration.htm` (titled "Issue Refunds and Settle Balances"). *Help uses lowercase "refund orchestration" as a process name rather than "Refunds Orchestration" as a capitalized product name.*
- **Dunning Orchestration** as the collections automation mechanism. ✓ Per `ind.billing_dunning_orchestration_enable.htm`.
- **Document Generation Service** with Omnistudio templates, Document Builder, low-code customization. ✓ Per `ind.billing_setup_document_generation.htm` and related articles.
- **Billing Dispute Management** with automated resolution actions. ✓ Per `ind.billing_manage_disputes.htm`. *But see Section 9 — "invocable actions" is M1v2's phrasing, not the Help's.*
- **Suspend / Resume Billing** as customer-facing controls. ✓ Per `ind.billing_suspend_and_resume.htm`.
- **Holiday / weekend exclusions** as a 262 scheduler enhancement. ✓ Per the M2v2 validation finding — the option is now available for Daily, Weekly, AND Monthly recurring frequencies in 262 (was Monthly-only in 260).
- **The 4 charge types** (One-Time, Recurring, Usage-Based, Milestone) — Unit 2 Key Takeaways gets this right.

---

## 1. Agentforce product names — Unit 1

### What M1v2 says

- "Service uses the **Invoice Explanation Agent** to query Invoice Lines and Usage Summaries, while the **Billing Inquiries topic** pulls real-time data from the Payment and Credit Memo objects."
- "**Agentforce actively works on your behalf** to prioritize collections through the **Agentforce Collections Agent** — using Dunning Orchestration..."
- Key Takeaways: "Shared data across Sales, Service, Finance, and Partners reduces customer friction and powers agentic experiences like the **Invoice Explanation Agent**, the **Billing Inquiries agent**, and the **Collections Agent**."

### What the 262 Help actually documents

Per `ind.billing_agentforce_billing_agent.htm` ("Agentforce for Billing Employee Assistance") and `ind.billing_agentforce_for_billing_service_assistance_agent.htm`:

- The parent product for internal users is **Agentforce for Billing Employee Assistance**.
- It has three subagents:
  - **Subagent: Invoice Line Explanation** — "Help users understand their invoice lines by providing detailed explanations of each charge."
  - **Subagent: Billing Collections Management** — "an at-a-glance view of financial standing, highlighting high-risk invoices based on payment history, disputes, and outstanding balances."
  - **Subagent: Billing Inquiries** — "answers questions about account balances, payment plans, upcoming payment dates, invoice details, and downloadable invoice documents."
- A separate, customer-facing product **Agentforce for Billing Service Assistance Agent** runs in the Experience Cloud billing portal for external users.

### Substantive correction

**Edit A.** Re-name the agent references throughout Unit 1 to match the 262 product taxonomy:

| M1v2 (current) | 262 product name |
|---|---|
| "Invoice Explanation Agent" | **Subagent: Invoice Line Explanation** (under Agentforce for Billing Employee Assistance) |
| "Billing Inquiries topic" | **Subagent: Billing Inquiries** (under Agentforce for Billing Employee Assistance) |
| "Agentforce Collections Agent" | **Subagent: Billing Collections Management** (under Agentforce for Billing Employee Assistance) |

Also: M1v2 doesn't mention **Agentforce for Billing Service Assistance Agent** — the customer-facing agent in Experience Cloud. That's a separate product the seller story should include because it's how the Unified Customer Record extends to *partners and end customers*, not just internal teams.

### Precision edit

M1v2 says Billing Inquiries "pulls real-time data from the Payment and Credit Memo objects." Per the 262 Help, Billing Inquiries surfaces "account balances, payment plans, upcoming payment dates, invoice details, and downloadable invoice documents." Payment data is implied via "balances" and "due dates" but Credit Memo isn't called out. Either soften the claim ("pulls real-time data from Payment, Invoice, and related billing records") or cite the Help's actual list.

### Voice flag

"Agentforce actively works on your behalf" is the **exact anthropomorphism Mike has flagged before** on Module 2 v1. Recommend replacement:

> "Billing automates the collections workflow through the **Subagent: Billing Collections Management** — combining Dunning Orchestration and refund orchestration to resolve disputes faster and reduce DSO by 20–30%."

---

## 2. "Bill Now" → "Generate Invoices" — Unit 3

### What M1v2 says

> "**'Bill Now' Functionality:** This is the manual 'override.' If a customer needs an invoice immediately — perhaps for a one-time service or a mid-month request — a user can trigger 'Bill Now' directly from the Account."

### What 262 Help actually documents

Per `ind.billing_invoice_generation_for_accounts_orders.htm`:

> "The **Generate Invoices quick action** is available by default on the Account object's page layout. To generate invoices for orders, add the quick action to the Order object's page layout. ... From the quick actions menu, click **Generate Invoices**."

The feature is called **Generate Invoices** — a quick action on Account and Order records. The button labeled "Bill Now" doesn't exist in 262.

### Substantive correction

**Edit B.** Rename "Bill Now" → **"Generate Invoices" (quick action)** throughout Unit 3:

> **"Generate Invoices" Quick Action:** This is the on-demand path for one-off or mid-month bills. From an Account or Order record, a user clicks **Generate Invoices** in the quick actions menu, selects a target date and whether to produce Draft or Posted invoices, and the system creates invoices for all eligible billing schedules. Behind the scenes this invokes the Create Invoices By Using Billing Schedules API.

---

## 3. "Billing Preview" → "Preview Invoices" — Unit 3

### What M1v2 says

> "**The Billing Preview:** Before creating an actual invoice, users can run a preview..."

### What 262 Help actually documents

Per `ind.billing_invoice_previews.htm` (titled "Preview Invoices"):

> "Preview invoices for the next two billing periods of orders, quotes, accounts, or billing schedule groups to verify order products, discounts, amendments, cancellations, and tax calculations."

The user-facing feature name is **Preview Invoices**; the programmatic surface is the **Invoice Preview API**. M1v2's "Billing Preview" is close enough to be understood but isn't the actual product name.

### Substantive correction

**Edit C.** Rename "Billing Preview" → **"Preview Invoices"** in Unit 3 and add the API surface:

> **Preview Invoices:** Before generating an actual invoice, users can preview what billing will produce for the next two billing periods of an order, quote, account, or BSG. The same logic is exposed through the **Invoice Preview API** for programmatic preview. This is the safety net for Finance teams who want to verify amendments, cancellations, and tax calculations before posting.

---

## 4. "Usage Summaries" is not a 262 object — Units 1 and 2

### What M1v2 says

- Unit 1: "Service uses the Invoice Explanation Agent to query Invoice Lines and **Usage Summaries**..."
- Unit 2 Key Takeaways: "Objects like Billing Schedule Groups and **Usage Summaries** allow businesses to handle complex, modern revenue models at scale..."

### What 262 actually has

A snapshot grep for "Usage Summaries" or "Usage Summary" returns **zero results** in the 262 Billing snapshot. The actual usage objects are documented in Unit 2 itself:

- **Usage Entitlement Account (UEA)** — customer instance of a purchased usage product
- **Usage Entitlement Bucket** — the wallet that records credits/debits
- **Usage Entitlement Entry** — the per-transaction record

These three are the 262 model. "Usage Summary" was a Subscription Management era term (pre-Revenue Cloud Billing) that doesn't survive to 262.

### Substantive correction

**Edit D.** Replace "Usage Summaries" with the correct 262 object reference in both locations:

- Unit 1: "Service uses the Subagent: Invoice Line Explanation to retrieve invoice line context, including charges tied to **Usage Entitlement Accounts and Buckets** for usage-based products."
- Unit 2 Key Takeaways: "Objects like **Billing Schedule Groups and the Usage Entitlement chain (Account → Bucket → Entry)** allow businesses to handle complex, modern revenue models at scale."

---

## 5. Billing Profile vs Billing Account naming — Unit 2

### What M1v2 says

> "An Account in Salesforce can support multiple **Billing Profiles (commonly known as Billing Accounts)**, which serve as the central source of truth for an automated billing relationship."

### What 262 Help actually documents

Per `ind.billing_billing_profiles_create.htm`:

> "Each billing profile corresponds to a billing account record."
> "Enter a name for the **billing account**."
> "On Account record pages in the Billing app, the Billing Profile related list on the Billing Profile tab has been updated in Winter '26. It now displays **Billing Accounts records**, replacing the **Account Billing Accounts** records shown in Summer '25."

So the relationship is more nuanced:

- The **SObject record** is `BillingAccount` (or possibly `BillingProfile` — both names are used interchangeably in the Help text).
- "Billing Profile" is the user-facing label / Lightning App term.
- "Billing Account" is the record-level name displayed in related lists.
- The Summer '25 → Winter '26 UI change renamed the related list from "Account Billing Accounts" to "Billing Accounts."

### Precision edit (not substantive — current phrasing is acceptable)

**Edit E (optional).** Tighten the Billing Profile / Billing Account framing:

> "An Account in Salesforce can carry multiple **Billing Profiles** (the record-level SObject is the **Billing Account**, and the two terms are used interchangeably in the Lightning App)..."

Also worth noting as a **Winter '26 enhancement** if you want to call it out: the related list was renamed from "Account Billing Accounts" to "Billing Accounts" — a UX cleanup that customers upgrading from Summer '25 may need to manually fix on customized Account pages.

---

## 6. Charge Frequency vs Charge Type conflation — Unit 1

### What M1v2 says

> "When to charge (the contract terms, **Charge Frequency including one-time, recurring, milestone, and usage-based charge types**, Start Dates, End Dates, Bill Dates)"

### Why this is misleading

In the data model:

- **Charge Frequency** = One-Time / Recurring (Monthly, Quarterly, Annual, etc.)
- **Charge Type** = One-Time / Recurring / Usage-Based / Milestone-Based

A charge can be Recurring frequency + Usage type (a monthly meter), or One-Time + Milestone (a single project milestone). Mixing frequency and type into one bullet conflates two orthogonal concepts and creates confusion later when Unit 2 introduces Usage Entitlement Buckets and Milestone Plans as separate constructs.

### Substantive correction

**Edit F.** Rewrite the Unit 1 bullet:

> "When to charge — start and end dates, billing day of month, and the combination of **Charge Frequency** (One-Time or Recurring) and **Charge Type** (One-Time, Recurring, Usage-Based, or Milestone-Based). Different combinations support different revenue patterns: monthly recurring SaaS, quarterly usage overages, one-off implementation fees, milestone-billed services contracts."

---

## 7. Statistics and marketing claims — Unit 1

M1v2 carries three statistics in the "Solve Critical Business Problems" section:

- "Many companies lose **1–5% of their earnings**..."
- "Automation reduces billing errors by **up to 50%**."
- "...reduce DSO by **20–30%**."

The 262 Billing Help snapshot doesn't ground any of these. They're either marketing-deck numbers from internal Salesforce content or industry-benchmark claims from analyst sources (Aberdeen, Forrester, etc.).

### Recommendation

These statistics are fine for a seller-enabled audience as long as they're either (a) sourced to a specific Salesforce-approved value-book or analyst study or (b) softened to qualitative claims ("typically 1–5%," "can reduce billing errors significantly," "studies show 20–30% DSO improvement"). The current draft asserts them as facts without a source. Either add citations to the Value Book / Billing Technical Enablement 2026 / analyst report, or soften the language.

---

## 8. "Tax Adapter" vs "TaxEngineAdapter" — Unit 3

### What M1v2 says

> "**Tax Adapter:** Tax is complicated and ever-changing. While RCB does have standard tax tables for simple tax use cases most customers will choose to utilize the tax adaptor. The **Tax Adaptor** allows customers to connect RCBs high scale bill run directly to the external tax engine of their choice (like Avalara or Vertex)."

### What 262 Help actually documents

Per `ind.billing_tax_configuration_prerequisites.htm`:

> "If you want to calculate standard taxes based on flat tax rates or use your own tax engine, define a custom tax adapter by extending the **TaxEngineAdapter Apex interface**."

The formal name is **TaxEngineAdapter** (an Apex interface). "Tax Adapter" / "Tax Adaptor" are informal shorthands. M1v2 uses both spellings inconsistently in the same paragraph (one "Adapter," one "Adaptor").

### Precision edit

**Edit G.** Normalize the spelling and cite the formal interface name once:

> "**Tax Adapter:** RCB ships a **Revenue Standard Tax Engine** for simple tax tables, but most customers connect to a third-party engine like Avalara or Vertex. Custom integrations extend the **TaxEngineAdapter Apex interface**. The adapter's output lands in Invoice Line Tax records linked to the corresponding Invoice Lines."

(Spelling normalized to "Adapter" throughout.)

---

## 9. "Dispute Management invocable actions" — Unit 3 Key Takeaways

### What M1v2 says

> "Agentic Upgrades: High Scale Billing, Refunds Orchestration, **Dispute Management invocable actions**, and the Spring Batch removal..."

### What 262 actually has

Per `ind.billing_manage_disputes.htm`, Billing Dispute Management uses:

- **Omniscripts** for intake forms
- **Unified Catalog** templates for service process definitions
- **Automated resolution actions** ("Resolve Case quick action that triggers automated workflows")
- A **Case Notifications** layer
- **Pre-built service process templates** (Suspend Billing, Update Bill To Contact, Extend Invoice Due Date, Incorrect Invoice Charge, Other Billing Inquiries)
- 262 enhancement: "Starting Summer '26, your service reps can also submit service requests and raise cases on behalf of the customer, directly using the Billing app."

The phrase "invocable actions" doesn't appear in the Help — though the underlying mechanism (automated resolution actions invoked from Case records) is what M1v2 is gesturing at. The phrasing isn't wrong but isn't a 262 product term.

### Precision edit (optional)

**Edit H.** Soften the term to match the Help's framing:

> "Dispute Management's automated resolution actions and the new 262 capability for service reps to raise cases on behalf of customers."

---

## 10. Unsourced / unverifiable terms — Unit 3 and Key Takeaways

These M1v2 terms don't appear in the 262 Billing snapshot:

| Term | M1v2 location | Status |
|---|---|---|
| **High Scale Billing** | Unit 3 Seller Sidebar + Key Takeaways | 0 hits in 262 snapshot |
| **Spring Batch removal** | Unit 3 Key Takeaways | 0 hits |
| **DocGen (now free of event consumption)** | Unit 3 Key Takeaways | "event consumption" doesn't appear |
| **m3ter** | Unit 2 Seller Sidebar | 0 hits (partner not in Help) |
| **National Satellite Service** | Unit 2 Seller Sidebar | Customer name — not in Help, unverifiable from this snapshot |

**Recommendation:** Either (a) Mike sources these from the Spring '26 / Summer '26 release notes or product marketing materials and we add the citation, (b) we drop them, or (c) we mark them as "release-notes claims under verification" in a footnote. They feel right for a seller-facing module but they aren't grounded in customer-facing Help docs.

### Substantive correction

**Edit I.** Pull these claims out into a "Pending source verification" section the SME can fill in, or remove them. Recommend not shipping a Trailhead module with unsourced agentic-upgrade claims (Mike's earlier feedback flagged this exact pattern).

---

## 11. Voice patterns — applies to all three units

Mike's feedback on Module 2 v1 flagged several voice patterns. M1v2 carries the same patterns:

### Anthropomorphism

- **"Agentforce actively works on your behalf"** (Unit 1) — direct anthropomorphism Mike has explicitly flagged.

### Metaphor saturation

- Opening **dominoes** metaphor stretches across two paragraphs.
- "**Risky patchwork**" for legacy systems.
- "**Digital labor**" used as a metaphor for manual data entry (3+ instances).
- "**Connective tissue**" (multiple).
- "**Shares the same DNA**" / "**Source of Truth**" / "**Change Agent**" / "**Source of Truth**" (the "Change Agent" framing for Order is unusual technical phrasing).
- "**Swivel chair**" for cross-system data entry.
- "**Leaks in the business bucket**."
- "**Pre-plan future revenue**" / "**'Closed-Won' deal**" / "**deal to a dollar**" (alliterative phrasing density).
- "**Brain**" (in graphic suggestion: Billing Schedule as the "brain").

### Soft-on-object-names

- "The Order is the 'Change Agent'" — anthropomorphizing the data model object.
- "The BSG doesn't start over — it evolves" — anthropomorphizing the BSG.
- "The Billing Schedule contains the specific details of how we bill" — "we bill" is conversational but blurs subject/object.

### Recommendation

**Edit J.** Run M1v2 through the same Trailhead AI Review Checklist pass Mike applied to M2v2. The 27-word sentence limit, the no-X-not-Y comparison ban, the modal restriction (might/could/may), and the anthropomorphism flag will catch most of these.

Recommend doing this AFTER the substantive corrections above are agreed — re-grounding the content first, then polishing the voice.

---

## 12. Open questions for Mike

1. **Agentforce product taxonomy (Section 1).** Confirm the rename from "Invoice Explanation Agent / Billing Inquiries topic / Agentforce Collections Agent" → the actual 262 subagent names. Also confirm whether Unit 1 should add the **Agentforce for Billing Service Assistance Agent** (Experience Cloud customer-facing). It feels like a meaningful Unified Customer Record proof point.

2. **"Bill Now" rename (Section 2).** Confirm the rename to "Generate Invoices quick action."

3. **"Usage Summaries" replacement (Section 4).** The Unit 2 body already documents Usage Entitlement Account / Bucket / Entry correctly. The "Usage Summaries" references in Unit 1 and Unit 2 Key Takeaways are stale — confirm replacement with the Entitlement chain.

4. **Charge Frequency vs Type (Section 6).** Confirm the rewrite to separate the two concepts.

5. **High Scale Billing / Spring Batch / DocGen event-consumption / m3ter / National Satellite Service (Section 10).** These are unsourced in the 262 Help. Mike, can you point me at the release notes / marketing materials that ground these so we can either cite them or drop them? Particularly:
   - Is "High Scale Billing" a 262 GA product, a roadmap term, or marketing-speak?
   - "Spring Batch removal" — what's the actual technical change here? Removal of the old batch APEX framework in favor of Batch Management Service?
   - "DocGen now free of event consumption" — is this a pricing/licensing change, or an infrastructure change?

6. **Voice pass (Section 11).** Want to run M1v2 through the same checklist pass M2v2 went through, in a separate iteration after these factual corrections land?

7. **Resources section.** The M1v2 Resources are link text only (no article IDs). Should we attach actual 262 article IDs the way M2v2 does — e.g.:
   - "Salesforce Help: Explore the Revenue Cloud Data Model" → ?
   - "Salesforce Help: Billing Essentials" → `ind.billing.htm` (Manage Billing in Agentforce Revenue Management)?
   - "Salesforce Help: Usage Management Essentials" → ? (not in Billing area; needs the Usage Management root article ID)

---

## 13. Recommended edit sequence

If you want to apply these in priority order:

1. **Agentforce product names** (Edit A) — substantive, factual, audience-affecting.
2. **"Bill Now" → "Generate Invoices"** (Edit B) — substantive, factual.
3. **"Billing Preview" → "Preview Invoices"** (Edit C) — substantive, factual.
4. **"Usage Summaries" → Usage Entitlement chain** (Edit D) — substantive, factual.
5. **Charge Frequency vs Type** (Edit F) — substantive, technical accuracy.
6. **Resources article IDs** (per Section 12 Q7) — pure factual.
7. **TaxEngineAdapter naming + Adapter/Adaptor spelling** (Edit G) — precision.
8. **Billing Profile / Billing Account framing** (Edit E) — optional precision.
9. **Dispute Management phrasing** (Edit H) — optional precision.
10. **Unsourced terms triage** (Edit I) — depends on Mike's input on Section 12 Q5.
11. **Voice checklist pass** (Edit J) — after factual edits land.
12. **Anthropomorphism fix** ("Agentforce actively works on your behalf") — can fold into Edit J or do immediately.

---

*All citations resolve to articles in `docs/salesforce/262/help/articles/`. Where a claim depends on project metadata rather than the snapshot, the citation says so explicitly.*
