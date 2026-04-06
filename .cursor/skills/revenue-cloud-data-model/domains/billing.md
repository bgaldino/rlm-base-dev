# Billing Domain

54 objects covering invoicing, payments, credits, tax, general ledger, collections, and billing policies.

## Billing Policy Objects

| Object | Purpose | Key Fields |
|--------|---------|-----------|
| `BillingPolicy` | Top-level billing policy | Name, DefaultBillingTreatmentId |
| `BillingTreatment` | Treatment within a policy | Name, BillingPolicyId, LegalEntityId |
| `BillingTreatmentItem` | Detail item within a treatment | Name, BillingTreatmentId |

## Billing Schedule Objects

| Object | Purpose | Key Fields |
|--------|---------|-----------|
| `BillingSchedule` | Schedule linking orders to billing | ReferenceEntityId (→ Order), AccountId, BillingTreatmentItemId, TaxTreatmentId, OriginalBillingScheduleId |
| `BillingScheduleGroup` (BSG) | Groups billing schedules | BillingArrangementId, BillingTreatmentId, LegalEntityId, PaymentTermId, TaxTreatmentId |
| `BillingPeriodItem` | Period within a billing schedule | BillingScheduleGroupId, InvoiceBatchRunId, InvoiceId, InvoiceLineId |
| `BillingArrangement` | Arrangement container | — |
| `BillingArrangementLine` | Lines within an arrangement | — |
| `BsgRelationship` | Relationships between BSGs | AssociatedBsgId |
| `BillingMilestonePlan` | Milestone-based billing plan | BillingTreatmentId |
| `BillingMilestonePlanItem` | Items within a milestone plan | BillingScheduleGroupId, ReferenceItemId (→ BillingSchedule) |

## Invoice Objects

| Object | Purpose | Key Fields |
|--------|---------|-----------|
| `Invoice` | Invoice record | AccountId, BillingAccountId, LegalEntityId, PaymentTermId, InvoiceBatchRunId |
| `InvoiceLine` | Line item on an invoice | InvoiceId, Product2Id, BillingScheduleId, BillingScheduleGroupId, LegalEntityId, TaxTreatmentId |
| `InvoiceLineTax` | Tax detail on an invoice line | — |
| `InvoiceAddressGroup` | Address grouping for invoices | — |
| `InvoiceLineRelationship` | Relationships between invoice lines | AssociatedInvoiceLineId, UsageProductBillSchdGrpId |
| `InvoiceDocument` | Generated invoice document | — |
| `InvoiceBatchRun` | Batch invoice generation run | BillingBatchSchedulerId |
| `InvoiceBatchRunCriteria` | Criteria for batch runs | — |
| `InvoiceBatchRunRecovery` | Recovery for failed batch runs | — |
| `InvBatchDraftToPostedRun` | Draft-to-posted batch run | — |

## Credit/Debit Memo Objects

| Object | Purpose | Key Fields |
|--------|---------|-----------|
| `CreditMemo` | Credit memo | AccountId, LegalEntityId, ReferenceEntityId (→ Order) |
| `CreditMemoLine` | Line on a credit memo | CreditMemoId |
| `CreditMemoLineTax` | Tax on a credit memo line | LegalEntityId |
| `CreditMemoAddressGroup` | Address grouping | — |
| `CreditMemoInvApplication` | Application of credit to invoice | CreditMemoId, CreditMemoLineId |
| `CreditMemoLineInvoiceLine` | Junction: credit memo line ↔ invoice line | CreditMemoLineId, TaxTreatmentId, LegalEntityId |
| `DebitMemo` | Debit memo | — |
| `DebitMemoLine` | Line on a debit memo | LegalEntityId, TaxTreatmentId, BillingAddressId |
| `DebitMemoLineTax` | Tax on a debit memo line | BillingAddressId |
| `DebitMemoAddress` | Address for debit memos | — |

## Payment Objects

| Object | Purpose | Key Fields |
|--------|---------|-----------|
| `Payment` | Payment record | AccountId |
| `PaymentLineInvoice` | Payment applied to an invoice | LegalEntityId |
| `PaymentLineInvoiceLine` | Payment applied to an invoice line | — |
| `PaymentBatchRun` | Batch payment run | BillingBatchSchedulerId |
| `PaymentSchedule` | Payment schedule (may link to collection plan or invoice) | CollectionPlanItemId, ReferenceEntityId |
| `PaymentScheduleItem` | Items within a payment schedule | PaymentBatchRunId, PaymentId |
| `PaymentSchedulePolicy` | Policy for payment schedules | DefaultTreatmentId |
| `PaymentScheduleTreatment` | Treatment for payment schedules | — |
| `PaymentScheduleTreatmentDtl` | Detail within a payment treatment | — |
| `PaymentTerm` | Payment terms (Net 30, etc.) | Name |
| `PaymentTermItem` | Items defining payment term schedule | PaymentTermId, Type |
| `PaymentRetryRule` | Rules for retrying failed payments | — |
| `PaymentRetryRuleSet` | Set of retry rules | — |
| `PymtSchdDistributionMethod` | Distribution method for payment schedules | — |
| `Refund` | Refund record | — |
| `RefundLinePayment` | Refund applied to a payment | — |

