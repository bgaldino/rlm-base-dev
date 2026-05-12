---
article_id: ind.um_guided_workflow_considerations.htm
title: Guided Workflow Considerations and Limits
source_url: https://help.salesforce.com/s/articleView?id=ind.um_guided_workflow_considerations.htm&type=5&release=262
release: 262
release_name: Summer '26
area: usage
fetched_at: 2026-05-11
---

# Guided Workflow Considerations and Limits

Review the record limits, supported policy types, and custom field constraints when you configure your usage product.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Advanced license and the Revenue Cloud Billing license
Considerations
You can only edit the usage-related records until they’re in the draft state.
You can add up to 3 mandatory custom fields in the workflow interface. The workflow interface only shows the required custom fields. Optional custom fields are hidden. Supported data types for custom fields include Text, Text Area, Number, Checkbox, Date, Percent, Currency, and Picklist. However, the Product Usage Resource object doesn’t support custom fields.
For product usage resource and product usage grant records, the time for the effective start date defaults to 12:00 AM and the effective end date defaults to 11:59 PM, in your locale.
If you have a custom page layout or custom record page, add the Configure Usage Properties action manually. See Customize Page Layouts and Create and Add Actions in Lightning App Builder.
For ease of setup, Usage Management creates these policies with the names listed in the table. If you already have existing policies with the same configuration, the workflow doesn’t create new policies and uses the existing policies.
POLICY TYPE	POLICY NAME	CONFIGURATION
Usage Aggregation Policy	Aggregate Usage Monthly by Sum	
Usage Accumulation Method—Sum
Usage Accumulation Period—Monthly
Status—Active

Usage Grant Refresh Policy	Renew Grants Monthly	
Renewal Frequency—1
Renewal Frequency Unit—Month

Usage Grant Rollover Policy	Rollover Grants without Expiry	
Rollover Allowed—selected
Allow Rollover Expiry—unselected
Maximum Rollover count—Empty

Usage Overage Policy	Overage Chargeable	
Chargeable—Yes

Usage Commitment Policy	Lowest Commitment Fulfilled Rate	
Commitment Fulfilled Rate—Lowest commitment

Rating Frequency Policy	Rate Usage Monthly	
Rating Period—Monthly
Rating Delay Duration—Empty
Rating Delay Duration Unit—Empty
Limitations

To manage scale, the workflow has these record limits.

The guided workflow doesn’t support:
Commitment-based usage products
Inactive records
Configuring rate management records, price books, and product selling models changes
Customizing field layouts
Configuring global rate cards that all products use if they’re using the same resource
The Add Usage Resource page shows a maximum of 200 usage resources, and users can select a maximum of 10 resources at one time.
The guided workflow supports a maximum of 20 Product Usage Resource (PUR) record creations.
Each PUR supports a maximum of five Product Usage Grant (PUG) records.
