---
page_id: connect_requests_contract_risk_analysis_input.htm
title: Contract Risk Analysis Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_requests_contract_risk_analysis_input.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_requests.htm
fetched_at: 2026-11-23
---

# Contract Risk Analysis Input

Input representation to start a risk analysis for a contract
document version.

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `documentPlaybook​VersionId` | String | ID of the playbook version to use for risk analysis standards and comparison. | Optional | 68.0 |

## JSON Example

```
{
  "documentPlaybookVersionId" : "00OEE000003530L2AQ"
}
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_requests_contract_risk_analysis_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
