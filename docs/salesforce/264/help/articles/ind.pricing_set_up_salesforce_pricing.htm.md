---
article_id: ind.pricing_set_up_salesforce_pricing.htm
title: Salesforce Pricing Basic Setup
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_set_up_salesforce_pricing.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pricing
parent_article: ind.pricing_salesforce_pricing.htm
fetched_at: 2026-09-07
---

# Salesforce Pricing Basic Setup

Salesforce Pricing provides the key tools to manage your pricing infrastructure. To leverage these tools effectively, you must first complete the basic setup detailed in this section. This process represents our recommended base configuration and is a prerequisite for building any custom solution. It ensures essential pricing configuration can be transferred, procedures can be customized, and data can be synced for accuracy. Complete all of the following steps before continuing on to design your pricing solution.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Growth license or the Revenue Cloud Advanced license.
Configure Decision Tables
Decision tables form the foundation of your pricing logic. Salesforce Pricing evaluates complex rules and looks up specific values, such as list prices, discounts, or volume tiers, based on defined input criteria. Configure standard decision tables that pull data directly from your Salesforce objects.
Pricing Recipes Setup
Pricing Recipes in Salesforce Pricing enable you to create and manage detailed pricing strategies. These recipes associate data from selected objects with decision tables to develop comprehensive pricing procedures. Understanding pricing recipes is crucial for successfully leveraging Salesforce Pricing.
Select a Pricing Procedure
To apply pricing rules and logic to calculate the final net price of a product, you must first clone a predefined pricing procedure available with Salesforce Pricing or build a custom one. This is necessary because Salesforce ships a predefined template, not an executable procedure, meaning templates can’t be directly configured for use.
Sync Pricing Data in Revenue Management
Regularly sync your pricing data in Salesforce Revenue Management to ensure the latest information is available in decision tables that are mapped to a pricing recipe and have their usage type set to Pricing.
Set Up Price Waterfall
To ensure transparency and accuracy in final product price determination, utilize Price Waterfall to understand and verify your pricing calculations at each step. This is particularly valuable when tracking complex pricing structures, including volume discounts and other tiered adjustments.
Set Up Price Logs Capture
To collect logs captured by pricing APIs, turn on Price Logs Capture.
Configure Salesforce Pricing Objects
To optimize Salesforce Pricing, configure the page layouts for Product, Price Book Entry, and Price Adjustment Schedule objects to ensure the proper display and functionality of pricing-related fields and related lists, thereby guaranteeing accurate product and service pricing and streamlining sales processes.
Configure Record Sharing for Salesforce Pricing
For runtime users to access the data created by product designers or catalog admins, set up record sharing for all Salesforce Pricing objects. This configuration is crucial for the seamless execution of pricing processes within Salesforce.
