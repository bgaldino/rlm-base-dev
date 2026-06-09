---
page_id: connect_requests_graph_record_input.htm
title: Graph Record for Invoice Ingestion
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_graph_record_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-06-09
---

# Graph Record for Invoice Ingestion

A Graph record is an object that’s a part of the graph structure,
representing both the fields and relationships among different objects. Each record in the
graph can contain attributes, which are fields of the object, and references to other related
records.

Invoice ingestion supports a Graph record count of 500. The supported Graph
attribute types for invoice ingestion are Account, Contact, Invoice, InvoiceLine,
InvoiceLineTax, and InvoiceAddressGroup.

A Graph record has these properties and associated fields.

| Field | Description |
| --- | --- |
| `referenceId` | Unique identifier of the record that’s used to reference the record in the graph. |
| `record` | Object containing the actual data for the record. |
| `record.attributes.type` | Standard object of the referenced record. In this scenario, this field indicates an `InvoiceAddressGroup` attribute type. |
| `record.attributes.method` | Method that defines the operation on the record. For example, POST to create a record, PUT to update a record, or GET to get record data. |

JSON example
:   ```
    {
      "referenceId": "refBillingAddress",
      "record": {
        "attributes": {
          "type": "InvoiceAddressGroup",
          "method": "POST"
        },
        //Contains the actual data
      }
    }
    ```

## Account Record

Keep these considerations in mind when you specify an Account record as the Graph attribute
type.

