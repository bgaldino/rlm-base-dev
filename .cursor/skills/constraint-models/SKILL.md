# Constraint Models (CML)

Working with Revenue Cloud Constraint Modeling Language models — the rules that decide
what a configurator will let a user select inside a bundle.

Covers the file layout, the four records a bundle member needs, how a change reaches an
org, and why a change can appear to deploy and still not take effect.

**Related:** `datasets/constraints/README.md` (the `export_cml` / `import_cml` /
`validate_cml` utility reference) · `.cursor/skills/expression-sets/SKILL.md` (Expression
Sets generally — constraint models are Expression Sets with `UsageType=Constraint`).

---

## Quick Rules

1. **The `.ffxblob` is plain text and it IS the artifact.** `import_cml` uploads it
   verbatim. Edit the blob.
2. **`scripts/cml/*.cml` is reference only.** Editing it changes nothing in any org. Keep
   it byte-identical to the blob (`cp` from the blob).
3. **Importing into an ACTIVE version does not redeploy the model.** The version must be
   cycled — deactivate then reactivate — after the upload. `prepare_constraints` does this
   (step 11 deactivates, step 12 reactivates). **A standalone `import_cml` does not**, so
   cycle it yourself. See [Making a change reach an org](#making-a-change-reach-an-org).
4. **Only the configurator proves deployment.** Reading `ConstraintModel` back proves the
   blob was *stored* — it is the same field `import_cml` writes. It cannot tell you the
   runtime rebuilt.
5. **A bundle member needs FOUR records, not one.** PRC row, `type` + `relation` in the
   model, an ESC `Type` association, and an ESC `Port` association.
6. **`Sequence` is part of the PRC composite key.** A Port association whose sequence
   disagrees with the SFDMU plan fails to resolve — loudly: `import_cml` warns per row,
   collects the unresolved tags and raises, so the import fails rather than half-applying.
7. **Only one QuantumBit model may be active at a time.** `QuantumBitBundle_V1` is the
   active one; Complete and PCM are imported inactive for A/B comparison.

---

## DO NOT

- **DO NOT** edit `scripts/cml/*.cml` and expect an org to change. It is documentation.
- **DO NOT** treat `.ffxblob` as binary. It is ASCII CML source (`file` reports it as
  "c program text").
- **DO NOT** report a model change as verified because `import_cml` succeeded, **or**
  because `ConstraintModel` reads back with your change in it. `import_cml` writes that
  exact field, so reading it back only proves the upload was stored. Deployment is proved
  by selecting the product in the configurator.
- **DO NOT** add a `type` without also adding its ESC `Type` **and** `Port` associations.
  A product with a PRC row but no type association appears in the bundle and then fails
  Product Validation — the failure looks like a product problem, not a model problem.
- **DO NOT** invent a `Sequence` for a new PRC row. Copy the one the SFDMU plan already
  uses for that product.
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
  *Adding New Models*).

---

## The file layout

```
datasets/constraints/qb/<Model>/
├── ExpressionSet.csv                        # the Expression Set (UsageType=Constraint)
├── ExpressionSetConstraintObj.csv           # ESC: Type + Port associations  <- the wiring
├── ExpressionSetDefinitionContextDefinition.csv
├── ExpressionSetDefinitionVersion.csv
├── Product2.csv                             # legacy Id -> Name map for remapping
├── ProductClassification.csv
├── ProductRelatedComponent.csv              # legacy Id -> composite key map
└── blobs/
    └── ESDV_<Model>_V1.ffxblob              # THE MODEL. Plain text CML.

scripts/cml/<Model>.cml                      # reference copy, byte-identical to the blob
```

Ids in these CSVs are from the **authoring** org and are placeholders. `import_cml` remaps
them: `Product2` by **Name**, `ProductRelatedComponent` by **composite key**. So the
placeholder Id only has to be internally consistent, and mnemonic ones are conventional
(`01tWt000009CMTE` → Each, `...CMTF` → Flat, `...CMTB` → Bounded).

⚠️ `QuantumBitPCM` has a blob and **no** reference `.cml`, so the blob set — not the
`.cml` set — is the authoritative inventory of shipped models.

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

