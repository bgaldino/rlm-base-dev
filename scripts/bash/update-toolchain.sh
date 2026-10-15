#!/usr/bin/env bash
# update-toolchain.sh — refresh the local dev toolchain for rlm-base-dev.
#
# Updates, in order:
#   1. Homebrew packages (direnv, nvm, pyenv, pipx, etc.), keeping openssl@3
#      installed on request first
#   2. Python — latest patch in the 3.13 line (via pyenv); stops if it can't
#      import ssl. pyenv's global follows it from an older 3.13 patch that holds
#      no packages of its own; anything else is left alone, with a warning when
#      it's an older patch that does
#   3. Node — latest LTS (via nvm), carrying npm globals forward
#   4. sf CLI — npm-installed under the active nvm Node
#   5. CCI — pipx (reinstall is required after any Python patch bump), then
#      robot/requirements.txt re-injected (CCI's own pins downgrade selenium)
#   6. sf plugins (SFDMU, etc.)
#   7. Gate interpreter — <main checkout>/.venv, if it exists (rebuilt after a
#      Python patch bump, or when it isn't built on pyenv's Python, with its
#      other packages carried over, then
#      pr_gate.py's requirements reinstalled); a $RLM_GATE_PYTHON override is
#      probed only. A gate interpreter left unusable fails the script after step 9
#   8. Build-harness TUI venvs — <checkout>/.harness/tui-venv in every worktree,
#      rebuilt the same way, so an old Python patch can be uninstalled
#   9. cci task run validate_setup
#
# A step that fails without stopping the run is listed again at the end, and
# the script exits nonzero rather than printing "Done".
#
# Designed to be idempotent. Re-run after any tool emits a "new version" notice.
# Major-line pins live in this script (PY_LINE, NODE_LINE) — edit them to bump.

set -euo pipefail

PY_LINE="3.13"
NODE_LINE="lts/*"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Ensure pipx-managed bins (cci, snowfakery, etc.) are findable. pipx
# ensurepath only updates shell rc files for future shells; we need PATH in
# *this* shell so the final `cci task run validate_setup` works from a
# minimal env. (Note: sf CLI lives under nvm's node bin, not here, and the
# sfdmu plugin lives inside sf's plugin tree — neither passes through pipx.)
export PATH="$HOME/.local/bin:$PATH"

log()  { printf '\n\033[1;34m[update]\033[0m %s\n' "$*"; }
warn() { printf '\n\033[1;33m[warn]\033[0m  %s\n' "$*" >&2; }
die()  { printf '\n\033[1;31m[fail]\033[0m  %s\n' "$*" >&2; exit 1; }
# A step that didn't do its job, but needn't stop the steps after it. The script
# still fails at the end, after validate_setup: validate_setup can pass with an
# update missing, so "Done" would claim more than happened.
STEP_FAILED=()
fail_later() { warn "$*"; STEP_FAILED+=("$*"); }
# Something the owner should act on that isn't a failure (the run still ends in
# "Done"). Repeated at the end too, so it isn't lost above a long run's output.
NOTICES=()
notice_later() { warn "$*"; NOTICES+=("$*"); }

# ── 1. Homebrew ─────────────────────────────────────────────────────────────
command -v brew >/dev/null || die "brew not found — install Homebrew from https://brew.sh first"
log "Homebrew: update + upgrade"
brew update
# Keep openssl@3 before upgrading. The pyenv Python 3.13 builds link it, but
# Homebrew now defaults to openssl@4 and pyenv depends on that, so once nothing
# Homebrew tracks needs openssl@3, upgrade's autoremove deletes it and every
# `cci` dies at startup (docs/guides/dev-environment-setup.md, "OpenSSL 4
# migration"). Marking it installed on request is what keeps it; a machine set
# up before that step was documented has it as a dependency only.
brew list --versions openssl@3 >/dev/null 2>&1 || brew install openssl@3
brew tab --installed-on-request openssl@3 >/dev/null \
  || die "couldn't mark openssl@3 installed on request (brew tab), so brew upgrade could remove it"
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
PY_TARGET_BIN="$(pyenv prefix "$PY_TARGET")/bin/python3"
[ -x "$PY_TARGET_BIN" ] || die "Target Python not found: $PY_TARGET_BIN"
# CumulusCI imports ssl at startup, so a Python that can't would only fail
# later, after the Node and sf steps, inside pipx and validate_setup. Stop
# here, before any of them, with Python's own error.
# openssl@3 is in place by now (step 1), so a failure means this Python was
# built against another OpenSSL, or its install is broken: rebuild it.
"$PY_TARGET_BIN" -c 'import ssl' \
  || die "Python $PY_TARGET can't import ssl (error above) — rebuild it with 'pyenv install --force $PY_TARGET' while openssl@3 is installed; see docs/guides/dev-environment-setup.md (OpenSSL 4 migration)"

