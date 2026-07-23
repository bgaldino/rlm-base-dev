# syntax=docker/dockerfile:1
#
# Revenue Cloud Base Foundations — self-contained build environment.
#
# Bakes the full local toolchain (Python 3.13 + CumulusCI, Node LTS + Salesforce
# CLI + SFDMU v5, Robot Framework + headless Chromium) plus a snapshot of the
# repo and the friendly `rlm` wrapper CLI and a bundled Claude Code agent, so a
# user who knows nothing about git / cci / sf can connect orgs and build them.
#
# Build (from repo root):   docker build -f docker/Dockerfile -t rlm-base:latest .
# Run:                      docker/rlm            (host launcher — see docker/README.md)
#
# The toolchain mirrors docs/guides/dev-environment-setup.md, but pinned for a
# reproducible container instead of pyenv/nvm/direnv version managers.

FROM python:3.13-slim-bookworm

ARG NODE_MAJOR=24
ARG DEBIAN_FRONTEND=noninteractive

# ---------------------------------------------------------------------------
# Environment that must be in place for every `sf`/`cci` invocation, including
# the build-time SFDMU plugin install below.
#   - Generic UNIX keychain  → store auth as plain JSON under ~/.sfdx (no OS
#     keyring exists in a headless container).
#   - SF_TEMP_SHOW_SECRETS    → CCI 4.10.x still parses the access token out of
#     `sf --json`; the May 2026 redaction change otherwise breaks scratch creation
#     (see docs/guides/dev-environment-setup.md §6).
#   - Disable telemetry/auto-update so the CLI never prompts or self-mutates.
# ---------------------------------------------------------------------------
ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIPX_HOME=/opt/pipx \
    PIPX_BIN_DIR=/usr/local/bin \
    CHROME_BIN=/usr/bin/chromium \
    SF_USE_GENERIC_UNIX_KEYCHAIN=true \
    SFDX_USE_GENERIC_UNIX_KEYCHAIN=true \
    SF_TEMP_SHOW_SECRETS=true \
    SF_DISABLE_TELEMETRY=true \
    SF_DISABLE_AUTOUPDATE=true \
    npm_config_update_notifier=false \
    npm_config_fund=false \
    npm_config_audit=false

# ---------------------------------------------------------------------------
# OS packages: git, a headless browser + driver for the Robot UI steps in
# prepare_rlm_org (prepare_docgen, prepare_ux, ...), and small utilities the
# wrapper CLI relies on (jq, tini for PID 1 signal handling).
# ---------------------------------------------------------------------------
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        ca-certificates curl gnupg git jq less nano tini procps socat \
        chromium chromium-driver fonts-liberation libnss3 libxss1 libasound2; \
    rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------------------------------
