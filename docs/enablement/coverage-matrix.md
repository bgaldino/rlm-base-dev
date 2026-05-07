# Revenue Cloud Enablement — Coverage Matrix

Working document tracking what enablement artifacts exist across releases, what's missing, and what needs to be created or updated for Winter '26.

**Version mapping** (RCA package versions → seasonal release):

| Folder | Package | Release | Status |
|---|---|---|---|
| 248 | 248 | Spring '24 | Reference only — oldest, sparse |
| (none) | 250 | Summer '24 | Missing entirely |
| 252 | 252 | Winter '25 | Exercises only |
| 254 | 254 | Spring '25 | Exercises only |
| 256 | 256 | Summer '25 | Exercises only |
| 258 | 258 | Winter '26 | Exercise drafts (some incomplete) |

Most "Overview" links in the journey map point out to Salesforce Help; we author **Hands-On Exercises only**.

---

## Coverage by Functional Area

Legend: ✅ have it · ⚠️ partial/draft · ❌ missing · — not in journey map for that release

| Functional Area              | 258 (W'26) Target | 256 (Su'25) | 254 (Sp'25) | 252 (W'25) | 248 (Sp'24) |
|------------------------------|---|---|---|---|---|
| Context Service              | ⚠️ draft (placeholder header) | — | — | — | — |
| Product Catalog Management   | ⚠️ draft | ✅ | ✅ | ✅ | ✅ |
| Salesforce Pricing           | ⚠️ draft | ✅ | ✅ | ✅ | ✅ |
| Configuration / Configurator | ⚠️ draft (filename "Product Configurator") | ✅ | ✅ | ✅ | — |
| Transaction Management       | ⚠️ draft | ✅ | ✅ | ✅ | — |
| Dynamic Revenue Orchestration| ⚠️ draft | ✅ | ✅ | ✅ | — |
| Usage Management             | ⚠️ draft | ✅ | ✅ | ✅ | — |
| Invoice Management           | ⚠️ draft (placeholder header) | ✅ | ✅ | ✅ | — |
| Revenue Cloud Billing        | ❌ | ✅ | ✅ | — | — |
| Advanced Approval            | ❌ in 258 (journey map shows it) | — (overview-only in Su'25) | ✅ Release Overview only | ✅ | — |
| CLM / Contracts              | — (dropped in W'26) | — | ✅ | ✅ | — |

### Notes on draft state of 258 PDFs

All 258 files are titled "Enablement Exercises, Version 1.0, Winter '26" — confirmed exercise content (not overview decks) despite the "External" filename suffix.

Several have **placeholder headers** (`Salesforce Feature Name` instead of the actual feature name) — these are drafts that were never finalized:

- Context Service (22pp)
- Invoice Management (23pp)

The rest carry proper headers but should still be reviewed for completeness.

---

## Data Shape Evolution Across Releases

The example data used in exercises has changed across releases. This affects how much can be ported vs. needs rewriting.

| Release | Example company / data | Notes |
|---|---|---|
| 248 (Sp'24) | "Acme" + Android/iOS phones | Generic, pre-RCA naming ("RLM" prefix on filenames) |
| 252 (W'25) | "Laptop Pro Bundle" + various | Different from 248 |
| 254 (Sp'25) | (no clear company tag found in PCM) | Mixed |
| 256 (Su'25) | **"QuantumBit (SmartBytes company)"** | First clear use of QB |
| 258 (W'26) | Generic Setup-driven instructions | Few specific data references |

The current `rlm-base-dev` data plan (`datasets/sfdmu/qb/`) builds the **QuantumBit** catalog — 162 products across 28 PCM objects, with structured attributes, classifications, and bundles. This is the org shape that any new Winter '26 (or later) exercises should align to.

The older `scratch_data` plan still exists in the repo but is the legacy shape (Accounts like "Global Media", "Infinitech").

---

## Filename Normalization Recommendation

Current naming is inconsistent:

- `248 RLM Pricing Hands-on Exercises.pdf`
- `Winter '25 - Pricing Exercises.pdf`
- `Spring '25 Pricing Hands On Exercises.pdf`
- `Summer '25 - Salesforce Pricing.pdf`
- `Salesforce Pricing - Winter '26 Revenue Cloud - External.pdf`

Proposed convention going forward:

```
{version} - {area} - Hands-On.pdf      # exercises
{version} - {area} - Overview.pdf      # if/when overview decks are authored
```

Example: `258 - Salesforce Pricing - Hands-On.pdf`

Sorts cleanly by version, area is unambiguous, type suffix lets both kinds coexist.

---

## Open Questions for Author

1. **Scope of org/data change** — Is the work to:
   - (a) migrate exercises that still reference older data shapes (Acme, Laptop Pro) onto the QuantumBit catalog?
   - (b) update QuantumBit-aligned exercises to reflect changes within QB itself (new products, restructured bundles, renamed fields)?
   - (c) both?
2. **Target release** — Is Winter '26 (258) the deliverable, or are we already working ahead to Spring '26 (260) / Summer '26 (262) given that `rlm-base-dev` is on the `262-test` branch?
3. **Advanced Approval** for 258 — needs to be authored from scratch? The journey map includes it, but no draft exists in the 258 folder.
4. **Recordings** — Winter '26 page in the journey map omits the "Recording" links every prior release had. Intentional (no recordings this cycle), or TODO?

---

*Last updated: 2026-05-06*
