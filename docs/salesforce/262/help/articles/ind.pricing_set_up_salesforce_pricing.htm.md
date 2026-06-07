---
article_id: ind.pricing_set_up_salesforce_pricing.htm
title: Salesforce Pricing Basic Setup
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_set_up_salesforce_pricing.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Salesforce Pricing Basic Setup

Salesforce Pricing provides the key tools to manage your pricing infrastructure. To leverage these tools effectively, you must first complete the basic setup detailed in this section. This process represents our recommended base configuration and is a prerequisite for building any custom solution. It ensures essential pricing configuration can be transferred, procedures can be customized, and data can be synced for accuracy. Complete all of the following steps before continuing on to design your pricing solution.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Salesforce Pricing is enabled
Configure Decision Tables
Decision tables form the foundation of your pricing logic. Salesforce Pricing evaluates complex rules and looks up specific values, such as list prices, discounts, or volume tiers, based on defined input criteria. Configure standard decision tables that pull data directly from your Salesforce objects.
Set Up Pricing Recipes

Select a Pricing Procedure
To apply pricing rules and logic to calculate the final net price of a product, you must first clone a predefined pricing procedure available with Salesforce Pricing or build a custom one. This is necessary because Salesforce ships a predefined template, not an executable procedure, meaning templates can’t be directly configured for use.
Sync Pricing Data in Agentforce Revenue Management
Regularly sync your pricing data in Salesforce Agentforce Revenue Management to ensure the latest information is available in decision tables that are mapped to a pricing recipe and have their usage type set to Pricing.
Set Up Price Waterfall in Salesforce Pricing

Set Up Price Logs Capture
To collect logs captured by pricing APIs, turn on Price Logs Capture.
Configure Salesforce Pricing Objects
To optimize Salesforce Pricing, configure the page layouts for Product, Price Book Entry, and Price Adjustment Schedule objects to ensure the proper display and functionality of pricing-related fields and related lists, thereby guaranteeing accurate product and service pricing and streamlining sales processes.
Configure Record Sharing for Salesforce Pricing
For runtime users to access the data created by product designers or catalog admins, set up record sharing for all Salesforce Pricing objects. This configuration is crucial for the seamless execution of pricing processes within Salesforce.
