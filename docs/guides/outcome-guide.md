# Outcome Guide: what you can do with the skills

[Home](../../README.md) · [Documentation index](../index.md)
[Skill catalog](../../.cursor/skills/README.md)

Start from the result you want, not from a skill name. Each section below lists
outcomes, what to ask your coding agent for, and the skill that covers each. The
[skill catalog](../../.cursor/skills/README.md) is the agent's router, organized by task. This guide
is its companion for people: it is organized by outcome and says what you get back.

## How to use this guide

1. **Find your outcome** in the sections below, or in one of the
   [common journeys](#common-journeys).
2. **Name the outcome and its context to your agent.** Say the goal, the release or org
   you target, and whether it may change an org or should only read.
   Example: "Using the billing-operations skill, explain how an invoice run
   differs from an on-demand invoice, and list what I should check afterward."
3. **Read the labels on the answer.** Skills that describe product behavior mark where a
   statement comes from. Tags name the source, usually with its article, path or date:
   `[Help: <article>]` (the checked-in Salesforce Help snapshot), `[Repo: <path>]` (this
   repository's code and data), `[Measured: <date>]` (observed on an org),
   `[Platform behaviour, traced]` (read from platform behavior, not run), or `[inferred]`
   (reasoned, not confirmed). Other sources, such as `[Dev guide: <page>]`, follow the same
   pattern. Treat `[inferred]` and "not measured" as questions to settle on your org
   before you promise them to a customer.

You can read and plan without an org. Anything that changes or queries an org needs
the access the skill names.

## What a skill gives you, and what it does not

| A skill gives you | A skill does not |
|---|---|
| The decisions to make, with the options and their consequences | Make the commercial decision for you |
| The order to do things in, and what each step depends on | Replace a live check: a release not yet generally available can differ from its Help text |
| A verification step: what to query or run to prove it worked | Prove behavior it has not measured; it says "not measured" instead |
| Where this repository already ships the pattern (data plans, flows, templates) | Carry values from your own project; examples use neutral sample values |

## Understand the platform

| I want to… | Ask the agent to… | Skill |
|---|---|---|
| Know which objects exist and how they relate | Explain the objects behind a business concept and write the query | [Data model](../../.cursor/skills/revenue-cloud-data-model/SKILL.md) |
| Call Revenue Cloud APIs | Pick the endpoint, build the request, explain the response | [Business APIs](../../.cursor/skills/rlm-business-apis/SKILL.md) |
| Check a product claim against the documentation | Ground the statement in the Help snapshot and cite the article | [Revenue Cloud docs](../../.cursor/skills/revenue-cloud-docs/SKILL.md) |
| Set up or troubleshoot Contracts (CLM) | Walk contract types, lifecycle states, clauses and templates | [Salesforce Contracts](../../.cursor/skills/salesforce-contracts/SKILL.md) |

## Model the offering

| I want to… | Ask the agent to… | Skill |
|---|---|---|
| Turn commercial offerings into a product catalog | Decide product vs attribute vs component, bundle shape, selling models, catalogs | [Product catalog modeling](../../.cursor/skills/product-catalog-modeling/SKILL.md) |
| Control what can be configured together | Write or debug bundle rules and explain why a rule did not take effect | [Constraint models](../../.cursor/skills/constraint-models/SKILL.md) |
| Load the catalog as data | Author or review an SFDMU data plan with safe reload behavior | [SFDMU data plans](../../.cursor/skills/sfdmu-data-plans/SKILL.md) |

## Price it

| I want to… | Ask the agent to… | Skill |
|---|---|---|
| Set up Salesforce Pricing in an org | Walk enablement, permissions, price books, adjustment schedules, proration, revision policies | [Pricing setup](../../.cursor/skills/pricing-setup/SKILL.md) |
| Configure how a price is calculated | Choose and order pricing elements (discounts, aggregates, revision, and others) | [Pricing procedures](../../.cursor/skills/pricing-procedures/SKILL.md) |
| Wire recipes, procedures and lookup mappings in order | Sequence the layers so a pricing change lands in dependency order | [Pricing wiring](../../.cursor/skills/pricing-wiring/SKILL.md) |
| Edit a pricing, rating or qualification procedure | Read, change and activate an expression set | [Expression sets](../../.cursor/skills/expression-sets/SKILL.md) |
| Fix a price that disagrees with its source data | Check whether a lookup is stale, refresh it, confirm | [Decision tables](../../.cursor/skills/decision-tables/SKILL.md) |
| Feed more data into pricing | Extend a context definition and its mappings | [Context Service](../../.cursor/skills/context-service/SKILL.md) |

## Sell it: quotes, approvals and documents

| I want to… | Ask the agent to… | Skill |
|---|---|---|
| Configure or demonstrate the quote and order line editor | Set columns, groups and action buttons; explain a blank price or reset attribute | [Transaction line editor](../../.cursor/skills/transaction-line-editor/SKILL.md) |
| Quote a multi-year deal with stepped periods | Build and verify a ramp quote and its per-period uplift | [Ramped quotes](../../.cursor/skills/ramped-quotes/SKILL.md) |
| Handle several pricing rounds on one deal | Clone a quote into a round, say what carries over, choose the winning round | [Quote negotiation rounds](../../.cursor/skills/quote-negotiation-rounds/SKILL.md) |
| Add sign-off rules to a quote | Map an approval matrix and test submit, review and recall | [Advanced approvals](../../.cursor/skills/advanced-approvals/SKILL.md) |
| Produce the customer document | Build or fix a `.docx` template and verify generated output | [Document generation](../../.cursor/skills/document-generation/SKILL.md) |
| Fix a document data mapping | Author and debug the OmniDataTransform behind a template | [ODT authoring](../../.cursor/skills/odt-authoring/SKILL.md) |

## Fulfill, bill and collect

| I want to… | Ask the agent to… | Skill |
|---|---|---|
| Orchestrate fulfillment of an order | Design decomposition, steps and dependencies; load them as data | [DRO plans](../../.cursor/skills/dro-plans/SKILL.md) |
| Decide how a line is billed | Choose billing frequency, advance or arrears treatment, milestones and payment terms | [Billing setup](../../.cursor/skills/billing-setup/SKILL.md) |
| Run billing after setup and read it back | Explain schedules, invoice runs and previews, tax, payments, credits and the ledger, and what to query to confirm each | [Billing operations](../../.cursor/skills/billing-operations/SKILL.md) |

Billing is split on purpose: **billing setup** decides how a line bills;
**billing operations** covers what happens once billing runs.

## Meter and rate usage

| I want to… | Ask the agent to… | Skill |
|---|---|---|
| Set up usage resources, units, policies, grants, commitments and wallets | Walk the usage setup and what each piece is for | [Usage setup](../../.cursor/skills/usage-consumption/usage-setup.md) |
| Define rates and how rating finds one | Set up rate cards, entries, tiers and adjustments; trace which table a lookup reads | [Rate management](../../.cursor/skills/rate-management/SKILL.md) |
| Build, rate and verify a consumption demo | Create a usage asset, record usage, rate it and check the result | [Usage and consumption](../../.cursor/skills/usage-consumption/SKILL.md) |
| Bill usage | Route to schedules and invoicing | [Billing operations](../../.cursor/skills/billing-operations/SKILL.md) |

Usage runs through three skills: **usage and consumption** builds and verifies the
scenario, **rate management** owns rates and rating, and **billing operations** owns
the invoice. For a step-by-step walk-through, see the
[usage runbook](usage-consumption-runbook.md).

## Change and renew

| I want to… | Ask the agent to… | Skill |
|---|---|---|
| Know what happens when an asset is amended, swapped, canceled or renewed | Follow a change through reprice, order, activation and the asset | [Asset lifecycle changes](../../.cursor/skills/asset-lifecycle-changes/SKILL.md) |
| Create renewal-ready test assets | Build assets across the renewal windows with lifecycle history | [Renewal asset creation](../../.cursor/skills/renewal-asset-creation/SKILL.md) |

## Generate data, demos and training

| I want to… | Ask the agent to… | Skill |
|---|---|---|
| Produce volume transaction data | Plan, mint and inspect quotes, orders and invoices, and clean up what the skill can remove | [Transaction data harness](../../.cursor/skills/txn-data-harness/SKILL.md) |
| Prepare a demo walkthrough | Generate the per-release demo script | [QB demo script](../../.cursor/skills/qb-demo-script/SKILL.md) |
| Make a clone ready for a hands-on workshop | Capture seeded quotes and configuration, replay and verify | [DF workshop setup](../../.cursor/skills/df-workshop-setup/SKILL.md) |
| Write or refresh enablement exercises | Author exercises grounded in the release documentation | [Release enablement](../../.cursor/skills/release-enablement/SKILL.md) |
| Maintain in-app learning content | Rebuild and verify the learning data plan | [In-app framework](../../.cursor/skills/inapp-framework/SKILL.md) |

## Build and run an environment

| I want to… | Ask the agent to… | Skill |
|---|---|---|
| Set up my workstation | Audit and install the toolchain without breaking it | [Toolchain](../../.cursor/skills/toolchain/SKILL.md) |
| Build or change an org | Run, sequence and flag the build flows | [CCI orchestration](../../.cursor/skills/cci-orchestration/SKILL.md) |
| Repeat a build with progress and resume | Run a harness profile and report | [Build harness](../../.cursor/skills/build-harness/SKILL.md) |
| Build a partner development org | Apply the runtime-only feature overrides and verify they revert | [PDE org build](../../.cursor/skills/pde-org-build/SKILL.md) |
| Connect an agent to an org through MCP | Stand up and inspect the MCP servers and client login | [MCP integration](../../.cursor/skills/mcp-integration/SKILL.md) |
| Add a feature or metadata | Place it in the right directory and order | [Repository integration](../../.cursor/skills/repo-integration/SKILL.md) |
| Pull UX changes made in an org back into source | Capture, review and apply drift | [UX assembly and retrieve](../../.cursor/skills/repo-integration/ux-assembly-retrieve.md) |

## Diagnose and keep it correct

| I want to… | Ask the agent to… | Skill |
|---|---|---|
| Fix a failing build or deploy | Match the symptom to a cause and a fix | [Troubleshooting](../../.cursor/skills/troubleshooting/SKILL.md) |
| Check the schema diagram against an org | Validate, refresh or certify the data-model diagram | [Schema validation](../../.cursor/skills/schema-validation/SKILL.md) |
| Test org setup in a browser | Write and debug Robot Framework automation | [Robot testing](../../.cursor/skills/robot-testing/SKILL.md) |
| Harden Apex security | Enforce CRUD and field-level security and permission sets | [Apex security hardening](../../.cursor/skills/apex-security-hardening/SKILL.md) |

## Contribute

| I want to… | Ask the agent to… | Skill |
|---|---|---|
| Check documentation before a pull request | Compare docs against the code and configuration that changed | [Doc consistency](../../.cursor/skills/doc-consistency/SKILL.md) |
| Add or change a skill | Author, register and test it | [Skill authoring](../../.cursor/skills/skill-authoring/SKILL.md) |
| Handle review comments | Verify each finding, fix the class, reply and resolve | [Audit review](../../.cursor/skills/audit-review/SKILL.md) |

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for the contribution rules.

## Common journeys

Chain skills in this order. Each step names the decision or proof it produces.

**Plan the build of a Revenue Cloud implementation**
1. [Data model](../../.cursor/skills/revenue-cloud-data-model/SKILL.md):
   find the objects the scope touches.
2. [Product catalog modeling](../../.cursor/skills/product-catalog-modeling/SKILL.md):
   decide the catalog shape.
3. [Pricing setup](../../.cursor/skills/pricing-setup/SKILL.md) and
   [pricing procedures](../../.cursor/skills/pricing-procedures/SKILL.md):
   decide how prices are calculated.
4. [Billing setup](../../.cursor/skills/billing-setup/SKILL.md) and
   [rate management](../../.cursor/skills/rate-management/SKILL.md):
   decide how lines bill and usage is rated.
5. [Billing operations](../../.cursor/skills/billing-operations/SKILL.md):
   decide the operate side (invoice runs, tax, payments, ledger).

**Prove quote to cash on a scratch org**
1. [CCI orchestration](../../.cursor/skills/cci-orchestration/SKILL.md): build the org.
2. [Transaction data harness](../../.cursor/skills/txn-data-harness/SKILL.md):
   run a quote through order, activation and invoice.
3. [Asset lifecycle changes](../../.cursor/skills/asset-lifecycle-changes/SKILL.md):
   amend, cancel and renew the result.
4. [Troubleshooting](../../.cursor/skills/troubleshooting/SKILL.md): when a step fails.

**Prepare a usage-based demo**
1. [Usage setup](../../.cursor/skills/usage-consumption/usage-setup.md):
   resources, grants, commitments.
2. [Rate management](../../.cursor/skills/rate-management/SKILL.md): rate cards and rating.
3. [Usage and consumption](../../.cursor/skills/usage-consumption/SKILL.md):
   build the asset, record usage, rate, verify.
4. [Billing operations](../../.cursor/skills/billing-operations/SKILL.md):
   invoice it and read it back.

**Get a clone ready for a hands-on session**
1. [QB demo script](../../.cursor/skills/qb-demo-script/SKILL.md): the walkthrough.
2. [DF workshop setup](../../.cursor/skills/df-workshop-setup/SKILL.md):
   capture, replay and verify the seeded state.
3. [Release enablement](../../.cursor/skills/release-enablement/SKILL.md): the exercises.

## When there is no skill yet

Some areas have no owning skill. Start from
[Revenue Cloud docs](../../.cursor/skills/revenue-cloud-docs/SKILL.md) and the Help snapshot.
The router's [Help area map](../../.cursor/skills/README.md#help-area-to-owning-skill)
lists the current gaps. Ask the agent to say which claims come from Help and which it
infers, and settle the inferred ones on an org before you rely on them.
