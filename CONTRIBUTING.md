# Contributing Guide

Thank you for your interest in contributing to **Revenue Cloud Base
Foundations**. This guide explains how to submit changes using a fork and a
pull request, and what this repository expects before a PR is merged.

> **Repository location.** This project is moving to a Salesforce-owned GitHub
> namespace. The commands below use the repository's current location — if an
> upstream URL no longer resolves, use the **Code → Clone** URL shown on the
> repository page you are reading this from.

## 1. Fork the Repository

To contribute, create your own copy:

1. Open this repository on github.com.
2. Click the **Fork** button in the top-right corner.
3. Select your GitHub account as the destination.
4. GitHub will create your personal fork at
   `https://github.com/<your-username>/rlm-base-dev`.

## 2. Clone Your Fork

Clone your personal fork:

```sh
git clone https://github.com/<your-username>/rlm-base-dev.git
cd rlm-base-dev
```

Add the original repository as the upstream remote:

```sh
git remote add upstream https://github.com/bgaldino/rlm-base-dev.git
```

## 3. Set Up Your Environment

Two supported paths — pick one:

- **Containerized (no local toolchain):** `./docker/rlm setup` — see
  [`docker/README.md`](docker/README.md).
- **Local (Homebrew + pyenv + nvm):** follow the *macOS Environment Setup*
  section of the [README](README.md), then
  [`docs/guides/dev-environment-setup.md`](docs/guides/dev-environment-setup.md)
  for the canonical layered view.

Verify the toolchain before you start (no org required):

```sh
cci task run validate_setup
```

## 4. Create a Branch

Create a new branch for your work:

```sh
git checkout -b my-feature-name
```

Use a short, descriptive name. **Never commit or push directly to `main`** —
every change goes through a branch and a pull request.

## 5. Make Your Changes

Before editing, read [`AGENTS.md`](AGENTS.md) — it is the canonical guide for
this repository (and the instruction file every AI coding agent reads). It
carries the safety guards that cause the most review churn when missed:

- Edit `templates/`, never `unpackaged/post_ux/` (auto-generated).
- Keep `force-app/` profiles `classAccesses`-only; layout and app visibility
  live in `templates/profiles/`.
- Do not switch an SFDMU plan from `operation: Upsert` to `Insert` +
  `deleteOldData: true` without explicit maintainer approval — it is
  destructive.
- Never commit real email addresses in `rlm.network-meta.xml`.
- Behavioral Robot Framework changes must be verified against a **live scratch
  org**; `robot --dryrun` is not verification.

Task-specific guidance lives in the skill files indexed in `AGENTS.md`
(`.cursor/skills/**` — plain markdown, readable by any tool or human).

## 6. Validate Before You Push

Run the checks that apply to what you changed:

```sh
cci task run validate_setup                                # toolchain + repo sanity (no org)
python scripts/ai/generate_cci_reference.py                # after any cumulusci.yml edit — commit the output
python scripts/ai/check_plan_readme_consistency.py         # plan README ↔ export.json/CSVs (expects 0 errors)
python scripts/validate_sfdmu_v5_datasets.py               # SFDMU v5 plan compliance — see the baseline note
python tests/<name>.py                                     # top-level suites — run directly, never via pytest
python -m pytest tests/build_harness tests/txn_data_harness # harness suites — pytest-collected
```

`pyproject.toml` explains the split: top-level `tests/*.py` use a self-contained
`check()` aggregator and would false-pass under pytest, so they are run directly;
the harness suites are the pytest-collected ones. The build-harness suite needs
`pip install -r scripts/build_harness/tui/requirements.txt`, and txn-data-harness
additionally needs `requests` and `PyYAML`.

For LWC work, check the files you touched rather than the whole repo:

```sh
npx eslint <changed-lwc-files>
npx prettier --check <changed-files>
npm test -- --passWithNoTests                              # Jest — the repo has no LWC suites yet,
                                                           # so a bare `npm test` exits 1
```

`prettier --check` formats Apex but never compiles or runs it. **Apex changes
need an org**: deploy, then run the tests, then confirm the permission set is
actually sufficient at runtime.

