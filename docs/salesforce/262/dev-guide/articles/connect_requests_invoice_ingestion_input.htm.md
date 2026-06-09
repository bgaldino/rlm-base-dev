---
page_id: connect_requests_invoice_ingestion_input.htm
title: Invoice Ingestion Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_invoice_ingestion_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-06-09
---

# Invoice Ingestion Input

Input representation of the details of the invoice to be processed. The details include
the tax processing status, user preferences for tax callouts, and associated object graph
representation.

JSON example to ingest a draft invoice with a tax callout
:   ```
    {
      "invoices": [
        {
          "shouldCalculateTax": true,
          "taxCalculationStatus": "Estimated",
          "graph": {
            "graphId": "CreateInvoice",
            "records": [
              {
                "referenceId": "refAccount",
                "record": {
                  "attributes": {
                    "type": "Account",
                    "method": "GET",
                    "id": "ExternalId__c/123"
                  }
                }
              },
              {
                "referenceId": "refContact",
                "record": {
                  "attributes": {
                    "type": "Contact",
                    "method": "GET",
                    "id": "ExternalId__c/123"
                  }
                }
              },
              {
                "referenceId": "refInvoice",
                "record": {
                  "attributes": {
                    "type": "Invoice",
                    "method": "POST"
                  },
                  "billingAccountId": "@{refAccount.Id}",
                  "billToContactId": "@{refContact.Id}",
                  "paymentTermId": "2OXxx0000004CFUGA2",
                  "referenceEntityId": "801xx000003GeQQAA0",
                  "status": "Draft",
                  "invoiceDate": "2024-12-19",
                  "currencyIsoCode": "USD",
                  "dueDate": "2024-12-19",
                  "invoiceNumber": "DOC-10",
                  "description": "Sample Invoice",
                  "uniqueIdentifier": "5873af8f-f007-4aa0-9e3d-53a08c3f59de"
                }
              },
              {
                "referenceId": "refBillingAddress",
                "record": {
                  "attributes": {
                    "type": "InvoiceAddressGroup",
                    "method": "POST"
                  },
                  "street": "123 Main St",
                  "city": "NewYork",
                  "postalCode": "10001",
                  "state": "New York",
                  "country": "US",
                  "longitude": "123.456",
                  "latitude": "78.910",
                  "invoiceId": "@{refInvoice.id}"
                }
              },
              {
                "referenceId": "refShippingAddress",
                "record": {
                  "attributes": {
                    "type": "InvoiceAddressGroup",
                    "method": "POST"
                  },
                  "street": "123 Main St",
                  "city": "NewYork",
                  "postalCode": "10001",
                  "state": "New York",
                  "country": "US",
                  "longitude": "123.456",
                  "latitude": "78.910",
                  "invoiceId": "@{refInvoice.id}"
                }
              },
              {
                "referenceId": "refShipFromAddress",
                "record": {
                  "attributes": {
                    "type": "InvoiceAddressGroup",
                    "method": "POST"
                  },
                  "street": "1 Market Street",
                  "city": "San Francisco",
                  "postalCode": "94105",
                  "state": "CA",
                  "country": "US",
                  "longitude": "123.456",
                  "latitude": "78.910",
                  "invoiceId": "@{refInvoice.id}"
                }
              },
              {
                "referenceId": "refInvoiceLine1",
                "record": {
                  "attributes": {
                    "type": "InvoiceLine",
                    "method": "POST"
                  },
                  "name": "productName1",
                  "product2Id": "01txx0000006ic4AAA",
                  "invoiceLineStartDate": "2024-11-10",
                  "invoiceLineEndDate": "2024-11-13",
                  "quantity": "10",
                  "unitPrice": "10",
                  "chargeAmount": "100",
                  "invoiceId": "@{refInvoice.id}",
                  "referenceEntityItemId": "802xx000001neB9AAI",
                  "billingAddressId": "@{refBillingAddress.id}",
                  "shippingAddressId": "@{refShippingAddress.id}",
                  "shipFromAddressId": "@{refShipFromAddress.id}",
                  "taxTreatmentId": "1ttxx0000000BOTAA2",
                  "legalEntityId": "0fwxx0000000001AAA",
                  "legalEntityAccountingPeriodId": "1HLxx0000004C92GAE"
                }
              },
              {
                "referenceId": "refInvoiceLine2",
                "record": {
                  "attributes": {
                    "type": "InvoiceLine",
                    "method": "POST"
                  },
                  "name": "productName2",
                  "product2Id": "01txx0000006ic4AAA",
                  "invoiceLineStartDate": "2024-11-10",
                  "invoiceLineEndDate": "2024-11-15",
                  "quantity": "10",
                  "unitPrice": "10",
                  "chargeAmount": "100",
                  "invoiceId": "@{refInvoice.id}",
                  "referenceEntityItemId": "802xx000001neB9AAI",
                  "billingAddressId": "@{refBillingAddress.id}",
                  "shippingAddressId": "@{refShippingAddress.id}",
                  "shipFromAddressId": "@{refShipFromAddress.id}",
                  "taxTreatmentId": "1ttxx00000001DpAAI",
                  "legalEntityId": "0fwxx0000000001AAA",
                  "legalEntityAccountingPeriodId": "1HLxx0000004C92GAE"
                }
              },
              {
                "referenceId": "refInvoiceLineTax",
                "record": {
                  "attributes": {
                    "type": "InvoiceLineTax",
                    "method": "POST"
                  },
                  "taxAmount": 7.25,
                  "taxCode": "CA-94121",
                  "taxName": "CALIFORNIA",
                  "taxRate": 0.25,
                  "taxEffectiveDate": "2024-11-10",
                  "taxDocumentNumber": "123",
                  "taxExemptAmount": 0,
                  "taxTransactionNumber": "kl",
                  "description": "Associated tax line.",
                  "invoiceLineId": "@{refInvoiceLine1.id}"
                }
              },
              {
                "referenceId": "refInvoiceLineTax1",
                "record": {
                  "attributes": {
                    "type": "InvoiceLineTax",
                    "method": "POST"
                  },
                  "taxAmount": "10",
                  "taxCode": "CA-94121",
                  "taxName": "CALIFORNIA",
                  "taxRate": 0.25,
                  "taxEffectiveDate": "2024-11-10",
                  "taxDocumentNumber": "123",
                  "taxExemptAmount": 0,
                  "taxTransactionNumber": "125",
                  "invoiceLineId": "@{refInvoiceLine2.id}",
                  "description": "Associated tax line."
                }
              }
            ]
          }
        }
      ]
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `correlation​Id` | String | Splunk correlation ID to track the messages that are related to the request and are logged in Splunk by the different services involved in the request. If the ID isn’t specified, the service creates a random Universally Unique Identifier (UUID). | Optional | 63.0 |
    | `graph` | [Object Graph Input](https://developer.salesforce.com/docs/./connect_requests_object_graph_input.htm.md) | Graph that represents the invoice structure for invoice ingestion or generation.  The supported Graph attribute types for invoice ingestion are Account, Contact, Invoice, InvoiceLine, InvoiceLineTax, and InvoiceAddressGroup. See [Graph Record for Invoice Ingestion](./connect_requests_graph_record_input.htm.md "A Graph record is an object that’s a part of the graph structure, representing both the fields and relationships among different objects. Each record in the graph can contain attributes, which are fields of the object, and references to other related records."). | Required | 63.0 |
    | `should​CalculateTax` | Boolean | Indicates whether the estimated tax must be calculated for the ingested invoice (`true`) or not (`false`). The default value is `false`. | Optional | 63.0 |
    | `taxCalculation​Status` | String | Status of the tax calculation, which is saved on the invoice line. Valid values are:   - `Estimated` - `Pending` - `Posted`  The default value is `Pending`. | Optional | 63.0 |
