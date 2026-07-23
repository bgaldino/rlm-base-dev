# Context plans

Additive **context-plan JSON** consumed by the `manage_context_definition` /
`apply_context_*` CumulusCI tasks (class `rlm_context_service.ManageContextDefinition`)
and by `ExtendStandardContext`. Each plan declares the attributes, mappings, and
tags this repo layers onto a Revenue Cloud **Context Definition** — e.g. adding
`RampMode__c` to the Sales Transaction context and mapping it to
`QuoteLineItem.RLM_RampMode__c`.

## What this format is (and is not)

The **plan-JSON format is this repo's own** — it is **not** a Salesforce-native
artifact. The platform has no context *import* format; our CCI task reads a plan
and drives the standard Connect / SObject-REST APIs to apply it. Two other
formats exist and are distinct:

- **MDAPI `.contextDefinition`** (`force-app/main/default/contextDefinitions/`,
  deployed by `deploy_context_definitions`) — the platform's *tracked-metadata*
  format. Deploys a definition as one atomic unit; can't express "add just these
  N artifacts" and can't set activation/default-mapping. Different layer.
- **Connect / SObject-REST payloads** — the platform *runtime* wire format. The
  CCI task builds these from a plan; you do not hand-author them.

Plan JSON is the granular, source-controlled, additive layer that sits above
both. It is **additive-only**: a plan adds/upserts artifacts onto a base — there
is no per-artifact delete directive (deactivation is whole-version, via
`deactivate_before`).

## Layout

```
<PlanName>/
  manifest.json            # lists one or more contexts (developerName + planFile)
  contexts/<plan>.json     # the additive plan for one definition
archive/                   # retired plans; skipped by the validator unless --include-archive
```

A `manifest.json` points at each plan file:

```json
{ "contexts": [
  { "developerName": "RLM_SalesTransactionContext",
    "planFile": "contexts/ramp_mode.json" } ] }
```

Current plans: **Billing**, **ConstraintEngineNodeStatus**, **DocGen**
(`create: true` — a net-new custom definition), **PartnerAccount**,
**PrmPricing**, **RampMode**. Four extend `RLM_SalesTransactionContext`
(`ConstraintEngineNodeStatus`, `PartnerAccount`, `PrmPricing`, `RampMode`);
`Billing` and `DocGen` target their own definitions.

## Schema, enums, limits, `__c` rule — see the skill

The **authoritative** plan-file schema (every recognized key, the `dataType` /
`fieldType` enums, the three mapping types, the scoped `__c`-suffix rule, and the
guardrail limits) lives in the context-service skill so there is a single source
of truth:

- **`.cursor/skills/context-service/data-model-and-api.md`** → *Repo plan-file
  format*, *Guardrail limits* — the schema tables.
- **`.cursor/skills/context-service/authoring-and-lifecycle.md`** → extend vs
  clone, activation/deactivation, versioning, upgrade/Sync, gotchas.
- **`.cursor/skills/context-service/SKILL.md`** → Quick Rules, DO NOT, task +
  script routing.

## Working with plans

```bash
# Lint (offline — no org). Must be 0 errors before applying.
python scripts/context_service/definition/validate_context_plan.py \
  datasets/context_plans/RampMode/manifest.json

# Inspect / compare a live definition (read-only)
python scripts/context_service/definition/describe_context.py --target-org <sf_alias> --developer-name <name>
python scripts/context_service/definition/diff_context.py --target-org <sf_alias> \
  --plan-file datasets/context_plans/RampMode/manifest.json

# Apply (mutates the org) — via the CCI task, not a script
cci task run manage_context_definition -o plan_file datasets/context_plans/RampMode/manifest.json --org <cci_alias>
```

`diff_context.py` and `patch_context.py` (both read-only) can compare a plan
against an org and extract the drift back into a plan-JSON patch — see
`scripts/context_service/README.md`. **Editing a plan?** Re-run the validator, and if you
add/rename recognized keys, update the schema table in `data-model-and-api.md`
in the same change (per `.cursor/skills/doc-consistency/SKILL.md`).
