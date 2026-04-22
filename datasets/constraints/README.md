# CML Constraint Model Utility

**Module:** `tasks/rlm_cml.py`
**CCI Tasks:** `export_cml`, `import_cml`, `validate_cml`

This utility manages Constraint Modeling Language (CML) data for Revenue Cloud Expression Sets. It replaces the deprecated standalone scripts (`scripts/cml/export_cml.py`, `import_cml.py`, `validate_cml.py`) with CCI-integrated tasks that use org credentials directly from CumulusCI.

## Table of Contents

- [Architecture](#architecture)
- [Directory Structure](#directory-structure)
- [Export Workflow](#export-workflow)
- [Import Workflow](#import-workflow)
- [Validate Workflow](#validate-workflow)
- [CCI Integration](#cci-integration)
  - [prepare_constraints Flow (QuantumBit)](#prepare_constraints-flow-quantumbit)
  - [import_mfg_cml Flow (Manufacturing)](#import_mfg_cml-flow-manufacturing)
- [Data Plan Reference](#data-plan-reference)
- [Adding New Models](#adding-new-models)
- [Polymorphic Resolution](#polymorphic-resolution)
- [Migration from Deprecated Scripts](#migration-from-deprecated-scripts)
- [CML Source Files](#cml-source-files)

## Architecture

The utility is implemented as a single Python module (`tasks/rlm_cml.py`) with four classes:

| Class | Base Class | Purpose |
|-------|-----------|---------|
| `CMLBaseTask` | `BaseSalesforceTask` | Shared REST API helpers, CSV utilities, SOQL escaping, ID resolution constants |
| `ExportCML` | `CMLBaseTask` | Export constraint model metadata + blob from a Salesforce org |
| `ImportCML` | `CMLBaseTask` | Import constraint model data into a Salesforce org with polymorphic resolution |
| `ValidateCML` | `BaseTask` | Validate CML file structure and ESC association coverage (no org needed) |

`CMLBaseTask` extends `BaseSalesforceTask` so CCI provides the `--org` CLI flag and org config automatically. `ValidateCML` extends `BaseTask` directly since it operates on local files only.

### Key Capabilities

- **SOQL injection protection** -- all names are escaped before interpolation into queries
- **Polymorphic ReferenceObjectId resolution** -- handles Product2, ProductClassification, and ProductRelatedComponent references using ID prefix detection and composite key matching
- **Dry run mode** -- log all operations without executing (import only)
- **Idempotent imports** -- old ESC records are deleted only after all new ones succeed
- **Composite key matching for PRC** -- uses ParentProduct.Name, ChildProduct.Name, ChildProductClassification.Name, ProductRelationshipType.Name, and Sequence to portably resolve ProductRelatedComponent records across orgs
- **Binary blob handling** -- downloads and uploads ConstraintModel blobs via REST API

## Directory Structure

Each constraint model is stored as a self-contained data plan. Models are organised by feature family under `datasets/constraints/`:

```
datasets/constraints/
├── qb/                          # QuantumBit constraint models
│   ├── QuantumBitComplete/
│   │   ├── ExpressionSet.csv
│   │   ├── ExpressionSetConstraintObj.csv
│   │   ├── ExpressionSetDefinitionContextDefinition.csv
│   │   ├── ExpressionSetDefinitionVersion.csv
│   │   ├── Product2.csv
│   │   ├── ProductClassification.csv
│   │   ├── ProductRelatedComponent.csv
│   │   └── blobs/
│   │       └── ESDV_QuantumBitComplete_V1.ffxblob
│   └── Server2/
│       ├── (same CSV structure)
│       └── blobs/
│           └── ESDV_Server2_V1.ffxblob
├── mfg/                         # Manufacturing constraint models
│   ├── genSet/
│   │   ├── ExpressionSet.csv
│   │   ├── ExpressionSetConstraintObj.csv
│   │   ├── ExpressionSetDefinitionContextDefinition.csv
│   │   ├── ExpressionSetDefinitionVersion.csv
│   │   ├── Product2.csv
│   │   ├── ProductClassification.csv
│   │   ├── ProductRelatedComponent.csv
│   │   └── blobs/
│   │       └── ESDV_GeneratorSet_V1.ffxblob
│   └── fuelCell/
│       ├── (same CSV structure)
│       └── blobs/
│           └── ESDV_Fuel_Cell_V1.ffxblob
└── README.md               # This file
```

### CSV Files

| File | Contents |
|------|----------|
| `ExpressionSetDefinitionVersion.csv` | ESDV metadata including ConstraintModel blob URL |
| `ExpressionSetDefinitionContextDefinition.csv` | Links between Expression Set Definition and Context Definition |
| `ExpressionSet.csv` | Expression Set metadata (ApiName, UsageType, etc.) |
| `ExpressionSetConstraintObj.csv` | All ESC association records (tags, types, reference object IDs) |
| `Product2.csv` | Product records referenced by ESC (Id + Name for portable resolution) |
| `ProductClassification.csv` | Classification records referenced by ESC |
| `ProductRelatedComponent.csv` | PRC records with traversal fields for composite key resolution |
| `blobs/ESDV_<Model>_V<N>.ffxblob` | Binary ConstraintModel blob |

## Export Workflow

Export extracts a complete constraint model from a Salesforce org to a local directory.

### Usage

```bash
cci task run export_cml --org <source_org> \
    -o developer_name <DeveloperName> \
    -o version 1 \
    -o output_dir datasets/constraints/qb/<ModelName>
```

### Options

| Option | Required | Description |
|--------|----------|-------------|
| `developer_name` | Yes | DeveloperName of the Expression Set Definition |
| `version` | No | Version number (default: 1) |
| `output_dir` | Yes | Directory to write CSV exports and blobs |
| `api_version` | No | Override Salesforce API version (e.g. 66.0) |

### What Gets Exported

1. **ExpressionSetDefinitionVersion** -- queries by DeveloperName and VersionNumber; includes ConstraintModel blob URL
2. **ExpressionSetDefinitionContextDefinition** -- links to Context Definition
3. **ExpressionSet** -- expression set metadata
4. **ExpressionSetConstraintObj** -- all ESC association records for the expression set
5. **Product2** -- products referenced by ESC (filtered by `01t` ID prefix)
6. **ProductClassification** -- classifications referenced by ESC (filtered by `11B` ID prefix)
7. **ProductRelatedComponent** -- PRC records referenced by ESC (filtered by `0dS` ID prefix), with traversal fields for portable resolution
8. **ConstraintModel blob** -- binary blob downloaded to `blobs/` subdirectory

### Example

```bash
# Export QuantumBitComplete from qb-migrate org
cci task run export_cml --org qb-migrate \
    -o developer_name QuantumBitComplete \
    -o version 1 \
    -o output_dir datasets/constraints/qb/QuantumBitComplete
```

Expected output:
```
Exporting CML model 'QuantumBitComplete' v1 to datasets/constraints/qb/QuantumBitComplete
Exporting ExpressionSetDefinitionVersion.csv...
  1 records fetched
Exporting ExpressionSetConstraintObj.csv...
  43 records fetched
Exporting Product2.csv...
  22 records fetched
Exporting ProductRelatedComponent.csv...
  21 records fetched
Downloaded blob to .../blobs/ESDV_QuantumBitComplete_V1.ffxblob
Export complete
```

## Import Workflow

Import loads constraint model data from a local directory into a target Salesforce org, resolving all polymorphic references to match the target org's record IDs.

### Usage

```bash
cci task run import_cml --org <target_org> \
    -o data_dir datasets/constraints/qb/<ModelName> \
    -o dataset_dirs "datasets/sfdmu/qb/en-US/qb-pcm"
```

### Options

| Option | Required | Description |
|--------|----------|-------------|
| `data_dir` | Yes | Directory containing CML CSV exports and blobs/ |
| `dataset_dirs` | No | Comma-separated additional directories for cross-referencing (e.g. qb-pcm plan dir for additional Product2/PRC names) |
| `dry_run` | No | Log operations without executing (default: false) |
| `api_version` | No | Override Salesforce API version |

### Import Steps

1. **Upsert ExpressionSet** by ApiName (create if missing, update if exists)
2. **Resolve ExpressionSetDefinitionVersion** by DeveloperName
3. **Upsert ExpressionSetDefinitionContextDefinition**
4. **Build polymorphic lookup maps** -- reads exported CSVs to build legacy ID-to-name mappings, queries target org to resolve names to target IDs
5. **Create ExpressionSetConstraintObj records** -- resolves each polymorphic ReferenceObjectId
6. **Delete old ESC records** -- only if all new records were created successfully
7. **Upload ConstraintModel blob** via REST PATCH

### Dry Run

Use `dry_run` to preview what the import would do without making changes:

```bash
cci task run import_cml --org dev-sb0 \
    -o data_dir datasets/constraints/qb/QuantumBitComplete \
    -o dataset_dirs "datasets/sfdmu/qb/en-US/qb-pcm" \
    -o dry_run true
```

### Example Output

```
Importing CML data from datasets/constraints/qb/QuantumBitComplete (dry_run=False)
Loaded 43 ESC records
Updated ExpressionSet 'QuantumBitComplete' -> 9QLWs000007UVaDOAW
Resolved ESDV 'QuantumBitComplete_V1' -> 9QBWs000000SPptOAG
Updated ESDCD -> 9QYWs000000RBVdOAO
Resolution maps: Product2=158, Classification=16, PRC_composite=37, PRC_name=21
Found 0 existing ESC records to replace
Created ExpressionSetConstraintObj -> 1JEWs00000045abOAA
...
43 ESC records created
Uploaded blob to ExpressionSetDefinitionVersion/9QBWs000000SPptOAG.ConstraintModel
Import complete
```

## Validate Workflow

Validate checks CML file structure, annotations, and optionally cross-references ESC association data. This task does **not** require a Salesforce org connection.

### Usage

```bash
cci task run validate_cml \
    -o cml_dir scripts/cml \
    -o data_dir datasets/constraints/qb/QuantumBitComplete
```

### Options

| Option | Required | Description |
|--------|----------|-------------|
| `cml_dir` | No | Directory containing .cml files (default: `scripts/cml`) |
| `data_dir` | No | Constraints data plan directory for ESC association checking |
| `expression_set_name` | No | Override Expression Set name for association checks |

### What Gets Validated

- **Syntax** -- brace/parenthesis balance, type declarations, relation references
- **Annotations** -- checks for supported annotation keys, validates boolean/integer/enum/date values
- **Type hierarchy** -- verifies base types exist, detects duplicate type definitions
- **Relations** -- ensures relation target types are defined
- **Association coverage** (when `data_dir` is provided):
  - Checks that CML types have corresponding ESC type associations
  - Checks that CML relations have corresponding ESC port associations
  - Reports ESC associations that reference missing CML types or relations

## CCI Integration

### prepare_constraints Flow (QuantumBit)

The `prepare_constraints` flow in `cumulusci.yml` orchestrates the full QuantumBit constraint setup:

| Step | Task | Condition | Purpose |
|------|------|-----------|---------|
| 1 | `insert_qb_transactionprocessingtypes_data` | `constraints` + `qb` | Load TransactionProcessingType records |
| 2 | `deploy_post_constraints` | `constraints` | Deploy constraint-related metadata |
| 3 | `assign_permission_sets` | `tso` + `constraints` | Assign constraint permission sets |
| 4 | `apply_context_constraint_engine_node_status` | `constraints` | Apply context attribute mappings |
| 5 | `enable_constraints_settings` | `constraints_data` | Set Default Transaction Type, Asset Context, and enable Constraints Engine toggle (Robot Framework) |
| 6 | `validate_cml` | `constraints_data` + `qb` | Validate CML files against data |
| 7 | `import_cml` (QuantumBitComplete) | `constraints_data` + `qb` | Import QuantumBitComplete model |
| 8 | `import_cml` (Server2) | `constraints_data` + `qb` | Import Server2 model |
| 9 | `manage_expression_sets` | `constraints_data` + `qb` | Activate QuantumBitComplete_V1 and Server2_V1 |

### Feature Flags (QuantumBit)

| Flag | Default | Purpose |
|------|---------|---------|
| `constraints` | `true` | Enable constraint metadata deployment (steps 1-4) |
| `constraints_data` | `false` | Enable constraint data loading and activation (steps 5-8) |
| `qb` | `true` | QuantumBit dataset family |

To run the full constraints flow including data:
```yaml
# In cumulusci.yml, set:
constraints_data: true
```

Or override at runtime:
```bash
cci flow run prepare_constraints --org <org> -o constraints_data true
```

### import_mfg_cml Flow (Manufacturing)

Manufacturing constraint models are loaded via the `import_mfg_cml` flow, which is invoked as step 4 of `prepare_mfg_data` (itself part of `prepare_manufacturing`). All steps are gated by `badger=true`.

| Step | Task | Condition | Purpose |
|------|------|-----------|---------|
| 1 | `import_cml` (GeneratorSet) | `badger` | Import GeneratorSet constraint model |
| 2 | `import_cml` (Fuel_Cell) | `badger` | Import Fuel Cell constraint model |
| 3 | `manage_expression_sets` | `badger` | Activate `GeneratorSet_V1` and `Fuel_Cell_V1` |

The MFG models do not use a `dataset_dirs` cross-reference since the manufacturing PCM product catalog is loaded separately by `insert_badger_pcm_data` earlier in `prepare_mfg_data`.

To run the manufacturing CML import independently:
```bash
cci flow run import_mfg_cml --org <org>
```

## Data Plan Reference

### Current Models

| Model | Family | ESC Records | Product2 | PRC | Blob |
|-------|--------|------------|----------|-----|------|
| QuantumBitComplete | qb | 43 | 22 (Type) | 21 (Port) | ESDV_QuantumBitComplete_V1.ffxblob |
| Server2 | qb | 81 | 41 (Type) | 40 (Port) | ESDV_Server2_V1.ffxblob |
| GeneratorSet | mfg | 467 | 235 (Type) | 231 (Port) | ESDV_GeneratorSet_V1.ffxblob |
| Fuel_Cell | mfg | 29 | 15 (Type) | 14 (Port) | ESDV_Fuel_Cell_V1.ffxblob |

### Source Orgs

**QuantumBit models** were extracted from the `qb-migrate` connected org. To re-extract:

```bash
cci task run export_cml --org qb-migrate \
    -o developer_name QuantumBitComplete -o version 1 \
    -o output_dir datasets/constraints/qb/QuantumBitComplete

cci task run export_cml --org qb-migrate \
    -o developer_name Server2 -o version 1 \
    -o output_dir datasets/constraints/qb/Server2
```

**Manufacturing models** use the dedicated `export_cml_genSet` and `export_cml_fuelCell` tasks. To re-extract:

```bash
cci task run export_cml_genSet --org <mfg_source_org>
cci task run export_cml_fuelCell --org <mfg_source_org>
```

Which are equivalent to:

```bash
cci task run export_cml --org <mfg_source_org> \
    -o developer_name GeneratorSet -o version 1 \
    -o output_dir datasets/constraints/mfg/genSet

cci task run export_cml --org <mfg_source_org> \
    -o developer_name Fuel_Cell -o version 1 \
    -o output_dir datasets/constraints/mfg/fuelCell
```

## Adding New Models

To add a new constraint model to the project:

1. **Export from the source org:**
   ```bash
   cci task run export_cml --org <source_org> \
       -o developer_name <NewModelName> \
       -o version 1 \
       -o output_dir datasets/constraints/qb/<NewModelName>
   ```

2. **Add CCI anchor** in `cumulusci.yml` under the custom dataset anchors:
   ```yaml
   new_model_constraints_data_dir: &new_model_constraints_data_dir "datasets/constraints/qb/<NewModelName>"
   ```

3. **Add import step** to `prepare_constraints` flow (after existing import steps):
   ```yaml
   N:
     task: import_cml
     when: project_config.project__custom__constraints_data and project_config.project__custom__qb
     options:
       data_dir: *new_model_constraints_data_dir
       dataset_dirs: "datasets/sfdmu/qb/en-US/qb-pcm"
   ```

4. **Add to activation step** -- append `<NewModelName>_V1` to the `version_full_names` list in the `manage_expression_sets` step.

5. **Test with dry run:**
   ```bash
   cci task run import_cml --org <target_org> \
       -o data_dir datasets/constraints/qb/<NewModelName> \
       -o dataset_dirs "datasets/sfdmu/qb/en-US/qb-pcm" \
       -o dry_run true
   ```

6. **Commit** the new data plan directory.

## Polymorphic Resolution

`ExpressionSetConstraintObj.ReferenceObjectId` is a polymorphic field that can point to three different object types. The import task resolves these references portably across orgs:

### Resolution by ID Prefix

| Prefix | Object | Resolution Strategy |
|--------|--------|-------------------|
| `01t` | Product2 | Match by Name |
| `11B` | ProductClassification | Match by Name |
| `0dS` | ProductRelatedComponent | Match by composite key (ParentProduct.Name + ChildProduct.Name + ChildProductClassification.Name + ProductRelationshipType.Name + Sequence) |

### Why Composite Keys for PRC?

ProductRelatedComponent has an auto-numbered `Name` field (e.g. `PRC-000000022`) that is not portable across orgs. The import task builds a composite unique key from the PRC's relationship fields, which remain consistent across orgs because they reference products and classifications by their human-readable names.

### Dataset Dirs

The `dataset_dirs` option provides additional name candidates for resolution. For example, `datasets/sfdmu/qb/en-US/qb-pcm` contains the full product catalog with all Product2, ProductClassification, and ProductRelatedComponent records, giving the import task a broader set of names to match against in the target org.

## Migration from Deprecated Scripts

The standalone scripts in `scripts/cml/` are deprecated. Here is the mapping:

### Export

```bash
# Old (deprecated):
python scripts/cml/export_cml.py \
    --developerName QuantumBitComplete --version 1 \
    --outputDir data --sfdmuDir sfdmu_out

# New (CCI):
cci task run export_cml --org <org> \
    -o developer_name QuantumBitComplete \
    -o version 1 \
    -o output_dir datasets/constraints/qb/QuantumBitComplete
```

### Import

```bash
# Old (deprecated):
python scripts/cml/import_cml.py --dataDir data --targetAlias tgtOrg

# New (CCI):
cci task run import_cml --org <org> \
    -o data_dir datasets/constraints/qb/QuantumBitComplete \
    -o dataset_dirs "datasets/sfdmu/qb/en-US/qb-pcm"
```

### Validate

```bash
# Old (deprecated):
python scripts/cml/validate_cml.py --cmlDir scripts/cml --dataDir data

# New (CCI):
cci task run validate_cml \
    -o cml_dir scripts/cml \
    -o data_dir datasets/constraints/qb/QuantumBitComplete
```

### Key Differences

| Aspect | Old Scripts | New CCI Tasks |
|--------|-----------|--------------|
| Authentication | `sf org display` subprocess | CCI org config (automatic) |
| Configuration | CLI arguments (`argparse`) | CCI task options |
| Global state | Module-level variables | Instance methods on task class |
| Error handling | Basic try/except | Structured logging with CCI logger |
| SOQL safety | No escaping | `_soql_escape()` for all interpolated values |
| Dry run | Not available | `--dry_run true` (import only) |
| SFDMU output | `write_sfdmu_files()` (incomplete) | Removed (pure Python approach) |

## CML Source Files

The CML constraint model source files are located in `scripts/cml/`:

| File | Family | Description |
|------|--------|-------------|
| `QuantumBitComplete.cml` | qb | QuantumBit Complete constraint model |
| `Server2.cml` | qb | Server2 constraint model |
| `Server260.cml` | qb | Server 260 constraint model |
| `GeneratorSet258.cml` | mfg | Generator Set 258 constraint model (source for `GeneratorSet_V1` blob) |
| `GeneratorSet256.cml` | mfg | Generator Set 256 constraint model (prior release reference) |

These `.cml` files define the constraint model types, relations, attributes, and rules. They are compiled into binary blobs and uploaded to `ExpressionSetDefinitionVersion.ConstraintModel` via the import task.

> **Note:** There is no standalone `.cml` source file for `Fuel_Cell`. The `ESDV_Fuel_Cell_V1.ffxblob` blob in `datasets/constraints/mfg/fuelCell/blobs/` was extracted directly from the source org via `export_cml_fuelCell`.

The `validate_cml` task checks these files for structural correctness and cross-references them against the ESC association data in the constraint data plans.
