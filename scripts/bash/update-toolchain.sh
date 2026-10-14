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
#   7. Gate interpreter — <main checkout>/.venv, if it exists (rebuilt after a
#      Python patch bump with its other packages carried over, then
#      pr_gate.py's requirements reinstalled); a $RLM_GATE_PYTHON override is
#      probed only. A gate interpreter left unusable fails the script after step 8
#   8. cci task run validate_setup
#
# Designed to be idempotent. Re-run after any tool emits a "new version" notice.
# Major-line pins live in this script (PY_LINE, NODE_LINE) — edit them to bump.

set -euo pipefail

PY_LINE="3.13"
NODE_LINE="lts/*"

# Ensure pipx-managed bins (cci, snowfakery, etc.) are findable. pipx
# ensurepath only updates shell rc files for future shells; we need PATH in
# *this* shell so the final `cci task run validate_setup` works from a
# minimal env. (Note: sf CLI lives under nvm's node bin, not here, and the
# sfdmu plugin lives inside sf's plugin tree — neither passes through pipx.)
export PATH="$HOME/.local/bin:$PATH"

log()  { printf '\n\033[1;34m[update]\033[0m %s\n' "$*"; }
warn() { printf '\n\033[1;33m[warn]\033[0m  %s\n' "$*" >&2; }
die()  { printf '\n\033[1;31m[fail]\033[0m  %s\n' "$*" >&2; exit 1; }

# ── 1. Homebrew ─────────────────────────────────────────────────────────────
command -v brew >/dev/null || die "brew not found — install Homebrew from https://brew.sh first"
log "Homebrew: update + upgrade"
brew update
brew upgrade

# ── 2. Python (pyenv) ───────────────────────────────────────────────────────
command -v pyenv >/dev/null || die "pyenv not found"

LATEST_KNOWN="$(pyenv latest -k "$PY_LINE" 2>/dev/null || true)"
LATEST_INSTALLED="$(pyenv latest "$PY_LINE" 2>/dev/null || true)"
[ -n "$LATEST_KNOWN" ] || die "pyenv can't resolve latest Python $PY_LINE — run 'brew upgrade pyenv' to refresh python-build definitions"

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
NVM_PREFIX="$(brew --prefix nvm 2>/dev/null || true)"
[ -n "$NVM_PREFIX" ] && [ -s "$NVM_PREFIX/nvm.sh" ] || die "nvm.sh not found via 'brew --prefix nvm' — is nvm installed?"
# shellcheck disable=SC1091
. "$NVM_PREFIX/nvm.sh"

OLD_NODE="$(nvm current 2>/dev/null || echo none)"
log "Node: installing $NODE_LINE (current: $OLD_NODE)"
# Drive install from NODE_LINE so changes at the top of this script take effect.
# `lts/*` resolves to the active LTS line; explicit majors (e.g. `24`) also work.
# --reinstall-packages-from=current carries `sf` and other globals forward.
nvm install "$NODE_LINE" --reinstall-packages-from=current --latest-npm
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
# Re-bootstrap pipx under $PY_TARGET first. A Python patch bump can break the
# existing pipx script's shebang (it pointed at the old patch's python3, which
# may have been uninstalled). `command -v pipx` would still succeed in that
# case but invocations would fail with a broken interpreter. Reinstalling pipx
# under the current target Python (idempotent) repairs this proactively.
PY_TARGET_BIN="$(pyenv prefix "$PY_TARGET")/bin/python3"
[ -x "$PY_TARGET_BIN" ] || die "Target Python not found: $PY_TARGET_BIN"
log "pipx: refresh under Python $PY_TARGET"
"$PY_TARGET_BIN" -m pip install --user --upgrade pipx
"$PY_TARGET_BIN" -m pipx ensurepath >/dev/null 2>&1 || true

# Pin pipx invocation to the target Python so subsequent calls aren't subject
# to PATH ordering surprises or shebang breakage from previous patch installs.
# We never invoke bare `pipx` after this point, so no PATH check is needed —
# this works even from a minimal env where ~/.local/bin isn't yet on PATH.
PIPX=( "$PY_TARGET_BIN" -m pipx )

cci_reinstall() {
  log "CCI: reinstalling under Python $PY_TARGET"
  "${PIPX[@]}" install --force cumulusci --python "$PY_TARGET_BIN"
}

if [ "$PY_UPGRADED" -eq 1 ] || ! "${PIPX[@]}" list --short 2>/dev/null | grep -q '^cumulusci'; then
  cci_reinstall
else
  log "CCI: upgrade in place"
  if ! "${PIPX[@]}" upgrade cumulusci; then
    warn "pipx upgrade failed — reinstalling"
    cci_reinstall
  fi
fi

# Modern CCI 4.8+ with snowfakery 4.x requires setuptools>=75.4.
# Historical `<71` pin is incompatible — see docs/guides/local-installation.md,
# "Step 7 — Install CumulusCI" (Note on setuptools).
# Force-inject to repair any stale legacy install.
# CI (.github/workflows/prepare-rlm-org.yml) pins CCI 4.10.1 with the same
# uncapped setuptools>=75.4; the old `<77` cap was only needed for CCI 4.8.1.
log "CCI: ensuring setuptools>=75.4"
"${PIPX[@]}" inject --force cumulusci "setuptools>=75.4"

# ── 6. sf plugins ───────────────────────────────────────────────────────────
log "sf plugins: update"
sf plugins update || warn "sf plugins update failed"

