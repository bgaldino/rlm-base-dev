---
name: revenue-cloud-docs
description: >-
  Ground product claims about Salesforce Revenue Cloud (Agentforce Revenue
  Management) — Billing, Pricing, Quoting, Orders, Contracts, Assets, Usage,
  DRO — against the captured Salesforce Help portal and Developer Guide
  snapshots under `docs/salesforce/{release}/`. Use before authoring or
  accepting any Trailhead module passage, enablement exercise, internal doc,
  or SME review response that asserts how a Revenue Cloud feature works. Use
  when verifying object names, field labels, feature behavior, or terminology
  against the current release's docs. Use when refreshing the snapshot for a
  new Salesforce release with the standalone `python -m scripts.doc_snapshot`
  tool. The snapshot replaces the per-release PDF compendiums with
  grep-friendly, diffable per-article markdown that AI agents can read
  surgically.
---

# Revenue Cloud Help Snapshot — AI Grounding Source

Use the Salesforce Help portal snapshots at `docs/salesforce/{release}/help/` as the canonical source of truth for product claims about Revenue Cloud — Billing, Pricing, Quoting, Orders, Contracts, Assets, Usage, and the adjacent areas. Every Trailhead module, enablement exercise, internal doc, or SME review response that asserts something about how Revenue Cloud works should ground that assertion against an article in the snapshot before being written or accepted.

