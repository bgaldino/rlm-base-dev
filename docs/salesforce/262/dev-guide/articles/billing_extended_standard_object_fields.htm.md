---
page_id: billing_extended_standard_object_fields.htm
title: Billing Fields on Standard Objects
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/billing_extended_standard_object_fields.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_overview.htm
fetched_at: 2026-06-09
---

# Billing Fields on Standard Objects

Billing adds standard fields to some standard Salesforce objects of other features to
represent information specific to Billing. These fields are available only in orgs where
Billing is enabled.

- **[Billing Fields on AccountBillingAccount](./billling_sforce_api_objects_accountbillingaccount.htm.md)**  
  Standard fields extend the AccountBillingAccount object for use in Billing to represent information about default billing accounts. This object is available in API version 63.0 and later.
- **[Billing Fields on BillingAccount](./billling_sforce_api_objects_billingaccount.htm.md)**  
  Standard fields extend the BillingAccount object for use in Billing to represent information about the billing suspension date and the billing resumption date. This object is available in API version 63.0 and later.
- **[Billing Fields on CollectionPlan](./billing_sforce_api_objects_collectionplan.htm.md)**  
  Standard fields extend the CollectionPlan object for use in Billing to represent information about the total invoice balance. This object is available in API version 64.0 and later.
- **[Billing Fields on CollectionPlanItem](./billing_sforce_api_objects_collectionplanitem.htm.md)**  
  Standard fields extend the CollectionPlanItem object for use in Billing to represent information about the invoice balance. This object is available in API version 64.0 and later.
- **[Billing Fields on ExpressionSet](./billing_sforce_api_objects_expressionset.htm.md)**  
  Standard fields extend the ExpressionSet object for use in Billing. These fields represent information about an expression set that performs a series of calculations by using lookups and user-defined variables and constants to calculate taxes. This object is available in API version 66.0 and later.
- **[Billing Fields on Dispute](./billing_sforce_api_objects_dispute.htm.md)**  
  Represents the details of a billing dispute that involves one invoice and one or more disputed invoice lines. The details include the disputed amount, the approved amount, and the dispute type, subtype and status. This object is available in API version 66.0 and later.
- **[Billing Fields on DisputeItem](./billing_sforce_api_objects_disputeitem.htm.md)**  
  Represents a specific invoice line or charge that’s being disputed. The details include the total transaction amount, transaction date, disputed amount, reason, and status of the dispute. This object is available in API version 66.0 and later.
- **[Billing Fields on Payment](./billing_sforce_api_objects_payment.htm.md)**  
  Standard fields extend the Payment object for use in Billing to represent information about corporate currency, transaction amounts in corporate currency, and accounting periods for legal entities. This object is available in API version 64.0 and later.
- **[Billing Fields on PaymentLineInvoice](./billing_sforce_api_objects_paymentlineinvoice.htm.md)**  
  Standard fields extend the PaymentLineInvoice object for use in Billing to represent information about legal entities and legal entity accounting periods. This object is available in API version 64.0 and later.
- **[Billing Fields on Refund](./billing_sforce_api_objects_refund.htm.md)**  
  Standard fields extend the Refund object for use in Billing to represent information about corporate currency, transaction amounts in corporate currency, and accounting periods for legal entities. This object is available in API version 64.0 and later.
- **[Billing Fields on RefundLinePayment](./billing_sforce_api_objects_refund_line_payment.htm.md)**  
  Standard fields extend the Refund Line Payment object for use in Billing to represent information about accounting periods for legal entities. This object is available in API version 64.0 and later.
- **[Billing Fields on TaxRate](./billing_sforce_api_objects_taxrate.htm.md)**  
  Standard fields extend the TaxRate object for use in Billing. These fields represent information about the tax rate for a transaction that's determined by the applicable tax code and country. This object is available in API version 66.0 and later.
- **[Billing Fields on TransactionJournal](./billing_sforce_api_objects_transactionjournal.htm.md)**  
  Standard fields extend the TransactionJournal object for use in Billing to represent information about the general ledger accounts for billing transactions. This object is available in API version 63.0 and later.
