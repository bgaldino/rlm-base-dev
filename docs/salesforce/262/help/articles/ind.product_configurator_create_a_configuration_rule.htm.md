---
article_id: ind.product_configurator_create_a_configuration_rule.htm
title: Manage Configuration Rules with Business Rules Engine
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_create_a_configuration_rule.htm&type=5&release=262
release: 262
release_name: Summer '26
area: configurator
fetched_at: 2026-05-12
---

# Manage Configuration Rules with Business Rules Engine

Reduce configuration errors, and easily manage product validation and compatibility by using configuration rules.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license
USER PERMISSIONS
NEEDED
To manage configuration rules:	Manage Configurator with Business Rules Engine

Before you create configuration rules, make sure that your Salesforce admin has set up Business Rules Engine for Product Configurator.

Keep these considerations in mind when defining configuration rules.

If you deactivate a child product, remove all the references to the product in configuration rules to prevent errors.
If you have an active rule on a product attribute or product bundle, and modify the attribute or bundle in the product catalog, the Product Configurator fails if the rule and the catalog are out of sync. To correct this error, deactivate the rule, update it to be consistent with product catalog data, and then activate the rule.
If you create a configuration rule on a product bundle to run on a product, such as adding the product to the bundle, the configuration rule fails if the product has default attribute values that prevent the user from configuring the product.
For configuration rules created before Summer '25 and containing a condition with the NetUnitPrice sub-condition, the name of the NetUnitPrice sub-condition appears as ItemDetailNetUnitPrice from Summer '25.
Create a Rule

Create rules to validate configurations of products, product bundles, or transactions.

From the home page of the Product Catalog Management app, click Product Configuration Rules.
Click New.
In the Rules Details page, specify these details:
Enter a name for the configuration rule.
The API name automatically populates.
Enter a description for the configuration rule.
Enter the rule duration.
Select the rule status.
To determine when this rule runs, enter the rule sequence.
When multiple rules trigger together, rules with lower numbers run first.
Click Next.
In the Rule Criteria page, specify these details:
Select the rule scope. See Rule Scope.
Specify the conditions to run the rule.
The resource for each condition is either a product or product classification. Each rule supports up to three conditions and eight sub-conditions. Currently, the system supports only the AND logical operand between conditions. So, the rule runs only when all the conditions are met.
Specify the action to take when the conditions are met. See Actions.
Each rule supports up to three actions. You can add a message for each action. The type of message depends on the type of action.
Save your changes.
Edit a Rule

To add, update, or delete rule conditions and actions, modify the rule details or the rule criteria.

From the home page of the Product Catalog Management app, click Product Configuration Rules.
From the quick action menu next to the configuration rule that you want to edit, select Edit Rule.
On the Rule Details page, update the necessary details.
Click Next.
On the Rule Criteria page, update the necessary details.
Save your changes.
Delete a Rule

Delete a configuration rule when you no longer need it.

From the home page of the Product Catalog Management app, click Product Configuration Rules.
From the quick action menu next to the configuration rule that you want to delete, select Delete, and confirm your action.

After you create configuration rules, make sure that you validate them to maintain rule integrity.
