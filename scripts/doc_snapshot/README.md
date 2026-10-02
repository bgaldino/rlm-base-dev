# doc_snapshot — snapshot public Salesforce docs into markdown

The **snapshot tool** saves public Salesforce documentation as markdown files
in this repo, so people and AI agents can grep, diff, and cite it instead of
working from PDFs or a browser. It covers two sources:

- **Help** — articles on help.salesforce.com, release notes included.
- **Developer guides** — the "atlas" guides on developer.salesforce.com.

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
| `dev-guide/` | The Revenue Cloud Developer Guide. |
| `dev-guide-industries/` | The Revenue Cloud sections of the Industries Common Resources guide. |

Every corpus holds the same three things:

- `articles/<id>.md`: one file per article, with YAML frontmatter (id, title,
  source URL, release, area or section, fetch date) followed by the article
  body.
- `manifest.json`: the machine-readable index described above.
- `index.md`: a human-readable index generated from the manifest.

## Install

Use any Python 3.9+ environment. The repo's CumulusCI environment isn't needed.

```bash
python3 -m venv .venv-docs && . .venv-docs/bin/activate
pip install -r scripts/doc_snapshot/requirements.txt
python -m playwright install chromium
```

- `help` and `dev-guide` need `playwright`. Both sites render in the browser and
  block plain HTTP clients, so the tool drives a real Chromium.
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
| `check [--release R]` | Look for glued-link text artifacts in the captured Help corpus. |
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
| `refresh` | Re-fetch every article and overwrite the files. |

A capture only touches the selected area. Other areas in the same manifest are
left as they are.

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
  a browser error or timeout, or a missing dependency. A run where any article
  it tried to capture failed also exits 1, after saving its progress; the
  failed ids are named in the error and recorded in the manifest, and a later
  run retries them.
- `2`: a usage error, such as an unknown preset, an empty selector, a boolean flag that is not `true`/`false` (or `yes`/`no`, `on`/`off`, `1`/`0`), or conflicting flags. Every selected preset is checked before any runs, so a usage error never follows a partial run.

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
| `release_name` | from the release block | Written into frontmatter. A release that isn't in `presets.yaml` has no default, so pass `--release-name`. |
| `output_dir` | per source; see below | Relative paths resolve from the repo root. |
| `mode` | `all` | See **Modes**. |
| `headless` | `true` | Set `false` to watch the browser. |
| `concurrency` | 4 (Help), 6 (dev guide) | Parallel fetches. |
| `wait_ms` | 3000 | Time to wait after each page load. |

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
| `include_release_param` | `true` | Adds `&release=` to article URLs. |

**`dev-guide`:**

| Option | Default | Notes |
|---|---|---|
| `deliverable` | `revenue_lifecycle_management_dev_guide` | The guide's atlas id. |
| `doc_version` | none | For example `264.0`. **Set this for a new release:** without it, the site keeps serving the previous release's guide even after the new one is published. Changing it on a corpus that already has captured pages requires `--mode refresh`. |
| `section` / `sections` | whole guide | TOC titles or page ids. `--section` on the CLI overrides a preset's `sections` for that run. |
| `follow_links` | on for a whole guide, off when sections are set | Whether cross-references pull in pages outside the TOC walk. |
| `output_dir` | `docs/salesforce/{release}/dev-guide` | |
| `batch_delay_ms` | 400 | Pause between fetch batches. |
| `max_pages` | 5000 | Safety cap. |

Flags that point at one specific target (`--root-article-id`, `--prefix`,
`--output-dir`, `--deliverable`, `--section`, `--sections`) are rejected when a
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
python -m scripts.doc_snapshot bootstrap --from 264 --to 266 --release-name "Spring '27" --discover
```

Bootstrap appends a new release block to `presets.yaml` as plain text, so
existing comments survive. It copies every preset's options and changes the
release number in each `output_dir`. It leaves out the two release-specific
options:

- `expect_min_articles`: set new floors once you've seen the new release's counts.
- `doc_version`: set it on the dev-guide presets once the new guide is published.

`--discover` then runs a discovery on every new Help preset, which gives you
the counts.

A Help area can serve the previous release's text for a while after the new
release appears. Before capturing, compare a few articles with the previous
release's corpus. New article ids, or changed text in shared articles, are good
signs that the area has been updated.

## Tests

```bash
python tests/test_snapshot_help.py           # stdlib only
python tests/test_snapshot_dev_guide.py      # stdlib only
python tests/test_doc_snapshot_presets.py    # needs PyYAML
```

All three run offline without a browser. `scripts/ai/pr_gate.py` runs them.
