# doc_snapshot — snapshot public Salesforce docs into markdown

The **snapshot tool** saves public Salesforce documentation as markdown files
in this repo, so people and AI agents can grep, diff, and cite it instead of
working from PDFs or a browser. It covers two sources:

- **Help** — articles on help.salesforce.com, release notes included.
- **Developer guides** — the "atlas" guides on developer.salesforce.com, and
  the newer server-rendered guides (`source: site`, see **Site guides**).

It needs no Salesforce org and no CumulusCI. For how to *use* the saved docs
when grounding product claims, see
[`revenue-cloud-docs/SKILL.md`](../../.cursor/skills/revenue-cloud-docs/SKILL.md).

## Terms

| Term | Meaning |
|---|---|
| **release** | A Salesforce release number such as `264`. It names the output folder and goes into every article's frontmatter. |
| **preset** | A named set of options for one Help area or one developer guide, stored in [`presets.yaml`](presets.yaml) under its release. |
| **area** | A section of the Help portal (Billing, Pricing, …): one root article plus all the articles listed under it in the sidebar. |
| **discover** | Walk the sidebar (Help) or table of contents (dev guide) and record which articles exist. Fast, and fetches no article text. |
| **capture** | Fetch the text of discovered articles and write them as markdown. |
| **corpus** | The saved output for one source and release, such as `docs/salesforce/264/help/`. |
| **manifest** | `manifest.json` in a corpus. It lists every discovered article and its status: `pending`, `captured`, or `error`. |
| **floor** | A preset's `expect_min_articles`. Discovery fails if it finds fewer articles, which catches a walk that silently came back short. |

## What it produces

Each corpus lives under `docs/salesforce/{release}/`:

| Folder | Source |
|---|---|
| `help/` | Help portal areas. Every area of a release shares this one folder and its manifest. |
| `release-notes/` | The Revenue section of the release notes, for releases that have a `release_notes` preset. |
| `dev-guide/` | The Revenue Management Developer Guide. |
| `dev-guide-industries/` | The Revenue Cloud sections of the Industries Common Resources guide. |

Every corpus holds the same three things:

- `articles/<id>.md`: one file per article, with YAML frontmatter (id, title,
  source URL, release, area or section, fetch date) followed by the article
  body and a source-attribution note that links the source URL. Files
  captured before the note was added lack it until they are recaptured with
  `--mode refresh` (the other modes skip captured articles).
- `manifest.json`: the machine-readable index described above.
- `index.md`: a human-readable index generated from the manifest.

## Install

Use any Python 3.9+ environment. The repo's CumulusCI environment isn't needed.

```bash
python3 -m venv .venv-docs && . .venv-docs/bin/activate
pip install -r scripts/doc_snapshot/requirements.txt
python -m playwright install chromium
```

- `help` and atlas `dev-guide` presets need `playwright`. Both sites render in
  the browser and block plain HTTP clients, so the tool drives a real Chromium.
  `source: site` dev-guide presets use plain HTTP and need no browser.
- `markdownify` is optional. Without it, `dev-guide` falls back to a built-in
  converter whose tables and lists are less clean.
- `PyYAML` reads `presets.yaml`. `check` needs neither PyYAML nor Playwright.

## Subcommands

Run every subcommand from the repo root. `<subcommand> --help` lists all of its
flags.

| Subcommand | What it does |
|---|---|
| `list [--release R]` | Show the presets. |
| `help --release R --area A` | Snapshot one or more Help areas. |
| `dev-guide --release R --guide G` | Snapshot one or more developer guides. |
| `run --release R [--only k1,k2]` | Snapshot every preset of a release, Help and dev guide alike. |
| `check [--release R]` | Look for glued-link text artifacts in the captured Help corpus, and for `X, formerly X` rename artifacts in every captured corpus (upstream text that a recapture will not change). |
| `bootstrap --from R --to NEW --release-name N` | Add a release to `presets.yaml` by copying an existing one. |

`--area` and `--guide` take a preset key, a comma-separated list of keys, or
`all`. `python scripts/doc_snapshot/cli.py …` also works. The global
`--presets PATH` option, which goes before the subcommand, reads a different
presets file instead of the default one (useful for testing).

## Common workflows

**See what's configured:**

```bash
python -m scripts.doc_snapshot list --release 264
```

**Check that an area still discovers correctly (fast, fetches no text):**

```bash
python -m scripts.doc_snapshot help --release 264 --area pricing --mode discover
```

**Capture new or pending articles for an area:**

```bash
python -m scripts.doc_snapshot help --release 264 --area pricing
```

