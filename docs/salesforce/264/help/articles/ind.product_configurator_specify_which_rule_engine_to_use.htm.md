---
article_id: ind.product_configurator_specify_which_rule_engine_to_use.htm
title: Define Rules Engine with Transaction Processing Types
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_specify_which_rule_engine_to_use.htm&type=5&release=264
release: 264
release_name: Winter '27
area: configurator
parent_article: ind.product_configurator_setup.htm
fetched_at: 2026-09-04
---

# Define Rules Engine with Transaction Processing Types

Create Transaction Processing Type records to define the rules engine that you want to use to process configuration rules. Then, specify the default transaction processing type on the Revenue Settings page.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Growth license or the Revenue Cloud Advanced license
NOTE

Constraint Rules Engine services aren’t available in Government Cloud or in orgs within the EU Operating Zone (OZ). For more information, contact your Salesforce account executive.

Configure the transaction processing type with the appropriate RuleEngine value:

To use Business Rules Engine, specify StandardConfigurator as the RuleEngine value.
To use Constraint Rules Engine, specify AdvancedConfigurator as the RuleEngine value.

Sales reps can’t see the fields in Transaction Processing Type records. If necessary, append the name of the rules engine to the Transaction Processing Type record name.

Set the default transaction processing type only if you plan to use Business Rules Engine. When you enable Constraint Rules Engine, AdvancedConfigurator automatically becomes the default rules engine.

When users create quotes and orders, the Transaction Type field is automatically populated with the default Transaction Processing Type record. The Transaction Type field on a quote or order determines the rule engines that's used to validate product configurations, and to execute configuration rules and constraints.

ENABLED FEATURE	RULES ENGINE USED	CONDITIONS
Only Constraint Rules Engine is enabled	Constraint Rules Engine	Configuration rules are run by using Constraint Rules Engine.
Only Business Rules Engine is enabled	Business Rules Engine	StandardConfigurator is specified as the rule engine in the associated Transaction Processing Type record.
Only Business Rules Engine is enabled	No rules engine used	There's no Transaction Type value on quotes and orders, or no Rule Engine value on the Transaction Processing Type record.
Both rules engines are enabled	Business Rules Engine	StandardConfigurator is specified as the rule engine in the associated Transaction Processing Type record.
Both rules engines are enabled	Constraint Rules Engine	StandardConfigurator is not specified as the rule engine in the associated Transaction Processing Type record.
