---
article_id: ind.billing_legal_entity_default.htm
title: Legal Entity Automatic Population, Usage, and Considerations
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_legal_entity_default.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Legal Entity Automatic Population, Usage, and Considerations

You are here:

SALESFORCE HELP
DOCS
AGENTFORCE REVENUE MANAGEMENT
Legal Entity Automatic Population, Usage, and Considerations

Legal entity is a required value for financial accounting. It's either specified or automatically populated when billing transaction records are created. Explore the usage of legal entity and considerations of editing legal entity on the billing transactions.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
Legal Entity Autopopulated for Billing Schedule Groups

The legal entity is automatically populated on billing schedule groups in this sequential order.

SCENARIO	LEGAL ENTITY USED
Legal entity is selected for the related order item.	Legal entity of the related order item
Legal entity is selected for the related order.	Legal entity of the related order
Legal entity isn't selected for the related order or order item.	Default legal entity of your Salesforce org
Legal Entity Autopopulated for Billing Transactions

The legal entity is populated automatically on billing transaction records in this sequential order.

SCENARIO	LEGAL ENTITY USED
Legal entity is selected for the billing transaction.	The selected legal entity
Legal entity isn't selected for the billing transaction.	Legal entity from the parent or the related record of the billing transaction
Legal entity isn't selected for the billing transaction record, its parent record, or its related record.	Default legal entity of your Salesforce org
Derivation of Legal Entities from Parent or Related Records

This table specifies the parent or the related record that the billing transaction derives its legal entity from.

BILLING TRANSACTION	LEGAL ENTITY DERIVED FROM
Invoice	The related Billing Schedule Group record
Invoice Line	The parent Invoice record
Invoice Line Tax	The parent Invoice Line record
Credit Memo	The Invoice record that's specified in the Reference Entity field
Credit Memo Line	The parent Credit Memo record
Credit Memo Line Tax	The parent Credit Memo Line record
Credit Memo Line Invoice Line	The related Invoice Line record
Payment	Default legal entity of your Salesforce org
Payment Line Invoice	The related Invoice record
Payment Line Invoice Line	The related Invoice Line record
Refund	Default legal entity of your Salesforce org
Refund Line Payment	The related Payment record
Debit Memo	Default legal entity of your Salesforce org
Debit Memo Line	The parent Debit Memo record
Usage of Legal Entities

After automatic population of legal entity on billing transactions, the legal entity is used in these scenarios.

Legal Entity Based Tax Treatment: When you choose legal entity as the treatment selection during tax policy creation, the system selects the tax treatment based on the legal entity and populates it on the order product or quote line item. This tax treatment is then used for the tax calculation. See Create Tax Policies and Treatments.
Invoice Grouping: When the invoice grouping type on the billing schedule is set to default or custom, the system uses the billing schedule group's legal entity along with other fields that make a default group to consolidate invoice records. See Define Invoice Grouping on a Billing Schedule.
Settle invoice lines based on legal entity: During the credit application process, the system validates the invoice line and credit memo line for a matching legal entity. The system applies the credit memo line to an invoice line only if it finds a matching legal entity on the invoice line. See Create and Apply Credit Memos to Invoice Lines.
Financial Accounting Usage:
Automatic Population of Legal Entity Accounting Period: When legal entity of a billing transaction is autopopulated, its legal entity accounting period is also automatically populated. See Assign Legal Entities to Accounting Periods
Transaction Journal creation: During transaction journal creation for the general ledger account assignment rule, the system validates if the transaction type's legal entity matches the general ledger account assignment rule's legal entity. See General Ledger Account Assignment Rules and Related Records.
Legal Entity Accounting Period (LEAP) Closure: During legal entity accounting period closure, the system validates billing transaction records that match the legal entity accounting period's legal entity and are within the start and end dates of its accounting period. See Close Legal Entity Accounting Periods.
Considerations for Editing Legal Entity on Billing Transactions

Review these considerations before you edit the Legal Entity field on billing transactions.

The Legal Entity field on billing transactions is editable regardless of the billing transaction's status.
When you edit the legal entity of a billing transaction, update the legal entity accounting period of the billing transaction manually. See Assign Legal Entities to Accounting Periods.
The legal entity is automatically populated only when a Billing Transaction record is created. When the Legal Entity field is updated on a billing transaction, the Legal Entity field on its related records must be manually updated.
If you edit the Legal Entity field on billing transaction records for which transaction journals are created, then:
Manually update the Legal Entity field on the transaction journals created for the general ledger accounting assignment rule.
Manually update the existing foreign exchange realized gain and loss transaction journals that are created for the Payment Line Invoice, Payment Line Invoice Line, and Credit Memo Line Invoice Line records.
Reopen and close Legal Entity Accounting Period record to update the legal entity field for the foreign exchange unrealized gain and loss transaction journals.
