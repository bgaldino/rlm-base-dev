# Data Plan Dependency Graph

## Load Order (QB en-US)

Plans must load in dependency order. Arrows show "depends on" relationships.

```
scratch_data (Account, Contact, BillingAccount)
    │
    └──→ qb-pcm (ROOT — 28 objects)
            │   Product2, attributes, classifications, bundles, categories
            │
            ├──→ qb-pricing (16 objects)
            │       PriceBook2, PBE, PAS, PAT, adjustments
            │
            ├──→ qb-billing (16 object entries, 3 passes)
            │       AccountingPeriod, LegalEntity (Readonly), BillingPolicy, treatments, PaymentTerm,
            │       GL accounts and assignment rules, PaymentRetryRuleSet/Rule
            │       │
            │       └──→ qb-accounting (4 objects)
            │               GeneralLedgerAccount, GL assignment rules, journal entry rules,
            │               BillingBatchFilterCriteria
            │
            ├──→ qb-tax (9 object entries, 2 passes)
            │       TaxPolicy, TaxTreatment, TaxEngine, TaxEngineProvider (NamedCredential Readonly)
            │       Also creates LegalEntity (idempotent with qb-billing)
            │
            ├──→ qb-rating (17 object entries, 2 passes)
            │       UoM, UoMClass, UsageResource, UsageResourceBillingPolicy, PUR, usage policies
            │       Pass 2 updates existing rows without Status; activateRatingRecords.apex activates
            │       │
            │       ├──→ qb-rating-entitlements (24 object entries, 2 passes; each pass: PURP + PUG plus 10 Readonly)
            │       │       Matches PURP and PUG on ProductUsageResourceId, resolved on the target org
            │       │
            │       └──→ qb-rates (8 object entries, 2 passes)
            │               RateCard, RateCardEntry, RABT, PriceBookRateCard
            │               MUST load after qb-rating (RCE and RABT → UsageResource)
            │               Upstream: qb-pricing (PriceBook2)
            │
            ├──→ qb-dro (17 objects)
            │       Fulfillment step definitions, decomp rules, scenarios
            │
            ├──→ qb-clm (6 objects)
            │       ObjectStateDefinition, values, transitions, actions; clause sets load in a
            │       separate step (insert_clm_clause_sets)
            │
            ├──→ qb-guidedselling-products (1 object)
            │       Product2 guided selling field updates; requires guided selling field metadata
            │       Decorator plan loaded by prepare_guidedselling in org builds
            │
            ├──→ qb-prm (5 objects, 2 passes)
            │       Account (partner), ChannelProgram, ChannelProgramLevel, ChannelProgramMember
            │
            ├──→ qb-prm-pricing (6 object entries, 3 passes)
            │       Overlay that runs after qb-prm (prepare_prm_pricing); Account, ChannelProgram,
            │       ChannelProgramLevel, ChannelProgramMember
            │
            ├──→ qb-approvals (2 objects)
            │       ApprovalAlertContentDef (requires EmailTemplate metadata)
            │
            └──→ qb-transactionprocessingtypes (1 object, standalone)
                    TransactionProcessingType

procedure-plans (6 objects, 2 passes)
    Depends on: Expression sets deployed as metadata + Connect API (creates PPD+PPDV)

qb-price-revision (2 objects, no lookups — independent)
    IndexRate, PriceRevisionPolicy → refresh Index_Rate_Decision_Table after
```

## Deletion Order

Deletions must run in reverse dependency order. SFDMU's `deleteOldData: true` handles per-object deletion in reverse array order within a plan, but cross-plan deletions must be sequenced manually.

`delete_qb_rating_data` does not need `delete_qb_rates_data` first. Measured live on a 264 org (2026-11-24): `delete_qb_rating_data` succeeds with qb-rates data present and leaves every rate record in place. No foreign key forces this order: in the 264 schema no rate object has a ProductUsageResource lookup, and RateCardEntry and RateAdjustmentByTier look up UsageResource, which `deleteQbRatingData.apex` leaves in place. Neither runs in a flow any more: the qb pricing, rates and rating plans reload in place (todo 298), so these deletes are for a manual full teardown only.

```
Delete order (for full teardown; items 1 and 2 are the usual order, not a requirement):
1. qb-rates (RateCardEntry, deactivated first; its RateAdjustmentByTier go with it → PriceBookRateCard → RateCard; `deleteQbRatesData.apex`)
2. qb-rating + qb-rating-entitlements (PUG → PURP → RatingFrequencyPolicy → UsagePrdGrantBindingPolicy → PUR → grant renewal, rollover, overage and commitment policies → UsageResourceBillingPolicy; `deleteQbRatingData.apex`. UsageResource, UnitOfMeasure and UnitOfMeasureClass stay)
3. qb-pricing (adjustments → PricebookEntry → PriceAdjustmentSchedule → Pricebook2)
4. qb-billing (treatments → BillingPolicy → PaymentTerm → LegalEntity)
5. qb-tax (TaxTreatment → TaxPolicy → TaxEngine)
6. qb-dro (steps → rules → scenarios)
7. qb-pcm (bundles → products → attributes → classifications → categories)
```

## Other Plan Families

| Family | Plans | Notes |
|--------|-------|-------|
| Q3 | q3-pcm, q3-pricing, q3-billing, q3-dro, q3-tax, q3-rating, q3-rating-entitlements, q3-rates | Parallel product line, mirrors qb plan shapes; same dependency ordering (q3-multicurrency was split into q3-pcm + q3-pricing). q3-tax and q3-billing only map the q3 products onto qb-tax/qb-billing policies, which a q3 build also loads, and q3-dro only sets their decomposition scope (todo 210) |
| Manufacturing | mfg-aaf, mfg-billing, mfg-configflow, mfg-constraints-p, mfg-constraints-prc, mfg-dro, mfg-guidedselling, mfg-pcm, mfg-pricing, mfg-rebates, mfg-tax | **11 plans, none wired** — `grep -ic mfg cumulusci.yml` returns 0. Wiring is tracked separately; `mfg-multicurrency` was removed for being unwired with zero-byte CSVs (pack 110) |
| Procedure Plans | procedure-plans | Depends on expression sets metadata, not on QB data |
