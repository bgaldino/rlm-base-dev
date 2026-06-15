---
page_id: connect_resources_generate_documents.htm
title: Generate On-Demand Invoice Document (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_generate_documents.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_resources.htm
fetched_at: 2026-06-09
---

# Generate On-Demand Invoice Document (POST)

Generate an invoice document for a record, and update any junction
object record.

Resource
:   ```
    /revenue/billing/document/actions/generate
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/revenue/billing/document/actions/generate
    ```

Available version
:   66.0

HTTP methods
:   POST

Request body for POST
:   JSON example
    :   ```
        {
          "recordId": "3ttasd98776266777",
          "shouldForceRegenerate": true,
          "documentTemplateId": "0694x000000XyzABC",
          "documentTitle": "DOC-00000012",
          "tokenData": "{\"InvoiceLines\":{\"StartDate\":\"02/21/2025\",\"IsUsageBasedInvoiceLine\":false,\"UnitPrice\":\"$7.99\",\"ProductName\":\"Mouse\",\"UsageProductId\":\"01tSG00000BHFPSYA5\",\"Subtotal\":\"$7.99\",\"Quantity\":\"1\",\"Tax\":\"$0.00\",\"Id\":\"5TVSG000000DU3V4AW\",\"CurrencyIsoCode\":\"USD\",\"EndDate\":\"02/21/2025\"},\"NetCreditsApplied\":\"$0.00\",\"CompanyEmail\":\"rsamantaray@salesforce.com\",\"CompanyState\":\"CA\",\"DocumentNumber\":\"DOC-000000001\",\"SubTotal\":\"$7.99\",\"CompanyStreet\":\"1 Market St\",\"CompanyName\":\"260.1\",\"TotalAmnt\":\"$7.99\",\"TotalTax\":\"$0.00\",\"InvoiceDueDate\":\"10/08/2025\",\"CompanyPostalCode\":\"94105\",\"InvoiceDate\":\"09/08/2025\",\"CompanyCity\":\"San Francisco\",\"CompanyCountry\":\"US\",\"AccountName\":\"Sonia BAT Account\"}"
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `documentTemplateId` | String | Document template ID to use for PDF generation. The document template must be active with UsageType as `INVOICE`  If you don't specify this value, the system auto-resolves by using the default template. | Optional | 66.0 |
        | `documentTitle` | String | Custom title for the generated document. If you don't specify a value, the value is auto-generated. | Optional | 66.0 |
        | `recordId` | String | Record ID of the object the document is generated for. You can specify invoice ID only. | Required | 66.0 |
        | `shouldForceRegenerate` | Boolean | Indicates whether to regenerate the document (`true`) or not (`false`). If set to `true`, this API generates a document, replacing any existing ones. If set to `false`, this API skips the generation of document if invoice already has an associated document. The default value is `false`. | Optional | 66.0 |
        | `tokenData` | String | Token data to generate the document. | Optional | 66.0 |

Response body for POST
:   [On-Demand Document
    Generation Response](./connect_responses_on_demand_doc_gen_output.htm.md "Output representation of the details of the generated document along with error response.")
