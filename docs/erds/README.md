# Revenue Cloud Entity Relationship Diagrams

This directory contains comprehensive entity relationship diagrams (ERDs) for the Revenue Cloud Base Foundations project, generated from `erd-data.json`.

**Current baseline:** Release 264 (Winter '27, API v68.0) — **263 objects, 4,252 platform fields, 674 relationships** across 9 domains.

The release/apiVersion values here and in `erd-data.json` are *provenance*: they
record which orgs the schema was extracted from, not a version the file is pinned
to. Bumping them without re-extracting would make the ERD claim to describe a
release while serving another one's data.

The ERD reflects **canonical Revenue Cloud platform schema only** — custom fields (any `__c` suffix, including project `RLM_*__c` and managed packages) are excluded by validation tooling. The 264 capture was cross-validated across two independently built `prepare_rlm_org` 264 orgs (`rlm-base__264merged` and `rlm-base__264fresh`, both `ent` shape) which agreed field-for-field — 254 describable objects and 3,913 platform fields each — so no figure rests on a single org. The 127-entity Core UDD verification at `gitcore.soma.salesforce.com/core-2206/core-262-public@p4/262-patch` is carried forward from the 262 pass and was not re-run; 264 has no published Core UDD branch or Metadata Coverage Report yet, which is why a live org is ground truth for this release.

**262 → 264:** 70 fields added, 8 removed, 0 type changes, 1 polymorphic
reference-target change, 270 picklist values added and 18 removed, across 62 changed
objects. All 8 removals are usage-domain, and **7 of them** are a single
architectural move rather than attrition: 264 relocated the usage policy bindings
off the definition and runtime objects and onto `ProductUsageResourcePolicy`, the
**product-and-resource-specific** binding site. `UsageResourcePolicy` still carries
the same four policy lookups at **resource** level in a 264 org, so PURP is the new
binding site, not the only one.

The 8th removal, `TransactionUsageEntitlement.DrawdownOrder`, is **not** part of that
move — PURP has no drawdown field. In 264 drawdown ordering lives on
`ProductUsageGrant` and on the per-transaction policy objects. Full delta, including
the SFDMU `--impact` cross-reference, at
`scripts/erd/schema_diff/262-vs-264-diff.md`.

<details>
<summary>260 → 262 (previous baseline, kept for history)</summary>

Per-object 262 schema changes. The 260 → 262 delta is **field-level additive** (45 fields added, 0 removed, 0 type changes, 2 polymorphic-reference targets expanded — e.g. `Invoice.ReferenceEntityId` now also accepts `Opportunity`/`Quote`) with **value-level picklist deltas** of 243 added and 62 removed. The picklist removals are IANA TimeZone renames (e.g. `America/Catamarca` → `America/Argentina/Catamarca`, `Europe/Kiev` → `Europe/Kyiv`) and cleanup of unused industry-specific `UsageType` values (`InsuranceRuleAction`, `StageManagement`) on fulfillment objects; the picklist-removal audit tabulated the full breakdown. Each removed value was cross-referenced against every CSV under `datasets/sfdmu/{qb,q3,mfg}/**` — **zero maintained-plan rows reference any removed value**. Nine objects with deltas appear in existing SFDMU plans per `scripts/erd/schema_diff/260-vs-262-diff.md`, but **no SFDMU remediation is required**: additive fields can't break loads, and the removed picklist values aren't in use.

</details>

To refresh the ERD against a new release or different org configuration, see `.cursor/skills/schema-validation/SKILL.md`.

## Generated Files

### Individual Domain Mermaid Diagrams

Detailed ERDs for each domain, suitable for documentation and analysis:

- **pcm.mermaid** — Product Catalog Management (11 objects)
  - Product hierarchy, attributes, classifications, and qualifications
  
- **pricing.mermaid** — Salesforce Pricing (14 objects)
  - Price books, price book entries, and adjustment logic
  
- **rate-management.mermaid** — Rate Management (15 objects)
  - Rate cards, rate card entries, and rate lookup data
  
- **configurator.mermaid** — Product Configurator (4 objects)
  - Product configuration flows, rules, and assignments
  
- **transaction-management.mermaid** — Transaction Management (37 objects)
  - Assets, asset state periods, orders, order items, quotes, approvals
  - Contract items, pricing details, and related transaction records
  
- **dro.mermaid** — Dynamic Revenue Orchestrator (27 objects)
  - DRO transactions, message sets, outbound messages, and orchestration rules
  
- **usage-management.mermaid** — Usage Management (22 objects)
  - Product usage grants, usage resources, usage records, and policies
  
- **billing.mermaid** — Billing (54 objects)
  - Billing accounts, schedules, treatments, invoices, credit/debit memos
  - Payment schedules, tax treatment, and general ledger integration

### Master Diagram

- **master.mermaid** — High-level cross-domain relationships
  - Shows key objects from each domain as nodes
  - Illustrates critical cross-domain relationships (e.g., OrderItem → Product2, Invoice → BillingSchedule → Order)
  - Suitable for architecture documentation and executive summaries

### Interactive HTML Viewer

- **revenue-cloud-erd.html** — Force-directed graph with full field detail
  - 263 objects, 4,252 fields, 674 relationships across 9 domains
  - **Features:**
    - Click any object node to see all fields (type, description, refersTo links)
    - Fields grouped into Relationship Fields, Data Fields, and Related Objects sections
    - Collapsible field sections with clickable refersTo navigation
    - Domain filtering via colored toggle pills
    - Object search (filters sidebar list and graph simultaneously)
    - Zoom/pan, drag nodes, fit-to-view, label/link toggles
    - Hover tooltips with domain, field count, and click prompt
    - Node size proportional to field count (sqrt scale)
    - Domain color coding with legend
  - Data sourced from dual-org cross-validation across two 264 orgs, diffed against the committed 262 snapshot
  - Self-contained (D3.js v7 CDN only external dependency)

- **erd-data.json** — Complete machine-readable schema (263 objects, 4,252 fields, 674 relationships)
  - Custom fields excluded by design (project-deployed `RLM_*__c` and managed-package fields)
  - Fields include type, description, and refersTo metadata
  - Regenerate via `scripts/erd/validate_erd_against_org.py --org <alias> --patch` after schema changes

## How to Use

### Viewing Mermaid Diagrams

Mermaid files can be viewed in several ways:

1. **GitHub** — Automatically renders `.mermaid` files in browser
2. **Mermaid Live Editor** — https://mermaid.live/
   - Copy-paste diagram content from `.mermaid` files
3. **VS Code** — Install "Markdown Preview Mermaid Support" extension
4. **Local Preview** — Use any Markdown preview that supports Mermaid

### Using the Interactive HTML Viewer

1. Open `revenue-cloud-erd.html` in any modern web browser
2. No installation or build required
3. Use the sidebar to:
   - Filter domains (checkboxes)
   - Search for objects (text input)
   - View statistics
4. Interact with the graph:
   - Hover over nodes to see details
   - Click and drag to pan
   - Scroll to zoom in/out
   - Drag nodes to reposition

## Understanding Relationship Types

### Mermaid Notation

- `}o--||` — Many-to-one (child → parent, typically a Lookup field)
- `||--o{` — One-to-many (parent → child, Master-Detail)
- `||--||` — One-to-one

### Salesforce Relationship Types

- **Lookup** — Optional relationship; child can exist without parent
- **Master-Detail** — Required relationship; child cannot exist without parent
- **Polymorphic** — Field can reference multiple object types (e.g., OwnerId)

## Statistics

- **Total Objects:** 263
- **Total Fields:** 4,252 (canonical platform fields only; custom fields excluded)
- **Total Relationships:** 674 (unique cross-object lookups)
- **Total Domains:** 9 (PCM, Pricing, Rates, Configurator, Transactions, Approvals, DRO, Usage, Billing)
- **Last verified:** 2026-08-15 (two 264 orgs cross-validated; 127-entity Core UDD check carried forward from the 262 pass)

## Diagram Layout Strategy

### Domain Diagrams
- Show all objects within a domain and their internal relationships
- Include key field names for context
- Suitable for:
  - Feature documentation
  - Developer onboarding
  - Data model reviews
  - Feature-specific architecture discussions

### Master Diagram
- High-level view showing only key objects per domain
- Shows critical cross-domain relationships
- Suitable for:
  - Executive presentations
  - System architecture documentation
  - Data flow overview
  - Integration planning

### Interactive Viewer
- Full-featured force-directed graph with all objects
- Suitable for:
  - Live exploration and discovery
  - Complex relationship analysis
  - Impact analysis (understanding connected objects)
  - Training and demos

## Maintenance

The current ERD was built by combining the original v260 Developer Guide PDF extraction with org-introspection cross-validation against fresh `prepare_rlm_org`-built scratch orgs (260, 262, then **264**), then individually verifying 127 entities against canonical Core UDD source. Mermaid domain files are relationship-focused summaries — they are **hand-maintained, not generated**, so treat `erd-data.json` as canonical when the two disagree.

To refresh after a schema change or new release:

1. Build a fresh scratch org from the target release branch
2. Run `python scripts/erd/validate_erd_against_org.py --org <alias> --patch` to add new fields and relationships. `--patch` is **add-only at field granularity** — for a field the ERD already carries it writes nothing, so a wrong `refersTo`, `relationshipName`, `description`, or `type` on an existing field survives the run. Re-check those four against the org describe yourself; see `.cursor/skills/schema-validation/SKILL.md`
3. Run `python scripts/erd/cleanup_orphan_erd_fields.py --orgs <alias>,<alias2> --dry-run` to identify candidates for cleanup. Pass **two distinct orgs on the target release with complementary shapes**. Orphans are unioned across orgs, so a second org can only rescue a feature-gated field from deletion — which makes a differently shaped org useful and an identically shaped one inert. Either way, absence from every org is a candidate filter, not proof of removal: confirm each against the release diff or Core source before removing. The 264 pass used two Enterprise orgs and so removed only the 8 fields the 262→264 diff independently showed gone
4. Run `python scripts/erd/build_erds.py` to regenerate the HTML viewer
5. Run `python tests/test_erd_doc_counts.py` and fix whatever it names. A refresh moves the counts the docs quote, and updating the headline triple is not enough: the **per-domain** counts in `.cursor/skills/revenue-cloud-data-model/SKILL.md` and its `domains/*.md` are separate hand-maintained numbers that this repo has never swept. Before the check existed, 7 of that table's 9 rows disagreed with `erd-data.json` and summed to 185 against an actual 263 — under a correct "263 objects" headline
6. Re-validate: `python scripts/erd/validate_erd_against_org.py --org <alias> --report docs/erds/validation-report.md` and confirm only the **expected feature-gated gaps** remain (diff against the committed `validation-report.md`; the current expected baseline is 9 feature-gated objects unfindable in a default RLM scratch profile — `AssetDowntimePeriod`, `AssetOwnerSharingRule`, `AssetShare`, `AssetTag`, `AssetWarranty`, `PricingProcedureResolution`, `ProductPriceHistoryLog`, `ProductPriceRange`, `ProductSellingModelDataTranslation` — plus **0** objects with field gaps and **58** ERD-side fields that don't surface in a stock org, which are the feature-gated / cross-cloud set carried forward from the 262 pass). A clean refresh produces **zero NEW gaps** vs the committed baseline, not zero gaps absolute.

> The 262 baseline was 33 objects with field gaps and 822 ERD-side fields; at 264 the report reads 0 and 58. The two moved for different reasons, and only one of them is `--patch`: patching **adds**, so it can close org-side gaps (33 → 0) but can never lower the ERD-side count. That fell through deliberate removal — the orphan-cleanup batches, plus this refresh's 8 retired fields — which is why step 3 exists and why `--patch` is not a substitute for it. Quote the report rather than these numbers if they disagree; `validation-report.md` is generated, this line is not.

Detailed workflow at `.cursor/skills/schema-validation/SKILL.md`.

---

**Last refresh:** 2026-08-15 (Release 264 / Winter '27 / API v68.0)
**Verified against:** `rlm-base__264merged` and `rlm-base__264fresh` (both 264, `ent` shape, agreed field-for-field); baseline `scripts/erd/schema_diff/262-schema.json`; Core UDD `core-262-public@p4/262-patch` carried forward from the 262 pass
**Custom fields:** Excluded by design (canonical platform schema only)
