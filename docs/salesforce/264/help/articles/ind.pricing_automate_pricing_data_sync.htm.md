---
article_id: ind.pricing_automate_pricing_data_sync.htm
title: Automate Pricing Data Sync with a Scheduled Flow
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_automate_pricing_data_sync.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pricing
parent_article: ind.pricing_sync_pricing_data.htm
fetched_at: 2026-09-07
---

# Automate Pricing Data Sync with a Scheduled Flow

Create a scheduled flow that refreshes your pricing decision tables on a regular cadence so that Agentforce Revenue Management always uses current pricing data without requiring a manual sync.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Growth license or the Revenue Cloud Advanced license.
USER PERMISSIONS
NEEDED
To create and activate flows:	Manage Flow
To enable data sync:	Salesforce Pricing Design Time
To ensure complete sync of decision tables:	Assetize Order

You can sync pricing data manually at any time by using the Sync Pricing Data button in Salesforce Pricing Setup. Optionally, you can also automate this process with a scheduled flow that calls the Refresh Decision Table action on a regular cadence. This ensures that decision tables stay current — for example, with a nightly refresh — without relying on an admin to run the sync after every pricing change.

Before you set up a scheduled sync, review these considerations.

Schedule refreshes during off-peak hours
Decision table refreshes consume processing resources. For orgs with large pricing catalogs (thousands of price book entries or complex tier structures), schedule the flow to run during off-peak hours when few users are actively creating quotes or orders. This minimizes the risk of pricing calculations reading stale data mid-refresh.
Pause automation during bulk data loads
Deactivate this flow before performing large data imports (for example, bulk product or price book entry loads). A refresh triggered mid-import can capture an incomplete data state. Run a manual sync after the import completes, then reactivate the flow.
Set up error notifications
If a Refresh Decision Table action fails — for example, because a decision table was deactivated or the hourly limit was reached — the flow fails without alerting anyone by default. In Flow Builder, add a fault path to the action or enable flow error email notifications in Setup so that admins are alerted to failures.
Verify successful refreshes
After activating the flow, confirm that decision tables are refreshing as expected. From Setup, navigate to the Decision Tables page and check the Last Refreshed timestamp. You can also review flow execution history in Setup under Process Automation.
Set Up Automated Pricing Data Sync
From Setup, in the Quick Find box, enter Flows, and then select Flows.
Click New Flow.
Under Scheduled Automations, select Schedule-Triggered Flow and click Create.
Click Set Schedule on the Start element and configure the schedule.
Set a start date, start time, and select Daily or Weekly from the Frequency dropdown. For most orgs, a daily frequency running during off-peak hours (for example, 2:00 AM) is sufficient. If your org serves users in multiple time zones, choose a window when the fewest users are actively generating quotes or orders. You can skip the optional Choose Object step.
Click the + icon between the Start and End elements, and select Action.
In the Search Actions field, search for and select Refresh Decision Table.
Enter a label for the action, and in the Decision Table API Name input field, enter the API name of the decision table to refresh.
To refresh multiple decision tables, add a separate Refresh Decision Table action for each one.
Save the flow and click Activate.

The flow runs at the scheduled time and refreshes the specified decision tables. Pricing calculations in Agentforce Revenue Management then use the updated data for all subsequent transactions.
