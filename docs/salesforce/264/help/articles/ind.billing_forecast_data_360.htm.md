---
article_id: ind.billing_forecast_data_360.htm
title: Add the Billing Forecast to Data 360
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_forecast_data_360.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_forecast.htm
fetched_at: 2026-09-04
---

# Add the Billing Forecast to Data 360

Complete this setup if you want to review forecast data in the Billing Forecast Console, which uses Tableau Next.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER PERMISSIONS NEEDED
To update a Data 360 data bundle:	Data Cloud Architect permission set

Before you start, turn on Billing Forecast. Data 360 must be enabled and connected. See Build your Data Cloud Connection.

If you already use Billing Analytics, add the Billing Forecast object to the Advanced Billing Bundle in Data 360, then update the bundle and redeploy Billing Analytics.

If you haven’t installed Billing Analytics yet, deploy the Common Billing Bundle and the Advanced Billing Bundle, then install Billing Analytics. See Deploy the Revenue Management Intelligence Data Kit and Install Revenue Management Intelligence Apps.

From the App Launcher, find and select Data 360.
Click the Data Streams tab.
Open the Salesforce CRM data stream for the Advanced Billing Bundle.
On the objects page, select Billing Forecast.
Click Update.

After the update completes, from the App Launcher or the Billing app navigation bar, find and select Billing Forecast Console.
