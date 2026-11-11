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
            ├──→ qb-billing (18 object entries, 3 passes)
            │       BillingPolicy, treatments, PaymentTerm, LegalEntity (Readonly), GL accounts,
            │       PaymentRetryRuleSet/Rule, SequencePolicy, SeqPolicySelectionCondition
            │       │
            │       └──→ qb-accounting (4 objects)
            │               GeneralLedgerAccount, GL rules, journal entry rules
            │
            ├──→ qb-tax (8 objects, 2 passes)
            │       TaxPolicy, TaxTreatment, TaxEngine
            │       Also creates LegalEntity (idempotent with qb-billing)
            │
            ├──→ qb-rating (12 objects, 2 passes)
            │       UoM, UoMClass, UsageResource, UsageResourceBillingPolicy, PUR, usage policies
            │       Pass 2 updates existing rows without Status; activateRatingRecords.apex activates
            │       │
            │       ├──→ qb-rating-entitlements (12 objects: PURP + PUG, 10 Readonly; 2 passes)
            │       │       Matches PURP and PUG on ProductUsageResourceId, resolved on the target org
            │       │
            │       └──→ qb-rates (5 objects)
            │               RateCard, RateCardEntry, RABT, PriceBookRateCard
            │               MUST load after qb-rating (RCE and RABT → UsageResource)
            │               Upstream: qb-pricing (PriceBook2)
            │
            ├──→ qb-dro (17 objects)
            │       Fulfillment step definitions, decomp rules, scenarios
            │
            ├──→ qb-clm (7 objects)
            │       ObjectStateDefinition, transitions, clause sets
            │
            ├──→ qb-guidedselling-products (1 object)
            │       Product2 guided selling field updates; requires guided selling field metadata
            │       Decorator plan loaded by prepare_guidedselling in org builds
            │
            ├──→ qb-prm (5 objects, 2 passes)
            │       Account (partner), ChannelProgram, ChannelProgramMember
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

**Order kept, reason unverified**: run `delete_qb_rates_data` BEFORE `delete_qb_rating_data`. No foreign key explains this order: in the 264 schema no rate object has a ProductUsageResource lookup, and RateCardEntry and RateAdjustmentByTier look up UsageResource, which `deleteQbRatingData.apex` leaves in place. Keep the order until a reason is established. Neither runs in a flow any more: the qb pricing, rates and rating plans reload in place (todo 298), so these deletes are for a manual full teardown only.

```
Delete order (for full teardown):
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
