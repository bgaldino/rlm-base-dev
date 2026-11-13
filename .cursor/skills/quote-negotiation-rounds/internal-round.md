# An Internal What-If Round

Read this when one round (a walk-away price, a what-if) must never be presented to
the customer, synced to the opportunity forecast, or turned into an order. Parent:
[quote-negotiation-rounds](SKILL.md).

**Nothing in the 264 docs marks a quote as internal-only, and this repo ships nothing for
it.** Every option below is either a documented building block or a design you add and then
test. Each says which.

## Options

| Option | Status | What it gives | What it doesn't |
|---|---|---|---|
| **Quote `Status`** | Documented values. On 264 the picklist is Draft, Needs Review, In Review, Approved, Rejected, Presented, Accepted, Denied [Measured: 2026-11-10, 264, describe]. Help converts an **accepted** quote into an order [Help: `ind.qocal_create_orders_from_a_quote`], and its example contract-creation flow triggers on Accepted [Help: `ind.qocal_create_contracts_using_a_flow`] | A visible marker: keep the round out of Presented and Accepted | Nothing stops a user from changing it. The create-order validations traced do not compare `Quote.Status` (not run against a Draft or Rejected quote), which differs from the Help wording about converting an accepted quote [Platform behaviour, traced in part]; not run live, so treat the marker as a convention only. A deep clone resets status to the first value of the Status picklist, normally Draft [Help: `ind.qocal_clone_quotes_and_orders`; Platform behaviour, traced], so the marker never travels to the next round |
| **Record type** | Quote record types are standard platform; the clone API takes `options.recordTypeId` [Dev guide: `connect_requests_clone_options_input`]. This repo ships no Quote record type (the org measured has only Master) [Measured: 2026-11-10, 264, describe] | A separate page layout or Lightning page without Generate Document, Create Order and Sync | The dev guide describes `recordTypeId` as the "record type related to the record to clone": whether it sets the clone's record type is not measured. Adding one means assigning its page layout and a default record type per profile |
| **Object state definition** | Documented for **orders**: states, allowed transitions and custom permissions per transition [Help: `ind.qocal_order_lifecycle_management_using_object_state_definitions`, `ind.qocal_create_object_state_transitions`]. The dev guide's `AppUsageType` description mentions quotes [Dev guide: `quote_and_order_capture_fields_on_object_state_definition`] | Enforced status transitions, if it applies to quotes | No Help article covers a quote lifecycle; whether one enforces `Quote.Status` is not measured |
| **Flag plus validation rules** | Design pattern, not shipped by this repo; measured on one org [Measured: 2026-11-12, 264] | A custom checkbox (for example `Internal_Round__c`) and a rule on each object the round must not reach. Measured: quote rules refused Status Presented and Accepted on a flagged quote, which stayed Draft; an Opportunity rule on `SyncedQuote.<flag>` refused a write of `Opportunity.SyncedQuoteId`, and `syncQuoteOpportunity` returned `UNKNOWN_EXCEPTION` carrying the sync rules' message (the Opportunity rule and the quote's `IsSyncing` rule shared one message, so the run doesn't show which refused the action. Traced: the action saves the Opportunity with the synced quote, and a hook in that save then saves the Quote with `IsSyncing` true, remapping its errors onto the Opportunity, so either rule can produce the message; which evaluates first is not established, so give the two rules distinct messages and read the message to see which refused [Platform behaviour, traced in part]), and the opportunity didn't sync to the flagged quote; an Order rule on `Quote.<flag>` made `createOrdersFromQuote` return the rule's message, and no order was created. A quote rule refusing the flag while `IsSyncing` is true stops a synced quote being flagged afterwards | Proposal and document generation had no server-side guard in the run measured (the proposal action is a screen flow); they were only hidden by page visibility, checked in the deployed page metadata, not in the UI. A deep clone of a flagged round came back with the flag `false`, so the clone is customer-facing at once ([deep-clone.md](deep-clone.md)) |

## Recommended combination

1. **Mark** the round with a flag field and the parent skill's name convention ("<Opportunity> — R3 Walk-away (internal)").
2. **Block** with validation rules on the flag: on Quote, Status Presented or Accepted, and the
   flag set while `IsSyncing` is true; on Opportunity, a `SyncedQuote` whose flag is set; on
   Order, a `Quote` whose flag is set. Each held in the run measured above: the status writes,
   the flag on a synced quote, the `SyncedQuoteId` write, `syncQuoteOpportunity` and
   `createOrdersFromQuote`. A direct `Order` insert was not tried.
3. **Hide** Generate Document, proposal and PDF creation, Email, Sync and Create Order on the
   page when the flag is set. For documents this was the only gate measured; check it in the UI.
4. **Set the flag again on every clone that must stay internal.** A clone of a flagged round
   comes back unflagged, so a clone of the internal round is customer-facing until you do.
   For the next customer-facing round, check the clone's flag is clear after it settles.
5. **Test each gate** on your org (status change, sync, document, order) and record the
   result. Until then, say "untested" in the build plan.

Steps 1–4 are a design, not documented behaviour. The rules in step 2 and the unflagged clone
in step 4 were measured on one org [Measured: 2026-11-12, 264]; step 5 is what makes them
facts on yours.
