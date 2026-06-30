#!/usr/bin/env bash
#
# build_pde_dev_r1.sh — Build a Partner Development Environment (PDE) org.
#
# Provisions a NEW, uniquely-aliased scratch org (pde<datetimestamp><pid>) from
# the `tfid-pde` scratch shape and runs `prepare_rlm_org` with two runtime-only
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
#   * The flow regenerates files under unpackaged/post_ux/ (UX assembly) and
#     datasets/sfdmu/ (SFDMU export.json writeback). To guarantee those edits
#     are build-only, the script REQUIRES those paths to be clean before it
#     runs, then reverts all churn there on exit (tracked + untracked). Set
#     CLEAN_BUILD_ARTIFACTS=false to skip both the pre-check and the cleanup and
#     manage those paths yourself.
#
# Each build provisions a FRESH scratch org: if the resolved alias already
# exists the script fails fast rather than reusing a stale/partial org.
#
# Overridable via environment variables:
#   ORG=pde<datetime><pid>       scratch-org alias to create/build (must be unused)
#   SHAPE=tfid-pde               scratch shape (config under orgs.scratch)
#   FLOW=prepare_rlm_org         CCI flow to run
#   CLEAN_BUILD_ARTIFACTS=true   require/clean post_ux + datasets build churn
#
# Usage:
#   scripts/build_pde_dev_r1.sh
#   ORG=pde-demo scripts/build_pde_dev_r1.sh
#
set -euo pipefail

# Suffix the timestamp with the PID ($$) so two builds launched in the same
# second (e.g. concurrent scheduled runs) can never resolve to the same alias.
ORG="${ORG:-pde$(date +%Y%m%d%H%M%S)$$}"
SHAPE="${SHAPE:-tfid-pde}"
FLOW="${FLOW:-prepare_rlm_org}"
CLEAN_BUILD_ARTIFACTS="${CLEAN_BUILD_ARTIFACTS:-true}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

CCI_YML="cumulusci.yml"
BACKUP="$(mktemp "${TMPDIR:-/tmp}/cumulusci.yml.pdebuild.XXXXXX")"

# Tracked paths the prepare_rlm_org flow is known to regenerate at runtime.
ARTIFACT_PATHS=(unpackaged/post_ux datasets/sfdmu)

# Set true only once we've verified those paths started clean, so the EXIT trap
# never runs a destructive clean on a tree it didn't pre-check.
ARTIFACTS_PRECHECKED=false

log() { printf '\n[build-pde] %s\n' "$*"; }

restore() {
  # 1) Revert the runtime cumulusci.yml flag overrides.
  if [[ -f "$BACKUP" ]]; then
    cp "$BACKUP" "$CCI_YML"
    rm -f "$BACKUP"
    log "Restored original ${CCI_YML} (runtime flag overrides reverted)."
  fi

  # 2) Revert ALL build-generated churn under ARTIFACT_PATHS. Safe to wipe the
  #    whole path set only because we verified it started clean (see pre-check);
  #    git checkout restores tracked modifications/deletions, git clean removes
  #    files the build newly created.
  if [[ "$CLEAN_BUILD_ARTIFACTS" == "true" && "$ARTIFACTS_PRECHECKED" == "true" ]]; then
    if [[ -n "$(git status --porcelain -- "${ARTIFACT_PATHS[@]}")" ]]; then
      git checkout -- "${ARTIFACT_PATHS[@]}" 2>/dev/null || true
      git clean -fdq -- "${ARTIFACT_PATHS[@]}" 2>/dev/null || true
      log "Reverted build-generated churn under ${ARTIFACT_PATHS[*]}."
    fi
  fi
}
trap restore EXIT

if [[ ! -f "$CCI_YML" ]]; then
  echo "[build-pde] ERROR: ${CCI_YML} not found in ${REPO_ROOT}" >&2
  exit 1
fi

# Require the regenerated paths to be clean BEFORE the build. The flow rewrites
# files here and we revert them afterward; if the caller had local edits there,
# proceeding would clobber them and the post-build revert could not distinguish
# their content from build output. Fail fast instead of corrupting their work.
if [[ "$CLEAN_BUILD_ARTIFACTS" == "true" ]]; then
  if [[ -n "$(git status --porcelain -- "${ARTIFACT_PATHS[@]}")" ]]; then
    echo "[build-pde] ERROR: uncommitted changes under ${ARTIFACT_PATHS[*]}." >&2
    echo "[build-pde] The build regenerates and then reverts these paths, which would" >&2
    echo "[build-pde] discard your local edits. Commit or stash them first, or re-run" >&2
    echo "[build-pde] with CLEAN_BUILD_ARTIFACTS=false to manage these paths yourself." >&2
    exit 1
  fi
  ARTIFACTS_PRECHECKED=true
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

# Register a FRESH, uniquely-aliased scratch org from the configured shape. Each
# build must provision a new org, so refuse to reuse an alias that already
# exists (stale/partial state, or a colliding pinned/timestamp alias). The
# actual org is created lazily by CCI when the flow first runs against it.
if cci org info "$ORG" >/dev/null 2>&1; then
  echo "[build-pde] ERROR: scratch-org alias '${ORG}' already exists." >&2
  echo "[build-pde] Each PDE build must provision a FRESH org. Choose a different ORG," >&2
  echo "[build-pde] or delete the existing one: cci org scratch_delete ${ORG}" >&2
  exit 1
fi
log "Registering scratch org '${ORG}' from shape '${SHAPE}': cci org scratch ${SHAPE} ${ORG}"
cci org scratch "$SHAPE" "$ORG"

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