# scripts/ai/gate_python.py: resolves and probes the gate interpreter (step 7),
# and --carry-over lists the packages a Python environment holds of its own,
# reading site-packages directly, so it works when that environment's Python is
# gone. Steps 2, 7 and 8 all use it.
gate_python() { (cd "$REPO_ROOT" && "$PY_TARGET_BIN" scripts/ai/gate_python.py "$@"); }

# pyenv's global version (~/.pyenv/version) is the `python` every shell gets
# outside a project that pins its own. It moves with the line, as step 3 moves
# nvm's default Node, but only from an older patch of $PY_LINE, and only when
# that interpreter holds no packages of its own: anything pip-installed straight
# into it would disappear from `python` and the pyenv shims after the switch.
# Virtualenvs built on it are unaffected either way (they record its path), so
# none of them needs rebuilding for this. A global set to `system`, another
# line or several versions is a deliberate choice and is left alone.
PY_GLOBAL="$(pyenv global 2>/dev/null | paste -sd ' ' - || true)"
PY_LINE_RE="^${PY_LINE//./\\.}\\.[0-9]+$"
if [ "$PY_GLOBAL" = "$PY_TARGET" ]; then
  log "Python: pyenv global is $PY_TARGET"
elif [[ "$PY_GLOBAL" =~ $PY_LINE_RE ]] \
    && [ "$(printf '%s\n%s\n' "$PY_GLOBAL" "$PY_TARGET" | sort -V | head -1)" = "$PY_GLOBAL" ]; then
  if [ ! -d "$(pyenv root)/versions/$PY_GLOBAL" ]; then
    # Already uninstalled: every shell outside a pinned project gets "version
    # not installed", so moving it on is a repair with nothing to lose.
    pyenv global "$PY_TARGET"
    log "Python: pyenv global $PY_GLOBAL -> $PY_TARGET ($PY_GLOBAL isn't installed)"
  elif ! PY_GLOBAL_PKGS="$(gate_python --carry-over "$(pyenv root)/versions/$PY_GLOBAL")"; then
    notice_later "Python: pyenv global stays $PY_GLOBAL — couldn't list the packages installed into it, so switching could hide some. Check, then run 'pyenv global $PY_TARGET' yourself"
  elif [ -z "$PY_GLOBAL_PKGS" ]; then
    pyenv global "$PY_TARGET"
    log "Python: pyenv global $PY_GLOBAL -> $PY_TARGET (it held no packages of its own)"
  else
    notice_later "Python: pyenv global stays $PY_GLOBAL — it holds packages installed into it directly: $(printf '%s\n' "$PY_GLOBAL_PKGS" | paste -sd ',' - | sed 's/,/, /g'). Reinstall the ones you still use under $PY_TARGET (or with pipx), then run 'pyenv global $PY_TARGET'. Don't uninstall $PY_GLOBAL before that"
  fi
else
  log "Python: pyenv global is ${PY_GLOBAL:-unset} — not an older $PY_LINE patch, so left alone"
fi

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
nvm install "$NODE_LINE" --latest-npm
nvm alias default "$NODE_LINE" >/dev/null
NEW_NODE="$(nvm current)"
# Carry `sf` and other globals forward, only when the version changed. Passing
# --reinstall-packages-from=current to `nvm install` instead fails (exit 2) on a
# re-run where Node is already on the latest LTS.
if [ "$NEW_NODE" != "$OLD_NODE" ] && [ "${OLD_NODE#v}" != "$OLD_NODE" ]; then
  log "Node: reinstalling global packages from $OLD_NODE"
  nvm reinstall-packages "$OLD_NODE" \
    || fail_later "couldn't carry npm globals over from $OLD_NODE — reinstall them under $NEW_NODE by hand"
