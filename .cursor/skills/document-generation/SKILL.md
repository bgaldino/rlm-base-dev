---
name: document-generation
description: >-
  Create, modify, and troubleshoot Salesforce OmniStudio .docx templates and
  DocumentTemplate lifecycle operations. Use for token mapping, template activation,
  document generation, or output verification; use odt-authoring for deep
  OmniDataTransform mapper work.
---

# OmniStudio Document Generation

Use this skill when creating, modifying, or troubleshooting Salesforce OmniStudio
document templates (`.docx`) and DocumentTemplate lifecycle operations.
For ODT mapper architecture and deep ODT troubleshooting, use
`../odt-authoring/SKILL.md`.

## Quick Rules

1. **Template needs two ODT names** — DocumentTemplate must reference one Extract
   and one Transform ODT by name.
2. **Token syntax** — use `{{FieldName}}` for scalars, `{{#Section}}...{{/Section}}`
   for repeating rows, and `{{IMG_name}}` for images.
3. **Use canonical template scripts** — `docgen_template_*` is the only public
   command surface for template build, token extraction, lifecycle, and generation.
4. **Deactivate before mutable edits** — set template to Draft before binary or
   metadata updates; reactivate only after changes are complete.
5. **Generate to verify behavior** — use `docgen_template_generate.py` for
   end-to-end smoke tests after template or mapper updates.
6. **Keep Context Service input separate from runtime Context API input.** For a
   Context Service DocumentGenerationProcess, set `DocGenAdditionalInputType`
   to `ContextService` and pass the root entity ID as the plain
   `DocGenAdditionalInput` value. The runtime `{"inputData": ...}` shape does
   not belong in that DGP field.
7. **Keep template and mapper changes in sync** — if token structure changes,
   confirm Extract/Transform output alignment before reactivation.
8. **Route ODT deep work to ODT skill** — hierarchy design, mapper structure,
   filter semantics, and array-depth debugging live in `../odt-authoring/SKILL.md`.
9. **Dynamic image contract is strict** — `IMG_*:src` must resolve to
   ContentDocument (`069`) plus width/height; see `dynamic-images.md`.


## DO NOT

- **DO NOT** use dot notation in Extract `InputFieldName` — use colons
  (`Invoice:PaymentTerm:Name`, not `Invoice.PaymentTerm.Name`).
- **DO NOT** leave `OutputObjectName` null on any OmniDataTransformItem — this
  causes a runtime NPE that silently produces empty output.
- **DO NOT** create duplicate object query items — duplicates can cause the entire
  Extract to fail silently, producing no data.
- **DO NOT** pass a ContentVersion Id (`068`) or file Title to `IMG_token:src` —
  only ContentDocument Id (`069`) works; others crash the engine.
- **DO NOT** omit `width` or `height` from `IMG_` token objects — the image
  silently fails to render if either dimension is missing.
- **DO NOT** edit `TargetOutputFileName` or `MapperOmniDataTransformName` while the
  DocumentTemplate or ODT is Active — deactivate first.
- **DO NOT** use the SObject REST API to create/edit/delete ODTs in shared,
  production, or customer orgs — the official docs say these records are "for
  internal use only." Use Metadata API XML instead.

---

## Entry Conditions

| Task | Use this skill? |
|------|-----------------|
| Create a new `.docx` invoice/quote/contract template | Yes |
| Wire up Extract + Transform ODTs for a template | Use `../odt-authoring/SKILL.md` |
| Add fields/tokens to an existing template | Yes |
| Troubleshoot blank output or generation errors | Yes |
| Add dynamic images to a template | Yes — see `dynamic-images.md` |
| Create ODT items programmatically via API | Use `../odt-authoring/SKILL.md` |

---

## Where the depth lives

| Task | Read |
|---|---|
| List, replace, create or download a template; execute an Extract or Transform; lint or diff ODTs; generate end to end; helper scripts; Context Service DGP fields | [template-lifecycle-and-testing.md](template-lifecycle-and-testing.md) |
| Stage-by-stage data flow; token syntax (scalar, section, IF_, IMG_, HYP_, RTB_); page-break rules | [architecture-and-tokens.md](architecture-and-tokens.md) |
| Extract and Transform item fields; the DocumentTemplate record | [item-types-and-template-record.md](item-types-and-template-record.md) |
| Blank or wrong output, engine errors, Extract architecture pitfalls | [troubleshooting.md](troubleshooting.md) |
| Create Extract and Transform ODTs through the API, cloning patterns, shell escaping | [data-mapper-authoring.md](data-mapper-authoring.md) |
| Formula catalog, filter mechanics, hierarchy and array semantics, Preview API | [extract-engine-reference.md](extract-engine-reference.md) |
| Dynamic images (`IMG_` tokens) | [dynamic-images.md](dynamic-images.md) |
| Print configurator attributes on a quote; a rep's generation fails or prints blanks | [quote-line-attributes-and-rep-access.md](quote-line-attributes-and-rep-access.md) |

---

## Validation Checks

### Before generation

1. Both ODTs are Active (`IsActive: true`)
2. DocumentTemplate references correct ODT names (exact match, case-sensitive)
3. No items with null `OutputObjectName`:
   ```sql
   SELECT Id, OutputFieldName FROM OmniDataTransformItem
   WHERE OmniDataTransformationId = '<id>' AND OutputObjectName = null
   ```
4. No duplicate object query items (same Seq + OutputFieldName + FilterValue)
5. All object queries have `InputFieldName` and `FilterGroup` set
6. Field mapping paths use colons, not dots

