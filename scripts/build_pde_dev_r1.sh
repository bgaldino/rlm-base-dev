#!/usr/bin/env bash
#
# build_pde_dev_r1.sh — Build a Partner Development Environment (PDE) org.
#
# Provisions a NEW, uniquely-aliased scratch org (pde<datetimestamp>) from the
# `dev-r1` scratch shape and runs `prepare_rlm_org` with two runtime-only
# feature-flag overrides applied to cumulusci.yml:
#
#     pde:        false -> true
#     billing_ui: true  -> false
#
# All other feature flags stay exactly as committed on the current branch.
#
# Nothing the build touches is left in the working tree:
#   * cumulusci.yml is backed up before any edit and restored on exit
#     (success, failure, or interrupt).
#   * Tracked files the build regenerates under unpackaged/post_ux/ and
#     datasets/sfdmu/ (UX assembly output, SFDMU export.json writeback) are
#     reverted on exit — but only the ones THIS build dirtied (pre-existing
#     local edits are left untouched). Disable with CLEAN_BUILD_ARTIFACTS=false.
#
# Overridable via environment variables:
#   ORG=pde<datetime>            scratch-org alias to create/build
#   SHAPE=dev-r1                 scratch shape (config under orgs.scratch)
#   FLOW=prepare_rlm_org         CCI flow to run
#   CLEAN_BUILD_ARTIFACTS=true   revert build-generated post_ux/datasets churn
#
# Usage:
#   scripts/build_pde_dev_r1.sh
#   ORG=pde-demo scripts/build_pde_dev_r1.sh
#
set -euo pipefail

ORG="${ORG:-pde$(date +%Y%m%d%H%M%S)}"
SHAPE="${SHAPE:-dev-r1}"
FLOW="${FLOW:-prepare_rlm_org}"
CLEAN_BUILD_ARTIFACTS="${CLEAN_BUILD_ARTIFACTS:-true}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

CCI_YML="cumulusci.yml"
BACKUP="$(mktemp "${TMPDIR:-/tmp}/cumulusci.yml.pdebuild.XXXXXX")"
PRE_DIRTY_FILE="$(mktemp "${TMPDIR:-/tmp}/pdebuild.predirty.XXXXXX")"

# Tracked paths the prepare_rlm_org flow is known to regenerate at runtime.
ARTIFACT_PATHS=(unpackaged/post_ux datasets/sfdmu)

log() { printf '\n[build-pde] %s\n' "$*"; }

restore() {
  # 1) Revert the runtime cumulusci.yml flag overrides.
  if [[ -f "$BACKUP" ]]; then
    cp "$BACKUP" "$CCI_YML"
    rm -f "$BACKUP"
    log "Restored original ${CCI_YML} (runtime flag overrides reverted)."
  fi

  # 2) Revert build-generated tracked churn under ARTIFACT_PATHS, but only the
  #    files that THIS build dirtied (compare against the pre-build snapshot).
  if [[ "$CLEAN_BUILD_ARTIFACTS" == "true" && -f "$PRE_DIRTY_FILE" ]]; then
    local reverted=0 path
    while IFS= read -r path; do
      [[ -z "$path" ]] && continue
      if ! grep -Fxq "$path" "$PRE_DIRTY_FILE"; then
        if git checkout -- "$path" 2>/dev/null; then
          reverted=$((reverted + 1))
        fi
      fi
    done < <(git status --porcelain -- "${ARTIFACT_PATHS[@]}" | cut -c4-)
    if [[ $reverted -gt 0 ]]; then
      log "Reverted ${reverted} build-generated file(s) under post_ux/ and datasets/sfdmu/."
    fi
  fi
  rm -f "$PRE_DIRTY_FILE"
}
trap restore EXIT

if [[ ! -f "$CCI_YML" ]]; then
  echo "[build-pde] ERROR: ${CCI_YML} not found in ${REPO_ROOT}" >&2
  exit 1
fi

# Snapshot which ARTIFACT_PATHS files are ALREADY dirty so we never revert a
# user's pre-existing local edits — only build-introduced churn.
git status --porcelain -- "${ARTIFACT_PATHS[@]}" | cut -c4- > "$PRE_DIRTY_FILE" || true

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

# Register a fresh, uniquely-aliased scratch org from the dev-r1 shape. The
# actual org is created lazily by CCI when the flow first runs against it.
if cci org info "$ORG" >/dev/null 2>&1; then
  log "Scratch-org alias '${ORG}' already registered; reusing it."
else
  log "Registering scratch org '${ORG}' from shape '${SHAPE}': cci org scratch ${SHAPE} ${ORG}"
  cci org scratch "$SHAPE" "$ORG"
fi

log "Running: cci flow run ${FLOW} --org ${ORG}"
rc=0
if cci flow run "$FLOW" --org "$ORG"; then
  rc=0
else
  rc=$?
fi

if [[ $rc -eq 0 ]]; then
  log "PDE build SUCCEEDED for org '${ORG}' (SF CLI alias: rlm-base__${ORG})."
else
  log "PDE build FAILED for org '${ORG}' (exit ${rc})."
fi

# trap restore runs on exit and reverts cumulusci.yml + build churn in all cases.
exit $rc
