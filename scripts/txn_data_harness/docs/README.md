# Transaction Data Harness — Contract Documentation

> **Status:** implemented and live-verified against a Revenue Cloud R262
> scratch org with the bundled QB demo dataset (API v67.0). `lifecycle.py` is a
> direct transcription of the endpoint bodies, response shapes, async barriers,
> and sequencing rules captured here. Re-verify against a live org and update
> this file before changing lifecycle behavior.
>
> **Scope guard.** Only behaviors that have been **probed live** belong in
> these files. Open questions, anomalies awaiting characterization, and
> probes that would generalize a finding live in
> [`../FOLLOWUPS.md`](../FOLLOWUPS.md) — pair-edit the two when a probe lands a
> new answer (write the verified contract here, move the open entry there
> into *Resolved*).
>
> **Evidence notebook.** Unlike the user-facing README and guide, these files may
> include observed org aliases, run ids, invoice numbers, dates, and record
> identifiers as proof of a probe. Treat those values as evidence only, never as
> reusable inputs.

## Document index

| File | Covers |
|------|--------|
| [`contracts-shared.md`](contracts-shared.md) | Environment, object describes, terminal-state detection, timing/sequencing, permissions, Phase 5 decision |
| [`contracts-sales-txn-quote.md`](contracts-sales-txn-quote.md) | Quote-path lifecycle steps (Opportunity → PST place → Order → Activate → Usage → Invoice → Post) |
| [`contracts-sales-txn-order.md`](contracts-sales-txn-order.md) | Direct-order path (stub — populated after Phase 0 live probe) |
| [`contracts-invoice-ingestion.md`](contracts-invoice-ingestion.md) | Invoice ingestion path (standalone billing, bypasses PST spine) |
