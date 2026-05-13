# Mike's Comments on Module 3 v2 — Response Plan

**Date captured:** 2026-05-12 (Google Docs ID `1HR4YwZIKg5sVIEfxcoUU-dPrGAWiSOPqP5vBHoTiW5M`)
**Comments + suggestions captured:** 26
**Status (2026-05-13):** Group A high-confidence items #1, #2, #3, #5, #7, #9, #12+13 applied to `module-3-v2.md`. Group A items #8 (Rating Discovery scope — applied strict reading) and #11 (Usage Overage Policy existence) plus Group B open questions still pending Mike's clarification.

**Re-validation pass (2026-05-13, late):** Re-pulled the Google Doc state via DOM probe of the comment sidebar. Found that **all 15 of Mike's standalone track-change suggestions are marked "Suggestion was deleted"** — meaning Brian has processed each one in the doc. Also surfaced **three NEW comments** that came in after the initial capture (timestamps 12:33 PM, 12:39 PM, 12:41 PM Today):

* **NEW #14 (12:33 PM):** "The bucket structure tracks the overall balance and the in period balance. Roll overs appear as Usage Entitlement Entries in that bucket. This needs to be rewritten to be clear." — Mike's mental-model correction on the bucket section. My v2 paragraph (treating child buckets as separate per-grant containers) misrepresents the structure. **Applied 2026-05-13.**
* **NEW #15 (12:39 PM):** "This is really called the Digital Wallet. It shows what resources are accessible, how much is included, and how much is left. It allows customers to drill down into each resource and see the actual debits and credits being made. Can we rewrite it" — Customer-facing UI naming correction. The "Unified Usage Dashboard" terminology should reframe around **Digital Wallet** for seller content. **Applied 2026-05-13.**
* **NEW #16 (12:41 PM):** "See my edits to that area" — Mike pointed Brian at inline track-change suggestions, all of which were accepted (the suggestion bubbles are marked "Suggestion was deleted"). The Google Docs editor is canvas-rendered, so the current accepted body text cannot be extracted via DOM. **Action: Brian to confirm M3v2.md matches the doc's current body, OR share the body via another path (export to .docx, copy/paste into a scratch file, etc.).**

## Group A — Applied (2026-05-13)

| # | Change | Where applied |
|---|---|---|
| 1 | UEA credit-card-in-wallet metaphor | Unit 1 → "Define the Usage Data Model Objects" UEA/Bucket/Entry bullets + Seller Sidebar |
| 2 | UOM / UOM Class as binding-target grouping mechanism | Unit 1 → "Understand the Binding Mechanism" new paragraph |
| 3 | 5-field usage record list → Mike's 9-field list (Account, Activity Date, Status, Quantity, Start Date, End Date, Reference Record, Usage Resource, Quantity Unit) | Unit 2 → "Identify the Required Fields on a Usage Record" |
| 5 | Rating Frequency Policy framing (admin configures *when* it runs, monthly/daily, or on-demand) | Unit 2 → "Map the Pipeline" closing paragraph |
| 7 | Rewrote Rating Procedure section procedurally (5-step execution walkthrough). Section retitled "Describe How Rating Procedures Calculate the Net Rate." LO 2.3 updated to match. Quiz updated to test procedural framing. | Unit 2 → renamed section + LO + quiz |
| 8 (strict) | Dropped Rating Discovery Procedures from Module 3 (strict reading — keep Rating Procedures, drop Rating Discovery). Flagged for Mike confirmation. | Unit 2 → removed Rating Discovery bullet + Key Takeaways sentence |
| 9 | Swept body for version notations. Removed "262" from agent-naming note and from "two other 262 features" line. Style note in header retained (it documents the evergreen rule itself). | Unit 3 |
| 12+13 | Drawdown + Rollover rewrite: new lead-up ("You might think that the rating story resets each billing period — that's not the case."), "grant" terminology replaces "bucket" throughout the policy descriptions, question-pair framing returns at end. Key Takeaways + quiz aligned to grant terminology. | Unit 3 → "Apply Drawdown Policies and Rollover Policies" |

**Note on #8:** Applied strict reading per the recommended interpretation. Open follow-up to Mike still pending: confirm whether dropping Rating Discovery Procedures is what he meant, or whether he meant something broader about usage pricing at quote time.

## Group A — Held pending Mike clarification

| # | Item | Status |
|---|---|---|
| 11 | Remove Usage Overage Policy references (Mike: "no longer exist") | **HELD.** Current 262 snapshot has dedicated article `ind.um_create_usage_overage_policy.htm` and 7+ references. Body currently retains the Usage Overage Policy callout in Unit 3. Will remove after Mike confirms it's deprecated. |

---

## Substantive content corrections

### Unit 1: Data Model

