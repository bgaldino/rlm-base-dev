---
page_id: connect_resources_invoices_ingestion.htm
title: Invoice Ingestion (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_invoices_ingestion.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_resources.htm
fetched_at: 2026-06-09
---

# Invoice Ingestion (POST)

Ingest or generate an invoice from an internal or external billing
transaction data.

Create invoices from any external or internal transaction. For example, create invoices by using
external orders, policies, quotes, or internal data, such as assets or quotes.

You can also perform these additional tasks.

- Ingest invoices from any external system into Billing to manage invoice operations such
  as issuing credits against an invoice or voiding an invoice.
- Generate invoices from debit memos from API version 66.0 and later.

Keep these considerations in mind when you use this API.

- If the Convert Negative Invoice Lines to Credit Memo Lines feature isn’t enabled, use
  the [Negative Invoice Lines to Credit
  Conversion API](./connect_resources_convert_negative_invoice_lines_to_credit.htm.md "HTML (New Window)") to create a credit memo against an ingested negative invoice
  line.
- Use the [Apply Credit Action](./actions_obj_run_apply_credit.htm.md "HTML (New Window)") to
  apply a credit memo to an invoice.
- To ingest legacy invoices, create at least one invoice line.
- To generate invoices from debit memos, specify the debit memo ID as the `referenceEntityId` property value in the request body of
  this API. Make sure that the debit memo is in `Posted`
  status and is ready for invoice generation. The invoice is generated in `Draft` status.

Resource
:   ```
    /commerce/invoicing/invoices/collection/actions/ingest
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/commerce/invoicing/invoices/collection/actions/ingest
    ```

Available version
:   63.0

HTTP methods
:   POST

Request body for POST
:   JSON example to ingest a draft invoice with a tax callout
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

    JSON example to ingest a draft invoice without a tax callout
    :   ```
        {
          "invoices": [
            {
              "taxCalculationStatus": "Estimated",
              "graph": {
                "graphId": "123",
                "records": [
                  {
                    "referenceId": "refAccount",
                    "record": {
                      "attributes": {
                        "type": "Account",
                        "method": "GET",
                        "id": "TestExternalId__c/123"
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
                      "billToContactId": "003xx000004Wk8qAAC",
                      "paymentTermId": "2OXxx0000004CFUGA2",
                      "referenceEntityId": "801xx000003GeQQAA0",
                      "status": "Draft",
                      "invoiceDate": "2024-12-19",
                      "currencyIsoCode": "USD",
                      "dueDate": "2024-12-19",
                      "invoiceNumber": "DOC-10",
                      "description": "testInvoice",
                      "uniqueIdentifier": "c76011a1-e113-49d9-9c54-3b5c68950ada"
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
                      "description": "description for tax Line",
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
                      "description": "description for tax Line"
                    }
                  }
                ]
              }
            }
          ]
        }
        ```

    JSON example to ingest posted invoices
    :   ```
        {
          "invoices": [
            {
              "taxCalculationStatus": "Posted",
              "graph": {
                "graphId": "123",
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
                    "referenceId": "refInvoice",
                    "record": {
                      "attributes": {
                        "type": "Invoice",
                        "method": "POST"
                      },
                      "billingAccountId": "001SG00000njpF3YAI",
                      "billToContactId": "003xx000004Wk8qAAC",
                      "paymentTermId": "2OXxx0000004CFUGA2",
                      "referenceEntityId": "801xx000003GeQQAA0",
                      "status": "Posted",
                      "invoiceDate": "2024-12-19",
                      "currencyIsoCode": "USD",
                      "dueDate": "2024-12-19",
                      "invoiceNumber": "DOC-10",
                      "description": "Sample Invoice",
                      "uniqueIdentifier": "9994b2c4-c0c3-47c3-806f-ae6e1f16bac3"
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
                      "invoiceLineId": "@{refInvoiceLine1.id}",
                      "description": "Associated tax line."
                    }
                  }
                ]
              }
            }
          ]
        }
        ```

    JSON example to generate invoices from debit memos
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
                    "referenceId": "refInvoice",
                    "record": {
                      "attributes": {
                        "type": "Invoice",
                        "method": "POST"
                      },
                      "accountId": "001SB00001V3RxNYAV",
                      "billToContactId": "003xx000004WhUQAA0",
                      "referenceEntityId": "4DmAAC000008UP70BM",
                      "status": "Draft",
                      "invoiceDate": "2024-12-19",
                      "dueDate": "2024-12-19",
                      "description": "Sample Invoice"
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
        | `invoices` | [Invoice Ingestion Input](./connect_requests_invoice_ingestion_input.htm.md "Input representation of the details of the invoice to be processed. The details include the tax processing status, user preferences for tax callouts, and associated object graph representation.")[] | List of invoices to be generated or ingested, enabling the submission and processing of multiple invoices in a single request. This API supports one invoice per request. To send 25 requests at a time, see the [Composite Batch request](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_rest.meta/api_rest/requests_composite_batch.htm "HTML (New Window)"). | Required | 63.0 |

Response body for POST
:   [Invoice
    Ingestion](./connect_responses_invoices_ingestion_output.htm.md "Output representation of the details of the generated invoices.")
