# Writing and checking models from a script

`scripts/constraint_models/cml_tool.py` is a small CLI over the same REST routes the
constraint tasks use. It takes `--target-org <sf_alias_or_username>`, goes through the
sf CLI transport of `scripts/expression_sets/_client.py`, and holds no org ids.

| Command | Does | Writes? |
|---|---|---|
| `size` | Byte length of each constraint model version and its share of a limit; exit 1 if any is over | No |
| `push --api-name <Name> --file <model-file>` | Cycles the active version (else the latest): saves the model in service to `<file>.previous` (active version only), deactivates if active, writes `ConstraintModel`, activates, reads the blob back and fails on a mismatch or an inactive version | Yes, with `--confirm` |
| `scaffold --spec <spec.json> [--out <ids.json>]` | Creates a classification, picklist attributes, products, selling model option, price book entries, an Expression Set with its version and the constraint rows, from a spec | Yes, with `--confirm` |

Mutating commands print a preview unless `--confirm` is given. `scaffold` prints the ids it
created; without `--out`, a failure part-way prints none.

```bash
python scripts/constraint_models/cml_tool.py size --target-org <sf_alias_or_username>
python scripts/constraint_models/cml_tool.py scaffold --spec scripts/constraint_models/example-spec.json --target-org <sf_alias_or_username>
python scripts/constraint_models/cml_tool.py scaffold --spec scripts/constraint_models/example-spec.json --target-org <sf_alias_or_username> --confirm
```

## The spec

`example-spec.json` shows the shape: a `prefix` (names, codes and the model ApiName
`CM_<prefix>` derive from it, so reruns in one org need a new prefix), `attrs` (each with
a developer name and picklist `values`) and `products` (a name and a tag). Product
`Code`, the attribute `Name`, `DeveloperName` and `Code`, and picklist value codes are
unique per org, which is why they carry the prefix (attribute `<prefix>_<dev>`, product
`<prefix>_<name>`; in `DeveloperName` and the ApiName, characters other than letters and
digits in the prefix become `_`). Two
scaffolds with the same attributes and different prefixes both completed, and the same
prefix twice failed with a duplicate `Code`
`[Measured: 2026-11-27, 264, scratch org]`.

## What to use it for

- Check a model against the save limit before importing it
  ([size-and-limits.md](size-and-limits.md)).
- Build a throwaway classification-based test product and model in a scratch org, then
  read the product back through Configure ([computed-attribute-and-setup.md](computed-attribute-and-setup.md)).
- For shipped models under `datasets/constraints/`, keep using `import_cml`,
  `export_cml`, `validate_cml` and `prepare_constraints`; they remap record ids through
  CSVs, which this tool does not.

## Gotcha: never round-trip the Connect read

`GET industries/constraints/{expressionSetId}/versions/{versionId}` returns `constraintModel`
HTML-escaped (`"` as `&quot;`, `&` as `&amp;`). Its length is wrong, and writing it back
stores escaped text that fails to parse on activation
`[Measured: 2026-11-26, 264 (USA796), ent-sb0 harness build]`. Read the stored blob
(`ExpressionSetDefinitionVersion.ConstraintModel`) for sizes and read-backs; the tool does,
and `push` reads the blob back after activation and fails if it differs from the file or
the version is not active. `QuantumBitBundle` reads 8,774 bytes and `Server2` 21,541, the same as their repo files.

## When a push fails

A failed activation leaves the new blob stored and the version inactive; the old model is
no longer the stored one `[Open: seen on the model that lacked the LineItem type; the stored
blob was not read back after that failure]`. Before writing, `push` saves the model in service to `<file>.previous`, but only when
the version is active. A rerun after a failed activation finds the version inactive, so
it leaves `.previous` alone; pushing that file restores the old model
`[Open: restore from .previous not run against a live org]`. The backup is
gitignored (`*.previous`). A connection reset during the
cycle left a model inactive once `[Measured: 2026-11-26, 264 (USA796), ent-sb0 harness build]`;
rerunning the same command works, because `push` skips the deactivate step for an
inactive version. With no active version `push` targets the latest one, which on a
model with several versions may not be the one the first run used: read the version in
the preview line before `--confirm`. A model must declare `type LineItem;` before its subtypes, as every shipped
model does; a test model without it did not activate
`[Measured: 2026-11-26, 264 (USA796), ent-sb0 harness build]`.

## Status

The unit test (`tests/test_cml_tool.py`) covers size arithmetic, the push call order
against a fake transport, a read-back that comes back escaped, the `.previous` backup (made
for an active version, left alone for an inactive one, and holding the old text in a full
`cmd_push` run), and spec validation.
Run against a full 264 build `[Measured: 2026-11-26, 264 (USA796), ent-sb0 harness build]`:
`size` (read-only); `scaffold`, which created the classification, attributes, product and
Expression Set with its association; and `push` of a one-product model with `type LineItem;`
declared, cycled once from inactive and once from active, with the read-back identical and
the version active.
