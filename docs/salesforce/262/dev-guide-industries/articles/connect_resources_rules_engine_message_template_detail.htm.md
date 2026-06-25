---
page_id: connect_resources_rules_engine_message_template_detail.htm
title: Explainability Message Template Details (GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_rules_engine_message_template_detail.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: decision_explainer_bre_resources.htm
fetched_at: 2026-06-25
---

# Explainability Message Template Details (GET)

Retrieves the details of an explainability message template for a
specified template ID.

Resource
:   ```
    /connect/business-rules/explainability/message-templates/${messageTemplateId}
    ```

Resource Example
:   ```
    https://yourInstance.salesforce.com/services/data/v66.0/connect
    /business-rules/explainability/message-templates/8U8x00000000027CAA
    ```

Available version
:   56.0

Requires Chatter
:   No

HTTP methods
:   GET

Response body for GET
:   [Message Template Details](./connect_responses_message_template_detail_output.htm.md "Output representation of explainability message template details.")
