#!/usr/bin/env bash
#
# rlm-setup-state — idempotent persistent-state wiring for the RLM container.
#
# Symlinks the Salesforce / CumulusCI / Claude auth dirs onto the single state
# volume, generates a stable CUMULUSCI_KEY, picks the repo (mounted /work or the
# baked snapshot), and writes ~/.rlm-env (the image's BASH_ENV) so every shell
# gets RLM_REPO + the key.
#
# Run two ways, both safe and idempotent:
#   • SOURCED by rlm-entrypoint  — exports propagate to the dispatched process.
#   • EXECUTED as the devcontainer postStartCommand — Reopen-in-Container uses
#     VS Code's keep-alive command (overrideCommand), so the image ENTRYPOINT
#     does NOT run; this hook does the wiring instead. Exports don't propagate
#     when executed, but ~/.rlm-env (read via BASH_ENV) carries them to shells.
set -euo pipefail

STATE_DIR="${RLM_STATE_DIR:-$HOME/.rlm-state}"
mkdir -p "$STATE_DIR/sfdx" "$STATE_DIR/sf" "$STATE_DIR/cumulusci" "$STATE_DIR/claude"

# Relink ~/.<name> → volume (migrating any pre-existing real dir once). The SFDMU
# plugin lives under ~/.local/share/sf (not relinked), so it stays baked.
link_state() {
  local name="$1" home_path="$HOME/.$1" vol_path="$STATE_DIR/$1"
  [ -L "$home_path" ] && return 0
  if [ -e "$home_path" ]; then
    cp -a "$home_path/." "$vol_path/" 2>/dev/null || true
    rm -rf "$home_path"
  fi
  ln -s "$vol_path" "$home_path"
}
link_state sfdx
link_state sf
link_state cumulusci
link_state claude
# ~/.claude.json is a file (not a dir) — link it separately.
if [ ! -L "$HOME/.claude.json" ]; then
  if [ -e "$HOME/.claude.json" ]; then
    cp -a "$HOME/.claude.json" "$STATE_DIR/claude.json" 2>/dev/null || true
    rm -f "$HOME/.claude.json"
  fi
  ln -s "$STATE_DIR/claude.json" "$HOME/.claude.json"
fi

# Stable CumulusCI key (16 chars), generated into the volume (not baked).
KEYFILE="$STATE_DIR/cumulusci/.rlm_cci_key"
if [ ! -s "$KEYFILE" ]; then
  ( umask 077; head -c 32 /dev/urandom | base64 | tr -dc 'A-Za-z0-9' | head -c 16 > "$KEYFILE" )
fi
CUMULUSCI_KEY="$(cat "$KEYFILE")"
export CUMULUSCI_KEY

# Choose repo: a host-mounted working copy at /work overrides the baked snapshot.
if [ -f /work/cumulusci.yml ]; then
  RLM_REPO=/work
else
  RLM_REPO="${RLM_BAKED_REPO:-/opt/rlm-base-dev}"
fi
export RLM_REPO

# CumulusCI shells out to git; a mounted /work repo may be owned by a different
# uid than the container user, which git rejects as "dubious ownership".
git config --global --add safe.directory '*' 2>/dev/null || true

# Make RLM_REPO + CUMULUSCI_KEY available to later shells via BASH_ENV. Keep this
# file side-effect free (no cd) — BASH_ENV runs for every bash invocation.
{
  echo "export RLM_REPO=$RLM_REPO"
  echo "export CUMULUSCI_KEY=$CUMULUSCI_KEY"
} > "$HOME/.rlm-env"
# Interactive shells (attach / IDE terminal) also start in the repo. Appended
# after the distro .bashrc non-interactive guard, so it only runs interactively.
grep -q 'rlm-env' "$HOME/.bashrc" 2>/dev/null || \
  printf '%s\n' '[ -f "$HOME/.rlm-env" ] && . "$HOME/.rlm-env"; cd "${RLM_REPO:-$HOME}" 2>/dev/null || true' \
    >> "$HOME/.bashrc"
