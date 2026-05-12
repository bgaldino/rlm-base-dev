---
article_id: ind.pricing_advanced_price_log_settings.htm
title: Set Up Advanced Price Logs
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_advanced_price_log_settings.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Set Up Advanced Price Logs

Capture input values and exception details for complex pricing elements. Use this diagnostic data to identify and fix performance issues.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Salesforce Pricing is enabled
USER PERMISSIONS NEEDED
To turn on advanced price logs:	Salesforce Pricing Admin
IMPORTANT We strongly recommend that you enable advanced logging only during active troubleshooting, and turn it off immediately after debugging is complete to maintain optimal system speed and prevent other system issues.
From Setup, in the Quick Find box, enter Salesforce Pricing, and then select Salesforce Pricing Setup.
Turn on Activate Price Waterfall for API Responses and Price Waterfall Persistence.
Under Salesforce Pricing, select Advanced Price Log Settings.
Turn on advanced logs for the elements that you want to debug, such as Attribute-Based Pricing Element, Derived Pricing Element, Price Propagation Element, and Pricing Promotion Element.
To view the logs, use the Pricing WaterfallAPI.