**Re-capture everything after Salesforce updates the docs:**

```bash
python -m scripts.doc_snapshot help --release 264 --area all --mode refresh
```

**Snapshot one section of a developer guide:**

```bash
python -m scripts.doc_snapshot dev-guide --release 264 --guide rlm --section "Constraint Modeling Language"
```

**Snapshot a whole release, or a few of its presets:**

```bash
python -m scripts.doc_snapshot run --release 264
python -m scripts.doc_snapshot run --release 264 --only pricing,rlm
```

**Spot-check the Help corpus after a capture:**

```bash
python -m scripts.doc_snapshot check --release 264
```

## Modes

`--mode` selects how much work a run does.

| Mode | Behavior |
|---|---|
| `discover` | Record every article as `pending`; fetch no text. |
| `capture` | Fetch the manifest's `pending` articles only. |
| `all` (default) | `discover`, then `capture`. Re-running never re-fetches captured articles. |
| `refresh` | Re-fetch every article and overwrite the files, except captures the guard refuses (see **Capture guard**). |

A capture only touches the selected area. Other areas in the same manifest are
left as they are.

## Capture guard

A refresh used to write whatever the portal served. Two bad shapes got through
the fetch-level checks, and the 2026-11-23 264 refresh wrote both into the
corpus. `scripts/doc_snapshot/guard.py` now refuses them before anything is
written (stdlib, offline-testable):

| Shape | What the portal served | Signals (any one refuses) |
|---|---|---|
| **Not-found page** | A rendered page with an H1 and a body, no HTTP error: "We couldn't find the page you're looking for." (4 captures: two Help articles, two release notes) | The title, or the body's first line, leads with a known not-found headline (curly quotes and case folded; the older "We looked high and low" shell too); or a body of 1,500 characters or fewer that carries both boilerplate markers ("Searching for something? Agentforce can help", "May we also suggest"). |
| **Truncated stub** | A developer-guide page cut to its heading and first lines (the atlas 264.0 source itself; the converter is faithful) | The new body keeps **under 50% of the prior capture's characters and under 60% of its words**, and the prior body was **at least 500 characters**. |

Evidence behind the thresholds (the 264 refresh, compared 2026-11-23 over the
3,917 pages that had a prior capture): the four not-found pages and the six
stubs are all caught. The stubs kept 3% to 21% of the prior characters
(Decision Table Definitions POST: 410 body characters against 16,162). On the
same data, a characters-only 50% rule flagged 371 pages, almost all short
reference pages that lost a table or a note upstream; requiring the word ratio
as well brought that to 13: those 10 plus 3 pages whose text really shrank (a
page that became an index of its children, and two short Help articles). Those
3 need `--accept-shrinkage` if a refresh should take them. The 500-character
floor exists because a page of a few lines (479 characters, now "Reserved for
internal use.") swings its ratio on any edit. Pages whose text changed upstream
by a few cells or notes (the credit memo and calculation-procedure pages checked
at source in 413) stay well above both limits and are written.

A refused capture:

- **keeps the prior file** and its `file` and `body_length` in the manifest,
  and is recorded as `status: error` with `error: "refused: <reason>"`, so it
  shows under **Errored** in `index.md`;
- is logged as `[refused] <id>: <reason>` as it happens, and listed again with
  the way out at the end of the capture;
- counts as a failed capture: the run exits 1 after saving its progress. A failed
  run returns no stats, so the count rides on the error: the multi-preset
  summary prints it on that preset's FAILED row ("... [N refused by the capture
  guard, M no longer in the contents] ...").

A refused page is listed under **Errored** in `index.md`, while its kept prior
file stays on disk and `check` still reads it. The same holds for any failed
fetch (a navigation timeout, a missing H1, an empty body): Help and dev-guide
alike keep the prior file and its `file` and `body_length`, and change only
`status` and `error`.

**Override.** `--accept-shrinkage ID[,ID...]` (on `help`, `dev-guide` and `run`)
writes the named pages even when the shrinkage rule would refuse them, and logs
one `[accepted] <id>: <reason>` warning per page it lets through. It names pages,
never the whole run, so one real cut cannot switch the guard off for the rest.
Use it only after reading each page and finding the loss is real upstream
(verify against the live content API or page, as 413 did). It is a run flag, not
a preset option. An id that no capture used in the run (a typo, a moved page, or
a page that did not shrink) is named in a warning at the end; the exit code is
unchanged. It never writes a not-found page: the id was retired or moved, so
search the manifest by title for its new id.

The new body is measured without its leading H1 and preview banner, the same
way the prior file's body is, so a long title cannot hide a stub.