### Sequence is part of the composite key

`import_cml` resolves a Port association's PRC by
`ParentProduct.Name | ChildProduct.Name | ChildProductClassification.Name |
ProductRelationshipType.Name | Sequence`, matched against the SFDMU plan in
`dataset_dirs`. **If the sequence in the constraint dir disagrees with the qb-pcm plan the
Port association will not resolve** — copy the sequence from the plan.

This fails loudly, not silently: `ImportCML` logs `Could not resolve ReferenceObjectId`
per row, accumulates `unresolved_tags`, sets `import_failed`, and raises rather than
half-applying (`tasks/rlm_cml.py:679-690`). A dry run surfaces the same warnings, which is
why the dry run is worth reading rather than just checking its exit code.

---

## Making a change reach an org

**`import_cml` uploads the blob; it does not redeploy the model.** If the target
`ExpressionSetDefinitionVersion` is already `Active`, the new model is stored and the org
keeps running the old one — and the import reports success.

```bash
# manage_expression_sets does NOT accept --org (see Known gaps) -- it uses the DEFAULT org.
# Set the default first so all three steps hit the same org.
cci org default <alias>

cci task run manage_expression_sets -o operation deactivate_versions \
    -o version_full_names "QuantumBitBundle_V1"

cci task run import_cml --org <alias> \
    -o data_dir datasets/constraints/qb/QuantumBitBundle \
    -o dataset_dirs "datasets/sfdmu/qb/en-US/qb-pcm"

cci task run manage_expression_sets -o operation activate_versions \
    -o version_full_names "QuantumBitBundle_V1"
```

`prepare_constraints` does this for you at steps 11-12; a standalone `import_cml` does
not. See below.

### How the flow handles it, and why step 11 looks redundant

`manage_expression_sets` is the right tool: `_update_version_status` queries
`ExpressionSetVersion` by `ApiName` and PATCHes `IsActive`
(`tasks/rlm_manage_expression_sets.py:527-591`) — the same record and field the Constraint
Builder UI toggles.

`prepare_constraints` orders it like this:

```
 7-10. import_cml  Complete, Server2, PCM, Bundle
11.    deactivate  -> QuantumBitComplete_V1, QuantumBitPCM_V1, QuantumBitBundle_V1
12.    activate    -> Server2_V1, QuantumBitBundle_V1
```

**Bundle appears in both step 11 and step 12 deliberately.** Steps 7–10 upload into a
version that may already be active, which stores the blob without redeploying the runtime
model; step 11 then deactivates Bundle and step 12 reactivates it, giving the
deactivate/reactivate cycle that makes the platform pick the new model up. Removing Bundle
from step 11 would make step 12 a no-op on an already-active version and the flow would
report success while the org kept running the old model. It is a no-op on a fresh build,
where versions are created inactive.

> Verified at step level on a scratch org: Bundle `true` → deactivated → `true`, with
> Complete and PCM left `false`. **Not yet verified end-to-end** — that a full flow run
> against an org with an already-active model carries a change through to the configurator
> still needs a real build, and is tracked separately.

**A standalone `import_cml` gets none of this** — it uploads and stops. That is the normal
way to ship a model change, so cycle the version yourself afterwards:

```bash
cci org default <alias>   # manage_expression_sets does not accept --org, see Known gaps

cci task run manage_expression_sets -o operation deactivate_versions \
    -o version_full_names "QuantumBitBundle_V1"
cci task run manage_expression_sets -o operation activate_versions \
    -o version_full_names "QuantumBitBundle_V1"
```

or do the same in the UI: the Constraint Model record is the `ExpressionSet` record page
(`/lightning/r/ExpressionSet/<9QL…>/view`), its **Constraint Model Versions** related list
is `ExpressionSetVersion`, and opening a version launches **Constraint Builder**, whose
toolbar carries **Sync**, **Deactivate** and **Save**.

Salesforce documents the requirement:

> "If the table data is deployed when the constraint model is activated, and you add
> records to the table after constraint model activation, to fetch the new table data at
> runtime you must deactivate and reactivate the constraint model."
> — Help, *Import Object Data* (262)