fi
log "Node: now on $NEW_NODE"

# ── 4. sf CLI ───────────────────────────────────────────────────────────────
# sf lives in nvm's npm globals, and `sf update` refuses npm-based installs
# ("not updatable") while still exiting 0, so update it through npm.
if [ -d "$(npm root -g)/@salesforce/cli" ]; then
  log "sf CLI: npm install -g @salesforce/cli@latest (was $(sf --version 2>/dev/null | head -1 | cut -d' ' -f1))"
  npm install -g @salesforce/cli@latest || fail_later "sf CLI update failed — try: npm install -g @salesforce/cli@latest"
  log "sf CLI: now $(sf --version 2>/dev/null | head -1 | cut -d' ' -f1)"
elif command -v sf >/dev/null 2>&1; then
  log "sf CLI: installer-based install at $(command -v sf) — sf update"
  sf update || fail_later "sf update failed"
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
log "pipx: refresh under Python $PY_TARGET"
"$PY_TARGET_BIN" -m pip install --user --upgrade pipx
"$PY_TARGET_BIN" -m pipx ensurepath >/dev/null 2>&1 || true

# Pin pipx invocation to the target Python so subsequent calls aren't subject
# to PATH ordering surprises or shebang breakage from previous patch installs.
# We never invoke bare `pipx` after this point, so no PATH check is needed —
# this works even from a minimal env where ~/.local/bin isn't yet on PATH.
PIPX=( "$PY_TARGET_BIN" -m pipx )

CCI_VENV="$("${PIPX[@]}" environment --value PIPX_LOCAL_VENVS)/cumulusci" \
  || die "couldn't resolve pipx's venv directory (pipx environment --value PIPX_LOCAL_VENVS)"

# The Python patch CCI's venv actually runs, or empty if it's missing or broken.
cci_python() {
  "$CCI_VENV/bin/python" -c 'import platform, ssl; print(platform.python_version())' 2>/dev/null || true
}

cci_reinstall() {
  log "CCI: reinstalling under Python $PY_TARGET"
  # `pipx reinstall` rebuilds the venv on the new interpreter and keeps injected
  # packages. `pipx install --force --python` doesn't: pipx 1.17 ignores --python
  # with --force and rebuilds the venv in place, still linked to the old patch.
  # Test the venv directory, not `pipx list`: that exits 1 when any venv is
  # broken, and omits a venv whose interpreter is gone, which is this case.
  if [ -d "$CCI_VENV" ]; then
    "${PIPX[@]}" reinstall cumulusci --python "$PY_TARGET_BIN"
  else
    "${PIPX[@]}" install cumulusci --python "$PY_TARGET_BIN"
  fi
  [ "$(cci_python)" = "$PY_TARGET" ] \
    || die "CCI's venv isn't running Python $PY_TARGET after the reinstall — see docs/guides/dev-environment-setup.md (pipx venv broken after Python patch bump)"
}

# Decide on the venv's real interpreter, not on whether this run bumped Python,
# so a re-run after a failed reinstall repairs it.
if [ "$PY_UPGRADED" -eq 1 ] || [ "$(cci_python)" != "$PY_TARGET" ]; then
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

# CCI 4.10.1 declares selenium<4 and SeleniumLibrary<6. `pipx upgrade` above
# re-resolves CCI without its injected packages, so it moves them down (selenium
# 3.141.0); a reinstall re-injects what was injected before. That pin is for CCI's
# own Salesforce Robot library, which this repo doesn't use. The repo's suites
# need selenium 4 (they build drivers with Service), and selenium 3 fails under
# urllib3 2. CI's build already runs CCI 4.10.1 with robot/requirements.txt.
# Re-apply those pins here: validate_setup floor-checks only selenium, so a
# SeleniumLibrary left on 5.x would pass it silently.
log "CCI: re-applying robot/requirements.txt"
"${PIPX[@]}" inject --force cumulusci -r "$REPO_ROOT/robot/requirements.txt" \
  || fail_later "couldn't inject robot/requirements.txt — run: pipx inject --force cumulusci -r robot/requirements.txt (validate_setup only flags selenium below 4.10)"

