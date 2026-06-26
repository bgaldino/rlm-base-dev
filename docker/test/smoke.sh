#!/usr/bin/env bash
#
# smoke.sh — non-destructive regression suite for the rlm Docker tooling.
#
# Exercises the real `rlm` command paths against the built image. Safe to run
# anytime:
#   • a FRESH throwaway volume is used for every guard check, so deploy/build
#     can never auto-confirm against a real org;
#   • the live state volume (default: rlm-state) is used ONLY for read-only
#     checks, and those are skipped if it isn't present.
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
TC="rlm-smoke-c-$$"
PASS=0; FAIL=0; SKIP=0

g(){ printf '  \033[32mPASS\033[0m %s\n' "$1"; PASS=$((PASS+1)); }
b(){ printf '  \033[31mFAIL\033[0m %s\n' "$1"; [ -n "${2:-}" ] && printf '       %s\n' "$2"; FAIL=$((FAIL+1)); }
s(){ printf '  \033[33mSKIP\033[0m %s\n' "$1"; SKIP=$((SKIP+1)); }
has(){ printf '%s' "$1" | grep -qiE "$2"; }
hd(){ printf '\n\033[1m%s\033[0m\n' "$1"; }
cleanup(){ docker rm -f "$TC" >/dev/null 2>&1 || true; docker volume rm "$FRESH" >/dev/null 2>&1 || true; rm -f "/tmp/rlm-smk-$$" 2>/dev/null || true; }
trap cleanup EXIT

dvol(){ docker run --rm -v "$1:/home/rlm/.rlm-state" "$IMG" "${@:2}" 2>&1; }            # via entrypoint
braw(){ docker run --rm -v "$1:/home/rlm/.rlm-state" --entrypoint bash "$IMG" -c "$2" 2>&1; }  # bypass entrypoint
live_has_orgs(){ docker volume inspect "$LIVE" >/dev/null 2>&1; }

docker image inspect "$IMG" >/dev/null 2>&1 || { echo "Image '$IMG' not found — run ./docker/rlm setup"; exit 2; }

hd "1. Toolchain / image"
o=$(dvol "$FRESH" version)
for t in node sf sfdmu cci claude python; do has "$o" "^  $t " && g "version: $t present" || b "version: $t missing"; done
docker volume rm "$FRESH" >/dev/null 2>&1 || true
o=$(dvol "$FRESH" doctor); has "$o" "All required checks passed|Passed *: *12" && g "doctor: validate_setup all pass" || b "doctor failed" "$(printf '%s' "$o"|tail -2)"
docker volume rm "$FRESH" >/dev/null 2>&1 || true

hd "2. State wiring (fresh volume)"
n=$(dvol "$FRESH" sh -c 'ls -ld ~/.sfdx ~/.sf ~/.cumulusci ~/.claude ~/.claude.json 2>&1 | grep -c -- "-> /home/rlm/.rlm-state"')
[ "$(printf '%s' "$n"|tail -1)" = "5" ] && g "entrypoint: 5 auth dirs symlinked to volume" || b "entrypoint symlinks" "$n"
has "$(dvol "$FRESH" sh -c 'test -s ~/.rlm-state/cumulusci/.rlm_cci_key && echo ok')" ok && g "entrypoint: stable CUMULUSCI_KEY generated" || b "key missing"
# devcontainer path: ENTRYPOINT bypassed → postStartCommand wires state
o=$(braw "$FRESH" '/usr/local/bin/rlm-setup-state >/dev/null 2>&1; ls -ld ~/.sfdx 2>&1 | grep -c -- "->"; grep -c CUMULUSCI_KEY ~/.rlm-env')
has "$o" "1" && g "devcontainer postStartCommand wires state + ~/.rlm-env" || b "postStartCommand wiring" "$o"
# BASH_ENV recovery: a NEW bash after setup-state picks up the env file
o=$(braw "$FRESH" '/usr/local/bin/rlm-setup-state >/dev/null 2>&1; bash -c "echo R=\$RLM_REPO K=\${CUMULUSCI_KEY:+set}"')
has "$o" "R=/opt/rlm-base-dev K=set" && g "BASH_ENV recovers RLM_REPO + CUMULUSCI_KEY" || b "BASH_ENV" "$o"
docker volume rm "$FRESH" >/dev/null 2>&1 || true

hd "3. Org-aware (live volume '$LIVE', read-only)"
if live_has_orgs; then
  o=$(dvol "$LIVE" orgs); has "$o" "devhub|@" && g "orgs lists connected org(s)" || s "orgs: no orgs in volume"
  sc=$(dvol "$LIVE" sf org list --json | jq -r '.result.scratchOrgs[]? | .alias // empty' | sed 's/^[^_]*__//' | head -1)
  if [ -n "$sc" ]; then
    has "$(dvol "$LIVE" open "$sc")" "frontdoor.jsp" && g "open '$sc' → login URL (CCI alias resolved)" || b "open failed"
  else s "open: no scratch org in volume"; fi
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
has "$( cd /tmp && "/tmp/rlm-smk-$$" version 2>&1 )" "CumulusCI version" && g "REPO_ROOT: org commands work off-checkout" || b "version off-checkout"

hd "6. Persistent lifecycle (isolated container)"
RLM_CONTAINER="$TC" RLM_STATE_VOLUME="$FRESH" ./docker/rlm up >/dev/null 2>&1
has "$(docker exec "$TC" rlm version 2>&1)" "repo *  */work" && g "up + exec: repo resolves to /work mount" || b "up/exec repo"
has "$(docker exec "$TC" bash -c 'echo R=$RLM_REPO K=${CUMULUSCI_KEY:+set}' 2>&1)" "R=/work K=set" && g "exec bash -c: env via BASH_ENV (real path)" || b "exec BASH_ENV"
RLM_CONTAINER="$TC" ./docker/rlm down >/dev/null 2>&1 && g "down: container removed" || b "down"

printf '\n\033[1m════════════════════════════════════════\033[0m\n'
printf '  RESULT: \033[32m%d passed\033[0m, \033[31m%d failed\033[0m, \033[33m%d skipped\033[0m\n' "$PASS" "$FAIL" "$SKIP"
printf '\033[1m════════════════════════════════════════\033[0m\n'
[ "$FAIL" -eq 0 ]