> **Not yet investigated:** the builder's **Sync** button, which is distinct from
> activate/deactivate. Its effect is unknown — do not assume it is a no-op.

---

## Examples

### Add a product to a configurable bundle

Adding `QB-CMT-TKN-BND` to `QB-COMPLETE`, mirroring its siblings:

```bash
# 1. Confirm the PRC row exists and note its Sequence (here: 25)
grep QB-CMT-TKN-BND datasets/sfdmu/qb/en-US/qb-pcm/ProductRelatedComponent.csv

# 2. Edit the BLOB (not the .cml): add a relation and a type next to the siblings
#      relation quantumbitdatabasetokencommitbounded : QuantumBitDatabaseTokenCommitBounded;
#      type     QuantumBitDatabaseTokenCommitBounded : LineItem;

# 3. Re-sync the reference copy
cp datasets/constraints/qb/QuantumBitBundle/blobs/ESDV_QuantumBitBundle_V1.ffxblob \
   scripts/cml/QuantumBitBundle.cml

# 4. Add Product2 + both ESC rows (Type and Port), reusing Sequence 25 on the PRC row
# 5. Dry run, then deactivate -> import -> activate (above)
```

### Read the deployed model back out of an org

```bash
URL=$(sf data query --use-tooling-api --target-org <alias> \
  -q "SELECT ConstraintModel FROM ExpressionSetDefinitionVersion WHERE DeveloperName='QuantumBitBundle_V1'" \
  --json | python3 -c "import json,sys; print(json.load(sys.stdin)['result']['records'][0]['ConstraintModel'])")
INST=$(sf org display --target-org <alias> --json | python3 -c "import json,sys; print(json.load(sys.stdin)['result']['instanceUrl'])")
TOK=$(sf org display --target-org <alias> --json | python3 -c "import json,sys; print(json.load(sys.stdin)['result']['accessToken'])")
curl -s -H "Authorization: Bearer $TOK" "$INST$URL" | grep "TokenCommitBounded"
```

---

## Validation Checks

Before calling a constraint-model change done:

1. `cci task run validate_cml -o cml_dir scripts/cml -o data_dir <dir>` → **0 errors**
   (warnings are noisy and largely pre-existing; the error count is the signal).
2. Blob and reference `.cml` byte-identical: `diff -q <blob> scripts/cml/<Model>.cml`.
3. Dry-run import resolves your new rows to **real org Ids**, and you queried those Ids
   back to confirm they are the records you meant — not just that something resolved.
4. Deactivate → import → activate actually run, in that order.
5. `ConstraintModel` reads back with your change in it (recipe above). Note what this
   does **not** prove: `import_cml` writes that same field, so it confirms the upload was
   stored and nothing more. It cannot distinguish "stored" from "deployed".
6. Diff the **expected** set against the org rather than listing what is there:
   ```bash
   sf data query --target-org <alias> \
     -q "SELECT ConstraintModelTag, ConstraintModelTagType FROM ExpressionSetConstraintObj"
   ```
   then assert every product you expect has **both** a `Type` and a `Port` row.
7. **Select the product in the configurator UI.** This is the only check that proves the
   runtime model was rebuilt. Nothing above distinguishes a deployed model from a stored
   one, so this step is not optional — it is the verification.

---

## Known gaps

- **`manage_expression_sets` rejects `--org`** and runs against the default org. One
  instance of a repo-wide problem (102 of 193 custom tasks). `import_cml`, `export_cml`
  and `validate_cml`'s siblings do accept it.
- **`validate_cml` emits ~1,779 warnings** on the QuantumBit models, nearly all
  pre-existing "missing type association for leaf type". Errors are the usable signal;
  the warning stream is not yet clean enough to gate on.
- **A standalone `import_cml` never cycles the version.** `prepare_constraints` covers
  this at steps 11-12, but shipping a model change usually means running `import_cml` on
  its own — where the upload lands and nothing redeploys. There is no single task that
  does import-and-cycle.
- **No signal distinguishes "stored" from "deployed".** `ConstraintModel` is the upload
  field, so only the configurator can confirm a rebuild. A deployment-specific signal
  would make this verifiable without a click.
- **The builder's `Sync` button is uninvestigated.**
