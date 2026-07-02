# Authoring Patterns

Conventions for handling edge cases that come up across release-enablement exercises but aren't covered by the bare template structure. These were extracted from the 260 Pricing and PCM drafts; they apply uniformly across all areas going forward.

When you encounter one of these situations during authoring, follow the pattern here so all exercise files stay consistent (and the eventual auto-gen reads predictable structures).

---

## Pattern 1: Upgrade Guidance

**When this applies:** the release adds **transitional actions customers must take after upgrading from the prior release**. These appear in the master PDF's "Upgrade Guidance for {Release}" section as per-area content. They are **not features** — they're remediation steps.

**Examples from 260:**
- *Discover Products Flow Update* — must add `discoverProductsContext` Apex-Defined variable if not done in Winter '26.
- *Custom Permission Set Groups Update* — must recalculate permissions to fix net-aggregate FLS.

**How to handle:**

Place a dedicated H2 section **immediately after Release Overview** and **before the first Feature section**. Heading: `## Upgrade Guidance from {prior_release}`. If the area has no upgrade guidance for the cycle, omit the section entirely.

Each guidance item gets an H3 subsection with: a short description, who's affected, and the steps to resolve. Mark `[NEEDS REVIEW]` only if the steps weren't pulled from the master PDF.

```markdown
## Upgrade Guidance from Winter '26

> Customers upgrading from 258 (Winter '26) to 260 (Spring '26) — review these transitional actions before assuming the carry-forward features in this area work as expected. Source: master PDF "Upgrade Guidance for Spring '26" section.

### Discover Products Flow Update

If you didn't update the Discover Products flow during Winter '26, Spring '26 requires it for Groups in quotes/orders to keep working. Add the `discoverProductsContext` Apex-Defined variable (`ProductConfig__DiscoverProductsContext`) to the flow, mark it Available for Input.

**Affected:** customers using Groups in quotes/orders, with a custom Discover Products flow not updated in 258.

**Steps:** ...

### Custom Permission Set Groups Update

...
```

**Why this matters for the auto-gen:** Upgrade guidance is per-pair-of-releases (`{from} → {to}`). The eventual auto-gen will track these so they land in the right exercise file and not get duplicated when 262 → 264 also has guidance.

---

## Pattern 2: Known Issues

**When this applies:** the release ships with **known bugs or limitations admins should be aware of**. They often have workarounds. These appear in the master PDF's "Upgrade Guidance" section as side notes, or in feature-specific notes.

**Examples from 260:**
- *Limitation with Price Propagation Element* — `ClassCastException` when Price Propagation + Pricing Setting elements run together in certain configurations. Workaround: retry.
- *Canceling derived pricing products results in incorrect net total price* — no workaround.

**How to handle:**

Place a callout block **at the top of the relevant feature's section** (right after the H2 feature title) using a blockquote with ⚠️ prefix. Don't make these their own H2 sections — they're feature-scoped.

```markdown
## Feature 1: Streamline Complex Quote Calculations with Smarter Price Propagation

> ⚠️ **Known issue (260):** Intermittent Pricing API failures occur when Price Propagation and Pricing Setting elements are used together — the procedure must be configured without a change set, with context reuse disabled — throws `ClassCastException: CacheableDataColumn cannot be cast to CacheableMetaColumn`. Workaround: retry the request. Source: master PDF p 117.

### Business Objective
...
```

If a known issue is not feature-specific (e.g., affects multiple features or the area as a whole), put it in a `## Known Issues for {Release}` H2 section right after Upgrade Guidance.

**Why this matters:** customers reading exercises *will* hit these issues during walkthroughs. Calling them out inline saves a support escalation.

---

## Pattern 3: Sub-Features

**When this applies:** the Solution Overview deck or release notes group multiple distinct sub-features under a single parent name. The parent name is for organization; each sub-feature has its own Customer Need / Solution / Use Case / Impact.