# Node.js LTS → Salesforce CLI (sf) + Claude Code, installed globally.
# ---------------------------------------------------------------------------
RUN set -eux; \
    curl -fsSL "https://deb.nodesource.com/setup_${NODE_MAJOR}.x" | bash -; \
    apt-get install -y --no-install-recommends nodejs; \
    rm -rf /var/lib/apt/lists/*; \
    npm install -g @salesforce/cli @anthropic-ai/claude-code; \
    npm cache clean --force; \
    node --version; sf --version

# ---------------------------------------------------------------------------
# Python tooling: CumulusCI in an isolated pipx venv (bins published to
# /usr/local/bin), plus the Robot Framework deps injected into that same venv
# so CCI can drive `robot`. PyYAML goes in the system interpreter for the build
# harness (scripts/build_harness, which runs under the ambient `python3`).
# robot/requirements.txt is copied first so this layer caches independently of
# repo source churn.
# ---------------------------------------------------------------------------
COPY robot/requirements.txt /tmp/robot-requirements.txt
RUN set -eux; \
    pip install pipx PyYAML; \
    pipx install cumulusci; \
    pipx inject cumulusci "setuptools>=75.4"; \
    pipx inject cumulusci --force -r /tmp/robot-requirements.txt; \
    rm -f /tmp/robot-requirements.txt; \
    cci version

# ---------------------------------------------------------------------------
# Non-root runtime user. SFDMU is installed as this user so the plugin (which
# lives under ~/.local/share/sf, *outside* the persisted state dirs) is baked
# into the image and survives a fresh state volume. The final step asserts the
# baked plugin meets the repo floor of 5.6.4 (upsert-matching fix for
# relationship externalIds landed in the 5.6.4 release, commit 50be987; matches validate_setup's
# required_sfdmu_version) — `sort -V -C` exits non-zero, failing the build,
# if the installed version sorts below 5.6.4.
# ---------------------------------------------------------------------------
RUN set -eux; \
    useradd --create-home --uid 1000 --shell /bin/bash rlm; \
    su -s /bin/bash rlm -c 'mkdir -p ~/.config/sf && printf "%s" "[\"sfdmu\"]" > ~/.config/sf/unsignedPluginAllowList.json'; \
    su -s /bin/bash rlm -c 'sf plugins install sfdmu'; \
    su -s /bin/bash rlm -c 'v=$(sf plugins | grep -i sfdmu | grep -oE "[0-9]+\.[0-9]+\.[0-9]+" | head -1); echo "sfdmu $v"; printf "5.6.4\n%s\n" "$v" | sort -V -C'

# ---------------------------------------------------------------------------
# Baked repo snapshot + wrapper CLI, entrypoint, and interactive banner.
# ---------------------------------------------------------------------------
COPY --chown=rlm:rlm . /opt/rlm-base-dev
COPY docker/rlm-cli        /usr/local/bin/rlm
COPY docker/entrypoint.sh  /usr/local/bin/rlm-entrypoint
COPY docker/setup-state.sh /usr/local/bin/rlm-setup-state
COPY docker/motd.sh        /etc/profile.d/zz-rlm-motd.sh
RUN chmod +x /usr/local/bin/rlm /usr/local/bin/rlm-entrypoint /usr/local/bin/rlm-setup-state; \
    # Pre-create the state dir owned by rlm so a fresh *named* volume mounted
    # here inherits rlm ownership (Docker seeds an empty volume from the image
    # dir's perms). Without this, uid-1000 can't write to the root-owned volume.
    mkdir -p /home/rlm/.rlm-state; \
    chown -R rlm:rlm /home/rlm/.rlm-state

# CumulusCI requires the project to be a git repository (it reads branch/commit/
# remote from git). The baked snapshot ships without history (.git is excluded
# from the build context), so initialize a single-commit repo here — run as the
# rlm user so .git is rlm-owned and git doesn't flag "dubious ownership". A
# mounted /work repo brings its own .git and is unaffected.
RUN su -s /bin/bash rlm -c 'set -eux; cd /opt/rlm-base-dev; \
    export GIT_AUTHOR_NAME="RLM Build" GIT_AUTHOR_EMAIL="build@rlm.local"; \
    export GIT_COMMITTER_NAME="RLM Build" GIT_COMMITTER_EMAIL="build@rlm.local"; \
    git init -q; \
    git symbolic-ref HEAD refs/heads/main; \
    git add -A; \
    git commit -qm "Baked snapshot of rlm-base-dev"; \
    git remote add origin https://github.com/bgaldino/rlm-base-dev || true'

# HOME is set here (not earlier) so root's build steps above don't pollute the
# rlm home dir with root-owned cache files.
ENV HOME=/home/rlm \
    RLM_BAKED_REPO=/opt/rlm-base-dev \
    RLM_STATE_DIR=/home/rlm/.rlm-state \
    BASH_ENV=/home/rlm/.rlm-env

USER rlm
WORKDIR /opt/rlm-base-dev

# tini reaps zombies (sf/cci spawn child processes); entrypoint wires up the
# persistent state volume and chooses the baked vs. mounted repo.
ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/rlm-entrypoint"]
CMD ["shell"]
