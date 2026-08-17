# Deploy a GitHub Repo into Your Org with an AI Agent

Point an AI coding agent (**Cursor** or **Claude Code**) at a GitHub repository
link and have it deploy that repo's metadata into a Salesforce org you already
have — a sandbox, a Developer Edition, or a scratch org. The agent does the
mechanical work: clone the repo, read its layout, pick the right deploy command,
authenticate to your org, deploy, run any post-deploy steps the repo's README
calls for, and verify.

This is a **general pattern** that works for most source-format Salesforce
projects. The [Usage Wallet Preview Utility](https://github.com/jason-runnels-git/usage-wallet-preview-utility)
is used throughout as a concrete worked example, but nothing here is specific to
it.

> **Audience:** a developer comfortable running a local toolchain (`git`, the
> Salesforce CLI, Node). If you'd rather install almost nothing, see the
> container path in [`docker/README.md`](../../docker/README.md) — the `rlm`
> wrapper bundles the whole toolchain and a Claude Code agent.

> **Target org:** this guide assumes an **existing** org (sandbox / dev /
> Developer Edition). **Never point it at production.** A deploy changes
> metadata and can load data; treat it like any other change you'd review first.

---

## 1. What kinds of repos this works for

The agent adapts to whatever the repo actually is. The common shapes:

| Repo contains… | Deploy mechanism the agent should use |
|----------------|----------------------------------------|
| `sfdx-project.json` + a source dir (e.g. `force-app/`) | `sf project deploy start` (Salesforce CLI) |
| `cumulusci.yml` | `cci flow run <flow>` / `cci task run <task>` (CumulusCI) |
| An unlocked/managed **package** id or install link in the README | `sf package install` (or the install URL) |
| A bare `mdapi`/`src` folder with `package.xml` | `sf project deploy start --metadata-dir …` after conversion, or `sf project convert mdapi` |
| **Data** the app needs (CSV + a loader, SFDMU, or "Known Gotchas" in the README) | Whatever the README specifies — this is the step people forget |

The **most important file for the agent to read is the repo's `README.md`.** Good
Salesforce READMEs (the wallet example included) list *prerequisites*, *manual
setup*, and *known gotchas* that no deploy command performs automatically —
permission-set assignment, feature toggles, field-level config, record
activation order, sample data. The agent's real value is turning that prose into
the exact CLI commands and doing them in order.

---

## 2. One-time prerequisites (local)

You need these installed once. Ask the agent to verify them for you (see the
prompt in §4) — it can install anything missing.

| Tool | Check | Install (macOS) |
|------|-------|-----------------|
| **git** | `git --version` | `brew install git` |
| **Salesforce CLI (`sf`)** | `sf --version` (2.x) | `npm install -g @salesforce/cli` |
| **Node.js (LTS)** | `node --version` | `nvm install --lts` |
| GitHub CLI (optional, for private repos) | `gh --version` | `brew install gh` && `gh auth login` |

If the repo uses CumulusCI you'll also need `cci` (`pipx install cumulusci`) and,
for data plans, the SFDMU plugin (`sf plugins install sfdmu`). For the full,
canonical local setup see [`docs/guides/dev-environment-setup.md`](./dev-environment-setup.md).

> **Agent PATH note (important for both tools):** Cursor and Claude Code spawn
> **non-interactive** shells that do **not** source `~/.zshrc`. If the agent says
> `sf: command not found` even though your terminal finds it, your tool init for
> `nvm`/`pyenv` lives in `~/.zshrc` only. Move it to `~/.zshenv` and restart the
> agent. This repo's README documents the exact `~/.zshenv` blocks under
> *macOS Environment Setup → Steps 3 and 4*.

---

## 3. The workflow the agent runs

Whether you use Cursor or Claude Code, the agent should follow the same eight
steps. You don't have to type these — the prompt templates in §4 tell it to — but
knowing the shape lets you supervise it.

1. **Clone** the repo into a working directory
   (`git clone <url>` — or `gh repo clone` for a private repo).
2. **Inspect** it: read `README.md`, `sfdx-project.json`, `cumulusci.yml`,
   `package.xml`, the source tree, and any `data/`/`scripts/` folders. Decide the
   deploy mechanism from the table in §1.
3. **Confirm the target org** with you and authenticate (see §3.1). Echo back
   *which* org it's about to touch before deploying.
4. **Dry-run / validate** the deploy first
   (`sf project deploy start --dry-run …`) and show you the plan.
5. **Deploy** the metadata.
6. **Post-deploy steps** from the README: assign permission sets, flip feature
   toggles, load sample data, set fields that aren't on a layout, respect any
   activation ordering. This is where most "it deployed but nothing shows up"
   problems live.
7. **Verify**: deploy status succeeded, permission sets assigned, a smoke check
   (open the page / query the objects).
8. **Summarize** what changed and what you still have to do by hand.

### 3.1 Authenticating to your org

The agent runs one of these for you. **Alias** the org so later commands are
unambiguous.

```bash
# Production or Developer Edition or a dev org (login.salesforce.com)
sf org login web --alias myorg

# Sandbox (test.salesforce.com)
sf org login web --alias mysandbox --instance-url https://test.salesforce.com

# Confirm what you connected
sf org display --target-org myorg
```

A browser opens; log in and approve. From then on the agent passes
`--target-org myorg` (or `-o myorg`) on every command.

### 3.2 Deploying (source-format / SFDX repo)

For a repo with `sfdx-project.json` and a `force-app/` directory (the common
case, and what the wallet example is):

```bash
# Validate first — deploys nothing, just checks
sf project deploy start --source-dir force-app --target-org myorg --dry-run

# Then deploy for real
sf project deploy start --source-dir force-app --target-org myorg
```

If the repo declares multiple package directories, deploy the whole project by
dropping `--source-dir` (the CLI reads `sfdx-project.json`), or name the specific
directory you want.

### 3.3 Deploying (CumulusCI repo)

```bash
cci org connect myorg          # or: cci org import <sf-alias> myorg
cci flow list                  # find the setup flow
cci flow run <flow_name> --org myorg
```

---

## 4. Prompt templates

Paste one of these into the agent, filling the three placeholders. Both
templates encode the §3 workflow, the safety gates, and "read the README for
manual steps."

### Cursor

Open the agent (`Cmd+L` / `Cmd+I`) in a folder where it's OK to clone the repo,
and paste:

```text
Deploy this GitHub repo into my Salesforce org.

Repo:   <PASTE GITHUB URL>
Org:    <alias or username of my target org>   (this is a <sandbox|dev|dev-edition> org — NOT production)

Do this:
1. Clone the repo into a subfolder here.
2. Read README.md, sfdx-project.json / cumulusci.yml, and the source tree.
   Tell me what the repo is and which deploy mechanism you'll use.
3. Make sure `sf` (and `cci` if needed) are installed; if not, stop and tell me.
4. Confirm the exact org you'll deploy to (run `sf org display`) before touching it.
5. Run a validate/dry-run deploy and show me the plan.
6. Deploy.
7. Do EVERY post-deploy step the README calls for — permission sets, feature
   toggles, sample data, field/config that isn't on a layout, activation order.
   List anything you cannot automate so I can do it by hand.
8. Verify the deploy succeeded and give me a short summary of what changed and
   what's left for me to do.

Stop and ask me before anything destructive or anything that loads/deletes data.
```

### Claude Code

From a terminal in your working directory, run `claude`, then paste the **same
prompt** above. Claude Code will use its Bash tool to run the `git` / `sf` / `cci`
commands. If it reports a tool isn't found, see the PATH note in §2.

> Tip: if the repo ships its own `CLAUDE.md` / `AGENTS.md` / `.cursor/rules`,
> the agent will pick those up automatically once the repo is cloned and open —
> they usually encode the project's real deploy steps, so let them take
> precedence over this generic flow.

---

## 5. Worked example — Usage Wallet Preview Utility

Repo: `https://github.com/jason-runnels-git/usage-wallet-preview-utility`

**What the agent discovers by reading it:**

- `sfdx-project.json` → source-format project, single `force-app` package dir,
  API 66.0, no namespace. **Deploy mechanism: `sf project deploy start`.**
- The metadata is 2 Apex classes + 2 Lightning Web Components (a Quote wallet bar
  and a negotiate modal). No `cumulusci.yml`, no package install — a plain metadata deploy.
- The README's **Prerequisites / Known Gotchas** are the real work. The utility
  *reads live usage data*, so after the deploy nothing renders until the org has
  the right configuration.

**Deploy:**

```bash
git clone https://github.com/jason-runnels-git/usage-wallet-preview-utility
cd usage-wallet-preview-utility
sf org login web --alias mysandbox --instance-url https://test.salesforce.com
sf project deploy start --source-dir force-app --target-org mysandbox --dry-run
sf project deploy start --source-dir force-app --target-org mysandbox
```

**Post-deploy (from that repo's README — the agent should walk these, not skip them):**

- Add the LWCs to the Quote record page (Lightning App Builder) if they aren't
  surfaced automatically.
- Ensure the usage config **data** exists: `ProductUsageResource`,
  `ProductUsageGrant` (Quantity set), `RateCardEntry` (Rate set) for the anchor product.
- **Activation order matters:** `ProductUsageGrant` → `ProductUsageResource` →
  Anchor `Product` (never reversed; a Draft grant shows quantity 0).
- Set `UoM Class Type = Usage` and `UoM Type = Custom` — not on the default
  layout, so set it via CLI/Dev Console.
- Rate Card Entry Rate UoM = USD.
- On the quote: add the anchor product line, open **Manage Usage Resources** once
  per line so the override records the utility reads get created.

This example makes the general lesson concrete: **the deploy is one command; the
README's manual configuration is the part that actually makes it work**, and it's
exactly what you want the agent to execute for you step by step.

---

## 6. Safety, review, and verification

- **Never deploy to production** from this flow. Point at a sandbox / dev / DE org.
- **Read the dry-run.** `--dry-run` (or `cci` in a scratch org) shows what will
  change before it changes. Have the agent show it to you.
- **Gate data operations.** Metadata deploys are reversible-ish; data
  loads/deletes are not. Tell the agent to pause before anything that writes or
  deletes records.
- **Watch destructive flags.** Be suspicious of `--ignore-conflicts`,
  `sf project delete source`, `deleteOldData: true` (SFDMU), or any "reset the
  org" step. Approve them explicitly.
- **Check licenses/features.** Some repos need features your org doesn't have
  (e.g. Revenue Cloud, a specific edition). A deploy that references missing
  entities will fail — that's the README's job to warn you, and the agent should
  surface it.
- **Verify at the end:** `sf project deploy report`, `sf org assign permset` ran,
  and an actual smoke check (open the page, run a SOQL query on the new objects).

---

## 7. Troubleshooting

| Symptom | Likely cause / fix |
|---------|--------------------|
| Agent: `sf: command not found` (but your terminal finds it) | Non-interactive shell PATH — move `nvm`/`pyenv` init to `~/.zshenv`, restart the agent (§2). |
| `sf org login web` hangs / can't open browser | Log in in a real terminal, or import an existing auth: `sf org login sfdx-url`. Headless/container logins are unreliable. |
| Private repo won't clone | `gh auth login` first, then `gh repo clone <owner>/<repo>`. |
| Deploy fails on missing objects/fields | Org lacks a required feature/license, or a dependency the README lists wasn't set up first. Read the README prerequisites. |
| `INVALID_TYPE` / API version mismatch | The repo's `sourceApiVersion` is newer than the org. Lower it in `sfdx-project.json` or update the org. |
| Deployed but the UI shows nothing | Post-deploy config missing — permission set, page assignment, feature toggle, or required data. This is the norm, not a bug. |
| Component references data that isn't there | Load the sample/config data the README specifies, respecting any activation order. |

---

## See also

- [`docker/README.md`](../../docker/README.md) — zero-local-install path via the
  `rlm` container (bundles the toolchain + a Claude Code agent).
- [`docs/guides/dev-environment-setup.md`](./dev-environment-setup.md) — canonical
  local toolchain (pyenv/nvm/CCI/sf) and the `~/.zshenv` agent-PATH fix.
- [Salesforce CLI deploy reference](https://developer.salesforce.com/docs/atlas.en-us.sfdx_cli_reference.meta/sfdx_cli_reference/cli_reference_project_commands_unified.htm)
- [CumulusCI documentation](https://cumulusci.readthedocs.io/)