# ── 6. sf plugins ───────────────────────────────────────────────────────────
log "sf plugins: update"
sf plugins update || fail_later "sf plugins update failed"

# Rebuild a venv on pyenv's $PY_TARGET when it runs another Python, or one not
# built from pyenv's directory, carrying the packages it holds over. Both the
# patch and the base matter: a venv on Homebrew's python@3.13 passes a patch
# check while the two happen to match, then breaks or drifts when they don't.
# pyvenv.cfg's `home` names the base; resolved directories are compared so a
# symlinked PYENV_ROOT still matches. LABEL starts every message.
PY_TARGET_BASE="$(cd "$(dirname "$PY_TARGET_BIN")" && pwd -P)"
venv_home() { sed -n 's/^home *= *//p' "$1/pyvenv.cfg" 2>/dev/null | head -1 || true; }
venv_base() {
  local home
  home="$(venv_home "$1")"
  if [ -n "$home" ]; then (cd "$home" 2>/dev/null && pwd -P) || true; fi
}
refresh_venv() {
  local venv="$1" label="$2" version home keep lost="" req rebuild=1
  version="$("$venv/bin/python" -c 'import platform; print(platform.python_version())' 2>/dev/null || true)"
  home="$(venv_home "$venv")"
  if [ "$version" = "$PY_TARGET" ] && [ "$(venv_base "$venv")" = "$PY_TARGET_BASE" ]; then
    return 0
  fi
  # Clearing a venv under a running process (a ./tui-cci session in another
  # worktree, a gate run) breaks that process's next import. Leave it. This sees
  # processes started by the venv's path, which is how tui-cci and the gate
  # start theirs; one started from an activated shell as plain `python` isn't.
  # pgrep takes a regex: escape the path so `(`, `+`, `[` … in it match literally.
  if pgrep -f -- "$(printf '%s' "$venv/bin/" | sed 's/[][\\.*^$+?(){}|]/\\&/g')" >/dev/null 2>&1; then
    fail_later "$label: $venv needs a rebuild onto Python $PY_TARGET (it's on ${version:-an unusable Python}), but a process is running from it — left; rerun once it has exited"
    return 0
  fi
  # --clear empties the whole venv, so list what it holds first.
  keep="$(mktemp "${TMPDIR:-/tmp}/venv-packages.XXXXXX")"
  if ! gate_python --carry-over "$venv" >"$keep"; then
    if [ -n "$version" ]; then
      # It still runs, so clearing it would destroy what can't be listed for
      # nothing. Leave it on its old patch.
      fail_later "$label: couldn't list the packages in $venv — left on Python $version from ${home:-an unknown base} instead of rebuilding it; rerun once the cause is fixed"
      rebuild=0
    else
      fail_later "$label: couldn't list the packages in $venv, and its Python is gone — rebuilt without them; reinstall any you need"
    fi
  fi
  if [ "$rebuild" -eq 1 ]; then
    log "$label: rebuilding $venv on pyenv's Python $PY_TARGET (was ${version:-unusable} from ${home:-an unknown base})"
    "$PY_TARGET_BIN" -m venv --clear "$venv"
    # If the new venv still doesn't record pyenv's directory (a framework build
    # can name Python.framework instead), say so rather than rebuild every run.
    [ "$(venv_base "$venv")" = "$PY_TARGET_BASE" ] \
      || fail_later "$label: rebuilt $venv, but its pyvenv.cfg home ($(venv_home "$venv")) still isn't $PY_TARGET_BASE, so every run will rebuild it; see docs/guides/dev-environment-setup.md (Troubleshooting)"
    if [ -s "$keep" ]; then
      log "$label: reinstalling the $(wc -l <"$keep" | tr -d ' ') package(s) it held"
      # All at once first. pip resolves a requirements file all-or-nothing,
      # so on failure go one at a time, retrying a pin that won't install on
      # this Python unpinned, and lose only what really can't come back.
      if ! "$venv/bin/python" -m pip install -r "$keep"; then
        # fd 3, so a pip that reads stdin can't swallow the rest of the list.
        while IFS= read -r req <&3; do
          case "$req" in
            "") continue ;;
            "-e "*) "$venv/bin/python" -m pip install -e "${req#-e }" && continue ;;
            *) "$venv/bin/python" -m pip install "$req" && continue
               case "$req" in
                 *==*) "$venv/bin/python" -m pip install "${req%%==*}" && continue ;;
               esac ;;
          esac
          lost="${lost:+$lost, }$req"
        done 3<"$keep"
        [ -z "$lost" ] \
          || fail_later "$label: these didn't come back: $lost (full list: $keep)"
      fi
    fi
  fi
  [ -n "$lost" ] || rm -f "$keep"
}

