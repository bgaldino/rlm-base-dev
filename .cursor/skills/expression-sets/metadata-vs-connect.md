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

## Step names vs. labels

Each step has a spaceless **`name`** (API-Name identifier; the `parentStep`
foreign key) and a readable **`label`** (UI display text). They diverge sharply by
path — the reason Connect export/describe shows run-on names
(`Mapcontexttagstocommonpricingvariables`) while the UI shows a spaced title.

| Path | `name` | `label` |
|---|---|---|
| Connect (GET/POST/PATCH) | ✅ | ❌ no such field — sending it → `JSON_PARSER_ERROR: Unrecognized field "label"` |
| Metadata XML | ✅ `<name>` | ✅ `<label>` (shipped procedures ship readable labels this way) |
| Tooling `ExpressionSetDefinitionVersion.Metadata.steps[]` | ✅ | ✅ read + write |

**The load-bearing fact:** a **Connect full-graph PATCH clobbers every `label`
back to its `name`.** `import_expression_set` and `apply_expression_set_overlay`
do GET→merge→full-graph-replace, and the Connect representation has no `label`, so
the server rebuilds each label from `name` on every write. Steps created via
Connect come out with `label == name` (spaceless). Connect mutations and
Tooling-set labels are therefore mutually exclusive on one version.

**Reading/writing labels (Tooling only):**
- Read: `GET tooling/sobjects/ExpressionSetDefinitionVersion/{9QB}` →
  `Metadata.steps[].label`; join onto Connect steps by `name` (1:1; `name` is a
  de-spaced/de-punctuated derivation of `label`, occasionally with a uniqueness
  suffix like `…pricing36`).
- **Resolving the 9QB record — use the stable key.** The documented join
  `9QB.DeveloperName == 9QM.ApiName` holds at rest but is **NOT stable across a
  Connect full-graph PATCH**: a Connect PATCH *rewrites the ESDV `DeveloperName` in
  place* (live-verified 262/v67.0 — after an overlay apply, the same 9QB Id came
  back under an unrelated `DeveloperName`, so a lookup by ApiName returned 0 rows).
  The runtime `9QM.ApiName` and the `9QB.ExpressionSetDefinitionId` (→ 9QA) stay
  stable. Any path that resolves the 9QB **right after a Connect mutation** (i.e.
  auto-restore, or a relabel of a just-imported set) must query
  `ExpressionSetDefinitionId = {9QA} [AND VersionNumber = N]`, not `DeveloperName`.
  `_tooling.resolve_esdv(es_def_id=…, version_number=…)` does this; `capture_labels`
  and `relabel_version` pass the stable pair through.
- Write: `PATCH …/{9QB}` with `{"Metadata": {…drop read-only `urls`…}}` — a full
  `Metadata` PATCH (~180 KB). **Active-version guard applies**: PATCHing an active
  version → `INVALID_ID_FIELD: LatestVersionSnapshotId not found …` (does not
  persist). Deactivate `ExpressionSetVersion.IsActive` → PATCH → reactivate;
  labels survive.

**Toolkit — read/write labels:**
- `describe_expression_set.py --labels` (read, flags `label==name` drift); the
  `trace … --mermaid --labels` diagrams title step nodes with the label.
- `relabel_expression_set.py` (write, via deactivate→PATCH→reactivate). Label
  source: `--auto` (lossy derive), `--labels-file` (`{name: label}` JSON), `--set
  NAME=LABEL`, or **`--from-metadata <xml>`** — read the authoritative map straight
  from a source-controlled `force-app/…/expressionSetDefinition/*.expressionSetDefinition-meta.xml`.

**Auto-preservation (default-on).** The two Connect mutators no longer *lose*
labels: `import_expression_set` (replace) and `apply_expression_set_overlay`
**capture** the readable labels before the clobbering PATCH and **restore** them
after, in a second deactivate→Tooling-PATCH→reactivate cycle (`--no-preserve-labels`
to opt out). Two step populations are covered:
- **survivors** → restored from the pre-PATCH target-org snapshot (`capture_labels`).
  A step renamed/added on the clone won't match the snapshot by `name` — correct,
  since the snapshot only knows pre-PATCH names.
- **new steps** → labeled from the overlay's own `labels` block or per-`addSteps`
  `label` (`overlay_labels`); `export_expression_set_overlay.py --with-labels` writes
  that block so a sliced step travels self-describing.

Restore is **non-fatal** (the Connect mutation already succeeded; a restore failure
is reported with a `relabel_expression_set.py` fix hint, never raised) and runs only
when the version is reactivated (`activate_after`) — a relabel needs its own
deactivate window. Shared core: `_tooling.relabel_version`; auto-restore entry:
`_tooling.restore_labels_after_clobber`. Run a manual `relabel` **last**, after all
Connect work, if you opted out or a restore failed. For a step that must ship with a
label in the build, author it in the Metadata XML `<label>` and deploy — that path
preserves labels and is source-controlled.

---

## Related

- Overlays, three-scope dependency capture, safe step removal:
  `.cursor/skills/expression-sets/authoring-and-overlays.md`
- Exhaustive object/ID model, OAS schema enums, every error + resolution,
  Metadata authoring call sequence, verification checklist:
  `docs/references/expression-set-connect-api-reference.md`
- The standalone toolkit: `scripts/expression_sets/README.md`
