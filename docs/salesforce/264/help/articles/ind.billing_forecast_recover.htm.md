---
article_id: ind.billing_forecast_recover.htm
title: Recover Billing Schedules
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_forecast_recover.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_forecast.htm
fetched_at: 2026-09-04
---

# Recover Billing Schedules

Update Forecast Status from Processing to Pending Forecast or Forecasted so stuck billing schedules can be included in the next forecast run.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER PERMISSIONS NEEDED
To recover billing schedules from a failed forecast run:	Recover Forecast Billing Schedules user permission
NOTE Assign the Recover Forecast Billing Schedules user permission in a permission set. It isn’t included in the Billing Admin permission set. See Manage Permission Set Assignments.

When a billing forecast run fails partway through, some billing schedules can remain with Forecast Status set to Processing. A user with the Recover Forecast Billing Schedules user permission can update Forecast Status from Processing to either:

Pending Forecast: The schedule is queued for the next forecast run.
Forecasted: The schedule is marked as already reflecting current forecast data, without running a forecast on it again.

Performing this action changes the forecast status only. It doesn’t change the billing schedule Status used for invoicing.

To recover billing schedules:

Open the billing schedule that has Forecast Status set to Processing.
Change Forecast Status to Pending Forecast or Forecasted.
IMPORTANT Use this recovery step only for billing schedules that remain in progress after a failed or interrupted forecast run. Recover these schedules before starting a new forecast run. Running both at the same time can result in conflicting forecast statuses.

After you recover the schedules, run forecast again if you need updated Billing Forecast records. For a Once run that refreshes matching schedules, select Recalculate All Forecast Lines. See Schedule Billing Forecast Runs.
