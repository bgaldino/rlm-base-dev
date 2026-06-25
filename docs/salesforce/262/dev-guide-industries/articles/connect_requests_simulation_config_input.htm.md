---
page_id: connect_requests_simulation_config_input.htm
title: Simulation Config Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_simulation_config_input.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_requests.htm
fetched_at: 2026-06-25
---

# Simulation Config Input

Input information of the configuration version to run a
simulation.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=industries_reference)

#### Note

This API has been deprecated as of API version 55.0.
In API version 55.0 and later, use the new [Business APIs in Business Rules Engine](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/business_rules_engine_connect_apis.htm).

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `versionInfo` | [Simulation Version Info Input](./connect_requests_simulation_version_info_input.htm.md "Input information of the version details to run simulation.") | The version information of the expression set. | Required | 53.0 |
