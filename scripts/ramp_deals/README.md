# Ramped-quote helper scripts

A self-contained toolkit for authoring **ramped Revenue Cloud quotes** headlessly.
A ramped quote is a pattern over two ordinary sObjects — `QuoteLineGroup` (the
segment) and `QuoteLineItem` (the line inside it) — driven through the **Place
Sales Transaction** Connect API with a `groupRampAction`. There is **no ramp
sObject**: the ramp rides inline in the `place` body, and additional segments come
from a `clone` call.

Auth is delegated to the **`sf` CLI** (`sf api request rest --target-org …`), so
**no access token is ever handled or passed**. `--target-org` is always the
**SF CLI alias** (e.g. `rlm-base__sdb39`), **never** the CCI alias.
Pinned to Release 264 / API v68.0.

Full design lives in `.agents/artifacts/ramped-quote-skill/PLAN.md` (§4 data model,
§4.5 ramp rules, §8 call sequence) and the operational
`RUNBOOK-ramp-deals.md` beside it.

## Independent of the CCI tasks

This package imports **nothing** from `tasks/`, and nothing under `tasks/` imports
from it. It mirrors the architecture of `scripts/expression_sets/`: pure,
dependency-free core modules shared by the verb CLIs and the offline tests, so no
ramp logic is implemented twice. The pure modules pull in no `requests` /
CumulusCI / `sf` CLI — they operate on plain dicts and dates, so they unit-test
with no org.

Enums and field legality here were verified live on 264 / v68.0
(`.agents/artifacts/ramped-quote-skill/probe-264/E9-ramp-field-summary.md`).

## Layout

**Pure core (no org, no auth — plain dicts in, plain dicts out):**

| Module | Purpose |
|--------|---------|
| `_schedule.py` | Ramp-schedule math: calendar-month sizing (not `timedelta`), contiguity, the ≤12-paid-segment ceiling, the `FreeTrial` (not `Trial`) enum. |
| `_payload.py` | Place Sales Transaction body builders — `build_place_create`, `build_edit_group`, `build_clone_segment`, `build_group_ramp_action` — with read-only-field and enum rejection *before* the call. |
| `_verify.py` | `CalculationStatus` polling sets (incl. the 264-new `CloneInProgress`/`CloneFailed`) + the read-back ramp invariants (`verify_quote`). |

**Transport / orchestration (org, via `sf` CLI):**

| Module | Purpose |
|--------|---------|
| `_client.py` | Shared `sf`-CLI transport + the injectable `Transport` seam (a fake substitutes it in tests). |
| `_resolve.py` | Name→Id resolution (Account, Pricebook2, Product2/SKU, PricebookEntry) + `read_quote` (loads a quote into the exact shape `_verify` expects). |
| `_lifecycle.py` | `RampLifecycle`: place → poll → EditGroup → clone×N → read back → verify. |

**Verb CLIs:**

| Script | Org? | Purpose |
|--------|------|---------|
| `plan_ramp_schedule.py` | **None** | Plan + validate a schedule (pure). The natural dry-run before authoring, and the MCP `ramp_plan_schedule` tool. |
| `build_ramp_quote.py` | **Mutates** | Author a full multi-segment ramped quote end-to-end. **Preview by default; `--confirm` to write.** |
| `add_ramp_segment.py` | **Mutates** | Add one segment by cloning the quote's last segment. Preview by default. |
| `edit_ramp_segment.py` | **Mutates** | Edit a segment's dates / type / sort order via EditGroup. Preview by default. |
| `delete_ramp_quote.py` | **Mutates** | Delete a quote (destructive; disposable orgs only). Requires `--confirm` **and** `--yes-delete <id>`. |
| `inspect_ramp_quote.py` | Read-only | Dump a quote's segment table + each line's `RampIdentifier`/`SegmentIdentifier`. |
| `verify_ramp_quote.py` | Read-only | Run the ramp invariants; exit non-zero on any failure (CI/post-build gate). |

## Quick start

```bash
# 1. Plan the schedule — pure, no org. Prove the term is valid before touching an org.
python scripts/ramp_deals/plan_ramp_schedule.py \
    --start-date 2026-01-01 --segment-type Yearly --segments 3

# 2. Preview the build (resolves ids + logs the call sequence; NO write).
python scripts/ramp_deals/build_ramp_quote.py \
    --target-org rlm-base__sdb39 \
    --account "Laulima" --segment-type Yearly --segments 3 --start-date 2026-01-01 \
    --line SKU-PLATFORM:10 --line SKU-SUPPORT:1

# 3. Author it for real.
python scripts/ramp_deals/build_ramp_quote.py ... --confirm --json

# 4. Inspect / verify the result.
python scripts/ramp_deals/inspect_ramp_quote.py --target-org rlm-base__sdb39 --quote-id 0Q0...
python scripts/ramp_deals/verify_ramp_quote.py --target-org rlm-base__sdb39 --quote-id 0Q0... \
    --expected-segments 3
```

## Tests

```bash
python tests/test_ramp_deals_toolkit.py     # offline, no org, no pytest
```

The pure core is exercised directly; `_resolve` and `_lifecycle` are exercised
against a `FakeTransport` (canned SOQL, recorded connect calls) so the full
place→EditGroup→clone→verify sequence — including polling terminal/unknown/timeout
and the call-order assertions — runs with no org.

## Safety model

- **Preview by default.** `build_ramp_quote.py` runs `Transport(dry_run=True)`
  unless `--confirm` — mutating verbs are logged and skipped, reads still execute,
  so a preview resolves real ids and shows the real call sequence without writing.
- **Read-only verbs never mutate** (`inspect`, `verify`, `plan`).
- **The payload builders reject bad input before the call**: read-only /
  system-generated fields (`RampIdentifier`, `SegmentIdentifier`, `TotalPrice`, …)
  and off-enum segment types / group-ramp actions raise rather than round-trip a
  doomed request.
- **`unknown` status is not success.** The poller stops on a `CalculationStatus`
  the `_verify` sets don't recognize rather than assuming completion.

## Status / open work

The pure core + transport + orchestration + all seven verb CLIs
(`plan`/`build`/`add`/`edit`/`delete`/`inspect`/`verify`) are complete and
offline-tested. **Not yet done:** a live 264 end-to-end run (needs the writable org
and the `IsLargeDeal` precondition from the research briefing) — the mutating verbs
have not been exercised against an org, only offline against a fake transport;
`render_ramp_card.py`; and the `mcp/ramp_deals_server/` façade + `_auth.py` (gated on
research briefing Q1/Q2/Q6 — see `RUNBOOK-ramp-deals.md` §3).
