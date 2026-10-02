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
  Salesforce release (264 and later) via the standalone
  `python -m scripts.doc_snapshot` CLI. The snapshot replaces the unwieldy per-release PDF compendiums
  with grep-friendly, diffable per-article markdown that AI agents can read
  surgically.
---

# Revenue Cloud Help Snapshot — AI Grounding Source

Use the Salesforce Help portal snapshots at `docs/salesforce/{release}/help/` as the canonical source of truth for product claims about Revenue Cloud — Billing, Pricing, Quoting, Orders, Contracts, Assets, Usage, and the adjacent areas. Every Trailhead module, enablement exercise, internal doc, or SME review response that asserts something about how Revenue Cloud works should ground that assertion against an article in the snapshot before being written or accepted.

For **developer-facing** material — standard object/field reference, Business APIs, Apex, Metadata/Tooling API types, invocable actions, and **Constraint Modeling Language (CML)** — use the companion **Developer Guide snapshot** at `docs/salesforce/{release}/dev-guide/` (the atlas Revenue Cloud Developer Guide). See [Developer Guide snapshot (atlas)](#developer-guide-snapshot-atlas) below. Rule of thumb: **Help = how an admin/seller uses a feature; Dev Guide = the objects, fields, APIs, and CML a developer builds against.**

> **Branch note (264).** This branch targets Release 264 (Winter '27, API v68.0). **The Dev Guide corpora are captured at 264** — `docs/salesforce/264/dev-guide/` and `docs/salesforce/264/dev-guide-industries/`, both genuinely 264 content (prerelease disclaimer present on every article). **Help is now captured at 264 for ten areas** — `configurator`, `transaction_mgmt` (Contract Lifecycle Management folds into this preset), `billing`, `pcm`, `dro`, `pricing`, `rating`, `usage`, `agents`, and `approvals` — spot-checked against their 262 twins (`docs/salesforce/264/help/`). For `dro`, articles shared with 262 came back byte-identical (expected — not every article changes release to release); readiness was instead confirmed by 29 articles that exist only at 264 (99 discovered vs 70 at 262), with real, substantive bodies (e.g. `ind.dro_time_aware_fulfillment_example_add.htm`) — net-new content is proof a stale-262-serving portal cannot produce. For `pricing`, all 110 262 articles are present plus 45 net-new (155 discovered), and a shared article's body text itself changed release to release (`ind.pricing_pricing_procedures.htm`: "Revenue Cloud" → "Revenue Management (formerly Revenue Cloud)", updated edition/license language) — a second, independent readiness signal alongside net-new ids. For `rating`, all 35 262 articles are present plus 35 net-new (70 discovered vs 35 at 262) — the same net-new-only signal as `dro`. For `usage`, discovery matched the 262 twin exactly (52 articles) and shared bodies differ (title rename to "Revenue Management", edition-text changes). For `agents`, 17 discovered vs 13 at 262 (4 net-new, an Approval Agent), plus edition-text diffs on shared ids. For `approvals`, 43 discovered vs 34 at 262, plus a title rename ("Revenue Management (formerly Revenue Cloud)") and net-new articles (e.g. approval delegation records). **`collections` was checked and found NOT ready** — discovery matched the 262 twin exactly (97 articles) but 96/97 shared bodies came back byte-identical with zero net-new ids, the portal's own tell that it is still serving 262 text for that area; the capture was discarded rather than committed (pack 145 rule). Re-run `--mode discover` + a byte-diff spot-check on `collections` periodically until it shows the same net-new-or-changed-text signal the other areas did. Salesforce publishes 264 Help per-area on its own schedule (see todo pack 183 for the latest per-area readiness, following on from closed pack 145). For the Dev Guide, note that the unversioned atlas endpoint (`atlas.en-us.<deliverable>.meta`) keeps serving 262 even after 264 publishes — `mode: discover` alone will not pick up 264. The capture used an explicit `doc_version: "264.0"` (now set in the 264 dev-guide presets; `--doc-version` on the CLI) on `--mode capture` (see todo pack 156 for the full mechanism and why the versioned URL/meta-slug doesn't work as a direct API call). **Changing `doc_version` on a manifest that already has captured pages now requires `mode: refresh`** — `capture`/`all` raise `OptionsError` instead of silently mislabeling old-version content as new (a plain `discover` run is exempt and never writes a version bump over captured pages that would trigger this on the next capture).
>
> **Help discovery now polls until the sidebar stabilizes and raises loudly on a thin walk** (pack 146). The portal's SPA hydrates the sidebar tree at variable speed — live probing showed the same page taking anywhere from ~3s to >6s, with roughly 1 in 4 single-read attempts at a fixed wait catching the tree mid-hydration. `_discover_articles` polls every `wait_ms` up to `discover_timeout_ms` (default 20s) until the prefix-matching count holds steady across two consecutive reads (with `subtree_only`, the whole walk's id, parent and top-level signature must also repeat, since the prune reads the whole walk), then `_validate_discovery` raises `SnapshotError` (exit 1) if it still found zero matching articles, found fewer than the area's `expect_min_articles` preset (set for the ten captured areas above, at ~50% of their 262 twin's count — a floor that tolerates real content growth/shrinkage between releases, not a race), or hit `discover_timeout_ms` without ever seeing two consecutive equal reads — that last case raises even when the last read already clears the floor, because a still-growing count isn't reliably the full tree (PR #408 review round 3). **A passing `discover` on one of those ten areas is a real signal now; on the remaining `collections` preset it exits 0 with no floor to check against, so still read the logged count and byte-diff spot-check before trusting a capture** (the Dev Guide presets have no `root_article_id`/prefix at all, so this discover-floor discussion doesn't apply to them — they're already captured via the `doc_version` mechanism):
>
> ```bash
> python -m scripts.doc_snapshot help --release 264 --area pricing --mode discover   # run it plainly; keep the exit status
> # then read this line out of the output:
> #   "Discovered 0 unique articles (0 total before prefix filter)"   -> bad root, or the walker failed
> #   "Discovered 0 unique articles (N total before prefix filter)"   -> root walks, prefix is wrong for this area
> #   (both "0 kept" cases above raise unconditionally, regardless of expect_min_articles —
> #    only the "nonzero but below the floor" case needs expect_min_articles set)
> ```
>
> **Do not pipe it through `grep`.** The pipeline would report `grep`'s status instead of the snapshot's, so a failure *after* the count is logged — the manifest save, the index build — would read as success, and the traceback would be filtered away. If you want a filtered copy, keep both with `set -o pipefail` and `tee`.
>
> **Do not substitute the manifest's `stats.discovered` for that line** — it is cumulative, not per-run. `_merge_discovered` only adds, so an empty discovery leaves the prior articles untouched (with `subtree_only`, `_prune_moved_out` first removes this area's records whose complete parent chain places them in another sidebar branch (reaching a root ancestor or another aria-level 1 tree root), and after the manifest is saved every moved-out ID with no remaining record has its article file deleted (so a file orphaned by an interrupted run is removed by the next validated walk), so a subtree snapshot's counts can shrink after discovery; a record absent from the walk or with incomplete ancestry is kept, and an empty or unstable walk fails `_validate_discovery` before any merge); `_compute_stats` then counts **every area at once** (262 reports 935, the sum of 11 areas), and the per-area figure under `areas[]` is likewise the running total for that area. A failed re-discovery therefore leaves both numbers positive and unchanged. On a first 264 run neither exists — `docs/salesforce/264/help/` is not there yet, so reading the manifest raises `FileNotFoundError`. The per-area `last_run_discovered` field (`{kept, before_prefix_filter}`) is the one non-cumulative signal in the manifest — it reflects only the most recent discovery run for that area.
>
> **Never run two `help` snapshots concurrently against the same manifest** — every area shares one `docs/salesforce/{release}/help/manifest.json`, and each run loads it once into memory and periodically overwrites the file from that in-memory copy. Two processes running at once will lose whichever one saves last; a discover run's freshly-merged articles can vanish if a concurrent capture run's next periodic save clobbers the file with its own stale copy. Run them one at a time; `help --area all` and `run` already do, sequentially.
>
> And even a non-zero discover says nothing about *whether the release's content was written* on an area without `expect_min_articles` set: on a pre-GA release the articles behind a valid root can still hold the previous release's text, so a full capture can spend 10–15 minutes writing 262 content under a 264 path. Per-area readiness — which areas are worth capturing yet, and what to watch before re-checking — is assessed in the private artifacts repo (`.agents/artifacts/todos/`, todo 183, following on from closed todo 145), because it derives from internal tracking that does not belong in this repo.

