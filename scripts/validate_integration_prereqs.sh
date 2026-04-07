#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# validate_integration_prereqs.sh
#
# Validates that the local workstation has the tools required to set up and
# run Distill and Aegis alongside Revenue Cloud Foundations.
#
# Scope: This script checks prerequisites for the INTEGRATION workspace only.
# It does NOT check CCI, SF CLI, SFDMU, or Robot Framework — those are
# validated by `cci task run validate_setup` inside Foundations.
#
# Usage:
#   ./scripts/validate_integration_prereqs.sh            # validate prerequisites
#   ./scripts/validate_integration_prereqs.sh --scan      # inventory-only (no pass/fail)
#   ./scripts/validate_integration_prereqs.sh --fix       # validate + auto-install missing
#
# Modes:
#   (default)  Check prerequisites, report PASS/WARN/FAIL, detect conflicts
#   --scan     Inventory existing installs and detect conflicts only (no failures)
#   --fix      Same as default but attempt to auto-install missing tools
#
# Exit codes:
#   0  All required checks passed (or --scan mode)
#   1  One or more required checks failed
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

# ── colours (disabled when not a tty) ─────────────────────────────────────────
if [ -t 1 ]; then
  GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'
  CYAN='\033[0;36m'; BOLD='\033[1m'; DIM='\033[2m'; NC='\033[0m'
else
  GREEN=''; YELLOW=''; RED=''; CYAN=''; BOLD=''; DIM=''; NC=''
fi

PASS="${GREEN}PASS${NC}"
WARN="${YELLOW}WARN${NC}"
FAIL="${RED}FAIL${NC}"
INFO="${CYAN}INFO${NC}"
CONFLICT="${RED}CONFLICT${NC}"
SKIP="${DIM}SKIP${NC}"

# ── mode parsing ──────────────────────────────────────────────────────────────
MODE="validate"  # validate | scan | fix
case "${1:-}" in
  --scan) MODE="scan";;
  --fix)  MODE="fix";;
  "")     MODE="validate";;
  *)      echo "Usage: $0 [--scan | --fix]"; exit 2;;
esac

REQUIRED_FAILURES=0
WARN_COUNT=0
CONFLICT_COUNT=0
SKIP_COUNT=0

# ── helper functions ──────────────────────────────────────────────────────────

log_pass()     { printf "  [${PASS}]      %s\n" "$1"; }
log_warn()     { printf "  [${WARN}]      %s\n" "$1"; WARN_COUNT=$((WARN_COUNT + 1)); }
log_fail()     { printf "  [${FAIL}]      %s\n" "$1"; REQUIRED_FAILURES=$((REQUIRED_FAILURES + 1)); }
log_info()     { printf "  [${INFO}]      %s\n" "$1"; }
log_conflict() { printf "  [${CONFLICT}]  %s\n" "$1"; CONFLICT_COUNT=$((CONFLICT_COUNT + 1)); }
log_skip()     { printf "  [${SKIP}]      %s\n" "$1"; SKIP_COUNT=$((SKIP_COUNT + 1)); }
log_detail()   { printf "               %s\n" "$1"; }

section() {
  echo ""
  printf "${BOLD}${CYAN}── %s ──${NC}\n" "$1"
}

command_exists() { command -v "$1" &>/dev/null; }

version_major_minor() {
  echo "$1" | sed 's/^v//' | awk -F. '{print $1"."$2}'
}

version_major() {
  echo "$1" | sed 's/^v//' | cut -d. -f1
}

# ── macOS vs Linux detection ──────────────────────────────────────────────────
OS="$(uname -s)"
case "$OS" in
  Darwin) PKG_HINT="brew install";;
  Linux)  PKG_HINT="apt install";;
  *)      PKG_HINT="(install via your package manager)";;
esac

# ── workspace detection ───────────────────────────────────────────────────────
RC_WORKSPACE="${RC_WORKSPACE:-}"

# ─────────────────────────────────────────────────────────────────────────────
echo ""
printf "${BOLD}Integration Prerequisites Validator${NC}\n"
if [[ "$MODE" == "scan" ]]; then
  printf "Mode: ${CYAN}SCAN${NC} — inventory existing installs and detect conflicts.\n"
elif [[ "$MODE" == "fix" ]]; then
  printf "Mode: ${CYAN}FIX${NC} — validate + auto-install missing tools.\n"
else
  printf "Mode: ${CYAN}VALIDATE${NC} — check prerequisites + detect conflicts.\n"
fi
printf "Scope: Distill + Aegis toolchain only.\n"
printf "Does NOT check CCI/SF CLI/SFDMU/Robot — run 'cci task run validate_setup' for those.\n"

# ══════════════════════════════════════════════════════════════════════════════
section "1. Existing Installation Scan"
# ══════════════════════════════════════════════════════════════════════════════