**Examples from 260:**
- *Configurator UI Enhancements* groups two sub-features: New Streamlined Compact Layout + Fixed Position "Sticky" Error Messages.
- *Flexible Configuration Experience* groups three: Edit Transaction Line Context Fields + Inline Attribute Configuration + Enhanced Instance Selection and Cloning.

**How to handle:**

Each sub-feature gets its own H2 `## Feature N: {sub-feature name}` section in the body, with full four-part structure (Business Objective / Use Cases / Design Time Configuration / Configuration and Runtime Video).

In the **Release Overview**, group them under a parent bullet so readers see the conceptual grouping the Solution Overview presents:

```markdown
## Release Overview

Salesforce Revenue Cloud Product Configurator includes the following net-new features in Spring '26:

1. **Configurator UI Enhancements**
    - **New Streamlined Compact Layout** — compact mode toggle for large bundles
    - **Fixed Position "Sticky" Error Messages** — persistently displayed at top of configurator modal
2. **Flexible Configuration Experience**
    - **Edit Transaction Line Context Fields** — directly within the option card
    - **Inline Attribute Configuration for Bundle Components** — no separate-screen navigation
    - **Enhanced Instance Selection and Cloning** — multiple instances + clone configured ones
3. **Translation Support for Error Messages**
4. **Configuration Logs**
```

In the body, the **per-sub-feature sections are siblings** — `## Feature 1.1` is wrong; use `## Feature 1: New Streamlined Compact Layout`, `## Feature 2: Fixed Position "Sticky" Error Messages`, etc. with continuous numbering.

**Why this matters:** flat H2 numbering keeps the auto-gen simple and matches how readers actually navigate. The parent grouping lives in the bullet list and (optionally) a per-feature `parent_group:` frontmatter field for the auto-gen to render section breaks.

---

## Pattern 4: Cross-Area Features

**When this applies:** a feature has a primary home in one area but **affects another area meaningfully**. Examples: Promotions is primarily a Pricing feature but adds the Promotion Execution Element which affects Transaction Management. B2B Commerce items affect PCM.

**How to handle:**

**Decide on a primary home** for each cross-area feature based on where it's most prominently configured or where its core capability lives. Put the **full content** (Business Objective, Use Cases, Design Time Configuration, etc.) in the primary area's exercise file.

In the **secondary** area's exercise file, add a **brief reference section** at the bottom (after the area's own features, before the Open Questions section). Use H2 `## Cross-Area: {feature}` and limit content to:

- One-paragraph description of what it is
- Why it matters to *this* area's reader
- Pointer to the primary area's exercise file for the full walkthrough

```markdown
## Cross-Area: Promotions in Agentforce Revenue Management (Beta)

Promotions is documented in full in `260-salesforce-pricing-hands-on.md`. From a Transaction Management perspective: when a quote/order is processed, the Promotion Execution Element in the pricing procedure evaluates eligible promotions and applies them at runtime. Sellers see eligible promotions in the Quote line item product details panel; manual/coupon-code promotions require seller selection.

→ **Full configuration:** `docs/enablement/260/260-salesforce-pricing-hands-on.md` § Promotions (Beta)
```

**Multi-cross-area sources** (e.g., B2B Commerce features affect PCM, Pricing, *and* Transaction Management) get one cross-area block in each affected secondary area, with the primary home in the area where the feature was authored or in a dedicated exercise.

**Why this matters:** prevents content duplication and keeps each area's exercise focused. A reader picking up the Pricing exercise gets the full Promotions walkthrough; a reader doing Transaction Management sees enough to understand impact without having to re-read pricing details.

---

## Pattern 5: Carry-Forward Markers

**When this applies:** every exercise file has a Carry-Forward Inventory section listing prior-release features. Some entries are unchanged; some are *enhanced* in the current release; some are *deprecated*.

**How to handle:**

Use a status column with consistent emoji + word convention:

| Marker | Meaning |
|---|---|
| ✅ no change | Feature works the same as in the prior release. Reference prior-release PDF for the walkthrough. |
| 🔄 **enhanced** | Feature behavior was extended in the current release. Add a brief inline note pointing to which Feature section in the current doc covers the enhancement. |
| 🚫 **deprecated** | Feature is being phased out. Note the migration path or replacement. |
| ⚠️ **changed** | Behavior changed in a way that affects existing customers (not just an enhancement). Note what changed. |

