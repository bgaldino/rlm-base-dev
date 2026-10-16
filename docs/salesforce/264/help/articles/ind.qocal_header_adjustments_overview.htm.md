---
article_id: ind.qocal_header_adjustments_overview.htm
title: Set Up Header Adjustments
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_header_adjustments_overview.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_common_capabilities.htm
fetched_at: 2026-09-04
---

# Set Up Header Adjustments

Configure header adjustments to help your sales reps to apply discounts to an entire quote or order. Use the Discount Distribution Service (DDS) element in your pricing procedures to support this feature.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) where Transaction Management is enabled
USER PERMISSIONS NEEDED
To create pricing procedures:	Salesforce Pricing Design Time User permission set
IMPORTANT You can’t apply discount distribution to a pricing procedure that was used to calculate a product's derived price. This means that you can't have a Derived Price and a Discount Distribution Service element within the same pricing procedure.
SEE ALSO
Apply Header Adjustments to Quotes and Orders
Option 1: Set Up Header Adjustments Without Derived Pricing
Clone your Transaction Management pricing procedure.
Open the version in Pricing Procedure Builder and delete any existing derived pricing elements.
Add constants for header distribution types.
See Create Constant Resources.
Constant DDS Amount - Type: Text and Value: Amount
Constant DDS Percentage - Type: Text and Value: Percentage
Constant DDS Override - Type: Text and Value: Override
Add a List Group and Assignment for each discount type - Amount, Percentage, and Override.
Configure the Discount Distribution Service element and map the header variables.
In Revenue Settings, turn on Header Adjustments.
Option 2: Set Up Header Adjustments With Derived Pricing
Configure a separate pricing procedure specifically for the Discount Distribution Service element.
Create a Procedure Plan Definition for Quotes and another for Orders.
See Create a Custom Procedure Plan Definition.
Add two sections to the plan for these calculations.
Standard Pricing
DDS Pricing Procedure
In Revenue Settings, turn on Procedure Plan Orchestration for Pricing and turn on Header Adjustments.