## Why the snapshot exists

The Salesforce Help portal is an LWC SPA. `WebFetch`, `curl`, and naive scrapers all return an unrendered shell. The PDF Help compendium that Salesforce publishes per release is huge (124 MB for Spring '26 Billing alone), terrible for grep, opaque to file diffs, and impractical to commit. The snapshot replaces it with per-article markdown — one file per Help article, with YAML frontmatter carrying article ID, title, release, source URL, area, and fetched date. The markdown is small (~450 KB for ~170 Billing articles in 262), grep-friendly, diffable across releases, and structured well enough for AI agents to use as surgical grounding.

The snapshot is generated by the standalone `scripts/doc_snapshot/` CLI (`help_portal.py`) using Playwright + a recursive shadow-DOM walker. It needs no Salesforce org and no CumulusCI. The same pattern works for any Help area that has a root article ID and a consistent ID prefix; each one is a preset in `scripts/doc_snapshot/presets.yaml`. Install, usage and the preset schema are in [`scripts/doc_snapshot/README.md`](../../../scripts/doc_snapshot/README.md).

## Quick Rules

1. **Ground product claims before writing them.** If you're about to assert that a Revenue Cloud feature does X, grep the snapshot for X first. If no matching article appears, look for the area root (`ind.{area}.htm`) and walk its child article list.
2. **Article IDs are the stable identifier.** Filenames map 1:1 to Salesforce Help portal article IDs. The URL `https://help.salesforce.com/s/articleView?id=ind.billing.htm&type=5` corresponds to `docs/salesforce/{release}/help/articles/ind.billing.htm.md`.
3. **Use frontmatter, not body text, for filtering.** `release`, `area`, `parent_article`, and `fetched_at` are machine-readable. Body text is the substantive content.
4. **Re-snapshot when a release ships.** Run `python -m scripts.doc_snapshot help --release {release} --area {area}`. It is idempotent; re-running on an existing snapshot only captures pending articles unless you pass `--mode refresh`.
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
| `docs/salesforce/264/release-notes/` | Revenue Management section of the Winter '27 (264) release notes — 127 articles (`release-notes.rn_*`), same layout as `help/`. Captured by the 264 `release_notes` preset (`help --release 264 --area release_notes`). Use for "what changed in 264" and Where/Who/How enablement lines; release notes carry no Beta/Pilot labels for 264, so tiers still come from Help article titles. |
| `scripts/doc_snapshot/help_portal.py` | The Help capture (Playwright + shadow-DOM walker). `subtree_only: true` keeps only `root_article_id` and its sidebar descendants — needed for release notes, where every product shares the `release-notes.rn_` prefix. A validated discovery also prunes that area's articles whose complete parent chain places them in another sidebar branch, so `refresh` never recaptures them; articles absent from a (possibly partial) walk or with incomplete ancestry are kept |
| `scripts/doc_snapshot/presets.yaml` | Every preset, per release: `260` (billing), `262` (11 areas + 2 dev guides), `264` (11 areas + `release_notes` + 2 dev guides). `python -m scripts.doc_snapshot list` prints them. Ten 264 areas (`configurator`, `transaction_mgmt`, `billing`, `pcm`, `dro`, `pricing`, `rating`, `usage`, `agents`, `approvals`) are captured and root-verified; the remaining `collections` preset inherited its root article ID from 262 and is **checked but not ready** — discovery matches the 262 twin exactly, but the bodies came back byte-identical with no net-new content, the portal's own signal it's still serving 262 text — re-run `--mode discover` + a byte-diff spot-check periodically. (The `dev_guide` presets `rlm`/`industries` have no `root_article_id` — already captured, see the branch note above.) |

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

The **Revenue Cloud Developer Guide** lives in a different documentation system than Help — the "atlas" viewer at `developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta`. It is captured separately by **`scripts/doc_snapshot/dev_guide.py`** (the `dev-guide` subcommand) into `docs/salesforce/{release}/dev-guide/`, mirroring the help layout (`articles/{page_id}.md` + `manifest.json` + `index.md`).

| Path | Purpose |
|---|---|
| `docs/salesforce/{release}/dev-guide/articles/{page_id}.md` | One captured guide page, markdown body + YAML frontmatter |
| `docs/salesforce/{release}/dev-guide/manifest.json` | Machine index: page status, section, parent, doc_version, file path |
| `docs/salesforce/{release}/dev-guide/index.md` | Human index: stats + pages grouped by TOC section |
| `scripts/doc_snapshot/dev_guide.py` | The Dev Guide capture (Playwright + atlas JSON content API → markdown) |

**Why a separate snapshotter.** The atlas viewer exposes a clean JSON content API (`get_document` for the TOC, `get_document_content/<deliverable>/<page_id>/en-us/<doc_version>` per page), but it sits behind Akamai bot protection — plain `requests`/`curl` get HTTP 403. It drives the API from inside a Playwright browser context (so requests carry the browser's cookies/TLS) and converts the returned HTML to markdown (`markdownify` when installed, else a built-in converter). Intra-guide cross-references are rewritten to sibling `./<page_id>.md` files so the corpus is self-navigable.

**Frontmatter** carries `page_id`, `title`, `source_url`, `release`, `release_name`, `deliverable`, `section` (TOC top-level ancestor), `parent_page`, and `fetched_at`.

**Capture / refresh.** Same modes as the help snapshot (`discover` / `capture` / `all` / `refresh`). Run the whole guide or one section:

```bash
python -m scripts.doc_snapshot dev-guide --release 264 --guide rlm                                           # whole guide
python -m scripts.doc_snapshot dev-guide --release 264 --guide rlm --section "Constraint Modeling Language"   # one TOC section
python -m scripts.doc_snapshot dev-guide --release 264 --guide rlm --mode refresh                             # re-capture all (after a release update)
```

Requires Playwright (same install as the help snapshot); `markdownify` is optional, for best table/list fidelity. Both are in `scripts/doc_snapshot/requirements.txt`.

### Industries Common Resources dev guide (`dev-guide-industries`)

RC builds on shared **Industries common platform services** that the RLM dev guide doesn't document — Business Rules Engine (expression sets, decision tables/matrices), Context Service, OmniStudio, Discovery Framework (guided selling), Data Processing Engine/Batch, Decision Explainer, Collections and Recovery, Action Launcher, and Timeline. These live in a **second atlas deliverable**, `industries_reference`, captured separately into `docs/salesforce/{release}/dev-guide-industries/` (same `articles/` + `manifest.json` + `index.md` layout) by the same snapshotter with a distinct `output_dir` (the `industries` preset).

The full Industries Common Resources guide is ~1435 pages across 37 sections — most for *other* Industries clouds (Digital Lending, Document/Form Readers, Process Compliance, etc.). The snapshot is **scoped to the ~571 RC-relevant pages** (the nine sections' TOC subtrees) via the preset's `sections` list; `follow_links` stays off so an out-of-scope cross-reference can't drag in unrelated sections:

```bash
python -m scripts.doc_snapshot dev-guide --release 264 --guide industries                 # the 9 RC-relevant sections
python -m scripts.doc_snapshot dev-guide --release 264 --guide industries --mode refresh
# widen/narrow by editing the preset's `sections` list (TOC titles or page_ids) in presets.yaml,
# or pass --sections "A,B" / --section A for a one-off run
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

When a new release ships (e.g., Salesforce announces 266 GA):

1. **Add the release to `scripts/doc_snapshot/presets.yaml`** by copying an existing one:

   ```bash
   python -m scripts.doc_snapshot bootstrap --from 264 --to 266 --release-name "Spring '27" --dry-run   # preview
   python -m scripts.doc_snapshot bootstrap --from 264 --to 266 --release-name "Spring '27"
   ```

   Bootstrap appends a `"266"` block that keeps every root article ID and prefix, rewrites each `output_dir` to the new release, and drops `expect_min_articles` and `doc_version`. Floors are re-derived from the new release's counts, and the dev guides need their new `doc_version` set once it publishes (see the branch note above). A one-off area needs no preset at all: pass `--root-article-id`, `--prefix` and `--release-name` to `help`.

2. **Run discovery first** to see what's new:

   ```bash
   python -m scripts.doc_snapshot help --release 266 --area billing --mode discover
   python -m scripts.doc_snapshot help --release 266 --area all --mode discover    # every help preset, with a summary table
   ```

   (`bootstrap --discover` runs the second command for you.) The discovery phase walks the sidebar and writes `manifest.json` with all discovered article IDs as `pending`. Compare against the previous release's manifest to see additions, removals, renames.

   **Read the `Discovered N unique articles` line before moving on.** A zero-article discovery now raises (pack 146's `_validate_discovery`) — the exit code alone tells you *that* something's wrong, but not *what*: a wrong root, a reorganized prefix, and a walker crash all raise the same way, and only that log line's pre-filter total distinguishes them ("0 total" is a bad root/crashed walker; "N total, 0 kept" is a prefix that no longer matches). A **nonzero but thin** result is a quieter case — it exits 0 unless the preset has `expect_min_articles` set, so read the count either way. Read it out of the command's own output rather than piping to `grep`, which would substitute `grep`'s exit status and hide anything that fails after the count is logged. The manifest's `stats.discovered` is cumulative and cannot substitute for it either: an empty discovery adds nothing and removes nothing, so both the top-level count (every area summed) and the per-area count under `areas[]` survive a failed re-walk unchanged. Once the counts look right, set each preset's `expect_min_articles` (264 used ~50% of the 262 twin's count).

3. **Run full capture**:

   ```bash
   python -m scripts.doc_snapshot help --release 266 --area billing
   ```

   Captures every pending article in parallel (default concurrency 4). ~10-15 minutes for ~170 articles. `python -m scripts.doc_snapshot run --release 266` snapshots every help and dev-guide preset of the release in turn; a failed preset does not stop the rest, and the summary lists it.

4. **Validate**:

   ```bash
   # File count matches manifest
   ls docs/salesforce/266/help/articles/ | wc -l
   python3 -c "import json; m=json.load(open('docs/salesforce/266/help/manifest.json')); print(sum(1 for a in m['articles'] if a.get('status')=='captured'))"

   # No errors
   python3 -c "import json; m=json.load(open('docs/salesforce/266/help/manifest.json')); print([a for a in m['articles'] if a.get('status')=='error'])"

   # No breadcrumb noise leaked through (should print 0)
   grep -l "^You are here:" docs/salesforce/266/help/articles/*.md | wc -l

   # Glued-link text-artifact spot-check (non-gating; see Known limitations)
   python -m scripts.doc_snapshot check --release 266
   ```

5. **Commit** the corpus and the `presets.yaml` change together. A single-area snapshot is typically 100–500 KB; the full multi-area snapshot for one release lands around 4–5 MB (the 262 snapshot is **~4.3 MB across 935 articles** — see the *Per-area snapshots* table below). `.gitattributes` already marks `docs/salesforce/*/help/**` (and the release-notes and dev-guide trees) `linguist-generated=true`, so GitHub auto-collapses the diff on refresh PRs.

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

To get full agent coverage you need the `agents` preset (the dedicated area) **plus** every functional area's snapshot. Without the functional-area snapshots, you'll have agent topic descriptions but no how-to / use-case grounding.

**IMPORTANT — don't conflate adjacent domains.** Usage Management (`ind.um_*`) and Rate Management (`ind.rm_*`) are two distinct data-model domains and two distinct Help-portal areas. Pricing (`ind.pricing_*`) and Rate Management (`ind.rm_*`) are similarly distinct. Configurator (`ind.product_configurator_*`) is its own domain — easy to skip past because it has only 4 objects, but the Help portal area is real and covers configuration rules / flows that affect Quote/Order configuration. The `article_id_prefix` filter is a single startswith match, so capturing each requires **its own preset**. Module 3 of the L2 Billing Trailhead mix straddles Usage + Rating, which is why `presets.yaml` defines `usage` AND `rating` separately.

To add a new area: walk the sidebar from the Revenue Lifecycle Management parent (`ind.revenue_lifecycle_management.htm`) using the `SIDEBAR_WALKER_JS` pattern from `scripts/doc_snapshot/help_portal.py`. Note the area's root article ID, identify the prefix that filters its child articles, and try it ad hoc with `help --release {release} --area {name} --root-article-id {root} --prefix {prefix} --mode discover`. Once it walks, add it as a key under the release's `help:` block in `presets.yaml` (`area` defaults to the key). Every area uses the same snapshotter; only options differ. Always run `--mode discover` first and read the `Discovered N unique articles` line it logs. A wrong root or crashed walker now raises (pack 146's `_validate_discovery` rejects a zero-kept result unconditionally), but a thin, nonzero result — e.g. a reorganized prefix that still matches a handful of stale links — only raises if the new preset sets `expect_min_articles`; without that floor it exits 0, so read the count either way. Do not read `stats.discovered` from the manifest instead: it sums every area and retains prior runs, so it stays positive when a new area discovers nothing.

## Known limitations

- **Data Model articles are thin.** Articles named `ind.*_data_model_*.htm` are usually short (under 500 bytes captured) because the actual ERD is an image. For object schemas, fields, and relationships, use the `revenue-cloud-data-model` skill instead.
- **Article ID renames are silent.** When Salesforce renames an article between releases, the old ID 404s and the new ID may not be obvious. Two examples from 260→262: `ind.billing_milestone.htm` → `ind.billing_milestone_plans.htm`; `ind.billing_payment_terms.htm` is "Create Payment Terms" (its parent "Define Billing Policies and Billability Rules" is at `ind.billing_policies_and_treatments.htm`). When you encounter a 404, search the new release's manifest by title.
- **SObject field names vs. Help labels** diverge. The schema field `ShouldCaptureTaxesAtHeader` is labeled "Capture Taxes at Header" in the Help portal. The field `TaxEngineAddress` is referenced indirectly in articles ("the address used for tax calculation"). When verifying a claim that uses a field name, search by both the field name AND the human label.
- **Image-only content is invisible.** The capture is text-only (innerText). Diagrams, screenshots, and ERDs are not captured. If a Help article relies on an image for the substantive content, the captured markdown is thin.
- **Some articles span multiple Help "tabs"** (notes, considerations, examples). The capture currently only walks the main article tab; secondary tabs may be missed. Re-fetch manually via Chrome MCP if a specific article seems incomplete.
- **Rare glued-link / duplicated-label text artifacts are upstream Salesforce content typos, not extraction bugs.** Confirmed via live DOM inspection (todo 184, artifacts repo): Salesforce's own source HTML sometimes omits the space before a link (`See<a>Create a Constant Resource</a>` renders as "SeeCreate a Constant Resource") or has a callout badge whose label happens to duplicate the paragraph's own leading word ("NOTE Note: ..."). `innerText`-based capture is verbatim by design, so it faithfully reproduces these. Recapturing does not fix them — verify the hit against the live DOM first, then hand-edit the affected article, and only in the active release's corpus (e.g. `docs/salesforce/264/`); frozen snapshots (e.g. `docs/salesforce/262/`) are left as-is by design. `python -m scripts.doc_snapshot check [--release {release}]` is a non-gating spot-check for the glued-link class — it flags a pattern, not a confirmed defect — run it after any capture/refresh. Only 3 instances have ever been found across the whole corpus.

## Cross-reference with related skills

- **[`release-enablement`](../release-enablement/SKILL.md)** — for authoring Hands-On exercises per release. The snapshot is a primary input to that workflow.
- **[`revenue-cloud-data-model`](../revenue-cloud-data-model/SKILL.md)** — for object/field reference, ERDs, and schema details. Use this when the Help docs are thin (Data Model articles, image-only content).
- **[`doc-consistency`](../doc-consistency/SKILL.md)** — pre-merge consistency checks. When the snapshot reveals product renames or terminology shifts, propagate them through internal docs that reference the Help articles.
- **[`sfdmu-data-plans`](../sfdmu-data-plans/SKILL.md)** — for QuantumBit sample data referenced in walkthroughs.

## Snapshot Authoring Notes

The snapshotter is intentionally idempotent and refresh-friendly. Modes:

| Mode | Behavior |
|---|---|
| `discover` | Walk sidebar, update manifest with all IDs as `pending`. No body capture. Fast smoke test. |
| `capture` | Read existing manifest, capture pending articles only. Skips already-captured. |
| `all` (default) | Discover then capture. Idempotent — re-running won't re-fetch already-captured articles. |
| `refresh` | Re-capture every article, overwriting existing files. Use after a release update or a JS extractor change. |

Setup (once per environment):

```bash
python3 -m venv .venv-docs && . .venv-docs/bin/activate     # any Python 3.9+ env works; CumulusCI is not needed
pip install -r scripts/doc_snapshot/requirements.txt
python -m playwright install chromium
```

Every option is a kebab-case flag (`python -m scripts.doc_snapshot help --help`), and a flag overrides the preset value. See [`scripts/doc_snapshot/README.md`](../../../scripts/doc_snapshot/README.md) for the preset schema and the full option list.

## Change log

- **2026-10-02** — The 30 `snapshot_*` CCI tasks were replaced by the standalone `scripts/doc_snapshot` CLI (`help`, `dev-guide`, `run`, `check`, `bootstrap`, `list`), with presets in `scripts/doc_snapshot/presets.yaml`. `tasks/rlm_snapshot_help.py` → `scripts/doc_snapshot/help_portal.py`, `tasks/rlm_snapshot_dev_guide.py` → `scripts/doc_snapshot/dev_guide.py`, `scripts/ai/check_help_corpus_text_artifacts.py` → `scripts/doc_snapshot/check.py`. Captured output is unchanged apart from the `capture_method` provenance string.

- **2026-09-07** — Added the glued-link/duplicated-label text-artifact known limitation and `scripts/ai/check_help_corpus_text_artifacts.py` spot-check (todo 184). Carved a narrow exception into DO NOT #2 (hand-edit prohibition) for this artifact class, since a refresh cannot fix an upstream typo (PR #412 review).
- **2026-05-11** — Skill created. Initial 262 Billing snapshot covers 171 articles (~440 KB).
