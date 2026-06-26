#!/usr/bin/env bash
#
# smoke.sh — non-destructive regression suite for the rlm Docker tooling.
#
# Exercises the real `rlm` command paths against the built image. Safe to run
# anytime:
#   • a FRESH throwaway volume is used for every guard check, so deploy/build
#     can never auto-confirm against a real org;
#   • the live state volume (default: rlm-state) is mounted READ-ONLY, and only
#     to make a throwaway copy — every org-aware command runs against the copy,
#     so the suite can never mutate the user's real credentials. Skipped if the
#     live volume isn't present.
#
# Usage:   docker/test/smoke.sh            (image must exist — `./docker/rlm setup`)
# Env:     RLM_IMAGE (default rlm-base:latest), RLM_STATE_VOLUME (default rlm-state)
# Exit:    0 if all checks pass, 1 otherwise.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

IMG="${RLM_IMAGE:-rlm-base:latest}"
LIVE="${RLM_STATE_VOLUME:-rlm-state}"
FRESH="rlm-smoke-$$"
COPY="rlm-smoke-live-$$"
TC="rlm-smoke-c-$$"
PASS=0; FAIL=0; SKIP=0

g(){ printf '  \033[32mPASS\033[0m %s\n' "$1"; PASS=$((PASS+1)); }
b(){ printf '  \033[31mFAIL\033[0m %s\n' "$1"; [ -n "${2:-}" ] && printf '       %s\n' "$2"; FAIL=$((FAIL+1)); }
s(){ printf '  \033[33mSKIP\033[0m %s\n' "$1"; SKIP=$((SKIP+1)); }
has(){ printf '%s' "$1" | grep -qiE "$2"; }
hd(){ printf '\n\033[1m%s\033[0m\n' "$1"; }
cleanup(){ docker rm -f "$TC" >/dev/null 2>&1 || true; docker volume rm "$FRESH" "$COPY" >/dev/null 2>&1 || true; rm -f "/tmp/rlm-smk-$$" 2>/dev/null || true; }
trap cleanup EXIT

dvol(){ docker run --rm -v "$1:/home/rlm/.rlm-state" "$IMG" "${@:2}" 2>&1; }            # via entrypoint
braw(){ docker run --rm -v "$1:/home/rlm/.rlm-state" --entrypoint bash "$IMG" -c "$2" 2>&1; }  # bypass entrypoint
live_has_orgs(){ docker volume inspect "$LIVE" >/dev/null 2>&1; }

docker image inspect "$IMG" >/dev/null 2>&1 || { echo "Image '$IMG' not found — run ./docker/rlm setup"; exit 2; }

hd "1. Toolchain / image"
# Assert the actual binaries exist via command -v. `rlm version` prints the
# labels even when a tool is missing (and validate_setup doesn't check claude),
# so a label-only check could pass on an image that dropped a tool.
o=$(dvol "$FRESH" sh -c 'for x in node sf cci python3 claude; do command -v "$x" >/dev/null 2>&1 || echo "MISSING:$x"; done; sf plugins 2>/dev/null | grep -qi sfdmu || echo "MISSING:sfdmu"; echo __ok__')
if has "$o" "__ok__" && ! has "$o" "MISSING:"; then g "toolchain binaries present (node/sf/sfdmu/cci/python/claude)"; else b "toolchain binaries" "$(printf '%s' "$o"|grep MISSING)"; fi
docker volume rm "$FRESH" >/dev/null 2>&1 || true
has "$(dvol "$FRESH" version)" "project *  *rlm-base" && g "rlm version runs (project rlm-base)" || b "rlm version"
docker volume rm "$FRESH" >/dev/null 2>&1 || true
# Validate the image with auto-fix DISABLED, so a missing/outdated dep fails the
# check here instead of being silently installed in this throwaway container
# (which would leave the image broken for the next run while the suite passes).
o=$(dvol "$FRESH" cci task run validate_setup -o auto_fix false -o auto_fix_robot false)
has "$o" "All required checks passed|Passed *: *12" && g "validate_setup (auto-fix off): all pass" || b "validate_setup failed" "$(printf '%s' "$o"|grep -iE 'fail|error'|tail -2)"
docker volume rm "$FRESH" >/dev/null 2>&1 || true

