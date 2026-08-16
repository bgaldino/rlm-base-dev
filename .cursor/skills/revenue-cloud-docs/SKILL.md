---
name: revenue-cloud-docs
description: >-
  Ground product claims about Salesforce Revenue Cloud (Agentforce Revenue
  Management) — Billing, Pricing, Quoting, Orders, Contracts, Assets, Usage,
  DRO — against the captured Salesforce Help portal snapshots at
  `docs/salesforce/{release}/help/`. Use before authoring or accepting any
  Trailhead module passage, enablement exercise, internal doc, or SME review
  response that asserts how a Revenue Cloud feature works. Use when verifying
  object names, field labels, feature behavior, or terminology against the
  current release's Help articles. Use when refreshing the snapshot for a new
  Salesforce release (264 and later) via the `snapshot_{area}_help_{release}`
  CCI tasks. The snapshot replaces the unwieldy per-release PDF compendiums
  with grep-friendly, diffable per-article markdown that AI agents can read
  surgically.
---

# Revenue Cloud Help Snapshot — AI Grounding Source

Use the Salesforce Help portal snapshots at `docs/salesforce/{release}/help/` as the canonical source of truth for product claims about Revenue Cloud — Billing, Pricing, Quoting, Orders, Contracts, Assets, Usage, and the adjacent areas. Every Trailhead module, enablement exercise, internal doc, or SME review response that asserts something about how Revenue Cloud works should ground that assertion against an article in the snapshot before being written or accepted.

