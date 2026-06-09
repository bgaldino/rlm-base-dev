---
page_id: sforce_api_objects_billingschedule.htm
title: BillingSchedule
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_billingschedule.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# BillingSchedule

Represents information about the order item that's used in the invoicing
process. This object is available in API version 62.0 and later.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=revenue_lifecycle_management_dev_guide)

#### Important

Where possible, we changed noninclusive terms to align with our
company value of Equality. We maintained certain terms to avoid any effect on customer
implementations.

## Supported Calls

`describeLayout()`, `describeSObjects()`, `getDeleted()`,
`getUpdated()`, `query()`, `retrieve()`, `search()`, `update()`

## Special Access Rules

You need the Billing Admin permission set to access this object.

## Fields

| Field | Details |
| --- | --- |
| BillDayOfMonth | Type  int  Properties  Filter, Group, Nillable, Sort  Description  The day of the month on which a recurring billing process is scheduled to occur. |
| BilledAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The total amount (excluding tax) that has been invoiced from the billing schedule.  This field is a calculated field. |
| BillingAccountId | Type  reference  Properties  Filter, Group, Sort  Description  Required. The ID of the account that's related to the billing schedule.  This field is a relationship field.  Relationship Name  BillingAccount  Refers To  Account |
| BillingMethod | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  The type of billing used for the source item.  Valid values are:  - `Evergreen` - `OrderAmount` - `Usage—`Available   in API version 63.0 and later with Revenue Cloud Billing   license. |
| BillingMilestonePlanId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The billing milestone plan associated with the billing schedule. This field is available in API version 63.0 and later with Revenue Cloud Billing license.  This field is a relationship field.  Relationship Name  BillingMilestonePlan  Refers To  BillingMilestonePlan |
| BillingPeriodAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The amount to be invoiced each billing period. For example, if the billing period is monthly, this field shows the monthly amount that appears on the invoice line. |
| BillingScheduleEndDate | Type  date  Properties  Filter, Group, Nillable, Sort  Description  The last date that the billing schedule is available for invoicing. This value is inherited from the EndDate field on the order item. |
| BillingScheduleGroupId | Type  reference  Properties  Filter, Group, Sort  Description  Required. The billing schedule group that contains the billing schedule. Billing schedules are grouped when they have the same source order item. The source order item is the original order item that a customer bought. Afterwards, if the customer amends, cancels, or renews the order item, a new billing schedule is created with the BillingScheduleGroupId for the original order item.  This field is a relationship field.  Relationship Name  BillingScheduleGroup  Relationship Type  Master-detail  Refers To  BillingScheduleGroup (the master object) |
| BillingScheduleNumber | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  Required. The auto-generated reference number for the billing schedule. |
| BillingScheduleStartDate | Type  date  Properties  Filter, Group, Nillable, Sort  Description  The date when the billing schedule is available for invoicing. This value is inherited from the ServiceDate field on the order item. |
| BillingTerm | Type  int  Properties  Filter, Group, Nillable, Sort  Description  The duration for which the customer is invoiced. |
| BillingTermUnit | Type  picklist  Properties  Filter, Group, Restricted picklist, Sort  Description  Required. The unit of measurement of the billing term.  Valid values are:  - `BillingMilestonePlan`—Available in API   version 63.0 and later with Revenue Cloud Billing   license. - `Day` - `Month` - `OneTime` - `Quarter` - `Semi-Annual` - `Year` |
| BillingTreatmentId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The ID of the billing treatment record associated with the billing schedule. Available in API version 67.0 and later.  This field is a relationship field.  Relationship Name  BillingTreatment  Refers To  BillingTreatment |
| BillingTreatmentItemId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The billing treatment item that's used to configure invoiceable amounts on the billing schedule.  This field is a relationship field.  Relationship Name  BillingTreatmentItem  Refers To  BillingTreatmentItem |
| BillingType | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The timing of invoicing for a product or service relative to its delivery to the customer.  Valid values are:  - `Advance`—   Invoices a product or service before its delivery. - `Arrears` —   Invoices a product or service after its delivery. |
| CancellationDate | Type  date  Properties  Filter, Group, Nillable, Sort  Description  The date from when the user can no longer access the service. For example, if a service ends on August 31, the cancellation date is September 1 because that’s the date from when the user can no longer use the service. Billing schedules past their cancellation date aren't invoiced. |
| Category | Type  picklist  Properties  Filter, Group, Restricted picklist, Sort  Description  Required. The category of the billing schedule.  Valid values are:  - `Amendment`— A   billing schedule for an order that was amended. Available in   API version 67.0 and later. - `AmendQuantity`— A   billing schedule for an order that changes the quantity. - `Cancellation` — A   billing schedule for an order that was canceled. - `Original` — A   billing schedule for the initial order. - `Renewal` — A   billing schedule for an order that was renewed. |
| CustomInvoiceGroupKey | Type  string  Properties  Filter, Group, Restricted picklist, Sort  Description  The group identifier for which an invoice must be generated when the invoice group type is `Custom`.  This field is available in API version 63.0 and later with Revenue Cloud Billing license. |
| InvBatchDraftToPostedRunId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The batch job that posts all invoices with a status as `Draft` that are generated by the invoice batch run associated with the billing schedule.  This field is a relationship field.  Relationship Name  InvBatchDraftToPostedRun  Refers To  InvBatchDraftToPostedRun |
| InvoiceBatchRunId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The invoice batch run that evaluated the billing schedule and its billing period items to generate an invoice.  This field is a relationship field.  Relationship Name  InvoiceBatchRun  Refers To  InvoiceBatchRun |
| InvoiceGroupType | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Specifies whether to generate an invoice for a billing schedule, a custom group, or the default group of account, bill-to-contact, payment term, currency, and tax engine.  Valid values are:  - `Billing Schedule` - `Custom` - `Default`  This field is available in API version 63.0 and later with Revenue Cloud Billing license. |
| InvoiceRunMatchingValue | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The batch value used by the invoice run that evaluated the billing schedule. During an invoice run, billing schedules with the same batch value, including null, are grouped to the same invoice run. |
| LineAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The amount associated with a specific line item in the billing schedule. Available in API version 63.0 and later. |
| NetUnitPrice | Type  currency  Properties  Filter, Nillable, Sort  Description  The net unit price of the order item for which the billing schedule was created. Available in API version 64.0 and later. |
| NextBillingDate | Type  date  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The date that the next billing period starts for the invoice. This date is used to calculate which invoice lines are included on an invoice. When an invoice scheduler or API evaluates an order for invoicing, billing schedules with a next billing date on or before the invoice's target date are included in the invoice. |
| NextChargeFromDate | Type  date  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The date that the billing schedule is invoiced in the upcoming billing period. For example, if you invoiced a customer for a billing period of 01/01/24 through 01/31/24, the billing schedule's NextChargeFromDate is 02/01/22. |
| OriginalBillingScheduleId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  If the billing schedule is an amended or canceled billing schedule, then this field shows the original billing schedule. Otherwise, this field is null.  This field is a relationship field.  Relationship Name  OriginalBillingSchedule  Refers To  BillingSchedule |
| PendingAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The amount from the current billing term that hasn't been billed yet. For example, the unbilled amount for a month, quarter, or year, depending on this billing schedule's billing term. |
| PricingTermUnit | Type  picklist  Properties  Filter, Group, Restricted picklist, Sort  Description  Required. The unit of time for which the pricing of the product applies.  Valid values are:  - `Months` - `Quarterly` - `Semi-Annual` - `Annual`  Available in API version 66.0 and later. |
| ProcessingOrder | Type  int  Properties  Filter, Group, Nillable, Sort  Description  Specifies the order in which billing transactions are applied. Available in API version 67.0 and later.  This field is an autogenerated field. |
| Quantity | Type  double  Properties  Filter, Nillable, Sort  Description  The quantity of the order item that created the billing schedule. |
| Reference | Type  reference  Properties  Filter, Group, idLookup, Sort  Description  The ID of the parent record of the reference item for which the billing schedule is created. Available in API version 61.0 and later. |
| ReferenceEntityId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The parent order of the order item that created the billing schedule.  This field is a polymorphic relationship field.  Relationship Name  ReferenceEntity  Refers To  Order |
| ReferenceEntityItemId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The order item or asset that created the billing schedule.  This field is a polymorphic relationship field.  Relationship Name  ReferenceEntityItem  Refers To  OrderItem, OrderItemAdjustmentLineItem |
| ReferenceItem | Type  reference  Properties  Filter, Group, idLookup, Sort  Description  The ID of the transaction line item record for which the billing schedule is created. Available in API version 61.0 and later. |
| SubCategory | Type  picklist  Properties  Filter, Group, Restricted picklist, Sort  Description  The subcategory of the billing schedule. Available in API version 67.0 and later.  Valid values are:  - `AsIsRenewal` - `BillingFrequencyAmendment` - `ChangeEndDate` - `DeltaPriceAmend` - `PriceAmend` - `QuantityAmendment` - `SimplifiedCancel` - `SimplifiedRenewal` |
| Status | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  Required. The status of the order item that the billing schedule represents.  Valid values are:  - `WaitingForMilestoneEventAccomplishment`—Available   in API version 63.0 and later with Revenue Cloud Billing   license. - `CompletelyBilled` - `Error` - `Processing` - `ReadyForInvoicing` |
| TaxTreatmentId | Type  reference  Properties  Filter, Group, Sort  Description  Required. The ID of the treatment that's used to calculate tax for the billing schedule. This value is defined based on the order item's tax policy.  This field is a relationship field.  Relationship Name  TaxTreatment  Refers To  TaxTreatment |
| TotalAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The total amount of the order item represented by the billing schedule. |
| Type | Type  picklist  Properties  Filter, Group, Restricted picklist, Sort  Description  The type of the billing schedule.  Valid values are:  - `LineItemAdjustedCharge` - `LineItemAdjustment` - `LineItemCharge` |
| UnitOfMeasureId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The ID of the unit of measure for the billing schedule. Available in API version 63.0 and later.  This field is a relationship field.  Relationship Name  UnitOfMeasure  Refers To  UnitOfMeasure |
| UnitPrice | Type  currency  Properties  Filter, Nillable, Sort  Description  The price for an individual unit of the billing schedule's parent order item, including charges, adjustments, and discounts. This value is inherited from the order item's UnitPrice field. |
| UsageResourceId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The usage resource associated with the billing schedule. This field is available in API version 63.0 and later with Revenue Cloud Billing license.  This field is a relationship field.  Relationship Name  UsageResource  Refers To  UsageResource |