# Collect everything we find so later sections can make informed decisions.

# ── All Python installations ──────────────────────────────────────────────────
declare -a PYTHON_INSTALLS=()
SYSTEM_PYTHON=""
SYSTEM_PYTHON_VER=""
BREW_PYTHON=""
BREW_PYTHON_VER=""
PYENV_PYTHONS=()

if command_exists python3; then
  SYSTEM_PYTHON=$(command -v python3)
  SYSTEM_PYTHON_VER=$(python3 --version 2>&1 | awk '{print $2}')
  PYTHON_INSTALLS+=("system:${SYSTEM_PYTHON}:${SYSTEM_PYTHON_VER}")
  log_info "System python3: ${SYSTEM_PYTHON_VER} (${SYSTEM_PYTHON})"
fi

if [[ "$OS" == "Darwin" ]] && command_exists brew; then
  BREW_PY=$(brew --prefix python@3 2>/dev/null || true)
  if [[ -n "$BREW_PY" && -x "${BREW_PY}/bin/python3" ]]; then
    BREW_PYTHON="${BREW_PY}/bin/python3"
    BREW_PYTHON_VER=$("$BREW_PYTHON" --version 2>&1 | awk '{print $2}')
    if [[ "$BREW_PYTHON" != "$SYSTEM_PYTHON" ]]; then
      PYTHON_INSTALLS+=("brew:${BREW_PYTHON}:${BREW_PYTHON_VER}")
      log_info "Homebrew python3: ${BREW_PYTHON_VER} (${BREW_PYTHON})"
    fi
  fi
  for minor in 10 11 12 13 14; do
    BREW_PY_X=$(brew --prefix "python@3.${minor}" 2>/dev/null || true)
    if [[ -n "$BREW_PY_X" && -x "${BREW_PY_X}/bin/python3.${minor}" ]]; then
      PY_X_VER=$("${BREW_PY_X}/bin/python3.${minor}" --version 2>&1 | awk '{print $2}')
      PYTHON_INSTALLS+=("brew-3.${minor}:${BREW_PY_X}/bin/python3.${minor}:${PY_X_VER}")
      log_info "Homebrew python@3.${minor}: ${PY_X_VER}"
    fi
  done
fi

