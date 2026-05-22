---
article_id: ind.product_configurator_convert_bre_rules_to_cml.htm
title: Convert Rules from Business Rules Engine into CML Code
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_convert_bre_rules_to_cml.htm&type=5&release=262
release: 262
release_name: Summer '26
area: configurator
fetched_at: 2026-05-12
---

# Convert Rules from Business Rules Engine into CML Code

Export rules from Business Rules Engine, then convert them to CML code and import them into Constraint Rules Engine.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license
USER PERMISSIONS NEEDED
To import rules to Constraint Rules Engine:	Product Configuration Constraints Designer permission set

To migrate rules from Business Rules Engine (BRE) to CML, first add all relevant products with related classes, attributes, product components, product component groups, and bundle definitions to Product Catalog Management (PCM).

Go to https://www.npmjs.com/ and install the plugins @salesforce/plugin-data and @salesforce/plugin-bre-to-cml. For detailed instructions on importing rules to Constraint Rules Engine, see information in plugin-bre-to-cml.
To export rules from Business Rules Engine and save as a JSON file, in plugin-data, use the sf data export bulk command in the source org, as in this example. The ConfigurationRuleDefinition field contains the JSON representation of the BRE rule. To confirm that a rule exports successfully, in the WHERE clause add a search on Name = "myBreRuleToTest".
sf sf data export bulk -o srcOrg --query "SELECT ApiName, ConfigurationRuleDefinition,Description, EffectiveFromDate, EffectiveToDate, Id, IsDeleted, Name, ProcessScope, RuleSubType, RuleType, Sequence, Status FROM ProductConfigurationRule WHERE RuleType = 'Configurator' AND Status = 'Active'" --output-file ./data/ProductConfigurationRules_Active.json --result-format json --wait 10 --all-rows
To convert the rules from the JSON file to CML code and save the code as a pair of CML and association files, in plugin-bre-to-cml, run the sf cml convert prod-cfg-rules command in the source org, as in this example. The value you pass as —cml-api is the API name for each generated CML constraint model. A 0-based index appends to that value with "_" as a separator. To make sure that the rules convert successfully, inspect the CML rules before you import them to the target org.
sf cml convert prod-cfg-rules --pcr-file data/ProductConfigurationRules_Active.json --cml-api CML_API --workspace-dir data --target-org srcOrg
To import the CML into the target org, run the import command for each CML rule that was generated during conversion. All classes, attributes, product components, product component groups, and bundle definitions must be present in the target org. You can select which CML rules to import, and import them in any order. If the conversion generates only one CML rule, import the rule for CML_API_0. See these examples.
sf cml import as-expression-set --cml-api CML_API_0 --context-definition PricingTransactionCD2 --workspace-dir data --target-org tgtOrg   sf cml import as-expression-set --cml-api CML_API_N --context-definition PricingTransactionCD2 --workspace-dir data --target-org tgtOrg
Activate and test each imported CML rule.

The CML code for the imported rules uses a similar structure as that used to import bundle products from PCM into CML Editor. For detailed instructions on importing rules to Constraint Rules Engine, see information in plugin-bre-to-cml.

To edit the imported CML rules, such as creating new types or adding annotations, use the CML Editor in Product Configurator. To avoid unexpected outcomes, don’t make changes directly in the CML code. If you edit the CML rules in the target org and import the rules again, the later import overwrites the earlier import.

These behaviors are different in CML than in Business Rules Engine:

In CML, conditional defaults for Set Default Attribute Value and Set Default Product aren’t supported.

In CML, auto-adding multiple instances of a product isn’t supported. For example, consider this rule: if product == A and quantity > 5, auto-add B. In the Business Rules Engine, if there are 2 line items of product A with quantity greater than 5, two instances of product B are added. In CML, only 1 instance of product B is added.

In CML, a message persists as long as a condition is true.
