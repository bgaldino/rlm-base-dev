# Contract Record Behaviors

Read this when a contract record, its roles or its signature status does something a builder
did not expect. Parent: [salesforce-contracts](SKILL.md). Facts tagged `[Platform behaviour,
traced]` come from reading the 264 platform source and were not run.

## ContractContactRole

- Fields on a 264 org: `ContractId`, `ContactId`, `Role`, `IsPrimary` and system fields. The entity is not
  customizable, not Apex-triggerable and not workflow-enabled, so it takes no custom fields, triggers or
  record-triggered automation; the sales-side `OpportunityContactRole` is customizable and triggerable
  [Measured: 2026-11-26, 264 (USA796), ent-sb0 harness build]. If a model needs extra attributes per role (a lease role with its
  own access, say), keep them on a custom object related to the role's Contract and Contact.
- One contact can hold several roles on one contract: each is its own record. Contract, Contact and Role form
  the unique key [Dev guide: `ContractContactRole` object reference; not in the 264 snapshot].
- [Open: community users can create role records only through the API; not run.]
- There is no `ContractContactRelationship` object.

## E-signature status mapping

The Update Envelope Status action maps the envelope's final status to a contract state
[Help: `ind.sf_contracts_default_contract_states_and_predefined_contract_actions_relationship`]:

| Envelope | Contract state |
|---|---|
| Completed | Signed |
| Declined | Signature Declined |
| Voided, whatever the reason | Negotiating |

An expired envelope is a void, so the contract returns to Negotiating, not Contract Expired; the only path to Contract Expired is
system expiration from Activated. On void the updater copies DocuSign's reason into `DocumentEnvelope.FinalStatusReason`
(a string) [Platform behaviour, traced]. `DocumentEnvelope.Status` values on a 264 org: Sent, Delivered, Declined, Voided,
Completed [Measured: 2026-11-26, 264 (USA796), ent-sb0 harness build]. There is no setting to change the target state.
To separate expiry from a revocation, add a state and a transition and a flow keyed on `FinalStatusReason`
([content-and-migration.md](content-and-migration.md)) [Open: not built; whether a record-triggered flow on `DocumentEnvelope`
fires and whether the second status change in the same transaction is accepted. The object is customizable and Apex-triggerable
on a 264 org (measured); flow support is not].

## Quote-to-contract start date

`createContract`, called by the quote-to-contract flow override in Revenue Settings, defaults `StartDate` to the GMT calendar
date, not the user's or the org's. For a user east of UTC in the early hours the default is yesterday. The start date is the
earliest line start only when that is earlier than the GMT date. `StartDate` stays editable on a Draft contract and `EndDate`
recalculates when `ContractTerm` is set [Platform behaviour, traced; GUS closing summary: working as designed]. To default to local
time, clone the quote-to-contract flow and correct the date after the action [Open: not built; whether a before-save flow on
Contract fires for `createContract` inserts].
