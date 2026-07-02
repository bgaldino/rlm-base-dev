---
release_version: 260
release_name: "Spring '26"
api_version: 66.0
area: "Advanced Approvals"
document_version: 0.1
status: draft
last_updated: 2026-05-06
authors:
  - Brian Galdino
data_shape: qb
prerequisites:
  - "`cci flow run prepare_rlm_org` completed against the target org"
  - "Revenue Cloud Approvals enabled (Setup → Approval Components)"
  - "Approval flows configured (or referenced from prior-release exercise)"
sources:
  - "docs/salesforce/260/revenue-cloud-spring-26-2026-01-15.pdf — master Help compendium § Advanced Approvals (pp 887–927)"
  - "docs/salesforce/260/solution-overview-spring-26.pdf — Approvals subsection within Transaction Management"
  - "docs/salesforce/260/feature-index.md — Advanced Approvals section"
  - "docs/enablement/260/260-transaction-management-hands-on.md — Features 5 + 6 (primary home for 260 Approval features)"
  - ".cursor/skills/release-enablement/authoring-patterns.md"
---

# Revenue Cloud — Advanced Approvals

**Enablement Exercises** · Version 0.1 (draft), Spring '26

> **Branding note:** Salesforce has rebranded *Revenue Cloud* as *Agentforce Revenue Management* in Spring '26. This exercise series continues to use "Revenue Cloud" throughout 260 to match what users see in the product UI.

> **Positioning of this exercise:** Per the Revenue Cloud journey map convention, **Advanced Approvals is an "Additional Topic"** rather than a primary functional area. 260 Approval features are built on top of Transaction Management workflows, so the **primary configuration walkthroughs live in `260-transaction-management-hands-on.md` Features 5 + 6**. This exercise serves as the entry point for readers coming via the Approvals path: it summarizes 260 Approval features, surfaces carry-forward inventory from prior releases, and cross-references TM for full walkthroughs.

> Org / data shape: QuantumBit (`qb`). These exercises assume an org provisioned by `rlm-base-dev`'s `prepare_rlm_org` flow.

---

## Status of this document

🚧 **DRAFT — features verified against Spring '26 release notes, Solution Overview deck, and master Help PDF.** Most 260 Approval feature configuration is consolidated in TM Features 5 + 6. This standalone Approval doc is intentionally thin — it acts as an index and carry-forward reference, not a duplicate set of walkthroughs.

---

## Carry-forward inventory (from prior releases)

Advanced Approvals has a substantial multi-release history. Readers needing foundational Approval workflow content should reference the prior-release PDFs.