A dev-guide page that is refused and has no prior file is left out of the set of
known pages, so links to it keep their online URL instead of pointing at a file
that does not exist. A prior file that is not valid UTF-8 is treated as absent
(the capture replaces it).

**Orphans.** A page that errors and is no longer listed by the run's own
discovery (a whole-guide TOC walk for `dev-guide`, the sidebar walk for `help`)
is reported at the end as moved or retired upstream, with its earlier capture
kept (a failed fetch never deletes it). The 264.0 guide dropped 18 asset and order object pages this way. The
report is a lead: a page reached only through cross-reference following is also
not in the TOC. Retire such a page or mark it moved by hand; the tool never
deletes it.

## Site guides (`source: site`)

Salesforce is moving developer guides off atlas onto server-rendered sites
(`/docs/revenue/revenue-management/guide/<slug>.html`,
`/docs/industries/industries-common-dev/guide/<slug>.html`). Atlas URLs 301 to
them, and the atlas content API serves the new guides empty or truncated, so the
atlas fetcher cannot capture them. A dev-guide preset with `source: site` reads
the site over plain HTTP (no browser) through `site_guide.py`:

- **TOC** from the HTML-escaped JSON in the `sidebar-content` attribute of
  `<doc-content-layout>`, the same on every page. `sections` filter it as for
  atlas, by label or slug; an atlas page id such as `business_rules_engine` works.
- **Body** is the markup inside `<doc-content-layout>`, converted by the same
  HTML to markdown converter as atlas pages. `<doc-heading>` becomes a heading,
  `<dx-code-block>` a code block, `<doc-content-callout>` a labelled paragraph; any
  other `doc-*`/`dx-*` element is logged as unconverted.
- **Files** are named by slug (`articles/rlm-get-started.md`); `page_id` is the
  slug and `source_url` the new page URL. Intra-guide links point at sibling files
  when the target was captured, else keep the online URL.
