---
page_id: connect_requests_expression_set_des_token_mapping.htm
title: Expression Set DES Token Mapping Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_expression_set_des_token_mapping.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Expression Set DES Token Mapping Input

Input representation of the DES token mapping in an expression set
      version step.

**Root XML tag**

: `<ExpressionSetDesTokenMappingInput>`

**JSON example**

: 

```
"passedMessageTokenMappings": [
{
"expressionSetMessageToken": "price",
"resourceReference": "DM1__Price"
}
],
"failedMessageTokenMappings": [
{
"expressionSetMessageToken": "model",
"resourceReference": "Model"
}
],

"noResultMessageTokenMappings": [
{
"expressionSetMessageToken": "year",
"resourceReference": "Year"
}
]
```

**Properties**

: 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `resource​Reference` | String | Name of the expression set resource that’s mapped to a token, such as Variable, Constant, or FiledAlias. | Required | 59.0 |
| `expressionSet​MessageToken` | String | Name of the explainability message template token. | Required | 59.0 |
