# An Internal What-If Round

Read this when one round (a floor, a walk-away price, a what-if) must never be presented to
the customer, synced to the opportunity forecast, or turned into an order. Parent:
[quote-negotiation-rounds](SKILL.md).

**Nothing in the 264 docs marks a quote as internal-only, and this repo ships nothing for
it.** Every option below is either a documented building block or a design you add and then
test. Each says which.

## Options

| Option | Status | What it gives | What it doesn't |
|---|---|---|---|
| **Quote `Status`** | Documented values. On 264 the picklist is Draft, Needs Review, In Review, Approved, Rejected, Presented, Accepted, Denied [Measured: 2026-11-10, 264, describe]. Help converts an **accepted** quote into an order [Help: `ind.qocal_create_orders_from_a_quote`], and its example contract-creation flow triggers on Accepted [Help: `ind.qocal_create_contracts_using_a_flow`] | A visible marker: keep the round out of Presented and Accepted | Nothing stops a user from changing it. Whether Create Order refuses a non-Accepted quote is not measured. A deep clone resets status to Draft [Help: `ind.qocal_clone_quotes_and_orders`], so the marker never travels to the next round |
| **Record type** | Quote record types are standard platform; the clone API takes `options.recordTypeId` [Dev guide: `connect_requests_clone_options_input`]. This repo ships no Quote record type (the org measured has only Master) [Measured: 2026-11-10, 264, describe] | A separate page layout or Lightning page without Generate Document, Create Order and Sync | The dev guide describes `recordTypeId` as the "record type related to the record to clone": whether it sets the clone's record type is not measured. Adding a record type changes every quote page assignment |
| **Object state definition** | Documented for **orders**: states, allowed transitions and custom permissions per transition [Help: `ind.qocal_order_lifecycle_management_using_object_state_definitions`, `ind.qocal_create_object_state_transitions`]. The dev guide's `AppUsageType` description mentions quotes [Dev guide: `quote_and_order_capture_fields_on_object_state_definition`] | Enforced status transitions, if it applies to quotes | No Help article covers a quote lifecycle; whether one enforces `Quote.Status` is not measured |
| **Flag plus validation rule** | Design pattern, not shipped by this repo and not measured | A custom checkbox (for example `Internal_Round__c`) and a validation rule that refuses Status Presented or Accepted while it is set. Hide presentation actions with Lightning page visibility on the same field | A validation rule fires on a quote save. Starting sync writes the opportunity, and creating an order writes a new order, so neither is covered unless you also guard those objects. Whether a deep clone copies the flag is unknown: one editable custom field copied; a read-only custom field and two standard fields did not ([deep-clone.md](deep-clone.md)) |

## Recommended combination

1. **Mark** the round with a flag field and a name convention ("Round 3 — Floor (internal)").
2. **Block** Presented and Accepted with a validation rule on the flag.
3. **Hide** Generate Document, Email, Sync and Create Order on the page when the flag is set.
4. **Never clone the next customer-facing round from the internal one** without clearing the
   flag on the clone and checking it after the clone settles.
5. **Test each gate** on a scratch org (status change, sync, document, order) and record the
   result. Until then, say "untested" in the build plan.

Steps 1–4 are a design, not documented behaviour; step 5 is what turns them into facts.
