# Multicurrency build: currency inheritance flows and rate refresh

> Sub-file of `.cursor/skills/pricing-wiring/SKILL.md`. Why a lookup must pass `CurrencyIsoCode`, and the
> wrong-currency symptoms: [`../pricing-setup/multicurrency.md`](../pricing-setup/multicurrency.md).

## Currency inheritance flows

Two before-save flows show the pattern; their **placement differs by scope**:

| Flow | Lives in | Why |
|------|----------|-----|
| `RLM_Default_AssetRateCard_Currency` | `force-app/main/default/flows/` | Foundational. An `AssetRateCardEntry` whose currency differs from its Asset is *always* wrong; the platform defaults it to USD and never inherits (262, no config remedy). Every multicurrency build needs this. |
| `RLM_Default_Opportunity_Currency` | `unpackaged/post_quantumbit/flows/` | Feature-specific. It **enforces** account currency, so a deliberately cross-currency Opportunity cannot be created while it is active — acceptable for the QB demo, not something to impose on every build. Gated behind the `quantumbit` flag. |

The distinction generalises: a flow that corrects an always-wrong platform default is
foundational; one that removes a legitimate user choice to suit a demo belongs in
that demo's feature bundle.

Offline guard: `python tests/test_qb_multicurrency_data.py`.
Live guard: `cci task run validate_multicurrency_rates`.

## Refreshing exchange rates in the plans

qb/en-US qb-pricing's `CurrencyType.csv` is the rate table for
the USD-corporate shapes that share a currency with qb (q3 shares it), so refresh it there and copy
the shared rates. qb/ja's is JPY-corporate (USD 0.00663): never point the task's `csv_path` at it, as it
would write USD-based rates into a JPY-based table.

1. `cci task run update_currency_rates_csv` (preview with `-o dry_run true`; restrict with `-o iso_codes EUR,GBP`).
   It writes qb-pricing's CSV by default; pass `-o csv_path` for another plan's.
2. Regenerate qb's converted prices: `python scripts/expand_currency_pricing_data.py --apply`.
3. Copy the six shared rates into `q3-pricing/CurrencyType.csv`, then
   `python scripts/expand_currency_pricing_data.py --plan datasets/sfdmu/q3/en-US/q3-pricing --currencies AUD,CAD,CHF,EUR,GBP,JPY --apply`.
   Review the diff: the script also creates six-currency rows for q3's six USD-only entries and for
   its adjustment, tier and derived-price rows, which carry USD only today.
4. To bring a built org in line, reload the regenerated plans (`CurrencyType` and `PricebookEntry` are
   `Upsert`, so the rows update in place), then refresh the pricing decision tables:
   `cci task run refresh_dt_default_pricing --org <cci_alias>` and
   `cci task run refresh_dt_pricing_discovery --org <cci_alias>` (or `cci flow run
   refresh_all_decision_tables --org <cci_alias>`, which runs both). Pricing reads their snapshots, not
   the entries, so until the refresh the org keeps quoting the old prices. The refresh only queues the
   tables; once the queue drains, confirm with `cci task run check_decision_table_freshness --org
   <cci_alias>`: no pricing table should be Stale (a "Not comparable" table isn't a failure). `cci task run update_currency_rates` changes only the org's
   `CurrencyType` rates (fetched live again, not read from the CSV) and leaves its prices stale; without
   `-o iso_codes` it patches every active non-corporate currency, including q3's own and mfg's.

Prices in a currency follow its rate, so never change one without the other. mfg keeps its own rates
until it is aligned separately.
