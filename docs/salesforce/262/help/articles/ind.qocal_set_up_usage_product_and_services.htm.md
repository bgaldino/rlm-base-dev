---
article_id: ind.qocal_set_up_usage_product_and_services.htm
title: Set Up Usage-Based Product and Services
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_set_up_usage_product_and_services.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Set Up Usage-Based Product and Services

The first step to sell usage-based products is to set up the product structure, its resources, and setting up the grants provided with the sellable product.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
Define Usage Resources and Units of Measure

Use the Usage Resource object to define services that are provided as grants, units of measure to measure these services, and unit of measure classes to group the units of measure.

Configure Sellable Product and Mapping

To provide the usage-based services, you must associate it with a sellable product. Create a sellable product by selecting a usage model type in the product record. To create a mapping between a sellable product and the related services, create a product usage resource record.

Setup Commits, Grants, and Entitlements

If your sellable product provides an initial quantity of associated services—grants, configure Product Usage Grants. A product usage grant record includes details, such as the number of grants provided with the sellable product, validity of the granted quantity, a set of policies that defines the behavior of the grants, and the order in which the service units will be debited. Similarly, if you're working with a commitment-based usage product, select the Commit type while configuring the product usage grant record.

Configure Policies

The usage resources, grants, and entitlements are governed by various policies.

Usage Aggregation Policy—defines how Usage Management aggregates the consumption data.
Usage Overage Policy—defines whether overconsumed resource units are charged.
Rating Frequency Policy—defines the frequency at which rating is triggered for the ratable summary records.
Renewal and Rollover Policies—determines when the grant resets and whether the unused units carry over to the next period, respectively.
Product Usage Resource Policy—associates all policies applicable to the usage resource.
Usage Commitment Policy—defines the set of rules that determines the rate applicable for overage computation after the commitment is fulfilled. You can either select the discounted commit rate or use the rate applicable for the bounded target.
EXAMPLE

Define a usage-based product—a mobile plan; create and associate usage resources—call minutes and data; to measure these services, create units of measure—Minutes and GB and group them into units of measure classes—Time and Data. To ensure all services consumed in the accumulation period are aggregated, define the usage aggregation policy with the Sum accumulation method.

SEE ALSO
Enable Usage Management
Usage Management Setup
Validate Your Setup
