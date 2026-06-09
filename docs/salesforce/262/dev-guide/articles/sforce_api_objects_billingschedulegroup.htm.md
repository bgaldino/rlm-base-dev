---
page_id: sforce_api_objects_billingschedulegroup.htm
title: BillingScheduleGroup
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_billingschedulegroup.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# BillingScheduleGroup

Represents a consolidated view of all the billing schedules related
to the order items generated from one asset, including new orders and amendment
orders. This object is available in API version 62.0 and later.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=revenue_lifecycle_management_dev_guide)

#### Important

Where possible, we changed noninclusive terms to align with our
company value of Equality. We maintained certain terms to avoid any effect on customer
implementations.

## Supported Calls

`delete()`, `describeLayout()`, `describeSObjects()`,
`getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `update()`

## Special Access Rules

You need the Billing Admin permission set to access this object.

## Fields

| Field | Details |
| --- | --- |
| AnchorProdtBillingSchdGrpId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The billing schedule group for the anchor product in a usage-based product. The anchor product contains the grants for the usage-based product. This field is available in API version 63.0 and later with Revenue Cloud Billing license.  This field is a relationship field.  Relationship Name  AnchorProdtBillingSchdGrp  Refers To  BillingScheduleGroup |
| BillDayOfMonth | Type  int  Properties  Filter, Group, Nillable, Sort  Description  The day of the month on which a recurring billing process is scheduled to occur. |
| BillToContactId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The ID of the contact related to the billing schedule group.﻿ This field can’t be modified when related billing schedules are in processing.  This field is a relationship field.  Relationship Name  BillToContact  Refers To  Contact |
| BillingAccountId | Type  reference  Properties  Filter, Group, Sort  Description  Required. The ID of the account that's related to the billing schedule group.  This field is a relationship field.  Relationship Name  BillingAccount  Refers To  Account |
| BillingAddress | Type  address  Properties  Filter, Nillable  Description  The compound form of the billing address. Read only. See [Address Compound Fields](https://developer.salesforce.com/docs/atlas.en-us.262.0.api.meta/api/compound_fields_address.htm "HTML (New Window)") for details on compound address fields. |
| BillingArrangementId | Type  reference  Properties  Filter, Group, Sort  Description  Required. The ID of the billing arrangement that’s related to the billing schedule group. Available in API version 66.0 and later.  This field is a relationship field.  Relationship Name  BillingArrangement  Refers To  BillingArrangement |
| BillingMethod | Type  picklist  Properties  Filter, Group, Restricted picklist, Sort  Description  Required. The type of billing used for the source item.  Valid values are:  - `Evergreen` - `OrderAmount` - `Usage` |
| BillingResumptionDate | Type  date  Properties  Filter, Group, Nillable, Sort  Description  The date when billing for the asset related to the billing schedule group is resumed. Available in API version 63.0 and later. |
| BillingScheduleGroupNumber | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  Required. The auto-generated reference number for the billing schedule group. |
| BillingStartMonth | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  This is a read-only field used with annual billing. The field shows the numbers from 1 through 12, which indicate the month when billing begins for an annual subscription. For example, if billing starts in January, the value is 1; if billing starts in June, the value is 6. |
| BillingSuspensionDate | Type  date  Properties  Filter, Group, Nillable, Sort  Description  The date when billing for the asset related to the billing schedule group is suspended. Available in API version 63.0 and later. |
| BillingTerm | Type  int  Properties  Filter, Group, Nillable, Sort  Description  This field is used with BillingTermUnitfield to define a billing cycle. For example, bill every 20 days or every two months. In this example, the BillingTerm field value  is 20 and the BillingTermUnit field value is `Day`. |
| BillingTermUnit | Type  picklist  Properties  Filter, Group, Restricted picklist, Sort  Description  Required. The unit of measurement of the billing term.  Valid values are:  - `BillingMilestonePlan`—Available in API   version 63.0 and later with Revenue Cloud Billing   license. - `Day` - `Month` - `OneTime` - `Quarter` - `Semi-Annual` - `Year` |
| BillingTreatmentId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The billing treatment item that's used to configure invoiceable amounts on the billing schedule group.  This field is a relationship field.  Relationship Name  BillingTreatment  Refers To  BillingTreatment |
| BillingType | Type  picklist  Properties  Filter, Group, Restricted picklist, Sort  Description  Required. The timing of invoicing for a product or service relative to its delivery to the customer.  Valid values are:  - `Advance`—   Invoices a product or service before its delivery. - `Arrears`—   Invoices a product or service after its delivery. |
| BindingInstanceId | Type  reference  Properties  Filter, Group, Nillable, Sort, Update  Description  The asset or custom object record associated with the billing schedule group. This field is available in API version 63.0 and later with Revenue Cloud Billing license.  This field is a polymorphic relationship field.  Relationship Name  BindingInstance  Refers To  Asset |
| CancellationDate | Type  date  Properties  Filter, Group, Nillable, Sort  Description  The date from when the user can no longer access the service. For example, if a service ends on August 31, the cancellation date is September 1 because that’s the date from when the user can no longer use the service. Billing schedules past their cancellation date aren't invoiced. |
| Controller | Type  picklist  Properties  Filter, Group, Restricted picklist, Sort  Description  Required. During the invoicing process, this field determines which date is used when the billing schedule group and billing schedule have a related field with conflicting values. For example, when Controller has a value of `BillingScheduleGroup`, if the billing schedule's billing day of month is 5 while the billing schedule group's billing day of month is 10, the invoice is sent on the 10th day of the month.  Valid values are:  - `BillingScheduleGroup` - `None` |
| EffectiveNextBillingDate | Type  date  Properties  Filter, Group, Nillable, Sort  Description  The earliest NextBillingDate from all billing schedules in the billing schedule group. This field is a reference field that isn't used for any features or calculations.  This field is a calculated field. |
| EndDate | Type  date  Properties  Filter, Group, Nillable, Sort  Description  The end date of the billing schedule group. |
| ExternalBindingInstance | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The custom target associated with the entitlements that are granted with the sellable product. This field is available in API version 63.0 and later with Revenue Cloud Billing license. |
| ExternalRefRecordIdentifier | Type  string  Properties  Filter, Group, Nillable, Sort, Update  Description  The identifier of the external record for which the billing schedule group was created. Available in API version 64.0 and later. |
| LegalEntityId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The ID of the legal entity that's related to the billing schedule group.  This field is a relationship field.  Relationship Name  LegalEntity  Refers To  LegalEntity |
| NextBillingDateOverride | Type  date  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The next billing date for all the billing schedules related to the billing schedule group. If specified, this date overrides the next billing dates of the billing schedules. Available in API version 63.0 and later. |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Required. The ID of the user who created the billing schedule group.  This field is a polymorphic relationship field.  Relationship Name  Owner  Refers To  Group, User |
| PaymentTermId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The ID of the payment term used in this billing schedule group. ﻿This field can’t be modified when related billing schedules are in processing.  This field is a relationship field.  Relationship Name  PaymentTerm  Refers To  PaymentTerm |
| PeriodBoundary | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  This field is inherited from the order item's parent quote line item or sales transaction item. The period boundary determines the start and end date of the billing periods.  Valid values are:  - `AlignToCalendar` - `Anniversary` - `DayOfPeriod` - `LastDayOfPeriod` |
| Product2Id | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The product that was charged or ordered to create the billing schedule group.  This field is a relationship field.  Relationship Name  Product2  Refers To  Product2 |
| ProductName | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The name of the product for the order item that's represented by each billing schedule in the billing schedule group. |
| ProrationPolicyId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The ID of the proration policy that applies to this billing schedule group. The proration policy defines how time periods are calculated for orders. For example, whether partial periods are allowed. This field is inherited from the shared proration policy for each billing schedule in the billing schedule group.  This field is a relationship field.  Relationship Name  ProrationPolicy  Refers To  ProrationPolicy |
| ReferenceEntityId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The asset used to create the billing schedules in the billing schedule group.  This field is a relationship field.  Relationship Name  ReferenceEntity  Refers To  Asset |
| ReferenceRecordId | Type  reference  Properties  Filter, Group, Nillable, Sort, Update  Description  The ID of the Salesforce record for which the billing schedule group was created. Available in API version 64.0 and later.  This field is a polymorphic relationship field.  Relationship Name  BillingScheduleGroups |
| SavedPaymentMethodId | Type  reference  Properties  Filter, Group, Nillable, Sort, Update  Description  The ID of the SavedPaymentMethod record that's used to collect payment for the billing schedule group. Available in API version 64.0 and later.  This field is a relationship field.  Relationship Name  BillingScheduleGroups  Refers To  SavedPaymentMethod |
| ShipFromAddress | Type  address  Properties  Filter, Nillable  Description  The address from which the product in the billing schedule group is shipped. Available in API version 64.0 and later. |
| ShippingAddress | Type  address  Properties  Filter, Nillable  Description  The compound form of the shipping address. See [Address Compound Fields](https://developer.salesforce.com/docs/atlas.en-us.262.0.api.meta/api/compound_fields_address.htm "HTML (New Window)") for details on compound address fields.  This field is a read-only field. |
| StartDate | Type  date  Properties  Filter, Group, Nillable, Sort  Description  The earliest start date from all billing schedules in the billing schedule group. |
| TaxTreatmentId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The ID of the tax treatment record that's used to calculate tax for the billing schedule group. This value is defined based on the order item's tax policy.  This field is a relationship field.  Relationship Name  TaxTreatment  Refers To  TaxTreatment |
| TotalBilledAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The amount that has been invoiced for the billing schedules within the billing schedule group.  This field is a calculated field. |
| TotalPendingAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The amount that hasn't yet been invoiced for the billing schedules within the billing schedule group.  This field is a calculated field. |
| UsageType | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  The usage type for the billing schedule group.  Valid values are:  - `Revenue Cloud` - `Commerce Cloud` - `Insurance Cloud`  Available in API version 66.0 and later. |
