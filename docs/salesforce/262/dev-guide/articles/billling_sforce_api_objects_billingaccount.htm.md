---
page_id: billling_sforce_api_objects_billingaccount.htm
title: Billing Fields on BillingAccount
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/billling_sforce_api_objects_billingaccount.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_extended_standard_object_fields.htm
fetched_at: 2026-06-09
---

# Billing Fields on BillingAccount

Standard fields extend the BillingAccount object for use in Billing
to represent information about the billing suspension date and the billing resumption
date. This object is available in API version 63.0 and later.

## Supported Calls

`describeLayout()`, `describeSObjects()`, `getDeleted()`,
`getUpdated()`, `query()`, `retrieve()`, `search()`

## Special Access Rules

You need the Billing Admin permission set, Billing Operations User permission set, or Billing
Customer Service User permission set access to this object.

## Fields

| Field | Details |
| --- | --- |
| AccountID | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  Specifies the account that's related to the billing account. Available in API version 65.0 and later.  This field is a relationship field.  Relationship Name  Account  Refers To  Account |
| AddTaxIdentificationDetails | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The additional tax identification details, such as a Peppol ID. Available in API version 66.0 and later. |
| BillDayOfMonth | Type  int  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  A number from 1 to 31 that indicates the billing date. Available in API version 64.0 and later. |
| BillToContactId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The contact associated with the billing account. Available in API version 64.0 and later.  This field is a relationship field.  Relationship Name  BillToContact  Refers To  Contact |
| BillingResumptionDate | Type  date  Properties  Filter, Group, Nillable, Sort  Description  The date when billing for the account is resumed. |
| BillingSuspensionDate | Type  date  Properties  Filter, Group, Nillable, Sort  Description  The date when billing for the account is suspended. |
| DeliveryTerms | Type  picklist  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The standard code in internal trades used to define shipping responsibilities.  Valid values are:  - `CFR` - `CIF` - `CIO` - `CPT` - `CUS` - `DAF` - `DAP` - `DDP` - `DDU` - `DEQ` - `DES` - `DPU` - `EXW` - `FAS` - `FCA` - `FOB` - `SUP`  The default value is `USD`. Available in API version 66.0 and later. |
| DoesSkipAutomaticPayments | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether to skip the automatic creation of payment schedules and payment schedule items for posted invoices related to billing accounts (`true`) or not (`false`). This boolean value is considered when the automatic creation of payment schedules and payment schedule items is turned on. Available in API version 65.0 and later. |
| EmailTemplateId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The template used for sending billing account emails. Available in API version 65.0 and later.  This field is a relationship field.  Relationship Name  EmailTemplate  Refers To  Email template |
| InvoiceDocumentTemplateId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The document template that’s used to generate PDF documents for the invoices that are related to the billing account. Available in API version 66.0 and later.  This field is a relationship field.  Relationship Name  InvoiceDocumentTemplate  Refers To  DocumentTemplate |
| IsDefaultBillingProfile | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether the billing account is the default billing profile (`true`) or not (`false`). Available in API version 65.0 and later. |
| PaymentTermId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The payment term associated with the billing account. Available in API version 64.0 and later.  This field is a relationship field.  Relationship Name  PaymentTerm  Refers To  PaymentTerm |
| SavedPaymentMethodId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The saved payment method that’s used to collect payments for the default billing profile of an account when the automatic creation of payment schedules and payment schedule items is turned on. Available in API version 65.0 and later.  This field is a relationship field.  Relationship Name  SavedPaymentMethod  Refers To  SavedPaymentMethod |
| ShippingAddress | Type  address  Properties  Filter, Nillable  Description  The shipping address of the billing account. Available in API version 64.0 and later. |
| ShouldAttachInvoiceDocToEmail | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether to attach the invoice PDF document to the email that’s sent to the billing account. Available in API version 65.0 and later.  The default value is false. |
| TaxExemptionExpirationDate | Type  date  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The date until which the tax exemption is valid. Available in API version 66.0 and later. |
| TaxExemptionNumber | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  A unique identifier used to indicate that a transaction is tax exempt. Available in API version 66.0 and later. |
| TaxExemptionStatus | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The status of the tax exemption with values defined by the user. Available in API version 66.0 and later. |
| TaxIdentificationNumber | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The tax identification number such as a VAT ID. Available in API version 66.0 and later. |

#### See Also

- [*Energy and Utilities Cloud Developer Guide*: BillingAccount](https://developer.salesforce.com/docs/atlas.en-us.262.0.eu_developer_guide.meta/eu_developer_guide/sforce_api_objects_billingaccount.htm "Energy and Utilities Cloud Developer Guide: BillingAccount - HTML (New Window)")
