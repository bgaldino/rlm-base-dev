---
page_id: connect_resources_get_activate_calc_procedure_version.htm
title: Calculation Procedure Version Definition (Activate, Get)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_get_activate_calc_procedure_version.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_resources.htm
fetched_at: 2026-06-25
---

# Calculation Procedure Version Definition (Activate, Get)

Retrieve the definition of an expression set (also known as
calculation procedure) version record. Activate an expression set version
record.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=industries_reference)

#### Note

This API has been deprecated as of API version 55.0.
In API version 55.0 and later, use the new [Business APIs in Business Rules Engine](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/business_rules_engine_connect_apis.htm).

Resource
:   ```
    /connect/omnistudio/evaluation-services/version-definitions/${id}
    ```

Example
:   ```
    /services/data/v53.0/connect/omnistudio/evaluation-services/
    version-definitions/0lIxx000000001dEAA
    ```

Available version
:   53.0

Requires Chatter
:   No

HTTP methods
:   GET, PATCH

Response body for GET
:   [Calculation Procedure Version Definition Output](./connect_responses_calculation_procedure_version_definition_output.htm.md "Output representation of the expression set version definition.")

Response body for PATCH
:   [Calculation Procedure Activation Output](./connect_responses_calculation_procedure_activation_output.htm.md "Output representation of the calculation procedure version record activation.")
