---
article_id: ind.rm_rate_management.htm
title: Configure Rate Pricing Calculations in Agentforce Revenue Management
source_url: https://help.salesforce.com/s/articleView?id=ind.rm_rate_management.htm&type=5&release=262
release: 262
release_name: Summer '26
area: rating
fetched_at: 2026-05-11
---

# Configure Rate Pricing Calculations in Agentforce Revenue Management

Use Rate Management to easily define the rates for usage resources granted with the sellable product. Set up rates based on consumption of a usage resource. Define rate adjustments based on the consumption quantity of a usage resource. Use rating procedures to create precise formulas for calculating the final net rate and use the rating waterfall view to understand the rate breakup steps of the rating calculation process.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license
Explore Rate Management in Agentforce Revenue Management
Learn about the licenses required to use rate management and the personas each license supports. Understand the key terms and things to consider when you implement rate management for your organization.
Rate Management Setup
Rate Management provides the key tools to manage rates for consumption-based products. To leverage these tools effectively, you must first complete the setup detailed in this section. This process represents our recommended base configuration and is a prerequisite for building any custom solution. It ensures essential procedures can be customized and data can be synchronized for accuracy. Complete all of the following steps before continuing to design your rating solution.
Rating Procedures
Rating procedures are customizable, ordered stacks of rating elements that are used to calculate the final net rate of a usage resource. Each rating element forms a step in a rating procedure. Rating elements call appropriate lookup tables to perform the rating calculations.
Rating Discovery Procedures
Rating discovery procedures fetch the binding objects, rate cards, rate card entries, and rate adjustments associated with multiple sellable products and usage resources related to a price book. Use the retrieved rate information to provide quotes for usage-based products to customers by using Quote and Order Capture and Asset Lifecycle.
Rate Management Limits
Review the default limits for Rate Management components and their usage. To modify the set default values, ask your Salesforce admin to raise a support ticket.
