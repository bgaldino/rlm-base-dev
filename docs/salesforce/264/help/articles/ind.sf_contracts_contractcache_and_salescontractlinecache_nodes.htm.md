---
article_id: ind.sf_contracts_contractcache_and_salescontractlinecache_nodes.htm
title: ContractCache and SalesContractLineCache Nodes
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_contractcache_and_salescontractlinecache_nodes.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_context_definitions_to_create_and_update_contracts.htm
fetched_at: 2026-10-13
---

# ContractCache and SalesContractLineCache Nodes

Nodes are canonical objects containing the attributes mapped to real data by the consuming application. A structure is defined between the nodes to ensure that the right set of information is passed during each step of the process.

NODES	ATTRIBUTES	TYPE	DESCRIPTION


ContractCache

(parent node)

	Account	INPUT OUTPUT	

The input output type value is retrieved from the object. For example, Account and Description.

The account attribute is mandatory to create the node.


Description	INPUT OUTPUT
Status	OUTPUT	

To create and update contracts, you must define the output type and specify the value of these mandatory output fields. These fields are case-sensitive.

Status: The status of the contract.

IsAssociatedWithClm is flagged.

<SourceobjectId>

It isn't mandatory to add the word ‘source” as a prefix to the custom field. The custom field name must match the Contract, Contract Use Case Mapping, and Context Definition Mapping node structure.


IsAssociatedWithClm	OUTPUT
SourceOpportunityId, SourceOrderId, SourceQuoteId, or any source custom field that the user has configured in the Contract object.	OUTPUT


SalesContractLineCache

(child node)

	ParentReference	INPUT	The ParentReference field gets automatically created when the context definition is created.
Product	INPUT OUTPUT	 
UnitPrice	INPUT OUTPUT	 
TotalPrice	INPUT OUTPUT	 
ServiceDate	INPUT OUTPUT	 
ContractId	INPUT OUTPUT	ContractId is a mandatory field.
Name	INPUT OUTPUT	Name is a mandatory field.
See Also

Key Terms in Context Service

Create Custom Source Field for Contract Object
