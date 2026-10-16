---
article_id: ind.um_usage_management_limits.htm
title: Usage Management Limits
source_url: https://help.salesforce.com/s/articleView?id=ind.um_usage_management_limits.htm&type=5&release=264
release: 264
release_name: Winter '27
area: usage
parent_article: ind.um_usage_management.htm
fetched_at: 2026-09-07
---

# Usage Management Limits

Before you plan and set up usage management, sell consumption-based products, or process their consumption, review the supported limits and features.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
Usage Selling
A quote or an order can have up to:
200 quote line items or order items
200 quote line item rate card entries
800 quote line item rate adjustments
Usage Management doesn't support selling usage-based products as part of a product bundle.
You can't add a usage-based product as a child component within a bundled product. For example, adding a usage-based API consumption product as part of a software bundle.
You can't configure a usage-based product as the parent product of a bundle. For example, creating a bundle where the main product tracks consumption.
To sell multiple usage-based products together, add them as separate line items on the same quote or order rather than bundling them into a single product.
You can sell usage-based and non-usage products in the same order, but they must be separate line items.
Usage Selling doesn’t support these Transaction Management features:
Evergreen or onetime anchor products
Early renewals for ramp and non-ramp assets are supported for Usage Selling, but not for Consumption Management.
Renewals of expired assets is supported for Usage Selling, but not for Consumption Management.
Start-date amendments, including pulling in or pushing out the start date
End-date amendments
Account and asset transfers
Amendment of a usage-based product with a future-dated and back-dated change.
Upgrades, downgrades, and swaps
Backdated amendments, renewals, and cancellations
Amendment rollbacks
Revival of canceled assets
Pausing and resuming assets
Consumption Management

Consumption Management requires Usage Selling and has the same Usage Selling limitations. In addition, Consumption Management has these limitations:

Consumption Management objects don’t support creating records in Data Cloud.
Consumption Management doesn’t support processing of data from monetary and quantity commitment products.
