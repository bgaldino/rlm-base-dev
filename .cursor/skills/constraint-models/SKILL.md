---
name: constraint-models
description: >-
  Author, deploy, and diagnose Revenue Cloud Constraint Modeling Language (CML) bundle
  rules. Use when editing constraint .ffxblob artifacts, wiring bundle members,
  importing models, or investigating why configurator behavior did not change after
  deployment.
---

# Constraint Models (CML)

Revenue Cloud Constraint Modeling Language models: the rules that decide what a
configurator lets a user select inside a bundle. Covers the file layout, the four records
a bundle member needs, how a change reaches an org, size limits, runtime behavior, and
tooling (`scripts/constraint_models/`).

**Related:** `datasets/constraints/README.md` (the `export_cml` / `import_cml` /
`validate_cml` utility reference) · `.cursor/skills/expression-sets/SKILL.md` (Expression
Sets generally — constraint models are Expression Sets with `UsageType=Constraint`).

---

## Quick Rules

1. **The `.ffxblob` is plain text and it IS the artifact.** `import_cml` uploads it
   verbatim. Edit the blob.
2. **Validate the dataset you will import.** Pass `validate_cml -o data_dirs <directory>`
   to check its shipped blob against its own associations. Standalone `.cml` files
   require an explicit `cml_dir`; they are not deployment artifacts.
