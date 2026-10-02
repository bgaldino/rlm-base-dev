# doc_snapshot — snapshot public Salesforce docs into markdown

A standalone CLI that captures public Salesforce documentation into
per-article markdown with YAML frontmatter plus a `manifest.json` and an
`index.md`, under `docs/salesforce/{release}/`. Agents use that corpus to
ground product claims; see
[`revenue-cloud-docs/SKILL.md`](../../.cursor/skills/revenue-cloud-docs/SKILL.md)
for how to use it.

| Subcommand | What it does |
|---|---|
| `list` | Show the presets in `presets.yaml` |
| `help` | Snapshot help.salesforce.com areas, release notes included (`help_portal.py`) |
| `dev-guide` | Snapshot developer.salesforce.com atlas developer guides (`dev_guide.py`) |
| `run` | Snapshot every preset of a release, both kinds |
| `check` | Non-gating lint of the captured Help corpus for glued-link text artifacts (`check.py`) |
| `bootstrap` | Add a release to `presets.yaml` by copying an existing one |

It needs no Salesforce org and no CumulusCI. The 30 `snapshot_*` CCI tasks it
replaced are gone.

## Install

Use any Python 3.9+ environment:

```bash
python3 -m venv .venv-docs && . .venv-docs/bin/activate
pip install -r scripts/doc_snapshot/requirements.txt
python -m playwright install chromium
```

- `playwright` is required by `help` and `dev-guide`.
- `markdownify` is optional. Without it, `dev-guide` falls back to a built-in
  HTML-to-markdown converter with weaker table and list output.
- `PyYAML` is needed for anything that reads `presets.yaml`. `check` needs
  neither it nor Playwright.

## Usage

Run from the repo root:

```bash
python -m scripts.doc_snapshot list --release 264
python -m scripts.doc_snapshot help --release 264 --area pricing --mode discover
python -m scripts.doc_snapshot help --release 264 --area pricing              # discover + capture pending
python -m scripts.doc_snapshot help --release 264 --area all                  # every help preset, in turn
python -m scripts.doc_snapshot help --release 264 --area release_notes --mode refresh
python -m scripts.doc_snapshot dev-guide --release 264 --guide rlm --section "Constraint Modeling Language"
python -m scripts.doc_snapshot run --release 264 --only pcm,rlm
python -m scripts.doc_snapshot check --release 264
```

`python scripts/doc_snapshot/cli.py …` works too. Each subcommand's `--help`
lists its flags.

`--area` and `--guide` accept a preset key, a comma-separated list of keys, or
`all`. When several presets run, a failure is logged and the remaining presets
still run. A summary table follows, and the exit code is 1 if any preset
failed. Flags that describe one specific target (`--root-article-id`,
`--prefix`, `--output-dir`, `--deliverable`, `--section`, `--sections`) are
rejected when more than one preset is selected.

**Ad hoc runs.** A `help` area does not need a preset. Pass its root and prefix
directly:

```bash
python -m scripts.doc_snapshot help --release 266 --release-name "Spring '27" \
    --area foo --root-article-id ind.foo.htm --prefix ind.foo --mode discover
```

**Exit codes.** `0` ok, `1` snapshot failed (thin or unstable discovery, an
HTTP error, a missing dependency), `2` usage error (bad options, unknown
preset).

**Do not run two `help` snapshots for one release at the same time.** Every
area shares one `help/manifest.json`, and the last process to save wins.

## Modes

| Mode | Behavior |
|---|---|
| `discover` | Walk the sidebar or TOC and record every article as `pending`. No bodies. A fast smoke test. |
| `capture` | Capture the manifest's pending articles only. |
| `all` (default) | Discover, then capture. Re-running never re-fetches captured articles. |
| `refresh` | Re-capture every article and overwrite the files. Use after a release update or an extractor change. |

## Options

Every option can be set on a preset or as a kebab-case flag. A flag overrides
the preset for that run, and an unset flag never masks a preset value.

