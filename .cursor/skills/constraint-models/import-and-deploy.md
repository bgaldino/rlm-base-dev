# Importing, cycling and moving constraint models

How a model change gets from the repo (or another org) into an org and onto the solver.
Read the parent [SKILL.md](SKILL.md) first for the four records a bundle member needs and
the Quick Rules. This file holds the depth: why an import can fail half-way, the
deactivate, import, activate cycle, and moving a model between orgs.

**Contents:** [Sequence is part of the composite key](#sequence-is-part-of-the-composite-key) ·
[Making a change reach an org](#making-a-change-reach-an-org) ·
[Active models and downtime](#active-models-and-downtime) ·
[Moving a model between orgs](#moving-a-model-between-orgs) ·
[Writing models programmatically](#writing-models-programmatically)

---

## Sequence is part of the composite key

`import_cml` resolves a Port association's PRC in two hops, and neither one reads the
SFDMU plan's PRC rows:

1. **Legacy Id → composite key**, built from the **constraint dir's own**
   `ProductRelatedComponent.csv` (`tasks/rlm_cml.py:842-854`), as
   `ParentProduct.Name | ChildProduct.Name | ChildProductClassification.Name |
   ProductRelationshipType.Name | Sequence`.
2. **Composite key → real Id**, matched against `ProductRelatedComponent` records
   **queried from the target org** (`tasks/rlm_cml.py:868-892`).

`dataset_dirs` contributes only candidate *names* — products, classifications and PRC
parents — and those merely scope the org lookups, here as
`WHERE ParentProduct.Name IN (…) OR Name IN (…)`. It never supplies a composite key.

**So the sequence in the constraint dir has to match the PRC row the org actually holds.**
The plan matters because it is what loads that row — which is why copying the sequence
from the plan is the right authoring move. But when a Port fails to resolve, **query the
org**; do not diff the two CSVs. An org whose plan was never loaded, or was loaded from a
different revision, disagrees with the plan on disk.

It fails loudly rather than silently — `ImportCML` logs `Could not resolve
ReferenceObjectId` per row and accumulates `unresolved_tags` — but **it does not fail
atomically**, and the distinction matters when you are recovering.

`create_record()` is called inline for every row as the loop walks the ESC list, so by the
time a failure is diagnosed the rows that *did* resolve are already in the org. Step 6
(delete the old ESC records) is skipped on a failed import, so the previous generation of
rows is still there too. The task says so itself: *"Import had errors -- skipping deletion
of old ESC records. Target org may contain a mix of old and new constraints."*

**Two failure modes. Both now fail loudly** — they did not always:

| Failure | Raises? | Org left holding |
|---|---|---|
| A reference will not resolve (bad `Sequence`, missing product) | **yes** (not in `dry_run`) | every pre-existing ESC row, plus whatever was created before the failure; blob **not** uploaded |
| `create_record()` fails but every reference resolved | **yes** (not in `dry_run`) | same |

Usually that means a *mix* of old and new — but not always: if every create failed there
are no new rows, and on a model with no prior rows there is no old generation to mix with.
Query the ESC set rather than assuming.

Both converge on `describe_esc_import_failure()` in `tasks/rlm_cml.py`, and steps 6-7 run
through `_finalize_esc_import()`. The raise happens *after* the "skipping deletion of old
ESC records" warning and *before* the blob upload, so the model is never uploaded over a
partial ESC set. **A `dry_run` logs the same diagnosis at error level and does not raise** —
it wrote nothing, so nothing is left behind.

> ⚠️ **Before this fix, the second mode exited 0.** `unresolved_tags` was empty so the raise
> never fired: the blob uploaded, `Import complete` logged, and the task returned success
> over a partial set. `prepare_constraints` runs `import_cml`, so a build could go green
> carrying a partial constraint model. If you are reading logs from an older build, an
> `Import complete` there does **not** mean every ESC row landed.

**A clean rerun cleans up after either failure.** The existing-ESC snapshot is taken fresh
at the top of every run (`WHERE ExpressionSetId = …`, unfiltered otherwise), so it captures
the old generation *and* the partial rows left by the failed run; a pass that resolves and
creates everything then deletes the whole snapshot. Fix the cause and rerun — you do not
have to clear the mix by hand.

What does not self-correct is a rerun that *also* fails: the delete is skipped again and
another partial generation layers on. So if the import errored, rerun until one pass is
clean.

A dry run surfaces the resolution warnings without touching the org, which is why it is
worth reading rather than just checking its exit code. That holds for a model the org
already has; for a new model a dry run stops before resolving any row (Validation
check 3).
---

## Making a change reach an org

**`import_cml` uploads the blob; it does not redeploy the model.** If the target
`ExpressionSetDefinitionVersion` is already `Active`, the new model is stored and the org
keeps running the old one — and the import reports success.

```bash
# Pass the same --org to all three steps so they hit the same org.
# <Version>  = the ApiName from the discovery query, e.g. QuantumBitBundle_V1
# <DataDir>   = the model's directory under datasets/constraints/, from `ls -d`
# <PlanDir>   = the SFDMU plan that loaded the ESC's Product2/PRC rows into the org
#               (it supplies the names that scope import_cml's lookup queries)
cci task run manage_expression_sets --org <cci_alias> -o operation deactivate_versions \
    -o version_full_names "<Version>"

cci task run import_cml --org <cci_alias> \
    -o data_dir <DataDir> \
    -o dataset_dirs "<PlanDir>"

cci task run manage_expression_sets --org <cci_alias> -o operation activate_versions \
    -o version_full_names "<Version>"
```

<details><summary>Filled in for the QuantumBit bundle, as an example</summary>

```bash
cci task run manage_expression_sets --org <cci_alias> -o operation deactivate_versions \
    -o version_full_names "QuantumBitBundle_V1"
cci task run import_cml --org <cci_alias> \
    -o data_dir datasets/constraints/qb/QuantumBitBundle \
    -o dataset_dirs "datasets/sfdmu/qb/en-US/qb-pcm"
cci task run manage_expression_sets --org <cci_alias> -o operation activate_versions \
    -o version_full_names "QuantumBitBundle_V1"
```

</details>

`prepare_constraints` does this for you at steps 9-10; a standalone `import_cml` does
not. See below.

### How the flow handles active-version reruns

`manage_expression_sets` queries `ExpressionSetVersion` by ApiName. For a constraint model
(`ExpressionSet.UsageType = 'Constraint'`) it PATCHes
`/services/data/v<api>/industries/constraints/{expressionSetId}/versions/{versionId}` with
`{"status": "Active"}` or `{"status": "Inactive"}`. That resource deploys the model to the
constraint solver on activation (along with every other active constraint model) and removes
it on deactivation. It returns HTTP 200 with `success: false` on a failed deploy, so the task
checks `success`. Every other expression set gets an `IsActive` PATCH.

An **already-Active** version is skipped, and for a constraint model the task warns that
the skip doesn't redeploy anything: `activate_versions` alone never picks up a re-import, so
always deactivate first. Cycling only the model you changed is enough, even on a cold
solver, because activating one constraint model deploys every active one (checked live in
both directions with QuantumBitBundle and Server2).

The resource is not in the public developer guide; it is the route Constraint Builder uses,
and nothing else deploys a model. Measured live on 2026-10-29: when the task still
PATCHed `IsActive` for constraint models, a model re-imported into an active version kept
running the old one through this exact cycle, and a cold org stayed cold after activation.

`prepare_constraints` imports Server2 and Bundle in steps 7-8, deactivates their
versions in step 9, and activates both in step 10. Every activated version must
also be deactivated first: an import into an active version stores the blob without
redeploying the runtime, and activation alone would be a no-op. The cycle is a
no-op on a fresh build where imports create inactive versions.

**A standalone `import_cml` gets none of this** — it uploads and stops. That is the normal
way to ship a model change, so cycle the version yourself afterwards:

```bash
# <Version> is the ApiName from the discovery query — e.g. QuantumBitBundle_V1,
# Server2_V1, or whatever the org actually reports as active for the model you changed.
cci task run manage_expression_sets --org <cci_alias> -o operation deactivate_versions \
    -o version_full_names "<Version>"
cci task run manage_expression_sets --org <cci_alias> -o operation activate_versions \
    -o version_full_names "<Version>"
```

Cycle **the version you imported into**. If several models are active, cycling an
unrelated one proves nothing and briefly deactivates a model something else may depend on.

or do the same in the UI: the Constraint Model record is the `ExpressionSet` record page
(`/lightning/r/ExpressionSet/<9QL…>/view`), its **Constraint Model Versions** related list
is `ExpressionSetVersion`, and opening a version launches **Constraint Builder**, whose
toolbar carries **Sync**, **Deactivate** and **Save**.

Salesforce documents the requirement:

> "If the table data is deployed when the constraint model is activated, and you add
> records to the table after constraint model activation, to fetch the new table data at
> runtime you must deactivate and reactivate the constraint model."
> — Help, *Import Data from Salesforce Objects to Use in Constraint Models* (264)

> **Not yet investigated:** the builder's **Sync** button, which is distinct from
> activate/deactivate. Its effect is unknown — do not assume it is a no-op.
---

## Active models and downtime

An active model cannot take an in-place update: the version must be inactive when the
model is written, and activation runs the compile and validation checks before it deploys
to the solver `[Help: deployment-product-configurator-additional-info, 264]`. So the cycle
above leaves the model inactive between the two calls, and activating one constraint
model redeploys every active one (checked live in both directions on two models, per the earlier skill text). No supported
option updates an active model without that window `[Open: no such option found in Help,
the repo or the resource; not measured]`. To shorten it, script both calls back to back
for each changed model, one model at a time, and check `success` in the body of each
response (HTTP 200 does not mean the deploy worked).

Never flip `ExpressionSetVersion.IsActive` to cycle a constraint model. It skips
compilation and validation, and it can leave the solver's cached copy out of step with the
record: a model deactivated that way can keep running `[Platform behaviour, traced]`. Use
the constraint-version resource, or the Constraint Builder buttons (Constraint Models page
of the ExpressionSet).

## Moving a model between orgs

No supported tool moves a constraint model between orgs on its own. Metadata API
retrieve and deploy carry the `ExpressionSetDefinition` shell without the CML body or the
`ExpressionSetConstraintObj` rows, so a change set or a DevOps tool alone is not enough
`[Help: deployment-product-configurator-additional-info, 264; meta_expressionsetdefinition]`.
The repo's tasks do the whole move over the data and Tooling APIs:

1. Load the PCM data the model references into the target first (products, classifications,
   product related components). The import matches products by Name and components by
   composite key, so the target must hold them
   (see [Sequence is part of the composite key](#sequence-is-part-of-the-composite-key)).
2. `export_cml` from the source into a data dir (writes the blob, the ESC rows and the
   id-to-name maps), then check the dir with `validate_cml`
   `[Repo: datasets/constraints/README.md]`.
3. `import_cml` into the target, with `dataset_dirs` naming the plan that loaded the PCM rows.
4. Deactivate, then activate, the imported version ([above](#making-a-change-reach-an-org)).
5. Prove it with the headless `configure` check
   ([Validation Checks](SKILL.md#validation-checks), check 7).

A manual one-off also works: create the shell by Metadata API, paste the CML text in
Constraint Builder, then recreate the association rows by data load. It is error-prone for a
large model.

## Writing models programmatically

An integration that generates CML (for example from a PLM export) can use the same path the
repo's tasks use `[Repo: tasks/rlm_cml.py]`: create the `ExpressionSet`
(`UsageType = Constraint`), write the model text (base64) to
`ExpressionSetDefinitionVersion.ConstraintModel` while the version is inactive, create the
`ExpressionSetConstraintObj` rows, then activate through the constraint-version resource.
The Metadata API does not carry the CML body, and the constraint-version resource and the
Constraint Studio APIs are not in the 264 developer guide; public documentation is planned
for a later release `[Open: planned for 268 per internal tracking; check the release's
developer guide]`. `scripts/constraint_models/cml_tool.py push` does this for a single
model ([tooling.md](tooling.md)).

Writing the field directly does not validate the CML: a sObject write stored an invalid or
oversized model without error, and only activation or the save path reports problems
(see [size-and-limits.md](size-and-limits.md)). Always run `validate_cml` or activate and
read the result.