hd "2. State wiring (fresh volume)"
n=$(dvol "$FRESH" sh -c 'ls -ld ~/.sfdx ~/.sf ~/.cumulusci ~/.claude ~/.claude.json 2>&1 | grep -c -- "-> /home/rlm/.rlm-state"')
[ "$(printf '%s' "$n"|tail -1)" = "5" ] && g "entrypoint: 5 auth dirs symlinked to volume" || b "entrypoint symlinks" "$n"
has "$(dvol "$FRESH" sh -c 'test -s ~/.rlm-state/cumulusci/.rlm_cci_key && echo ok')" ok && g "entrypoint: stable CUMULUSCI_KEY generated" || b "key missing"
# devcontainer path: ENTRYPOINT bypassed → postStartCommand wires state.
# Label each half so BOTH must pass — a bare grep for "1" over the combined
# output would green on "0\n1" (symlink missing) or "1\n0" (env-key missing).
o=$(braw "$FRESH" '/usr/local/bin/rlm-setup-state >/dev/null 2>&1; printf "SL=%s\n" "$(ls -ld ~/.sfdx 2>&1 | grep -c -- "->")"; printf "KE=%s\n" "$(grep -c CUMULUSCI_KEY ~/.rlm-env 2>/dev/null)"')
{ has "$o" "SL=1" && has "$o" "KE=1"; } && g "devcontainer postStartCommand wires state + ~/.rlm-env" || b "postStartCommand wiring" "$o"
# BASH_ENV recovery: a NEW bash after setup-state picks up the env file
o=$(braw "$FRESH" '/usr/local/bin/rlm-setup-state >/dev/null 2>&1; bash -c "echo R=\$RLM_REPO K=\${CUMULUSCI_KEY:+set}"')
has "$o" "R=/opt/rlm-base-dev K=set" && g "BASH_ENV recovers RLM_REPO + CUMULUSCI_KEY" || b "BASH_ENV" "$o"
docker volume rm "$FRESH" >/dev/null 2>&1 || true

hd "3. Org-aware (throwaway COPY of live volume '$LIVE' — original never written)"
if live_has_orgs; then
  # The org commands below (sf/cci) write cache/config and may refresh tokens,
  # which would mutate the user's real credential volume. Mount the live volume
  # READ-ONLY just long enough to copy it into a throwaway, then run every check
  # against the copy so the original is never touched. The copy MUST run as root
  # (--user 0:0): a fresh named volume's root is root-owned, so the non-root rlm
  # user can't write to /dst — copy, then chown to uid 1000 so the later rlm-user
  # containers can read the creds and wire state. The copy carries
  # cumulusci/.rlm_cci_key so CCI/sf can decrypt the saved orgs.
  docker run --rm -v "$LIVE:/src:ro" -v "$COPY:/dst" --user 0:0 --entrypoint bash "$IMG" \
    -c 'cp -a /src/. /dst/ 2>/dev/null; chown -R 1000:1000 /dst' >/dev/null 2>&1
  # Guard: prove the copy actually carried the creds. Bypass the entrypoint so a
  # freshly *generated* key can't mask an empty copy as success.
  if has "$(braw "$COPY" 'test -s ~/.rlm-state/cumulusci/.rlm_cci_key && echo OK')" "OK"; then
    # Count REAL authenticated orgs (a username / "@"), NOT the static legend
    # line ("Default DevHub") or the predefined cci scratch CONFIGS
    # (beta/dev/ent…), which `rlm orgs` prints even with zero saved auth.
    usern=$(dvol "$COPY" sf org list --json | jq -r '(.result.nonScratchOrgs[]?,.result.scratchOrgs[]?)|.username//empty' | grep -c '@')
    [ "${usern:-0}" -ge 1 ] && g "orgs: $usern authenticated org(s) carried in copy" || s "orgs: no authenticated orgs in volume"
    sc=$(dvol "$COPY" sf org list --json | jq -r '.result.scratchOrgs[]? | .alias // empty' | sed 's/^[^_]*__//' | head -1)
    if [ -n "$sc" ]; then
      has "$(dvol "$COPY" open "$sc")" "frontdoor.jsp" && g "open '$sc' → login URL (CCI alias resolved)" || b "open failed"
    else s "open: no scratch org in volume"; fi
  else b "live-volume copy failed — org checks not run (copy carried no .rlm_cci_key)"; fi
  docker volume rm "$COPY" >/dev/null 2>&1 || true
