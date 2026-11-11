---
article_id: ind.sf_contracts_turn_on_context_service_for_salesforce_contracts.htm
title: Enable Context Service for Salesforce Contracts
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_turn_on_context_service_for_salesforce_contracts.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_configure_context_services_to_create_and_update_contracts.htm
fetched_at: 2026-10-13
---

# Enable Context Service for Salesforce Contracts

Turn on Context Service for Salesforce Contracts to switch the create and update contract APIs from the XML field mapping framework to the Context Service framework.

Prerequisites:

Turn on Context Service.

Turn on Salesforce Contracts.

The org must have the Salesforce Contracts permission set license. It includes the Context Service user permissions.

The org must have the Context Service Access platform license provisioned.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, Professional, and Developer Editions
USER PERMISSIONS NEEDED	 
To enable Context Service for Salesforce Contracts:	

CLM Admin User

From Setup, in the Quick Find box, enter Contract Lifecycle Management, and then select General Settings.
Turn on Context Service for Salesforce Contracts.
This loads the out-of-the-box context definition named ContractsContextDefinition for Salesforce Contracts under Context Definitions. The Context Use Case Mapping setup page under Contract Lifecycle Management becomes available. The context use case mapping includes the corresponding seeded hydration and persistence mapping data for Opportunity, Order, and Quote (if your org has Quote enabled).

See Also

Personas and Permission Set Licenses for Salesforce Contracts

Permissions for Context Service Users

Turn On Context Service

Enable Salesforce Contracts
