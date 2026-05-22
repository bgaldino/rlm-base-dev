---
article_id: ind.qocal_create_ramp_deal_for_groups_for_usage_products.htm
title: Ramp Deals for Groups for Usage Products
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_create_ramp_deal_for_groups_for_usage_products.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Ramp Deals for Groups for Usage Products

Use ramp deals for groups for usage products to break down a long-term deal into smaller time-based segments.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license

Let’s look at DataFlow, a software company, that sells a data transfer service with tiered pricing based on usage. They want to offer a promotional deal to a new customer, GlobalCorp, for a three-year contract.

Set Up Subscription: GlobalCorp signs a three-year subscription. The sales rep sets up a ramp deal with three annual grouped segments.
Group Products: The rep creates a group in the quote called Data Transfer Services and adds all usage-based products, such as DB inbound data transfer and DB outbound data transfer.
Define Ramp Schedule: The rep defines the ramp schedule for the group, with each segment lasting one year.
Ramp 1 (Year 1): To attract GlobalCorp, DataFlow offers a 20% discount on all data transfer usage for the first year.
Ramp 2 (Year 2): The discount is reduced to 10% for the second year.
Ramp 3 (Year 3): Rating is done on the standard rate, and DataFlow includes a loyalty grant of 100 GB of free data transfer to encourage renewal.
Billing: As GlobalCorp uses the service, usage management automatically applies the correct pricing for each year.

This approach provides a clear rating structure for the customer while helping the company to adjust rates and offer incentives over time. See Set Up Ramp Deals for Groups for your usage products.

Considerations for Managing Ramp Deals for Groups for Usage Products
Learn how to effectively manage your ramp segments for usage products.
