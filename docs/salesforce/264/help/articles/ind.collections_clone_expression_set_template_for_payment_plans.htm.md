---
article_id: ind.collections_clone_expression_set_template_for_payment_plans.htm
title: Create an Expression Set from a Prebuilt Expression Set Template for Payment Plan Mapping
source_url: https://help.salesforce.com/s/articleView?id=ind.collections_clone_expression_set_template_for_payment_plans.htm&type=5&release=264
release: 264
release_name: Winter '27
area: collections
parent_article: ind.collections_setup_payment_plans_for_financial_hardships.htm
fetched_at: 2026-11-23
---

# Create an Expression Set from a Prebuilt Expression Set Template for Payment Plan Mapping

Collections and Recovery includes a prebuilt expression set template, Payment Plan Mapping Expression Set. Create an expression set from this template.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: View product and edition availability.
USER PERMISSIONS NEEDED
To view an expression set template:	Rule Engine Designer
To save an expression set template as an expression set or an expression set version:	Rule Engine Designer

The prebuilt expression set template references the decision table that contains the financial account type to payment plan mapping details. When you create an expression set from this template, make sure that you retain the same name. The prebuilt Omniscript, CollectionsCreatePaymentPlansForCustomers references this expression set template.

Create an expression set from the prebuilt, read-only expression set template, Payment Plans for Collections.
Make sure that you retain the name of the expression set as is.
Activate the expression set.
If you have renamed the decision table from its default name, FAPaymentPlanMapping, to something else, follow these steps to update the lookup table reference in the expression set that you created earlier.
From the App Launcher, find and select Business Rules Engine.
From the app navigation menu, select Expression Set Templates.
Open the expression set that you created earlier.
Expand the FAPaymentPlanMapping lookup table.
Specify the changed lookup table name.
Save your changes and activate the expression set.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.collections_clone_expression_set_template_for_payment_plans.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