PYENV_OK=false
if command_exists pyenv; then
  PYENV_OK=true
  while IFS= read -r ver; do
    [[ -z "$ver" ]] && continue
    PYENV_PYTHONS+=("$ver")
    PYTHON_INSTALLS+=("pyenv:pyenv:${ver}")
  done < <(pyenv versions --bare 2>/dev/null || true)
  if [[ ${#PYENV_PYTHONS[@]} -gt 0 ]]; then
    log_info "pyenv versions: ${PYENV_PYTHONS[*]}"
  else
    log_info "pyenv installed but no versions found"
  fi
fi

log_info "Total Python installations found: ${#PYTHON_INSTALLS[@]}"

# ── Node.js installations ────────────────────────────────────────────────────
SYSTEM_NODE=""
SYSTEM_NODE_VER=""
NVM_OK=false
NVM_NODES=()

export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
if [[ -s "$NVM_DIR/nvm.sh" ]]; then
  source "$NVM_DIR/nvm.sh" 2>/dev/null || true
fi

if command_exists nvm 2>/dev/null || type nvm &>/dev/null; then
  NVM_OK=true
  NVM_VER=$(nvm --version 2>/dev/null || echo "unknown")
  log_info "nvm: ${NVM_VER}"
  while IFS= read -r ver; do
    ver=$(echo "$ver" | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//' | sed 's/ .*//')
    [[ -z "$ver" || "$ver" == "system" || "$ver" == "->" ]] && continue
    NVM_NODES+=("$ver")
  done < <(nvm ls --no-colors 2>/dev/null | grep -E "v[0-9]" | sed 's/.*\(v[0-9][0-9.]*\).*/\1/' || true)
  if [[ ${#NVM_NODES[@]} -gt 0 ]]; then
    log_info "nvm Node versions: ${NVM_NODES[*]}"
  fi
fi

if command_exists node; then
  SYSTEM_NODE=$(command -v node)
  SYSTEM_NODE_VER=$(node --version 2>/dev/null)
  log_info "Active Node.js: ${SYSTEM_NODE_VER} (${SYSTEM_NODE})"
fi

# ── Existing workspace / venvs / clones ───────────────────────────────────────
if [[ -n "$RC_WORKSPACE" ]]; then
  log_info "RC_WORKSPACE: ${RC_WORKSPACE}"

  for repo_dir in "foundations" "distill" "aegis"; do
    target="${RC_WORKSPACE}/${repo_dir}"
    if [[ -d "$target/.git" ]]; then
      REPO_BRANCH=$(git -C "$target" branch --show-current 2>/dev/null || echo "detached")
      log_info "  ${repo_dir}/ already cloned (branch: ${REPO_BRANCH})"
    elif [[ -d "$target" ]]; then
      log_info "  ${repo_dir}/ directory exists but is not a git repo"
    fi

    # Check for existing venvs
    for venv_name in ".venv" "venv" ".env"; do
      if [[ -d "${target}/${venv_name}" ]]; then
        VENV_PY=$("${target}/${venv_name}/bin/python3" --version 2>&1 | awk '{print $2}' || echo "unknown")
        log_info "  ${repo_dir}/${venv_name}/ exists (Python ${VENV_PY})"
      fi
    done

    # Check for .python-version
    if [[ -f "${target}/.python-version" ]]; then
      PV_CONTENT=$(cat "${target}/.python-version" 2>/dev/null)
      log_info "  ${repo_dir}/.python-version = ${PV_CONTENT}"
    fi
  done
else
  log_info "RC_WORKSPACE not set — workspace scan skipped"
  log_detail "Set RC_WORKSPACE to scan existing clones/venvs"
fi

# ══════════════════════════════════════════════════════════════════════════════
section "2. Conflict Detection"
# ══════════════════════════════════════════════════════════════════════════════

# ── Python version conflicts ──────────────────────────────────────────────────

# Conflict: system Python is 3.13+ but no pyenv 3.12 → Distill will fail
if [[ -n "$SYSTEM_PYTHON_VER" ]]; then
  SYS_MINOR=$(echo "$SYSTEM_PYTHON_VER" | cut -d. -f2)
  if [[ "$SYS_MINOR" -ge 13 ]]; then
    HAS_312=false
    for pv in "${PYENV_PYTHONS[@]+"${PYENV_PYTHONS[@]}"}"; do
      if [[ "$pv" == 3.12.* ]]; then HAS_312=true; break; fi
    done
    if ! $HAS_312 && ! $PYENV_OK; then
      log_conflict "System Python is ${SYSTEM_PYTHON_VER} (3.13+) — incompatible with Distill"
      log_detail "Distill requires 3.10-3.12. pyenv is not installed."
      log_detail "Fix: Install pyenv, then: pyenv install 3.12"
    elif ! $HAS_312 && $PYENV_OK; then
      log_conflict "System Python is ${SYSTEM_PYTHON_VER} (3.13+) and pyenv has no 3.12.x"
      log_detail "Fix: pyenv install 3.12"
    else
      log_pass "System Python ${SYSTEM_PYTHON_VER} (3.13+) — pyenv 3.12 available for Distill"
    fi
  elif [[ "$SYS_MINOR" -ge 10 && "$SYS_MINOR" -le 12 ]]; then
    log_pass "System Python ${SYSTEM_PYTHON_VER} is directly compatible with Distill"
    if $PYENV_OK; then
      log_detail "pyenv is available for future-proofing if system Python upgrades"
    fi
  else
    log_conflict "System Python ${SYSTEM_PYTHON_VER} is too old for Distill (needs 3.10+)"
    log_detail "Fix: pyenv install 3.12"
  fi
fi

# Conflict: Homebrew Python shadows pyenv
if [[ -n "$BREW_PYTHON" ]] && $PYENV_OK; then
  if [[ "$SYSTEM_PYTHON" == *"Cellar"* || "$SYSTEM_PYTHON" == *"Homebrew"* ]]; then
    log_warn "Homebrew Python may shadow pyenv in PATH"
    log_detail "Current python3 resolves to: ${SYSTEM_PYTHON}"
    log_detail "Ensure pyenv shims come first: check 'eval \"\$(pyenv init -)\"' in shell profile"
    log_detail "Verify with: which python3  (should show ~/.pyenv/shims/python3)"
  else
    log_pass "pyenv shims take priority over Homebrew Python"
  fi
elif [[ -n "$BREW_PYTHON" ]] && ! $PYENV_OK; then
  log_info "Homebrew Python found without pyenv — will use Homebrew Python directly"
fi

# Conflict: existing venv was built with wrong Python
if [[ -n "$RC_WORKSPACE" ]]; then
  for check in "distill:.venv:3.12" "aegis:venv:3.12"; do
    IFS=: read -r repo_name venv_name expected_minor <<< "$check"
    VENV_BIN="${RC_WORKSPACE}/${repo_name}/${venv_name}/bin/python3"
    if [[ -x "$VENV_BIN" ]]; then
      VENV_VER=$("$VENV_BIN" --version 2>&1 | awk '{print $2}')
      VENV_MINOR=$(echo "$VENV_VER" | cut -d. -f2)
      if [[ "$VENV_MINOR" != "$expected_minor" ]]; then
        log_conflict "${repo_name}/${venv_name}/ was created with Python ${VENV_VER} (expected 3.${expected_minor}.x)"
        log_detail "Fix: rm -rf \"${RC_WORKSPACE}/${repo_name}/${venv_name}\" and recreate with Python 3.${expected_minor}"
      else
        log_pass "${repo_name}/${venv_name}/ uses Python ${VENV_VER}"
      fi
    fi
  done

  # Conflict: .python-version points to a version not installed in pyenv
  if $PYENV_OK; then
    for repo_name in "distill" "aegis"; do
      PV_FILE="${RC_WORKSPACE}/${repo_name}/.python-version"
      if [[ -f "$PV_FILE" ]]; then
        PV_WANT=$(cat "$PV_FILE")
        PV_MATCH=$(pyenv versions --bare 2>/dev/null | grep -E "^${PV_WANT}" | head -1 || true)
        if [[ -z "$PV_MATCH" ]]; then
          log_conflict "${repo_name}/.python-version requests ${PV_WANT} but it's not installed in pyenv"
          log_detail "Fix: pyenv install ${PV_WANT}"
        else
          log_pass "${repo_name}/.python-version → ${PV_WANT} (resolved to ${PV_MATCH})"
        fi
      fi
    done
  fi

  # Conflict: Foundations has a .python-version (could interfere with CCI/pipx)
  if [[ -f "${RC_WORKSPACE}/foundations/.python-version" ]]; then
    log_conflict "foundations/.python-version exists — may interfere with CCI/pipx"
    log_detail "CCI manages its own Python. Remove: rm \"${RC_WORKSPACE}/foundations/.python-version\""
  fi
fi

# Conflict: nvm Node vs Homebrew Node
if $NVM_OK && [[ "$OS" == "Darwin" ]] && command_exists brew; then
  BREW_NODE=$(brew --prefix node 2>/dev/null || true)
  if [[ -n "$BREW_NODE" && -x "${BREW_NODE}/bin/node" ]]; then
    BREW_NODE_VER=$("${BREW_NODE}/bin/node" --version 2>/dev/null || echo "unknown")
    if [[ -n "$SYSTEM_NODE" && "$SYSTEM_NODE" == *"Cellar"* ]]; then
      log_warn "Homebrew Node.js ${BREW_NODE_VER} may shadow nvm in PATH"
      log_detail "Active node: ${SYSTEM_NODE}"
      log_detail "Fix: brew unlink node   (then rely on nvm exclusively)"
      log_detail "  or: ensure nvm sourcing comes after Homebrew in shell profile"
    else
      log_pass "nvm Node.js takes priority over Homebrew Node.js"
    fi
  fi
fi

# Info: pipx Python vs pyenv — not a conflict unless the version is uninstalled
if command_exists pipx; then
  PIPX_PY=$(pipx environment 2>/dev/null | grep "PIPX_DEFAULT_PYTHON" | awk -F= '{print $2}' | tr -d ' ' || true)
  if [[ -n "$PIPX_PY" ]]; then
    if [[ "$PIPX_PY" == *".pyenv"* ]]; then
      PIPX_PY_VER=$(echo "$PIPX_PY" | grep -oE '3\.[0-9]+\.[0-9]+' || echo "unknown")
      log_info "pipx is using pyenv Python ${PIPX_PY_VER}"
      log_detail "This is normal. Keep this version installed to avoid breaking CCI."
      log_detail "Changing pyenv global does NOT break pipx — only pyenv uninstall would."
    else
      log_pass "pipx uses non-pyenv Python: ${PIPX_PY}"
    fi
  fi
fi

if [[ $CONFLICT_COUNT -eq 0 ]]; then
  log_pass "No conflicts detected"
fi

# In scan mode, stop here — no pass/fail validation needed
if [[ "$MODE" == "scan" ]]; then
  echo ""
  printf "${BOLD}── Scan Complete ──${NC}\n"
  printf "  Found ${#PYTHON_INSTALLS[@]} Python installation(s), "
  if $NVM_OK; then
    printf "${#NVM_NODES[@]} nvm Node version(s)"
  elif [[ -n "$SYSTEM_NODE_VER" ]]; then
    printf "1 Node installation"
  else
    printf "0 Node installations"
  fi
  echo ""
  if [[ $CONFLICT_COUNT -gt 0 ]]; then
    printf "  ${RED}${CONFLICT_COUNT} conflict(s) detected — resolve before proceeding.${NC}\n"
  else
    printf "  ${GREEN}No conflicts.${NC}\n"
  fi
  printf "\n  Run without --scan to validate all prerequisites.\n"
  printf "  Run with --fix to auto-install missing tools.\n\n"
  exit 0
fi

# ══════════════════════════════════════════════════════════════════════════════
section "3. System-Level Tools"
# ══════════════════════════════════════════════════════════════════════════════

# ── git ───────────────────────────────────────────────────────────────────────
if command_exists git; then
  GIT_VER=$(git --version | awk '{print $3}')
  log_pass "git ${GIT_VER}"
else
  log_fail "git not found"
  log_detail "Fix: ${PKG_HINT} git"
fi

# ── Homebrew (macOS only) ─────────────────────────────────────────────────────
if [[ "$OS" == "Darwin" ]]; then
  if command_exists brew; then
    log_pass "Homebrew $(brew --version 2>/dev/null | head -1 | awk '{print $2}')"
  else
    log_warn "Homebrew not found — recommended for installing tools on macOS"
    log_detail "Fix: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
  fi
fi

# ══════════════════════════════════════════════════════════════════════════════
section "4. Python Version Management (pyenv)"
# ══════════════════════════════════════════════════════════════════════════════

if $PYENV_OK; then
  PYENV_VER=$(pyenv --version | awk '{print $2}')
  log_skip "pyenv ${PYENV_VER} — already installed"
else
  log_fail "pyenv not found — required to manage Python 3.12 (Distill) alongside 3.13+ (Foundations)"
  if [[ "$OS" == "Darwin" ]]; then
    log_detail "Fix: brew install pyenv"
    log_detail "Then add to your shell profile (~/.zshrc or ~/.bashrc):"
  else
    log_detail "Fix: curl https://pyenv.run | bash"
    log_detail "Then add to ~/.bashrc:"
  fi
  log_detail '  export PYENV_ROOT="$HOME/.pyenv"'
  log_detail '  [[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"'
  log_detail '  eval "$(pyenv init -)"'
  log_detail "Then restart your shell and re-run this script."
  if [[ "$MODE" == "fix" ]] && [[ "$OS" == "Darwin" ]] && command_exists brew; then
    echo ""
    log_detail "Attempting auto-install: brew install pyenv ..."
    brew install pyenv 2>/dev/null && {
      eval "$(pyenv init - 2>/dev/null)" || true
      log_pass "pyenv installed (restart shell to complete setup)"
      PYENV_OK=true
      REQUIRED_FAILURES=$((REQUIRED_FAILURES - 1))
    } || log_detail "Auto-install failed — install manually."
  fi
fi

# ── Python 3.12 (for Distill + Aegis) ────────────────────────────────────────
PY312_OK=false
if $PYENV_OK; then
  PY312_INSTALLED=$(pyenv versions --bare 2>/dev/null | grep -E "^3\.12\." | tail -1 || true)
  if [[ -n "$PY312_INSTALLED" ]]; then
    log_skip "Python ${PY312_INSTALLED} — already available via pyenv"
    PY312_OK=true
  else
    log_fail "Python 3.12.x not installed in pyenv — required by Distill"
    log_detail "Fix: pyenv install 3.12"
    if [[ "$MODE" == "fix" ]]; then
      echo ""
      log_detail "Attempting auto-install: pyenv install 3.12 ..."
      pyenv install 3.12 2>/dev/null && {
        PY312_INSTALLED=$(pyenv versions --bare 2>/dev/null | grep -E "^3\.12\." | tail -1 || true)
        log_pass "Python ${PY312_INSTALLED} installed"
        PY312_OK=true
        REQUIRED_FAILURES=$((REQUIRED_FAILURES - 1))
      } || log_detail "Auto-install failed — install manually with: pyenv install 3.12"
    fi
  fi
else
  if [[ -n "$SYSTEM_PYTHON_VER" ]]; then
    SYS_PY_MINOR=$(echo "$SYSTEM_PYTHON_VER" | cut -d. -f2)
    if [[ "$SYS_PY_MINOR" -ge 10 && "$SYS_PY_MINOR" -le 12 ]]; then
      log_warn "System Python ${SYSTEM_PYTHON_VER} is compatible with Distill but pyenv is recommended"
      log_detail "Without pyenv, upgrading Python globally could break Distill."
      PY312_OK=true
      REQUIRED_FAILURES=$((REQUIRED_FAILURES > 0 ? REQUIRED_FAILURES - 1 : 0))
    else
      log_fail "System Python is ${SYSTEM_PYTHON_VER} — Distill requires 3.10-3.12"
      log_detail "Fix: Install pyenv first (see above), then: pyenv install 3.12"
    fi
  else
    log_fail "No python3 found"
    log_detail "Fix: Install pyenv first (see above), then: pyenv install 3.12"
  fi
fi

# ── Python 3.13+ check (informational — for Foundations/CCI) ──────────────────
if $PYENV_OK; then
  PY313_INSTALLED=$(pyenv versions --bare 2>/dev/null | grep -E "^3\.1[3-9]\." | tail -1 || true)
  if [[ -n "$PY313_INSTALLED" ]]; then
    log_pass "Python ${PY313_INSTALLED} also available (for Foundations/CCI)"
  else
    if [[ -n "$SYSTEM_PYTHON_VER" ]]; then
      SYS_PY_MINOR=$(echo "$SYSTEM_PYTHON_VER" | cut -d. -f2)
      if [[ "$SYS_PY_MINOR" -ge 13 ]]; then
        log_pass "System Python ${SYSTEM_PYTHON_VER} available for Foundations/CCI (outside pyenv)"
      else
        log_warn "Python 3.13+ not found — Foundations/CCI may need it if pipx expects it"
        log_detail "Optional: pyenv install 3.13  (only if CCI needs it)"
      fi
    else
      log_warn "Python 3.13+ not in pyenv — Foundations/CCI may use system Python instead"
      log_detail "Optional: pyenv install 3.13  (only if CCI needs it)"
    fi
  fi
fi

# ══════════════════════════════════════════════════════════════════════════════
section "5. Node.js Version Management (nvm)"
# ══════════════════════════════════════════════════════════════════════════════

if $NVM_OK; then
  NVM_VER=$(nvm --version 2>/dev/null || echo "unknown")
  log_skip "nvm ${NVM_VER} — already installed"
else
  log_warn "nvm not found — recommended for managing Node.js versions"
  log_detail "Node.js is needed for Foundations only (sf CLI + SFDMU plugin)."
  log_detail "Fix: brew install nvm   (macOS)"
  log_detail "     or: curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash"
  log_detail "Then add to your shell profile and restart."
fi

# ── Node.js ───────────────────────────────────────────────────────────────────
if command_exists node; then
  NODE_VER=$(node --version 2>/dev/null)
  NODE_MAJOR=$(echo "$NODE_VER" | sed 's/^v//' | cut -d. -f1)
  if [[ "$NODE_MAJOR" -ge 18 ]]; then
    log_skip "Node.js ${NODE_VER} — already installed (required by Foundations for sf CLI)"
  else
    log_warn "Node.js ${NODE_VER} is old — LTS (18+) recommended"
    log_detail "Fix: nvm install --lts && nvm use --lts"
  fi
else
  log_warn "Node.js not found — required by Foundations for sf CLI + SFDMU"
  log_detail "Fix: nvm install --lts   (if nvm is installed)"
  log_detail "     or: ${PKG_HINT} node"
fi

# ══════════════════════════════════════════════════════════════════════════════
section "6. Distill-Specific Tools"
# ══════════════════════════════════════════════════════════════════════════════

# ── Google Cloud CLI ──────────────────────────────────────────────────────────
if command_exists gcloud; then
  GCLOUD_VER=$(gcloud --version 2>/dev/null | head -1 | awk '{print $NF}')
  log_skip "Google Cloud CLI ${GCLOUD_VER} — already installed"

  # Check if authenticated
  GCLOUD_ACCOUNT=$(gcloud config get-value account 2>/dev/null || true)
  if [[ -n "$GCLOUD_ACCOUNT" && "$GCLOUD_ACCOUNT" != "(unset)" ]]; then
    log_pass "gcloud authenticated as: ${GCLOUD_ACCOUNT}"
  else
    log_warn "gcloud installed but not authenticated"
    log_detail "Fix: gcloud auth login"
  fi
else
  log_fail "gcloud not found — required by Distill for Vertex AI fallback"
  if [[ "$OS" == "Darwin" ]]; then
    log_detail "Fix: brew install google-cloud-sdk"
  else
    log_detail "Fix: https://cloud.google.com/sdk/docs/install"
  fi
  if [[ "$MODE" == "fix" ]] && [[ "$OS" == "Darwin" ]] && command_exists brew; then
    echo ""
    log_detail "Attempting auto-install: brew install google-cloud-sdk ..."
    brew install google-cloud-sdk 2>/dev/null && {
      log_pass "gcloud installed"
      REQUIRED_FAILURES=$((REQUIRED_FAILURES - 1))
    } || log_detail "Auto-install failed — install manually."
  fi
fi

# ── cmake ─────────────────────────────────────────────────────────────────────
if command_exists cmake; then
  CMAKE_VER=$(cmake --version 2>/dev/null | head -1 | awk '{print $3}')
  log_skip "cmake ${CMAKE_VER} — already installed"
else
  log_fail "cmake not found — required by Distill (sentence-transformers build)"
  log_detail "Fix: ${PKG_HINT} cmake"
  if [[ "$MODE" == "fix" ]] && [[ "$OS" == "Darwin" ]] && command_exists brew; then
    echo ""
    log_detail "Attempting auto-install: brew install cmake ..."
    brew install cmake 2>/dev/null && {
      log_pass "cmake installed"
      REQUIRED_FAILURES=$((REQUIRED_FAILURES - 1))
    } || log_detail "Auto-install failed — install manually."
  fi
fi

# ══════════════════════════════════════════════════════════════════════════════
section "7. Aegis-Specific Tools"
# ══════════════════════════════════════════════════════════════════════════════

# ── Chrome / Chromium ─────────────────────────────────────────────────────────
CHROME_FOUND=false
if [[ "$OS" == "Darwin" ]]; then
  if [[ -d "/Applications/Google Chrome.app" ]]; then
    CHROME_VER=$("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --version 2>/dev/null | awk '{print $NF}' || echo "unknown")
    log_skip "Google Chrome ${CHROME_VER} — already installed"
    CHROME_FOUND=true
  elif [[ -d "/Applications/Chromium.app" ]]; then
    log_skip "Chromium — already installed"
    CHROME_FOUND=true
  fi
else
  if command_exists google-chrome || command_exists chromium-browser || command_exists chromium; then
    CHROME_FOUND=true
    CHROME_CMD=$(command -v google-chrome || command -v chromium-browser || command -v chromium)
    CHROME_VER=$($CHROME_CMD --version 2>/dev/null | awk '{print $NF}' || echo "unknown")
    log_skip "Chrome/Chromium ${CHROME_VER} — already installed"
  fi
fi
if ! $CHROME_FOUND; then
  log_warn "Chrome/Chromium not found — Playwright can download Chromium, but system Chrome is recommended"
  log_detail "Fix (macOS): brew install --cask google-chrome"
  log_detail "Fix (Linux): apt install chromium-browser"
  log_detail "Alternative: Playwright installs its own Chromium via 'playwright install chromium'"
fi

# ── Playwright browsers (if Aegis venv exists) ────────────────────────────────
if [[ -n "$RC_WORKSPACE" && -x "${RC_WORKSPACE}/aegis/venv/bin/playwright" ]]; then
  PW_CHROMIUM=$("${RC_WORKSPACE}/aegis/venv/bin/python3" -c "
import subprocess, json, sys
try:
  r = subprocess.run(['${RC_WORKSPACE}/aegis/venv/bin/playwright', 'install', '--dry-run'], capture_output=True, text=True)
  if 'chromium' in r.stdout.lower() and 'up to date' in r.stdout.lower():
    print('installed')
  else:
    print('needed')
except: print('unknown')
" 2>/dev/null || echo "unknown")
  if [[ "$PW_CHROMIUM" == "installed" ]]; then
    log_skip "Playwright Chromium — already installed in aegis/venv"
  elif [[ "$PW_CHROMIUM" == "needed" ]]; then
    log_info "Playwright Chromium needs install — run: cd aegis && source venv/bin/activate && playwright install chromium"
  fi
fi

# ══════════════════════════════════════════════════════════════════════════════
section "8. Network Access"
# ══════════════════════════════════════════════════════════════════════════════

if git ls-remote --exit-code https://github.com/salesforce-internal/revenue-cloud-foundations.git HEAD &>/dev/null 2>&1; then
  log_pass "github.com/salesforce-internal reachable"
else
  log_warn "Cannot reach github.com/salesforce-internal — check SSH keys / GitHub access"
  log_detail "Needed for: Foundations, Distill repos"
fi

if git ls-remote --exit-code https://git.soma.salesforce.com/industries/Automated-Remote-Org-Test.git HEAD &>/dev/null 2>&1; then
  log_pass "git.soma.salesforce.com reachable (VPN connected)"
else
  log_warn "Cannot reach git.soma.salesforce.com — VPN may be required"
  log_detail "Needed for: Aegis repo. Connect to VPN and re-run."
fi

# ══════════════════════════════════════════════════════════════════════════════
section "9. Environment Variables (informational)"
# ══════════════════════════════════════════════════════════════════════════════

if [[ -n "${GEMINI_API_KEY:-}" ]]; then
  log_pass "GEMINI_API_KEY is set"
else
  log_warn "GEMINI_API_KEY not set — required by Distill DataMapper"
  log_detail "Create at: https://console.cloud.google.com/apis/credentials"
  log_detail "Set via: export GEMINI_API_KEY=\"your-key-here\""
fi

if [[ -n "${SF_URL:-}" ]]; then
  log_pass "SF_URL is set (${SF_URL})"
else
  log_warn "SF_URL not set — required by Aegis for test execution"
  log_detail "Set via: export SF_URL=\"https://your-org.my.salesforce.com/\""
fi

# ══════════════════════════════════════════════════════════════════════════════
section "10. Optimization Suggestions"
# ══════════════════════════════════════════════════════════════════════════════

OPT_COUNT=0

# Suggest removing Homebrew Python if pyenv is managing everything
if [[ -n "$BREW_PYTHON" ]] && $PYENV_OK; then
  HAS_ALL_NEEDED=true
  for need in "3.12"; do
    FOUND=$(pyenv versions --bare 2>/dev/null | grep -E "^${need}\." | head -1 || true)
    [[ -z "$FOUND" ]] && HAS_ALL_NEEDED=false
  done
  if $HAS_ALL_NEEDED; then
    log_info "Consider: brew unlink python@3 to avoid pyenv/Homebrew conflicts"
    log_detail "pyenv already has all needed versions. Unlinking Homebrew Python reduces PATH confusion."
    OPT_COUNT=$((OPT_COUNT + 1))
  fi
fi

# Suggest nvm default if multiple Node versions exist
if $NVM_OK && [[ ${#NVM_NODES[@]} -gt 1 ]]; then
  NVM_DEFAULT=$(nvm alias default 2>/dev/null | sed 's/.*-> //' | sed 's/ .*//' || true)
  log_info "Multiple nvm Node versions found. Default: ${NVM_DEFAULT:-none}"
  log_detail "Set preferred: nvm alias default <version>"
  OPT_COUNT=$((OPT_COUNT + 1))
fi

# Suggest pyenv global if not set
if $PYENV_OK; then
  PYENV_GLOBAL=$(pyenv global 2>/dev/null || true)
  if [[ "$PYENV_GLOBAL" == "system" || -z "$PYENV_GLOBAL" ]]; then
    log_info "pyenv global is 'system' — consider setting a default: pyenv global 3.12"
    log_detail "This makes python3 default to 3.12 outside of repos with .python-version"
    OPT_COUNT=$((OPT_COUNT + 1))
  fi
fi

# Suggest recreating stale venvs
if [[ -n "$RC_WORKSPACE" ]]; then
  for check in "distill:.venv" "aegis:venv"; do
    IFS=: read -r repo_name venv_name <<< "$check"
    VENV_BIN="${RC_WORKSPACE}/${repo_name}/${venv_name}/bin/python3"
    if [[ -x "$VENV_BIN" ]]; then
      VENV_VER=$("$VENV_BIN" --version 2>&1 | awk '{print $2}')
      VENV_MINOR=$(echo "$VENV_VER" | cut -d. -f2)
      if [[ "$VENV_MINOR" -lt 10 || "$VENV_MINOR" -gt 12 ]]; then
        log_info "Recreate ${repo_name}/${venv_name}/ — built with Python ${VENV_VER} (needs 3.10-3.12)"
        log_detail "rm -rf \"${RC_WORKSPACE}/${repo_name}/${venv_name}\" && cd \"${RC_WORKSPACE}/${repo_name}\" && python3 -m venv ${venv_name}"
        OPT_COUNT=$((OPT_COUNT + 1))
      fi
    fi
  done
fi

if [[ $OPT_COUNT -eq 0 ]]; then
  log_pass "No optimizations suggested — setup looks clean"
fi

# ══════════════════════════════════════════════════════════════════════════════
# Summary
# ══════════════════════════════════════════════════════════════════════════════
echo ""
printf "${BOLD}── Summary ──${NC}\n"

printf "  Installs: ${#PYTHON_INSTALLS[@]} Python"
if [[ -n "$SYSTEM_NODE_VER" ]]; then printf ", Node ${SYSTEM_NODE_VER}"; fi
echo ""

if [[ $CONFLICT_COUNT -gt 0 ]]; then
  printf "  ${RED}${CONFLICT_COUNT} conflict(s) detected — resolve before proceeding.${NC}\n"
fi

if [[ $SKIP_COUNT -gt 0 ]]; then
  printf "  ${DIM}${SKIP_COUNT} tool(s) already installed — skipped.${NC}\n"
fi

if [[ $REQUIRED_FAILURES -eq 0 ]]; then
  printf "  ${GREEN}All required checks passed.${NC}"
  if [[ $WARN_COUNT -gt 0 ]]; then
    printf " ${YELLOW}(${WARN_COUNT} warning(s) — see above)${NC}"
  fi
  echo ""
  echo ""
  echo "  Next steps:"
  echo "    1. Foundations: cci task run validate_setup          (validates CCI/SF CLI/SFDMU/Robot)"
  echo "    2. Follow docs/integration/isolated-testing-setup.md (Distill + Aegis setup)"
  echo ""
  exit 0
else
  printf "  ${RED}${REQUIRED_FAILURES} required check(s) failed.${NC}"
  if [[ $WARN_COUNT -gt 0 ]]; then
    printf " ${YELLOW}(${WARN_COUNT} warning(s))${NC}"
  fi
  echo ""
  echo ""
  echo "  Fix the FAIL items above, then re-run:"
  echo "    ./scripts/validate_integration_prereqs.sh"
  echo ""
  echo "  To attempt auto-installation of missing tools:"
  echo "    ./scripts/validate_integration_prereqs.sh --fix"
  echo ""
  exit 1
fi
