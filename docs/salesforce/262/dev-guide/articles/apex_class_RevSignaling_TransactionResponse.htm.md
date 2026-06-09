---
page_id: apex_class_RevSignaling_TransactionResponse.htm
title: TransactionResponse Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_RevSignaling_TransactionResponse.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: apex_namespace_RevSignaling.htm
fetched_at: 2026-06-09
---

# TransactionResponse Class

Represents the transaction response from the signaling Apex processor.

## Namespace

[RevSignaling](./apex_namespace_RevSignaling.htm.md "The RevSignaling Namespace includes properties and methods to extend the standard procedure plan implementation through custom logic. Using this extension support, you can tailor implementations to your unique requirements.")

- **[TransactionResponse Properties](./apex_class_RevSignaling_TransactionResponse.htm.md#apex_RevSignaling_TransactionResponse_properties)**  
  Learn more about the properties that are available with the TransactionResponse class.

## TransactionResponse Properties

Learn more about the properties that are available with the TransactionResponse
class.

The `TransactionResponse` class includes these
properties.

- **[message](./apex_class_RevSignaling_TransactionResponse.htm.md#apex_RevSignaling_TransactionResponse_message)**  
  Get the message from the transaction response.
- **[status](./apex_class_RevSignaling_TransactionResponse.htm.md#apex_RevSignaling_TransactionResponse_status)**  
  Get the status of the request from the transaction response.

### message

Get the message from the transaction response.

#### Signature

`public String message {get; set;}`

```
RevSignaling.TransactionResponse, message
```

#### Property Value

Type: String

### status

Get the status of the request from the transaction response.

#### Signature

`public RevSignaling.TransactionStatus status {get; set;}`

```
RevSignaling.TransactionResponse, status
```

#### Property Value

Type: [RevSignaling.TransactionStatus](./apex_enum_RevSignaling_TransactionStatus.htm.md "Specifies the status of the transaction request.")