For **developer-facing** material — standard object/field reference, Business APIs, Apex, Metadata/Tooling API types, invocable actions, and **Constraint Modeling Language (CML)** — use the companion **Developer Guide snapshot** at `docs/salesforce/{release}/dev-guide/` (the atlas Revenue Cloud Developer Guide). See [Developer Guide snapshot (atlas)](#developer-guide-snapshot-atlas) below. Rule of thumb: **Help = how an admin/seller uses a feature; Dev Guide = the objects, fields, APIs, and CML a developer builds against.**

**Which releases and areas are captured.** Run `python -m scripts.doc_snapshot list` to see every preset, and open the corpus's `index.md` for what has actually been captured. On the active release, a Help preset with a floor (`min N` in `list`) has been verified and captured; one without a floor hasn't been verified yet, so don't treat its text as current-release content. Pre-GA, Salesforce publishes Help one area at a time, and an area can keep serving the previous release's text after the new release's pages appear.

**To refresh or extend a corpus**, use the standalone snapshot tool, `python -m scripts.doc_snapshot`. It needs no org and no CumulusCI. Install steps, modes, options, how to read a discovery result, and the add-an-area and add-a-release recipes are in [`scripts/doc_snapshot/README.md`](../../../scripts/doc_snapshot/README.md). This skill covers only what matters for grounding.

## Why the snapshot exists

The Salesforce Help portal renders in the browser, so `WebFetch`, `curl`, and simple scrapers get back an empty page shell. The PDF compendiums Salesforce publishes each release are huge, hard to grep, and can't be meaningfully diffed. The snapshot replaces them with one markdown file per Help article. Each file's YAML frontmatter carries the article ID, title, release, source URL, area, and fetch date. The files are small, easy to grep, diffable across releases, and precise enough for agents to cite one article at a time.

The snapshot tool (`scripts/doc_snapshot/`) drives a real Chromium through Playwright to render the portal and read each article's text. Each Help area or developer guide it captures is a preset in `scripts/doc_snapshot/presets.yaml`.

## Quick Rules

1. **Ground product claims before writing them.** If you're about to assert that a Revenue Cloud feature does X, grep the snapshot for X first. If no matching article appears, look for the area root (`ind.{area}.htm`) and walk its child article list.
2. **Article IDs are the stable identifier.** Filenames map 1:1 to Salesforce Help portal article IDs. The URL `https://help.salesforce.com/s/articleView?id=ind.billing.htm&type=5` corresponds to `docs/salesforce/{release}/help/articles/ind.billing.htm.md`.
3. **Use frontmatter, not body text, for filtering.** `release`, `area`, `parent_article`, and `fetched_at` are machine-readable. Body text is the substantive content.
4. **Re-snapshot when a release ships.** Run `python -m scripts.doc_snapshot help --release {release} --area {area}`. Re-running is safe: it fetches only articles not yet captured, unless you pass `--mode refresh`.
5. **Manifest is the index.** `docs/salesforce/{release}/help/manifest.json` lists every discovered article with status (captured / pending / errored). Use it for tooling; use `index.md` for human reading.
6. **Don't paraphrase from memory.** If you remember how a Revenue Cloud feature works, that memory might be stale or wrong — Salesforce renames objects, deprecates features, and refactors article structure between releases. Read the article, then write.

## DO NOT

1. **DO NOT** rely on the PDF compendiums (`docs/salesforce/{release}/revenue-cloud-*.pdf` or `salesforce-release-notes-*.pdf`) — they're gitignored and may not exist locally. The snapshot replaces them.
2. **DO NOT** hand-edit captured article markdown. The capture overwrites all `.md` files in `articles/` on refresh. If an article is wrong or stale, refresh from source. If you need to annotate an article with internal commentary, do it in a sibling note file (e.g., `articles/ind.billing.htm.notes.md`), not in the captured file. **Narrow exception:** a verified glued-link/duplicated-label artifact (see Known limitations below) is a hand-edit, not a refresh, because refreshing re-fetches the identical upstream typo — refreshing does not fix it and would silently undo the hand-edit on the next run. When you make this exception, update the manifest's `body_length` for that article and the affected area's + grand `total_captured_body_chars` to match (`docs/salesforce/{release}/help/manifest.json`), so the stats stay consistent with the file on disk.
3. **DO NOT** assume an article ID survives a release. `ind.billing_milestone.htm` (260) became `ind.billing_milestone_plans.htm` (262). Always grep titles AND check the current release's manifest before linking.
4. **DO NOT** confuse SObject field names with Help-portal labels. `ShouldCaptureTaxesAtHeader` is the field name; **"Capture Taxes at Header"** is the user-facing label. Both refer to the same feature. When writing seller-facing content, prefer the label; when writing developer content, prefer the field name; cite both when in doubt.
5. **DO NOT** trust thin (under ~300 bytes) Data Model articles for object schemas. Those articles are typically image-based ERDs; the `innerText` capture only retrieves the headline sentence. For object schemas, use the `revenue-cloud-data-model` skill instead.

## Sources and locations

| Path | Purpose |
|---|---|
| `docs/salesforce/{release}/help/articles/{article_id}.md` | One captured Help article, markdown body + YAML frontmatter |
| `docs/salesforce/{release}/help/manifest.json` | Machine-readable index: status, body length, parent, release, file path |
| `docs/salesforce/{release}/help/index.md` | Human-readable index: stats, captured table, pending/errored sections |
| `docs/salesforce/{release}/release-notes/` | The Revenue section of that release's release notes (`release-notes.rn_*`), same layout as `help/`, for releases with a `release_notes` preset. Use for "what changed in this release" and enablement Where/Who/How lines. Beta/Pilot tiers come from Help article titles, not from release notes. |
| `scripts/doc_snapshot/` | The snapshot tool that produces all of the above ([README](../../../scripts/doc_snapshot/README.md)). |
| `scripts/doc_snapshot/presets.yaml` | Every Help area and developer guide captured, per release. `python -m scripts.doc_snapshot list` prints them. |

Each captured article carries this frontmatter:

```yaml
---
article_id: ind.billing_billing_arrangements.htm
title: Manage Billing Arrangements
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_billing_arrangements.htm&type=5&release=262
release: "262"
release_name: "Summer '26"
area: billing
parent_article: ind.billing.htm
fetched_at: "2026-05-11"
---
```

## Developer Guide snapshot (atlas)

The **Revenue Cloud Developer Guide** lives in a different documentation system from Help: the "atlas" viewer at `developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta`. The snapshot tool's `dev-guide` subcommand captures it into `docs/salesforce/{release}/dev-guide/`, using the same layout as Help.

| Path | Purpose |
|---|---|
| `docs/salesforce/{release}/dev-guide/articles/{page_id}.md` | One captured guide page, markdown body + YAML frontmatter |
| `docs/salesforce/{release}/dev-guide/manifest.json` | Machine index: page status, section, parent, doc_version, file path |
| `docs/salesforce/{release}/dev-guide/index.md` | Human index: stats + pages grouped by TOC section |
Cross-references between pages are rewritten to point at sibling `./<page_id>.md` files, so you can follow links inside the corpus. **Frontmatter** carries `page_id`, `title`, `source_url`, `release`, `release_name`, `deliverable`, `section` (the top-level TOC section), `parent_page`, and `fetched_at`.

To refresh the whole guide or a single section, for example after a doc update:

```bash
python -m scripts.doc_snapshot dev-guide --release {release} --guide rlm
python -m scripts.doc_snapshot dev-guide --release {release} --guide rlm --section "Constraint Modeling Language"
```

### Industries Common Resources dev guide (`dev-guide-industries`)

Revenue Cloud builds on shared **Industries platform services** that its own dev guide doesn't document: Business Rules Engine (expression sets, decision tables and matrices), Context Service, OmniStudio, Discovery Framework (guided selling), Data Processing Engine/Batch, Decision Explainer, Collections and Recovery, Action Launcher, and Timeline. They're documented in a second atlas guide, `industries_reference`, which the `industries` preset captures into `docs/salesforce/{release}/dev-guide-industries/` (same layout).

Most of that guide covers other Industries clouds, so the preset captures only the sections listed in its `sections` key in `presets.yaml`. Edit that list to widen or narrow coverage. Ground OmniStudio, BRE, Context Service, Discovery Framework, and Timeline claims here.

**When to use which.** Ground **developer** claims (object/field API names, Business APIs, Apex, Metadata/Tooling types, invocable actions, **CML syntax and semantics**) against the dev-guide snapshot; ground **admin/seller** claims (feature setup, how-to, configuration) against the help snapshot. The CML section (`section: Constraint Modeling Language`, `cml_*.htm.md`) is the canonical reference for constraint-model authoring and the QuantumBit constraint-model work.

### ⚠ Where neither snapshot is authoritative: usage/consumption runtime semantics

Usage Management is the known gap in both corpora. Splitting a claim by developer
vs admin does **not** work here — check what each source actually gives you:

| Claim type | Where it lives | Example |
|-----------|----------------|---------|
| Object/field shape, picklist values | Dev guide (reference only) | `sforce_api_objects_usagecommitmentpolicy.htm.md` names `CommitmentRate` and its two values |
| What a configuration value *means* | Help (one-line definitions) | `ind.um_create_usage_commitment_policy.htm.md` defines `Bounded Object Rate` / `Lowest Commitment Rate` |
| **Runtime behaviour** — drawdown order, what each bucket decrements by, why a rated summary is empty | **Neither.** Establish by live verification. | commitment drains before grant; commitment by *discounted* qty, grant by *raw* |

**Do not infer runtime behaviour from a field description in either snapshot** — the
descriptions are one-line and omit ordering and interaction entirely. When you
establish such a rule live, record it in
`.cursor/skills/revenue-cloud-data-model/domains/usage.md` (rules) and
`docs/guides/qb-consumption-demo-scenarios.md` (worked arithmetic) so the next agent
does not have to rediscover it.

## Common grounding workflows

### Finding the article that covers a topic

```bash
# By literal term in body
grep -rl "Billing Arrangement" docs/salesforce/262/help/articles/

# By article title in manifest
python3 -c "
import json
m = json.load(open('docs/salesforce/262/help/manifest.json'))
for a in m['articles']:
    if 'arrangement' in a['title'].lower():
        print(a['article_id'], '-', a['title'])
"

# By article ID prefix (all milestone-related)
ls docs/salesforce/262/help/articles/ind.billing_milestone*.htm.md
```

### Reading an article cleanly (skip frontmatter)

```bash
# Skip frontmatter, print body only
awk '/^---$/{c++; next} c==2{print}' docs/salesforce/262/help/articles/ind.billing_invoice_batch_run.htm.md
```

### Cross-release diff

When a release ships, snapshot the matching area, then:

```bash
diff -u docs/salesforce/262/help/articles/ind.billing.htm.md \
        docs/salesforce/264/help/articles/ind.billing.htm.md
```

This surfaces every wording change, rename, or new content. Particularly useful for catching product renames (Revenue Cloud → Agentforce Revenue Management was visible in nearly every 260→262 article diff).

### Verifying a Module 2 v2 claim against the snapshot

Trailhead module work involves making product claims and citing Help articles in the Resources section. Before authoring a passage or accepting one in SME review:

1. Identify the key terms in the claim (object names, feature names, field names).
2. Grep the snapshot for each term.
3. Read the matching article(s) for full context.
4. Confirm the claim matches the article's wording or note the discrepancy.
5. When citing a Help article in Resources, use the article ID from the snapshot's frontmatter — not a guess at the URL.

## Refresh workflow

When Salesforce publishes a new release (for example 266), the snapshot tool's README has the full recipe, under **Add a release**. In outline:

1. `bootstrap --from <current> --to <new> --release-name "<name>" --discover` copies the presets into a new release block and discovers every Help area.
2. Read each area's `Discovered N unique articles` line (see **Reading the result** in the README). Before capturing an area, compare a few of its articles with the previous release's corpus. If no article IDs are new and the shared articles' text is unchanged, the area is probably still serving the previous release, so wait.
3. Capture the areas that are ready, and set an `expect_min_articles` floor on each one you verify. Set `doc_version` on the dev-guide presets once the new guide is published.
4. Run `check --release <new>` and resolve any hits (see Known limitations).
5. Commit the corpus and the `presets.yaml` change together. `.gitattributes` marks the corpus trees `linguist-generated`, so GitHub collapses them in PR diffs.

To compare releases once both are captured, run `diff -u` on the same article ID in each (see **Cross-release diff** above).

## Per-area snapshots

Each functional area in Revenue Cloud has its own root Help article and ID prefix. The areas follow the data-model domains documented in `revenue-cloud-data-model/SKILL.md`, but **not one-to-one**:

1. **Transaction Management is ONE Help area, not four.** Quote / Order / Contract / Asset / Lifecycle articles all share the `ind.qocal_*` prefix (Quote-Order-Contract-Asset-Lifecycle). One snapshot variant captures them all.
2. **Help-portal prefixes are short and idiomatic, not the long domain names.** Rate Management uses `ind.rm_*`, Usage Management uses `ind.um_*`, etc. Always verify with the live sidebar before assuming.

| Data-model domain | Help-portal area | Root article ID | ID prefix |
|---|---|---|---|
| PCM | Product Catalog Management | `ind.product_catalog_introduction.htm` | `ind.product_catalog` |
| Pricing | Pricing (Salesforce Pricing) | `ind.pricing_salesforce_pricing.htm` | `ind.pricing` |
| Rate Management | Rate Management | `ind.rm_rate_management.htm` | `ind.rm` |
| Configurator | Product Configurator | `ind.product_configurator_introduction.htm` | `ind.product_configurator` |
| Transaction Mgmt | Transaction Management (Q/O/C/A/L combined) | `ind.qocal_sales_transactions_rev_cloud.htm` | `ind.qocal` |
| DRO | DRO / Fulfillment | `ind.dro_dynamic_revenue_orchestrator.htm` | `ind.dro` |
| Usage Management | Usage Management | `ind.um_usage_management.htm` | `ind.um` |
| Billing | Billing | `ind.billing.htm` | `ind.billing` |
| **Cross-domain** | **Agentforce for Revenue Management** | `ind.rev_agent_overview.htm` | `ind.rev_agent` |
| Approvals | Advanced Approvals | `ind.approvals_advanced_approvals.htm` | `ind.approvals` |
| Collections | Collections and Recovery | `ind.collections.htm` | `ind.collections` |

**Manifest structure.** The shared manifest at `docs/salesforce/{release}/help/manifest.json` carries a top-level `areas` array that accumulates per-area run metadata (root, prefix, snapshot dates, per-area stats). Each article entry in `manifest.articles` is tagged with its `area` for filtering. The `index.md` renders an overall stats table + a per-area coverage summary + per-area captured-articles sections when the manifest covers multiple areas, falling back to the original single-area layout when only one area is captured. Use `manifest.areas` (or `grep area:` on per-article frontmatter) to filter by functional area.

### Agent content is cross-cutting — grep across multiple snapshots

The subagents under **Agentforce for Revenue Management** operate inside specific functional areas, and their how-to documentation lives under each area's prefix — not under `ind.rev_agent_*`. Examples:

| Subagent | Topic-reference article (in `ind.rev_agent_*`) | How-to / use-case articles (in functional-area prefix) |
|---|---|---|
| Product Selection | `ind.rev_agent_pcm_topic_product_selection.htm` | `ind.product_catalog_agentforce_*` |
| Product Description Generation | `ind.rev_agent_pcm_topic_product_description_generation.htm` | `ind.product_catalog_agentforce_*` |
| Quote Management | `ind.rev_agent_qocal_topic_quote_management.htm` | `ind.qocal_agentforce_quote_mgmt.htm`, other `ind.qocal_agentforce_*` |
| Consumption Management | `ind.rev_agent_usage_topic_consumption_management.htm` | likely `ind.um_agentforce_*` (verify in the usage snapshot) |
| Invoice Line Explanation | `ind.rev_agent_billing_topic_invoice_line_explanation.htm` | `ind.billing_agentforce_billing_agent.htm`, `ind.billing_agentforce_billingagent_usecase.htm` |
| Billing Collections Management | `ind.rev_agent_topic_billing_collections_management.htm` | `ind.billing_agentforce_*` |
| Billing Inquiries | `ind.rev_agent_topic_billing_inquiries.htm` | `ind.billing_agentforce_*` |

**Implication for validation:** when grounding an agent claim, **grep across ALL captured snapshots**, not just the dedicated agents snapshot. The dedicated snapshot has the topic-reference; the functional-area snapshots have the operating context, setup steps, use cases, and Experience Cloud framing. Example:

```bash
# WRONG — misses ind.qocal_agentforce_quote_mgmt.htm and similar:
grep -l "Quote Management" docs/salesforce/262/help/articles/ind.rev_agent_*.md

# RIGHT — catches both topic-reference and how-to articles:
grep -l "Quote Management" docs/salesforce/262/help/articles/*.md
```

To get full agent coverage you need the `agents` preset (the dedicated area) **plus** every functional area's snapshot. Without the functional-area snapshots, you'll have agent topic descriptions but no how-to / use-case grounding.

**IMPORTANT — don't conflate adjacent domains.** Usage Management (`ind.um_*`) and Rate Management (`ind.rm_*`) are two distinct data-model domains and two distinct Help-portal areas. Pricing (`ind.pricing_*`) and Rate Management (`ind.rm_*`) are similarly distinct. Configurator (`ind.product_configurator_*`) is its own domain — easy to skip past because it has only 4 objects, but the Help portal area is real and covers configuration rules / flows that affect Quote/Order configuration. The `article_id_prefix` filter is a single startswith match, so capturing each requires **its own preset**. That's why `presets.yaml` defines `usage` and `rating` separately: content that spans both needs both snapshots.

To add an area, follow **Add an area** in the [snapshot tool README](../../../scripts/doc_snapshot/README.md).

## Known limitations

- **Data Model articles are thin.** Articles named `ind.*_data_model_*.htm` are usually short (under 500 bytes captured) because the actual ERD is an image. For object schemas, fields, and relationships, use the `revenue-cloud-data-model` skill instead.
- **Article ID renames are silent.** When Salesforce renames an article between releases, the old ID 404s and the new ID may not be obvious. Two examples from 260→262: `ind.billing_milestone.htm` → `ind.billing_milestone_plans.htm`; `ind.billing_payment_terms.htm` is "Create Payment Terms" (its parent "Define Billing Policies and Billability Rules" is at `ind.billing_policies_and_treatments.htm`). When you encounter a 404, search the new release's manifest by title.
- **SObject field names vs. Help labels** diverge. The schema field `ShouldCaptureTaxesAtHeader` is labeled "Capture Taxes at Header" in the Help portal. The field `TaxEngineAddress` is referenced indirectly in articles ("the address used for tax calculation"). When verifying a claim that uses a field name, search by both the field name AND the human label.
- **Image-only content is invisible.** The capture is text-only (innerText). Diagrams, screenshots, and ERDs are not captured. If a Help article relies on an image for the substantive content, the captured markdown is thin.
- **Some articles span multiple Help "tabs"** (notes, considerations, examples). The capture reads only the main article tab, so secondary tabs may be missing. If an article seems incomplete, open it in a browser.
- **Rare glued-link / duplicated-label text artifacts are upstream Salesforce content typos, not extraction bugs.** Confirmed by inspecting the live page: Salesforce's own source HTML sometimes omits the space before a link (`See<a>Create a Constant Resource</a>` renders as "SeeCreate a Constant Resource") or has a callout badge whose label happens to duplicate the paragraph's own leading word ("NOTE Note: ..."). `innerText`-based capture is verbatim by design, so it faithfully reproduces these. Recapturing does not fix them — verify the hit against the live DOM first, then hand-edit the affected article, and only in the active release's corpus; frozen corpora of past releases are left as they are. `python -m scripts.doc_snapshot check [--release {release}]` is a non-gating spot-check for the glued-link class — it flags a pattern, not a confirmed defect — run it after any capture/refresh. Hits are rare.

## Cross-reference with related skills

- **[`release-enablement`](../release-enablement/SKILL.md)** — for authoring Hands-On exercises per release. The snapshot is a primary input to that workflow.
- **[`revenue-cloud-data-model`](../revenue-cloud-data-model/SKILL.md)** — for object/field reference, ERDs, and schema details. Use this when the Help docs are thin (Data Model articles, image-only content).
- **[`doc-consistency`](../doc-consistency/SKILL.md)** — pre-merge consistency checks. When the snapshot reveals product renames or terminology shifts, propagate them through internal docs that reference the Help articles.
- **[`sfdmu-data-plans`](../sfdmu-data-plans/SKILL.md)** — for QuantumBit sample data referenced in walkthroughs.

## Change log

- **2026-10-02** — The `snapshot_*` CumulusCI tasks were replaced by the standalone snapshot tool `scripts/doc_snapshot` (`help`, `dev-guide`, `run`, `check`, `bootstrap`, `list`), with presets in `scripts/doc_snapshot/presets.yaml`. Moves: `tasks/rlm_snapshot_help.py` → `scripts/doc_snapshot/help_portal.py`, `tasks/rlm_snapshot_dev_guide.py` → `scripts/doc_snapshot/dev_guide.py`, and `scripts/ai/check_help_corpus_text_artifacts.py` → `scripts/doc_snapshot/check.py`. Captured output is unchanged apart from the `capture_method` provenance string. The skill now leaves tool mechanics (install, modes, options, reading a discovery, adding areas and releases) to the tool's README, and no longer records per-release counts or readiness, which `list` and each corpus's `index.md` show.
- **2026-09-07** — Added the glued-link/duplicated-label text-artifact known limitation and `scripts/ai/check_help_corpus_text_artifacts.py` spot-check (todo 184). Carved a narrow exception into DO NOT #2 (hand-edit prohibition) for this artifact class, since a refresh cannot fix an upstream typo (PR #412 review).
- **2026-05-11** — Skill created. Initial 262 Billing snapshot covers 171 articles (~440 KB).