**1. UEA metaphor — rewrite.**
- Mike: "The UEA is more like a credit card in your wallet. Each card has a balance, it gets credits, refunds and charges. Can we rewrite?"
- Brian: "agree - will revise"
- **Action:** Reframe the UEA description from "the customer instance of a purchased usage product" to a credit-card-in-a-wallet framing. Each UEA is a "card" with its own balance, credits, refunds, charges. The Bucket structure inside the UEA holds the actual balance.

**2. Add UOM / UOM Class content.**
- Mike: "Need to say more about the UOM and how that UOM and UOM Class help group like Usage Resources together on the same binding target."
- Brian: "agree"
- **Action:** Add a paragraph (or expand the Usage Resource bullet) explaining how Unit of Measure (UOM) and UOM Class group like Usage Resources together on the same binding target. Currently the body only mentions UOM as a field on the usage record entering the Transaction Journal — not as a grouping mechanism for binding.

### Unit 2: Pipeline + Rating

**3. Required usage record fields — CORRECTION (current content is wrong).**
- Mike: "This is incorrect. What your showing is the old billing system. The new system requires these fields. Account, Activity Date, Status, Quantity, Start Date, Reference Record, Usage Resource, Quantity Unit, End Date"
- Brian: "right - not sure where this info came from. Will have it revise."
- **Action:** Replace the current 5-field list (External ID, Timestamp, Quantity, Unit of Measure, Matching Attribute) with Mike's verified 9-field list. The current content reflects the old Subscription Management / pre-RCB usage model, not the current one. Source for new fields: Mike (will verify against 262 snapshot during edit).

**4. Summary types — confirmed.**
- Mike: "I think this is wrong. confirming"
- Brian: "i think this is right? the liable summary is the charges - the usage summary is the aggregate usage per period"
- **Action:** This thread resolved itself — Brian's framing held. The Liable Summary is the charges; the Usage Summary is aggregate usage per period; the Usage Ratable Summary is the rated version between them. No change needed.

**5. Orchestrate Usage Management flow cadence.**
- Mike: "The admin can run the flow at any time. Also it can run once a month but also daily as defined under the Rating Frequency Policy"
- Brian: "ok but they don't need to write the orchestration - they just need to determine when it is to be run"
- **Action:** Update the body to clarify: admin doesn't *author* the orchestration, they configure *when it runs* via the **Rating Frequency Policy** (monthly or daily) and can also trigger it on-demand. Currently the body says "The admin doesn't write the orchestration manually. The admin schedules the flow to run on the cadence the customer's billing cycle requires." — close but missing the Rating Frequency Policy explicitly.

**6. Context Service + Data Processing Engine.**
- Mike: "I think it would make more sense to cover the context service and the Data Processing Engine here"
- Brian: "would it make sense to go into those details or to punch out to the existing trails on context service and DPE and just discuss the application of those concepts here?"
- **Status: OPEN.** Brian's follow-up question pending Mike's reply. Two paths:
  - (a) Deep dive into Context Service + DPE in Module 3 prose.
  - (b) Link out to existing Trailhead trails on Context Service + DPE; cover only the *application* in Module 3 (how rating uses them).
- **Recommended:** Wait for Mike's reply on Brian's follow-up.

**7. Rating procedure description — be more procedural.**
- Mike: "Instead of listing what is included describe how the procedure and elements work"
- **Action:** Rewrite the Rating Procedure section to walk through *how* the procedure executes (ordered stack of rating elements, each element calls a lookup table, the final result is the net rate) rather than listing what's in a procedure. Use a worked example if possible — anchor product rate → adjustment band → net rate.

**8. Rating Discovery Procedures — REMOVE from Module 3.**
- Mike: "Rating Discovery procedures are quoting related and have nothing to do with billing. Please Remove"
- Brian: "ok so exclude completely how usage pricing is determined?"
- **Status: PARTIALLY OPEN.** Mike clearly wants Rating Discovery Procedures out of Module 3. Brian's follow-up asks whether that means dropping usage pricing entirely from the module. Two interpretations:
  - **Strict reading:** Mike's "Rating Discovery procedures are quoting related" means just the discovery procedures — Module 3 keeps Rating Procedures (which DO calculate billing rates) but drops the Discovery Procedures (which are about quote-time rate lookup). This is the likely correct reading.
  - **Broader reading:** If Mike means "the entire usage-pricing-at-quote-time story belongs in another module," then Module 3 LO 2.3 needs reshaping.
- **Recommended action:** Apply the strict reading (drop Rating Discovery Procedures only, keep Rating Procedures). Note the follow-up for Mike to confirm.

**9. "Remove release details."**
- Mike: "remove release details"
- **Action:** Apply the evergreen rule wherever a release reference remains. Need to scan M3v2 for any version notations that slipped through.

