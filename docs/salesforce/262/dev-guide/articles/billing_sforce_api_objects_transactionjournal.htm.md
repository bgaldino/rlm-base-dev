---
page_id: billing_sforce_api_objects_transactionjournal.htm
title: Billing Fields on TransactionJournal
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/billing_sforce_api_objects_transactionjournal.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_extended_standard_object_fields.htm
fetched_at: 2026-06-09
---

# Billing Fields on TransactionJournal

Standard fields extend the TransactionJournal object for use in
Billing to represent information about the general ledger accounts for billing
transactions. This object is available in API version 63.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `undelete()`, `update()`, `upsert()`

## Special Access Rules

You need the Revenue Cloud Billing license and the Accounts Receivables Admin permission
set to access this object.

## Fields

| Field | Details |
| --- | --- |
| ActivityDate | Type  dateTime  Properties  Create, Filter, Sort, Update  Description  The date and time when a billing transaction record is posted or processed. |
| Credit | Type  currency  Properties  Create, Filter, Nillable, Sort, Update  Description  The transaction record amount when a credit general ledger account is specified. |
| CreditGeneralLedgerAccountId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The ID of the general ledger account for a debit transaction that's related to the transaction journal.  This field is a relationship field.  Relationship Name  CreditGeneralLedgerAccount  Refers To  GeneralLedgerAccount |
| Debit | Type  currency  Properties  Create, Filter, Nillable, Sort, Update  Description  The transaction record amount when a debit general ledger account is specified. |
| DebitGeneralLedgerAccountId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The ID of the General Ledger (GL) Treatment based on which transaction journals must be generated for the billing transaction.  This field is a relationship field.  Relationship Name  DebitGeneralLedgerAccount  Refers To  GeneralLedgerAccount |
| ForeignExchangeGainOrLossType | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Specifies the type of foreign exchange gain or loss for the transaction journal. This field is available in API version 65.0 and later.  Valid values are:  - `Realized` - `Unrealized` - `UnrealizedReversal` |
| GeneralLedgerAcctAsgntRuleId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The general ledger account assignment rule used to assign general ledger accounts to transaction journals that’s created for billing transactions.  This field is a relationship field.  Relationship Name  GeneralLedgerAcctAsgntRule  Refers To  GeneralLedgerAcctAsgntRule |
| GenlLdgrJournalEntryRuleId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The general ledger journal entry rule used to assign general ledger accounts to transaction journals created for billing transactions. This field is available in API version 65.0 and later.  This field is a relationship field.  Relationship Name  GenlLdgrJournalEntryRule  Refers To  GeneralLedgerJrnlEntryRule |
| LegalEntityId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The legal entity that's related to the transaction journal.  This field is a relationship field.  Relationship Name  LegalEntity  Refers To  LegalEntity |
| ReferenceTransactionRecordId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The transaction record for which the transaction journal is created.  This field is a polymorphic relationship field.  Relationship Name  ReferenceTransactionRecord  Refers To  CreditMemo, CreditMemoInvApplication, CreditMemoLine, CreditMemoLineInvoiceLine, CreditMemoLineTax, Invoice, InvoiceLine, InvoiceLineTax, Payment, PaymentLineInvoice, PaymentLineInvoiceLine, Refund |
| TransactionType | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The transaction type that's related to the transaction journal.  Valid values are:  - `CreditMemo` - `CreditMemoInvApplication` - `CreditMemoLine` - `CreditMemoLineTax` - `CreditMemoLineInvoiceLine` - `DebitMemoLine`—Available in API version 65.0   and later. - `Invoice` - `InvoiceLine` - `InvoiceLineTax` - `Payment`—Available in API version 64.0 and   later. - `PaymentLineInvoice`—Available in API version   64.0 and later. - `PaymentLineInvoiceLine`—Available in API   version 64.0 and later. - `Refund`—Available   in API version 64.0 and later. - `RefundLine`—Available in API version 64.0 and   later. |
| UniqueIdentifier | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  An auto-generated identifier for the transaction journal when the usage type is Billing. The identifier is a combination of the reference transaction record ID, the general ledger account assignment rule ID, and other internal-only fields. |
| UsageType | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort  Description  The type of usage.  Valid value is:  - `Billing` |

#### See Also

- [*Loyalty Management Developer Guide*: TransactionJournal](https://developer.salesforce.com/docs/atlas.en-us.262.0.loyalty.meta/loyalty/sforce_api_objects_transactionjournal.htm "Loyalty Management Developer Guide: TransactionJournal - HTML (New Window)")