- The supported Graph attribute method is GET only.
- The supported record count that you can specify for each account is one only.
- The id field on attributes is the value of the externalId field API Name in [Account](https://developer.salesforce.com/docs/atlas.en-us.262.0.object_reference.meta/object_reference/sforce_api_objects_account.htm "HTML (New Window)"). Use this field to
  resolve the Salesforce Account ID from the custom external ID field. See [Use an 'External ID' to set the values for audit
  fields](https://help.salesforce.com/s/articleView?id=000383278&type=1&language=en_US "HTML (New Window)").

JSON example
:   ```
    {
      "referenceId": "refAccount", 
      "record": {
        "attributes": {
          "type": "Account",
          "method": "GET",
          "id": "AccountId__c/7661eaaf-f527-4dcf-beb3-301f3eddcd9e"
        }
      }
    }
    ```

## Contact Record

Keep these considerations in mind when you specify a Contact record as the Graph attribute
type.

- The supported Graph attribute method is GET only.
- The supported record count that you can specify for Contact is one only.
- The id field on attributes is the value of the externalId field API Name in [Contact](https://developer.salesforce.com/docs/atlas.en-us.262.0.object_reference.meta/object_reference/sforce_api_objects_contact.htm "HTML (New Window)"). Use this field to resolve the Salesforce Contact ID from the custom
  external ID field. See [Use an 'External ID' to set the values for audit
  fields](https://help.salesforce.com/s/articleView?id=000383278&type=1&language=en_US "HTML (New Window)").

JSON example
:   ```
    {
      "referenceId": "refContact", 
      "record": {
        "attributes": {
          "type": "Contact",
          "method": "GET",
          "id": "ContactId__c/7661eaaf-f527-4dcf-beb3-301f3eddcd9e"
        }
      }
    }
    ```

## Invoice Record

Keep these considerations in mind when you specify an Invoice record as the Graph attribute
type.

- The supported Graph attribute method is POST only.
- The supported record count that you can specify for Invoice is one only.
- An invoice with `Draft` status can’t have a posted
  date.
- You can’t use an invoice with `Draft` status when the
  `taxCalculationStatus` property value is `Posted`. The `taxCalculationStatus` property must be `Estimated` or `Pending`.
- You can’t use an invoice with `Posted` status when
  the `shouldCalculateTax` property is `true`.
- An invoice with `Posted` status can’t include the
  `Estimated` or `Pending` as the `taxCalculationStatus`
  property values. The tax processing status must be `Posted`.
- An invoice with `Posted` status with an invoice line
  marked as `taxable` must include an `invoiceLineTax` for that invoice line.
- An invoice with `Posted` status with an invoice line
  marked as `nontaxable` must not include an `invoiceLineTax` for that invoice line.
- The `invoice.CreationMode` field value is `External`. This field differentiates the invoices created
  from a billing schedule or an invoice ingestion. For invoices created from a billing
  schedule, the value is Salesforce. For invoices created from an invoice ingestion, the
  value is `External`.
- The due date of an invoice graph is in the future or with a valid payment term, or your
  Salesforce org has a default payment term set.

JSON example
:   ```
    {
      "referenceId": "refInvoice",
      "record": {
        "attributes": {
          "type": "Invoice",
          "method": "POST"
        },
        "invoiceDate": "2024-01-01",
        "billingAccountId": "001xx000003Dzo9AAC",
        "billToContactId": "003xx000004TzFoAAI",
        "paymentTermId": "2OXxx0000004CFUGA2",
        "referenceEntityId": "801xx000003GeQQAA0",
        "status": "Draft",
        "currencyIsoCode": "USD",
        "dueDate": "2024-02-01",
        "postedDate": "2024-01-02",
        "invoiceNumber": "INV-12345",
        "uniqueIdentifier": "1a9380c1-8042-422d-bcc5-70c3f51c2588",
        "description": "Consulting Services"
      }
    }
    ```
:   Table 1. Properties

    | NAME | Standard Object Field | Description | Required or Optional |
    | --- | --- | --- | --- |
    | `invoiceDate` | Invoice.invoiceDate | Date when the invoice was created or issued. | Required |
    | `billingAccountId` | Invoice.billingAccountId | Billing account associated with this invoice, which you can resolve with the externalId field by using the GET method. | Required |
    | `billToContactId` | Invoice.billToContactId | Contact to whom the invoice is billed, which you can resolve with the externalId field by using the GET method. | Required |
    | `paymentTermId` | Invoice.paymentTermId | Payment term associated with the invoice. If a value isn’t specified, then the default payment term ID is used. | Optional |
    | `referenceEntityId` | Invoice.referenceEntityId | Reference to a related object, if applicable.  To generate invoices from debit memos, specify the debit memo ID as the property value. Make sure that the debit memo is in `Posted` status. Available in API version 66.0 and later. The invoice is generated in `Draft` status. | Optional |
    | `status` | Invoice.status | Status of the invoice. Valid values are:   - `Draft` - `Posted`.  The default value is `Draft`. | Optional |
    | `currencyIsoCode` | Invoice.currencyIsoCode | ISO code representing the currency of the invoice. This property must be specified if multi-currency is enabled in the organization. | Optional |
    | `dueDate` | Invoice.dueDate | Due date for the invoice payment. If a value isn’t specified, then this value is set based on the payment term. | Optional |
    | `postedDate` | Invoice.postedDate | Date the invoice was posted to the system.  Until API version 64.0, the default value is the current date irrespective of the value that’s specified in the input payload. In API version 65.0 and later, the posted date specified in the input payload is considered. | Required in API version 65.0 and later. |
    | `invoiceNumber` | Invoice.invoiceNumber | Unique identifier for the invoice. | Optional |
    | `uniqueIdentifier` | Invoice.uniqueIdentifier | Unique identifier for the invoice. This property is used as the idempotency key to avoid duplicate invoice generation. | Optional |
    | `description` | Invoice.description | Short description of the invoice or the billed items. | Optional |

## Invoice Line Record

Keep these considerations in mind when you specify an Invoice Line record as the Graph
attribute type.

- The supported Graph attribute method is POST only.
- The Graph must include at least one Graph record with the InvoiceLine attribute
  type.
- The invoice line end date must be greater than or equal to the invoice line start
  date.

JSON example
:   ```
    {
      "referenceId": "refInvoiceLine",
      "record": {
        "attributes": {
          "type": "InvoiceLine",
          "method": "POST"
        },
        "name": "Parle G",
        "invoiceLineStartDate": "2024-01-01",
        "invoiceLineEndDate": "2024-01-31",
        "quantity": 10,
        "unitPrice": 25,
        "chargeAmount": 250,
        "invoiceId": "@{refInvoice.id}",
        "shippingAddressId": "@{refShippingAddress.id}",
        "billingAddressId": "@{refBillingAddress.id}",
        "referenceEntityItemId": "802xx000001neB9AAI",
        "taxTreatmentId": "1ttxx0000000BOTAA2",
        "legalEntityId": "0fwxx0000000001AAA",
        "legalEntityAccountingPeriodId": "1HLxx0000004C92GAE",
        "product2Id": "01txx0000006ic4AAA",
        "usageProductId": "01txx0000006ic5AAA",
        "isUsageBasedInvoiceLine": false,
        "usageOverageQuantity": 5,
        "unitOfMeasureId": "0hExx0000000001EAA",
        "description": "Sample product description"
      }
    }
    ```
:   Table 2. Properties

    | NAME | Standard Object Field | Description | Required or Optional |
    | --- | --- | --- | --- |
    | `name` | InvoiceLine.name | Name or description of the invoice line item. | Required |
    | `invoiceLineStartDate` | InvoiceLine.invoiceLineStartDate | Start date for the invoice line period. For example, the date when the product or service is provided. | Required |
    | `invoiceLineEndDate` | InvoiceLine.invoiceLineEndDate | End date for the invoice line period. For example, the date when the product or service ends. | Required |
    | `quantity` | InvoiceLine.quantity | Quantity of the product or billed service in this invoice line. | Required |
    | `unitPrice` | InvoiceLine.unitPrice | Price per unit of the product or billed service. | Required |
    | `chargeAmount` | InvoiceLine.chargeAmount | Total charge amount for this invoice line, which is calculated as quantity \* unit price. | Required |
    | `invoiceId` | InvoiceLine.invoiceId | Reference to the invoice that this invoice line is associated with. | Required |
    | `shippingAddressId` | InvoiceLine.shippingAddressId | Shipping address associated with this invoice line. | Required |
    | `billingAddressId` | InvoiceLine.billingAddressId | Billing address associated with this invoice line. | Required |
    | `referenceEntityItemId` | InvoiceLine.referenceEntityItemId | Reference to a related object record for this invoice line. | Optional |
    | `taxTreatmentId` | InvoiceLine.taxTreatmentId | Tax treatment applied to this invoice line such as taxable or nontaxable. If the `TaxTreatmentId` property isn’t specified in the request, it’s retrieved from the [organization's default values](https://help.salesforce.com/s/articleView?language=en_US&id=ind.guided_setup_for_billing.htm&type=5 "HTML (New Window)"). If the organization's defaults aren’t set, an error is thrown. | Optional |
    | `legalEntityId` | InvoiceLine.legalEntityId | Legal entity that this invoice line belongs to. If the `LegalEntityId` property isn’t specified in the request, it’s retrieved from the [organization's default values](https://help.salesforce.com/s/articleView?id=ind.guided_setup_for_billing.htm&type=5&language=en_US "HTML (New Window)"). If the organization's defaults aren’t set, an error is thrown. | Optional |
    | `legalEntityAccountingPeriodId` | InvoiceLine.legalEntityAccountingPeriodId | Accounting period for the legal entity that this invoice line belongs to. | Optional |
    | `product2Id` | InvoiceLine.product2Id | Identifier for the product that’s billed in this invoice line. | Optional |
    | `usageProductId` | InvoiceLine.usageProductId | Identifier for the usage-based product if this invoice line is for usage-based billing. | Optional |
    | `isUsageBasedInvoiceLine` | InvoiceLine.isUsageBasedInvoiceLine | Boolean value that indicates whether this invoice line is for a usage-based product (`true`) or not (`false`). | Optional |
    | `usageOverageQuantity` | InvoiceLine.usageOverageQuantity | Quantity of usage overage for this invoice line, if applicable. | Optional |
    | `unitOfMeasureId` | InvoiceLine.unitOfMeasureId | Identifier for the unit of measure for the product or service, such as each, kg, or lb. | Optional |
    | `description` | InvoiceLine.description | Description of the invoice line item with additional details. | Optional |

## Tax Record

Keep these considerations in mind when you specify a Tax record as the Graph attribute
type.

- The supported Graph attribute method is POST only.
- The associated standard object is InvoiceLineTax.
- The invoiceLineTax graph record must not include the `taxCalculationStatus` property value as `Pending`.

JSON example
:   ```
    {
        "referenceId": "refInvoiceLineTax",
        "record": {
            "attributes": {
                "type": "InvoiceLineTax",
                "method": "POST"
            },
            "taxTransactionNumber": "TX123456789",
            "taxAmount": 15.00,
            "taxRate": 0.08,
            "taxName": "Sales Tax",
            "taxCode": "TX-SALES",
            "taxEffectiveDate": "2024-01-01",
            "invoiceLine": "@{refInvoiceLine.id}",
            "taxDocumentNumber": "TAXDOC987654",
            "taxExemptAmount": 0.00,
            "description": "Exempt from VAT"
        }
    }
    ```
:   Table 3. Properties

    | NAME | Standard Object Field | Description | Required or Optional |
    | --- | --- | --- | --- |
    | `taxTransactionNumber` | InvoiceLineTax.taxTransactionNumber | Unique identifier of the tax transaction related to this invoice line tax. | Required |
    | `taxAmount` | InvoiceLineTax.taxAmount | Total tax amount applied to the invoice line. | Required |
    | `taxRate` | InvoiceLineTax.taxRate | Rate at which the tax is applied on the invoice line. | Required |
    | `taxName` | InvoiceLineTax.taxName | Name of the tax applied on the invoice line, such as Sales Tax or Value Added Tax (VAT). | Required |
    | `taxCode` | InvoiceLineTax.taxCode | Tax code that corresponds to the applied tax rate. | Required |
    | `taxEffectiveDate` | InvoiceLineTax.taxEffectiveDate | Effective date from which the tax rate applies. | Required |
    | `invoiceLine` | InvoiceLineTax.invoiceLine | Reference to the invoice line this tax record is associated with. | Required |
    | `taxDocumentNumber` | InvoiceLineTax.taxDocumentNumber | Document number associated with the tax transaction, such as tax return document or government filing number. | Required |
    | `taxExemptAmount` | InvoiceLine.billingAddressId | Billing address associated with this invoice line. | Required |
    | `description` | InvoiceLineTax.description | Additional details about the tax. | Optional |

## Shipping Address Record

Keep these considerations in mind when you specify a Shipping Address record as the Graph
attribute type.

- The supported Graph attribute method is POST only.
- The associated standard object is InvoiceAddressGroup.

JSON example
:   ```
    {
        "referenceId": "refShippingAddress",
        "record": {
            "attributes": {
                "type": "InvoiceAddressGroup",
                "method": "POST"
            },
            "street": "456 Elm St",
            "city": "Springfield",
            "postalCode": "62701",
            "state": "IL",
            "country": "USA",
            "longitude": "-89.6501",
            "latitude": "39.7817",
            "invoiceId": "@{refInvoice.id}"
        }
    }
    ```
:   Table 4. Properties

    | NAME | Standard Object Field | Description | Required or Optional |
    | --- | --- | --- | --- |
    | `invoiceId` | InvoiceAddressGroup.invoice | Unique identifier of the invoice associated with this shipping address. | Required |
    | `street` | InvoiceAddressGroup.street | Street address where the goods or services are shipped to. | Required |
    | `city` | InvoiceAddressGroup.city | City where the shipment is delivered. | Required |
    | `postalCode` | InvoiceAddressGroup.postalCode | Postal or ZIP code for the shipping address. | Required |
    | `state` | InvoiceAddressGroup.state | State or province of the delivery location. | Required |
    | `country` | InvoiceAddressGroup.country | Country where the shipment is delivered. | Required |
    | `longitude` | InvoiceAddressGroup.longitude | Geographic longitude of the shipping address location for mapping purposes. | Optional |
    | `latitude` | InvoiceAddressGroup.latitude | Geographic latitude of the shipping address location for mapping purposes. | Optional |

## Billing Address Record

Keep these considerations in mind when you specify a Billing Address record as the Graph
attribute type.

- The supported Graph attribute method is POST only.
- The associated standard object is InvoiceAddressGroup.

JSON example
:   ```
    {
        "referenceId": "refBillingAddress",
        "record": {
            "attributes": {
                "type": "InvoiceAddressGroup",
                "method": "POST"
            },
            "street": "789 Oak St",
            "city": "Los Angeles",
            "postalCode": "90001",
            "state": "CA",
            "country": "USA",
            "longitude": "-118.2437",
            "latitude": "34.0522",
            "invoiceId": "@{refInvoice.id}"
        }
    }
    ```
:   Table 5. Properties

    | NAME | Standard Object Field | Description | Required or Optional |
    | --- | --- | --- | --- |
    | `invoiceId` | InvoiceAddressGroup.invoice | Unique identifier of the invoice associated with this billing address. | Required |
    | `street` | InvoiceAddressGroup.street | Street address for billing purposes. | Required |
    | `city` | InvoiceAddressGroup.city | City for billing address. | Required |
    | `postalCode` | InvoiceAddressGroup.postalCode | Postal or ZIP code for the billing address. | Required |
    | `state` | InvoiceAddressGroup.state | State or province for the billing address. | Required |
    | `country` | InvoiceAddressGroup.country | Country for the billing address. | Required |
    | `longitude` | InvoiceAddressGroup.longitude | Geographic longitude of the billing address location for mapping purposes. | Optional |
    | `latitude` | InvoiceAddressGroup.latitude | Geographic latitude of the billing address location for mapping purposes. | Optional |
