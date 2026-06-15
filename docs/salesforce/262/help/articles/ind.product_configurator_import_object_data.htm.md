---
article_id: ind.product_configurator_import_object_data.htm
title: Import Data from Salesforce Objects to Use in Constraint Models
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_import_object_data.htm&type=5&release=262
release: 262
release_name: Summer '26
area: configurator
fetched_at: 2026-05-12
---

# Import Data from Salesforce Objects to Use in Constraint Models

Import data from a standard or custom Salesforce object to use in a table constraint in a constraint model. The imported data populates the columns and rows in the table constraint in CML, and saves you the step of manually entering the data.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license
USER PERMISSIONS NEEDED
To import object data:	Product Configuration Constraints Designer permission set

Only the first 10,000 records with a maximum of 10 custom fields from the Salesforce object are imported.

In Setup, enter Permission Sets in Quick Find and select Permission Sets.
Select the Constraint Rules Engine Licenseless permission set. If the Constraint Rules Engine Licenseless permission set for the Platform Integration User isn't available in your org, contact Salesforce Customer Support.
In the Apps section of the setup page for Constraint Rules Engine Licenseless permission set, select Object Settings.
Locate and select the object whose data you want to import to a table constraint.
On the Object Settings page for the object, select Edit. Enable Read, Create, Edit, Delete, View All Records, and View All Fields permissions, then save your changes.
To confirm that the permissions are enabled, open Object Manager and select the object whose data you want to import.
Select Object Access. On the Permission Sets tab, confirm that the Constraint Rules Engine Licenseless permission set is listed, with Read, Create, Edit, and Delete permissions enabled.
To load the imported data into a constraint, in CML Editor, write an expression in the constraint model code. Use the SalesforceTable keyword and include the table name and column names.
EXAMPLE

In this example, data is imported to a table with four columns. The suffix __c indicates that the data is from a Salesforce custom object.

constraint(table(attr1, attr2, attr3, attr4, SalesforceTable("tablename__c","column1name__c,column2name__c,column3name__c,column4name__c")));

NOTE If the table data is deployed when the constraint model is activated, and you add records to the table after constraint model activation, to fetch the new table data at runtime you must deactivate and reactivate the constraint model.