```markdown
| Search Products in Large Catalogs (up to 20M) | 256 | same | 🔄 **enhanced** in 260 — Filterable/Searchable Field limits expanded (Feature 2) |
```

**Why this matters:** customers upgrading from 258 will scan this table to know what they need to re-check. The marker tells them where to look.

---

## Pattern 6: Recordings, Demo URLs, and `[NEEDS REVIEW]`

**When this applies:** every feature has a "Configuration and Runtime Video" subsection. Sources commonly tell us a recording exists (the licensing matrix in the Solution Overview deck names them) but rarely give us the URL.

**How to handle:**

Use a consistent inline format:

```markdown
### Configuration and Runtime Video

📹 **"{demo name from Solution Overview licensing matrix}"** — recorded demo confirmed. [NEEDS REVIEW — get URL.]
```

If multiple features share one combined demo (e.g., "If Else Formula, Auto-numbering Demo"):

```markdown
### Configuration and Runtime Video

📹 **"If Else Formula, Auto-numbering demo"** — single combined demo for both this feature and Feature 5 (Auto-Numbered Element Names). [NEEDS REVIEW — get URL.]
```

If no recording is being produced:

```markdown
### Configuration and Runtime Video

No dedicated recording for this feature in {release_name}. Help portal screenshots and walkthrough above are sufficient.
```

**Why this matters:** demos are the single most-asked-about authoring artifact. Codifying the placeholder syntax means PMs reviewing drafts know exactly where to drop the URLs without restructuring the doc.

---

## Pattern 7: QuantumBit Walkthrough Scenarios

**When this applies:** every feature's Design Time Configuration section benefits from a "Try this against the QB org" walkthrough that uses real QuantumBit catalog records.

**How to handle:**

After the Design Time Configuration steps, optionally add a `### QuantumBit walkthrough scenario` H3 subsection. Use specific QB records by name (looked up from `datasets/sfdmu/qb/en-US/`).

If QB doesn't natively model what the feature demonstrates (e.g., Price Propagation needs nested Building/Floor/Room hierarchies; QB has flat product classifications), explicitly call out the limitation rather than fabricating data:

```markdown
### QuantumBit walkthrough scenario

QB doesn't natively model nested Building/Floor/Room hierarchies that this feature targets. Three options for the exercise:
1. Layer a temporary overlay catalog with a nested structure
2. Pick a different scenario that QB *does* support (e.g., Q-Rack PC classification with sub-classifications)
3. Document the limitation and use a scaled-down demo that exercises ascending propagation between just two levels (Group → Line Item) using QB's existing structure
```

**Why this matters:** never fabricate sample data. Either use real QB records, or be explicit that the example doesn't fit and propose options.

---

## Pattern 8: Frontmatter Conventions

The base template covers frontmatter, but authoring practice has converged on these conventions:

- `document_version`: increment from `0.1` (initial outline) → `0.2` (research applied) → `0.3` (review-ready) → `1.0` (final).
- `status`: `outline` → `draft` → `review` → `final`. Match the document_version progression.
- `last_updated`: ISO date — bump on every meaningful edit.
- `sources`: list every file path / URL that informed the doc, including section page numbers when known. The auto-gen reads this list for the "Sources" footer.
- `prerequisites`: org-level setup the reader must have done before starting any feature in this exercise. List `cci flow run prepare_rlm_org` first.
- `data_shape`: `qb` for QuantumBit (current default), `mfg` for Manufacturing-shape, `q3` for the q3 shape. Affects which dataset README to look up product names from.

---

---

## Pattern 9: Scenario Threading (master exercises)

**When this applies:** authoring or maintaining a **master exercise** in `docs/enablement/master/`. Per-release extracts inherit threading mechanically; master files own it.