3. **Importing into an ACTIVE version does not redeploy the model.** The version must be
   cycled — deactivate then reactivate — after the upload, **through the constraint-version
   resource**, which is what `manage_expression_sets` uses for constraint models. A plain
   `ExpressionSetVersion.IsActive` update (sObject API, `sf data update`) flips the record but
   never reaches the solver, so the org keeps running the old model. `prepare_constraints`
   cycles the models it names. **A standalone `import_cml` does not**, so cycle it yourself.
   See [Making a change reach an org](#making-a-change-reach-an-org).
4. **Only the configurator proves deployment.** Reading `ConstraintModel` back proves the
   blob was *stored* — it is the same field `import_cml` writes. It cannot tell you the
   runtime rebuilt.
5. **A bundle member needs FOUR records, not one.** PRC row, `type` + `relation` in the
   model, an ESC `Type` association, and an ESC `Port` association.
6. **`Sequence` is part of the PRC composite key.** A Port association whose sequence
   disagrees with the PRC row **in the target org** fails to resolve — the SFDMU plan
   matters only because it is what loads that row. `import_cml` warns per row and raises —
   but **it half-applies first**: rows that did resolve are already created and the old
   ESC rows are not deleted. The blob is not uploaded, and a clean rerun clears the mix,
   so fix the cause and run it again.
7. **Do not activate overlapping models.** The shipped QB build uses Bundle for
   software and Server2 for hardware. Discover the org's active models before
   changing versions; unrelated model families can be active together.
8. **Runtime users must be able to see the model's `ExpressionSet` record.** On a cold
   solver (every template-spun org, since the cache is keyed by org; also any org whose models
   were activated by an `IsActive` update), the first configuration-rules run redeploys
   the models as the running user and reads the `ExpressionSet` rows in user mode. The
   criteria sharing rule `ExpressionSet.RLM_Constraint_Models_Read` in `post_constraints`
   shares `UsageType = Constraint` sets Read with all internal users. Without it, every
   non-admin fails with "Something went wrong while running configuration rules" until an
   admin runs the rules once. See [troubleshooting → Constraints / CML Errors](../troubleshooting/SKILL.md#constraints--cml-errors).

---

## DO NOT

- **DO NOT** edit a standalone `.cml` file and expect an org to change. Edit the dataset blob.
- **DO NOT** treat `.ffxblob` as binary. It is ASCII CML source (`file` reports it as
  "c program text").
- **DO NOT** report a model change as verified because `import_cml` succeeded, **or**
  because `ConstraintModel` reads back with your change in it. `import_cml` writes that
  exact field, so reading it back only proves the upload was stored. Deployment is proved
  by selecting the product in the configurator.
- **DO NOT** add a **bundle member** without both its ESC `Type` **and** `Port`
  associations. A product with a PRC row but no `Type` association appears in the bundle
  and then fails Product Validation — the failure looks like a product problem, not a
  model problem. (`Port` is per bundle **relation**, not per type — a cart-level or
  virtual-quote type has no port. See below.)
- **DO NOT** invent a `Sequence` for a new PRC row. Copy the one the SFDMU plan already
  uses for that product — and if the Port still fails to resolve, check the **org**, which
  is what `import_cml` matches against.
- **DO NOT** activate a second QuantumBit model without deactivating the current one.
  `manage_expression_sets` toggles only the versions you name; it does not auto-deactivate
  others.

---

## Entry Conditions

Use this skill when you are:

- adding or removing a product from a configurable bundle's constraint model;
- editing CML types, relations, attributes or rules;
- debugging "product fails Product Validation when selected" in the configurator;
- debugging a model change that deployed but did not take effect;
- adding a whole new constraint model (see `datasets/constraints/README.md` →
  *Adding New Models*);
- sizing a bundle's component quantities from attribute answers (see
  [Sub-Files](#sub-files)).

---

## <a name="discovering-what-you-are-working-with"></a>Discovering what you are working with

**Do not hardcode a model name from this or any other document.** The set of constraint
models differs per org and per feature flag, and grows as verticals are added. Three
sources, in the order you should consult them:

**1. What the org actually has** — authoritative for anything you are about to change:

```bash
# every constraint model and its active state
sf data query --target-org <sf_alias_or_username> -q "
  SELECT ExpressionSet.ApiName, ApiName, VersionNumber, IsActive
  FROM ExpressionSetVersion
  WHERE ExpressionSet.UsageType = 'Constraint'
  ORDER BY ExpressionSet.ApiName"
```

`ExpressionSet.UsageType = 'Constraint'` is the discriminator — that, not the name, is what
makes something a constraint model.

> **Two registries, two placeholders.** CCI and the `sf` CLI keep *separate* alias lists —
> a CCI alias `beta` is `rlm-base__beta` to `sf`. Recipes below use `<cci_alias>` with
> `cci … --org` and `<sf_alias_or_username>` with `sf … --target-org`; they are not
> interchangeable. See `AGENTS.md` → *Org Identity: CCI vs SF CLI*.

**2. What the repo ships** — authoritative for a fresh build, and the inventory a build
will import:

```bash
ls -d datasets/constraints/*/*/          # one directory per model, grouped by vertical
find datasets/constraints -name '*.ffxblob'
```

The **blob** set is the model inventory and the only checked-in CML source.

**3. What the flow imports and activates** — authoritative for what a build will end up
with, and the list to edit when adding a model:

```bash
cci flow info prepare_constraints    # import_cml steps, then the deactivate/activate lists
```

Adding a model means adding it to the data dir, the import steps, **and** the
activate/deactivate lists — see `datasets/constraints/README.md` → *Adding New Models*.

---

## The file layout

```
datasets/constraints/<vertical>/<Model>/     # e.g. qb/QuantumBitBundle, mfg/fuelCell
├── ExpressionSet.csv                        # the Expression Set (UsageType=Constraint)
├── ExpressionSetConstraintObj.csv           # ESC: Type + Port associations  <- the wiring
├── ExpressionSetDefinitionContextDefinition.csv
├── ExpressionSetDefinitionVersion.csv
├── Product2.csv                             # legacy Id -> Name map for remapping
├── ProductClassification.csv
├── ProductRelatedComponent.csv              # legacy Id -> composite key map
└── blobs/
    └── ESDV_<Model>_V1.ffxblob              # THE MODEL. Plain text CML.
```

Ids in these CSVs are from the **authoring** org and are placeholders. `import_cml` remaps
them: `Product2` by **Name**, `ProductRelatedComponent` by **composite key**. So the
placeholder Id only has to be internally consistent, and mnemonic ones are conventional
(`01tWt000009CMTE` → Each, `...CMTF` → Flat, `...CMTB` → Bounded).

### What this repo ships today

The 264 QB build imports and activates `QuantumBitBundle` and `Server2`, from their
respective directories under `datasets/constraints/qb/`. Manufacturing examples
remain under `datasets/constraints/mfg/` for standalone import. Discover live state
with the queries above; the blob and flow inventories supersede this snapshot.

---

## The four records a bundle member needs

Adding a product to a configurable bundle is not one change. Missing any of these fails
differently, and only the first is obvious:

| # | Record | Where | Symptom if missing |
|---|--------|-------|--------------------|
| 1 | `ProductRelatedComponent` | `datasets/sfdmu/qb/en-US/qb-pcm/ProductRelatedComponent.csv` | Product never appears in the bundle |
| 2 | `type` + `relation` | the `.ffxblob` | Model has no concept of the product |
| 3 | ESC association, `ConstraintModelTagType = Type` | `ExpressionSetConstraintObj.csv` | **Product appears, then fails Product Validation** |
| 4 | ESC association, `ConstraintModelTagType = Port` | `ExpressionSetConstraintObj.csv` | Relation is not bound to the bundle component |

**#3 is the one that bites.** With #1 present and #3 missing, the configurator offers the
product because the bundle says it is a component, then rejects it because the model has
no type for it. Nothing points at the constraint model.

`Type` associations reference a **Product2** (`01t` prefix); `Port` associations reference
a **ProductRelatedComponent** (`0dS` prefix).

### Ports are per bundle relation, not per type

Only types reachable as **bundle members** get a `Port`. The counts make the rule visible —
Port count tracks `relation` count, not `type` count:

| Model | Type | Port | `relation`s in the CML |
|---|---:|---:|---:|
| `Server2` | 41 | 40 | 40 |
| `QuantumBitBundle` | 33 | 28 | 29 |

Bundle's 29 relations against 28 Ports is the same distinction in miniature — the odd one
is `lineitems` on the `@(virtual = "true") Quote` container, a cart-level relation rather
than a bundle component, so it has no Port either.

**So the four-record rule above applies to bundle members.** For a cart-level or
virtual-quote type, records 1 and 4 (the PRC row and the `Port` association) do not
apply.

### Sequence is part of the composite key

`import_cml` resolves a Port association's `ProductRelatedComponent` through a composite
key that includes `Sequence`. Details and failure modes: [import-and-deploy.md](import-and-deploy.md#sequence-is-part-of-the-composite-key).

## Making a change reach an org

**`import_cml` uploads the blob; it does not redeploy the model.** If the target
`ExpressionSetDefinitionVersion` is already `Active`, the new model is stored and the org
keeps running the old one, and the import reports success. Deactivate, import, activate
through the constraint-version resource (a plain `IsActive` update does not deploy).
Commands, the rerun behavior of `prepare_constraints`, downtime, moving a model between
orgs and writing models programmatically:
[import-and-deploy.md](import-and-deploy.md).

## Ramp groups and segments

Rules that target quote groups, ramp groups and ramp segments: [ramp-groups.md](ramp-groups.md).

---

## Sub-Files

| File | Read this when... |
|---|---|
| [`import-and-deploy.md`](import-and-deploy.md) | A model change did not take effect; you need the import, deactivate and activate cycle, the composite-key rules, downtime, moving a model between orgs, or writing models from a script. |
| [`size-and-limits.md`](size-and-limits.md) | A save fails with "size limit for this constraint model", or before importing a large catalog into CML: the org-value limit, the save-path-only check, other limits, how to stay under. |
| [`configurator-behavior.md`](configurator-behavior.md) | A rule is correct but the configurator or Place behaves differently: clear-on-hide, productField rules, PST defaults and validation, error logs, triggers. |
| [`computed-attribute-and-setup.md`](computed-attribute-and-setup.md) | A CML-computed value must reach a quote line field, a rule should cover a whole classification, or a new test product must reach Configure. |
| [`tooling.md`](tooling.md) | You want to check model size, push a model, or scaffold a test classification, products and model from a spec (`scripts/constraint_models/cml_tool.py`). |
| [`ramp-groups.md`](ramp-groups.md) | A group-ramp quote must obey a constraint model. |
| [`quantities-from-attributes.md`](quantities-from-attributes.md) | A model must set component quantities from answers on the bundle (per unit, per N rounded up, zero unless chosen, chained derivations), with `@(split = false)`, `maxRelationSize`, rounding, `parent()`, exclusions, cross-line `Quote` checks, amendments, `Info` messages and headless testing. Read it before writing `ceil()`, `/` or `^` in CML. |

---

## Examples

### Add a product to a configurable bundle

Worked example — adding `QB-CMT-TKN-BND` to `QB-COMPLETE` in the `QuantumBitBundle` model. Substitute your own model and product; the shape is the same
for any vertical.

```bash
# 1. Confirm the PRC row exists and note its Sequence (here: 25)
grep QB-CMT-TKN-BND datasets/sfdmu/qb/en-US/qb-pcm/ProductRelatedComponent.csv

# 2. Edit the dataset BLOB: add a relation and a type next to the siblings
#      relation quantumbitdatabasetokencommitbounded : QuantumBitDatabaseTokenCommitBounded;
#      type     QuantumBitDatabaseTokenCommitBounded : LineItem;

# 3. Add Product2 + both ESC rows (Type and Port), reusing Sequence 25 on the PRC row
# 4. Validate the shipped blob, then deactivate -> import -> activate (above)
```

### Read the deployed model back out of an org

```bash
URL=$(sf data query --use-tooling-api --target-org <sf_alias_or_username> \
  -q "SELECT ConstraintModel FROM ExpressionSetDefinitionVersion WHERE DeveloperName='QuantumBitBundle_V1'" \
  --json | python3 -c "import json,sys; print(json.load(sys.stdin)['result']['records'][0]['ConstraintModel'])")
INST=$(sf org display --target-org <sf_alias_or_username> --json | python3 -c "import json,sys; print(json.load(sys.stdin)['result']['instanceUrl'])")
TOK=$(sf org auth show-access-token --target-org <sf_alias_or_username> --json | python3 -c "import json,sys; print(json.load(sys.stdin)['result']['accessToken'])")  # sf org display redacts it
curl -s -H "Authorization: Bearer $TOK" "$INST$URL" | grep "TokenCommitBounded"
```

---

## Validation Checks

Before calling a constraint-model change done:

1. `cci task run validate_cml -o data_dirs <dir>[,<dir>…]` → **0 errors** (an error now
   fails the task). This checks each dir's shipped `.ffxblob`, the exact file `import_cml`
   uploads, against its own ESC rows (warnings are largely
   pre-existing; the error count is the signal).
2. Check the shipped blob directly; there is no reference-copy sync step.
3. Dry-run import resolves your new rows to **real org Ids**, and you queried those Ids
   back to confirm they are the records you meant — not just that something resolved.
   A dry run can't do this for a model the org doesn't have yet: it creates no
   `ExpressionSet`, so it stops at "Could not find ExpressionSetDefinitionVersion for
   <name>" before resolving any row (measured 2026-11-11, fresh 264 `ent-sb0` scratch org).
   The task logs that at error level and returns without raising
   (`tasks/rlm_cml.py`), so read the log, not the exit code. For a new model the first
   import is a real run: read its resolution warnings, then query the ESC rows
   (check 6).
4. Deactivate → import → activate actually run, in that order.
5. `ConstraintModel` reads back with your change in it (recipe above). Note what this
   does **not** prove: `import_cml` writes that same field, so it confirms the upload was
   stored and nothing more. It cannot distinguish "stored" from "deployed".
6. Diff the **expected** set against the org rather than listing what is there — and
   **scope the query to the model you changed**. Model tags can overlap, so an unscoped query lets a tag missing from
   one model be masked by another model's row:
   ```bash
   sf data query --target-org <sf_alias_or_username> -q "
     SELECT ConstraintModelTag, ConstraintModelTagType
     FROM ExpressionSetConstraintObj
     WHERE ExpressionSet.ApiName = '<Model>'"
   ```
   then assert every product you expect has **both** a `Type` and a `Port` row.
7. **Exercise the configuration rules.** This is what proves the runtime model was
   rebuilt — nothing above distinguishes a deployed model from a stored one. It does
   **not** require the UI: POSTing the Product Configurator `configure` action with
   `executeConfigurationRules: true` against a quote line that uses the model runs the
   solver's current model headlessly. To prove a specific change, make it observable (for
   example a `message(true, "<marker>", "warning")` rule) and look for it in the response's
   `messages`. A valid configuration returns `success: true`,
   `solverStatus: "success"`, `errors: []`, and no `RevenueTransactionErrorLog` row on the
   quote carries a constraint's failure message; an invalid model returns `Model '…' is invalid`. A
   configuration the rules reject can still return `success: true`, with its message only
   in the error log: read both, as in
   [quantities-from-attributes.md → Reading a result](quantities-from-attributes.md#reading-a-result).
   Full recipe: [Runtime verification](../../../datasets/constraints/README.md#runtime-verification).

---

## Known gaps

- **`validate_cml`'s warning stream is not clean enough to gate on.** Treat the **error**
  count as the signal and compare warnings against a known-good baseline. The validator
  reads any `<identifier> =` or `<identifier> ==` on a declaration, `constraint` or
  `message` line as an annotation key (`ANNOTATION_KEY_RE` in `tasks/rlm_cml.py`), so
  `int plots = [1..120];` warns "Unsupported annotation 'plots'". Models with such warnings
  imported, activated and ran on fresh 264 `ent-sb0` scratch orgs. A virtual `Quote`
  container also draws "Missing port association" and "Missing type association"; its
  relations have no `Port` by design.
- **A standalone `import_cml` never cycles the version**; `prepare_constraints` does
  (steps 9-10). No single task does import-and-cycle; `cml_tool.py push` does for one file
  ([tooling.md](tooling.md)).
- **No passive signal distinguishes "stored" from "deployed".** Run a configurator
  `configure` POST (Validation check 7).
- **`import_cml` still half-applies on failure.** Both failure modes raise (outside
  `dry_run`) and neither uploads the blob, but rows already created stay. A clean rerun
  clears the mix; a failing rerun layers another partial generation. Staging the writes is
  the real fix.
- **The builder's `Sync` button is uninvestigated.**
- **Unmeasured items** are tagged `[Open]` in the sub-files; the scaffold's constraint-row
  step and `size` against live models need a scratch org with the Constraints Engine
  setting enabled.
