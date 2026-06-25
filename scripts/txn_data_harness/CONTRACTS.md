# Transaction Data Harness — Contracts (moved)

The single-file contract record has been split per kind. See
[`docs/`](docs/README.md) for the new layout:

- [`docs/contracts-shared.md`](docs/contracts-shared.md) — Environment, object
  describes, terminal-state detection, timing & sequencing rules, permissions,
  Phase 5 decision.
- [`docs/contracts-sales-txn-quote.md`](docs/contracts-sales-txn-quote.md) —
  Quote-path lifecycle steps (Opportunity → PST place → Order → Activate →
  Usage → Invoice → Post).
- [`docs/contracts-sales-txn-order.md`](docs/contracts-sales-txn-order.md) —
  Direct-order path (stub; populated after Phase 0 live probes).
- [`docs/contracts-invoice-ingestion.md`](docs/contracts-invoice-ingestion.md) —
  Standalone-billing ingestion (bypasses the PST spine).

Open questions and unverified behaviors continue to live in
[`FOLLOWUPS.md`](FOLLOWUPS.md).
