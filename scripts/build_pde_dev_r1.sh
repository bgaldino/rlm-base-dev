#!/usr/bin/env bash
#
# build_pde_dev_r1.sh — Build a Partner Development Environment (PDE) org.
#
# Creates/uses the `dev-r1` scratch org and runs `prepare_rlm_org` with two
# runtime-only feature-flag overrides applied to cumulusci.yml:
#
#     pde:        false -> true
#     billing_ui: true  -> false
#
# All other feature flags stay exactly as committed on the current branch.
#
# The edits to cumulusci.yml are RUNTIME ONLY. The original file is backed up
# before any change and restored on exit (success, failure, or interrupt), so
# nothing is left staged or committed after the build.
#
# Overridable via environment variables (defaults match the PDE build spec):
#   ORG=dev-r1            CCI scratch-org alias / config to build
#   FLOW=prepare_rlm_org  CCI flow to run
#   RECREATE_ORG=false    if true, scratch_delete the alias first for a fresh org
#
# Usage:
#   scripts/build_pde_dev_r1.sh
#   RECREATE_ORG=true scripts/build_pde_dev_r1.sh
#
set -euo pipefail

ORG="${ORG:-dev-r1}"
FLOW="${FLOW:-prepare_rlm_org}"
RECREATE_ORG="${RECREATE_ORG:-false}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

CCI_YML="cumulusci.yml"
BACKUP="$(mktemp "${TMPDIR:-/tmp}/cumulusci.yml.pdebuild.XXXXXX")"

log() { printf '\n[build-pde] %s\n' "$*"; }

restore() {
  if [[ -f "$BACKUP" ]]; then
    cp "$BACKUP" "$CCI_YML"
    rm -f "$BACKUP"
    log "Restored original ${CCI_YML} (runtime flag overrides reverted)."
  fi
}
trap restore EXIT

if [[ ! -f "$CCI_YML" ]]; then
  echo "[build-pde] ERROR: ${CCI_YML} not found in ${REPO_ROOT}" >&2
  exit 1
fi

log "Backing up ${CCI_YML} before applying runtime flag overrides."
cp "$CCI_YML" "$BACKUP"

# Apply the two runtime-only overrides. Each flag is matched exactly once at the
# project.custom indentation level; if the match count is anything other than 1
# the script aborts (and the trap restores the file) rather than silently
# building with the wrong flags.
log "Applying runtime overrides: pde=true, billing_ui=false."
python3 - "$CCI_YML" <<'PY'
import re, sys, pathlib

path = pathlib.Path(sys.argv[1])
text = path.read_text()

def set_flag(text, name, value):
    pat = re.compile(rf'^(?P<indent>    ){name}:[ \t]*(?:true|false)(?P<rest>.*)$', re.M)
    new_text, n = pat.subn(rf'\g<indent>{name}: {value}\g<rest>', text)
    if n != 1:
        sys.exit(f"ERROR: expected exactly 1 definition of '{name}' under "
                 f"project.custom, found {n}. Aborting without building.")
    return new_text

text = set_flag(text, "pde", "true")
text = set_flag(text, "billing_ui", "false")
path.write_text(text)
PY

# Confirm the override actually landed before spending time on a build.
grep -Eq '^    pde: true( |$|#)'         "$CCI_YML" || { echo "[build-pde] ERROR: pde override not present" >&2; exit 1; }
grep -Eq '^    billing_ui: false( |$|#)' "$CCI_YML" || { echo "[build-pde] ERROR: billing_ui override not present" >&2; exit 1; }
log "Verified overrides in ${CCI_YML}:"
grep -E '^    (pde|billing_ui):' "$CCI_YML" | sed 's/^/         /'

if [[ "$RECREATE_ORG" == "true" ]]; then
  log "RECREATE_ORG=true — deleting existing scratch org '${ORG}' (if any) for a fresh build."
  cci org scratch_delete "$ORG" --no-prompt || true
fi

log "Running: cci flow run ${FLOW} --org ${ORG}"
rc=0
if cci flow run "$FLOW" --org "$ORG"; then
  rc=0
else
  rc=$?
fi

if [[ $rc -eq 0 ]]; then
  log "PDE build SUCCEEDED for org '${ORG}'."
else
  log "PDE build FAILED for org '${ORG}' (exit ${rc})."
fi

# trap restore runs on exit and reverts cumulusci.yml in all cases.
exit $rc
