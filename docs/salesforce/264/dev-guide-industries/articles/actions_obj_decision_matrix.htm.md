---
page_id: actions_obj_decision_matrix.htm
title: Decision Matrix Actions
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/actions_obj_decision_matrix.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: lookup_tables_invocable_actions.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Decision Matrix Actions

Invoke a decision matrix in a flow with the Decision Matrix
      Actions. A decision matrix is a user-defined table where you can look up an output based
    on the inputs you provide. 

    
      

For example, you can look up a candidate’s eligibility to avail medical insurance in a
        decision matrix based on the candidate’s age and gender.

    

    
      

These actions are available in API version 55.0 and later.

    

    

## Supported REST HTTP Methods

      
      
        
          
            

**URI**

            
: 
`/services/data/v55.0/actions/custom/runDecisionMatrix/{UniqueName}`

#### Note

The
                value of UniqueName is the unique identifier of the record, which is sourced from
                the name of a decision matrix.

          
          
            

**Formats**

            
: JSON

          
          
            

**HTTP Methods**

            
: POST

          
          
            

**Authentication**

            
: `Authorization: Bearer
                  token`

          
        

      

    

    

## Inputs

      
      

Vary depending on the selected decision matrix.

    

    

## Outputs

      
      

Vary depending on the inputs of the selected decision matrix.

    

    

## Usage

      
      
        
          

**Sample Request**

          
: 
            

Here’s an example POST request that has the inputs, such as, age and state:

            

```
{
   "inputs":[
      {
         "age":"25",
         "state":"NY"
      },
      {
         "age":"25",
         "state":"CA"
      },
      {
         "age":"",
         "state":"WA"
      }
   ]
}
```

          

        
        
          

**Sample Response**

          
: 
            

Here’s an example response that has the premium and tax values based on the inputs
              provided in the example request.

            

```
[
   {
      "actionName":"premiumTaxLookup",
      "errors":null,
      "isSuccess":true,
      "outputValues":{
         "premium":2400.0,
         "tax":200.0
      }
   },
   {
      "actionName":"premiumTaxLookup",
      "errors":null,
      "isSuccess":true,
      "outputValues":{
         "premium":2400.0,
         "tax":200.0
      }
   },
   {
      "actionName":"premiumTaxLookup",
      "errors":[
         {
            "statusCode":"REQUIRED_FIELD_MISSING",
            "message":"Missing required input parameter: age",
            "fields":[
            ]
         }
      ],
      "isSuccess":false,
      "outputValues":null
   }
]
```
