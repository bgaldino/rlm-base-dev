# Expression Sets — Metadata API vs Connect API paths

Progressive-disclosure sub-file of `.cursor/skills/expression-sets/SKILL.md`.
Read this to choose the authoring **path** (source-controlled Metadata deploy vs
runtime Connect CRUD), and for the Connect path's **mutation lifecycle**,
verb-specific field handling, and GET serializer gotchas. For building/applying
declarative overlays and capturing a step's three dependency scopes, read the
companion sub-file `authoring-and-overlays.md`.

Pinned to Release 262 / API v67.0.

---

## Choosing the path

The step/param/variable **shapes are identical** across the two paths, so a step
authored once works for both. Choose by use case:

| Use case | Path |
|---|---|
| Source-controlled, git-tracked, diffable changes; part of the build | **Metadata API** — `expressionSetDefinition` XML + deploy |
| Runtime/programmatic CRUD, one-off exploration, org-to-org capture | **Connect API** — the CCI tasks or the standalone `scripts/expression_sets/` toolkit |

---

## Connect API — the mutation lifecycle

An **enabled version cannot be modified or deleted**, so every Connect mutation
runs **deactivate → PATCH/POST → reactivate**, in a guarded `finally`:

1. If a `ProcedurePlanDefinitionVersion` references the ES, deactivate it first
   (the cascade) — an active plan version locks the ES version.
2. Deactivate the `ExpressionSetVersion`.
3. HTML-unescape the payload, then PATCH/POST.
4. On success, reactivate (idempotent — a PATCH body with `enabled:true` already
   reactivates the version). On failure, **leave it deactivated and raise** —
   PATCH is non-atomic, so a half-applied mutation must not be re-enabled.

Pre-flight ordering is **validate (still-escaped) → strip read-only fields →
normalize entities → Connect call**. The overlay path runs its
overlay↔definition cross-check (placement/update/reorder/remove targets must
exist) **before** any deactivation, so a typo'd target fails while the version
is still active.

Both the CCI task (`tasks/rlm_expression_set_connect.py`) and the standalone
toolkit's `_lifecycle.py` (`LifecycleEngine`) enforce this identically — they are
independent implementations of the same live-verified rules. A version left
DEACTIVATED by a failed apply is re-enabled with
`activate_expression_set.py --activate` once inspected/restored.

### Verb-specific field handling

| Concern | POST (create new) | PATCH (replace existing) |
|---|---|---|
| version-level `id` | **omit** (task strips it on create) | **keep** (matches version in place) |
| top-level `id`/`error` | strip (output-only) | strip (output-only) |
| `contextDefinitions[].id` | **keep** — else context-node param data types fail (`Specify a valid data type for the … variable`) | n/a |
| `resourceInitializationType` | set correctly up front (`Default` common); **immutable after** | must equal stored value (task aligns it once) |
| `usageType` | set correctly (`DefaultPricing` for pricing, `Bre` for BRE; a wrong value like `sample` means the ES won't surface in UI / be invocable) | unchanged |

When exporting for a downstream replace, the toolkit's
`export_expression_set.py --for-import` strips the output-only top-level fields
and HTML-unescapes string leaves; the version-`id` rewrite to the *target* org
happens inside `import_expression_set.py` (a PATCH keeps the version id, so it is
left intact on export).

### Reading GET output — serializer gotchas

- Top-level steps come back **alphabetically by name**, NOT by `sequenceNumber`.
  Always read `sequenceNumber` for execution order; never trust the array index.
  (`describe_expression_set.py` and the graph in `trace_expression_set.py`
  re-order by per-parent `sequenceNumber` for you.)
- `sequenceNumber` is **scoped per parent** — child steps restart at 1 under
  each parent.
- JSON-in-string values (`customElement.parameters[].value`,
  `advancedCondition.criteria[].value`, formula text) are **HTML-escaped**. Send
  a PATCH/POST with raw GET output un-normalized and the engine rejects the
  entities (flat: `Syntax error. Found '&'`; nested: opaque `INVALID_INPUT:
  Error processing JSON`). `normalize_html_entities` (default on) fixes this; the
  Metadata path needs no equivalent — the XML parser decodes entities before the
  engine sees them.
- Version identity is resolved from the `ExpressionSetVersion` sObject (source of
  truth), not the GET body — GET can transiently serve a stale version apiName.

---

## Metadata API authoring (source-controlled path)

To author or modify a procedure in git, edit `expressionSetDefinition` metadata
and deploy it via the repo's pipeline (`cumulusci.tasks.salesforce.Deploy`, e.g.
the `deploy_expression_sets` / `deploy_post_prm_pricing_expression_sets` tasks).
All shipped procedures load this way.

Characteristics:

- **Handles nested step graphs** — shipped metadata contains the full nested
  graph and deploys.
- **Validation errors are specific and actionable** — e.g. *"ListGroup can not
  be empty"*, *"Select list filter as the first element in list group"*,
  *"Local variables aren't supported when a business element is used in a list
  group; specify a list variable"*. Each names exactly what to fix.
- **No activation lifecycle** — no deactivate/reactivate, no version-id juggling,
  no entity normalization (the XML parser decodes entities), no procedure-plan
  cascade. Edit source XML and deploy.
- **Source-controlled and diffable.**
- **Shape parity with Connect:** the Metadata XML step/param/variable shapes are
  identical to the Connect JSON shapes (only diffs: XML adds `<label>`, uses the
  legacy-misspelled `<shouldExposExecPathMsgOnly>`, and omits empty
  `*MessageTokenMappings`). A step authored once maps cleanly between
  representations.

### Create-with-content (new-version semantics)

For new-version semantics rather than in-place edit, prefer
**create-with-content** (Tooling-create a new `ExpressionSetDefinitionVersion`
from the prior version's `Metadata`) over create-then-PATCH — appending a step to
an existing version via a Tooling `Metadata` PATCH returns
`FIELD_INTEGRITY_EXCEPTION`. See the exhaustive reference for the exact call
sequence.

---

## Related

- Overlays, three-scope dependency capture, safe step removal:
  `.cursor/skills/expression-sets/authoring-and-overlays.md`
- Exhaustive object/ID model, OAS schema enums, every error + resolution,
  Metadata authoring call sequence, verification checklist:
  `docs/references/expression-set-connect-api-reference.md`
- The standalone toolkit: `scripts/expression_sets/README.md`
