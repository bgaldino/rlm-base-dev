# Transaction Data Harness — Contract Index

Live-verified lifecycle contracts are organized by shared behavior and scenario
kind:

- [`docs/contracts-shared.md`](docs/contracts-shared.md) — Environment, object
  describes, terminal-state detection, timing & sequencing rules, permissions,
  and the Composite batching decision.
- [`docs/contracts-sales-txn-quote.md`](docs/contracts-sales-txn-quote.md) —
  Quote-path lifecycle steps (Opportunity → PST place → Order → Activate →
  Usage → Invoice → Post).
- [`docs/contracts-sales-txn-order.md`](docs/contracts-sales-txn-order.md) —
  Direct-order path (PST Order graph, AppUsageAssignment gate, shared
  post-Order tail).
- [`docs/contracts-invoice-ingestion.md`](docs/contracts-invoice-ingestion.md) —
  Standalone-billing ingestion (bypasses the PST spine).
- [`docs/contracts-billing-settlement.md`](docs/contracts-billing-settlement.md) —
  Settlement stages after `invoice_posted` on every kind (credit memo and
  payment applied at the org's application level; platform auto-application
  at post). Line Level live-verified on 264; Header Level not.

Open questions and unverified behaviors continue to live in
[`docs/followups.md`](docs/followups.md).
