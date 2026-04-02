# Data Plan Dependency Graph

## Load Order (QB en-US)

Plans must load in dependency order. Arrows show "depends on" relationships.

```
scratch_data (Account, Contact)
    │
    └──→ qb-pcm (ROOT — 28 objects)
            │   Product2, attributes, classifications, bundles, categories
            │
            ├──→ qb-pricing (16 objects)
            │       PriceBook2, PBE, PAS, PAT, adjustments
            │
            ├──→ qb-billing (14 objects, 3 passes)
            │       BillingPolicy, treatments, PaymentTerm, LegalEntity, GL accounts
            │       │
            │       └──→ qb-accounting (4 objects)
            │               GeneralLedgerAccount, GL rules, journal entry rules
            │
            ├──→ qb-tax (8 objects, 2 passes)
            │       TaxPolicy, TaxTreatment, TaxEngine
            │       Also creates LegalEntity (idempotent with qb-billing)
            │
            ├──→ qb-rating (16 objects, 2 passes)
            │       UsageResource, PUR, PURP, PUG, policies
            │       Upstream: qb-billing (UsageResourceBillingPolicy)
            │       │
            │       └──→ qb-rates (5 objects)
            │               RateCard, RateCardEntry, RABT, PriceBookRateCard
            │               MUST load after qb-rating (RCE → UsageResource, PUR)
            │               Upstream: qb-pricing (PriceBook2)
            │
            ├──→ qb-dro (17 objects)
            │       Fulfillment step definitions, decomp rules, scenarios
            │
            ├──→ qb-clm (7 objects)
            │       ObjectStateDefinition, transitions, clause sets
            │
            ├──→ qb-guidedselling (10 objects)
            │       AssessmentQuestion, OmniProcess, OmniProcessElement
            │
            ├──→ qb-product-images (1 object)
            │       Product2 DisplayUrl updates
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
```

## Deletion Order

Deletions must run in reverse dependency order. SFDMU's `deleteOldData: true` handles per-object deletion in reverse array order within a plan, but cross-plan deletions must be sequenced manually.

**Critical**: `delete_qb_rates_data` must run BEFORE `delete_qb_rating_data` — rates FK to PURs.

```
Delete order (for full teardown):
1. qb-rates (RateAdjustmentByTier → RateCardEntry → PriceBookRateCard → RateCard)
2. qb-rating (PUG → PURP → PUR → policies → UsageResource)
3. qb-pricing (adjustments → PricebookEntry → PriceAdjustmentSchedule → Pricebook2)
4. qb-billing (treatments → BillingPolicy → PaymentTerm → LegalEntity)
5. qb-tax (TaxTreatment → TaxPolicy → TaxEngine)
6. qb-dro (steps → rules → scenarios)
7. qb-pcm (bundles → products → attributes → classifications → categories)
```

## Other Plan Families

| Family | Plans | Notes |
|--------|-------|-------|
| Q3 | q3-multicurrency, q3-billing, q3-dro, q3-tax, q3-rating, q3-rates | Parallel product line; same dependency ordering |
| Manufacturing | mfg-configflow, mfg-constraints-p, mfg-constraints-prc, mfg-multicurrency | Configuration and constraints |
| Procedure Plans | procedure-plans | Depends on expression sets metadata, not on QB data |