## Platform Behavior Reference

> Full detail: **[`extract-engine-reference.md`](extract-engine-reference.md)**
> (formula catalog, filter mechanics, hierarchy semantics, array patterns, Preview API)

Verified on Release 262, API v67.0; not re-verified on the active release.
Key concepts summarized below;
read the sub-file when designing or debugging complex Extracts.

### Critical Rules (quick reference)

| Rule | Detail |
|------|--------|
| **Internal ≠ Output paths** | Object query `OutputFieldName` (join scope) is decoupled from field mapping `OutputFieldName` (JSON shape). They share colon syntax but are independent namespaces. |
| **Depth uniformity** | ALL field mappings for the same output array must read from the same internal hierarchy depth. Mixed depths → parent entries leak into child array. |
| **Redundant join for parent fields** | To get a parent's field at child level without leaking grantless parents, re-join the parent object at the child level (Seq N filtering by child FK). |
| **Section-as-conditional** | `{{#FieldName}}...{{/FieldName}}` acts as truthy/falsy gate — renders when non-empty string/array/object; skips when absent, null, false, or empty. |
| **FilterGroup = OR** | Multiple FilterGroups are UNION ALL — on nested sequences this causes N×M×G cartesian explosion. Use only on root queries. |
| **Literals must be quoted** | `FilterValue: "'Active'"` not `FilterValue: "Active"`. Unquoted literals generate no WHERE clause. |
| **No subqueries** | Cannot filter "only parents with children." Use child-first hierarchy + redundant join pattern. |
| **Transform formulas are scalar** | `FormulaResultPath` cannot target per-array-element paths. Use section-as-conditional instead. |

### Runtime permissions (owner decision, 2026-11-25)

A sales rep cannot hold `DocGenRuntimeUser` without the `DocGenDesignerPsl` licence, whichever permission set
carries it; the platform refuses the permission otherwise. `RLM_QuantumBit_Sales_Representative` therefore does
not carry it by design, and a rep who generates documents needs a separately licensed DocGen set (`DocGenUser`,
which the persona group adds). Without it `DocumentTemplate` is not visible. Do not move `DocGenRuntimeUser` into
the rep set to "fix" this.

### Formula Quick Reference

Supported: `IF`, `ISBLANK`, `CONCAT`, `SUBSTRING`, `LIST`, `FUNCTION`,
arithmetic, comparisons, `AND`/`OR`/`NOT`, `ABS`/`ROUND`/`FLOOR`/`CEILING`/`MAX`/`MIN`.

**Not supported** (saves silently, produces no output): `CASE`, `LEN`,
`UPPER`/`LOWER`, `TEXT`, `FORMAT`, `VALUE`, `MOD`, `POWER`.

### ODT Naming

Alphanumeric only (no underscores/spaces). Use camelCase: `RLMQuoteExtractBasic`.

---

## Examples

### Creating a complete template pipeline

See `data-mapper-authoring.md` for the programmatic API approach to creating
Extract + Transform ODTs with all items.

### Adding a new field to an existing template

1. **Template**: Add `{{NewField}}` token in the `.docx`
2. **Extract**: Add field mapping item — `InputFieldName: "Object:FieldApiName"`,
   `OutputFieldName: "NewField"`, `OutputObjectName: "json"`
3. **Transform**: Add pass-through — `InputFieldName: "NewField"`,
   `OutputFieldName: "NewField"`, `OutputObjectName: "json"`
4. **If field is on a new object**: Add object query item first (with proper
   Seq, InputFieldName, FilterValue, FilterGroup)
5. **Re-toggle** both ODTs (`IsActive` false → true)
6. **Upload** new `.docx` (deactivate template → replace file → reactivate)

---
---

## Deployment & Repo Integration

For the full deployment guide, see **`docs/guides/docgen-setup.md`**.

### Key points:

- **Metadata path**: `unpackaged/post_docgen/omniDataTransforms/*.rpt-meta.xml`
- **Deploy flow**: `cci flow run prepare_docgen --org dev-scratch` (10 steps)
- **Fresh-org bug**: ODT INSERT fails when formula fields referenced in
  `inputFieldName` don't exist yet. Steps 3–5 of `prepare_docgen` pre-deploy
  formula fields and seed stub ODT records as a workaround.
- **Binary fix**: `fix_document_template_binaries` uploads correct `.docx` binary
  after metadata deploy (Metadata API drops binary content on deploy).
- **Feature gate**: All steps gated by `project_config.project__custom__docgen`.
- **Context Service alternative**: `RLM_QuoteProposal_CS` uses Context Service
  instead of ODTs — see the setup guide for that path.

### Retrieve an ODT from a scratch org:

```bash
sf project retrieve start --metadata OmniDataTransform:RLMInvoiceGetDetails --target-org dev-scratch
```

Then move the retrieved `.rpt-meta.xml` to `unpackaged/post_docgen/omniDataTransforms/`.

---

## Related Skills

- `../odt-authoring/SKILL.md` — ODT architecture, mapper design, and execution patterns
- `expression-sets/SKILL.md` — Expression Set authoring (pricing procedures use
  similar Connect/Metadata API patterns)
- `repo-integration/SKILL.md` — Where to place template metadata in the repo
- `sfdmu-data-plans/SKILL.md` — Loading template/ODT records via data plans
- `docs/guides/docgen-setup.md` — Full deployment sequence, bug workarounds, Context Service
