# QuantumBit Demo Script Generator

Use this skill when generating or refreshing the **QuantumBit demo script** that
SEs and partners consume as the canonical Revenue Cloud walkthrough. The
artifact today lives as a Slack canvas (`F09Q04HEC8Y` for the FY27/260 version);
this skill generates the Markdown source so future versions can be regenerated
mechanically per Salesforce release rather than hand-edited.

## Quick Rules

1. **The canvas is per-Salesforce-release.** Every release gets its own version
   (260, 262, 264, …). The previous-release version is a starting template, not
   a derivative — content WILL change as features change.
2. **Ground every record reference in `qb-scenario-reference.md`.** Never invent
   accounts, products, SKUs, bundles, or constraint models. If the scenario
   reference doesn't list it, it doesn't exist in the demo. (Personas are an
   exception today — see Quick Rule 4 for the second source. Optional features
   like Billing Portal that the user opts into are also exceptions.)
3. **Per-section structure is locked.** Header → image marker → 3-column
   click-path/talk-track/screenshot table. Existing canvas sections are the
   template; don't redesign them.
4. **Personas are stable across releases.** The 6-persona inventory (names,
   roles, bios) is currently sourced from the prior-release canvas at
   `.agents/artifacts/qb-canvas-{prior_release}-source.md` because the
   canonical `docs/enablement/master/qb-scenario-reference.md` doesn't yet
   include personas. Migrating personas into the scenario reference is a
   tracked follow-up so future regenerations don't depend on a local-only
   artifact. Until that lands, treat the prior canvas as authoritative for
   persona text.
5. **Image markers are placeholders.** Generated content uses
   `![placeholder][img-PLACEHOLDER-{slug}]` markers; real Slack file IDs are
   substituted at canvas-publish time, not at generation time.
6. **Setup steps and Known Bugs lists drift release-to-release.** The skill
   generates skeletons; an SME pass adds concrete bugs and Setup-UI changes
   that came in with the release.
7. **Output is a Markdown file**, not a Slack canvas. The canvas-publish step
   is a separate concern (Slack canvas API + image upload + image-marker
   substitution) and is out of scope for this skill.

## DO NOT

- **DO NOT** scrape the existing Slack canvas at runtime. Read the saved source
  at `.agents/artifacts/qb-canvas-{release}-source.md` if present, or the
  `qb-scenario-reference.md` directly.
- **DO NOT** invent customer accounts, products, SKUs, bundles, or constraint
  models. Pull them from `docs/enablement/master/qb-scenario-reference.md`.
- **DO NOT** invent personas. Pull the 6-persona inventory (name + role + bio)
  from `.agents/artifacts/qb-canvas-{prior_release}-source.md` (see Quick
  Rule 4 — the canonical scenario reference does not yet contain personas;
  migration is tracked separately). If the prior-canvas source is absent,
  omit the Demo Personas section rather than fabricate one.
- **DO NOT** reference `Solutions Workspace` URLs that don't exist for the
  target release. The DOT/TFID identifiers are release-specific.
- **DO NOT** copy talk-track narrative verbatim from the prior release without
  reviewing whether the feature behavior changed (e.g., "preview 262, Summer '26"
  becomes "GA in 262" once 262 is GA).
- **DO NOT** publish to a real Slack canvas without a human review pass — the
  artifact is consumer-facing and partner-facing.

---

## Inputs (grounding contract)

This skill is **fully self-contained on the Foundations side**. All inputs are
Foundations-internal artifacts. The skill works without any PMOS clone present
and without the cross-repo manifest being live in PMOS.

> PMOS narrative-polish consumption (mentioned in the "Cross-repo consumption"
> section below) is purely opt-in / future. It depends on Sandy shipping his
> half of the cross-repo manifest first. Until then, this skill ignores PMOS.

| Input | Path | Resolved via | Required? |
|---|---|---|---|
| QB scenario reference | `docs/enablement/master/qb-scenario-reference.md` | manifest `foundations.grounding.qb_scenario` | Required |
| Feature index for target release | `docs/salesforce/{release}/feature-index.md` | manifest `foundations.grounding.feature_index_active` | Required |
| Help portal mirror for target release | `docs/salesforce/{release}/help/articles/` + `manifest.json` | manifest `foundations.grounding.help_corpus_active` | Required |
| Capability roadmap (PMOS-side) | `context/CAPABILITIES.md` | manifest `pmos.context_files.capabilities` | Optional but recommended for "what's new" framing |
| Prior-release canvas source | `.agents/artifacts/qb-canvas-{prior_release}-source.md` | direct | Optional — used as structural template |
| Active CCI feature flags for target release | `cumulusci.yml` `project.custom` block | direct | Required for "Setup steps" and "Available features" sections |

