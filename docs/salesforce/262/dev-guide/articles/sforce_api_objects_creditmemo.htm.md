---
page_id: sforce_api_objects_creditmemo.htm
title: CreditMemo
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_creditmemo.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# CreditMemo

Represents a document that’s used to reduce the amount that a buyer
owes a seller under the terms of an earlier invoice. This object is available in API
version 62.0 and later.

## Supported Calls

`describeLayout()`,
`describeSObjects()`,
`getDeleted()`,
`getUpdated()`,
`query()`,
`retrieve()`,
`search()`,
`update()`

## Special Access Rules

You need the Credit Memo Operations User permission set to access this object.

## Fields

| Field | Details |
| --- | --- |
| Balance | Type  currency  Properties  Filter, Nillable, Sort  Description  The amount of the credit memo that's available for allocation. |
| BillToContactId | Type  reference  Properties  Filter, Group, Nillable, Sort, Update  Description  This field is inherited from the account’s Bill to Account field.  This field is a relationship field.  Relationship Name  BillToContact  Refers To  Contact |
| BillingAccountId | Type  reference  Properties  Filter, Group, Sort, Update  Description  Required. The ID of the customer account associated with this credit memo.  This field is a relationship field.  Relationship Name  BillingAccount  Refers To  Account |
| Category | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  Specifies whether the credit memo is created due to writing off an invoice, converting negative invoice lines, or referencing an existing record.  Valid values are:  - `InvoiceWriteOff` - `Referenced` - `Standalone`  This field is available in API version 64.0 and later. |
| CorpCrcyCnvTotAmtWithTax | Type  double  Properties  Filter, Nillable, Sort  Description  The sum of the total amount with tax on the credit memo in corporate currency. Available in API version 63.0 and later. |
| CorporateCurrencyCvsnDate | Type  date  Properties  Filter, Group, Nillable, Sort  Description  The date on which the credit memo amounts are converted to the corporate currency. Available in API version 63.0 and later. |
| CorporateCurrencyCvsnRate | Type  double  Properties  Filter, Nillable, Sort  Description  The exchange rate that's used to convert credit memo amounts to the corporate currency. Available in API version 63.0 and later. |
| CorporateCurrencyIsoCode | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The currency ISO code of the corporate currency. Available in API version 63.0 and later. |
| CreationMode | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  Specifies whether the credit memo originated in Salesforce or an external system.  Valid values are:  - `External` - `Salesforce` |
| CreditDate | Type  date  Properties  Filter, Group, Nillable, Sort  Description  The date when the credit memo was posted. |
| CreditMemoNumber | Type  string  Properties  Filter, Group, Nillable, Sort, Update  Description  The number of the credit memo. |
| Description | Type  string  Properties  Filter, Group, Nillable, Sort, Update  Description  Additional details about the credit memo. |
| DocumentNumber | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  Required. The auto-generated reference number for the credit memo. |
| EffectiveDate | Type  date  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The effective date of the credit memo. If this field is empty, the credit date is used. For reporting purposes only; this field drives no other logic. |
| ExternalReference | Type  string  Properties  Filter, Group, Nillable, Sort, Update  Description  An external system’s ID for the credit memo. |
| ExternalReferenceDataSource | Type  string  Properties  Filter, Group, Nillable, Sort, Update  Description  The name of the external system that also contains the credit memo. |
| FuncCrcyCnvTotAmtWithTax | Type  double  Properties  Filter, Nillable, Sort, Update  Description  The total amount with tax value in functional currency. Available in API version 66.0 and later. |
| FunctionalCurrencyCvsnDate | Type  date  Properties  Filter, Group, Nillable, Sort, Update  Description  The date on which the total amount with tax value is converted into functional currency. Available in API version 66.0 and later. |
| FunctionalCurrencyCvsnRate | Type  double  Properties  Filter, Nillable, Sort, Update  Description  The exchange rate that's used to convert the total amount with tax value into functional currency. Available in API version 66.0 and later. |
| FunctionalCurrencyIsoCode | Type  string  Properties  Filter, Group, Nillable, Sort, Update  Description  The ISO code of the functional currency. Available in API version 66.0 and later. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last accessed a credit memo record indirectly, for example, through a list view or related record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last viewed a credit memo record. If this value is null, it’s possible that the user only accessed the credit memo record or a related list view (LastReferencedDate), but not viewed the credit memo record itself. |
| LegalEntityAccountingPeriodId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The legal entity accounting period record that’s related to the credit memo. This field is available in API version 65.0 and later.  This field is a relationship field.  Relationship Name  LegalEntityAccountingPeriod  Refers To  LegalEntyAccountingPeriod |
| LegalEntityId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The legal entity record that’s related to the credit memo. This field is available in API version 65.0 and later.  This field is a relationship field.  Relationship Name  LegalEntity  Refers To  LegalEntity |
| NetCreditsApplied | Type  currency  Properties  Filter, Nillable, Sort  Description  The total difference between the credit applied to and credit unapplied from the invoice.  This field is a calculated field. |
| OwnerId | Type  reference  Properties  Filter, Group, Sort, Update  Description  Required. The ID of the user who owns a credit memo record.  This field is a polymorphic relationship field.  Relationship Name  Owner  Refers To  Group, User |
| ReasonCode | Type  picklist  Properties  Filter, Group, Nillable, Sort  Description  The reason code for the credit memo's category. For example, BD can be the reason code when the credit memo's category is `InvoiceWriteOff` and the reason for the invoice write-off is bad debt. This field is available in API version 64.0 and later. |
| ReferenceEntityId | Type  reference  Properties  Filter, Group, Nillable, Sort, Update  Description  The ID of the record that this credit memo was generated from. For example, the order, order summary, or invoice.  This field is a polymorphic relationship field.  Relationship Name  ReferenceEntity  Refers To  Invoice, Order |
| SettlementLevel | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  Specifies whether the credit memo amount was applied to an invoice or an invoice line. |
| SourceAction | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  Specifies which Salesforce API created the credit memo.  Valid values are:  - `Invoice` - `NegativeInvoiceLineConversion` - `Standalone` - `VoidPostedInvoice` - `WriteOffPostedInvoice`—Available in API   version 64.0 and later. |
| Status | Type  picklist  Properties  Filter, Group, Restricted picklist, Sort, Update  Description  Required. The status of the credit memo.  Valid values are:  - `Canceled` - `Draft` - `Error` - `Pending` - `Posted` - `Void In   Progress`—Available in API version 64.0 and   later. - `Voided` |
| TotalAdjustmentAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The sum of the TotalAmount field values for the credit memo’s adjustment lines.  This field is a calculated field. |
| TotalAdjustmentAmountWithTax | Type  currency  Properties  Filter, Nillable, Sort  Description  The sum of the credit memo’s adjustment line amounts, including tax. Available in API versions 62.0 and 63.0. |
| TotalAdjustmentTaxAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The sum of the credit memo’s adjustment line tax. Adjustment line balances are excluded. Available in API versions 62.0 and 63.0. |
| TotalAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The sum of the credit memo’s TotalLineAmount and TotalAdjustmentAmount field values.  This field is a calculated field. |
| TotalAmountWithTax | Type  currency  Properties  Filter, Nillable, Sort  Description  The total credit memo amount, with tax included.  This field is a calculated field. |
| TotalChargeAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The sum of the TotalAmount field values for the credit memo’s charge lines.  This field is a calculated field. |
| TotalChargeAmountWithTax | Type  currency  Properties  Filter, Nillable, Sort  Description  The sum of the credit memo’s charge line amounts, including tax. Available in API versions 62.0 and 63.0. |
| TotalChargeTaxAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The sum of the credit memo’s charge tax amount. Available in API versions 62.0 and 63.0. |
| TotalTaxAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The sum of the TotalAmount field values for the credit memo’s tax lines.  This field is a calculated field. |
| TotalTaxesCapturedAtHeader | Type  currency  Properties  Create, Filter, Nillable, Sort, Update  Description  The total tax calculated at the transaction header level. Available in API version 66.0 and later. |
