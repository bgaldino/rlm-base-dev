---
article_id: ind.collections_create_object_field_aliases.htm
title: Create Object Field Aliases for Collection Plan Fields
source_url: https://help.salesforce.com/s/articleView?id=ind.collections_create_object_field_aliases.htm&type=5&release=264
release: 264
release_name: Winter '27
area: collections
parent_article: ind.collections_setup_interaction_outcome.htm
fetched_at: 2026-11-23
---

# Create Object Field Aliases for Collection Plan Fields

Create aliases for the CurrentDueAmount, Status, and DaysPastDue fields of the Collection Plan object. These fields are used in the prebuilt expression set, Determine Case Eligibility for Legal Proceedings, to verify if the case is eligible for legal proceedings. To use object fields as variables in expression sets, the fields must have field aliases defined.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: View product and edition availability.
USER PERMISSIONS NEEDED
To configure an object field alias:	

Rule Engine Designer

AND

Collections and Recovery Admin

In Setup, find and select Object and Field Aliases.
Click New.
Select Default as the user type.
In Create Field Aliases, select New Object Aliases.
Enter CollectionPlanToTest as the object alias name.
Make sure that you don't change the object alias name. The prebuilt expression set, Determine Case Eligibility for Legal Proceedings, uses this object and field aliases to determine if the case is eligible for legal proceedings. If you change the object alias name, make sure that you update the same in the expression set.
To create field aliases:
In Source Field Name, enter Collection Plan >.
Select CurrentDueAmount.
Enter a corresponding field alias name, and save the changes.
Repeat these steps to create aliases for the Status, and DaysPastDue fields.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.collections_create_object_field_aliases.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
