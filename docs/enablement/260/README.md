# Revenue Cloud Enablement — Release 260 (Spring '26)

This directory contains the Hands-On Exercise catalog for Salesforce Revenue Cloud **Release 260 / Spring '26 / API v66.0**.

> **Branch context:** On the `262` branch this directory is the **prior-release reference**. 262 (Summer '26) extracts will live in `docs/enablement/262/` once the master pilots and the 262 feature index are stable. The master sources of truth live in `docs/enablement/master/`.

## Scope

Each functional area listed in the journey map gets one Markdown source-of-truth file in this directory. Distribution artifacts (PDF, Word) render from the Markdown.

| Area | Source file | Status |
|---|---|---|
| Salesforce Pricing | `260-salesforce-pricing-hands-on.md` | 🚧 draft |
| Product Catalog Management | `260-product-catalog-management-hands-on.md` | 🚧 draft |
| Product Configurator | `260-product-configurator-hands-on.md` | 🚧 draft |
| Transaction Management | `260-transaction-management-hands-on.md` | 🚧 draft |
| Dynamic Revenue Orchestration | `260-dynamic-revenue-orchestration-hands-on.md` | 🚧 draft |
| Usage Management | `260-usage-management-hands-on.md` | 🚧 draft |
| Invoice Management | `260-invoice-management-hands-on.md` | 🚧 draft |
| Context Service | `260-context-service-hands-on.md` | 🚧 draft |
| Advanced Approvals | `260-advanced-approval-hands-on.md` | 🚧 draft |
| Revenue Cloud Billing | `260-revenue-cloud-billing-hands-on.md` | 🚧 draft |
| Journey Map | `260-journey-map.md` | ⏳ pending (built last) |

## Authoring conventions

1. Use the template at [`../_template/exercise-template.md`](../_template/exercise-template.md) for every new file.
2. Frontmatter is the source of truth — auto-gen reads it for cover page, headers, footers, and version stamping.
3. Reference **product / catalog records** (products, SKUs, bundles, CML constraint models, attribute definitions, pricing entries) **by name** from the QuantumBit catalog (`datasets/sfdmu/qb/`, `datasets/constraints/qb/`) — do **not** invent product data or pull it from `scratch_data`. **Customer accounts and contacts**, by contrast, come from `scratch_data` (Infinitech is the primary, Global Media is the secondary, Robot Resellers is the partner channel — see rule 6 in `.cursor/skills/release-enablement/SKILL.md`). This split keeps QB as the canonical *catalog* and `scratch_data` as the canonical *customer* dataset.
4. Each release exercise covers **only net-new features for that release**. Stable features carry forward by reference (the "carry-forward" callout in the Release Overview points readers to prior-release exercise PDFs in `docs/enablement/258/` and earlier).
5. Historical artifacts in `docs/enablement/{248, 252, 254, 256, 258}/` are **read-only**. Do not edit them.

## Distribution artifact generation

Markdown is the source. Rendered PDF / Word artifacts ship from the Markdown via a still-to-be-built render task. Until that task exists, render manually with Pandoc:

```bash
pandoc 260-salesforce-pricing-hands-on.md -o "260 - Salesforce Pricing - Hands-On.pdf" \
  --pdf-engine=xelatex --toc --toc-depth=2
```

## Sign-off workflow

1. Author drafts the Markdown using the template.
2. Author + reviewers iterate (issues / comments / PR review).
3. Frontmatter `status` flips: `draft` → `review` → `final`.
4. Once `final` for all areas, render distribution artifacts.
5. Update `docs/enablement/coverage-matrix.md` to reflect 260 as published.

## Forward releases

The render/auto-gen pipeline will lift the structure forward to 262 (`docs/enablement/262/`) with frontmatter swaps and a content delta workflow. See `docs/enablement/_template/exercise-template.md` for the schema the auto-gen reads. The 262 feature index is already populated at [`../../salesforce/262/feature-index.md`](../../salesforce/262/feature-index.md) and the Help-portal snapshot is at [`../../salesforce/262/help/`](../../salesforce/262/help/).