## Tax Objects

| Object | Purpose | Key Fields |
|--------|---------|-----------|
| `TaxPolicy` | Tax policy (linked to Product2.TaxPolicyId) | Name, DefaultTaxTreatmentId, LegalEntityId, GeneralLedgerAcctAsgntRuleId |
| `TaxTreatment` | Treatment within a tax policy | Name, LegalEntityId, TaxEngineId, TaxPolicyId |
| `TaxEngine` | External tax engine config | TaxEngineName, TaxEngineProviderId, MerchantCredentialId, Status |
| `TaxEngineProvider` | Tax engine provider | DeveloperName |
| `TaxEngineInteractionLog` | Interaction log for tax engine calls | — |
| `TaxRate` | Tax rate record | LegalEntityId |

## GL and Accounting Objects

| Object | Purpose | Key Fields |
|--------|---------|-----------|
| `LegalEntity` | Legal entity for billing/tax | Name |
| `AccountingPeriod` | Accounting period | Name, FinancialYear |
| `LegalEntyAccountingPeriod` | Junction: LegalEntity ↔ AccountingPeriod | LegalEntityId, AccountingPeriodId |
| `GeneralLedgerAccount` | GL account | AccountingCode, LegalEntityId |
| `GeneralLedgerAcctAsgntRule` | GL assignment rule | CreditGeneralLedgerAccountId, DebitGeneralLedgerAccountId, LegalEntityId |
| `GeneralLedgerJrnlEntryRule` | Journal entry rule | CreditGeneralLedgerAccountId, DebitGeneralLedgerAccountId, GeneralLedgerAcctAsgntRuleId |
| `GeneralLdgrAcctPrdSummary` | GL period summary | LegalEntityAccountingPeriodId |
| `BillingBatchFilterCriteria` | Filter criteria for batch billing | BatchCriteriaId |
| `BillingBatchScheduler` | Batch billing scheduler | RunCriteriaId |

## Billing Account and Collections

| Object | Purpose | Key Fields |
|--------|---------|-----------|
| `BillingAccount` | Billing account (separate from Account) | AccountId, PaymentTermId |
| `AccountBillingAccount` | Junction: Account ↔ BillingAccount | — |
| `CollectionPlan` | Collections plan | — |
| `CollectionPlanItem` | Items within a collection plan | — |

## Error and Audit Objects

| Object | Purpose |
|--------|---------|
| `RevenueTransactionErrorLog` | Error log for revenue transactions (references many billing objects) |
| `Dispute` / `DisputeItem` | Billing dispute management (requires specific license) |
| `SequencePolicy` / `SeqPolicySelectionCondition` / `SequenceGapReconciliation` | Sequence numbering policies (requires specific license) |

## Key Cross-Domain Relationships

```
LegalEntity ← TaxTreatment, BillingScheduleGroup, GeneralLedgerAccount, Invoice, CreditMemo (LegalEntityId)
Product2 ← InvoiceLine (Product2Id)
Product2.BillingPolicyId → BillingPolicy
Product2.TaxPolicyId → TaxPolicy
Order ← BillingSchedule (ReferenceEntityId)
Order ← Invoice, CreditMemo (ReferenceEntityId)
Account ← Invoice, CreditMemo, Payment, BillingAccount (AccountId)
BillingSchedule ← InvoiceLine (BillingScheduleId)
PaymentTerm ← Invoice, BillingAccount, BillingScheduleGroup (PaymentTermId)
TaxTreatment ← BillingScheduleGroup, InvoiceLine, BillingSchedule (TaxTreatmentId)
```

## SFDMU Data Plans

- `qb-billing` — 14 objects across 3 passes (draft insert → activate treatment items → activate treatments/policies). Upstream: `qb-pcm`
- `qb-tax` — 8 objects across 2 passes. Upstream: `qb-pcm`, metadata (tax adapter)
- `qb-accounting` — 4 objects (GL accounts and rules). Upstream: LegalEntity from `qb-billing`/`qb-tax`