# ── 7. Gate interpreter (<main checkout>/.venv) ─────────────────────────────
# scripts/ai/pr_gate.py, the loop Stop hook and validate_setup's "Gate
# interpreter" check all run under <main checkout>/.venv. gate_python.py
# resolves and probes it for every one of them, so this step asks it too
# rather than restating where the venv lives. Like the pipx venv, its python
# is a symlink into one pyenv patch dir, so it's rebuilt when it isn't on
# $PY_TARGET (this also covers a symlink broken by an uninstalled patch). Then
# pr_gate.py's requirements are reinstalled, which picks up any DEPS change. Only
# an existing venv is managed: creating it is a setup step (local-installation.md,
# Step 6). A $RLM_GATE_PYTHON override is someone else's to manage, but it is
# still probed. Whichever venv is the gate interpreter must end up usable:
# validate_setup only warns about it, so a failure here fails the script
# (after validate_setup has run) instead of ending in "Done".
GATE_FAILED=""
if [ -n "${RLM_GATE_PYTHON:-}" ]; then
  log "Gate interpreter: \$RLM_GATE_PYTHON is set ($RLM_GATE_PYTHON) — probing it, not managing it"
  gate_python >/dev/null || GATE_FAILED="\$RLM_GATE_PYTHON ($RLM_GATE_PYTHON) can't run every pr_gate.py check"
elif ! GATE_VENV="$(gate_python --default-venv)"; then
  warn "Gate interpreter: $REPO_ROOT is not a git checkout — skipping"
elif [ -d "$GATE_VENV" ]; then
  refresh_venv "$GATE_VENV" "Gate interpreter"
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

# ── 8. Build-harness TUI venvs (<checkout>/.harness/tui-venv) ───────────────
# ./tui-cci creates its venv once and never rebuilds it, so it stays on the
# Python patch it was made with, and uninstalling that patch breaks it (tui-cci
# then misreports it as "Python < 3.11"). Each checkout of this repository,
# main or worktree, has its own, so every one gets the gate venv's treatment.
# tui-cci reinstalls its own requirements on its next run if any are missing.
TUI_SEEN=0
while IFS= read -r wt <&4; do
  [ -d "$wt/.harness/tui-venv" ] || continue
  TUI_SEEN=$((TUI_SEEN + 1))
  refresh_venv "$wt/.harness/tui-venv" "TUI venv"
done 4< <(git -C "$REPO_ROOT" worktree list --porcelain 2>/dev/null | sed -n 's/^worktree //p')
log "TUI venv: $TUI_SEEN found, each on pyenv's Python $PY_TARGET unless a warning above says otherwise"

# ── 9. Verify ───────────────────────────────────────────────────────────────
log "Running validate_setup"
cci task run validate_setup || fail_later "validate_setup failed (output above)"

[ -z "$GATE_FAILED" ] || STEP_FAILED+=("Gate interpreter: $GATE_FAILED, so the local gate (scripts/ai/pr_gate.py) can't run all its checks")
# Count first: expanding an empty array trips `set -u` on bash 3.2 (macOS /bin/bash).
if [ "${#NOTICES[@]}" -gt 0 ]; then
  for msg in "${NOTICES[@]}"; do warn "$msg"; done
fi
if [ "${#STEP_FAILED[@]}" -gt 0 ]; then
  for msg in "${STEP_FAILED[@]}"; do warn "$msg"; done
  die "${#STEP_FAILED[@]} step(s) failed (listed above)"
fi
log "Done."