- **API version check.** The site has no version selector: it serves one release
  (API 68.0 is release 264) and older ones exist only as PDFs on the guide's
  `*-pdf-archive.html` page. The capture counts the `/services/data/vNN.0`
  versions in the fetched pages and **refuses before writing anything** when the
  dominant one is not the preset's `api_version`. If the captured pages show no
  version (a metadata-only section), it fetches `probe_page` for evidence, and
  refuses when there is still none. The observed version and its votes are in the
  manifest.
  A corpus is never relabelled: a run for a different `api_version`, guide (the
  `/docs/<area>/<guide>/guide/` of `site_url`), `release_version` or `deliverable` over
  captured pages is refused, before anything is saved, unless it is a whole-guide
  `--mode refresh` (or uses another `output_dir`). That refresh resets the old page
  records (a different guide's are dropped and their files listed under `superseded_files`).
- **Sections.** A `sections` filter selects the TOC subtree of the named page id
  or label, also on a later `refresh`, whatever top-level section the stored
  records carry. `--mode capture` resolves it from the TOC paths (`ancestors`)
  recorded by discover, and refuses a section it cannot find. In every mode a label that
  names two TOC nodes is refused (name one by its page id). A manifest from before paths
  were recorded needs one discover. A page listed twice in the TOC keeps its
  first path in `ancestors` and its other branches in `alt_ancestors`, so a section
  filter on any branch selects it in every mode; its subtree is the union of its listings. A filter is a label or a
  bare page id, not a URL or path.
- **Legacy ids.** The manifest's `legacy_id_map` maps old atlas page ids to
  slugs (a TOC match on the usual rename, else the atlas URL's redirect); ids
  neither finds are the keys of `unmapped_legacy_ids`. They are never guessed.
  The old ids come from an atlas manifest in the same `output_dir`; switching that
  directory to the site needs a whole-guide `--mode refresh` (no `--section`), and the
  old articles are not deleted (remove them in the same change). The shrinkage guard
  compares a replacement with the page's atlas article (the longest, if several ids map
  to it) when no site article exists. An atlas article is listed under
  `superseded_files` only once its page has an article; a refused or failed replacement,
  and an id that maps to nothing (see `unmapped_legacy_ids`), leave it as the only copy
  and it is not offered for removal. A rerun retries the ids that stayed unmapped. (A
  switch to a different guide abandons the old corpus whole and lists all its files.)
- Rate limit: `concurrency` pages per batch (default 4), `batch_delay_ms` between
  batches (default 500), three attempts with backoff on a failed connection, 429 or
  5xx. The capture guard (not-found and stub) applies as for atlas.

| Option | Default | Notes |
|---|---|---|
| `source` | `atlas` | `site` selects this fetcher. |
| `site_url` | none | Required. Any page of the guide. |
| `api_version` | none | Required at run time, for example `68.0`. Dropped by `bootstrap`. |
| `probe_page` | none | Slug of a page that shows an API version. |
| `deliverable` | the guide's path segment | The legacy atlas id; frontmatter and the redirect lookup use it. |
| `sections`, `output_dir`, `mode`, `concurrency`, `batch_delay_ms`, `max_pages` | as for atlas | `doc_version` is rejected; `follow_links` does not apply. |

The 264 presets `rlm_site` and `industries_site` write to
`docs/salesforce/264/dev-guide-site` and `dev-guide-industries-site`; the atlas
presets stay the defaults until a re-capture switches them. A sample run:

```bash
python -m scripts.doc_snapshot dev-guide --release 264 --guide rlm_site \
    --output-dir /tmp/rlm-sample --section connect-resources-get-catalogs
```

## Reading the result

A Help discovery logs a line like this:

```text
Discovered 155 unique articles (612 total before prefix filter)
```

The first number is the articles kept for this area. The second is every link
the walk saw before filtering. Discovery fails (exit 1) when:

- **it kept nothing.** If the second number is also 0, the walk failed. If it is
  nonzero, the prefix is wrong.
- **it kept only the root article.** The root id is probably wrong: a
  nonexistent id still renders a page, and the root matches its own prefix.
  The walk keeps polling until the timeout first, since a sidebar that is still
  loading can show just the root for a while.
- **it kept fewer articles than the preset's floor.**
- **the sidebar never stopped growing** before the timeout.

An area **without a floor** that comes back short still exits 0. Before trusting
it, read the count yourself.

Two things to avoid:

- **Don't pipe the output through `grep`.** The pipeline then reports `grep`'s
  exit status, which hides any failure that happens after the count is logged.
- **Don't read counts from the manifest instead.** Its `stats` add up every area
  and keep earlier runs, so they stay unchanged after a failed walk. For an
  area's most recent walk, use its `last_run_discovered` entry under `areas[]`.

When several presets run (`--area all`, `run`), the tool logs a failure and
keeps going. It then prints a summary table and exits 1 if anything failed.

**Exit codes:**

- `0`: success.
- `1`: a snapshot failed, for example because of a short or unstable discovery,
  a browser error or timeout, a filesystem error such as an unwritable output folder, or a missing dependency. A run where any article
  it tried to capture failed also exits 1, after saving its progress; the
  failed ids are named in the error and recorded in the manifest, and a later
  run retries them. A capture the guard refuses (not-found page, truncated stub)
  counts as failed.
- `2`: a usage error, such as an unknown preset or preset option, an empty selector, flag value, or `sections` list, a list or mapping where an option takes one value (only `sections` may be a list), an integer option given `true` or `2.5`, a boolean flag that is not `true`/`false` (or `yes`/`no`, `on`/`off`, `1`/`0`), or conflicting flags. Every selected preset is checked before any runs, including a pinned `doc_version` that conflicts with a captured corpus, so these errors never follow a partial run.

`check` always exits 0. Its hits are leads to verify, not failures.

**Run one `help` snapshot at a time per release.** Every area writes to the same
`help/manifest.json`, and when two processes run at once the last one to save
overwrites the other's results. `--area all` and `run` already go one area at a
time.

## Options

Each option can be set on a preset or passed as a flag of the same name in
kebab case (`expect_min_articles` becomes `--expect-min-articles`). Values are
applied in this order, and each step overrides the one before:

1. the release: its key gives `release_version`, and its `release_name` gives the
   name written into frontmatter
2. the preset
3. CLI flags (a flag you don't pass never overrides anything)

**Shared options:**

| Option | Default | Notes |
|---|---|---|
| `release_name` | from the release block | Written into frontmatter. Set on the release block or with `--release-name`, never on a preset. A release that isn't in `presets.yaml` has no default, so pass `--release-name`. |
| `output_dir` | per source; see below | Relative paths resolve from the repo root. |
| `mode` | `all` | See **Modes**. |
| `headless` | `true` | Set `false` to watch the browser. |
| `concurrency` | 4 (Help), 6 (dev guide) | Parallel fetches. |
| `wait_ms` | 3000 | Time to wait after each page load. |
| `accept_shrinkage` | none | Page ids, as a flag only (`--accept-shrinkage ID[,ID...]`), never a preset value. See **Capture guard**. |

**`help`:**

| Option | Default | Notes |
|---|---|---|
| `root_article_id` | — | Required. The area's root article. |
| `article_id_prefix` | — | Required (`--prefix` on the CLI). Keeps only discovered ids that start with it. |
| `area` | the preset key | The area name recorded in the manifest and in frontmatter. |
| `output_dir` | `docs/salesforce/{release}/help` | |
| `expect_min_articles` | none | The floor. |
| `discover_timeout_ms` | 20000 | How long to wait for the sidebar to stop growing. |
| `subtree_only` | `false` | Keep only the root's own sidebar descendants. Use this when other sections share the prefix, as every release-notes product does. |

**`dev-guide`:**

| Option | Default | Notes |
|---|---|---|
| `deliverable` | `revenue_lifecycle_management_dev_guide` | The guide's atlas id. |
| `doc_version` | none | For example `264.0`. **Set this for a new release:** without it, the site keeps serving the previous release's guide even after the new one is published. Changing it on a corpus that already has captured pages requires `--mode refresh`. |
| `sections` | whole guide | A list of TOC titles or page ids. On the CLI, pass `--section` once per section; it replaces a preset's `sections` for that run. |
| `follow_links` | on for a whole guide, off when sections are set | Whether cross-references pull in pages outside the TOC walk. |
| `output_dir` | `docs/salesforce/{release}/dev-guide` | |
| `batch_delay_ms` | 400 | Pause between fetch batches. |
| `max_pages` | 5000 | Safety cap. |

Flags that point at one specific target (`--root-article-id`, `--prefix`,
`--output-dir`, `--deliverable`, `--section`) are rejected when a
command selects more than one preset.

## Presets — `presets.yaml`

```yaml
releases:
  "264":                              # quoted: it's used as a folder name
    release_name: "Winter '27"
    help:
      pricing:                        # preset key; `area` defaults to it
        root_article_id: ind.pricing_salesforce_pricing.htm
        article_id_prefix: ind.pricing
        expect_min_articles: 55
    dev_guide:
      rlm:
        deliverable: revenue_lifecycle_management_dev_guide
        doc_version: "264.0"
```

Comments in the file explain prefix conventions and why some areas are split.
Keep them accurate when you change a preset.

### Add an area

1. **Find the root.** Open the Revenue Lifecycle Management landing page
   (`ind.revenue_lifecycle_management.htm`) on help.salesforce.com, then copy the
   `id=` value from the area's sidebar link.
2. **Try it without a preset** and read the discovery line (see **Reading the
   result**):

   ```bash
   python -m scripts.doc_snapshot help --release 264 --area myarea \
       --root-article-id ind.myarea.htm --prefix ind.myarea --mode discover
   ```

   For a release that isn't in `presets.yaml`, add `--release-name`.
3. **Add a key under the release's `help:` block**, with an
   `expect_min_articles` floor comfortably below the discovered count. About half
   is a good starting point, because it tolerates real growth or shrinkage
   between releases.

### Add a release

```bash
python -m scripts.doc_snapshot bootstrap --from 264 --to 266 --release-name "Spring '27" --dry-run
python -m scripts.doc_snapshot bootstrap --from 264 --to 266 --release-name "Spring '27"
python -m scripts.doc_snapshot help --release 266 --area all --mode discover
```

Bootstrap appends a new release block to `presets.yaml` as plain text, so
existing comments survive. It copies every preset's options and changes the
release number in each `output_dir` (an `output_dir` outside `docs/salesforce/<release>/` is rejected, since the new release would share its corpus). It leaves out the two release-specific
options:

- `expect_min_articles`: set new floors once you've seen the new release's counts.
- `doc_version`: set it on the dev-guide presets once the new guide is published.

A preset can't set `release_version` or `release_name` (they come only from
its release block), and an empty or null option (including an empty `sections` list) is rejected rather than read
as the default, so every copied preset takes the new release block's values.

The `help … --mode discover` run then gives you each new Help area's count.

A Help area can serve the previous release's text for a while after the new
release appears. Before capturing, compare a few articles with the previous
release's corpus. New article ids, or changed text in shared articles, are good
signs that the area has been updated.

## Tests

```bash
python tests/test_snapshot_help.py           # stdlib only
python tests/test_snapshot_dev_guide.py      # stdlib only
python tests/test_snapshot_site_guide.py     # stdlib only; fixtures in tests/fixtures/doc_snapshot_site/
python tests/test_snapshot_guard.py          # needs PyYAML; fixtures in tests/fixtures/doc_snapshot_guard/
python tests/test_doc_snapshot_presets.py    # needs PyYAML
```

All five run offline without a browser. `scripts/ai/pr_gate.py` runs them.
