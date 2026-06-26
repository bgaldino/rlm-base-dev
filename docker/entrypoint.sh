#!/usr/bin/env bash
#
# rlm-entrypoint — runs once per `docker run`, before any user command.
#
# It wires up persistent state (via rlm-setup-state) and then hands off to the
# `rlm` wrapper or an interactive shell. NOTE: VS Code "Reopen in Container"
# bypasses this ENTRYPOINT (overrideCommand), so the same wiring also runs from
# the devcontainer postStartCommand — see docker/setup-state.sh.
set -euo pipefail

# Symlink auth dirs to the volume, stable CUMULUSCI_KEY, choose repo, write
# ~/.rlm-env. Sourced so RLM_REPO + CUMULUSCI_KEY propagate to the exec'd command.
. /usr/local/bin/rlm-setup-state

cd "$RLM_REPO"

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
