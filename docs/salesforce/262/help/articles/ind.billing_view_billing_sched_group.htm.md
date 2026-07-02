---
article_id: ind.billing_view_billing_sched_group.htm
title: Generated Billing Schedule Details
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_view_billing_sched_group.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Generated Billing Schedule Details

View all the key billing schedule and invoice details in the Billing Schedule Group records.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with Agentforce Revenue Management


This feature is available with the Agentforce Revenue Management Advanced license or the Agentforce Revenue Management Billing license.

The Usage Management feature is only available with the the Agentforce Revenue Management Billing license. Contact your Salesforce account executive for more information.

From the App Launcher, find and select Billing, and then click Billing Schedule Groups. Open any Billing Schedule Group record to view all the required details.

Asset of the Billing Schedule Group

The asset related to the order for which the billing schedule group is created appears on the Asset field of the Billing Schedule Group record.

Billing Schedules for Original, Amended, Renewed, and Canceled Assets

The Billing Schedules related list of a Billing Schedule Group record shows all the billing schedules for original, amended, canceled, and renewed assets. The Billing Schedules tab also shows the same billing schedules with additional details that help you identify and differentiate between them easily.

The billing schedules for original, amended, renewed, or canceled assets are created with the corresponding category.

The billing schedules created for amended or canceled assets have a reference to the original billing schedule that they’re related to.
When you cancel an asset, the cancellation date is populated for all the billing schedules that are related to the billing schedule group for the asset.
EXAMPLE

These examples illustrate the process of how amending and canceling assets affect the creation of billing schedules.

Asset Amendment Scenario: SmartBytes is a large enterprise company that uses Agentforce Revenue Management. One of its longstanding customers, Greenfield Enterprises, wants to purchase 10 more SmartBytes’ DocuCraft software licenses to cater to a rising employee demand. SmartBytes’ sales operations representative amends Greenfield Enterprises’ existing asset for DocuCraft software licenses to include 10 more licenses. On amending the asset, an amendment quote is created. The sales representative then creates an order for the amendment quote and activates it. On activating the order, a billing schedule is created for 10 licenses with Amendment as the category. The billing schedule is also linked to the billing schedule created for the initial asset.

Asset Cancellation Scenario: One of SmartBytes customers, TechCore Solutions, wants to cancel their ongoing order for DocuCraft software. SmartBytes’ sales operations representative cancels TechCore Solutions’ existing asset for DocuCraft software licenses. On canceling the asset, a cancellation quote is created. The sales representative then creates an order for the cancellation quote and activates it. On activating the order, a billing schedule is created with Cancellation as the category. The billing schedule is also linked to the billing schedule created for the initial asset.

Billing Schedules for Orders and Quotes With Future-Dated Changes

Billing automatically generates billing schedules when termed products are amended or renewed before or after future-dated orders or quotes. Any future-dated renewals on one-time and evergreen products are considered as amendments on the associated orders or quotes.

When you cancel an asset before or after the start of a future-dated amendment, Billing automatically generates billing schedules to reflect the correct quantity across different time periods.

When a future-dated amendment, renewal, or cancellation is rolled back before it takes effect, Billing doesn’t modify existing billing schedules. Instead, Billing creates compensating adjustment billing schedules that offset the impact of the rolled-back change. The original billing schedules are retained for historical accuracy, ensuring that future billing reflects the correct amounts and periods while preserving a complete audit trail.

Billing Schedules for Usage-Based Products

For usage-based products and add-on packs, billing schedules are ready for invoicing when the rated usage and overage charges are calculated.

See Track Product Usage and Consumption in Revenue Cloud.

Billing Schedules for Ramped Products

For ramped products, Billing automatically creates a billing schedule group for the asset and individual billing schedules for each ramp segment.

Billing Schedules for Price Changes

For evergreen, one-time, and termed products, Billing automatically generates billing schedules whenever a discount amount or discount percentage is applied on the associated quote or order.

Billing Schedules for Swapped Products

For evergreen, one-time, bundled, and termed products, Billing automatically generates billing schedules for the swapped in and swapped out products during various swap scenarios including and not limited to.

Swap from an evergreen to termed, termed to one-time, or one-time to evergreen product
Swap a bundled product with one or more single products
Swap products during the middle of a billing period
Swap products with different billing frequencies
Swap partial quantities of the same product
Billing Schedules for Updated Subscription End Dates

When a customer changes the end date of a subscription for an order, the related billing schedules are automatically updated to reflect the new service period. Billing regenerates billing schedules during amendments to ensure billing periods are accurate.

Billing Schedules for Billing Milestone Plans

When a billing treatment is configured for milestone-based billing, Billing creates a billing milestone plan and links it to the billing schedule. Billing generates the invoice lines based on the configured milestones. See Milestone Billing for Amended, Renewed, and Canceled Assets.

Main and Associated Billing Schedule Groups

In an order, related products are grouped in a bundle. These order bundles are displayed in a hierarchy to highlight the difference between related and independent products of the order. When billing schedule groups are created for bundled products of an order, billing schedule groups are created for the root bundle product and for each child product. Each order bundle corresponds to a billing schedule bundle.

On the Billing Schedule Group record that’s created for a root bundle product, the billing schedule groups that are created for the child products appear in the Associated Billing Schedule Group related list.

On the Billing Schedule Group record that’s created for a child product, the billing schedule group that's created for the root bundle product appears in the Main Billing Schedule Group related list.

Billing History Tab

The Billing History tab shows all the billing period items, billing milestone plan items, invoice lines, and revenue transaction error logs that are related to the billing schedule group.

View the related billing period items to track the billing schedules that were processed and the expected amount to be billed for an invoice.
View all the billing milestone plan items for the product to understand the status of the project milestones and the milestone amount.
View all the invoice lines that are generated for the product.
Troubleshoot invoice batch run errors by accessing all the revenue transaction error logs for a billing schedule group in a single place.
Preview Invoices Tab

You can generate up to two invoice previews for the billing schedule group. The billing schedule group’s effective next billing date is preselected as the start date for the invoice preview.

See Generate Invoice Previews for Billing Schedule Groups.

Relationships Graph

In addition to the Related tab, the Relationships Actionable Relationship Center (ARC) graph also shows the associated and main billing schedule groups. If the billing schedule group is for a usage-based product, the graph also shows the billing schedule groups for the valid product usage grants of the same product.

Quantity and Unit of Measure

Billing schedules inherit their quantity and unit of measure from the related order products’ quantity and unit of measure. A billing schedule’s quantity is rounded off based on the scale and rounding method of its unit of measure.

See View and Edit Orders in Agentforce Revenue Management and Decimal Quantity Support in Product Catalog Management.

Start and End Dates

Billing prioritizes the start and end dates found on Quote Line Detail and Order Item Detail records. If no dates are specified on the detail records, then Billing uses the dates from the parent order or quote item.
