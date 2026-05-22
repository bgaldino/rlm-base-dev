---
article_id: ind.um_configure_usage_records.htm
title: Configure Usage Management Records Manually
source_url: https://help.salesforce.com/s/articleView?id=ind.um_configure_usage_records.htm&type=5&release=262
release: 262
release_name: Summer '26
area: usage
fetched_at: 2026-05-11
---

# Configure Usage Management Records Manually

Use manual configuration when your setup requires direct control over individual records or involves product types that the guided workflow doesn't support.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Advanced license and the Revenue Cloud Billing license

To successfully set up your usage management system, you must configure your usage records in a specific sequence. Follow the configuration tasks in order because each record depends on the records created before it.

Create a Unit of Measure Class
Unit of measure class defines the groupings of units of measure (UOM). For example, the Currency unit of measure class groups various currencies, such as euros, dollars, and rupees.
Create Units of Measure
A unit of measure quantifies the consumption of a usage resource. You can define units of measure to support a wide range of usage resources. For example, a unit of measure can be time-based, volume-based, transaction-based, or count-based.
Create Usage-Based Products
Evaluate and select the appropriate usage model type for creating a sellable product.
Create a Usage Resource
Usage resource is an entitlement or service that you grant your customers along with a product that you sell. Before you define rates and rate adjustments for usage resources, create usage resources for your products.
Create a Product Usage Resource
Associate existing usage resources with products, with a limit of one token resource per product.
Create a Product Usage Grant
Define the details of a grant associated with a resource, product, or service, such as the granted quantity, renewal and rollover policy, and the grant's validity period.
Create Usage Aggregation Policy
Define the method used to aggregate consumption of a usage resource over a period.
Create Rating Frequency Policy
The rating frequency policy defines how often the rating for a sellable product and a usage resource should be computed.
Create a Usage Overage Policy
Define the set of rules that determine how units consumed beyond the granted limit are managed for a usage resource.
Create Usage Grant Refresh Policy
Define whether the grants provided with the usage resource can be refreshed and the frequency of the grant refresh.
Create Usage Grant Rollover Policy
Each grant provided with the product has a validity period. Usage grant rollover policies define whether the usage resource’s grants expire or can be rolled over after the initial validity period is completed.
Create Usage Product Grant Binding Policy
Define the association between the usage resource’s grant with the sellable product.
Create a Usage Resource Policy
Define the policies applicable to a usage resource, regardless of whether it's associated with a sellable product.
Create a Product Usage Resource Policy
Define the policies that apply when a usage resource is associated with a sellable product. After the product is sold, these rules automatically apply to the resource. The policies you select here override the policies defined in the individual usage resource policy record.
Create a Usage Commitment Policy
Define the set of rules that determine how commitments are applied to a usage resource.
Create a Usage Commitment Asset Related Object
Apply discounted rates and additional grants available for the commitment product to the resources consumed by an anchor product. To provide these benefits, link the commitment product to the anchor product.
