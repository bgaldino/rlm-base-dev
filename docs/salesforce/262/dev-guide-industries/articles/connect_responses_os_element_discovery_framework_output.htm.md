---
page_id: connect_responses_os_element_discovery_framework_output.htm
title: Omniscript Element Discovery Framework Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_os_element_discovery_framework_output.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Discovery Framework
parent_page: dfdt_apis_responses.htm
fetched_at: 2026-06-25
---

# Omniscript Element Discovery Framework Output

Output representation of the custom type details of the Omniscript elements for
Discovery Framework.

JSON example
:   ```
          "discoveryFramework": {
           "questionText": "Can you provide more details about the transaction"
        }
    ```

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=industries_reference)

#### Note

When you receive a GET response, HTML replaces reserved characters with their
corresponding entities. For example, "What's your address" will appear as "What&#39; s
your address."

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `description` | String | Description of the question for the Discovery Framework question type element. | Small, 63.0 | 63.0 |
| `displayTextCategory` | String | The category of the display text when the data type is Text Block. This field valued is returned for Health Cloud customers only. | Small, 63.0 | 63.0 |
| `question​Category` | String | Category of the question for the Discovery Framework question type element. | Small, 60.0 | 60.0 |
| `question​DataType` | String | Data type of the question for the Discovery Framework question type element. | Small, 60.0 | 60.0 |
| `question​Developer​Name` | String | Developer name of the question for the Discovery Framework question type element. | Small, 60.0 | 60.0 |
| `question​Namespace` | String | Namespace of the question for the Discovery Framework question type element. | Small, 60.0 | 60.0 |
| `question​Text` | String | Text of the question for the Discovery Framework question type element. | Small, 60.0 | 60.0 |