**Examples:**
- An exercise on Pricing introduces Volume Adjustments by walking through Infinitech's order for QB-MSG-STRT scaled to 16+ units (which exercises the standing 25% volume tier).
- An exercise on Configurator demonstrates Sticky Errors by attempting an invalid QB-QRack-750 configuration that violates Server2 CML port-type constraints.
- An exercise on Transaction Management builds a multi-bundle quote for Infinitech that includes QB-COMPLETE (with attribute-priced QB-API at "Prod") + QB-QRack-750 (with valid Server2 configuration) + Professional Services Bundle.

**How to handle:**

Every walkthrough in a master exercise should be **anchored to the workshop scenario** documented in `docs/enablement/master/qb-scenario-reference.md`. The scenario revolves around:

- **Customer**: Infinitech (primary) or Global Media (secondary) — sourced from `scratch_data`
- **Partner channel** (when relevant): Robot Resellers — sourced from `qb-prm`
- **Software bundle**: QB-COMPLETE (Software, with QuantumBitComplete CML applied)
- **Hardware bundle**: QB-QRack-750 (Hardware, with Server2 CML applied)
- **Pricing demo products**: QB-API (bundle + attribute pricing) · QB-MSG-STRT (volume pricing)
- **Usage demo products**: QB-DB / QB-DB-TOKEN / QB-TOKENS-PACK / QB-CMT-* commitments
- **Selling models**: Term Annual (software) · One-Time (hardware) · Term Monthly / Evergreen (subscription variants)
- **Legal Entities**: Default Legal Entity - US / Canada / EU / UK
- **Currencies**: USD (corporate), EUR / GBP / CAD / AUD / CHF / JPY (active)

**Scenario continuity callout pattern:**

When an exercise builds on what was set up in an earlier exercise, mark the dependency explicitly:

```markdown
> **Scenario continuity:** This exercise picks up where § PCM Exercise 4 (Catalog Setup for Infinitech) left off. The Infinitech account, BillingAccount, and Robot Resellers partner relationship are assumed to be in place from that exercise.
```

For walkthroughs that DON'T depend on prior scenario state (e.g., a standalone configuration walkthrough), say so:

```markdown
> **Standalone walkthrough:** This exercise can be run independently of the broader workshop sequence — no prior-exercise state is assumed.
```

**Why this matters:** workshop attendees follow Infinitech end-to-end across all exercises. The customer they configure in Exercise 1 should still be the customer being approved, fulfilled, and billed in Exercises 5–8. Without scenario threading, exercises become disconnected feature walkthroughs and lose the "live workshop" coherence.

---

## Pattern 10: Version-Aware Section Metadata

**When this applies:** every section in a **master exercise** that documents a feature, configuration, or capability that has a Salesforce-release lineage. Required for all per-feature H2 sections; recommended for sub-feature H3 sections.

**The schema:**

Each H2 (and meaningful H3) section in a master exercise carries lightweight inline metadata at the top of the section, immediately after the header:

```markdown
## Feature 4: If-Else Formula in Formula-Based Pricing

> **Version metadata:** introduced 260 (Spring '26) · available 260+ · scenario_step Pricing Demo 4

### Business Objective
...
```

**Field meanings:**

| Field | Required? | Meaning |
|---|---|---|
| `introduced` | ✅ | The release version where this capability first shipped (e.g., 260, 256, 248). For foundational content available since pre-RLM, use `foundational`. |
| `available` | ✅ | Range of releases where this content is in-scope. Format: `<version>+` for "still available" or `<version>-<version>` for retired-in-future. |
| `enhanced_in` | optional | Array of release versions that extended the feature (e.g., `[260]` if a 258 feature got new capabilities in 260). The render task can emit "Enhanced in 260" callouts. |
| `deprecated_in` | optional | Release version where the feature was deprecated. Render task can emit warning. |
| `scenario_step` | optional | Position in the workshop narrative (e.g., `Pricing Demo 3`, `Configurator Demo 1`). Helps maintain ordering when rearranging exercises. |

**The auto-gen filter logic:**

When rendering a per-release extract for `{version}`:

