---
article_id: ind.product_catalog_manage_qual_rule_components.htm
title: Manage Qualification Rule Components
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_manage_qual_rule_components.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pcm
parent_article: ind.product_catalog_qualification_rules.htm
fetched_at: 2026-09-04
---

# Manage Qualification Rule Components

To fine-tune your qualification rules, modify or deactivate its components.

REQUIRED EDITIONS
View supported products and editions.
SEE ALSO
Simulate and Active a Qualification Rule Procedure
Deactivate a Qualification Rule Procedure Version

You can’t edit active rule procedures. To edit a rule procedure, first deactivate the version.

REQUIRED EDITIONS
USER PERMISSIONS
NEEDED
To deactivate a qualification rule procedure:	Manage Product Catalog
To use a decision table:	Rules Engine Runtime
To create a context definition:	Context Service Admin
From the Product Catalog Management app’s home page, click Qualification Rules Procedures.
From the Qualification Procedures list view, click a qualification.
On the Qualification Procedures details page, click the qualification procedure under Qualification Procedure Versions.
On the expression set builder page, click Deactivate.
You can now edit the qualification rule procedure. After you save your changes, activate the rule procedure.
Edit a Qualification Rule Procedure

Edit a qualification rule procedure, or add new fields in the associated decision table and context definition.

REQUIRED EDITIONS
USER PERMISSIONS
NEEDED
To create a qualification rule procedure:	Manage Product Catalog
To use a decision table:	Rules Engine Runtime
To create a context definition:	Context Service Admin
Add Custom Fields to the qualification rule objects as necessary.
Modify or add nodes and attributes in an active context definition.
Deactivate the qualification and pricing procedures that are using the context definition.
Deactivate the context definition.
Edit the nodes and attributes.
Activate the context definition.
To add nodes and attributes to a context definition, edit the context definition.
Deactivate the decision table, update the decision table to use the new fields, and then activate the decision table.
To create a new version of the qualification rule procedure, update the qualification rule procedure and add mappings to the new fields.
Simulate the updated qualification procedure version, and then activate it if it meets your requirements.
Deactivate a Decision Table in Revenue Management

You can’t edit active decision tables. Deactivate a decision table, add new rules or modify existing rules, and then activate the decision table. The changes don't take effect until you deactivate and activate the decision table.

REQUIRED EDITIONS
USER PERMISSIONS
NEEDED
To deactivate the decision table:	

Manage Product Catalog

AND

Rules Engine Designer

AND

Context Service Runtime


To use a decision table:	Rules Engine Runtime
From the Product Catalog Management app’s home page, click Qualification Rules.
From the Qualification Decision Tables list view page, click the decision table that you want to deactivate.
Click Deactivate.
You can now edit the decision table to add new qualification rules, or delete or edit existing qualification rules. After you save your changes, activate the decision table. When you activate the decision table, the changes to the rules are applied to the objects, and the decision table shows the new rules.
