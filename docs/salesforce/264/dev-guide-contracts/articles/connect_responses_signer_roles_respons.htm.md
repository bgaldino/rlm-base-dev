---
page_id: connect_responses_signer_roles_respons.htm
title: Signer Roles Details
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_signer_roles_respons.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_responses.htm
fetched_at: 2026-10-13
---

# Signer Roles Details

Details of the e-signature signer roles.

    

## Properties

      
      

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `signerRoles` | String[] | Indicates the index or order of the signer in the e-signature. | Big, 56.0 | 56.0 |

    

    

## JSON Example

      
      

```

{
    "signerRoles": [
                        "signer1",
                        "signer2",
                        "signer3",
                        "signer4",
                        ........
                        "signerN"
                    ]
}
```
