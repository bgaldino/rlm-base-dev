---
page_id: deployment_billing_additional_info.htm
title: Billing Additional Information
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/deployment_billing_additional_info.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Revenue Cloud Deployment
parent_page: deployment_appendix_C.htm
fetched_at: 2026-06-09
---

# Billing Additional Information

Get to know additional deployment information for Billing in Revenue Cloud, including
active or inactive states, object information, and migration considerations.

## Object-Specific Information

| Object Name | Object API | Notes |
| --- | --- | --- |
| Legal Entity | LegalEntity | This object contains a polymorphic field for address. |
| Billing Policy | BillingPolicy | Activate after Billing Treatment is activated. |
| Billing Treatment | BillingTreatment | Activate after Billing Treatment Item is activated. |
| Billing Treatment Item | BillingTreatmentItem | Activate first when activating Billing Policy. |
| Tax Policy | TaxPolicy | Activate after Tax Treatment is activated. |
| Tax Treatment | TaxTreament | Activate first when activating Tax Policy. |
| Tax Treatment | TaxTreatment | Review these considerations for the TaxTreatment object.  - Create a tax treatment in Draft or Active status. - While the tax treatment is Active, you can’t edit LegalEntity, TaxEngine,   TaxCode, ProductCode, IsTaxable, or ShouldUseTaxTreatmentItems. - Status can move among Draft, Active, and Inactive states. |
| Payment Term | PaymentTerm | Activate after Payment Term Item is activated. |
| Payment Term Item | PaymentTermItem | Activate first when activating Payment Term. |
| Payment Schedule Policy | PaymentSchedulePolicy | Activate after Payment Schedule Treatment is activated |
| Payment Schedule Treatment | PaymentScheduleTreatment | Activate first when activating Payment Schedule Policy. |
| Payment Retry Rule | PaymentRetryRule | If `RetryIntervalType` field value is specified, you must also specify values for `IntervalUnit` and `IntervalValue` fields. |
| Payment Retry Rule Set | PaymentRetryRuleSet | You can’t delete or modify the active org-default rule set after the feature is enabled. The org can’t have multiple active org-default rule sets. |
| Tax Treatment Item | TaxTreatmentItem | You can’t delete a tax treatment item when the parent tax treatment is active. |
| Accounting Period | AccountingPeriod | Review these considerations for the AccountingPeriod object.  - The StartDate, EndDate, and FinancialYear fields can’t be edited if child   records exist. - The Name field is auto-populated. - The Status field is mutable. - The TotalAssetsAmount, TotalLiabilitiesAmount, TotalEquitiesAmount,   TotalRevenueAmount, and TotalExpensesAmount are derived or read-only   fields. - The creation of a record can happen only in Open status. - For AccountingPeriod as a parent record and LegalEntyAccountingPeriod as a   child record, the status of the parent record must be Open when the child is   created. The parent record can’t close if any non-closed child record exists.   The parent fields, such as StartDate, EndDate, or FinancialYear, become   immutable if any child record exists. |
| Billing Arrangement | BillingArrangement | Review these considerations for the BillingArrangement object.  - You can create a billing arrangement only in Draft status. - Before you activate it, add at least one billing arrangement line. - You can’t change ShouldBillRemainderToAccount field after the billing   arrangement is linked to a billing schedule group. - Status can move among Draft, Active, and Inactive states. |
| Billing Arrangement Line | BillingArrangementLine | Review these considerations for the BillingArrangementLine object.  - You can’t insert or update a line while the parent billing arrangement is in   Inactive status. - You can delete a line only when the parent billing arrangement is in Draft   status. |
| Billing Milestone Plan | BillingMilestonePlan | Review these considerations for the BillingMilestonePlan object.  - Create the plan in Draft status. - Activate only after you add at least one billing milestone plan item. - Updates apply only to lines that use the latest version number. - You can’t delete a line that has ShouldBillRemainder field set to `true`. - The related billing treatment must be active before you activate the   plan. - At least one billing milestone plan item must exist before activation. - While the plan is active, you can’t edit ReferenceItem, ExternalReference,   ReferenceItemAmount, BillingTreatment, Name, or Description fields. - You can’t change ReferenceItem or ExternalReference fields after the plan is   linked to a billing schedule. - Status can move among Draft, Active, and Inactive states. - The plan must be in Draft status before you can delete it. |
| Billing Milestone Plan Item | BillingMilestonePlanItem | Review these considerations for the BillingMilestonePlanItem object.  - Create items while the record is in Draft status. - The parent billing milestone plan must stay in Draft status while you create,   update, or delete items. |
| General Ledger Account | GeneralLedgerAccount | Review these considerations for the GeneralLedgerAccount object.  - You can’t edit LegalEntity after the account is tied to a general ledger   account assignment rule. - This object doesn’t use status transitions. - A general ledger account assignment rule can be active only when both a credit   and a debit general ledger account are set. |
| General Ledger Account Assignment Rules | GeneralLedgerAcctAsgntRule | Review these considerations for the GeneralLedgerAcctAsgntRule object.  - While the rule is active, you can’t edit the debit account, credit account, or   currency fields. - Status can move from Inactive to Active states. - The rule can be active only when both a credit and a debit general ledger   account are present. |
| General Ledger Journal Entry Rule | GeneralLedgerJrnlEntryRule | Review these considerations for the GeneralLedgerJrnlEntryRule object.  - You can’t edit the journal entry rule while its general ledger account   assignment rule is active. - This object doesn’t use status transitions. - The credit account, debit account, and assignment rule must belong to the same   legal entity. |
| Legal Entity Accounting Period | LegalEntityAccountingPeriod | Review these considerations for the LegalEntityAccountingPeriod object.  - After creation, you can’t change the AccountingPeriod or LegalEntity   fields. - The Name and CurrencyIsoCode fields are auto-populated. - You can change status according to the product’s transition rules. For   example, Open to Pending Closure, Pending Closure to Closed or Error, Closed to   Pending Reopen, and related paths for Reopened and Error. - The TotalAssetsAmount, TotalLiabilitiesAmount, TotalEquitiesAmount,   TotalRevenueAmount, and TotalExpensesAmount fields are derived or   read-only. - The ClosureStage field is read-only. - Create a record only when the status is Open. - When `AccountingPeriod` record is the   parent and `LegalEntityAccountingPeriod` is   the child record, the parent record must be Open when the child record is   created. The parent record can’t close if any child record is still open. The   StartDate, EndDate, and FinancialYear fields on the parent record can’t be   edited if any child record exists. - When `LegalEntity` record is the parent   record, it must be active when the child record is created. It can’t move to   Inactive status when any child accounting period is open. - For `LegalEntityAccountingPeriod` as parent   record and `GeneralLdgrAcctPrdSummary` as   child record, the parent can’t be deleted if children exist. Children can be   created or updated only when the parent is Open or Reopened. Child summary   records can’t be deleted. |
| Payment Schedule Treatment Detail | PaymentScheduleTreatmentDtl | Review these considerations for the PaymentScheduleTreatmentDtl object.  - While the parent payment schedule treatment is Active, Inactive, or Canceled,   you can’t change the InstallmentPaymentType, Percentage,   ProcessingDateReference, DateOffset, PaymentMethodSelectionType,   PymtSchdDistributionMethod, or PaymentRunMatchingValue fields. - Create a detail record only when the parent payment schedule treatment is in   Draft status. - Delete a detail record only when the parent payment schedule treatment is in   Draft status. |

## Other Information

- Data pipeline must be enabled before enabling Billing.
- Order to Billing Schedule Flow must be copied from the template and activated.
