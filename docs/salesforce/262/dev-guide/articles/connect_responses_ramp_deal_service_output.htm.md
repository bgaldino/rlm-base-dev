---
page_id: connect_responses_ramp_deal_service_output.htm
title: Ramp Deal Service
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_ramp_deal_service_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_responses.htm
fetched_at: 2026-06-09
---

# Ramp Deal Service

Output representation of the details of a created, updated, or deleted ramp
deal.

JSON Example
:   This example shows the sample response for the create, update, or view ramp deal
    requests.

    ```
    {
      "correlationId": "0QLDU0000002t0Z4AQ",
      "errors": [],
      "salesTransactionContext": {
        "SalesTransaction": [
          {
            "LegalEntity": null,
            "Account": null,
            "HeaderDistributionType": null,
            "BillingCity": null,
            "AccountBusinessType": null,
            "HeaderDiscountType": null,
            "businessObjectType": "Quote",
            "QuoteAccount": null,
            "EmployeeCount": null,
            "SalesTransactionName": "WarrantyPriceRampAR",
            "StartDate": null,
            "HeaderDiscountValue": null,
            "SalesTransactionType": null,
            "Pricebook": "01sDU000000JGf4YAG",
            "Opportunity": null,
            "ShippingCountry": null,
            "ShippingCity": null,
            "BillingPostalCode": null,
            "id": "0Q0DU0000002f3d0AA",
            "BillToContact": null,
            "CalculationStatus": "CompletedWithTax",
            "Status": "Draft",
            "LastPricedDate": null,
            "Subtotal": 108.47145205479453,
            "OriginalActionType": null,
            "TotalAmount": 99.98,
            "CurrencyIsoCode": null,
            "ShippingStreet": null,
            "SalesTransactionItem": [
              {
                "LegalEntity": null,
                "ProductName": "Warranty",
                "businessObjectType": "QuoteLineItem",
                "Product": "01tDU000000EsWSYA0",
                "ItemIsPrimarySegment": true,
                "ListPrice": 49.99,
                "ValidationResult": null,
                "StartDate": "2024-08-23T00:00:00.000Z",
                "ContractVolumePasId": null,
                "BillingTreatment": null,
                "PeriodBoundaryStartMonth": null,
                "SalesTransactionSourceAsset": null,
                "id": "0QLDU0000002t0Z4AQ",
                "PartnerDiscountPercent": null,
                "PriceWaterFall": "0QLDU0000002t0Z4AQ:548201414593252",
                "ItemProductRecipient": null,
                "BillingFrequency": "Annual",
                "ProductCode": "W001",
                "DerivedPricingAttribute": null,
                "TaxTreatment": "1ttDU0000001oGKYAY",
                "Subtotal": 8.491452054794523,
                "ItemRampIdentifier": "RDI5b5ce52b2db4484",
                "ItemSegmentName": "Trial",
                "PricebookEntry": "01uDU000000f4LSYAY",
                "DiscountAmount": null,
                "PricingTermCount": 0.0849315068493151,
                "NetUnitPrice": 0,
                "ItemEffectiveGrantDate": null,
                "ProductCategory": null,
                "SalesTransactionAction": null,
                "SalesTransactionActionType": null,
                "SalesTransactionItemGroup": null,
                "PeriodBoundaryDay": null,
                "LineItemDistributionType": null,
                "ProrationPolicy": "0muDU00000029ryYAA",
                "ContractDiscountType": null,
                "TransactionType": null,
                "ParentReference": null,
                "Discount": 100,
                "ProductSellingModel": "0jPDU00000029zb2AA",
                "PricingTermUnit": "Annual",
                "PricingSource": null,
                "StockKeepingUnit": null,
                "PartnerUnitPrice": null,
                "ItemTotalAdjustmentAmount": -8.491452054794523,
                "SalesTransactionItemSource": "0QLDU0000002t0Z4AQ",
                "ContractAttributePasId": null,
                "SubscriptionTerm": 1,
                "SellingModelType": "TermDefined",
                "EndQuantity": 2,
                "NetTotalPrice": 0,
                "TotalLineAmount": 8.491452054794523,
                "ItemSegmentType": "FreeTrial",
                "ProductBasedOn": null,
                "Deleted": null,
                "BillingReference": null,
                "ArePartialPeriodsAllowed": true,
                "ItemRecordedPrice": null,
                "CustomProductName": "Warranty",
                "ItemSegmentIdentifier": "SEG4380006a1c2b416",
                "SalesTransactionItemParent": "0Q0DU0000002f3d0AA",
                "Quantity": 2,
                "PeriodBoundary": "Anniversary",
                "ContractDiscountValue": null,
                "LineItemDiscountValue": null,
                "ContractId": null,
                "EndDate": "2024-09-22T00:00:00.000Z",
                "ItemGroupSummarySubtotal": null,
                "IsContracted": null,
                "UnitPrice": 49.99,
                "StartQuantity": 0,
                "ContractPrice": null,
                "TotalPrice": 0,
                "ItemPath": null,
                "LineItemDiscountType": null
              },
              {
                "LegalEntity": null,
                "ProductName": "Warranty",
                "businessObjectType": "QuoteLineItem",
                "Product": "01tDU000000EsWSYA0",
                "ItemIsPrimarySegment": false,
                "ListPrice": 49.99,
                "ValidationResult": null,
                "StartDate": "2024-09-23T00:00:00.000Z",
                "ContractVolumePasId": null,
                "BillingTreatment": null,
                "PeriodBoundaryStartMonth": null,
                "SalesTransactionSourceAsset": null,
                "id": "0QLDU0000003CZ94AM",
                "PartnerDiscountPercent": null,
                "PriceWaterFall": "0QLDU0000003CZ94AM:548201414593252",
                "ItemProductRecipient": null,
                "BillingFrequency": "Annual",
                "ProductCode": "W001",
                "DerivedPricingAttribute": null,
                "TaxTreatment": "1ttDU0000001oGKYAY",
                "Subtotal": 99.98,
                "ItemRampIdentifier": "RDI5b5ce52b2db4484",
                "ItemSegmentName": "Year-1",
                "PricebookEntry": "01uDU000000f4LSYAY",
                "DiscountAmount": null,
                "PricingTermCount": 1,
                "NetUnitPrice": 49.99,
                "ItemEffectiveGrantDate": null,
                "ProductCategory": null,
                "SalesTransactionAction": null,
                "SalesTransactionActionType": null,
                "SalesTransactionItemGroup": null,
                "PeriodBoundaryDay": null,
                "LineItemDistributionType": null,
                "ProrationPolicy": "0muDU00000029ryYAA",
                "ContractDiscountType": null,
                "TransactionType": null,
                "ParentReference": null,
                "Discount": null,
                "ProductSellingModel": "0jPDU00000029zb2AA",
                "PricingTermUnit": "Annual",
                "PricingSource": null,
                "StockKeepingUnit": null,
                "PartnerUnitPrice": null,
                "ItemTotalAdjustmentAmount": 0,
                "SalesTransactionItemSource": "0QLDU0000003CZ94AM",
                "ContractAttributePasId": null,
                "SubscriptionTerm": 1,
                "SellingModelType": "TermDefined",
                "EndQuantity": 2,
                "NetTotalPrice": 99.98,
                "TotalLineAmount": 99.98,
                "ItemSegmentType": "Yearly",
                "ProductBasedOn": null,
                "Deleted": null,
                "BillingReference": null,
                "ArePartialPeriodsAllowed": true,
                "ItemRecordedPrice": null,
                "CustomProductName": "Warranty",
                "ItemSegmentIdentifier": "SEG73ad7378e1ed4c5",
                "SalesTransactionItemParent": "0Q0DU0000002f3d0AA",
                "Quantity": 2,
                "PeriodBoundary": "Anniversary",
                "ContractDiscountValue": null,
                "LineItemDiscountValue": null,
                "ContractId": null,
                "EndDate": "2025-08-22T00:00:00.000Z",
                "ItemGroupSummarySubtotal": null,
                "IsContracted": null,
                "UnitPrice": 49.99,
                "StartQuantity": 0,
                "ContractPrice": null,
                "TotalPrice": 99.98,
                "ItemPath": null,
                "LineItemDiscountType": null
              }
            ],
            "AppUsageAssignment": [
              {
                "businessObjectType": "AppUsageAssignment",
                "ParentReference": null,
                "Record": "0Q0DU0000002f3d0AA",
                "id": "0j8DU0000002VKiYAM",
                "AppUsageType": "RevenueLifecycleManagement"
              }
            ],
            "BillingCountry": null,
            "BillingStreet": null,
            "ShippingPostalCode": null,
            "SalesTransactionSource": "0Q0DU0000002f3d0AA",
            "PrimaryIndustry": null,
            "ShippingState": null,
            "HeaderDistributionLogic": null,
            "Contract": null,
            "BillingState": null,
            "AnnualRevenue": null,
            "EffectiveDate": null
          }
        ]
      },
      "success": true,
      "transactionContextId": "d3fd83b007418ce4980340313b40fd45665b194973486ebac3674c2b8002336f"
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `correlation​Id` | String | Resource ID to correlate the API request with the response. | Small, 62.0 | 62.0 |
| `errors` | [Ramp Deal Service Error Response](./connect_responses_ramp_deal_service_error_response.htm.md "Output representation of the details of errors encountered during the processing of the API request.")[] | List of errors encountered during the processing of the API request. | Small, 62.0 | 62.0 |
| `sales​Transaction​Context` | Map<String, Object> | Context object for the sales transaction with updated segment details. | Small, 62.0 | 62.0 |
| `success` | Boolean | Indicates whether the API request is successful (`true`) or not (`false`). | Small, 62.0 | 62.0 |
| `transaction​ContextId` | String | ID of the sales transaction context record instance. | Small, 62.0 | 62.0 |
