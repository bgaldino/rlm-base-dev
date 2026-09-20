#!/bin/bash
# Customer demo onboarding deploy gate.
#
# OPT-IN: this hook does nothing unless .cursor/onboarding-gates.json exists.
# The conductor creates that file at the start of an onboarding run and deletes it
# when the run is done. Normal repo work is never gated.
#
# While the file exists, org-mutating commands (cci, sf sfdmu, sf project deploy)
# require "deployApproved": true. Otherwise the user is asked to approve inline.
#
# See .cursor/skills/rlm-customer-demo-conductor/SKILL.md

set -uo pipefail

GATES_FILE=".cursor/onboarding-gates.json"

allow() { printf '{"permission":"allow"}\n'; exit 0; }

input=$(cat)

# Gate inactive -> never interfere.
[ -f "$GATES_FILE" ] || allow

if command -v jq >/dev/null 2>&1; then
  command=$(printf '%s' "$input" | jq -r '.command // empty' 2>/dev/null)
else
  command=$(printf '%s' "$input" | sed -n 's/.*"command"[[:space:]]*:[[:space:]]*"\(.*\)".*/\1/p')
fi

[ -n "${command:-}" ] || allow

# Only org-mutating commands are gated. Read-only `sf data query` is not.
case "$command" in
  *"cci flow run"*|*"cci task run"*|*"sf sfdmu"*|*"sfdmu run"*|*"sf project deploy"*|*"sfdx force:source:deploy"*) ;;
  *) allow ;;
esac

if grep -Eq '"deployApproved"[[:space:]]*:[[:space:]]*true' "$GATES_FILE" 2>/dev/null; then
  allow
fi

if grep -Eq '"visionConfirmed"[[:space:]]*:[[:space:]]*true' "$GATES_FILE" 2>/dev/null; then
  stage="The product vision is confirmed, but the deploy gate has not been approved yet."
else
  stage="Neither the vision gate nor the deploy gate has been approved yet."
fi

printf '{"permission":"ask","user_message":"Customer demo onboarding gate: %s Approve to let this command write to the org.","agent_message":"Deploy gate is not yet approved in .cursor/onboarding-gates.json. Confirm the deploy with the user, then set deployApproved to true before retrying."}\n' "$stage"
exit 0