For **developer-facing** material — standard object/field reference, Business APIs, Apex, Metadata/Tooling API types, invocable actions, and **Constraint Modeling Language (CML)** — use the companion **Developer Guide snapshot** at `docs/salesforce/{release}/dev-guide/` (the atlas Revenue Cloud Developer Guide). See [Developer Guide snapshot (atlas)](#developer-guide-snapshot-atlas) below. Rule of thumb: **Help = how an admin/seller uses a feature; Dev Guide = the objects, fields, APIs, and CML a developer builds against.**

> **Branch note (264).** This branch targets Release 264 (Winter '27, API v68.0), but **262 is still the only captured corpus** — `docs/salesforce/262/help/` and `docs/salesforce/262/dev-guide*/`. The `snapshot_*_264` task variants exist in `cumulusci.yml`, but their root article IDs and prefixes are inherited from 262 and **unverified** (264 is pre-GA and has no published release notes), so run `mode: discover` first. Until a 264 capture lands, ground claims against the 262 snapshot and flag anything a 264 change could invalidate.
>
> **A passing `discover` proves nothing on its own — it exits 0 having found zero articles.** `_discover_articles` catches a sidebar-walker failure, logs it, and returns `[]`; the caller filters by prefix, logs the count, writes the manifest, and exits cleanly without ever rejecting an empty result (`tasks/rlm_snapshot_help.py`, discovery phase). A wrong root, a reorganized ID prefix, and a JS failure are therefore indistinguishable from success at the exit code. **Read the count this run logged:**
>
> ```bash
> cci task run snapshot_pcm_help_264 -o mode discover 2>&1 | grep 'unique articles'
> # "Discovered 0 unique articles (0 total before prefix filter)"   -> bad root, or the walker failed
> # "Discovered 0 unique articles (N total before prefix filter)"   -> root walks, prefix is wrong for this area
> ```
>
> **Do not substitute the manifest's `stats.discovered` for that line** — it is cumulative, not per-run. `_merge_discovered` only ever adds, so an empty discovery leaves the prior articles untouched; `_compute_stats` then counts **every area at once** (262 reports 935, the sum of 11 areas), and the per-area figure under `areas[]` is likewise the running total for that area. A failed re-discovery therefore leaves both numbers positive and unchanged. On a first 264 run neither exists — `docs/salesforce/264/help/` is not there yet, so reading the manifest raises `FileNotFoundError`.
>
> And even a non-zero discover says nothing about *whether the release's content was written*: on a pre-GA release the articles behind a valid root can still hold the previous release's text, so a full capture can spend 10–15 minutes writing 262 content under a 264 path. Per-area readiness — which areas are worth capturing yet, and what to watch before re-checking — is assessed in the private artifacts repo (`.agents/artifacts/todos/`, todo 145), because it derives from internal tracking that does not belong in this repo.

## Why the snapshot exists

The Salesforce Help portal is an LWC SPA. `WebFetch`, `curl`, and naive scrapers all return an unrendered shell. The PDF Help compendium that Salesforce publishes per release is huge (124 MB for Spring '26 Billing alone), terrible for grep, opaque to file diffs, and impractical to commit. The snapshot replaces it with per-article markdown — one file per Help article, with YAML frontmatter carrying article ID, title, release, source URL, area, and fetched date. The markdown is small (~450 KB for ~170 Billing articles in 262), grep-friendly, diffable across releases, and structured well enough for AI agents to use as surgical grounding.

The snapshot is generated by `tasks/rlm_snapshot_help.py` (CCI custom task) using Playwright + a recursive shadow-DOM walker. The same pattern works for any Help area that has a root article ID and a consistent ID prefix.

## Quick Rules

1. **Ground product claims before writing them.** If you're about to assert that a Revenue Cloud feature does X, grep the snapshot for X first. If no matching article appears, look for the area root (`ind.{area}.htm`) and walk its child article list.
2. **Article IDs are the stable identifier.** Filenames map 1:1 to Salesforce Help portal article IDs. The URL `https://help.salesforce.com/s/articleView?id=ind.billing.htm&type=5` corresponds to `docs/salesforce/{release}/help/articles/ind.billing.htm.md`.
3. **Use frontmatter, not body text, for filtering.** `release`, `area`, `parent_article`, and `fetched_at` are machine-readable. Body text is the substantive content.
4. **Re-snapshot when a release ships.** Run the matching `snapshot_{area}_help_{release}` CCI task. The task is idempotent; re-running on an existing snapshot only refreshes pending articles unless you pass `mode: refresh`.
5. **Manifest is the index.** `docs/salesforce/{release}/help/manifest.json` lists every discovered article with status (captured / pending / errored). Use it for tooling; use `index.md` for human reading.
6. **Don't paraphrase from memory.** If you remember how a Revenue Cloud feature works, that memory might be stale or wrong — Salesforce renames objects, deprecates features, and refactors article structure between releases. Read the article, then write.

## DO NOT

1. **DO NOT** rely on the PDF compendiums (`docs/salesforce/{release}/revenue-cloud-*.pdf` or `salesforce-release-notes-*.pdf`) — they're gitignored and may not exist locally. The snapshot replaces them.
2. **DO NOT** hand-edit captured article markdown. The capture task overwrites all `.md` files in `articles/` on refresh. If an article is wrong or stale, refresh from source. If you need to annotate an article with internal commentary, do it in a sibling note file (e.g., `articles/ind.billing.htm.notes.md`), not in the captured file.
3. **DO NOT** assume an article ID survives a release. `ind.billing_milestone.htm` (260) became `ind.billing_milestone_plans.htm` (262). Always grep titles AND check the current release's manifest before linking.
4. **DO NOT** confuse SObject field names with Help-portal labels. `ShouldCaptureTaxesAtHeader` is the field name; **"Capture Taxes at Header"** is the user-facing label. Both refer to the same feature. When writing seller-facing content, prefer the label; when writing developer content, prefer the field name; cite both when in doubt.
5. **DO NOT** trust thin (under ~300 bytes) Data Model articles for object schemas. Those articles are typically image-based ERDs; the `innerText` capture only retrieves the headline sentence. For object schemas, use the `revenue-cloud-data-model` skill instead.

## Sources and locations

| Path | Purpose |
|---|---|
| `docs/salesforce/{release}/help/articles/{article_id}.md` | One captured Help article, markdown body + YAML frontmatter |
| `docs/salesforce/{release}/help/manifest.json` | Machine-readable index: status, body length, parent, release, file path |
| `docs/salesforce/{release}/help/index.md` | Human-readable index: stats, captured table, pending/errored sections |
| `tasks/rlm_snapshot_help.py` | The capture task (Playwright + shadow-DOM walker) |
| `cumulusci.yml` | Task registrations: `snapshot_salesforce_help` (generic), plus per-release area variants — the `snapshot_*_262` family, `snapshot_billing_help_260`, and the `snapshot_*_264` family (264 root article IDs are inherited from 262 and **unverified**; run `-o mode discover` first) |

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

The **Revenue Cloud Developer Guide** lives in a different documentation system than Help — the "atlas" viewer at `developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta`. It is captured separately by **`tasks/rlm_snapshot_dev_guide.py`** into `docs/salesforce/{release}/dev-guide/`, mirroring the help layout (`articles/{page_id}.md` + `manifest.json` + `index.md`).

| Path | Purpose |
|---|---|
| `docs/salesforce/{release}/dev-guide/articles/{page_id}.md` | One captured guide page, markdown body + YAML frontmatter |
| `docs/salesforce/{release}/dev-guide/manifest.json` | Machine index: page status, section, parent, doc_version, file path |
| `docs/salesforce/{release}/dev-guide/index.md` | Human index: stats + pages grouped by TOC section |
| `tasks/rlm_snapshot_dev_guide.py` | The capture task (Playwright + atlas JSON content API → markdown) |

**Why a separate task.** The atlas viewer exposes a clean JSON content API (`get_document` for the TOC, `get_document_content/<deliverable>/<page_id>/en-us/<doc_version>` per page), but it sits behind Akamai bot protection — plain `requests`/`curl` get HTTP 403. The task drives the API from inside a Playwright browser context (so requests carry the browser's cookies/TLS) and converts the returned HTML to markdown (`markdownify` when injected, else a built-in converter). Intra-guide cross-references are rewritten to sibling `./<page_id>.md` files so the corpus is self-navigable.

**Frontmatter** carries `page_id`, `title`, `source_url`, `release`, `release_name`, `deliverable`, `section` (TOC top-level ancestor), `parent_page`, and `fetched_at`.

**Capture / refresh.** Same modes as the help task (`discover` / `capture` / `all` / `refresh`). Run the whole guide or one section:

```bash
cci task run snapshot_dev_guide_262                                   # whole guide
cci task run snapshot_dev_guide_262 -o section "Constraint Modeling Language"   # one TOC section
cci task run snapshot_dev_guide_262 -o mode refresh                  # re-capture all (after a release update)
```

Requires Playwright in the CCI venv (same inject as the help task); `markdownify` is an optional inject for best table/list fidelity. See the task docstring for setup.

### Industries Common Resources dev guide (`dev-guide-industries`)

RC builds on shared **Industries common platform services** that the RLM dev guide doesn't document — Business Rules Engine (expression sets, decision tables/matrices), Context Service, OmniStudio, Discovery Framework (guided selling), Data Processing Engine/Batch, Decision Explainer, Collections and Recovery, Action Launcher, and Timeline. These live in a **second atlas deliverable**, `industries_reference`, captured separately into `docs/salesforce/{release}/dev-guide-industries/` (same `articles/` + `manifest.json` + `index.md` layout) by the same task with a distinct `output_dir`.

The full Industries Common Resources guide is ~1435 pages across 37 sections — most for *other* Industries clouds (Digital Lending, Document/Form Readers, Process Compliance, etc.). The snapshot is **scoped to the ~571 RC-relevant pages** (the nine sections' TOC subtrees) via the task's `sections` list; `follow_links` stays off so an out-of-scope cross-reference can't drag in unrelated sections:

```bash
cci task run snapshot_industries_dev_guide_262                # the 9 RC-relevant sections
cci task run snapshot_industries_dev_guide_262 -o mode refresh
# widen/narrow by editing `sections` (comma-separated TOC titles or page_ids) in cumulusci.yml
```

Ground OmniStudio / BRE / Context Service / Discovery Framework / Timeline claims here. (The 262 industries snapshot is complete: 571 pages, 0 errored.)

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

When 264 ships, run the matching snapshot task, then:

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

When a new release ships (e.g., Salesforce announces 264 GA):

1. **Add the release-specific task variants** in `cumulusci.yml`:

   ```yaml
   snapshot_billing_help_264:
       class_path: tasks.rlm_snapshot_help.SnapshotSalesforceHelp
       options:
           release_version: "264"
           release_name: "Winter '27"
           area: billing
           root_article_id: ind.billing.htm
           article_id_prefix: ind.billing
           mode: all
   ```

2. **Run discovery first** to see what's new:

   ```bash
   cci task run snapshot_billing_help_264 -o mode discover 2>&1 | grep 'unique articles'
   ```

   The discovery phase walks the sidebar and writes `manifest.json` with all discovered article IDs as `pending`. Compare against the previous release's manifest to see additions, removals, renames.

   **Read the `Discovered N unique articles` line before moving on — a zero-article discovery also exits 0**, so the exit code cannot distinguish a good walk from a wrong root, a reorganized prefix, or a walker crash. That log line is the only number computed from *this* invocation. The manifest's `stats.discovered` is cumulative and cannot substitute for it: an empty discovery adds nothing and removes nothing, so both the top-level count (every area summed) and the per-area count under `areas[]` survive a failed re-walk unchanged.

3. **Run full capture**:

   ```bash
   cci task run snapshot_billing_help_264
   ```

   Captures every pending article in parallel (default concurrency 4). ~10-15 minutes for ~170 articles.

4. **Validate**:

   ```bash
   # File count matches manifest
   ls docs/salesforce/264/help/articles/ | wc -l
   python3 -c "import json; m=json.load(open('docs/salesforce/264/help/manifest.json')); print(sum(1 for a in m['articles'] if a.get('status')=='captured'))"

   # No errors
   python3 -c "import json; m=json.load(open('docs/salesforce/264/help/manifest.json')); print([a for a in m['articles'] if a.get('status')=='error'])"

   # No breadcrumb noise leaked through (should print 0)
   grep -l "^You are here:" docs/salesforce/264/help/articles/*.md | wc -l
   ```

5. **Commit**. A single-area snapshot is typically 100–500 KB; the full multi-area snapshot for one release lands around 4–5 MB (the 262 snapshot is **~4.3 MB across 935 articles** — see the *Per-area snapshots* table below). Mark the directory as generated in `.gitattributes` (`docs/salesforce/*/help/** linguist-generated=true`) so GitHub auto-collapses the diff on refresh PRs.

## Per-area snapshots

Each functional area in Revenue Cloud has its own root Help article and ID prefix. The areas mirror the **9 data-model domains** documented in `revenue-cloud-data-model/SKILL.md`, but the mapping to Help-portal areas is **not strictly 1:1**. Two important observations from the 2026-05-11 sidebar walk:

1. **Transaction Management is ONE Help area, not four.** Quote / Order / Contract / Asset / Lifecycle articles all share the `ind.qocal_*` prefix (Quote-Order-Contract-Asset-Lifecycle). One snapshot variant captures them all.
2. **Help-portal prefixes are short and idiomatic, not the long domain names.** Rate Management uses `ind.rm_*`, Usage Management uses `ind.um_*`, etc. Always verify with the live sidebar before assuming.

| Data-model domain | Help-portal area | Root article ID | ID prefix | Articles |
|---|---|---|---|---|
| PCM | Product Catalog Management | `ind.product_catalog_introduction.htm` | `ind.product_catalog` | 107 ✓ |
| Pricing | Pricing (Salesforce Pricing) | `ind.pricing_salesforce_pricing.htm` | `ind.pricing` | 110 ✓ |
| Rate Management | Rate Management | `ind.rm_rate_management.htm` | `ind.rm` | 35 ✓ |
| Configurator | Product Configurator | `ind.product_configurator_introduction.htm` | `ind.product_configurator` | 76 ✓ |
| Transaction Mgmt | Transaction Management (Q/O/C/A/L combined) | `ind.qocal_sales_transactions_rev_cloud.htm` | `ind.qocal` | 170 ✓ |
| DRO | DRO / Fulfillment | `ind.dro_dynamic_revenue_orchestrator.htm` | `ind.dro` | 70 ✓ |
| Usage Management | Usage Management | `ind.um_usage_management.htm` | `ind.um` | 52 ✓ |
| Billing | Billing | `ind.billing.htm` | `ind.billing` | 171 ✓ |
| **Cross-domain** | **Agentforce for Revenue Management** | `ind.rev_agent_overview.htm` | `ind.rev_agent` | 13 ✓ (topic-reference articles; functional-area how-to articles are captured under each area's prefix) |
| Approvals | Advanced Approvals | `ind.approvals_advanced_approvals.htm` | `ind.approvals` | 34 ✓ |
| Collections | Collections and Recovery | `ind.collections.htm` | `ind.collections` | 97 ✓ |

**Total 262 snapshot: 935 articles, ~4.3 MB markdown.** Complete coverage of all 9 RC data-model domains plus the cross-domain Agentforce-for-RC agent suite and the Collections & Recovery area (97 articles, all captured). Captured 2026-05-11 / 2026-05-12 (collections 2026-06-21; final 3 collections articles recaptured 2026-08-04 — 0 errored).

**Manifest structure (post-2026-05-12 polish).** The shared manifest at `docs/salesforce/{release}/help/manifest.json` carries a top-level `areas` array that accumulates per-area run metadata (root, prefix, snapshot dates, per-area stats). Each article entry in `manifest.articles` is tagged with its `area` for filtering. The `index.md` renders an overall stats table + a per-area coverage summary + per-area captured-articles sections when the manifest covers multiple areas, falling back to the original single-area layout when only one area is captured. Use `manifest.areas` (or `grep area:` on per-article frontmatter) to filter by functional area.

### Agent content is cross-cutting — grep across multiple snapshots

The 7 subagents under **Agentforce for Revenue Management** operate inside specific functional areas, and their how-to documentation lives under each area's prefix — not under `ind.rev_agent_*`. Examples confirmed against the 262 snapshot:

| Subagent | Topic-reference article (in `ind.rev_agent_*`) | How-to / use-case articles (in functional-area prefix) |
|---|---|---|
| Product Selection | `ind.rev_agent_pcm_topic_product_selection.htm` | `ind.product_catalog_agentforce_*` |
| Product Description Generation | `ind.rev_agent_pcm_topic_product_description_generation.htm` | `ind.product_catalog_agentforce_*` |
| Quote Management | `ind.rev_agent_qocal_topic_quote_management.htm` | `ind.qocal_agentforce_quote_mgmt.htm`, other `ind.qocal_agentforce_*` |
| Consumption Management | `ind.rev_agent_usage_topic_consumption_management.htm` | likely `ind.um_agentforce_*` (verify when running Usage snapshot deltas) |
| Invoice Line Explanation | `ind.rev_agent_billing_topic_invoice_line_explanation.htm` | `ind.billing_agentforce_billing_agent.htm`, `ind.billing_agentforce_billingagent_usecase.htm` (already captured) |
| Billing Collections Management | `ind.rev_agent_topic_billing_collections_management.htm` | `ind.billing_agentforce_*` |
| Billing Inquiries | `ind.rev_agent_topic_billing_inquiries.htm` | `ind.billing_agentforce_*` |

**Implication for validation:** when grounding an agent claim, **grep across ALL captured snapshots**, not just the dedicated agents snapshot. The dedicated snapshot has the topic-reference; the functional-area snapshots have the operating context, setup steps, use cases, and Experience Cloud framing. Example:

```bash
# WRONG — misses ind.qocal_agentforce_quote_mgmt.htm and similar:
grep -l "Quote Management" docs/salesforce/262/help/articles/ind.rev_agent_*.md

# RIGHT — catches both topic-reference and how-to articles:
grep -l "Quote Management" docs/salesforce/262/help/articles/*.md
```

To get full agent coverage you need: `snapshot_agents_help_262` (the dedicated area) **plus** every functional area's snapshot. Without the functional-area snapshots, you'll have agent topic descriptions but no how-to / use-case grounding.

**IMPORTANT — don't conflate adjacent domains.** Usage Management (`ind.um_*`) and Rate Management (`ind.rm_*`) are two distinct data-model domains and two distinct Help-portal areas. Pricing (`ind.pricing_*`) and Rate Management (`ind.rm_*`) are similarly distinct. Configurator (`ind.product_configurator_*`) is its own domain — easy to skip past because it has only 4 objects, but the Help portal area is real and covers configuration rules / flows that affect Quote/Order configuration. The `article_id_prefix` filter is a single startswith match, so capturing each requires **its own task variant**. Module 3 of the L2 Billing Trailhead mix straddles Usage + Rating, which is why `cumulusci.yml` defines `snapshot_usage_help_262` AND `snapshot_rating_help_262` separately.

To add a new area: walk the sidebar from the Revenue Lifecycle Management parent (`ind.revenue_lifecycle_management.htm`) using the `SIDEBAR_WALKER_JS` pattern from `tasks/rlm_snapshot_help.py`. Note the area's root article ID, identify the prefix that filters its child articles, and add a new task in `cumulusci.yml`. The same task class handles every area; only options differ. Always run `mode: discover` first and read the `Discovered N unique articles` line it logs — the task does **not** fail on a wrong root ID; it exits 0 with zero discovered articles, so that per-run count is the only signal. Do not read `stats.discovered` from the manifest instead: it sums every area and retains prior runs, so it stays positive when a new area discovers nothing.

## Known limitations

- **Data Model articles are thin.** Articles named `ind.*_data_model_*.htm` are usually short (under 500 bytes captured) because the actual ERD is an image. For object schemas, fields, and relationships, use the `revenue-cloud-data-model` skill instead.
- **Article ID renames are silent.** When Salesforce renames an article between releases, the old ID 404s and the new ID may not be obvious. Two examples from 260→262: `ind.billing_milestone.htm` → `ind.billing_milestone_plans.htm`; `ind.billing_payment_terms.htm` is "Create Payment Terms" (its parent "Define Billing Policies and Billability Rules" is at `ind.billing_policies_and_treatments.htm`). When you encounter a 404, search the new release's manifest by title.
- **SObject field names vs. Help labels** diverge. The schema field `ShouldCaptureTaxesAtHeader` is labeled "Capture Taxes at Header" in the Help portal. The field `TaxEngineAddress` is referenced indirectly in articles ("the address used for tax calculation"). When verifying a claim that uses a field name, search by both the field name AND the human label.
- **Image-only content is invisible.** The capture is text-only (innerText). Diagrams, screenshots, and ERDs are not captured. If a Help article relies on an image for the substantive content, the captured markdown is thin.
- **Some articles span multiple Help "tabs"** (notes, considerations, examples). The capture currently only walks the main article tab; secondary tabs may be missed. Re-fetch manually via Chrome MCP if a specific article seems incomplete.

## Cross-reference with related skills

- **[`release-enablement`](../release-enablement/SKILL.md)** — for authoring Hands-On exercises per release. The snapshot is a primary input to that workflow.
- **[`revenue-cloud-data-model`](../revenue-cloud-data-model/SKILL.md)** — for object/field reference, ERDs, and schema details. Use this when the Help docs are thin (Data Model articles, image-only content).
- **[`doc-consistency`](../doc-consistency/SKILL.md)** — pre-merge consistency checks. When the snapshot reveals product renames or terminology shifts, propagate them through internal docs that reference the Help articles.
- **[`sfdmu-data-plans`](../sfdmu-data-plans/SKILL.md)** — for QuantumBit sample data referenced in walkthroughs.

## Snapshot Authoring Notes

The capture task is intentionally idempotent and refresh-friendly. Modes:

| Mode | Behavior |
|---|---|
| `discover` | Walk sidebar, update manifest with all IDs as `pending`. No body capture. Fast smoke test. |
| `capture` | Read existing manifest, capture pending articles only. Skips already-captured. |
| `all` (default) | Discover then capture. Idempotent — re-running won't re-fetch already-captured articles. |
| `refresh` | Re-capture every article, overwriting existing files. Use after a release update or a JS extractor change. |

Setup (once per environment):

```bash
# pipx-installed CCI (recommended)
pipx inject cumulusci playwright
$(pipx environment --value PIPX_LOCAL_VENVS)/cumulusci/bin/python -m playwright install chromium
```

See `tasks/rlm_snapshot_help.py` module docstring for full options and alternate setup paths.

## Change log

- **2026-05-11** — Skill created. Initial 262 Billing snapshot covers 171 articles (~440 KB).
