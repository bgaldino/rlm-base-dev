---
page_id: dynamic_revenue_orchestrator_default_order_fulfillment_provider.htm
title: Standard Fulfillment Provider
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/dynamic_revenue_orchestrator_default_order_fulfillment_provider.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_callouts_overview.htm
fetched_at: 2026-06-09
---

# Standard Fulfillment Provider

The Standard Fulfillment Provider or `CalloutIntegrationProvider` is a provider for the order fulfillment usage type. A
Fulfillment Designer can configure this provider.

The Standard Fulfillment Provider includes these features.

- Predefined payload with sales transaction items and fulfillment items data, including
  attribute values
- Fixed integration parameters such as timeouts, credentials, encoding styles, and path. See
  [Integration Definition for Standard
  Fulfillment Provider](./dynamic_revenue_orchestrator_integration_definition_for_standard_fulfillment_provider.htm.md "Use supported attribute values of an integration definition for a Standard Fulfillment Provider to implement features as per your requirement.") for details about the integration parameters.
- Modified requests and responses via Omnistudio Integration Procedures
- Asynchronous interaction pattern. See [Asynchronous Interaction Pattern](./dynamic_revenue_orchestrator_async_interaction_pattern.htm.md "To specify an asynchronous request, you must add the callback URI to the integration definition for Standard Fulfillment Provider or Apex Type Provider as an optional attribute.").
- Request and response logging
- Error handling and retry policies. See [Fallout Design and
  Management](https://help.salesforce.com/s/articleView?id=ind.dro_fallout_design_and_management.htm&language=en_US "HTML (New Window)").
- Request transformation and response handling via integration procedures

To ‌configure the callout settings for Standard Fulfillment Provider, see [Configuration Steps](./dynamic_revenue_orchestrator_callout_configuration_steps.htm.md "Before you set up a callout provider, configure the callout settings. The settings include the creation of a named credential and an external credential, the creation of an integration definition, and the configuration of a fulfillment step definition.").

## Request Payload

This example shows a sample request payload structure
with data for sales transaction items and fulfillment transaction items. This data is
derived using context definition mappings that are defined through settings. See [Context Definitions in Order
Orchestration](https://help.salesforce.com/s/articleView?id=ind.dro_use_context_definitions.htm&language=en_US "HTML (New Window)").

```
{
  "AccountId": "001xx000003GbsxAAC",
  "OrderId": "801xx000003GbsyAAC",
  "StepId": "802xx000001ndnyAAA",
  "PlanSourceId": "802xx000001ndnyAAA",
  "StepSourceId": "13Wxx0000004Cdh",
  "CorrelationId": "callout:13Wxx0000004Cdh:",
  "SalesTransactionItems": [
    {
      "ArePartialPeriodsAllowed": "false",
      "ParentReference": "801xx000003GbsyAAC",
      "IsAssetizable": "true",
      "ProductName": "iPhone18",
      "ProductCode": "iPhone18",
      "SalesTransactionItemParent": "801xx000003GbsyAAC",
      "Attributes": [
        {
          "AttributeKey": "0tjxx00000000ePAAQ",
          "ParentReference": "802xx000001ndnxAAA",
          "AttributeValue": "true",
          "AttributeName": "IsDeliveryNotificationNeeded",
          "AttributeDefinitionCode": "FDT5",
          "SalesTransactionItemAttrParent": "802xx000001ndnxAAA"
        },
        {
          "AttributeKey": "0tjxx00000000eNAAQ",
          "ParentReference": "802xx000001ndnxAAA",
          "AttributeValue": "10",
          "AttributeName": "FDTCharge",
          "AttributeDefinitionCode": "FDT3",
          "SalesTransactionItemAttrParent": "802xx000001ndnxAAA"
        }
      ],
      "Product": "01txx0000006igoAAA",
      "Quantity": "1.0",
      "ListPrice": "1.0",
      "ItemTotalAdjustmentAmount": "0.0",
      "SalesTransactionItemSource": "802xx000001ndnxAAA",
      "PricebookEntry": "01uxx0000008zT8AAI",
      "StartDate": "2024-10-15T00:00:00.000Z",
      "UnitPrice": "1.0",
      "RoundedLineAmount": "1.0",
      "EndQuantity": "1.0",
      "TotalTaxAmount": "0.0",
      "IsItemLocked": "false",
      "TotalPrice": "1.0",
      "ProductBasedOn": "11Bxx000002C9M2EAK",
      "SalesTransactionActionType": "Add",
      "SalesTransactionAction": "8OAxx0000004DGOGA2"
    },
    {
      "ArePartialPeriodsAllowed": "false",
      "ParentReference": "801xx000003GbsyAAC",
      "IsAssetizable": "true",
      "ProductName": "iPhone19",
      "ProductCode": "iPhone19",
      "SalesTransactionItemParent": "801xx000003GbsyAAC",
      "Attributes": [
        {
          "AttributeKey": "0tjxx00000000eQAAQ",
          "ParentReference": "802xx000001ndnyAAA",
          "AttributeValue": "false",
          "AttributeName": "IsDelivered",
          "AttributeDefinitionCode": "FDT6",
          "SalesTransactionItemAttrParent": "802xx000001ndnyAAA"
        }
      ],
      "Product": "01txx0000006igpAAA",
      "Quantity": "1.0",
      "ListPrice": "1.0",
      "ItemTotalAdjustmentAmount": "0.0",
      "SalesTransactionItemSource": "802xx000001ndnyAAA",
      "PricebookEntry": "01uxx0000008zTAAAY",
      "StartDate": "2024-10-20T00:00:00.000Z",
      "UnitPrice": "1.0",
      "RoundedLineAmount": "1.0",
      "EndQuantity": "1.0",
      "TotalTaxAmount": "0.0",
      "IsItemLocked": "false",
      "TotalPrice": "1.0",
      "ProductBasedOn": "11Bxx000002C9M2EAK",
      "SalesTransactionActionType": "Add",
      "SalesTransactionAction": "8OAxx0000004DGOGA2",
      "SalesTrxnItemDescription": "TrackingRef:TRK-HUBSWQT18-4238"
    }
  ],
  "FulfillmentTransactionItems": [
    {
      "ParentReference": "0a3xx00000000JOAAY",
      "OriginalQuantity": "2.0",
      "FulfillmentItemSource": "0a4xx00000000JOAAY",
      "Attributes": [
        {
          "FulfillmentOrderLineId": "0a4xx00000000JOAAY",
          "LineAttributeDefinitionCode": "FDT6",
          "ParentReference": "0a4xx00000000JOAAY",
          "LineAttributeName": "IsDelivered",
          "LineAttributeValue": "false",
          "LineAttributeKey": "0tjxx00000000eQAAQ"
        },
        {
          "FulfillmentOrderLineId": "0a4xx00000000JOAAY",
          "LineAttributeDefinitionCode": "FDT2",
          "ParentReference": "0a4xx00000000JOAAY",
          "LineAttributeName": "FDTColor",
          "LineAttributeKey": "0tjxx00000000eMAAQ"
        },
        {
          "FulfillmentOrderLineId": "0a4xx00000000JOAAY",
          "LineAttributeDefinitionCode": "FDT1",
          "ParentReference": "0a4xx00000000JOAAY",
          "LineAttributeName": "FDTSize",
          "LineAttributeKey": "0tjxx00000000eLAAQ"
        }
      ],
      "FulfillmentItemAction": "ADD",
      "FulfillmentItemProductCode": "iPhone-Pack",
      "FulfillmentOrderItemQuantity": "2.0",
      "FulfillmentItemProductName": "iPhone-Pack",
      "FulfillmentOrderId": "0a3xx00000000JOAAY",
      "FulfillmentItemTypeCode": "Product",
      "FulfillmentItemType": "Order Product",
      "FulfillmentOrderNumber": "FO-0002",
      "FulfillmentItemStartDate": "2024-10-20T00:00:00.000Z",
      "FulfillmentItemProductId": "01txx0000006igqAAA"
    },
    {
      "ParentReference": "0a3xx00000000JNAAY",
      "OriginalQuantity": "2.0",
      "FulfillmentItemSource": "0a4xx00000000JNAAY",
      "Attributes": [
        {
          "FulfillmentOrderLineId": "0a4xx00000000JNAAY",
          "LineAttributeDefinitionCode": "FDT2",
          "ParentReference": "0a4xx00000000JNAAY",
          "LineAttributeName": "FDTColor",
          "LineAttributeKey": "0tjxx00000000eMAAQ"
        },
        {
          "FulfillmentOrderLineId": "0a4xx00000000JNAAY",
          "LineAttributeDefinitionCode": "FDT5",
          "ParentReference": "0a4xx00000000JNAAY",
          "LineAttributeName": "IsDeliveryNotificationNeeded",
          "LineAttributeValue": "false",
          "LineAttributeKey": "0tjxx00000000ePAAQ"
        },
        {
          "FulfillmentOrderLineId": "0a4xx00000000JNAAY",
          "LineAttributeDefinitionCode": "FDT3",
          "ParentReference": "0a4xx00000000JNAAY",
          "LineAttributeName": "FDTCharge",
          "LineAttributeKey": "0tjxx00000000eNAAQ"
        }
      ],
      "FulfillmentItemAction": "ADD",
      "FulfillmentItemProductCode": "iPhone-Tech",
      "FulfillmentOrderItemQuantity": "2.0",
      "FulfillmentItemProductName": "iPhone-Tech",
      "FulfillmentOrderId": "0a3xx00000000JNAAY",
      "FulfillmentItemTypeCode": "Product",
      "FulfillmentItemType": "Order Product",
      "FulfillmentOrderNumber": "FO-0001",
      "FulfillmentItemStartDate": "2024-10-10T00:00:00.000Z",
      "FulfillmentItemProductId": "01txx0000006igrAAA"
    }
  ]
}
```

The step source ID of the fulfillment step, which is either a related
order or fulfillment item, determines the payload composition with these considerations.

- If the step source ID is an order item, then all order items of the order are included
  in the payload under the SalesTransactionItems node.
- If the step source ID is a fulfillment item, then all fulfillment items of the
  fulfillment order are included in the payload under the FulfillmentTransactionItems
  node.
- If a product attribute doesn't have a defined code, then the attribute is excluded from
  the payload.

## Considerations

Keep these considerations in mind for the request payload.

- The maximum request payload size limit is 12 MB.
- The default timeout period is five seconds, and the maximum timeout period is 120
  seconds.
- The encoding style for fulfillment order line items, sales transaction items, and
  attributes can be configured through the [Integration Definition for Standard
  Fulfillment Provider](./dynamic_revenue_orchestrator_integration_definition_for_standard_fulfillment_provider.htm.md "Use supported attribute values of an integration definition for a Standard Fulfillment Provider to implement features as per your requirement.").

## Error Handling

To verify if the callout request was successful, check the `status` value in the payload. If the status is undefined, then these HTTP codes
indicate ‌a successful response.

- `200`
- `201`
- `202`
- `203`
- `204`
- `205`
- `206`
- `302`
- `304`

If the request isn't successful, then the fulfillment step state is marked as `Fatally Failed`.

## Integration Definition Configurations

You can configure these additional features for the integration definition.

- Select the
  **Save
  the request and response as attachments to the record** checkbox for the
  integration definition to save request and response payloads as attachments to the
  Integration Provider Execution record. Content publish limits apply when saving request
  and response payloads as attachments. Use [Shield
  Platform Encryption](https://help.salesforce.com/s/articleView?id=xcloud.security_pe_overview.htm&type=5&language=en_US "HTML (New Window)") for secure storage of sensitive information.
- [Define Input and Output Processors
  for the Integration Definition](https://developer.salesforce.com/docs/./dynamic_revenue_orchestrator_input_output_processors.htm.md "HTML (New Window)") for the pre-processing of the standard fulfillment
  request before you send the request to an external system. See [Omnistudio
  Integration Procedures](https://help.salesforce.com/s/articleView?id=xcloud.os_omnistudio_integration_procedures_48334.htm&type=5&language=en_US "HTML (New Window)").

See [Create an
Integration Definition](https://help.salesforce.com/s/articleView?id=ind.consumption_framework_integration_definitions.htm&type=5&language=en_US "HTML (New Window)").

- **[Integration Definition for Standard Fulfillment Provider](./dynamic_revenue_orchestrator_integration_definition_for_standard_fulfillment_provider.htm.md)**  
  Use supported attribute values of an integration definition for a Standard Fulfillment Provider to implement features as per your requirement.
