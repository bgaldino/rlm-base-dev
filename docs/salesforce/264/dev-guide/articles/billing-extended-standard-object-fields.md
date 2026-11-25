---
page_id: billing-extended-standard-object-fields
title: Billing Fields on Standard Objects
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/billing-extended-standard-object-fields.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-overview
legacy_page_id: billing_extended_standard_object_fields.htm
fetched_at: 2026-11-25
---

# Billing Fields on Standard Objects

Billing adds standard fields to some standard Salesforce objects of other features to represent information specific to Billing. These fields are available only in orgs where Billing is enabled.

- 

**[Billing Fields on AccountBillingAccount](./billling-sforce-api-objects-accountbillingaccount.md)**

Standard fields extend the AccountBillingAccount object for use in Billing to represent information about default billing accounts. This object is available in API version 63.0 and later.

- 

**[Billing Fields on AssetActionSource](./billing-sforce-api-objects-assetactionsource.md)**

Standard fields extend the AssetActionSource object for use in Billing to represent information about the billing term.

- 

**[Billing Fields on BillingAccount](./billling-sforce-api-objects-billingaccount.md)**

Standard fields extend the BillingAccount object for use in Billing to represent information about the billing suspension date and the billing resumption date. This object is available in API version 63.0 and later.

- 

**[Billing Fields on CollectionPlan](./billing-sforce-api-objects-collectionplan.md)**

Standard fields extend the CollectionPlan object for use in Billing to represent information about the total invoice balance. This object is available in API version 64.0 and later.

- 

**[Billing Fields on CollectionPlanItem](./billing-sforce-api-objects-collectionplanitem.md)**

Standard fields extend the CollectionPlanItem object for use in Billing to represent information about the invoice balance. This object is available in API version 64.0 and later.

- 

**[Billing Fields on ExpressionSet](./billing-sforce-api-objects-expressionset.md)**

Standard fields extend the ExpressionSet object for use in Billing. These fields represent information about an expression set that performs a series of calculations by using lookups and user-defined variables and constants to calculate taxes. This object is available in API version 66.0 and later.

- 

**[Billing Fields on Dispute](./billing-sforce-api-objects-dispute.md)**

Represents the details of a billing dispute that involves one invoice and one or more disputed invoice lines. The details include the disputed amount, the approved amount, and the dispute type, subtype and status. This object is available in API version 66.0 and later.

- 

**[Billing Fields on DisputeItem](./billing-sforce-api-objects-disputeitem.md)**

Represents a specific invoice line or charge that’s being disputed. The details include the total transaction amount, transaction date, disputed amount, reason, and status of the dispute. This object is available in API version 66.0 and later.

- 

**[Billing Fields on OrderItem](./billing-sforce-api-objects-orderitem.md)**

Standard fields extend the OrderItem object for use in Billing to represent information about the billing term.

- 

**[Billing Fields on Payment](./billing-sforce-api-objects-payment.md)**

Standard fields extend the Payment object for use in Billing to represent information about corporate currency, transaction amounts in corporate currency, and accounting periods for legal entities. This object is available in API version 64.0 and later.

- 

**[Billing Fields on PaymentLineInvoice](./billing-sforce-api-objects-paymentlineinvoice.md)**

Standard fields extend the PaymentLineInvoice object for use in Billing to represent information about legal entities and legal entity accounting periods. This object is available in API version 64.0 and later.

- 

**[Billing Fields on QuoteLineItem](./billing-sforce-api-objects-quotelineitem.md)**

Standard fields extend the QuoteLineItem object for use in Billing to represent information about the billing term.

- 

**[Billing Fields on Refund](./billing-sforce-api-objects-refund.md)**

Standard fields extend the Refund object for use in Billing to represent information about corporate currency, transaction amounts in corporate currency, and accounting periods for legal entities. This object is available in API version 64.0 and later.

- 

**[Billing Fields on RefundLinePayment](./billing-sforce-api-objects-refund-line-payment.md)**

Standard fields extend the Refund Line Payment object for use in Billing to represent information about accounting periods for legal entities. This object is available in API version 64.0 and later.

- 

**[Billing Fields on TaxRate](./billing-sforce-api-objects-taxrate.md)**

Standard fields extend the TaxRate object for use in Billing. These fields represent information about the tax rate for a transaction that’s determined by the applicable tax code and country. This object is available in API version 66.0 and later.

- 

**[Billing Fields on TransactionJournal](./billing-sforce-api-objects-transactionjournal.md)**

Standard fields extend the TransactionJournal object for use in Billing to represent information about the general ledger accounts for billing transactions. This object is available in API version 63.0 and later.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/billing-extended-standard-object-fields.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
