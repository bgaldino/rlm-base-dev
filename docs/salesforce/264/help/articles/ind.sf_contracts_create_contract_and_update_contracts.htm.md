---
article_id: ind.sf_contracts_create_contract_and_update_contracts.htm
title: Configure Contract Creation and Updates for Salesforce Contracts
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_create_contract_and_update_contracts.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_system_administration_for_salesforce_contracts.htm
fetched_at: 2026-10-13
---

# Configure Contract Creation and Updates for Salesforce Contracts

Set up the field mappings that control how contract records are created and updated from source objects such as opportunities, orders, quotes, and custom objects.

IMPORTANT XML field mapping has been deprecated. Use Context Service to configure field mappings.

The Create Contract and Update Contracts actions are available by default on opportunity, order, and quote objects. To enable these actions on other standard or custom objects, you must configure Context Service mappings and set up the action buttons for those objects.

Context Service maps data between the source object and the contract object. When a user creates or updates a contract, the application automatically populates contract fields based on these mappings. You can configure standard context definitions for common objects or create custom definitions for other use cases.

Configure Context Service to Create and Update Contracts
Context Service provides a mapping interface for creating and updating contracts from standard and custom objects. Context Service replaces the XML field mapping framework with a configurable, point-and-click approach.
Limitations for Create Contract and Update Contracts APIs
Current limitations for the create and update APIs that use Context Service.
