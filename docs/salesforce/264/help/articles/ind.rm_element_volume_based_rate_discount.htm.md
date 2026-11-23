---
article_id: ind.rm_element_volume_based_rate_discount.htm
title: Volume-Based Rate Discount
source_url: https://help.salesforce.com/s/articleView?id=ind.rm_element_volume_based_rate_discount.htm&type=5&release=264
release: 264
release_name: Winter '27
area: rating
parent_article: ind.rm_rating_elements.htm
fetched_at: 2026-11-23
---

# Volume-Based Rate Discount

The Volume-Based Rate Discount element calculates the usage resource rate based on the discounts configured for the quantities consumed.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license

For example, create rating rules for a usage resource that’s eligible for a 25% discount for 100 MBs or more units consumed over the granted limits. And a customer consumes 150 MBs.

Volume-Based Rate Discount Variables for Non-Negotiable Rates
To calculate non-negotiable rates, use the RateManagementContext context definition and relate the Volume-Based Rate Discount element with the Rate Adjustment by Volume Entries 2 lookup table.
Volume-Based Rate Discount Variables for Negotiable Rates
To calculate negotiable rates, relate the Volume-Based Rate Discount element with the Volume-based Rate Adjustment by Rate Card Entry ID lookup table.
Add the Volume-Based Rate Discount Element
Here’s how you can add the Volume-Based Rate Discount element to your rating procedure.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.rm_element_volume_based_rate_discount.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
