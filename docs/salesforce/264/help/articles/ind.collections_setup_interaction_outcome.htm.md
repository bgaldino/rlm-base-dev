---
article_id: ind.collections_setup_interaction_outcome.htm
title: Setup and Configuration for Capturing Customer Interaction Outcomes
source_url: https://help.salesforce.com/s/articleView?id=ind.collections_setup_interaction_outcome.htm&type=5&release=264
release: 264
release_name: Winter '27
area: collections
parent_article: ind.collections_setup.htm
fetched_at: 2026-11-23
---

# Setup and Configuration for Capturing Customer Interaction Outcomes

The prebuilt action, Capture Collections-Related Interaction, helps collections specialists to capture collections-related interactions and the next steps. For example, a collections specialist can use this action to record an interaction with a borrower after discussing ‌a disputed collection amount that requires investigation. They can also use the action to create a case, and case proceeding records. To set up this action and related flows, add picklist values for the relevant fields on the Collection Plan, Case, and Case Proceeding objects, create object field aliases, customize the prebuilt expression set, and configure field-level security.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: View product and edition availability.
Configure Picklist Values and Assign Field-Level Access
Add the picklist values for the various fields on the Collection Plan, Case, and Case Proceeding objects, and assign field-level access. Enable Business Rule Engine components.
Create Object Field Aliases for Collection Plan Fields
Create aliases for the CurrentDueAmount, Status, and DaysPastDue fields of the Collection Plan object. These fields are used in the prebuilt expression set, Determine Case Eligibility for Legal Proceedings, to verify if the case is eligible for legal proceedings. To use object fields as variables in expression sets, the fields must have field aliases defined.
Clone the Prebuilt Expression Set Template to Determine Legal Case Eligibility
The prebuilt expression set, Determine Case Eligibility for Legal Proceedings, uses the collection plan object fields, such as current due amount, days past due, and status to determine if a case is eligible for legal proceedings. Clone this expression set, and customize the new version based on your business needs.
Customize the Preconfigured Action Launcher Deployment and Enable Interaction Summaries
Edit the Collection Plan Processes deployment in Action Launcher to include the Capture Collections-Related Interaction quick action. Then, turn on Interaction Summary to view customer interactions on a collection plan record page.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.collections_setup_interaction_outcome.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
