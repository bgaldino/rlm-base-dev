---
name: quote-negotiation-rounds
description: >-
  Model bid or negotiation rounds as quote versions in Revenue Cloud: deep clone
  of a quote (UI action, Clone Sales Transaction Connect API, the
  deepCloneSalesTransaction invocable) and what carries over, naming and
  relating rounds, an internal what-if round that must never be presented or
  ordered, per-round line discounts, per-round approvals (what a clone does to
  approval status, resubmission vs Smart Approvals), and which round syncs to
  the opportunity and becomes the order. Use when a source has several pricing
  rounds per deal, when cloning quotes, or when planning how the winning round
  reaches an order. Line editing: transaction-line-editor. Approval design:
  advanced-approvals. Ramp segments: ramped-quotes.
---

# Quote Negotiation Rounds — Rounds as Quote Versions

Use this skill when a deal moves through pricing rounds (for example Opening, Round 2, an
internal Floor round and Award) and each round needs its own discounts and approval, with
one round becoming the order. Each round is a quote on the same opportunity, made by deep
cloning the previous round. Claims are tagged: `[Help: <article>]` and
`[Dev guide: <article>]` from `docs/salesforce/264/`, `[Repo: <path>]`, and
`[Measured: <date>, 264]` for a live run on one scratch org on that date.
`[Platform behaviour, traced]` marks a rule read from the platform's own logic;
`[Platform behaviour, traced in part]` marks one whose mechanism was read but whose scope,
path or consequence was not established (the text says what is missing).

## Quick Rules

1. **One round = one quote, deep cloned from the previous round, on the same opportunity.**
   The clone keeps the opportunity, groups, lines and line discounts, and starts in Draft
   [Help: `ind.qocal_clone_quotes_and_orders`; Measured: 2026-11-10, 264]. Details and
   the measured carry-over table: [deep-clone.md](deep-clone.md).
2. **Clone headlessly with the Connect API**, `POST /connect/rev/sales-transaction/actions/clone`
   [Dev guide: `connect_resources_clone_sales_transaction`]. For a whole quote, pass the quote
   id as both `recordIds[0]` and `salesTransactionId` [Measured: 2026-11-10, 264]. The invocable
   `deepCloneSalesTransaction` was not available on the org measured
   [Measured: 2026-11-10, 264].
3. **Check the clone before you edit it.** Wait for `CalculationStatus` to leave its clone
   and saving states, then compare the header fields and attributes the round depends on.
   Measured: `Description` and `ExpirationDate` came over blank, and a line with no
   attribute row gained one holding the default [Measured: 2026-11-10, 264]; a custom header
   picklist came back as its default and a custom header checkbox as `false`
   [Measured: 2026-11-12, 264]. A clone is rebuilt from the quote's context definition, so a
   field the definition does not map is expected to come back at its default (one field copied,
   unexplained by the repo's plans) [Platform behaviour, traced in part] ([deep-clone.md](deep-clone.md) → What
   carries over). Write back
   every round header field that differs from the source.
4. **Rename every clone.** It arrives as "<source name> Copy" [Measured: 2026-11-10, 264]. No
   documented field links a clone to its source, so the opportunity and the name carry the
   round order ([deep-clone.md](deep-clone.md) → Relating a clone).
