---
page_id: sforce_api_objects_generalledgeracctasgntrule.htm
title: GeneralLedgerAcctAsgntRule
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_generalledgeracctasgntrule.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# GeneralLedgerAcctAsgntRule

Represents information about the rule based on which general ledger accounts are
assigned to transaction journals that are created for billing transactions. This
object is available in API version 63.0 and later.

## Supported Calls

`create()`,
`delete()`,
`describeLayout()`,
`describeSObjects()`,
`getDeleted()`,
`getUpdated()`,
`query()`,
`retrieve()`,
`search()`,
`undelete()`,
`update()`,
`upsert()`

## Special Access Rules

You need Revenue Cloud Billing license and the Accounts Receivables Admin permission set
to access this object.

## Fields

| Field | Details |
| --- | --- |
| CreditGeneralLedgerAccountId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The general ledger account for a credit transaction that's related to the general ledger account assignment rule.  This field is a relationship field.  Relationship Name  CreditGeneralLedgerAccount  Refers To  GeneralLedgerAccount |
| CurrencyIsoCode | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The currency code of the general ledger account assignment rule for Salesforce orgs with multicurrency enabled.  Valid values are:  - `AUD`—Australian   Dollar - `EUR`—Euro - `SGD`—Singapore   Dollar - `USD`—U.S.   Dollar  The default value is `USD`. |
| DebitGeneralLedgerAccountId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The general ledger account for a debit transaction that's related to the general ledger account assignment rule.  This field is a relationship field.  Relationship Name  DebitGeneralLedgerAccount  Refers To  GeneralLedgerAccount |
| FilterCriteria | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The filter criteria for the general ledger account assignment rule.  Valid values are:  - `All` - `Any` - `Custom` |
| FilterLogic | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The filter logic for the general ledger account assignment rule when the filter criteria is `Custom`. Transaction journals are created for the transactions of the selected type that meet the defined filter logic. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last accessed this record indirectly, for example, through a list view or related record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last viewed this record or list view. If this value is null, and LastReferenceDate is not null, the user accessed this record or list view indirectly. |
| LegalEntityId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The legal entity that's related to the general ledger account assignment rule.  This field is a relationship field.  Relationship Name  LegalEntity  Refers To  LegalEntity |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  A user-defined name for the general ledger account assignment rule. |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  The ID of the owner of the general ledger account assignment rule record.  This field is a polymorphic relationship field.  Relationship Name  Owner  Refers To  Group, User |
| Priority | Type  int  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The priority of the general ledger account assignment rule when there are multiple general ledger account assignment rules defined for a transaction type. |
| Status | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  The status of the general ledger account assignment rule.  Valid values are:  - `Active` - `Inactive` |
| TransactionAmountField | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The amount field on the transaction type that's used to record the credit or debit amount in the transaction journals that are generated for that specific transaction type. This field is available in API version 64.0 and later. |
| TransactionType | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  The transaction type that's related to the general ledger account assignment rule.  Valid values are:  - `CreditMemo` - `CreditMemoInvApplication` - `CreditMemoLine` - `CreditMemoLineInvoiceLine` - `CreditMemoLineTax` - `DebitMemoLine`—Available in API version 65.0   and later. - `Invoice` - `InvoiceLine` - `InvoiceLineTax` - `Payment`—Available in API version 64.0 and   later. - `PaymentLineInvoice`—Available in API version   64.0 and later. - `PaymentLineInvoiceLine`—Available in API   version 64.0 and later. - `Refund`—Available   in API version 64.0 and later. - `RefundLinePayment`—Available in API version   64.0 and later. |
