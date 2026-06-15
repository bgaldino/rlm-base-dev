---
article_id: ind.product_catalog_create_decision_table_that_uses_custom_evaluation_object.htm
title: Create a Decision Table That Uses a Custom Evaluation Object
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_create_decision_table_that_uses_custom_evaluation_object.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Create a Decision Table That Uses a Custom Evaluation Object

If you use a custom object to store the evaluation criteria, create a decision table without using the templates.

REQUIRED EDITIONS
View supported products and editions.
USER PERMISSIONS NEEDED
To create a qualification rule:	Manage Product Catalog
To use a decision table:	Rules Engine Runtime

Before you create a decision table that uses a custom evaluation object, ensure that the object has certain mandatory fields. You use the mandatory fields to populate the rule criteria and create decision tables. You also use the mandatory fields in the qualification rule procedure. Based on the qualification rule type, the required mandatory fields are:

Product Qualification: ProductId of type FOREIGNKEY(Product2) and IsQualified of type BOOLEAN.
Product Disqualification: ProductId of type FOREIGNKEY(Product2) and IsDisqualified of type BOOLEAN.
Product Category Qualification: CategoryId of type FOREIGNKEY(Category) and IsQualified of type BOOLEAN
Product Category Disqualification: CategoryId of type FOREIGNKEY(Category) and IsDisqualified of type BOOLEAN
From the Product Catalog Management app’s home page, click Qualification Rules.
From the Qualification Decision Tables page, click New.
The Basic Details page appears.
On the Basic Details page:
Enter a name, API name, and description.
TIP Add the purpose of the decision table to the decision table name to specify whether the decision table is meant for qualification or disqualification. For example, if you’re creating a qualification decision table for furniture, name the decision table FurnitureQualify.
Select an application usage type.
To create a decision table for product qualification or disqualification, select Product Qualification. To create a decision table for product category qualification or disqualification, select Product Category Qualification.
Based on the number of records in your decision table, select a decision table type.
If the number of records in the decision table is less than 100,000, select

Standard

. If the number of records in the decision table exceeds 100,000, select

Advanced

.
Click Save & Next.
The Conditions & Results page appears.
Select a source object.
Skip the Related Objects field because rules are defined on only the source object.
To narrow down rows from the source object, add filters.
Click Source Filter.
To add a filter, click Add Filter, and then select a source object field, operator, and a value.
If you add more than one filter, use the Filter Logic field to specify the logic by using AND or OR.
To use the decision table for product qualification or disqualification, add the ProductId field with Equals as the operator. To use the decision table for product category qualification or disqualification, add CategoryId with Equals as the operator. In addition, add other fields that you want to use as input. In the Conditions section, add the fields that you want to use as input. To add a field as input:
Click Add Condition.
For Source Object Field, select the field name.
Select an operator.
The operator determines how a particular field from the business rule evaluates a record or a user-specified value.
If necessary, set the condition as optional.
To know about the permissible number of input and output fields, see Considerations for Creating Decision Tables.
Select a condition type.
When you use custom logic, the Number column indicates the sequence number of the fields. For example, if you have three input fields and you want to use custom logic that provides output when fields 1 and 2 match or when field 3 matches, specify the condition as: (1 AND 2) OR 3.
To use the decision table for product or category qualification, add the IsQualified field. To use the decision table for product or category disqualification, add the IsDisqualified field. In addition, add other fields that you want to use as the output. In the Results section, add all the fields that you want in the decision table output. To add a field as output:
Click Add Results.
In the Source Object Field, select the field name.
 Click Save & Next.
The Behaviours page appears.
In the Filter Result By field, select First Match.
If necessary, select an input or output field by which records must be sorted and then select the sort order.
To consider columns with null values during lookup, select Consider Null Values for Lookup.
See How Null Values Work in Decision Tables.
NOTE The Consider Null Values for Lookup option is available only when the decision table type is standard.
Click Save & Next.
The Preview & Save page appears.
On the Preview & Save page, review the information including the conditions and preview records, and then click Finish.
NOTE If you used custom fields in decision tables, then use change sets or package manager to first deploy the custom fields to your destination org before you deploy the decision tables.