5. **Every round is approved from scratch.** Approval work items aren't copied
   [Help: `ind.qocal_clone_quotes_and_orders`]. Measured: the clone had no submission, the
   repo's approval status field came over blank, and submitting it created a new submission
   while the source's stayed in progress [Measured: 2026-11-10, 264]. Smart Approvals skips
   steps only on a resubmission of the same record ([Approvals per round](#approvals-per-round)).
6. **One round syncs at a time, and only the Award round becomes the order.** Keep the current
   customer-facing round synced. One quote syncs per opportunity: setting
   `Opportunity.SyncedQuoteId` to a new round unsynced the previous one
   [Measured: 2026-11-10, 264]. Sync with `syncQuoteOpportunity`, not that field write. With
   Asynchronous Opportunity Sync on (the measured case; it applies only to quotes with the
   Revenue Cloud pricing type) the write only marks the quote as
   syncing, and no completion step was found in the logic read, so waiting does not help; and `createOrdersFromQuote` refused the quote
   ([Award round to order](#award-round-to-order)) [Measured: 2026-11-12, 264;
   Platform behaviour, traced in part]. Help converts
   an accepted quote into an order [Help: `ind.qocal_create_orders_from_a_quote`].
7. **An internal round needs a gate you build and test.** The docs have no internal-only
   quote; see [internal-round.md](internal-round.md).

## DO NOT

- **DO NOT** edit a round's quote in place to make the next round. That overwrites the
  previous round's numbers, which are the history the rounds exist to keep. (Smart Approvals
  is the exception that needs the same record; weigh it in
  [Approvals per round](#approvals-per-round).)
- **DO NOT** assume a clone is a byte copy. Check header fields, attributes and the round's
  flags after every clone ([deep-clone.md](deep-clone.md)).
- **DO NOT** use `ISCLONE()` to detect a deep clone; it isn't supported for these clones
  [Help: `ind.qocal_clone_quotes_and_orders`].
- **DO NOT** rely on a clone of an internal round staying internal. A custom internal flag
  came back `false` on the clone [Measured: 2026-11-12, 264]; set it again on a clone that
  must stay internal, and check it on one that mustn't ([internal-round.md](internal-round.md)).
- **DO NOT** leave two rounds in approval at once by accident. Recall or cancel the earlier
  round's submission when a new round supersedes it (actions in `advanced-approvals` →
  `actions-and-objects.md`).
- **DO NOT** use `/connect/pcm/deep-clone` for quotes; it clones products
  [Dev guide: `connect_resources_deep_clone`].
- **DO NOT** restate line-editor or approval mechanics here. Link `transaction-line-editor`
  and `advanced-approvals`.

## Entry Conditions

| Task | Use |
|---|---|
| A source runs several pricing rounds per deal and you are mapping them to Revenue Cloud | This skill |
| Clone a quote, through the UI, the Connect API or the invocable; what carries over | This skill → [deep-clone.md](deep-clone.md) |
| A round must never be presented, synced or ordered | This skill → [internal-round.md](internal-round.md) |
| Edit discounts on many lines, header discounts, Group By, filters | `transaction-line-editor` → `runtime-behavior.md` |
| Design the approval matrix, submit, recall, Smart Approvals eligibility | `advanced-approvals` |
| Clone a group-ramp segment (`lineScope`) | `ramped-quotes` |
| The MCP `cloneSalesTransaction` tool and its Apex | `mcp-integration` |
| Amendment, renewal or cancellation quotes | `asset-lifecycle-changes` |

## The round model

| Round | How it starts | Customer sees it | Approval | Syncs / orders |
|---|---|---|---|---|
| Opening | New quote on the opportunity | Yes | Its own submission | Synced while it is current |
| Round 2 | Deep clone of Opening, renamed | Yes | New submission | Sync moves to it |
| Floor (internal) | Deep clone of Round 2, renamed and marked internal | **No** | Its own submission if policy needs sign-off on the floor | **Never** |
| Award | Deep clone of the round the customer accepted (usually Round 2 or a revision of it), renamed | Yes | New submission | Synced; set to Accepted; Create Order |

- **Naming:** "<Opportunity> — R<n> <label>", for example "Example Corp renewal — R3 Floor
  (internal)". Rounds sort by name and read in list views.
- **Relating:** all rounds share the opportunity (the clone keeps it). If reports need a
  round number or the source round, add custom fields; the repo ships none.
- **Award from Floor?** If the award matches the floor's numbers, clone the Floor round and
  check the clone's internal marker is clear after it settles; a measured clone came back
  unflagged [Measured: 2026-11-12, 264] ([internal-round.md](internal-round.md)).

## Discounts per round, per line

A clone starts with the previous round's line discounts [Measured: 2026-11-10, 264]. Change
them in the line editor; `transaction-line-editor` → `runtime-behavior.md` covers:

- bulk edit (select lines, edit one cell, the value goes to all selected) in section 2;
- column filters cover parent lines only, and Group By works in the TLE only, in sections 2
  and 3;
- a header discount measured applying twice (19% for 10%) with an active procedure plan
  and `skipOrgSttPricing` on, in section 5.

Per-line discounts are what the repo's approval level reads: the approval-flags overlay sets
each line's level from its discount on every reprice (`advanced-approvals` → What the repo
ships). Reprice each round before submitting it.

## Approvals per round

- **What a clone does:** no submission and no work items on the clone
  [Help: `ind.qocal_clone_quotes_and_orders`; Measured: 2026-11-10, 264]. The repo's
  `RLM_Approval_Status__c` came over blank while `RLM_Approval_Level__c` (a roll-up of the
  cloned lines) came over set [Measured: 2026-11-10, 264]. So a cloned round shows a level
  and no status until it is submitted. The clone module has no reference to an approval status or
  `IsSyncing` (keyword search; the save through Place Sales Transaction was not traced); whether a custom status field comes back blank depends on whether the context
  definition maps it and whether it is editable, and the platform's defaulting on save was not
  traced [Platform behaviour, traced in part].
- **The previous round stays as it was.** Its submission is untouched by the clone; a
  measured clone and its source were both in progress at once [Measured: 2026-11-10, 264].
- **Resubmission vs Smart Approvals.** Smart Approvals compares a resubmission with the
  *previous submission* and skips steps whose conditions still hold
  [Help: `ind.approvals_smart_approvals`]. It is turned on per approval step, Use Smart
  Approval [Help: `ind.approvals_turn_on_smart_approvals`]; the repo's four steps set
  `CanUseSmartApproval` [Repo: `unpackaged/post_approvals/flows/RLM_Quote_Smart_Approval.flow-meta.xml`].
  Its eligibility rules (earlier submission Rejected or Recalled, reached at least 2 steps,
  at least one step approved, same flow version) are in `advanced-approvals` → `limitations.md`.
  After a full approval, the next submission is a new request, not a resubmission (same file).
  A round that is a new quote has no previous submission, so its first submission is a new
  request; that is inferred from those rules and from the measured clone having none.
  - Use **clone per round** when each round's numbers must be kept.
  - Use **revise and resubmit the same quote** within a round (the customer pushes back,
    the rep adjusts) to get Smart Approvals, before the round is fully approved. A quote whose
    submission has only one step (in the repo, a level-1 quote on Net 30 creates only the Manager item) can't
    qualify.

## Award round to order

1. Sync the Award round: Start Sync on the quote [Help:
   `ind.qocal_considerations_syncing_quotes_and_opportunities_in_revenue_cloud`]. Sync runs
   quote to opportunity only, flattens bundles and drops attributes (same article). With
   Asynchronous Opportunity Sync on, flows call `syncQuoteOpportunity`
   [Dev guide: `actions_obj_sync_quote_opportunity`]. The repo's quote page has the
   `SyncQuote` action [Repo: `templates/flexipages/base/RLM_Quote_Record_Page.flexipage-meta.xml`],
   but the platform hides it while Asynchronous Opportunity Sync is on, which `post_utils` turns
   on: the record actions API offered it with the setting off and not with it on, on the same org
   [Measured: 2026-11-12, 264]. In the UI, use the repo's Sync to Opportunity action, which calls
   `syncQuoteOpportunity` [Repo: `unpackaged/post_utils/flows/RLM_SyncQuoteToOpportunity.flow-meta.xml`].
   Headlessly, call `syncQuoteOpportunity` with `quoteId`. Measured: it returned no `aotId`, and
   the opportunity had its products when read after the call (no timing recorded). Writing
   `Opportunity.SyncedQuoteId` instead left `IsSyncing` true with no opportunity products, and
   `createOrdersFromQuote` then refused the quote as "currently syncing with its opportunity
   and has uncommitted changes" [Measured: 2026-11-12, 264]. The Start Sync button was not
   measured. Traced: with Asynchronous Opportunity Sync on, the field write marks the quote
   `IsSyncing` and skips the line copy, which only the action performs. For a standard quote the
   action copies inline (no tracker id) and stamps the opportunity's last sync time; for a large
   transaction it returns a tracker id and you must wait for the job
   [Platform behaviour, traced]. Create Order refuses the quote while it is marked
   `IsSyncing` and was changed after that last sync time (or the opportunity has none). The quote
   stays marked `IsSyncing` after a good sync (a code comment says this is intended; not
   otherwise confirmed); completion is "last sync time is not
   earlier than the quote's last modified time", not `IsSyncing` false. So any later edit to the
   quote, including a system or pricing save, needs another sync before ordering. Which saves
   change the quote's last modified time was not established
   [Platform behaviour, traced in part]. The check applies only with Asynchronous Opportunity
   Sync on; without it the field write is expected to run an older inline sync and order
   creation not to check sync state [inferred: only the early return and the order-side guard
   were read]. The setting is declared with no default-on attribute [Platform behaviour, traced], so it
   is expected to be off until set; whether a fresh 264 org ships it on was not established. The
   `syncQuoteOpportunity` action's access check is that same setting. This repo's `post_utils`
   settings bundle turns it on (`enableAsynchronousQuoteOpportunitySync`); on an org built
   another way, read that setting.
2. Set it to Accepted, then Create Order [Help: `ind.qocal_create_orders_from_a_quote`], or
   `createOrdersFromQuote` with `quoteId` [Dev guide: `actions_obj_create_orders_from_quote`].
   `createOrderFromQuote` is deprecated from API 65.0 [Dev guide: `actions_obj_create_order_from_quote`].
   The order `createOrdersFromQuote` created was Draft with `EffectiveDate` = the day it ran,
   not the quote's start date (future start 2027-01-01) [Measured: 2026-11-12, 264]. Traced
   in the header-creation logic for a single order: `EffectiveDate` is the earlier of the
   creation time and the earliest line start date on the quote, so a future start gives today
   and a past start gives that earlier date; lines with no start date are ignored, and with none
   it is the run date [Platform behaviour, traced in part]. The request schema and the
   split-order processors were not read, so with split orders each order may take its own
   earliest date; industry-specific order creation and time-zone conversion were not checked.
   Help says the start date defaults to the current date and that a future-dated contract
   errors, while the measured future start gave today with no error. To backdate an order, set
   past line start dates before creating it; read the date back before activating.
   The create-order validations traced do not compare `Quote.Status` (not run against a Draft
   or Rejected quote); this differs from the Help wording about converting an accepted quote
   [Platform behaviour, traced in part]. The refusals traced are other preconditions (sync
   state above, pending revenue async operations, a failed validation result, a calculation
   status in progress or failed, unmet required-to-enter lines, an invalid configuration, the
   maximum orders per quote, bundle/ramp/usage/group integrity checks, the large-transaction
   restriction). A declarative flow or validation rule on Quote or Order, or an approval you
   wired, can still stop it.
3. Close out the other rounds: recall open submissions; set customer-facing rounds that
   lost to Denied if your process tracks that.

## Examples

### Example 1 — Map a four-round workbook

Source: each deal has Opening, Round 2, Floor (internal) and Award tabs, each with its own
discount per product line and an approval level.

1. Opening = a new quote. Load lines and discounts; reprice; submit.
2. Round 2 = Connect clone of Opening; rename; change discounts with bulk edit; reprice;
   recall Opening's submission if still open; submit.
3. Floor = clone of Round 2; rename "(internal)"; set the flag; never sync.
4. Award = clone of the accepted round; rename; clear any internal flag; submit; sync;
   Accepted; Create Order.
5. Golden test: each round's totals match the workbook's tab for that round.

### Example 2 — Headless clone

```bash
sf api request rest "/services/data/v68.0/connect/rev/sales-transaction/actions/clone" \
  -X POST --target-org <sf_alias_or_username> \
  -b '{"recordIds":["<QUOTE_ID>"],"salesTransactionId":"<QUOTE_ID>"}'
# response .salesTransactionId = the new quote; then:
sf data query --target-org <sf_alias_or_username> -q "SELECT Name, Status, CalculationStatus, \
  OpportunityId, IsSyncing FROM Quote WHERE Id = '<NEW_QUOTE_ID>'"
```

## Validation Checks

After each clone, on the new quote:

```sql
SELECT Name, Status, CalculationStatus, OpportunityId, IsSyncing, ExpirationDate, Description
  FROM Quote WHERE Id = '<NEW>'
SELECT Id, Name FROM QuoteLineGroup WHERE QuoteId = '<NEW>'
SELECT LineNumber, QuoteLineGroupId, Quantity, Discount, NetUnitPrice, TotalPrice
  FROM QuoteLineItem WHERE QuoteId = '<NEW>' ORDER BY LineNumber
SELECT QuoteLineItemId, AttributeDefinition.Name, AttributeValue
  FROM QuoteLineItemAttribute WHERE QuoteLineItem.QuoteId = '<NEW>'
SELECT Id, Status FROM ApprovalSubmission WHERE RelatedRecordId = '<NEW>'
```

- Run the same queries on the source and compare: line counts, discounts, totals, groups,
  attributes, and every header field the round depends on.
- `CalculationStatus` is settled (not a clone, saving or queued state) before any edit.
- Only one round has `IsSyncing = true`, and it is the current customer-facing round; the
  opportunity has `OpportunityLineItem` rows from it (none means the sync didn't finish).
- The internal round has its marker and no Presented or Accepted status.
- For skill edits: `python scripts/ai/analyze_agent_tooling.py check`.

## Open questions

Not measured; settle on a live org before relying on them:

- Whether Asynchronous Opportunity Sync is on by default in a fresh 264 org (live check: read
  the setting on a fresh org).
- Why one custom header field copied although no context plan in this repo maps it (the org's
  active definition was not read; a mapping there is the first thing to check).
- Whether a mapped but non-editable, formula or output-only field survives a clone, and how a
  large (async) transaction clone carries fields ([deep-clone.md](deep-clone.md) → What carries over).
- Whether Create Order refuses a Draft or Rejected quote (not run live).
- Whether the `deepCloneSalesTransaction` invocable needs anything beyond
  `enableTransactionCloning`, and whether it behaves like the Connect API.
- Whether `options.recordTypeId` sets the clone's record type.
- Whether an object state definition can govern `Quote.Status`.
- What a clone does to bundles, ramp segments, header discounts and `QuoteLinePriceAdjustment`
  rows.

## Sub-files

- [deep-clone.md](deep-clone.md): read before cloning a quote or automating clones. Routes,
  response and completion, what carries over (documented and measured), relating a clone.
- [internal-round.md](internal-round.md): read when a round must never be presented,
  synced or ordered. Options, which are documented, which are design and what was measured,
  and a recommended combination.