**10. "They are wrong" — unclear anchor.**
- Mike: "They are wrong"
- **Status: NEEDS ANCHOR CHECK.** Without DOM-level anchoring, can't be sure what Mike's referring to. Most likely candidate: the procedure-type names (Default Rating Procedure / Negotiable Rating Procedure) given the proximity to comment #8 and #11. Will check the Drawdown section context once edits land.

**11. Usage Overage Policy — delete the callout.**
- Mike: "Delete: 'Usage Overage Policy — the governance object. Defines whether overage on a usage resource is chargea…'"
- Mike (separately): "This no longer exist"
- **Action:** Remove the Usage Overage Policy from M3v2. This was referenced in LO 3.1 + body content for Unit 3. The 262 Help portal has an article on creating Usage Overage Policies (`ind.um_create_usage_overage_policy.htm`), but Mike says this no longer exists. Need to verify against the latest snapshot — the article may have been deprecated since my earlier capture.

### Unit 3: Drawdown + Rollover section — major rewrite

**12. "Can we add some lead up here?"** — Mike wants more transition before the policy types.

**13. Track-change suggestions on the Drawdown/Rollover section:**
- Replace "T" with the lead-up text: "You might think that the rating story resets each billing period however this isnt the case. In fact..."
- Replace "types govern" with "types that govern"
- Delete: "Drawdown Policy controls which bucket gets debited when a customer consumes a resource that has multiple buckets available..."
- Add: "As you would expect the grant of new usage resource capacity and the rollover of remaining resource..."
- Replace existing "Together, Drawdown and Rollover answer two distinct customer questions..." opening with a revised Drawdown Policy definition that uses "grant" instead of "bucket"
- Re-add: "Together, Drawdown and Rollover answer two distinct customer questions..."

**Terminology shift Mike wants:** "Drawdown Policy controls which **grant** gets debited" (not "which **bucket**"). Subtle but matters — Grant is the abstract entitlement; Bucket is the wallet that holds the grant.

**Action:** Rewrite the Drawdown + Rollover section per Mike's structure:

1. Lead-up sentence: "You might think that the rating story resets each billing period — that's not the case."
2. "As you would expect, the grant of new usage resource capacity and the rollover of remaining resources from one period to the next happens automatically. Two policy types govern this behavior, both attached to the Transaction Usage Entitlement record at order activation, applied automatically by Consumption Management."
3. "**Drawdown Policy** controls which **grant** gets debited when a customer consumes a resource with multiple grants available." (Note: grant, not bucket.)
4. "**Rollover Policy** controls what happens to unused units when a billing period ends."
5. The Drawdown Order three values (Expiring First / Granted First / Granted Last) stay.
6. The two-question framing returns at the end: "Drawdown and Rollover answer two distinct customer questions..."

## What's not in this comment set

Mike's comments cover Units 1 and 2 + part of Unit 3 (Drawdown section). He didn't comment on:
- The Consumption Management subagent section in Unit 3 (LO 3.1)
- The Unified Usage Dashboard section
- The m3ter extension section
- Unit 3 Key Takeaways
- Resources
- Quiz

So those sections stay as-is for this revision pass.

## Recommended action plan

**Group A — Apply immediately (clear corrections):**

| Mike's # | Change |
|---|---|
| 1 | UEA credit-card-in-wallet metaphor rewrite |
| 2 | Add UOM / UOM Class grouping content |
| 3 | Replace 5-field usage record list with Mike's 9-field list |
| 5 | Add Rating Frequency Policy framing to the orchestration flow |
| 7 | Rewrite Rating Procedure section to describe *how* (procedural) instead of *what* (feature list) |
| 8 | Drop Rating Discovery Procedures from Module 3 (apply strict reading) |
| 9 | Sweep for any version notations and remove |
| 11 | Remove Usage Overage Policy references (verify Mike's "no longer exist" claim against snapshot) |
| 12 + 13 | Rewrite Drawdown + Rollover section per Mike's structure, using "grant" not "bucket" |

**Group B — Open questions for Mike:**

| # | Question |
|---|---|
| 6 | Context Service + DPE deep dive vs. link-out + applications-only? (Brian's follow-up to Mike) |
| 8 | If "Rating Discovery Procedures" means dropping ALL usage pricing from Module 3, LO 2.3 needs restructuring. Otherwise just drop the Discovery callout. (Brian's follow-up to Mike) |
| 10 | What does "They are wrong" refer to? Need anchor check. |
| 11 | Verify against snapshot: does Usage Overage Policy still exist? (Mike says no longer exist; current Help snapshot has it.) |

---

*Comments captured 2026-05-12 from `https://docs.google.com/document/d/1HR4YwZIKg5sVIEfxcoUU-dPrGAWiSOPqP5vBHoTiW5M/edit`.*
