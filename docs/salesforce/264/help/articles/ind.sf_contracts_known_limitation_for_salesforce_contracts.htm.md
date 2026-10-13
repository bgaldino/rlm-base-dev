---
article_id: ind.sf_contracts_known_limitation_for_salesforce_contracts.htm
title: General Considerations for Salesforce Contracts
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_known_limitation_for_salesforce_contracts.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_known_limitations.htm
fetched_at: 2026-10-13
---

# General Considerations for Salesforce Contracts

Here's a list of known limitations for Salesforce Contracts.

Salesforce doesn't recommend using Salesforce Contracts and Vlocity Contract Lifecycle Management applications in the same org. Doing so, can negatively impact contract authoring and contract lifecycle management functionalities.

Contract document templates that use custom classes aren't supported .

Salesforce Contracts UI isn't supported in the Salesforce mobile app.

Customers who upgrade from Spring ’24 to Summer ’24 face an issue where the document viewer doesn’t load the generated document. To resolve this, you must set the field-level security for the Document Type field to view the generated document. See Set Field-Level Security for Document Type in Salesforce Contracts.

In Restriction Rules and Scoping Rules, under Record Criteria, picklist fields behave in this way:
Community and Portal users: For Contract object, multi-select picklist values can be selected to support Salesforce Contracts use cases where records are viewed but not edited. This behavior ensures that Contract Search and related features work consistently without introducing errors when editing records. Multi-select can also be configured for objects such as Opportunity, Quote, or custom objects, however, only a single picklist value should be selected in these cases. See Restriction Rule Considerations and Scoping Rule Considerations.
All other user types: Multi-select picklists can be configured for any object. However, multi-select criteria isn't supported, so only a single picklist value should be selected.
