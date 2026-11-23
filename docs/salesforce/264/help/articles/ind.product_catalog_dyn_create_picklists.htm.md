---
article_id: ind.product_catalog_dyn_create_picklists.htm
title: Create Attribute Picklists
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_dyn_create_picklists.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pcm
parent_article: ind.product_catalog_picklists.htm
fetched_at: 2026-11-23
---

# Create Attribute Picklists

Follow these instructions to create an attribute picklist. You must create your picklists first before you create attributes of type picklist.

REQUIRED EDITIONS
USER PERMISSIONS NEEDED
To create picklists:	Manage Product Catalog
From the Product Catalog Management app’s home page, click Picklists.
On the Attribute Picklists list view page, click New.
In the New Attribute Picklist window, enter these values:
Enter a name and description for the picklist.
Select a data type.
The default data type is Boolean.
Select a status for the picklist.
You can use only active picklists for attributes.
NOTE Before you deactivate a picklist, ensure that it isn’t in use by any attribute of a product or an attribute of a product classification.
Save your changes.
Click the Related tab for the newly created picklist.
In the Attribute Picklist Values section, click New.
In the New Attribute Picklist Value window, enter these values:
Enter a name for the picklist value.
If necessary, enter an abbreviation for the picklist value.
Enter a unique code for the picklist value within the org.
Select a status for the picklist value.
You can use only active picklist values for attributes.
NOTE Before you deactivate a picklist value, ensure that it isn’t in use by any attribute of a product or an attribute of a product classification.
Select Default to make this picklist value the default value for the associated picklist. Only one value can be the default for a picklist.
Enter a display value. This picklist value is displayed at run time. Use this field when the display value is different from the actual value. For example, for the number value ‘5’, the display value is ‘Five’. The display value must be unique within a picklist.
Enter a value for the picklist item.
NOTE Ensure that you use a value that you haven’t used as a display value for this picklist.
Enter the sequence to determine the order in which this picklist value appears during the purchase.
Save your changes.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.product_catalog_dyn_create_picklists.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
