---
page_id: connect_requests_extraction_context_use_case_mapping_input.htm
title: Extraction Context Use Case Mapping Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_requests_extraction_context_use_case_mapping_input.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_requests.htm
fetched_at: 2026-11-23
---

# Extraction Context Use Case Mapping Input

Input representation of the use case-mapping configuration in the extraction
context.

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `additional​UseCase​Input` | String | Additional input required to execute the selected use case, specified as a JSON string. For example, this property can store the LLM model associated with a template for the Extract Contract Details use case, such as `{"ModelName":"OpenAI"}`. | Optional | 67.0 |
| `context​Definition​DeveloperName` | String | Developer name of the context definition. | Required | 61.0 |
| `mapping​Name` | String | Name of the mapping. | Required | 61.0 |
| `record​Type` | String | Type of the record involved in the mapping. | Required | 61.0 |
| `target​Object` | String | SObject that the data maps to. | Required | 61.0 |
| `template​Name` | String | Name of the template used for the mapping. | Required | 61.0 |

## JSON Example

```
{
  "ContextUsecaseMapping": {
    "templateName": "ContractExtractionTemplate",
    "contextDefinitionDeveloperName": "ContractExtractionContextDefinition",
    "mappingName": "ContractExtractionMappingName",
    "targetObject": "Contract",
    "recordType": "CLM",
    "additionalUseCaseInput": "{\"ModelName\":\"OpenAI\"}"
  }
}
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_requests_extraction_context_use_case_mapping_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