## Outputs

A single Markdown file at:

```
docs/enablement/{release}/qb-demo-script.md
```

The Markdown follows the Slack canvas conventions used in the existing FY27/260
canvas (`F09Q04HEC8Y`). Specifically:

- `# :quantumbit:` h1 with release identifier
- `### How do I get my own copy of QuantumBit?` (Solutions Workspace + TFID)
- `:::` layout / column markers (Slack canvas-specific; Markdown viewers ignore)
- `### :sf-setup: Demo Setup [required]` section
- `### :bug_60: Known Bugs & Issues to Avoid` section
- `### :persona: Demo Personas` (anchor links to per-persona blocks below)
- Body sections in the canonical order (Opportunity-to-Order, Usage Mgmt &
  Rating, Order/DRO, Asset Lifecycle, Invoicing & Billing, RMI, Payments &
  Collections, Salesforce Contracts)
- 3-column click-path table per section
- Persona block at the bottom (one row per persona, image-marker placeholder
  + bio)
- Image marker reference list at the very end (placeholders to be substituted)

When the canvas is later published to Slack, an additional pass uploads
images and substitutes the placeholder markers with real Slack file IDs.

## Generation flow

1. **Resolve target release** — argument (e.g., `262`) determines which
   `feature-index.md` and `help/articles/` directory to consume.
2. **Resolve prior canvas source** — if `.agents/artifacts/qb-canvas-{prior}-source.md`
   exists, use it as a structural template. Otherwise generate from scratch
   using the canonical section order.
3. **Read `docs/enablement/master/qb-scenario-reference.md`** — extract:
   - 3 customer accounts (Infinitech, Global Media, plus default)
   - Bundles (QB Complete Solution, QB Q-Rack 750, QB Services Project, QB
     Complete Solution Plus, QB Software Bundle)
   - Per-bundle SKU lists
   - Pricing-feature wiring (Software Maintenance derivation, API quantity
     auto-add, etc.)
   - Constraint models (QuantumBitComplete, Server2)
3a. **Read `.agents/artifacts/qb-canvas-{prior_release}-source.md`** — extract
    the 6-persona inventory (name + role + bio). This is intentionally a
    second source today; see Quick Rule 4 for the migration note. If the
    prior-canvas source is absent, skip the Demo Personas section rather
    than fabricate it (a missing persona section is preferable to invented
    text in a canonical artifact).
4. **Read target-release `feature-index.md`** — extract:
   - GA features new in this release (annotate "new in {release}" in talk-track)
   - Preview/Beta features (annotate "preview/beta")
   - Deprecations (annotate "removed/replaced")
5. **Read Help corpus** — for each demo section, find the canonical Help
   article(s) and surface the official terminology in talk-track (e.g.,
   "Pricing Procedure" not "pricing logic").
6. **Read `cumulusci.yml` `project.custom`** — only mention features in the
   demo script if the corresponding feature flag is `true` by default in the
   QB shape. Optional features (e.g., `billing_portal: false`) get marked
   "(optional)" in Setup steps.
7. **Apply prior-canvas section order and table structure** — reuse click-path
   prose where the underlying behavior is unchanged. Where a feature changed
   between releases (constraint engine UI redesign, Pricing Waterfall toggle,
   Agentforce updates), regenerate the relevant rows from the new Help articles.
8. **Annotate each section with a "What's new in {release}"** bullet block
   distilled from the feature-index delta.
9. **Emit image-marker placeholders** with descriptive slugs (e.g.,
   `[img-PLACEHOLDER-config-quantum-bit-complete-step-1]`). The publish step
   handles real image upload.
10. **Write to `docs/enablement/{release}/qb-demo-script.md`**.

## Section reference (the canonical demo flow)

The canvas covers 10 main sections. Generation must keep them in this order:

| # | Section | Source | Talk-track persona |
|---|---|---|---|
| 1 | Demo Setup [required] | Help: enable RC + setup; CCI feature flags | n/a (admin) |
| 2 | Known Bugs & Issues to Avoid | Hand-curated; SME pass | n/a |
| 3 | Demo Personas | `.agents/artifacts/qb-canvas-{prior_release}-source.md` (6 personas; migration into `qb-scenario-reference.md` is a tracked follow-up — see Quick Rule 4) | n/a |
| 4 | Opportunity to Order | Includes Configuration sub-sections, Pricing, Ramping & Grouping, Document Generation, Advanced Approvals, Quoting Agent | Kristen O'Reilly (AE) |
| 5 | Usage Management & Rating | Help: Usage + Rating; QB DataBase product | Anne Wei (SalesOps) |
| 6 | Order Entry, Fulfillment, & DRO | Help: DRO; QB pre-staged ramped order | Beth Henderson (Order Mgmt) |
| 7 | Asset Lifecycle | Help: Asset; ramped quote continuation | Anne Wei (SalesOps) |
| 8 | Invoicing & Billing | Help: Billing; bundle pre-seed flow | Jeane Claude Perrier (Billing) |
| 9 | Revenue Management Intelligence | Help: RMI dashboards | Edgar Fallon (CFO) |
| 10 | Payments & Collections | Help: Collections + Payments | Jeane Claude Perrier |
| 11 | Salesforce Contracts | Help: Contracts | (no specific persona today) |

