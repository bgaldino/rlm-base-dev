#!/usr/bin/env bash
# Install the repo's tracked git hooks. Todo 080 Deliverable 3.
#
#     scripts/bash/install-git-hooks.sh            # install
#     scripts/bash/install-git-hooks.sh --status   # report, change nothing
#     scripts/bash/install-git-hooks.sh --uninstall
#
# Points core.hooksPath at the tracked .githooks/ directory, so hook updates
# arrive with a normal `git pull` and never need reinstalling — unlike copying
# into .git/hooks/, where every clone drifts and nobody notices.
#
# WHY THIS IS SAFE FOR git-lfs. core.hooksPath makes git ignore .git/hooks/
# entirely, which would silently disable a git-lfs pre-push hook installed there
# by `git lfs install`. .githooks/pre-push chains to it explicitly, forwarding
# the same stdin. This script reports what it found so the chaining is visible
# rather than assumed.

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
GIT_DIR="$(git rev-parse --git-dir)"
[[ "$GIT_DIR" != /* ]] && GIT_DIR="$REPO_ROOT/$GIT_DIR"
HOOKS_DIR=".githooks"
MODE="${1:-install}"

current="$(git config --get core.hooksPath || true)"

report() {
    echo "git hooks"
    echo "  core.hooksPath : ${current:-<unset — git uses .git/hooks/>}"
    echo "  tracked hooks  : $(ls "$REPO_ROOT/$HOOKS_DIR" 2>/dev/null | tr '\n' ' ')"
    if [[ -e "$GIT_DIR/hooks/pre-push" ]]; then
        local who="unknown"
        grep -qi 'git.lfs' "$GIT_DIR/hooks/pre-push" 2>/dev/null && who="git-lfs"
        echo "  existing hook  : .git/hooks/pre-push ($who) — will be CHAINED, not replaced"
    else
        echo "  existing hook  : none in .git/hooks/ (nothing to chain today;"
        echo "                   if you later run 'git lfs install', it is picked up automatically)"
    fi
}

case "$MODE" in
    --status|status)
        report
        if [[ "$current" == "$HOOKS_DIR" ]]; then
            echo "  status         : INSTALLED"
        else
            echo "  status         : NOT installed — run scripts/bash/install-git-hooks.sh"
        fi
        ;;

    --uninstall|uninstall)
        if [[ "$current" == "$HOOKS_DIR" ]]; then
            git config --unset core.hooksPath
            echo "Uninstalled: core.hooksPath unset; git returns to .git/hooks/."
            echo "Any git-lfs hook there resumes running directly."
        else
            echo "Not installed (core.hooksPath is '${current:-unset}') — nothing to do."
        fi
        ;;

    install)
        if [[ -n "$current" && "$current" != "$HOOKS_DIR" ]]; then
            echo "REFUSING: core.hooksPath is already set to '$current'." >&2
            echo "  Something else manages hooks here. Overwriting it would silently" >&2
            echo "  disable that. Resolve deliberately, then re-run." >&2
            exit 1
        fi
        chmod +x "$REPO_ROOT/$HOOKS_DIR"/* 2>/dev/null || true
        git config core.hooksPath "$HOOKS_DIR"
        current="$HOOKS_DIR"
        report
        echo "  status         : INSTALLED"
        echo
        echo "Every push now runs scripts/ai/pre_push_audit.py first and is refused"
        echo "if it does not pass. Bypass deliberately with: git push --no-verify"
        ;;

    *)
        echo "usage: $0 [install|--status|--uninstall]" >&2
        exit 2
        ;;
esac
