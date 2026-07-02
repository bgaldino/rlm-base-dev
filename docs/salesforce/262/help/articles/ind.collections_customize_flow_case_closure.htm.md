---
article_id: ind.collections_customize_flow_case_closure.htm
title: Customize the Prebuilt Flow to Close Collection Plan and Associated Cases
source_url: https://help.salesforce.com/s/articleView?id=ind.collections_customize_flow_case_closure.htm&type=5&release=262
release: 262
release_name: Summer '26
area: collections
parent_article: ind.collections_configure_case_management.htm
fetched_at: 2026-06-21
---

# Customize the Prebuilt Flow to Close Collection Plan and Associated Cases

This flow automatically closes a collection plan and all its associated cases based on predefined conditions.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: View product and edition availability.
USER PERMISSIONS NEEDED
To customize the prebuilt flow for case closure:	

Collections and Recovery Admin permission set

AND

Customize Application permission

The prebuilt flow changes the status of a collection plan and its related cases to closed, and updates the collection plan’s closed date. The flow is auto-triggered when any of these conditions are met.

The current due amount for a collection plan is zero and the status isn’t closed.
The current due amount is less than 10 and the days past due is zero, and the status isn’t closed.
From Setup, in the Quick Find box, enter Flows, and then select Flows.
Click Close Collection Plan and Associated Cases.
Click Save as New Version.
NOTE If you plan to clone the flow, make sure that you don't change the API name.
Customize the flow according to your business requirements.
Save your changes and activate the flow.