| Feature | Introduced in | Reference | 260 status |
|---|---|---|---|
| Approval Workflow Designer (foundational, end-to-end Discount Approval Workflow walkthrough) | 252 (W'25) | `docs/enablement/252/Winter '25 - Advanced Approvals Exercises.pdf` | ✅ no change — foundational, all 260 features build on top |
| Auto-launched Approval Orchestration | 252 | same | ✅ no change |
| Approval Step + Decision / Condition workflow elements | 252 | same | ✅ no change |
| Triggering Approval flow (Apex Controller / VF Page / Quote Page Submit Button) | 252 | same | ✅ no change |
| Approval Designer Access + Get Quote Record Flow | 252 | same | ✅ no change |
| **E-Mail Based Notifications and Approvals** | 254 (Sp'25) | `docs/enablement/254/Spring '25 Advanced Approvals Release Overview.pdf` | 🔄 **enhanced** in 260 — see Feature 1 (Approval Notification with Email Templates) |
| **Submitter Notifications** | 254 | same | 🔄 **enhanced** in 260 — submitter notifications now use the new email template framework |

> The 256 (Su'25) and 258 (W'26) journey maps show Advanced Approvals as Overview-only — no dedicated standalone exercise for those cycles. Approvals updates from 256/258 (if any) are documented inline within the relevant TM exercise PDFs for those releases.

---

## Upgrade Guidance from Winter '26

The master PDF "Upgrade Guidance for Spring '26" section (pp 115–117) does not include a dedicated Advanced Approvals subsection. Customers with custom Approval Flows built on the foundational 252 patterns continue to work in 260 without modification.

If you've extended the **Approval Process flow** with custom Apex actions or referenced the underlying Approval data model objects (`ApprovalSubmission`, etc.), no specific upgrade steps are documented. Validate post-upgrade.

---

## Release Overview

Spring '26 Advanced Approvals adds **two primary new features** plus two supporting workflow enhancements, all integrated with the broader Transaction Management workflow:

1. **Approval Notification with Email Templates** *(GA)* — new email templates for approver assignment + submitter status notifications
2. **Rule-Based Auto-Approvals (Smart Approvals)** *(GA)* — auto-approve pre-qualified data changes; skip re-review of unchanged data on resubmissions
3. **Override Approval Work Item** *(GA)* — Flow Core Action enabling approval admins to override decisions for any assignee
4. **Stage Exit Condition** *(GA)* — configurable exit conditions for serial/parallel approval workflows that prevent deadlocks when conditional steps don't trigger

→ **Full configuration:** `260-transaction-management-hands-on.md` § Features 5 + 6.

---

## Feature 1 (cross-area pointer): Approval Notification with Email Templates

> **Primary home:** `260-transaction-management-hands-on.md` § Feature 5.

Spring '26 introduces dedicated email templates for approval-related notifications:

- **Approval Work Item Assignment Emails** — emails sent to approvers when work items are assigned (configurable via org setting `Send Approval Work Item Assignment Emails`)
- **Approval Submission Status Email Notifications** — emails sent to submitters when approval status changes (configurable via org setting `Send Approval Submission Status Email Notifications`)

These extend the **254 E-Mail Based Notifications** capability with branded, contextual content per approval flow.

→ **Full configuration:** `260-transaction-management-hands-on.md` § Feature 5 (Approval Notification with Email Templates).

---

## Feature 2 (cross-area pointer): Rule-Based Auto-Approvals (Smart Approvals)

> **Primary home:** `260-transaction-management-hands-on.md` § Feature 6.

Smart Approvals routes requests by:

- **Auto-approving pre-qualified data changes** that match defined rules
- **Skipping re-review of unchanged data** when a record is resubmitted

When a record is resubmitted, Smart Approvals **compares new conditions against the previous submission**. If values stay within the defined range, the request skips re-approval — meaningfully reducing approval cycle time for low-risk amendments.

→ **Full configuration:** `260-transaction-management-hands-on.md` § Feature 6 (Rule-Based Auto-Approvals).

---

## Supporting Features (briefly — full detail in TM exercise)

### Override Approval Work Item

A Flow Core Action that lets approval admins **override the status of an approval work item** to reflect their decision — applicable to *any* assignee. Used to handle escalations or to programmatically resolve stalled approvals.

→ Documented in `260-transaction-management-hands-on.md` § Feature 6 (under Smart Approvals → "Setup steps").

### Stage Exit Condition

Solves the deadlock problem where serial/parallel approval workflows wait for **all steps** to finish, but **can't account for conditional steps that were never triggered**. The Stage Exit Condition lets admins configure when a stage should exit even if not all steps fired.

→ Documented in `260-transaction-management-hands-on.md` § Feature 6 (under Smart Approvals → "Setup steps").

---

## QuantumBit Approval walkthroughs (suggested)

For QB-specific scenarios using Approvals, build on the 252 foundational walkthrough (Discount Approval Workflow):

| Scenario | QB context | 260 features exercised |
|---|---|---|
| **Discount Approval — escalating thresholds** | QB Complete bundle quotes with discount > 15%, > 25% trigger different approver tiers | Carry-forward 252 base + 260 Email Templates (Feature 1) |
| **Smart Approval for resubmissions** | QB Quote with 12% discount approved → sales rep adjusts quantity by 5% (no discount change) → resubmits | 260 Smart Approvals (Feature 2) auto-approves |
| **Override stuck approval** | QB approval flow stuck due to unavailable approver | 260 Override Approval Work Item handles |
| **Multi-stage approval with conditional steps** | QB high-value quote requires Discount Approver + (conditionally) Legal Review if multi-year | 260 Stage Exit Condition prevents deadlock when conditional Legal step doesn't fire |

These walkthroughs are templates — readers configure the discount thresholds, approver tiers, and conditional rules to match their org's policies.

---

## Open questions for author / PM

1. **256 / 258 Approvals updates** — the 256 + 258 journey maps showed Advanced Approvals as Overview-only with no standalone exercise. Did those releases ship Approvals features that should be in carry-forward inventory? Spot-check Salesforce release notes for 256 + 258.
2. **Approval-specific demo URLs** — Solution Overview Approvals subsection lists the 260 features but doesn't explicitly call out a dedicated Approvals demo. Are there separate Approvals walkthrough recordings, or only TM-embedded ones?
3. **Smart Approval scope** — confirm whether Smart Approvals applies to all Approval flow types (Autolaunched, Record-Triggered, Approval Process from Setup) or specific subsets.
4. **Migration from legacy Approval Process** — customers using legacy Salesforce Approval Process (pre-Flow Approvals) — should the 260 exercise include a brief migration callout? Likely no — that's an implementation-level concern, not a 260 feature.
5. **Approvals + DRO compatibility** — DRO Custom Logic Hook (Feature 3 in DRO exercise) can invoke Approval workflows during fulfillment. Worth a cross-area pointer here, or is that captured sufficiently in DRO?
6. **Approvals + Salesforce Contracts (262 forward-look)** — 262 introduces "Advanced Approvals for Contracts" as a *new* capability. 260 readers may not need this called out, but it's worth noting that the same Approval framework will extend to Contracts in 262.

---

## Forward-look: 262 (Summer '26)

The 262 preview shows two Approvals enhancements:

- **Slack Approvals (Accelerated Deal Approvals in Slack)** — execute Advanced Approvals from Slack directly + new Preview UX
- **Advanced Approvals for Contracts** — multi-stakeholder serial-approval workflows extended to Contracts

→ **Preview detail:** `docs/salesforce/262/feature-index.md` § Transaction Management.

These are NOT 260 features — included here as forward-look context for 260 readers planning multi-release Approval roadmaps.

---

## Footer (rendered at end of distribution PDF)

© Copyright 2000–2026 Salesforce, Inc. All rights reserved. Salesforce is a registered trademark of Salesforce, Inc., as are other names and marks.