```sh
sf project deploy start --target-org <alias>
sf apex run test --target-org <alias>
```

`sf apex run test` passing is necessary but not sufficient — it runs as an
admin. See the Validation Checks in
[`.cursor/skills/apex-security-hardening/SKILL.md`](.cursor/skills/apex-security-hardening/SKILL.md)
for the read-back and `System.runAs` / persona walk that catch what admin
context hides.

> **Compare against the baseline, don't chase it.** Some repo-wide checks
> already report findings on `main` that predate your change — today that
> includes `npm run lint`, `npm run prettier:verify`, and
> `validate_sfdmu_v5_datasets.py`. Run the check on `main` first and compare,
> so you fix what your change introduced instead of inheriting the backlog.
> Continuous integration gates on the baseline static checks and the automated
> review, not on these commands.

Documentation is part of the change, not a follow-up: when a task, flag, data
plan, or flow changes, update the docs that name it. The change-surface map in
[`.cursor/skills/doc-consistency/SKILL.md`](.cursor/skills/doc-consistency/SKILL.md)
lists exactly which docs each kind of change touches.

Then commit:

```sh
git add .
git commit -m "feat(scope): describe your change clearly"
```

This repository uses [Conventional Commits](https://www.conventionalcommits.org/)
— `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`, with an optional scope
(e.g. `fix(flow):`, `docs(decision-tables):`).

## 7. Push Your Branch

```sh
git push -u origin my-feature-name
```

GitHub will display a **Compare & pull request** button.

## 8. Open a Pull Request

Target **base branch `main`** (Release 262 / Summer '26, API v67.0). Release
260 work targets `release/260` — see *Branch Information* in the
[README](README.md).

Prefix the PR title with the Conventional Commit type that matches your
commits (`feat:`, `fix:`, `docs:`, `refactor:`, `chore:`), and write a
description that covers:

```
### Summary
Brief explanation of what this change adds or improves.

### Changes
- List key changes
- Mention new files or docs
- Describe any refactoring

### Motivation
Why this change is needed or helpful.

### Testing
Which validations you ran (and against which org, if any).

### Notes
Anything reviewers should know or follow up on.
```

Avoid generic titles like "Update" or "Fix."

## 9. Address Review Feedback

Automated reviewers (GitHub Copilot, Codex) and maintainers comment inline.
Every review comment is handled to completion, and each review round ends with
**zero unresolved threads**.

[`REVIEW.md`](REVIEW.md) is the canonical protocol — how a finding is verified,
how a round is closed out, and why a round's fixes are batched into a single
push. Read it before responding to your first review.

To update your PR:

```sh
git add .
git commit -m "fix: address review feedback"
git push
```

Your PR updates automatically.

## 10. Keep Your Fork Updated

Start each new branch from the latest upstream `main`. This keeps your work
current without pushing to any `main` branch — which
[`AGENTS.md`](AGENTS.md) prohibits:

```sh
git fetch upstream
git checkout -b my-next-feature upstream/main
```

Nothing in this workflow reads your fork's own `main`, so it can stay as it is.
If you would rather keep it current, use your fork's **Sync fork** button on
GitHub instead of pushing from the command line.

## 11. Merge

A maintainer merges your PR after approval and green checks.

## Summary

- Fork the repo, clone your fork, add the upstream remote.
- Set up the toolchain and run `validate_setup`.
- Create a branch — never commit to `main`.
- Make changes following `AGENTS.md`; update the docs your change touches.
- Run the validations for what you changed.
- Push the branch and open a PR against `main`.
- Drive every review round to zero unresolved threads.
- Branch from `upstream/main` for your next change.

## Code of Conduct

Participation in this project is governed by the
[Salesforce Open Source Community Code of Conduct](CODE_OF_CONDUCT.md).

## Security

Do **not** report security vulnerabilities through public GitHub issues — see
[SECURITY.md](SECURITY.md) for the disclosure process.

## License

By contributing, you agree that your contributions will be licensed under the
[Apache License 2.0](LICENSE.txt) that covers this project.