- Sections where `available` includes `{version}` AND `introduced <= {version}`: **emit**
- Sections where `enhanced_in` includes `{version}`: **emit with "Enhanced in {version}" callout**
- Sections where `introduced > {version}`: **skip** (not yet available)
- Sections where `deprecated_in <= {version}`: **skip or emit with deprecation warning** (depending on policy)

**Example master exercise frontmatter handling these:**

```yaml
---
mode: master
area: "Salesforce Pricing"
data_shape: qb
scenario_anchor: infinitech-cloud-deal
sections:
  - id: pricing-overview
    introduced: foundational
    available: "all"
    scenario_step: Pricing Foundation
  - id: bundle-based-adjustment
    introduced: 256
    available: "256+"
    scenario_step: Pricing Demo 1
  - id: attribute-based-adjustment
    introduced: 256
    available: "256+"
    scenario_step: Pricing Demo 2
  - id: if-else-formula
    introduced: 260
    available: "260+"
    scenario_step: Pricing Demo 4
  - id: price-propagation
    introduced: 260
    available: "260+"
    enhanced_in: []
    scenario_step: Pricing Demo 5
---
```

**Why this matters:** master exercises grow over many releases. Without version metadata on sections, generating the 260-specific extract requires a human pass through every section deciding what's relevant. With metadata, the render task does it mechanically and an in-person workshop can mix-and-match: "Spring '26 release training" omits foundational sections; "New hire onboarding workshop" includes everything.

---

## Pattern 11: License-Scope Split (Multi-License Areas)

**When this applies:** an area's content split across two licenses where one is a strict superset of the other. The clearest case is **Invoice Management (RCA)** vs **Revenue Cloud Billing (RCB)** — both billing-area features, but RCB is a paid superset of Invoice Management.

**How to handle:**

1. **Open both exercises with the same Capability Matrix at the top** showing which features are RCA-shared vs RCB-only:

   ```markdown
   ## RCA vs RCB Capability Matrix

   | Capability | Invoice Mgmt (RCA) | Revenue Cloud Billing (RCB) |
   |---|---|---|
   | One-Time & Subscription Charges | ✅ | ✅ |
   | Billing Arrangement, Usage Invoicing | | ✅ |
   | Payments, Refunds, Collections | | ✅ |
   ```

2. **Each exercise scopes itself to one column** with an explicit callout at the top: "This exercise covers the RCA column only. For RCB-only capabilities, see `260-revenue-cloud-billing-hands-on.md`."

3. **Cross-references between the two exercises** are *summary + link* (Pattern 4), not duplicated content. The RCA exercise references RCB for the broader picture; the RCB exercise references RCA-shared rows for the foundation.

**Why this matters:** customers reading the RCA exercise shouldn't have to wade through RCB-only content that requires an upgrade to access. Customers reading the RCB exercise shouldn't have to read foundational RCA content twice. The split lets each audience get exactly what they need.

**Validated in:** 260 Invoice Management + 260 Revenue Cloud Billing exercises.

---

## Where these patterns live

This file is `.cursor/skills/release-enablement/authoring-patterns.md`. It's referenced from `.cursor/skills/release-enablement/SKILL.md` and from each exercise file's `sources:` frontmatter when relevant.

Add new patterns here as they emerge from future drafts. Patterns become canon after they're applied to **at least two** exercise files — the "two implementations before abstraction" rule.

## Change Log

- **2026-05-06** — Initial patterns extracted from 260 Pricing + PCM drafts (upgrade guidance, known issues, sub-features, cross-area features, carry-forward markers, recordings placeholder, QB walkthrough handling, frontmatter conventions).
- **2026-05-06** — Added **Pattern 9 (Scenario Threading)** for master exercises, **Pattern 10 (Version-Aware Section Metadata)** for the auto-gen filter contract, and **Pattern 11 (License-Scope Split)** for multi-license areas like Invoice Mgmt vs RCB. Pattern 9 + 10 are master-exercise-specific; Pattern 11 was already in implicit use across Invoice Mgmt + RCB drafts and is now formally codified.
