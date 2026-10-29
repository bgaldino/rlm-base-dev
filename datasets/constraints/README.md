# Constraint model utilities

CML models are imported and exported by the CCI tasks in `tasks/rlm_cml.py`.
Their `.ffxblob` files are **plain-text CML** and are uploaded verbatim. Edit the
blob in the model's dataset directory; a `.cml` example does not deploy to an org.

## Shipped models

| Model | Directory | Type tags | Port tags | Imported by `prepare_constraints` |
|---|---|---:|---:|---|
| QuantumBitBundle | `qb/QuantumBitBundle/` | 33 | 28 | Yes, activated |
| Server2 | `qb/Server2/` | 41 | 40 | Yes, activated |
| GeneratorSet | `mfg/genSet/` | See CSV | See CSV | No; standalone import |
| Fuel_Cell | `mfg/fuelCell/` | See CSV | See CSV | No; standalone import |

The QB build ships two models only. Bundle provides the software bundle and
virtual-quote cart rules; Server2 provides hardware configuration for QB-QRack-750.
There are no import, export, activation, deactivation, or compatibility steps for
retired models. Manufacturing datasets remain available through generic CCI tasks;
there is no `import_mfg_cml` flow or dedicated manufacturing export task.

## Data layout

Each model directory contains:

```text
ExpressionSet.csv
ExpressionSetConstraintObj.csv
ExpressionSetDefinitionContextDefinition.csv
ExpressionSetDefinitionVersion.csv
Product2.csv
ProductClassification.csv
ProductRelatedComponent.csv
blobs/ESDV_<Model>_V1.ffxblob
```

CSV IDs belong to the authoring org. Import remaps Product2 and
ProductClassification by name and ProductRelatedComponent by its composite key:
parent product, child product, child classification, relationship type, and
**Sequence**. Copy the Sequence from the actual catalog relationship; inventing one
prevents a Port association from resolving. `dataset_dirs` supplies additional
candidate names for org queries; it does not replace the model's reference maps.

A bundle component needs a catalog ProductRelatedComponent, a CML type and
relation, a Type association, and a Port association. Cart-level types need no
Port. Bundle has 29 relations but 28 Ports because the virtual Quote's `lineitems`
relation is cart-level.

## CCI integration

Use the generated [`prepare_constraints` flow reference](../../.cursor/skills/cci-orchestration/flows-reference.md#prepare_constraints)
for current ordering, task options, and guards. The `constraints` flag controls
metadata, permissions, and context setup; its transaction-processing seed also
requires `quantumbit`. The independent `constraints_data` flag controls Robot
settings, validation, import, and activation; model operations also require `qb`.
Load the catalog and its product relationships before importing the model maps.

Uploading into an active version stores the blob without rebuilding its runtime.
The deactivate/reactivate pair therefore includes **both** Bundle and Server2 on
every rerun. `manage_expression_sets` runs that pair through the constraint-version
resource, which deploys to the solver; a plain `ExpressionSetVersion.IsActive` update
does not. A standalone `import_cml` does not cycle the version.

The flags live in `project.custom` in `cumulusci.yml`; they are not flow options.
Both constraint flags are normally enabled, but the current metadata and sample-data
steps retain their separate guards.

## Validate

```bash
cci task run validate_cml \
    -o data_dirs "datasets/constraints/qb/Server2,datasets/constraints/qb/QuantumBitBundle"
```

`data_dirs` validates the exact blob named by each directory's
ExpressionSetDefinitionVersion.csv against that directory's own ESC rows. Missing,
extra, or misnamed blobs and missing/empty required CSVs are errors. Validation runs
before any model import. Require zero errors; annotation warnings can be compared
with the retained-model baseline.

For standalone `.cml` files, explicitly pass `-o cml_dir <directory>` and optionally
`-o data_dir <model-dataset>` for association checks. There is no default reference
directory. These options do not replace shipped-blob validation.

## Import and activate

```bash
cci task run import_cml --org <cci_alias> \
    -o data_dir datasets/constraints/qb/QuantumBitBundle \
    -o dataset_dirs "datasets/sfdmu/qb/en-US/qb-pcm" \
    -o dry_run true
```

Remove `-o dry_run true` to apply. Import:

1. Upserts the ExpressionSet by ApiName. Creating a Constraint ExpressionSet
   auto-provisions its backing definition and V1 versions; no ESD metadata is needed.
2. Resolves the ExpressionSetDefinitionVersion and upserts its context association.
3. Resolves polymorphic references and creates the new ESC associations.
4. Deletes old ESC rows and uploads the blob **only when the new association set succeeds**.

A failed non-dry-run import raises before uploading the blob. Association creation
is not atomic: a failed run can leave new rows beside old ones. Fix the resolution
or creation error and rerun; a clean import replaces the complete previous set.

For an active-version rerun, cycle the imported version:

```bash
# manage_expression_sets uses the DEFAULT CCI org, not a --org option.
cci org default <cci_alias>
cci task run manage_expression_sets -o operation deactivate_versions \
    -o version_full_names "QuantumBitBundle_V1"
cci task run import_cml --org <cci_alias> \
    -o data_dir datasets/constraints/qb/QuantumBitBundle \
    -o dataset_dirs "datasets/sfdmu/qb/en-US/qb-pcm"
cci task run manage_expression_sets -o operation activate_versions \
    -o version_full_names "QuantumBitBundle_V1"
```

Use the same sequence for Server2 with its directory and version name.

## Export

```bash
cci task run export_cml --org <cci_alias> \
    -o developer_name QuantumBitBundle -o version 1 \
    -o output_dir datasets/constraints/qb/QuantumBitBundle
```

Export writes model metadata, polymorphic reference CSVs, and the blob. For
manufacturing, use `developer_name GeneratorSet` or `Fuel_Cell` and the respective
`mfg/genSet` or `mfg/fuelCell` output directory. Check the source org's actual
DeveloperName before exporting.

## Runtime verification

Reading `ConstraintModel` back proves storage, not execution. Query the model's
active version and associations, compare the expected Type/Port set with the org,
and execute configuration rules for a quote line using that model:

```text
POST /services/data/v68.0/connect/cpq/configurator/actions/configure
{
  "transactionLineId": "<configurable bundle QuoteLineItem Id>",
  "transactionId": "<Quote Id>",
  "correlationId": "<uuid>",
  "configuratorOptions": {
    "executeConfigurationRules": true,
    "validateProductCatalog": true
  }
}
```

Require a successful model solve without model errors, then repeat after importing
into already-active versions and cycling them. See the
[constraint-model skill](../../.cursor/skills/constraint-models/SKILL.md) for
association failure diagnosis and verification details.

## QuantumBitBundle rules

The shipped blob contains the full QB-COMPLETE configuration rules plus a virtual
Quote container. Cart rules require QuantumBit Database with API Access Requests
and recommend Essentials/Fundamentals Training. A product has one Component Type,
so the model uses LineItem types throughout. It has no AssetLineItem facet or
recommendation based on an existing Complete Solution asset.

## Adding new models

Export into `datasets/constraints/<vertical>/<Model>/`, verify the reference maps,
edit the blob, and run `validate_cml -o data_dirs <directory>`. Import explicitly
with `data_dir` and appropriate `dataset_dirs`. If adding a model to the build,
include it in validation, import, and both lifecycle lists, preserving feature
prerequisites and verifying its runtime through the configurator.
