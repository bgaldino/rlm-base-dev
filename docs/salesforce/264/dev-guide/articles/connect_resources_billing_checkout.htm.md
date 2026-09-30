---
page_id: connect_resources_billing_checkout.htm
title: Billing Checkout (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_billing_checkout.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_resources.htm
fetched_at: 2026-09-29
---

# Billing Checkout (POST)

Create a unified checkout transaction that generates billing schedules, an invoice, and an optional payment in a single request.

    
      

Use this API to process a checkout transaction for invoicing and payment. Specify account or customer details, line items, billing information, and payment details. You can also preview the invoice without committing the checkout transaction.

    

    

## Special Access Rules

      
      

You need the Billing Checkout access permission to use this API.

    

    

## Resource

      
      

```
/commerce/invoicing/invoices/collection/actions/checkout
```

    

    

## Resource Example

      
      

```
https://yourInstance.salesforce.com/services/data/v68.0/commerce/invoicing/invoices/collection/actions/checkout
```

    

    

## Available Version

      
      

68.0

    

    

## HTTP Methods

      
      

POST

    

    

## Request Body for POST

      
      

**JSON Example**

      

```
{
  "previewInvoice": false,
  "shouldCapturePayment": true,
  "isPartialPaymentAllowed": false,
  "accountId": "001xx0000004C90",
  "invoiceDate": "2026-09-01",
  "invoiceTargetDate": "2026-12-31",
  "currencyIsoCode": "USD",
  "amount": 1400.00,
  "billingContact": {
    "firstName": "Alex",
    "lastName": "Rivera",
    "email": "alex.rivera@example.com",
    "phone": "+1-415-555-0100"
  },
  "billingAddress": {
    "street": "415 Mission St",
    "city": "San Francisco",
    "state": "California",
    "stateCode": "CA",
    "country": "United States",
    "countryCode": "US",
    "postalCode": "94105"
  },
  "shippingAddress": {
    "street": "415 Mission St",
    "city": "San Francisco",
    "stateCode": "CA",
    "countryCode": "US",
    "postalCode": "94105"
  },
  "paymentDetails": {
    "paymentGatewayId": "0cgxx0000004C91",
    "idempotencyKey": "checkout-2026-09-01-abc123",
    "savedPaymentMethodDetails": {
      "merchantAccount": "0dmxx0000004C92",
      "gatewayToken": "tok_1PabcXYZ",
      "gatewayReference": "cus_ORef123",
      "type": "Card",
      "name": "Acme Corp Visa"
    }
  },
  "lineItems": [
    {
      "productName": "Platform Subscription",
      "transactionId": "TXN-PLATFORM-001",
      "quantity": 10,
      "unitPrice": 100.00,
      "netUnitPrice": 100.00,
      "lineTotal": 1000.00,
      "startDate": "2026-09-01",
      "endDate": "2027-08-31",
      "sellingModelType": "TermDefined",
      "periodBoundary": "DayOfPeriod",
      "billingDayOfMonth": 1,
      "billingTermUnit": "Month",
      "billingTerm": 12,
      "taxTreatmentId": "0cXxx0000004C94",
      "billingTreatmentId": "0cYxx0000004C95",
      "bundleProductDetails": [
        {
          "productName": "Premium Support Add-on",
          "associatedTransactionPricing": "IncludedInBundlePrice",
          "quantity": 10,
          "unitPrice": 200.00,
          "netUnitPrice": 200.00,
          "lineTotal": 200.00,
          "sellingModelType": "TermDefined",
          "periodBoundary": "DayOfPeriod",
          "billingDayOfMonth": 1,
          "billingTermUnit": "Month",
          "billingTerm": 12,
          "taxTreatmentId": "0cXxx0000004C94",
          "billingTreatmentId": "0cYxx0000004C95"
        }
      ],
      "ramps": [
        {
          "productId": "01txx0000004C93",
          "startDate": "2026-09-01",
          "endDate": "2027-02-28",
          "quantity": 10,
          "unitPrice": 100.00,
          "netUnitPrice": 100.00,
          "lineTotal": 500.00,
          "sellingModelType": "TermDefined",
          "periodBoundary": "DayOfPeriod",
          "billingDayOfMonth": 1,
          "billingTermUnit": "Month",
          "billingTerm": 6
        },
        {
          "productId": "01txx0000004C93",
          "startDate": "2027-03-01",
          "endDate": "2027-08-31",
          "quantity": 10,
          "unitPrice": 100.00,
          "netUnitPrice": 100.00,
          "lineTotal": 500.00,
          "sellingModelType": "TermDefined",
          "periodBoundary": "DayOfPeriod",
          "billingDayOfMonth": 1,
          "billingTermUnit": "Month",
          "billingTerm": 6
        }
      ]
    },
    {
      "productName": "Onboarding Fee",
      "quantity": 1,
      "unitPrice": 200.00,
      "netUnitPrice": 200.00,
      "lineTotal": 200.00,
      "sellingModelType": "OneTime",
      "billingTermUnit": "OneTime",
      "billingTerm": 1
    }
  ]
}
```

      

**JSON Example — Using an Existing Payment Record**

      

This example passes `paymentId` directly for an existing payment record, instead of `paymentDetails`.

      

```
{
  "accountId": "001SG00001QDo2kYAD",
  "currencyIsoCode": "USD",
  "amount": 60,
  "previewInvoice": false,
  "shouldCapturePayment": false,
  "paymentId": "0aQSG0000020WoL2AU",
  "lineItems": [
    {
      "productId": "01txx0000004C91",
      "quantity": 1,
      "unitPrice": 60.00,
      "netUnitPrice": 60.00,
      "lineTotal": 60.00
    }
  ]
}
```

      

**Properties**

      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `account​Id` | String | ID of the account placing the order. Use this or `customerDetails`. | Optional | 68.0 |
| `amount` | Double | Total amount to charge for this checkout transaction. | Required | 68.0 |
| `billing​Address` | [Address Input](./connect_requests_address_input.htm.md) | Customer’s billing address. Use this or `billingProfileId`. | Optional | 68.0 |
| `billing​Contact` | [Billing Contact Input](./connect_requests_billing_checkout_billing_contact_input.htm.md) | Billing customer details when `billingProfileId` isn’t provided. Creates the contact if it doesn’t exist. | Optional | 68.0 |
| `billing​Profile​Id` | String | ID of an existing billing profile. Use this or `billingAddress`. | Optional | 68.0 |
| `currency​Iso​Code` | String | The currency code of the transaction amount if your Salesforce org has multi-currency enabled. | Required | 68.0 |
| `customer​Details` | [Billing Checkout Customer Details Input](./connect_requests_billing_checkout_customer_details_input.htm.md) | Customer details used to create a customer when `accountId` isn’t provided. | Optional | 68.0 |
| `invoice​Date` | String | Date that appears on the generated invoice (YYYY-MM-DD). Defaults to the transaction date. | Optional | 68.0 |
| `invoice​Target​Date` | String | End date for the billing period to include on this invoice (YYYY-MM-DD). Creates a targeted invoice. | Optional | 68.0 |
| `is​Partial​Payment​Allowed` | Boolean | Indicates whether partial payment is allowed for this payment context (`true`) or not (`false`). The default value is `false`. | Optional | 68.0 |
| `line​Items` | [Billing Checkout Line Item Input](./connect_requests_billing_checkout_line_item_input.htm.md)[] | Array of products being purchased. | Required | 68.0 |
| `payment​Details` | [Billing Checkout Payment Details Input](./connect_requests_billing_checkout_payment_details_input.htm.md) | Raw payment details used to tokenize a new card or bank account. Use this or `paymentMethodId`. | Optional | 68.0 |
| `payment​Id` | String | ID of an existing payment record to associate with this checkout transaction. Not allowed when `shouldCapturePayment` is `true`, and not allowed together with `amount`. | Optional | 68.0 |
| `payment​Method​Id` | String | ID of a saved payment method. Use this or `paymentDetails`. | Optional | 68.0 |
| `preview​Invoice` | Boolean | If `true`, returns a preview of the invoice without committing the checkout transaction. | Optional | 68.0 |
| `shipping​Address` | [Address Input](./connect_requests_address_input.htm.md) | Customer’s shipping address. | Optional | 68.0 |
| `should​Capture​Payment` | Boolean | If `true`, captures the payment as part of the checkout transaction. | Optional | 68.0 |

    

    

## Response Body for POST

      
      

[Billing Checkout](./connect_responses_billing_checkout_output.htm.md)
