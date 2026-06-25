---
page_id: discoveryframework_prefill_integration_procedure.htm
title: DiscoveryFramework_Prefill Integration Procedure
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/discoveryframework_prefill_integration_procedure.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Discovery Framework
parent_page: discovery_framework.htm
fetched_at: 2026-06-25
---

# DiscoveryFramework\_Prefill Integration Procedure

The DiscoveryFramework\_Prefill Integration Procedure calls a
Omnistudio
Data Mapper and an Apex class. To customize the prefill flow, edit the steps of
the DiscoveryFramework\_Prefill Integration Procedure. Open the OmniStudio app, go to the
Integration Procedures page, expand the DiscoveryFramework/Prefill Integration Procedure, and open
the highest version.

|  |
| --- |
| Available in: Lightning Experience in **Enterprise**, **Professional**, and **Unlimited** editions where a Financial Services Cloud Growth license is enabled or in **Enterprise** and **Unlimited** editions where the Health Cloud license is enabled. |

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=industries_reference)

#### Note

To ensure access to this Integration Procedure, see [Security for
Omnistudio
Data Mappers and Integration Procedures](https://help.salesforce.com/s/articleView?id=xcloud.os_security_for_dataraptors_and_integration_procedures_56519.htm&type=5&language=en_US).

## Steps

| Component Name | Type | What it does | What it calls |
| --- | --- | --- | --- |
| GetAssessmentId | Omnistudio Data Mapper Extract Action | Fetches the Id of the most recent Assessment record related to the specified ContextId, which is an AccountId. | GetAssessmentId Omnistudio Data Mapper Extract |
| GetAssessmentData | Remote Action | Fetches the Assessment record object. | DiscoveryFrmwrk.PreFillAssessment Apex class |
| AssessmentData | Response Action | Returns the Assessment record data to the entity that called this Integration Procedure. | Nothing |

## GetAssessmentId Omnistudio Data Mapper

The GetAssessmentId
Omnistudio
Data Mapper Extract fetches the ID of the most recent Assessment record
related to the specified ContextId, which is an AccountId.

Settings
:   | Tab | Setting | Value |
    | --- | --- | --- |
    | Extract | Object | Assessment |
    | Extract | Extract Output Path | Assessment |
    | Extract | Filter | AccountId = ContextId ORDER BY LastModifiedDate DESC LIMIT 1 |
    | Output | Extract JSON Path | Assessment:Id |
    | Output | Output JSON Path | RemoteActionAssessmentId |

## PreFillAssessment Apex Class

Use the PreFillAssessment class to fetch question and response data related to an Assessment
object.

Namespace
:   DiscoveryFrmwrk

Usage
:   The PreFillAssessment class has two methods that do the same thing. The call method is
    necessary for the class to implement System.Callable.

Methods
:   - call(action, args)
    - omniScriptPreFill(input, output)

    call(action, args)

## call(action, args)

The call method accepts an Assessment Id and passes question and response data to the
AssessmentDataReturned output variable. It follows the syntax required for a class that
implements System.Callable.

API Version
:   57.0

Required Chatter
:   No

Signature
:   `public static PreFillAssessment call(String action,
    Map<String,Object> args)`

Parameters
:   **action**
:   Type: `string`
:   Set the action value to omniScriptPreFill
:   **args**
:   Type: `Map<String,Object>`
:   The first two names in the name-value pairs must be input and output. The input must
    specify an Assessment Id. The output must be null. For example: `{“input”: “0U3RO0000000Aai0AE”, “output”: null}`

Return Value
:   null

Usage
:   See the omniScriptPreFill method usage

## omniScriptPreFill(input, output)

The omniScriptPreFill method accepts an Assessment Id and passes question and response data to
the AssessmentDataReturned output variable.

API Version
:   57.0

Required Chatter
:   No

Signature
:   `public static PreFillAssessment
    omniScriptPreFill(Map<String,Object> input, Map<String,Object> output)`

Parameters
:   **input**
:   Type: `Map<String,Object>`
:   Set the input parameter to {“input”: “idString”}, where the idString is the Id of an
    Assessment object. For example: `{“input”:
    “0U3RO0000000Aai0AE”}`
:   **output**
:   Type: `Map<String,Object>`
:   In the input, set the output parameter to `{“output”:
    null}`.

Return Value
:   null

Usage
:   The data passed to the AssessmentDataReturned variable includes questions and their
    responses. The key for each question is the developer name of the question. For
    example:

    ```
    {
      "AssessmentDataReturned": {
        "RespondentName": "Arthur, King of the Britons.",
        "RespondentGoal": "To seek the Holy Grail.",
        "SwallowAirspeed": "An African or European swallow?"
      }
    }
    ```
