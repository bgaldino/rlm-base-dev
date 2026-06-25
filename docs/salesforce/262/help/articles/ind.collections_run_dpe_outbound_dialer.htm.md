---
article_id: ind.collections_run_dpe_outbound_dialer.htm
title: Run Prebuilt Data Processing Engine Definition for Collections Outbound Dialer
source_url: https://help.salesforce.com/s/articleView?id=ind.collections_run_dpe_outbound_dialer.htm&type=5&release=262
release: 262
release_name: Summer '26
area: collections
parent_article: ind.collections_setup_outbound_dialer.htm
fetched_at: 2026-06-21
---

# Run Prebuilt Data Processing Engine Definition for Collections Outbound Dialer

Clone, customize, and run the prebuilt Data Processing Engine definition, Filter Collection Plans by Overdue Amount. After this definition is run successfully, use this definition to create an actionable list of delinquent collections.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: View product and edition availability.
USER PERMISSIONS NEEDED
To open the prebuilt Data Processing Engine definition:	

Customize Application permission

AND

Modify All Data permission

AND

Collections and Recovery Admin permission set


To run the prebuilt Data Processing Engine definition:	

Customize Application permission

AND

Modify All Data permission

AND

Collections and Recovery Admin permission set

AND

Data Pipelines Base User

By default, the prebuilt Data Processing Engine definition, Filter Collection Plans by Overdue Amount, creates a dataset of collection plans and their corresponding accounts where the total overdue amount is greater than 100. Customize this Data Processing Engine definition according to your business requirements.

From Setup, in the Quick Find box, find, and select Data Processing Engine.
Search for the prebuilt definition, Filter Collection Plans by Overdue Amount, and click Save As.
Enter the name, API name, and save the changes.
Click the action menu of the cloned definition, and select Activate.
Open the active definition, click Run Definition, and then click Next.
Select one or more debug modes, and click Run Definition.
For information about the debug modes, see Troubleshoot Data Processing Engine Jobs with Debug Modes.
To monitor if the definition run succeeded or failed, go to Monitor Workflow Services, and view the status.
