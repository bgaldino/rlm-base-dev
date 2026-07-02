---
article_id: ind.billing_invoice_scheduler_amended_bundle_schedule_groups.htm
title: Generated Invoice Details
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_invoice_scheduler_amended_bundle_schedule_groups.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Generated Invoice Details

View the relationship between invoice lines in invoice line bundles generated for billing schedule group bundles. For amended billing schedules, eliminate manual calculations by automatically generating consolidated invoices. The amounts on invoice lines that are generated for amended, canceled, and renewed assets are matched to the corresponding billing schedule amounts, ensuring accuracy. The invoice lines generated for usage resources contain the consumed quantity and the applied overage charges. The invoice lines generated for orders with quantities in decimals inherit the same quantity and unit of measure.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with Agentforce Revenue Management


This feature is available with the Agentforce Revenue Management Advanced license or the Agentforce Revenue Management Billing license.

The Usage Management feature is available only with the the Agentforce Revenue Management Billing license. Contact your Salesforce account executive for more information.

Invoices for Amended, Renewed, or Canceled Assets

If there are billing schedules for amended, renewed, canceled assets, invoice lines are created for the same positive or negative amounts as those of the billing schedules.

Single Invoice Line for Amended Billing Schedules

When an asset is amended and the related amendment order is activated, amended billing schedule groups are generated. When you generate an invoice for an amended billing schedule, the details of the original and the amended order product are automatically consolidated into a single invoice line. The criteria to generate a consolidated invoice line is that the original and amended order product must have the same Billing Period Start Date and Billing Period End Date. The Has Multiple Items field of the amended Invoice Line record indicates if there are multiple billing period items for the invoice. If there are multiple billing period items, they appear on the Billing Period Items related list.

EXAMPLE If an asset priced at $5 per unit is amended by adding five units to an existing ten units, then the consolidated invoice line reflects a total of 15 units at a Charge Amount of $75.
Invoices for Usage-Based Products

For usage-based charge types, invoice lines for usage resources include details about the total consumed quantity, any overage quantity, and applicable overage charges. Usage-based products are invoiced when the liable summary, usage entitlement bucket, and usage entitlement account share the same grant binding target.

See Track Product Usage and Consumption in Revenue Cloud.

Quantity and Unit of Measure for Invoice Lines

Invoice lines inherit their quantity and unit of measure from the related billing schedules’ quantity and unit of measure. An invoice line’s quantity is rounded off based on the scale and rounding method of the quantity’s unit of measure.

See Generated Billing Schedule Details.

Invoice Line Bundles for Billing Schedule Group Bundles

When an invoice run processes a billing schedule group bundle, the corresponding invoice line bundles are generated. These invoice line bundles are displayed hierarchically in the Invoice Lines related lists of the Invoice record, distinguishing related and independent products.

All the invoice lines related to an invoice line bundle appear in the Associated Invoice Lines (1) related list of the Invoice Line Bundle record.
The invoice line bundle related to an invoice line appears in the Main Invoice Lines (2) related list of the Invoice Line record.

If the line amount of invoice lines in a bundle is zero, the parent invoice line shows the total line amount for the entire bundle.
