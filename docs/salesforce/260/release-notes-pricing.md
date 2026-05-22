# Spring '26 Salesforce Pricing — Release Notes

> **Source attribution and limited-use note.** This file is a captured snapshot of publicly-readable Salesforce Help release-note content (URL below). © Salesforce, Inc. The content is reproduced here **solely to ground AI agents authoring internal enablement material in this repository** against the exact phrasing of the published release notes. It is **not** intended as a redistribution of, or substitute for, the canonical published release notes. Readers and downstream tooling should treat the **source URL** as the system of record. If any wording diverges from the live page (Salesforce periodically edits release notes after GA), the live page wins. Do not re-publish this file's body text outside this repository's internal-grounding workflow without confirming Salesforce's redistribution terms.
>
> The same posture applies to the per-article Help snapshot under `docs/salesforce/{release}/help/articles/` — see `.cursor/skills/revenue-cloud-docs/SKILL.md` for the broader policy.

**Source:** https://help.salesforce.com/s/articleView?id=release-notes.rn_salesforce_pricing.htm&release=260&type=5
**Captured:** 2026-05-06 (via Chrome MCP)
**Release:** Spring '26 / 260 / API v66.0

> **Major naming change at the suite level:** Revenue Cloud is now branded **Agentforce Revenue Management**. Documentation and product references are transitioning. The Help portal still uses both names interchangeably during the transition.

## Summary

> Define pricing rules across complex, multi-level quotes by using conditional ascending propagation and cross-field horizontal calculations. Simplify pricing logic with conditional IF statements. Accelerate debugging by using auto-numbered steps and element descriptions in the now-renamed Revenue Cloud Operations Console. Improve troubleshooting accuracy with Advanced Price Log Settings and seamlessly deploy entire pricing workflow structures by packaging procedure plans.

## New features in Spring '26

### 1. Streamline Complex Quote Calculations with Smarter Price Propagation

Manage complex, multi-level quotes by defining formulas that calculate and propagate discounts and totals throughout the quote hierarchy. Simplify pricing configuration for complex quote structures with up to 5 levels of nesting. Build consistent pricing flows by using ascending propagation to conditionally roll up totals and discounts to the parent level. Use horizontal calculations to compute values based on other fields within the same quote line or group.

### 2. Package Your Pricing Workflow Seamlessly

Migrate entire pricing solutions across Salesforce orgs by adding procedure plans directly to your deployment package. Transfer the complete execution flow of pricing and discovery procedures to reduce manual setup effort. Deploy your validated pricing workflow with speed and accuracy to ensure immediate consistency in every target org.

### 3. Troubleshoot Pricing Elements with Advanced Price Log Settings

Use Advanced Price Log Settings to collect detailed diagnostic data for complex pricing elements. The logs capture exception details for elements such as Attribute-Based Price, Derived Price, and other logic-heavy elements. Enables troubleshooting and performance analysis so admins can identify the root cause of issues.

### 4. Build Pricing Logic with Conditional IF Statements

Solve complex pricing scenarios by using conditional IF statements and nested logic directly within the Formula-Based Pricing element. Pricing designers can now replicate complex business logic — such as intricate calculations for product pricing using basis points, or advanced logic for promotional discounts — without relying on custom code. This enhancement optimizes procedure readability and accelerates debugging.

### 5. Accelerate Debugging of Pricing Flows

Use auto-numbered steps and element descriptions in a pricing procedure to improve readability and provide a clear visual map of the execution path in the Pricing Operations Console. The numbering automatically adjusts when elements are added or moved, reducing manual effort and supporting faster, more accurate troubleshooting across pricing procedures.

### 6. Pricing Operations Console Is Now Revenue Cloud Operations Console

To better align with the data it presents, the **Pricing Operations Console** is now renamed to **Revenue Cloud Operations Console**. This change does not affect the console's underlying functionality.

## Related — Spring '26 upgrade guidance for Pricing

**From `revenue-cloud-spring-26-2026-01-15.pdf` upgrade guidance section:**

### Limitation with Price Propagation Element

Intermittent Pricing API failures can occur when using Price Propagation and Pricing Setting elements together. When the Pricing API runs a procedure that includes only the Pricing Setting and Price Propagation elements (configured without a change set, with context reuse disabled), the process may fail at the Context Layer with `ClassCastException: CacheableDataColumn cannot be cast to CacheableMetaColumn`. **Workaround:** retry the pricing request.

### Related Transaction Management notes that affect Pricing

- **Instant Pricing API returns additional records for ARC use cases** — when invoked headlessly with API v66.0, the response can include cancellation lines, ARC breakdown lines, ARC detail lines, and quote summary fields not returned in earlier API versions. Integrations that depend on the previous response structure should not upgrade the API version.
- **Canceling derived pricing products results in incorrect net total price** — known issue, no current workaround.

## Cross-area features that touch Pricing

From the Revenue Management overview release notes (same release):

- **Promotions in Agentforce Revenue Management (Beta)** — Pricing designers can set up promotions that users apply to transactions. Developers can use objects and APIs to manage promotions on sales transactions. *(Note: matches the commit hint `f2b8aa59 enhanced pricing procedure with promotions` in `rlm-base-dev`.)*

## Action items implied by these notes

1. Adopt the new "Agentforce Revenue Management" branding in the 260 enablement exercise — but cross-reference with current product UI strings before changing every label.
2. The Pricing Operations Console rename → Revenue Cloud Operations Console requires updating every screenshot and every step that says "navigate to Pricing Operations Console".
3. The Promotions Beta is worth explicit handling — the exercise should call out it's Beta, what's available, and what isn't yet.
4. Conditional ascending propagation, horizontal calculations, and conditional IF statements are all interconnected — they may belong in one umbrella section ("Smarter Pricing Procedures") rather than three separate features.