# ── 7. Gate interpreter (<main checkout>/.venv) ─────────────────────────────
# scripts/ai/pr_gate.py, the loop Stop hook and validate_setup's "Gate
# interpreter" check all run under <main checkout>/.venv. gate_python.py
# resolves and probes it for every one of them, so this step asks it too
# rather than restating where the venv lives. Like the pipx venv, its python
# is a symlink into one pyenv patch dir, so rebuild it when it isn't on
# $PY_TARGET (this also covers a symlink broken by an uninstalled patch). Then
# reinstall pr_gate.py's requirements, which pick up any DEPS change. Only an
# existing venv is managed: creating it is a setup step (local-installation.md,
# Step 6). A $RLM_GATE_PYTHON override is someone else's to manage, but it is
# still probed. Whichever venv is the gate interpreter must end up usable:
# validate_setup only warns about it, so a failure here fails the script
# (after validate_setup has run) instead of ending in "Done".
GATE_FAILED=""
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
gate_python() { (cd "$REPO_ROOT" && "$PY_TARGET_BIN" scripts/ai/gate_python.py "$@"); }

if [ -n "${RLM_GATE_PYTHON:-}" ]; then
  log "Gate interpreter: \$RLM_GATE_PYTHON is set ($RLM_GATE_PYTHON) — probing it, not managing it"
  gate_python >/dev/null || GATE_FAILED="\$RLM_GATE_PYTHON ($RLM_GATE_PYTHON) can't run every pr_gate.py check"
elif ! GATE_VENV="$(gate_python --default-venv)"; then
  warn "Gate interpreter: $REPO_ROOT is not a git checkout — skipping"
elif [ -d "$GATE_VENV" ]; then
  GATE_PY_VERSION="$("$GATE_VENV/bin/python" -c 'import platform; print(platform.python_version())' 2>/dev/null || true)"
  if [ "$GATE_PY_VERSION" != "$PY_TARGET" ]; then
    # --clear empties the whole venv, and the gate's packages are rarely all
    # it holds (the doc snapshot tooling and Robot requirements often live
    # here too). gate_python.py lists its top-level packages first, reading
    # site-packages itself so this works even when the venv's Python is gone.
    GATE_KEEP="$(mktemp "${TMPDIR:-/tmp}/gate-venv-packages.XXXXXX")"
    GATE_REBUILD=1
    if ! gate_python --carry-over "$GATE_VENV" >"$GATE_KEEP"; then
      if [ -n "$GATE_PY_VERSION" ]; then
        # It still runs, so clearing it would destroy what can't be listed for
        # nothing. Leave it on its old patch; the gate requirements still go in.
        warn "Gate interpreter: couldn't list the packages in $GATE_VENV — left on Python $GATE_PY_VERSION instead of rebuilding it"
        GATE_REBUILD=0
      else
        warn "Gate interpreter: couldn't list the packages in $GATE_VENV, and its Python is gone — rebuilding; only the gate's packages come back"
      fi
    fi
    [ "$GATE_REBUILD" -eq 0 ] || {
      log "Gate interpreter: rebuilding $GATE_VENV on Python $PY_TARGET (was ${GATE_PY_VERSION:-unusable})"
      "$PY_TARGET_BIN" -m venv --clear "$GATE_VENV"
    }
    if [ "$GATE_REBUILD" -eq 1 ] && [ -s "$GATE_KEEP" ]; then
      log "Gate interpreter: reinstalling the $(wc -l <"$GATE_KEEP" | tr -d ' ') package(s) it held"
      # All at once first. pip resolves a requirements file all-or-nothing,
      # so on failure go one at a time, retrying a pin that won't install on
      # this Python unpinned, and lose only what really can't come back.
      if ! "$GATE_VENV/bin/python" -m pip install -r "$GATE_KEEP"; then
        GATE_LOST=""
        # fd 3, so a pip that reads stdin can't swallow the rest of the list.
        while IFS= read -r req <&3; do
          case "$req" in
            "") continue ;;
            "-e "*) "$GATE_VENV/bin/python" -m pip install -e "${req#-e }" && continue ;;
            *) "$GATE_VENV/bin/python" -m pip install "$req" && continue
               case "$req" in
                 *==*) "$GATE_VENV/bin/python" -m pip install "${req%%==*}" && continue ;;
               esac ;;
          esac
          GATE_LOST="${GATE_LOST:+$GATE_LOST, }$req"
        done 3<"$GATE_KEEP"
        [ -z "$GATE_LOST" ] \
          || warn "Gate interpreter: these didn't come back: $GATE_LOST (full list: $GATE_KEEP)"
      fi
    fi
    [ -n "${GATE_LOST:-}" ] || rm -f "$GATE_KEEP"
  fi
  log "Gate interpreter: installing pr_gate.py requirements into $GATE_VENV"
  # Unquoted on purpose: one requirement per line, split into pip arguments.
  # shellcheck disable=SC2046
  if ! "$GATE_VENV/bin/python" -m pip install --upgrade \
      $("$GATE_VENV/bin/python" "$REPO_ROOT/scripts/ai/pr_gate.py" --requirements --all); then
    GATE_FAILED="pip install into $GATE_VENV failed"
  # The same probe the Stop hook and validate_setup run: every pr_gate.py
  # dependency imports, and the Python is new enough for every check.
  elif ! gate_python >/dev/null; then
    GATE_FAILED="$GATE_VENV still can't run every pr_gate.py check"
  fi
else
  log "Gate interpreter: $GATE_VENV not found — create it per docs/guides/local-installation.md (Step 6)"
fi
[ -z "$GATE_FAILED" ] || warn "Gate interpreter: $GATE_FAILED — see docs/guides/dev-environment-setup.md (Troubleshooting)"

# ── 8. Verify ───────────────────────────────────────────────────────────────
log "Running validate_setup"
cci task run validate_setup

[ -z "$GATE_FAILED" ] || die "Gate interpreter: $GATE_FAILED, so the local gate (scripts/ai/pr_gate.py) can't run all its checks"
log "Done."
