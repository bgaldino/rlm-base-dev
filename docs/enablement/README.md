# Revenue Cloud Enablement Catalog

Hands-on enablement exercises for Salesforce Revenue Cloud (Agentforce Revenue Management), maintained as part of the `rlm-base-dev` project so the materials stay aligned with the org-build automation.

> **Audience for this README:** colleagues reviewing the enablement catalog. Reading this in full takes ~10 minutes and gives you enough context to start reviewing any individual exercise. If you're an authoring agent (Cursor, Claude, etc.) instead, your entry point is [`.cursor/skills/release-enablement/SKILL.md`](../../.cursor/skills/release-enablement/SKILL.md) — read that, not this.

---

## TL;DR for reviewers

- We're building a **two-tier enablement catalog**: a **master / living** set for in-person workshops + per-release **delta extracts** for "what's new in 260" / "what's new in 262" reading
- All exercises anchor to a **single workshop scenario** — Infinitech (US, Technology) consolidates cloud infrastructure on QuantumBit, configuring **QB-COMPLETE** software bundles + **QB-QRack-750** hardware servers
- **2 master exercises drafted** (PCM, Pricing) · **10 per-release 260 drafts complete** · **262 QB demo script drafted** (`docs/enablement/262/qb-demo-script.md`) · **Master Configurator + Transaction Mgmt + 6 more areas pending** · **262 per-area extracts pending** (deferred until master coverage broadens)
- Standing customer accounts (Infinitech, Global Media) come from `scratch_data`; channel partner (Robot Resellers) comes from `qb-prm`; everything else from the QB data plans
- All content is **markdown source**; rendered PDFs/Word for distribution come later
- **Salesforce Help grounding for 262** uses the per-article markdown snapshot at `docs/salesforce/262/help/` (838 articles) — replaces the old per-release master Help PDFs
- **Where to start your review** depends on your role — see [Reading paths by reviewer role](#reading-paths-by-reviewer-role) below

> **Branch context:** This catalog is landing on the `262` branch. On 262, 260 is the **prior GA reference** and 262 (Summer '26) is the **current development cycle**. The 262 feature index is populated at [`../salesforce/262/feature-index.md`](../salesforce/262/feature-index.md) and the Help-portal snapshot lives at [`../salesforce/262/help/`](../salesforce/262/help/) (838 articles, replaces the prior per-release master Help PDFs). The `docs/enablement/262/` directory now contains the **262 QB demo script** ([`262/qb-demo-script.md`](262/qb-demo-script.md), generated 2026-05-24 via the [`qb-demo-script` SKILL](../../.cursor/skills/qb-demo-script/SKILL.md)); 262 per-area Hands-On extracts are still pending and will be derived from master coverage as it broadens.

---

## Why two-tier?

The catalog has two artifact types because they serve different audiences:

### Master exercises (`master/`)

Living, workshop-format exercises that progress through a Revenue Cloud area in a logical narrative arc. Foundational and release-specific content lives together. **Used during in-person enablement sessions** — instructors walk attendees from "what is Pricing?" through advanced features in one continuous story.

Each section in a master exercise carries version-aware metadata (`introduced`, `available`, `enhanced_in`) so the structure auto-derives release-specific extracts.

### Per-release extracts (`260/`, `262/`)

Filtered views of the master, scoped to net-new and enhanced features for a specific release. **Used by sellers / SEs / customers** who already know the prior cycle and want only the delta. Currently maintained manually; eventual auto-gen will derive them mechanically from master frontmatter.

The per-release directories also host **release-specific SE/partner artifacts** that aren't filtered views of master — currently the QB demo script ([`262/qb-demo-script.md`](262/qb-demo-script.md)). These have their own authoring SKILL (`.cursor/skills/qb-demo-script/`) and ground on the same QB scenario reference as the master exercises.

> **Why not just one document?** The same text serves these two audiences poorly. A workshop attendee learning Pricing for the first time needs foundational concepts (price books, procedures, selling models) **before** they hit "what's new in 260." A seller pitching 260 to an existing customer wants only the delta. Forcing both into one document means each audience reads through content they don't need.

---

## The workshop scenario — Infinitech

Every walkthrough in every exercise anchors to a single deal narrative:

> **Infinitech consolidates cloud infrastructure on QuantumBit, with QB-COMPLETE software bundles and QB-QRack-750 server racks across multiple environments (Pre-Prod, Prod, Gov). Robot Resellers (partner channel) facilitates the deal. Optional secondary customer Global Media provides multi-account walkthroughs.**

This scenario was deliberately chosen because:

- The customers ([Infinitech, Global Media](../../datasets/sfdmu/scratch_data/Account.csv)) and partner ([Robot Resellers](../../datasets/sfdmu/qb/en-US/qb-prm/Account.csv)) are already loaded by `prepare_rlm_org` — no new data plans required
- The bundles ([QB-COMPLETE](../../datasets/sfdmu/qb/en-US/qb-pcm/Product2.csv), [QB-QRack-750](../../datasets/sfdmu/qb/en-US/qb-pcm/ProductComponentGroup.csv)) exercise the **complete spectrum of Revenue Cloud capabilities** — bundle/attribute/volume pricing, CML constraint rules (QuantumBitComplete + Server2), nested component groups, multi-LE billing, usage products, ramp deals
- The deal naturally crosses every functional area: PCM (catalog) → Pricing (rates) → Configurator (rules) → Transaction Mgmt (quote) → Approvals (high-value review) → DRO (multi-location fulfillment) → Usage Mgmt (consumption) → Invoice/Billing (per-LE invoices)

For the canonical reference of what's in QB orgs by default — including bundle structure, CML constraint models, pricing-feature wiring, usage products, multi-LE setup — read **[`master/qb-scenario-reference.md`](master/qb-scenario-reference.md)**. That's the foundational document every other exercise builds on.

---

## Directory map

| Path | What's there | Status |
|---|---|---|
| **[`master/`](master/)** | The two-tier model's source of truth — master exercises + scenario reference | 🚧 **Pilot** (PCM + Pricing drafted; 8 areas pending) |
| **[`260/`](260/)** | Per-release extracts for 260 (Spring '26, prior GA reference on the 262 branch) | ✅ All 10 area drafts complete |
| **[`262/`](262/)** | Per-release artifacts for 262 (Summer '26, current development cycle on the 262 branch) | 🚧 QB demo script drafted ([`qb-demo-script.md`](262/qb-demo-script.md)); 10 per-area Hands-On extracts pending |
| `248/`, `252/`, `254/`, `256/`, `258/` *(not in repo)* | **Read-only historical labels** — used in exercise files to point at prior published exercise PDFs (e.g. ``docs/enablement/258/Salesforce Pricing - Winter '26 Revenue Cloud - External.pdf``). The PDFs themselves live outside git (see the *External dependencies* table below); these path labels exist only as textual references in carry-forward sections. | Frozen labels. Never created in-repo. |
| **[`coverage-matrix.md`](coverage-matrix.md)** | Cross-release inventory of what's drafted where | Keep current as drafts complete |
| **[`_template/`](_template/)** | Per-release-extract scaffold template | Stable |

The historical PDFs (248–258) are not in git but are referenced by `docs/enablement/{release}/{filename}.pdf` path labels in carry-forward sections of master exercises and the 260 per-area extracts. Those labels are intentionally non-clickable — they identify the source PDF, not a real directory in this checkout. If you need the PDFs for review, they were uploaded earlier in the authoring process — contact Brian.

External dependencies (also gitignored / external):

| Path | What | Status |
|---|---|---|
| `docs/salesforce/260/revenue-cloud-spring-26-2026-01-15.pdf` | Master Help compendium for 260 (Spring '26), 1,460 pages | Public from help.salesforce.com but 130 MB — not in repo |
| `docs/salesforce/260/solution-overview-spring-26.pdf` | Internal Solution Overview deck for 260 (RCA) | **CONFIDENTIAL — Internal Only**. Not in repo. |
| `docs/salesforce/260/solution-overview-spring-26-billing.pdf` | Internal Solution Overview deck for 260 (RCB) | **CONFIDENTIAL — Internal Only**. Not in repo. |
| `docs/salesforce/262/*.pdf` | Equivalent 262 sources (RCA + Billing SOs, release notes) | Same status — not in repo |

The markdown content in [`docs/salesforce/260/feature-index.md`](../salesforce/260/feature-index.md) and [`docs/salesforce/262/feature-index.md`](../salesforce/262/feature-index.md) summarizes what's in those sources, so you can review without needing the raw PDFs.

---

## Reading paths by reviewer role

Pick the path that matches your role. Each path takes 30–90 minutes for a reasonable first-pass review.

### 📚 Workshop instructor / SE running an enablement session

You'll lead an in-person workshop using these materials. Goals: confirm the narrative arc works for a live audience, the QB anchors are accurate, the workshop synthesis exercises are runnable in your own org.

1. Read **[`master/qb-scenario-reference.md`](master/qb-scenario-reference.md)** — the canonical QB scenario reference (~25 minutes)
2. Read **[`master/01-product-catalog-management.md`](master/01-product-catalog-management.md)** — Part 1 of the workshop (~30 minutes)
3. Read **[`master/02-salesforce-pricing.md`](master/02-salesforce-pricing.md)** — Part 2 of the workshop (~30 minutes)
4. Walk through the synthesis exercises at the end of each in a real org. Note any QB data references that don't match what you see.

**Feedback I want from you:**

- Does the narrative arc work for live teaching?
- Do the QB walkthroughs match what's actually in your QB org?
- Are the synthesis capstones the right scope (4–6 hours each)?
- What sections need full step-by-step walkthroughs that currently say "see prior-release PDF"?

### 🧠 PM / Product owner reviewing accuracy

Your goal: confirm the feature descriptions, version metadata, and behavior claims are accurate.

1. Skim **[`master/qb-scenario-reference.md`](master/qb-scenario-reference.md)** Section 7 (CML Constraint Models) and the Pricing-feature mapping in Section 3
2. Review **[`docs/salesforce/260/feature-index.md`](../salesforce/260/feature-index.md)** — every 260 feature, with my interpretation of customer need / solution / use case. Flag anything I got wrong.
3. Review **[`docs/salesforce/262/feature-index.md`](../salesforce/262/feature-index.md)** — same for 262 preview.
4. Spot-check a feature in **[`master/02-salesforce-pricing.md`](master/02-salesforce-pricing.md)** to verify the version metadata (e.g., "introduced: 256 · enhanced_in: [260]") matches your knowledge.

**Feedback I want from you:**

- Any feature where the `introduced` version is wrong?
- Any feature where the description misses key context?
- Any 260 or 262 feature that I missed entirely or shouldn't have included?
- Solution Overview deck content that I summarized incorrectly?

### 🛠️ Implementation / SI reviewing technical correctness

Your goal: confirm the technical walkthroughs work — that the configuration steps are real, the QB references are accurate, the constraint models behave as described.

1. Read **[`master/qb-scenario-reference.md`](master/qb-scenario-reference.md)** end to end
2. Read **[`master/02-salesforce-pricing.md`](master/02-salesforce-pricing.md)** § 5–8 (Volume / Bundle / Attribute / Derived adjustments) and § 15–16 (Price Propagation)
3. Read **[`master/01-product-catalog-management.md`](master/01-product-catalog-management.md)** § 8–11 (Bundles, Component Groups, Constraint Rules)
4. Spot-check by running through a walkthrough in a 260 org

**Feedback I want from you:**

- Configuration steps that don't quite work, or are missing prerequisites
- QB record references (SKUs, classifications, attribute codes) that don't match your org
- Known issues / workarounds I should call out that aren't currently surfaced
- Constraint behavior on QB-COMPLETE or QB-QRack-750 that I described inaccurately

### 🎯 Sales / SE reviewing for customer-readiness

Your goal: confirm the materials work for customer enablement (or could, after polish). Identify what's confidential, what's external-friendly, what tone changes are needed.

1. Skim the [`master/`](master/) folder for tone and approach
2. Spot-check 2–3 sections in either master file for content you'd be comfortable reading aloud to a customer
3. Look at **[`260/`](260/)** to see how the per-release-delta extracts read

**Feedback I want from you:**

- Anything currently in the markdown that should NOT go to customers (internal jargon, preview-only feature claims, branding mismatches)
- Tone adjustments that would make this customer-ready vs internal-only
- Whether "Agentforce Revenue Management" branding should propagate to these exercises now, or stay "Revenue Cloud" until product UI catches up

### 🤖 Authoring agent (you don't need this README)

Read [`.cursor/skills/release-enablement/SKILL.md`](../../.cursor/skills/release-enablement/SKILL.md) and [`authoring-patterns.md`](../../.cursor/skills/release-enablement/authoring-patterns.md). Those are the entry points for any agent — Claude, Cursor, etc. — that's authoring or maintaining exercises. The skills tell you how to work; the QB Scenario Reference tells you what to anchor walkthroughs to.

---

## Current draft status

### Master exercises (`master/`)

| File | Status | Sections | Drafted by | Last updated |
|---|---|---|---|---|
| [`qb-scenario-reference.md`](master/qb-scenario-reference.md) | ✅ Foundation | 16 sections | Brian + Claude | 2026-05-06 |
| [`01-product-catalog-management.md`](master/01-product-catalog-management.md) | 🚧 Draft v0.1 | 30 sections | Claude pilot | 2026-05-06 |
| [`02-salesforce-pricing.md`](master/02-salesforce-pricing.md) | 🚧 Draft v0.1 | 25 sections | Claude pilot | 2026-05-06 |
| `03-product-configurator.md` | ⏳ Pending | — | — | — |
| `04-transaction-management.md` | ⏳ Pending | — | — | — |
| `05-advanced-approval.md` | ⏳ Pending | — | — | — |
| `06-dynamic-revenue-orchestration.md` | ⏳ Pending | — | — | — |
| `07-usage-management.md` | ⏳ Pending | — | — | — |
| `08-invoice-management.md` | ⏳ Pending | — | — | — |
| `09-revenue-cloud-billing.md` | ⏳ Pending | — | — | — |
| `10-context-service.md` | ⏳ Pending | — | — | — |

### Per-release 260 extracts (`260/`)

All 10 functional areas drafted. Currently authored manually pending the auto-gen. Once the master set is complete and signed off, the 260 directory will be regenerated mechanically from master frontmatter.

| File | Status |
|---|---|
| [`260/260-product-catalog-management-hands-on.md`](260/260-product-catalog-management-hands-on.md) | 🚧 Draft v0.2 |
| [`260/260-salesforce-pricing-hands-on.md`](260/260-salesforce-pricing-hands-on.md) | 🚧 Draft v0.5 |
| [`260/260-product-configurator-hands-on.md`](260/260-product-configurator-hands-on.md) | 🚧 Draft v0.1 |
| [`260/260-transaction-management-hands-on.md`](260/260-transaction-management-hands-on.md) | 🚧 Draft v0.3 |
| [`260/260-advanced-approval-hands-on.md`](260/260-advanced-approval-hands-on.md) | 🚧 Draft v0.1 |
| [`260/260-dynamic-revenue-orchestration-hands-on.md`](260/260-dynamic-revenue-orchestration-hands-on.md) | 🚧 Draft v0.1 |
| [`260/260-usage-management-hands-on.md`](260/260-usage-management-hands-on.md) | 🚧 Draft v0.1 |
| [`260/260-invoice-management-hands-on.md`](260/260-invoice-management-hands-on.md) | 🚧 Draft v0.1 |
| [`260/260-revenue-cloud-billing-hands-on.md`](260/260-revenue-cloud-billing-hands-on.md) | 🚧 Draft v0.1 |
| [`260/260-context-service-hands-on.md`](260/260-context-service-hands-on.md) | 🚧 Draft v0.1 |

### Per-release 262 artifacts (`262/`)

| File | Status |
|---|---|
| [`262/qb-demo-script.md`](262/qb-demo-script.md) | 🚧 Draft (preview release; pending SME pass for Setup-UI verification, Known-Bugs population, image capture, Slack canvas publish) |
| 262 per-area Hands-On extracts (10 areas) | ⏳ Pending — deferred until master coverage broadens beyond the 2 piloted areas |

Status legend: ✅ final · 🚧 draft (under iteration) · ⏳ pending (not yet started)

For an at-a-glance cross-release view, see **[`coverage-matrix.md`](coverage-matrix.md)**.

---

## How this work was done — process overview

A condensed walkthrough of the authoring process so you understand how a draft got from "blank file" to "v0.1 draft":

### 1. Source material gathering

For each release (260, 262), I worked from up to 4 sources:

| Source | Use |
|---|---|
| **Master Help compendium** (Salesforce-published PDF, ~1,500 pages) | Definitive but huge — used for detailed configuration steps |
| **Internal Solution Overview deck** (CONFIDENTIAL) | Per-feature Customer Need / Solution / Use Case / Impact — most digestible primary source |
| **Public Salesforce Help portal release notes** | Captured via Chrome MCP (the Help portal is a SPA, so a recursive shadow-DOM walker is needed to extract content) |
| **The `rlm-base-dev` project itself** | QB scenario reference, data plans, skills — what's actually in QB orgs |

For an authoring agent picking up the work later, the captured release notes (e.g., [`docs/salesforce/260/release-notes-pricing.md`](../salesforce/260/release-notes-pricing.md)) preserve what was on the public Help portal at extraction time, archived next to the captured Solution Overview content in [`docs/salesforce/{version}/feature-index.md`](../salesforce/260/feature-index.md).

### 2. Skill + pattern extraction

Two implementation files for cross-workstation handoff:

- [`.cursor/skills/release-enablement/SKILL.md`](../../.cursor/skills/release-enablement/SKILL.md) — workflow, source inventory pattern, frontmatter schema, two-tier model documentation
- [`.cursor/skills/release-enablement/authoring-patterns.md`](../../.cursor/skills/release-enablement/authoring-patterns.md) — 11 patterns for handling edge cases (upgrade guidance, known issues, sub-features, cross-area features, carry-forward markers, recordings placeholders, QB walkthrough handling, frontmatter, scenario threading, version-aware section metadata, license-scope split)

These were derived inductively — Pattern N was added only after at least two exercises had encountered the same edge case ("two implementations before abstraction").

### 3. Per-release drafts (current state)

The 10 per-release 260 drafts in `260/` were authored first, before the two-tier model was established. They follow the original "what's new in this release" framing with carry-forward inventory pointing back to prior PDFs.

### 4. Two-tier reframing

Mid-process, the framing shifted from per-release-only to two-tier (master + extract) based on the goal of supporting in-person workshops. The skills and patterns updated; master exercises 01 (PCM) and 02 (Pricing) authored as pilots.

The per-release 260 drafts remain valid but will eventually be regenerated as filtered views of the master set.

### 5. QB scenario grounding

The `master/qb-scenario-reference.md` document was authored after a comprehensive study of `rlm-base-dev`'s data plans. Particularly important for review: the **pricing-feature wiring** (Bundle / Attribute / Volume adjustments are wired to specific QB-COMPLETE products) and the **constraint engine semantics** (QuantumBitComplete + Server2 CML models, with Type/Port tags driving compatibility logic).

---

## Open questions (consolidated from all drafts)

These are decisions that need authoring + PM input before drafts can move from `draft` → `review`. Pulled together from the Open Questions sections in the individual exercise files.

### Cross-cutting structural questions

1. **Depth of prior-release content in master exercises** — sections referencing 252/254/256/258 features currently summarize behavior in a paragraph and link to the prior PDF. Is that sufficient, or should master sections include full step-by-step walkthroughs (would 3× the file length)?
2. **Synthesis exercise scope** — each master exercise's capstone is a 4–6 hour comprehensive walkthrough. Should we offer scoped variants (2-hour quick walkthrough vs 6-hour full)?
3. **Branding** — keep "Revenue Cloud" labels (matches current product UI), switch to "Agentforce Revenue Management" (matches Spring '26 marketing), or use both during transition? Currently we use "Revenue Cloud" throughout.

### Demo URLs

Solution Overview decks confirm specific recorded demos exist. We have demo names but not URLs. Need actual URLs from PM for:

- Price Propagation Demo · Promotions Demo · If Else Formula / Auto-numbering Demo (Pricing)
- Product Detail Caching Demo · Filterable & Searchable Field Demo · Enhanced Multi-Selection Demo (PCM)
- Decomposition Workspace Demo · Pause External Callouts Demo · Custom Logic Hook Demo · Orchestrate Business Process Demo · CME Interop Demo · Move and Change Plan Demo (DRO)
- Plus a long list more across other areas

### `[NEEDS REVIEW]` markers

Several configuration walkthroughs are flagged `[NEEDS REVIEW]` pending an org walkthrough or deeper master-PDF research. Notable concentrations:

- Master Pricing § 21 (Advanced Price Log Settings setup steps)
- 260 Configurator (B2B Commerce decisions, per-feature demo URLs)
- 260 RCB (Tax Treatment Resolution detail, Payment API endpoints)
- 260 Context Service (the obvious release-notes URL is a 404; PM verification needed)

These can be filled in incrementally without blocking review.

### `rlm-base-dev` data gaps

Master Pricing § 15 (Price Propagation) wants pre-built propagation rules for QB-QRack-750. None exist by default. The walkthrough configures the propagation table during the exercise — actually a strength for in-person teaching, but worth confirming with PM.

Several optional QB enhancements documented in [`master/qb-scenario-reference.md`](master/qb-scenario-reference.md) § Gaps + Recommendations:

- Multi-LE BillingAccounts on Infinitech (currently 1 BillingAccount, US LE only)
- Pre-built starter Opportunity / Quote for Infinitech
- Sample Contracts for CLM exercises
- Non-USD PricebookEntry overlays

None block the workshop scenario; they'd improve fidelity.

---

## How to provide feedback

Pick whatever works for your context:

| Mechanism | When to use |
|---|---|
| **Inline comments on the markdown** in your local clone | If you're hands-on with the code — natural for SI / implementation reviewers |
| **GitHub PR review** (once branch is pushed) | Best for structured per-line discussion |
| **Markdown comments to Brian over Slack/email** | If you're scanning for big-picture concerns rather than line-level edits |
| **Edits directly to a clone** | If you want to demonstrate a fix rather than describe it |

**High-priority feedback areas (in order of urgency):**

1. ✅ **The two-tier model itself** — does master + per-release derivative make sense as a long-term structure?
2. ✅ **The Infinitech workshop scenario** — does it work for in-person enablement, or would you swap in a different customer/scenario?
3. **Workshop synthesis sections** — is the dense single-deal capstone right, or should it split?
4. **Master exercise structure** (the 9- or 10-part organization) — does the narrative arc work?
5. **Section-level technical accuracy** — anywhere I got the QB references, version metadata, or feature behavior wrong?

Lower priority (can wait for a v0.2 pass):

- Demo URLs to embed
- `[NEEDS REVIEW]` markers in individual configuration walkthroughs
- Branding adjustments
- Sample-data gap fills

---

## Project alignment

This work lives in `rlm-base-dev` so:

- Exercises stay aligned with the org-build automation (`prepare_rlm_org` flow + qb-* data plans)
- The QB scenario reference is the canonical source — when QB data plans change, the reference updates
- Authoring agents (Cursor / Claude / Codex / etc.) all read from the same project skills and rules — see [`AGENTS.md`](../../AGENTS.md) for the canonical agent entry point

Project conventions that affect this work:

- All `.md` files in `docs/` use **lower-kebab-case** filenames
- Markdown is the source; distribution artifacts (PDF / Word) render from markdown
- Skills live at `.cursor/skills/` and are usable by any agent (Cursor-specific format but plain markdown)

---

## Change log

- **2026-05-04 → 2026-05-06** — Initial enablement work: 10 per-release 260 drafts authored manually + skill + patterns extracted + QB scenario reference written + 2 master exercise pilots (PCM, Pricing) drafted + 262 feature index scaffolded
- **2026-05-06** — Two-tier model formally documented in skill; master exercise pilots authored validating Pattern 9 (Scenario Threading) + Pattern 10 (Version-Aware Section Metadata)
- **2026-05-06** — Initial commit on branch `feat/enablement-260-master-exercises` (commit `cae8d05d`)
- **2026-05-22** — Brought the catalog onto the `262` branch (master + 260 extracts + 260/262 feature indexes + 262 Help-portal snapshot). Trailhead L2 editorial artifacts stay off the public branch.
- **2026-05-24** — 262 QB demo script drafted (`262/qb-demo-script.md`) via the `qb-demo-script` SKILL; introduces a new per-release artifact type (SE/partner demo script) alongside the per-area Hands-On extracts.
- **2026-05-28** — README refreshed for 262 status (this commit). 262 per-area Hands-On extracts intentionally deferred until master coverage broadens — see *Why two-tier?* and the *Per-release 262 artifacts* table for the rationale.

---

## Quick links

| Document | Purpose |
|---|---|
| 🎯 [QB Scenario Reference](master/qb-scenario-reference.md) | What's in QB orgs by default. Foundation for all exercises. |
| 📘 [Master PCM Exercise](master/01-product-catalog-management.md) | First master exercise — Part 1 of the workshop |
| 📘 [Master Pricing Exercise](master/02-salesforce-pricing.md) | Second master exercise — Part 2 of the workshop |
| 📊 [Coverage Matrix](coverage-matrix.md) | What's drafted across releases |
| 🔧 [Release Enablement Skill](../../.cursor/skills/release-enablement/SKILL.md) | For authoring agents — workflow + source inventory |
| 📐 [Authoring Patterns](../../.cursor/skills/release-enablement/authoring-patterns.md) | 11 patterns for edge cases |
| 📋 [260 Feature Index](../salesforce/260/feature-index.md) | What's new in 260, by area |
| 📋 [262 Feature Index](../salesforce/262/feature-index.md) | What's new in 262 (preview) |
| 🗂️ [260 Per-Release Drafts](260/) | All 10 area drafts for 260 |
| 🎬 [262 QB Demo Script](262/qb-demo-script.md) | Per-release SE/partner demo script for 262 (preview, draft) |
| 📚 [262 Help Snapshot](../salesforce/262/help/) | Per-article markdown mirror of help.salesforce.com for 262 (838 articles) |

---

*This README is itself a draft — flag anything that's confusing, wrong, or missing.*
