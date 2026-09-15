# Revenue Cloud Base Foundations

**Agent skills, reference data, and automation for Salesforce Revenue Cloud.**

Give your coding agent practical guidance for working with Revenue Cloud: explore
its data model, configure pricing and product rules, build usage scenarios, and
troubleshoot implementations. The skills connect to the scripts, Salesforce
metadata, datasets, and reference documentation in this repository.

**[Browse the skills](.cursor/skills/README.md)** ·
**[Explore the documentation](docs/index.md)** ·
**[Build an environment](#build-and-configure-an-org)**

**This branch:** Release 264 (Winter '27), API v68.0.
See [branch information](#branch-information) before choosing an org or release.

## Start with a skill

1. **Clone or download this repository** and open it in your coding agent's workspace.
2. **Give the agent a task.** Start with the prompt below or pick a capability from the table.
3. **Follow the selected skill.** It links to the relevant references, tools, and verification steps.

```text
Read AGENTS.md and the skill catalog in .cursor/skills/README.md.
Choose the relevant skill, then use the repository's references to explain
how products, pricing, and usage grants relate. Cite the files you use.
```

The skills are Markdown guides that any coding agent with repository-file access
can read. They live under `.cursor/skills/` for historical reasons. Use the prompt
above with Cursor, Claude Code, Codex, GitHub Copilot, or another file-capable agent;
native skill discovery varies by tool. [AGENTS.md](AGENTS.md) provides the shared
project instructions and safety rules.

You can explore the checked-in guides and references without connecting a Salesforce
org. Running scripts or changing an org requires the tools and access described by
the selected skill. Keep the full repository available: skills reference files
outside their own folders.

| I want to… | Start here |
|---|---|
| Understand Revenue Cloud objects and relationships | [Data model](.cursor/skills/revenue-cloud-data-model/SKILL.md) |
| Build integrations and work with Revenue Cloud APIs | [Business APIs](.cursor/skills/rlm-business-apis/SKILL.md) |
| Configure pricing recipes and procedures | [Pricing wiring](.cursor/skills/pricing-wiring/SKILL.md) · [Expression sets](.cursor/skills/expression-sets/SKILL.md) |
| Author product configuration rules | [Constraint models](.cursor/skills/constraint-models/SKILL.md) |
| Extend context definitions and mappings | [Context Service](.cursor/skills/context-service/SKILL.md) |
| Build and verify usage-based consumption scenarios | [Usage and consumption](.cursor/skills/usage-consumption/SKILL.md) |
| Create document templates and data mappings | [Document generation](.cursor/skills/document-generation/SKILL.md) |
| Diagnose a build or deployment problem | [Troubleshooting](.cursor/skills/troubleshooting/SKILL.md) |

For more workflows, including decision tables, ramped quotes, renewal assets, and
data loading, see the **[complete skill catalog](.cursor/skills/README.md)**.

## What this repository provides

Alongside the skills, Foundations automates the creation and configuration of
Salesforce environments for Revenue Cloud, formerly Revenue Lifecycle Management (RLM).

- **Repeatable environment builds:** CumulusCI tasks and flows deploy metadata,
  load data, and configure features using Salesforce CLI, Python, Apex, and browser automation.
- **Salesforce configuration:** metadata, permissions, flows, and UX templates for
  product catalogs, pricing, quoting, fulfillment, billing, and related capabilities.
- **Reference datasets:** QuantumBit product and pricing data, SFDMU plans,
  constraint models, and context-definition plans.
- **Tools and evidence:** API references, data-model diagrams, checked-in Salesforce
  documentation, validation scripts, and workflow-specific verification guidance.

The main build flow is `prepare_rlm_org`. Feature flags select which capabilities
are included. Read the [build-process guide](docs/guides/prepare-rlm-org-build-guide.md)
for how these pieces fit together, or the [repository map](docs/references/repository-layout.md)
to locate the source files.

## Build and configure an org

Choose the setup path that fits your workstation:

| Path | Guide |
|---|---|
| Containerized toolchain or VS Code / Cursor devcontainer | [Docker environment](docker/README.md) |
| Install tools locally and authenticate | [Local installation](docs/guides/local-installation.md) |
| Maintain or replicate an existing local toolchain | [Developer environment](docs/guides/dev-environment-setup.md) |

Building requires a Salesforce org with Revenue Cloud licenses and appropriate
metadata-deployment permissions; scratch-org creation also requires a Dev Hub.
The data-loading toolchain requires **SFDMU v5.6.4 or later**.
See the [complete prerequisites](docs/guides/local-installation.md#prerequisites).

Once your tools and org connection are ready, use the
[org quick start](docs/guides/org-operations.md#quick-start). For repeatable builds
with progress reporting and resume support, use the [build harness](docs/guides/build-harness.md).

### macOS Environment Setup

Follow the [local installation guide](docs/guides/local-installation.md#macos-environment-setup-homebrew--pyenv--nvm)
for the step-by-step macOS setup referenced by the contributing guide.

## Documentation

| Find… | Reference |
|---|---|
| All guides and feature documentation | [Documentation index](docs/index.md) |
| Task names and options | [Generated task reference](.cursor/skills/cci-orchestration/tasks-reference.md) |
| Flow steps and conditions | [Generated flow reference](.cursor/skills/cci-orchestration/flows-reference.md) |
| Feature flags and defaults | [Generated flag reference](.cursor/skills/cci-orchestration/feature-flags.md) |
| Data plans, validation, and dataset READMEs | [Data-plan guide](docs/guides/data-plans.md) |
| Deployment examples and troubleshooting | [Org operations](docs/guides/org-operations.md) |
| Revenue Cloud API collections | [Postman guide](postman/README.md) |
| Data-model diagrams | [ERD guide](docs/erds/README.md) |
| Hands-on learning | [Enablement exercises](docs/enablement/README.md) |

## Contributing

Contributions go through a fork and a pull request — see
**[CONTRIBUTING.md](CONTRIBUTING.md)** for the full workflow: environment setup,
the validation commands to run before pushing, commit/PR conventions, and how
review rounds are handled.

When contributing to this project:

1. Follow the existing code structure and patterns
2. Document custom tasks in `cumulusci.yml` and create example documentation
3. Test changes with appropriate scratch org configurations
4. Update this README if adding new prerequisites or workflows
5. Add detailed READMEs for new data plans
6. Register new tasks and flows in `cumulusci.yml`

Participation is governed by the [Code of Conduct](CODE_OF_CONDUCT.md). Report
security vulnerabilities privately through the process in
[SECURITY.md](SECURITY.md) — never through a public GitHub issue.

## Branch Information

- **`264`**: Salesforce Release 264 (Winter '27, API v68.0) — **active development line**, cut from `main` at `49a494de`
- **`main`**: Salesforce Release 262 (Summer '26, API v67.0) — current GA target
- **`release/262`**: Frozen Release 262 GA reference, snapshotted from `main` at `49a494de`
- **`release/260`**: Salesforce Release 260 (Spring '26, GA) — prior GA reference
- **`262`**: The original 262 upgrade branch, retained for history. It is *behind* `main` — use `release/262` for the 262 reference, not this branch.
- Other branches exist for different release scenarios and preview features

New work targets `264`. `main` receives the promotion merge once 264 is certified, mirroring how `262` was merged into `main` via PR #208.

## Project Governance & Support

- [License](LICENSE.txt) — Apache License, Version 2.0
- [Code of Conduct](CODE_OF_CONDUCT.md) — Salesforce Open Source Community Code of Conduct
- [Contributing](CONTRIBUTING.md) — fork, branch, validate, pull request
- [Security](SECURITY.md) — report vulnerabilities privately, never through a public issue
- [Review Guide](REVIEW.md) — how pull requests are reviewed in this repository

For questions or problems, open an issue or a pull request in this repository.

## License

This project is licensed under the **Apache License, Version 2.0** — see
[`LICENSE.txt`](LICENSE.txt) for the full text.

```
Copyright (c) 2026 Salesforce, Inc.
All rights reserved.
```
