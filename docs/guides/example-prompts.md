# Example Prompts: getting started with your coding agent

[Home](../../README.md) · [Documentation index](../index.md)
[Outcome guide](outcome-guide.md) · [Skill catalog](../../.cursor/skills/README.md)

Copy a prompt, change the parts in angle brackets, and give it to your coding agent
with this repository open. Most prompts name the skill so the agent reads the right
guide first. Find your outcome in the [outcome guide](outcome-guide.md) if none of
these fit.

## Before you start

1. Open this repository in your agent's workspace. Keep the whole repository
   available: skills link to files outside their own folders.
2. Start with the sections marked *no org needed*. They need no Salesforce org and
   change nothing in one.
3. Move to *With an org connected* and *Prepare a demo or workshop* only when you have
   an org connected and know which one the agent may change. Say so in the prompt.

## A good prompt has four parts

| Part | Example |
|---|---|
| **Outcome** | "Explain how an invoice run differs from an on-demand invoice" |
| **Skill** | "Use the billing-operations skill" |
| **Scope** | "Read only. Do not change an org or any file." |
| **Proof** | "Cite the files you used and mark anything you inferred" |

The proof line matters most. Skills that describe product behavior label each claim as
`[Help]`, `[Repo]`, `[Measured]`, `[Platform behaviour, traced]` or `[inferred]`; asking
for the labels keeps the answer honest. Operational skills (builds, data loading,
toolchain) may not label claims; for those, ask the agent to say what it ran or read.

## First prompts: no org needed

**Find the right skill**

```text
Read AGENTS.md and the skill catalog in .cursor/skills/README.md. I want to
<describe your goal in one sentence>. Which skill covers it, which other skills does
it hand off to, and what do I need before I start? Do not change any files.
```

**Learn the data model**

```text
Use the revenue-cloud-data-model skill. Which objects hold <a quote line / an asset /
a billing schedule>, how are they related, and what SOQL would list <the records I
care about>? Cite the files you used.
```

**Check a claim against the documentation**

```text
Use the revenue-cloud-docs skill. A colleague says "<the claim>". Find the Help
article that supports or contradicts it, quote the relevant sentence, and say whether
the claim holds for the release this repository carries.
```

**Understand how a feature fits together**

```text
Use the pricing-procedures skill. In plain language, explain how a list price becomes
a net price on a quote line: which elements run, in what order, and where a discount
is applied. Mark anything you inferred rather than read.
```

## Plan a design: no org needed

**Model a product catalog**

```text
Use the product-catalog-modeling skill. I sell <a software subscription with optional
add-ons and a one-time setup service>. Propose a catalog: what is a product, an
attribute and a component, whether the bundle is static or configurable, and which
selling models apply. List the decisions I still need to make.
```

**Decide how lines are billed**

```text
Use the billing-setup skill. My subscription is sold for <a 12-month term> and the
customer wants to be invoiced <monthly>. What do I need to set so the line is
accepted and billed that way, and what happens if I leave it out?
```

**Choose billing operations**

```text
Use the billing-operations skill. List the choices I make on the operate side after
setup: how invoices are generated, how tax is calculated, how payments are applied,
and how credits and write-offs work. For each, say what to query to confirm it.
```

**Plan usage and rating**

```text
Use the usage-consumption skill (usage-setup.md) and the rate-management skill. I
charge <per unit with volume tiers and a monthly commitment>. Which records do I need
for resources, units, grants and commitments, and which rate card and entries model
the tiers? Show the order to create them in.
```

## Work in this repository: no org needed

**Review a data plan**

```text
Use the sfdmu-data-plans skill. Review the plan in <datasets/sfdmu/... directory> for
SFDMU v5 compliance and idempotency. Run the validator the skill names, and list any
finding with the file and line. Do not change the plan.
```

**Check your setup**

```text
Use the toolchain skill. Audit my local toolchain against what this repository
requires, and tell me what is missing or out of date. Report only; do not install
anything.
```

**Find where something lives**

```text
Read docs/references/repository-layout.md. Where would I add <a new decision table /
a new data plan / a flexipage change>, and which skill describes the steps? Do not
change any files.
```

## With an org connected

State the org and what the agent may change. Use a scratch or sandbox org first.

**Build an org**

```text
Use the cci-orchestration skill. I want to build a scratch org with the default
Revenue Cloud flow. Show me the commands and the feature flags I should consider
before I run anything, and wait for my go before you run a task that changes the org.
```

**Prove a quote reaches an invoice**

```text
Use the txn-data-harness skill on <my scratch org>. Plan a smoke run that takes one
quote to an order, activation and an invoice. List what it will create, run it only
after I confirm, then verify the result with the queries the skill gives.
```

**Explain a price that looks wrong**

```text
Use the decision-tables and pricing-procedures skills on <my org>. Quote line <name>
shows a price that does not match the price book. Check whether a lookup is stale,
read-only first. Tell me what you found before you refresh or change anything.
```

**Test an amendment or renewal**

```text
Use the asset-lifecycle-changes skill on <my org>. Take asset <name>, amend it by
<removing two units>, and follow the change through reprice, order, activation and
the asset. Report what the skill says to expect, what you measured, and any
difference.
```

**Fix a failed build**

```text
Use the troubleshooting skill. This build step failed: <paste the error>. Match it to
a known cause, tell me how you reached that conclusion, and propose the fix. Do not
re-run the build until I agree.
```

## Prepare a demo or workshop: org needed

```text
Use the qb-demo-script skill to generate the demo walkthrough for the release this
repository carries. Then list the setup steps I need on the org before I present, and
which of them need a live check.
```

```text
Use the df-workshop-setup skill. I have a clone that should be workshop-ready. List
what to capture, what to replay and how to verify it before it is templated. Read
only until I confirm.
```

## Tips for better answers

- **Give the release and the org.** Behavior differs between releases, and a live org
  is the final word.
- **Ask for read-only first.** Plan, review the plan, then let the agent act.
- **Ask what is inferred.** Settle inferred or "not measured" items on an org before
  you commit to them.
- **Say what you already know.** "I have already loaded the catalog" saves the agent
  from redoing it.
- **One outcome per prompt.** For a long journey, take the steps in the
  [outcome guide's common journeys](outcome-guide.md#common-journeys) one at a time.
- **Use your own values.** Prompts here use placeholders. Replace them with your
  scenario, and keep customer names and private values out of anything you commit.
