---
page_id: connect_resources_list_of_contract_actions.htm
title: List of Contract Actions
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_resources_list_of_contract_actions.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: connect_resources_clm_resources.htm
fetched_at: 2026-10-13
---

# List of Contract Actions

 Get the list of actions possible for a particular
    contract.

    

## Resource

      
      

```
/connect/clm/contract/$CONTRACT_ID/contract-actions
```

    

    

## Available Version

      
      

56.0

    

    

## HTTP Methods

      
      

GET

    

    

## Example for GET

      
      

```
https://YOUR_INSTANCE.salesforce.com/services/data/v56.0/connect/clm/contract/${contractId}/contract-actions
```

    

    

## Response Body for GET

      
      

[Contract Action List Representation](./connect_responses_contract_action_list_respns.htm.md)
