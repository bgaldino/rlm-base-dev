#!/usr/bin/env bash
#
# rlm-entrypoint — runs once per `docker run`, before any user command.
#
# Responsibilities:
#   1. Wire all Salesforce/CumulusCI auth + keychain state to ONE mounted
#      volume, so a single `-v` makes logins and connected orgs survive
#      container restarts.
#   2. Provide a stable CumulusCI encryption key (stored in the volume, never
#      baked into the image).
#   3. Pick the repo to operate on: a host-mounted working copy at /work wins;
#      otherwise the baked snapshot at /opt/rlm-base-dev.
#   4. Hand off to the `rlm` wrapper or an interactive shell.
set -euo pipefail

STATE_DIR="${RLM_STATE_DIR:-$HOME/.rlm-state}"

# --- 1) Persist auth/keychain on one volume via symlinks --------------------
# We relink the fixed home dotdirs (~/.sfdx, ~/.sf, ~/.cumulusci) into the
# volume. The SFDMU plugin lives under ~/.local/share/sf (NOT relinked), so it
# stays available from the baked image even with an empty state volume.
mkdir -p "$STATE_DIR/sfdx" "$STATE_DIR/sf" "$STATE_DIR/cumulusci"

link_state() {
  local name="$1"
  local home_path="$HOME/.$name"
  local vol_path="$STATE_DIR/$name"
  # Already linked? nothing to do.
  if [ -L "$home_path" ]; then
    return 0
  fi
  # A real dir from a previous (unmounted) run — migrate its contents once.
  if [ -e "$home_path" ]; then
    cp -a "$home_path/." "$vol_path/" 2>/dev/null || true
    rm -rf "$home_path"
  fi
  ln -s "$vol_path" "$home_path"
}
link_state sfdx
link_state sf
link_state cumulusci

# --- 2) Stable CumulusCI key (16 chars), generated into the volume ----------
KEYFILE="$STATE_DIR/cumulusci/.rlm_cci_key"
if [ ! -s "$KEYFILE" ]; then
  ( umask 077; head -c 32 /dev/urandom | base64 | tr -dc 'A-Za-z0-9' | head -c 16 > "$KEYFILE" )
fi
CUMULUSCI_KEY="$(cat "$KEYFILE")"
export CUMULUSCI_KEY

# --- 3) Choose repo: mounted /work overrides the baked snapshot -------------
if [ -f /work/cumulusci.yml ]; then
  RLM_REPO=/work
else
  RLM_REPO="${RLM_BAKED_REPO:-/opt/rlm-base-dev}"
fi
export RLM_REPO
# CumulusCI shells out to git; a mounted /work repo may be owned by a different
# uid than the container user, which git rejects as "dubious ownership".
git config --global --add safe.directory '*' 2>/dev/null || true
cd "$RLM_REPO"

# Make RLM_REPO + CUMULUSCI_KEY available to later shells. This file is the
# image's BASH_ENV, so every non-interactive `bash -c` inside the container
# (e.g. `docker exec ... bash -c 'cci ...'`) picks it up. Keep it side-effect
# free — no `cd` here, since BASH_ENV runs for every bash invocation.
{
  echo "export RLM_REPO=$RLM_REPO"
  echo "export CUMULUSCI_KEY=$CUMULUSCI_KEY"
} > "$HOME/.rlm-env"
# Interactive shells (attach / IDE terminal): also start in the repo. Appended
# after the distro .bashrc non-interactive guard, so it only runs interactively.
grep -q 'rlm-env' "$HOME/.bashrc" 2>/dev/null || \
  printf '%s\n' '[ -f "$HOME/.rlm-env" ] && . "$HOME/.rlm-env"; cd "${RLM_REPO:-$HOME}" 2>/dev/null || true' \
    >> "$HOME/.bashrc"

# --- 4) Dispatch ------------------------------------------------------------
case "${1:-}" in
  ""|shell)
    exec bash -l
    ;;
  serve|up)
    # Long-running mode: keep the container alive so an IDE (Cursor / VS Code
    # Dev Containers) or `docker exec` can attach. tini reaps + forwards signals.
    echo "rlm container ready — attach with 'docker exec -it <name> bash -l' or your IDE."
    exec sleep infinity
    ;;
  bash|sh|/bin/bash|/bin/sh|zsh)
    exec "$@"
    ;;
  rlm)
    shift
    exec rlm "$@"
    ;;
  *)
    exec rlm "$@"
    ;;
esac
