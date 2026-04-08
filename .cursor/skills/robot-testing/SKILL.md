# Robot Framework Testing

Use this skill when writing, modifying, or debugging Robot Framework tests.

## Quick Rules

1. `tests/setup/` = **org configuration automation** (not tests). `tests/e2e/` = **functional tests**.
2. Setup tests run mid-flow to toggle settings with no API equivalent. E2E tests run after provisioning.
3. No `//` comments in JavaScript blocks — Robot joins continuation lines, breaking everything after `//`.
4. Use `composed: true` on dispatched events to cross shadow DOM boundaries.
5. Use `self.org_config.username` in Python wrappers for `sf org open -o`.
6. Gate E2E tests with `Skip If "${QB}" == "false"` on the relevant feature flag.
7. For Setup UI + shadow DOM vs iframe: read `setup-ui-shadow-dom.md` before adding new keywords (LWS, `composed`, VF frames).

## DO NOT

- **DO NOT** use `//` comments in Robot JavaScript — use `/* */` instead
- **DO NOT** use standard `input_text` for LWC inputs — use native setter pattern
- **DO NOT** log session tokens — wrap URL retrieval with `Set Log Level NONE`

---

## Two Purposes: Setup vs E2E

| Aspect | Setup Tests | E2E Tests |
|--------|------------|-----------|
| Location | `tests/setup/` | `tests/e2e/` |
| Purpose | Configure org settings (no API equivalent) | Validate business workflows |
| When they run | Mid-flow in `prepare_rlm_org` | On demand after provisioning |
| Idempotent? | Yes — detects state before toggling | Yes — resets account first |
| Headed? | Headless by default | Headless default, headed for debug |
| Asserts logic? | No — only asserts control was set | Yes — verifies records/assets |

### Setup tests — what they configure

| Robot File | What | Why Robot? |
|-----------|------|-----------|
| `configure_revenue_settings` | Pricing Procedure, Usage Rating, Instant Pricing, flows | Shadow DOM controls, no API |
| `enable_analytics` | CRM Analytics + Data Sync toggle | VF iframe, no API |
| `enable_document_builder` | Document Builder toggle | Shadow DOM, no API |
| `enable_constraints_settings` | Transaction Type, Asset Context, Constraints Engine | Shadow DOM, no API |
| `reorder_app_launcher` | App Launcher ordering | SortOrder is platform read-only |

### E2E tests — what they validate

| Robot File | Flow | Prerequisite |
|-----------|------|-------------|
| `quote_to_order` | Full Reset→Opp→Quote→Products→Order→Assets | `prepare_rlm_org` with `qb=true` |
| `setup_quote` | Part 1: Reset→Opp→Quote | Same |
| `order_from_quote` | Part 2: Products→Order→Assets | A Quote must exist |
| `reset_account` | Reset Account via QuickAction | An account must exist |

---

## CCI Task Wiring

For detailed CCI task tables, Python wrapper patterns, shadow DOM
traversal code, LWC reactivity patterns, keyword references, and
test authoring guides, read `.cursor/skills/robot-testing/patterns.md`.

For **agent-oriented** setup-UI pitfalls (shadow vs iframe, logging, when
not to copy generic Selenium), read
`.cursor/skills/robot-testing/setup-ui-shadow-dom.md`.

### Running tests

```bash
cci task run robot_e2e --org beta              # headless
cci task run robot_e2e_debug --org beta         # headed + CDP port 9222
cci task run robot_e2e_debug -o pause_for_recording true --org beta  # with pauses
```

---

## Related Skills

- **CCI Orchestration** — `.cursor/skills/cci-orchestration/SKILL.md`
- **Troubleshooting** — `.cursor/skills/troubleshooting/SKILL.md`
- **Repo Integration** — `.cursor/skills/repo-integration/SKILL.md`