## Per-section table conventions

```
|**Click Path/Action**|**Talk Track**|**Screenshot**|
|  ---  |  ---  |  ---  |
|- Action 1<br><br>- Action 2|Talk track narrative.|![placeholder][img-PLACEHOLDER-{slug}]|
```

Important conventions verified against the FY27/260 canvas:
- `<br><br>` for line breaks within a cell (single `<br>` for tighter spacing)
- Bold via `**` for UI element names (button labels, field names, attribute
  names)
- Italic via `*` for parenthetical hints / asides
- Sub-section headers use `## :slug-emoji: Section Name|||` followed by an empty
  row
- Slack emoji shortcuts (`:solution-found:`, `:price-tag:`, `:ramps:`,
  `:document-3870:`, `:approval_60-1:`, `:agentforce:`) are preserved literally
  — don't substitute Unicode

## Sub-skill: regenerate vs refresh

The skill operates in two modes:

- **regenerate** (default): produce the full canvas Markdown for a target
  release from scratch (or from a prior-release template). Use for a new
  release rollover (260 → 262, 262 → 264).
- **refresh**: take an existing `qb-demo-script.md` and update only the
  sections affected by a delta in `feature-index.md` since last generation.
  Use for in-release patches (262.10.5 → 262.10.6) where most of the canvas
  is unchanged.

Both modes write to `docs/enablement/{release}/qb-demo-script.md` (refresh
backs up the prior file to `.bak.{timestamp}` first).

## Cross-repo consumption (Phase 6.3+ — **OPT-IN, not active today**)

> **Today (2026-05-24):** This skill does NOT invoke PMOS. PMOS is read-only
> from the Foundations side and the cross-repo manifest exists only in
> Foundations. PMOS adoption is Sandy's call (see
> `.agents/artifacts/pmos-side-manifest-draft.md` for the proposal handed to
> Sandy). When/if PMOS ships its manifest half AND completes Tier 0 hygiene
> (see `pmos-tier-0-hygiene-ask.md`), the patterns below become viable.

When the manifest pattern is fully wired, this skill could optionally
invoke PMOS skills for narrative-quality polish:

- `pmos.skills.demo-script` — narrative-voice rewrite of talk-track prose
- `pmos.skills.presentation` — slide-outline companion artifact for SE briefings
- `pmos.skills.sales-enablement` — battle-card / talk-track companion artifact

The skill MUST continue to ground on Foundations canonical sources for all
record references (accounts, products, SKUs, personas) regardless of whether
PMOS is consumed. PMOS-side narrative polish is purely voice/tone, never
fact source.

**Discovery pattern when activated:**

```python
# In a future revision of this skill (illustrative only — do not implement until
# PMOS manifest half is live):
from scripts.ai.skill_manifest import load_manifest, resolve_skill, resolve_repo_root
m = load_manifest()
pmos_root = resolve_repo_root(m, repo='pmos')
if pmos_root is None:
    # PMOS clone not present; skill operates standalone (current state)
    pass
else:
    pmos_demo_script = resolve_skill(m, repo='pmos', skill_id='demo-script')
    if pmos_demo_script and pmos_demo_script.is_file():
        # Pass talk-track output through PMOS narrative-polish step
        ...
```

The skill must degrade gracefully when PMOS is absent. Today that's the
default state for every consumer.

## Related

- `release-enablement` skill — the broader release-enablement workstream this
  fits inside. Per-release exercise files live alongside this canvas at
  `docs/enablement/{release}/`.
- `revenue-cloud-docs` skill — Help portal mirror access patterns; this skill
  consumes that corpus.
- `qb-scenario-reference.md` — canonical demo data dictionary; mandatory read.
- `.agents/artifacts/skills-consolidation-plan.md` — the consolidation context
  this skill is the first concrete instance of (Cluster C1).
- `.claude/skill-manifest.yml` — cross-repo discovery for Phase 6.3+ PMOS
  consumption.
