---
page_id: quote_and_order_capture_fields_on_quote.htm
title: Transaction Management Fields on Quote
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/quote_and_order_capture_fields_on_quote.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: quote_and_order_capture_fields_on_standard_objects.htm
fetched_at: 2026-06-09
---

# Transaction Management Fields on Quote

Standard and custom fields extend the standard Quote object for use in
Transaction Management to represent information about quotes. This object is available
in API version 60.0 and later.

## Special Access Rules

To view these fields, you must have the Revenue Cloud Advanced license. See [Quote](https://developer.salesforce.com/docs/atlas.en-us.262.0.object_reference.meta/object_reference/sforce_api_objects_quote.htm) for fields on the Salesforce platform
object.

## Fields

| Field | Details |
| --- | --- |
| AdjustmentDistributionLogic | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Specifies how the overall discount amount is distributed among all the quote line items that have prices associated with them.  The amount distributed is either the value specified in the AppliedDiscountAmount field or the difference between the values in the calculated TotalPrice and the user-specified TotalPriceOverride fields.  Valid values are:  - `Equal`—Distributes the discount amount   equally among all the quote line items. - `Proportionate`—Distributes the discount   amount in proportion to the   ListPriceTotal values of the quote   line items.  Available in API version 65.0 and later. |
| AppliedDiscount | Type  percent  Properties  Create, Filter, Nillable, Sort, Update  Description  The percent discount applied to each quote line item. Available in API version 65.0 and later. |
| AppliedDiscountAmount | Type  currency  Properties  Create, Filter, Nillable, Sort, Update  Description  The discount amount that’s distributed among all the quote line items that have prices associated with them. This amount is distributed based on the logic specified in the AdjustmentDistributionLogic field. Available in API version 65.0 and later. |
| LastPricedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date when the quote is last priced. |
| OriginalActionType | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  Specifies the action that created the quote.  Valid values are:  - `Amend`—Indicates   that the quote was created to amend assets. - `Cancel`—Indicates   that the quote was created to cancel assets. - `Renew`—Indicates   that the quote was created to renew assets. - `Transfer`—Indicates that the quote was   created to transfer assets.  Available in API version 61.0 and later. |
| PartnerAccountId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  ID of the related partner account.  This field is a relationship field.  Relationship Name  PartnerAccount  Relationship Type  Lookup  Refers To  Account |
| TotalPriceOverride | Type  currency  Properties  Create, Filter, Nillable, Sort, Update  Description  The value that the TotalPrice field must be set to by applying overall discounts.  Transaction Management calculates the overall discount amount by finding the difference between the value in the calculated TotalPrice field and the value in this field. It then uses the logic specified in the AdjustmentDistributionLogic field to distribute the discount amount among all the quote line items that have prices associated with them.  Available in API version 65.0 and later. |
| TotalPriceWithTax | Type  currency  Properties  Filter, Nillable, Sort  Description  The sum of TotalPrice and TotalTaxAmount.  This field is available only when you turn on Add Estimated Tax to Quotes and Orders settings and enable Revenue Cloud in your Revenue Cloud org.  Available in API version 64.0 and later. |
| TotalTaxAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The total amount of all taxes.  This field is available only when you turn on Add Estimated Tax to Quotes and Orders settings and enable Revenue Cloud in your Revenue Cloud org.  Available in API version 64.0 and later.  This field is a calculated field. |
| TransactionType | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Specifies the type of quote being processed.  Valid value is:  - `AdvancedConfigurator`—Indicates that the   transaction must be processed by using the configuration   rules and constraints set up in Constraint Rules Engine.  Available in API version 62.0 and later. |
| ValidationResult | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Specifies whether the quote was configured and priced.  This field serves as a staleness indicator. When this value is blank, pricing is up-to-date. When this value is set, it signals that the quote needs attention before its pricing can be trusted.  Valid values are:  - `Blank/null`—Specifies that the quote pricing   is current and valid. - `MissingContributor`—Specifies that the quote   contains a derived product but not its pricing source. This   occurs when the quote contains derived products without its   necessary pricing sources. - `TransactionIncomplete`—Specifies that the   quote wasn’t configured and priced. This typically occurs   when a line item or action is modified outside the standard   pricing flow, such as saving changes through a method other   than the Place Quote or Place Sales Transaction API.  Available in API version 61.0 and later. |
