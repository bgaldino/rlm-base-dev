# Writing and checking models from a script

`scripts/constraint_models/cml_tool.py` is a small CLI over the same REST routes the
constraint tasks use. It takes `--target-org <sf_alias_or_username>`, goes through the
sf CLI transport of `scripts/expression_sets/_client.py`, and holds no org ids.

| Command | Does | Writes? |
|---|---|---|
| `size` | Byte length of each constraint model version and its share of a limit; exit 1 if any is over | No |
| `push <model-file>` | Cycles a version: deactivate if active, write `ConstraintModel`, activate; raises when activation reports `success: false` | Yes, with `--confirm` |
| `scaffold <spec.json>` | Creates a classification, picklist attributes, products, selling model option, price book entries, an Expression Set with its version and the constraint rows, from a spec | Yes, with `--confirm` |

Mutating commands print a preview unless `--confirm` is given.

```bash
python scripts/constraint_models/cml_tool.py size --target-org <sf_alias_or_username>
python scripts/constraint_models/cml_tool.py scaffold scripts/constraint_models/example-spec.json --target-org <sf_alias_or_username>
python scripts/constraint_models/cml_tool.py scaffold scripts/constraint_models/example-spec.json --target-org <sf_alias_or_username> --confirm
```

## The spec

`example-spec.json` shows the shape: a `prefix` (names, codes and the model ApiName
`CM_<prefix>` derive from it, so reruns in one org need a new prefix), `attrs` (each with
a developer name and picklist `values`) and `products` (a name and a tag). Product
`Code` and picklist value codes are unique per org, which is why they carry the prefix.

## What to use it for

- Check a model against the save limit before importing it
  ([size-and-limits.md](size-and-limits.md)).
- Build a throwaway classification-based test product and model in a scratch org, then
  read the product back through Configure ([computed-attribute-and-setup.md](computed-attribute-and-setup.md)).
- For shipped models under `datasets/constraints/`, keep using `import_cml`,
  `export_cml`, `validate_cml` and `prepare_constraints`; they remap record ids through
  CSVs, which this tool does not.

## Status

The unit test (`tests/test_cml_tool.py`) covers size arithmetic, the push call order
against a fake transport, and spec validation. The scaffold's record creation ran
against a scratch org up to the constraint-row step; the constraint-row step and
`size` against live models were not run, because the build used lacked the constraints
engine `[Open: needs a scratch org with the Constraints Engine setting enabled]`.
