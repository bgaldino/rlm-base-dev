---
article_id: ind.product_catalog_qualification_rules.htm
title: Manage Qualification Rules for Products in Agentforce Revenue Management
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_qualification_rules.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Manage Qualification Rules for Products in Agentforce Revenue Management

Use qualification rules to define the customer eligibility and availability for products, or product categories. Configure qualification rules using criteria such as location, account attributes, purchase history, and more.

REQUIRED EDITIONS
View supported products and editions.

By default every product or product category is qualified. With qualification rules, you can specify the conditions under which products and categories remain qualified or become disqualified.

Sales reps can select qualified products during the quote and order process through the Browse Catalogs button. Disqualified products don't appear in Browse Catalogs and can't be added to quotes or orders.

Rule Types

In Product Catalog Management, you can define qualification rules in two ways:

Qualification
The product or product category is qualified when the product or product category matches specified qualification criteria. For example, a premium dining table is available to customer accounts with enough rewards points.
Disqualification
The product or product category is disqualified when the product or product category matches specified disqualification criteria. For example, a newly launched product category is available to customer accounts in all states except New York. In this example, it’s easier to control availability with a disqualification rule. The product is disqualified when the customer account's state is New York.
Qualification Rule Components

To use qualification rules, you must define these components:

Objects
Qualification rule criteria are stored in Salesforce objects. You can either build your own custom objects, or choose to extend the out-of-the-box qualification objects that come with Product Catalog Management.
Context Definitions
Use a context definition to pass product or product category data to the qualification procedure. The qualification procedure then evaluates the qualification of products or product categories, and returns the qualification or disqualification results to the context definition.
Decision Tables
Decision tables contain the selected Salesforce object criteria fields through which the rules qualify or disqualify products and product categories. Decision tables facilitate data lookup and criteria matching.
Qualification Rule Procedures
A qualification rule procedure consists of a series of steps connected in a logical flow that evaluate product or product category qualification and disqualification based on criteria defined in the related decision table.
Qualification Rule Considerations
Products and categories that don’t have any qualification or disqualification rules are qualified by default.
Qualification rules take precedence over disqualification rules. For example, when a category is qualified based on a category qualification rule, the category remains qualified even if it’s disqualified based on other rules.
If a product category is qualified based on a qualification criteria, then the user sees all the products within the qualified category, provided the products don’t have specific disqualification rules defined.
Build a Qualification Rule

Qualification rules can be a complex topic to understand. Follow these steps in sequence to build a functional qualification rule.

Create Qualification Rule Criteria
Create criteria using field data on your chosen Salesforce object that you want to use for qualification rules. The object can be one that you create, or one of the included qualification or disqualification objects.
Configure a Context Definition for Qualification Rules
For qualification rules, context definitions pass product or product catagory data to your qualification rule procedures. The qualification procedure then evaluates the qualification of products or product categories and returns the qualification or disqualification results back to the context definition.
Decision Tables for Qualification Rules
A decision table contains the criteria used for qualification and disqualification of products and product categories. Create a decision table for every type of qualification and disqualification that you want to configure.
Create a Qualification Rule Procedure
A qualification rule procedure contains qualification procedure elements that evaluate the rules in a decision table. The procedure accepts a list of categories and products as input and returns the list of products and categories along with their qualification or disqualification information as output.
Simulate and Activate a Qualification Rule Procedure
Before you activate your qualification rule procedure, run simulations to test whether the rules you defined in the decision table are accurate and give you the desired output. If your rule procedure doesn’t work as expected, edit the values and simulate again. When you’re satisfied, activate the rule procedure version.
/apex/HTViewHelpDoc?id=ind.Chunk771702022.htm#product_catalog_manage_qual_rule_components

Explore a Qualification Rule Example
Qualification rules can be a complex topic to understand. Let's look at an example to see how the components come together to create a fully functional qualification rule.
