#!/usr/bin/env bash
# update-toolchain.sh — refresh the local dev toolchain for rlm-base-dev.
#
# Updates, in order:
#   1. Homebrew packages (direnv, nvm, pyenv, pipx, etc.)
#   2. Python — latest patch in the 3.13 line (via pyenv)
#   3. Node — latest LTS (via nvm), carrying npm globals forward
#   4. sf CLI — npm-installed under the active nvm Node
#   5. CCI — pipx (reinstall is required after any Python patch bump)
#   6. sf plugins (SFDMU, etc.)
#   7. cci task run validate_setup
#
# Designed to be idempotent. Re-run after any tool emits a "new version" notice.
# Major-line pins live in this script (PY_LINE, NODE_LINE) — edit them to bump.

set -euo pipefail

PY_LINE="3.13"
NODE_LINE="lts/*"

log()  { printf '\n\033[1;34m[update]\033[0m %s\n' "$*"; }
warn() { printf '\n\033[1;33m[warn]\033[0m  %s\n' "$*" >&2; }
die()  { printf '\n\033[1;31m[fail]\033[0m  %s\n' "$*" >&2; exit 1; }

# ── 1. Homebrew ─────────────────────────────────────────────────────────────
log "Homebrew: update + upgrade"
brew update
brew upgrade

# ── 2. Python (pyenv) ───────────────────────────────────────────────────────
command -v pyenv >/dev/null || die "pyenv not found"

LATEST_KNOWN="$(pyenv latest -k "$PY_LINE" 2>/dev/null || true)"
LATEST_INSTALLED="$(pyenv latest "$PY_LINE" 2>/dev/null || true)"
[ -n "$LATEST_KNOWN" ] || die "pyenv can't resolve latest Python $PY_LINE — run 'pyenv update' or upgrade pyenv"

log "Python: latest known $PY_LINE = $LATEST_KNOWN ; installed = ${LATEST_INSTALLED:-none}"
if [ "$LATEST_KNOWN" != "$LATEST_INSTALLED" ]; then
  log "Installing Python $LATEST_KNOWN"
  pyenv install --skip-existing "$LATEST_KNOWN"
  PY_UPGRADED=1
else
  log "Python $LATEST_INSTALLED already latest"
  PY_UPGRADED=0
fi
PY_TARGET="$(pyenv latest "$PY_LINE")"
export PYENV_VERSION="$PY_TARGET"

# ── 3. Node (nvm) ───────────────────────────────────────────────────────────
export NVM_DIR="$HOME/.nvm"
# shellcheck disable=SC1091
. "/opt/homebrew/opt/nvm/nvm.sh"

OLD_NODE="$(nvm current 2>/dev/null || echo none)"
log "Node: installing latest in $NODE_LINE (current: $OLD_NODE)"
# --reinstall-packages-from=current carries `sf` and other globals forward.
nvm install --lts --reinstall-packages-from=current --latest-npm
nvm alias default "$NODE_LINE" >/dev/null
NEW_NODE="$(nvm current)"
log "Node: now on $NEW_NODE"

# ── 4. sf CLI ───────────────────────────────────────────────────────────────
log "sf CLI: update channel"
if command -v sf >/dev/null 2>&1; then
  sf update || warn "sf update failed — try: npm install -g @salesforce/cli@latest"
else
  warn "sf not found on PATH for $NEW_NODE — installing"
  npm install -g @salesforce/cli@latest
fi

# ── 5. CCI (pipx) ───────────────────────────────────────────────────────────
command -v pipx >/dev/null || die "pipx not found"

if [ "$PY_UPGRADED" -eq 1 ] || ! pipx list --short 2>/dev/null | grep -q '^cumulusci'; then
  log "CCI: reinstalling under Python $PY_TARGET"
  pipx install --force cumulusci --python "$(pyenv prefix "$PY_TARGET")/bin/python"
else
  log "CCI: upgrade in place"
  pipx upgrade cumulusci || warn "pipx upgrade failed — falling back to reinstall"
fi

# CCI 4.x needs setuptools<71 (pyfilesystem2 / pkg_resources removed in 71+).
log "CCI: pinning setuptools<71"
pipx inject --force cumulusci "setuptools<71"

# ── 6. sf plugins ───────────────────────────────────────────────────────────
log "sf plugins: update"
sf plugins update || warn "sf plugins update failed"

# ── 7. Verify ───────────────────────────────────────────────────────────────
log "Running validate_setup"
cci task run validate_setup

log "Done."
