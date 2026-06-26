# Revenue Cloud Base Foundations — Docker Build Environment

A single Docker image that contains **everything** needed to build and customize
Revenue Lifecycle Management (RLM) orgs from this repo — Python + CumulusCI, the
Salesforce CLI + SFDMU, Robot Framework + a headless browser, a snapshot of the
repo itself, and an AI assistant grounded in the repo's skills.

You do **not** need to know GitHub, CumulusCI, or the Salesforce CLI. You only
need Docker and a friendly command called `rlm`.

---

## 1. Install Docker

- **Mac / Windows:** install [Docker Desktop](https://docs.docker.com/get-docker/)
  and start it.
- **Linux:** install Docker Engine and make sure your user can run `docker`.

That's the only thing you install on your own computer.

## 2. Get the launcher

Everything runs through one script: [`docker/rlm`](rlm). From a checkout of this
repo, get the image one of two ways:

```bash
./docker/rlm setup                                   # build it locally (a few minutes)
# — or — download a published image instead of building:
RLM_IMAGE=ghcr.io/bgaldino/rlm-base:latest ./docker/rlm pull
```

`pull` downloads the image and tags it `rlm-base:latest`, so every later command
just works. (Publishing the image is a one-time maintainer step — see
[Publishing the image](#publishing-the-image-maintainers).)

> Tip: copy `docker/rlm` anywhere on your `PATH` (e.g. `~/bin/rlm`) and you can
> just type `rlm …` from anywhere. The first real command auto-builds the image
> if you skip `setup`.

## 3. Pick your path

There are **two ways to work**. Not sure which? Run the guided chooser:

```bash
./docker/rlm start     # asks what you want to do and connects the right thing
```

Otherwise jump straight in:

- **① Build a brand-new org** — you create your own scratch orgs (needs a Dev Hub) → A below.
- **② Customize an org you already have** — sandbox / dev / existing scratch → B below.

In both cases the AI assistant (C) can make changes for you.

### A) Build a brand-new, fully-configured org

```bash
./docker/rlm login --devhub     # 1. connect a Salesforce Dev Hub
./docker/rlm build              # 2. create + configure a fresh scratch org
./docker/rlm open               # 3. print a URL to open it in your browser
```

`rlm login` prints a **link** to open in your browser. The browser-based flow is
**best-effort inside a container** — Salesforce CLI's localhost OAuth callback
doesn't always complete headless. If it hangs after you click *Allow*, use the
**reliable import** instead: pipe in an existing login as an SFDX auth URL.

```bash
# Already have the org/Dev Hub authorized with sf on this machine? Reuse it:
SF_TEMP_SHOW_SECRETS=true sf org auth show-sfdx-auth-url --target-org <username> --json \
  | ./docker/rlm login --auth-url --devhub --alias devhub
```

The credential is piped straight host→container (never written to host disk or
shown in a terminal), used by `sf`, and shredded. Drop `--devhub` (and use a
different alias) to import a regular org you want to customize.

`rlm build` creates a scratch org and runs the full 35-step `prepare_rlm_org`
flow. It can take a while. If a step fails (usually transient), just run
`./docker/rlm resume` to continue from where it stopped.

Faster, lighter build (skips the UI-heavy steps — UX, document generation, PRM,
analytics):

```bash
./docker/rlm build --lite
```

Other build options: `--shape ent|dev` (default `ent`), `--days N` (default
`30`), `--alias NAME` (default auto-generated).

### B) Customize an org you already have

```bash
./docker/rlm login              # sign in to an existing org (production / dev)
./docker/rlm login --sandbox    # ...or a sandbox (test.salesforce.com)
./docker/rlm deploy             # apply the full RLM build to it
./docker/rlm customize          # ...or run individual build steps
```

`rlm deploy` runs the same configuration flow against your connected org. It
deploys metadata **and** data, so point it at a dev/test org, not production.
`rlm customize` lets you run one flow/task at a time (or hand it to the AI).

### C) Customize / extend an org with AI help

```bash
./docker/rlm ask "add the payments feature to my org and explain what changed"
./docker/rlm assist             # open an interactive AI session
./docker/rlm customize          # menu of individual build steps to run
```

`rlm ask` / `rlm assist` launch a bundled **Claude Code** agent that reads this
repo's `CLAUDE.md` and `.cursor/skills/`, so it already knows the project's
conventions (SFDMU rules, pricing wiring, UX assembly, etc.).

**Sign the assistant in once** (either option):

- Easiest — pass a Console API key when you launch:
  ```bash
  ANTHROPIC_API_KEY=sk-ant-... ./docker/rlm assist
  ```
- Or log in with your Claude subscription:
  ```bash
  ./docker/rlm auth-ai
  ```

---

## Work inside the container (Cursor / VS Code / Claude Code)

The one-off commands above each spin up a throwaway container. To **live inside**
the container — editing files, running builds, and driving an AI agent — start a
persistent one and attach your editor.

### Start a persistent workspace

```bash
./docker/rlm up        # starts a long-running container named "rlm-base"
./docker/rlm attach    # opens a shell inside it (welcome banner + rlm commands)
./docker/rlm down      # stop + remove it when you're done
./docker/rlm logs      # follow its logs
```

`up` bind-mounts your checkout at `/work` (so edits persist on your machine),
keeps your logins, and publishes the sign-in port — so `rlm login`, `rlm build`,
`claude`, `cci`, and `sf` all work in the attached shell.

### Attach Cursor or VS Code

This repo ships a [`.devcontainer/devcontainer.json`](../.devcontainer/devcontainer.json).
With the **Dev Containers** extension installed, either:

- **Reopen in Container** — Command Palette → *Dev Containers: Reopen in
  Container*. Your editor opens the repo *inside* the image, with the Salesforce
  and Claude Code extensions preinstalled and the integrated terminal already in
  the toolchain.
- **Attach to a running one** — after `./docker/rlm up`, Command Palette →
  *Dev Containers: Attach to Running Container…* → **rlm-base**.

> Cursor uses the Open VSX marketplace; if "Reopen in Container" isn't available,
> install the **Dev Containers** extension (or just use `./docker/rlm up` +
> *Attach to Running Container*, which Cursor supports).

### Use Claude Code inside the container

Claude Code is already installed. In the container's terminal (attached shell or
the IDE's integrated terminal):

```bash
claude                 # interactive agent, grounded in CLAUDE.md + .cursor/skills
rlm ask "..."          # one-shot
```

Sign it in once with `ANTHROPIC_API_KEY` (pass it to `./docker/rlm up` via your
shell environment) or `rlm auth-ai`.

---

## Your logins are remembered

All Salesforce and CumulusCI credentials are stored in a Docker named volume
(`rlm-state`) mounted at `/home/rlm/.rlm-state`. They persist across runs, so you
sign in once. To start completely fresh:

```bash
docker volume rm rlm-state
```

## Keeping your changes / working on the repo itself

By default the container uses a **baked-in snapshot** of the repo, so it's fully
self-contained. If you want to work against your own checkout (and keep edits,
build artifacts, customizations), mount it:

```bash
RLM_MOUNT_REPO="$(pwd)" ./docker/rlm assist
```

Anything the container does then happens in your working copy on disk. With
Compose, uncomment the `../:/work` line in [`compose.yaml`](compose.yaml).

## Updating

- **Repo / build logic changed:** rebuild the image — `./docker/rlm setup`.
- **Just want a shell to poke around:** `./docker/rlm shell`.

---

## Command reference (`rlm help`)

**Host launcher only** (manage the image + a persistent container):

| Command | What it does |
|---|---|
| `./docker/rlm setup` | Build the image locally. |
| `./docker/rlm pull [REF]` | Download a published image and tag it `rlm-base:latest`. |
| `./docker/rlm up` | Start a persistent workspace container (`rlm-base`). |
| `./docker/rlm attach` | Open a shell in the persistent container. |
| `./docker/rlm down` / `logs` | Stop+remove / follow logs of the persistent container. |

**In-container `rlm`** (also reachable as `./docker/rlm <cmd>`):

| Command | What it does |
|---|---|
| `rlm start` | Guided chooser — connect a Dev Hub (build new) or an existing org (customize). |
| `rlm login [--devhub] [--sandbox] [--alias N]` | Browser sign-in (best-effort in containers — see auth notes). |
| `rlm login --auth-url [--devhub] [--alias N]` | **Reliable** — import an existing login piped in as an SFDX auth URL. |
| `rlm connect` | Alias for `rlm login` (an existing target org). |
| `rlm orgs` | List the orgs you're signed in to. |
| `rlm build [--lite] [--shape ent\|dev] [--days N] [--alias N] [-y]` | Build a new scratch org. Resumable. |
| `rlm resume` | Resume the last build from where it failed. |
| `rlm deploy [--org ALIAS]` | Run the full build flow against a connected org. |
| `rlm open [ALIAS]` | Print a browser login URL for an org. |
| `rlm customize` | Interactive menu of individual build steps. |
| `rlm ask "PROMPT"` | One-shot AI request grounded in the repo skills. |
| `rlm assist [PROMPT]` | Interactive AI session. |
| `rlm auth-ai` | Sign the AI assistant in to your Claude account. |
| `rlm tui` | Launch the interactive Build Manager TUI (advanced). |
| `rlm doctor` | Verify the toolchain (`cci task run validate_setup`). |
| `rlm version` | Show tool + repo versions. |
| `rlm shell` | Drop into a bash shell. |
| `rlm cci …` / `rlm sf …` | Pass commands straight to CumulusCI / Salesforce CLI. |

---

## How it works (for maintainers)

| File | Role |
|---|---|
| [`Dockerfile`](Dockerfile) | Builds the image: Python 3.13 + CumulusCI (pipx), Node LTS + `sf` CLI + SFDMU, Robot deps + Chromium, Claude Code, a non-root `rlm` user, and a baked repo at `/opt/rlm-base-dev`. |
| [`entrypoint.sh`](entrypoint.sh) | Per-run setup: symlinks `~/.sfdx`, `~/.sf`, `~/.cumulusci` into the single state volume; generates a stable `CUMULUSCI_KEY`; selects the baked repo or a `/work` mount; dispatches. |
| [`rlm-cli`](rlm-cli) | The in-container `rlm` command (installed to `/usr/local/bin/rlm`). |
| [`rlm`](rlm) | The **host** launcher that wraps `docker run`. |
| [`motd.sh`](motd.sh) | Interactive welcome banner. |
| [`compose.yaml`](compose.yaml) | Compose alternative to the host launcher. |
| [`.devcontainer/devcontainer.json`](../.devcontainer/devcontainer.json) | Cursor / VS Code Dev Container definition (image, `/work` mount, extensions). |
| [`.github/workflows/docker-publish.yml`](../.github/workflows/docker-publish.yml) | Opt-in CI to build + push the image to GHCR. |
| `.dockerignore` (repo root) | Keeps secrets, caches, and large runtime outputs out of the baked snapshot. |

The persistent-workspace lifecycle (`up`/`attach`/`down`) keeps a named
container alive via the entrypoint's `serve` mode (`exec sleep infinity`), so
`docker exec` and IDE attach work. The in-container `rlm` recovers `RLM_REPO`
and the CumulusCI key on its own, so it behaves the same whether launched by the
entrypoint or a bare `docker exec`.

Design decisions worth knowing:

- **Auth: `--auth-url` import is reliable; the web flow is best-effort.** This
  `sf` build has no device login. `org login web` won't print its URL (it
  auto-opens a browser) and binds its OAuth callback to loopback, so `rlm login`
  jumps through hoops to surface the URL (stay-alive fake `firefox` on `PATH`),
  bind IPv4 (`NODE_OPTIONS=--dns-result-order=ipv4first`), relay it out
  (`socat` `1717`→`1718`), and publish on both `127.0.0.1` and `[::1]` (since
  `localhost` resolves to IPv6 first on macOS). **Even so, Salesforce CLI's
  callback server frequently doesn't complete the handshake headless** — the
  browser reaches `localhost:1717` but the page hangs. The dependable path is
  `rlm login --auth-url`, which imports an existing SFDX auth URL via stdin and
  needs no callback. `SF_USE_GENERIC_UNIX_KEYCHAIN=true` stores tokens as files
  (no OS keyring); `SF_TEMP_SHOW_SECRETS=true` keeps CCI's scratch-org creation
  working (see `docs/guides/dev-environment-setup.md` §6).
- **Builds route through the build harness.** `rlm build` writes a one-off
  scenario for `scripts/build_harness/harness.py` and runs it with
  `--keep-orgs`. That's the maintained way to apply `project.custom` flag
  overrides (full vs. `--lite`) — `cci flow run` has no `--skip` — and it gives
  free checkpoint/resume.
- **Single state volume.** The SFDMU plugin lives under `~/.local/share/sf`
  (outside the relinked auth dirs), so it stays baked in the image even with a
  brand-new `rlm-state` volume.

## Publishing the image (maintainers)

So users can `pull` instead of `build`, publish the image to GitHub Container
Registry with [`.github/workflows/docker-publish.yml`](../.github/workflows/docker-publish.yml):

- **Manually:** Actions → *Publish build-environment image* → *Run workflow*
  (pick a tag like `latest` or `262`).
- **On a tag:** push `image-v<version>` (e.g. `git tag image-v262.0 && git push origin image-v262.0`).

It builds `linux/amd64` + `linux/arm64` and pushes to
`ghcr.io/<owner>/rlm-base:<tag>` and `:latest`. Make the package **public**
(Packages → rlm-base → Package settings → Change visibility) so users can pull
without authenticating; otherwise they run `docker login ghcr.io` first. Then:

```bash
RLM_IMAGE=ghcr.io/<owner>/rlm-base:latest ./docker/rlm pull
```

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Docker is installed but not running` | Start Docker Desktop. |
| `No Dev Hub connected` on `rlm build` | Run `rlm login --devhub` first. |
| Login link spins / hangs after you click **Allow** | Salesforce CLI's headless callback often doesn't complete. Use the reliable import: `... show-sfdx-auth-url ... --json \| ./docker/rlm login --auth-url --devhub`. |
| Build stopped partway | `rlm resume`. Inspect `.harness/runs/<id>/report.md` (mount the repo to keep it). |
| AI says it isn't signed in | Set `ANTHROPIC_API_KEY` or run `rlm auth-ai`. |
| Want to verify the toolchain | `rlm doctor`. |
| Start over with fresh logins | `docker volume rm rlm-state`. |
