---
article_id: ind.pricing_considerations_for_importing_and_exporting_pricing_data.htm
title: Considerations for Importing and Exporting Pricing Data
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_considerations_for_importing_and_exporting_pricing_data.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pricing
parent_article: ind.pricing_salesforce_pricing.htm
fetched_at: 2026-09-07
---

# Considerations for Importing and Exporting Pricing Data

Use a packaged file to import and export pricing metadata from one org to another, including pricing recipes, decision tables, context definitions, and pricing procedures. These metadata components are crucial for ‌pricing processes, where pricing procedures use recipes for accurate calculations.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Growth license or the Revenue Cloud Advanced license.

Pricing recipes are associated with decision tables, other individual decision tables, and context definitions. A pricing procedure then calls these definitions to perform pricing calculations. When you export or import this data, you must follow certain guidelines to ensure the data is transferred successfully.

Key considerations when you export pricing data to a package file
Before you do anything else, export your context definitions and decision tables.
When you export a pricing recipe, all the decision tables and discovery procedures mapped to it are packaged together.
The default pricing recipe selected from the Setup page is packaged with the default pricing procedure.
The decision tables associated with a procedure, including the org’s default pricing procedure, are packaged with the procedure.
Key considerations when you import pricing data from a package file
Import your context definitions and decision tables before anything else.
Before you import the pricing procedures, make sure you import all pricing recipes and the decision tables associated with the procedure.
NOTE Before importing data, check your org's current decision tables to ensure you're within the limits. Importing decision tables without verifying available space may cause the data import to fail.
Export and Import Your Pricing Data
To create a new package with your pricing data to reuse them in another Salesforce org, create a new package and deploy it on another Salesforce org.