else s "live volume '$LIVE' not present — skipping org-aware checks"; fi

hd "4. Safe-error guards (fresh volume — no real org touched)"
has "$(dvol "$FRESH" build --days abc)" "days must be a positive integer" && g "build --days <non-int> guarded" || b "days guard"
has "$(dvol "$FRESH" build)"            "No Dev Hub connected"             && g "build w/o Dev Hub guarded"     || b "devhub guard"
has "$(dvol "$FRESH" deploy)"           "no CumulusCI default org"          && g "deploy w/o default guarded"   || b "deploy guard"
has "$(dvol "$FRESH" customize)"        "No CumulusCI default org"          && g "customize w/o default guarded"|| b "customize guard"
has "$(printf 'force://bogus\n' | docker run --rm -i -v "$FRESH:/home/rlm/.rlm-state" "$IMG" login --auth-url --alias x 2>&1)" "INVALID_SFDX_AUTH_URL" && g "login --auth-url plumbing" || b "auth-url plumbing"
docker volume rm "$FRESH" >/dev/null 2>&1 || true

hd "5. Host launcher (bash 3.2)"
for f in docker/rlm docker/rlm-cli docker/entrypoint.sh docker/setup-state.sh docker/motd.sh; do
  /bin/bash -n "$f" 2>/dev/null && g "syntax: $f" || b "syntax: $f"; done
cp docker/rlm "/tmp/rlm-smk-$$"
has "$( cd /tmp && "/tmp/rlm-smk-$$" setup 2>&1 | head -1 )" "Can't find the rlm-base checkout" && g "REPO_ROOT: build-needing cmd errors clearly off-checkout" || b "REPO_ROOT guard"
# Point at a throwaway volume so a clean machine/CI doesn't get the real
# rlm-state volume created as a side effect (cleaned up by the EXIT trap).
has "$( cd /tmp && RLM_STATE_VOLUME="$FRESH" "/tmp/rlm-smk-$$" version 2>&1 )" "CumulusCI version" && g "REPO_ROOT: org commands work off-checkout" || b "version off-checkout"

hd "6. Persistent lifecycle (isolated container)"
RLM_CONTAINER="$TC" RLM_STATE_VOLUME="$FRESH" ./docker/rlm up >/dev/null 2>&1
has "$(docker exec "$TC" rlm version 2>&1)" "repo *  */work" && g "up + exec: repo resolves to /work mount" || b "up/exec repo"
has "$(docker exec "$TC" bash -c 'echo R=$RLM_REPO K=${CUMULUSCI_KEY:+set}' 2>&1)" "R=/work K=set" && g "exec bash -c: env via BASH_ENV (real path)" || b "exec BASH_ENV"
# Assert the container is actually gone, not just that `down` exited 0 — `down`
# exits 0 whether it removed $TC or found nothing (so a regression that ignored
# RLM_CONTAINER would be masked by the EXIT trap's later cleanup).
RLM_CONTAINER="$TC" ./docker/rlm down >/dev/null 2>&1
docker inspect "$TC" >/dev/null 2>&1 && b "down: container still present after down" || g "down: container removed"

printf '\n\033[1m════════════════════════════════════════\033[0m\n'
printf '  RESULT: \033[32m%d passed\033[0m, \033[31m%d failed\033[0m, \033[33m%d skipped\033[0m\n' "$PASS" "$FAIL" "$SKIP"
printf '\033[1m════════════════════════════════════════\033[0m\n'
[ "$FAIL" -eq 0 ]