**Shared:** `release_name` (written into frontmatter; defaults to the release
block's), `output_dir` (relative paths resolve from the repo root), `mode`,
`headless` (default `true`), `concurrency`, `wait_ms` (default 3000).

**`help`:**

| Option | Default | Notes |
|---|---|---|
| `root_article_id` | — | Required. Sidebar root to walk. |
| `article_id_prefix` | — | Required. A startswith filter on discovered ids. CLI alias `--prefix`. |
| `area` | the preset key | Tag recorded per article and per area in the shared manifest. |
| `output_dir` | `docs/salesforce/{release}/help` | |
| `concurrency` | 4 | |
| `discover_timeout_ms` | 20000 | How long to poll for the sidebar to stop growing. |
| `expect_min_articles` | none | Fail discovery below this count. Catches a partial walk that still finds something. |
| `include_release_param` | `true` | Adds `&release=` to article URLs. |
| `subtree_only` | `false` | Keep only the root's sidebar descendants. Used for release notes, where every product shares one prefix. |

**`dev-guide`:**

| Option | Default | Notes |
|---|---|---|
| `deliverable` | `revenue_lifecycle_management_dev_guide` | Atlas deliverable slug. |
| `doc_version` | the unversioned endpoint | e.g. `264.0`. The unversioned endpoint keeps serving the prior release after a new one publishes. Changing it on a captured manifest requires `--mode refresh`. |
| `section` / `sections` | whole guide | TOC titles or page ids. `--section` on the CLI replaces a preset's `sections` for that run. |
| `follow_links` | on for a whole guide, off when sections are set | Whether intra-guide cross-references pull in pages outside the TOC walk. |
| `output_dir` | `docs/salesforce/{release}/dev-guide` | |
| `concurrency` | 6 | |
| `batch_delay_ms` | 400 | Pause between fetch batches. |
| `max_pages` | 5000 | Safety cap. |

## Presets — `presets.yaml`

```yaml
releases:
  "264":                              # quoted: it's a path component
    release_name: "Winter '27"
    help:
      pcm:                            # preset key; `area` defaults to it
        root_article_id: ind.product_catalog_introduction.htm
        article_id_prefix: ind.product_catalog
        expect_min_articles: 53
    dev_guide:
      rlm:
        deliverable: revenue_lifecycle_management_dev_guide
        doc_version: "264.0"
```

Options are applied in this order, each overriding the one before:

1. the release block (`release_name`, `release_version`)
2. the preset
3. CLI flags

The comments in the file record how each root was verified, the prefix
conventions, and where each floor came from. Keep them current when you change
a preset.

### Add an area

1. Find the area's root: walk the sidebar from
   `ind.revenue_lifecycle_management.htm` and copy the area link's `id=`.
2. Try it with an ad hoc `help … --root-article-id … --prefix … --mode discover`,
   and read the `Discovered N unique articles (M total before prefix filter)`
   line. If `M` is 0, the root is wrong. If `N` is 0 but `M` is not, the prefix
   is wrong.
3. Add it as a key under the release's `help:` block, with an
   `expect_min_articles` floor below the discovered count.

### Add a release

```bash
python -m scripts.doc_snapshot bootstrap --from 264 --to 266 --release-name "Spring '27" --dry-run
python -m scripts.doc_snapshot bootstrap --from 264 --to 266 --release-name "Spring '27" --discover
```

Bootstrap appends the new block to `presets.yaml` as text, so existing comments
survive. It copies every root and prefix and rewrites each `output_dir` to the
new release. It drops `expect_min_articles` and `doc_version`, which have to be
re-derived for the new release. With `--discover`, it then discovers every new
help preset so the counts are available for setting floors.

## Tests

```bash
python tests/test_snapshot_help.py           # stdlib only
python tests/test_snapshot_dev_guide.py      # stdlib only
python tests/test_doc_snapshot_presets.py    # needs PyYAML
```

All three run offline, without a browser, and `scripts/ai/pr_gate.py` runs
them.
