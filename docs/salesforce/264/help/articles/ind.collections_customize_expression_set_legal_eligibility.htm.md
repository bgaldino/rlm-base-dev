---
article_id: ind.collections_customize_expression_set_legal_eligibility.htm
title: Clone the Prebuilt Expression Set Template to Determine Legal Case Eligibility
source_url: https://help.salesforce.com/s/articleView?id=ind.collections_customize_expression_set_legal_eligibility.htm&type=5&release=264
release: 264
release_name: Winter '27
area: collections
parent_article: ind.collections_setup_interaction_outcome.htm
fetched_at: 2026-11-23
---

# Clone the Prebuilt Expression Set Template to Determine Legal Case Eligibility

The prebuilt expression set, Determine Case Eligibility for Legal Proceedings, uses the collection plan object fields, such as current due amount, days past due, and status to determine if a case is eligible for legal proceedings. Clone this expression set, and customize the new version based on your business needs.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: View product and edition availability.
USER PERMISSIONS NEEDED
To clone the expression set template:	

Actionable Event Orchestration Runtime

AND

Collections and Recovery Agent

Make sure that you have created object field aliases for collection plan fields.

When you clone the prebuilt expression set template, the steps from the template are copied to the first version of the cloned expression set by default.

From the App Launcher, find and select Business Rules Engine.
From the app navigation menu, select Expression Set Templates.
Click Determine Case Eligibility for Legal Proceedings.
From the Save As dropdown, select New Expression Set.
Don't change the expression set name. If you plan to change it, make sure that you update the new name in the prebuilt flow, Collections: Create Case and Related Case Proceeding Records. This flow uses the expression set to determine if the case is eligible for legal proceedings and whether to create case proceedings and participant records.
Save your changes.
To link the object field aliases that you created earlier, expand CollectionPlan Eligibility Condition.
In the Resource column, reference the object field aliases as shown in this example.
EXISTING RESOURCE NAME	OBJECT FIELD ALIAS NAME
Current Due Amount	CollectionPlanToTest.CollectionPlanCurrentAmountDue
Status	CollectionPlanToTest.CollectionPlanStatus
Days Past Due	CollectionPlanToTest.CollectionPlanDaysPastDue
Update the logical conditions based on your business needs.
Click , and select a start date and time.
Save your changes.
Click Activate.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.collections_customize_expression_set_legal_eligibility.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
