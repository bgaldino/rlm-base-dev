---
article_id: ind.collections_customize_flow_case_closure.htm
title: Customize the Prebuilt Flow to Close Collection Plan and Associated Cases
source_url: https://help.salesforce.com/s/articleView?id=ind.collections_customize_flow_case_closure.htm&type=5&release=264
release: 264
release_name: Winter '27
area: collections
parent_article: ind.collections_configure_case_management.htm
fetched_at: 2026-11-23
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

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.collections_customize_flow_case_closure.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
