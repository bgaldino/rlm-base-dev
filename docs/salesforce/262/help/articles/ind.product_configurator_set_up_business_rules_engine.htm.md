---
article_id: ind.product_configurator_set_up_business_rules_engine.htm
title: Set Up Business Rules Engine for Product Configurator
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_set_up_business_rules_engine.htm&type=5&release=262
release: 262
release_name: Summer '26
area: configurator
fetched_at: 2026-05-12
---

# Set Up Business Rules Engine for Product Configurator

Before you define product configuration rules by using Business Rules Engine, set up Business Rules Engine for Product Configurator.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license
USER PERMISSIONS NEEDED
To set up Business Rules Engine for Product Configurator:	Product Configuration Rules Designer permission set
Create a Rule Library

Rule creation requires a rule library to store and run rules in Business Rules Engine.

Before you create a rule library, select a default pricing procedure on the Revenue Settings page. This pricing procedure uses a context definition that's extended from the SalesTransactionContext context definition.

From the App Launcher, find and select Rule Libraries.
Click New.
Enter a name and API name for the rule library.
Select Configurator as the usage type.
Enter the developer name of the extended SalesTransactionContext context definition that's configured for your default pricing procedure on the Revenue Settings page.
Save your changes.
Go to the Rule Library Versions related list and open the version that you want to activate.
From the action dropdown, click Activate.
Refresh the page.
The rule library version is now activated.
NOTE If you change the extended SalesTransactionContext context definition used by your default pricing procedure, create a new rule library with the latest context definition, or create a rule library version.
Enable Configuration Rules with Business Rules Engine

Grant users the access to set up product configuration rules by using Business Rules Engine.

From Setup, in the Quick find box, enter Revenue Settings, and then select Revenue Settings.
Turn on Set Up Configuration Rules with Business Rules Engine.
Create Transaction Processing Type Records for Business Rules Engine

Create a transaction processing type and specify StandardConfigurator as the rule engine.

See Define Rules Engine with Transaction Processing Types.

This completes the setup of Business Rules Engine for Product Configurator. To learn about creating product configuration rules by using Business Rules Engine, see Define Configuration Rules with Business Rules Engine.

This completes the setup for Product Configurator. To proceed with the rest of the Revenue Cloud setup, see Set Up Agentforce Revenue Management.
