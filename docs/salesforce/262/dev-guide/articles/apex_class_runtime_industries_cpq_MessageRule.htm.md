---
page_id: apex_class_runtime_industries_cpq_MessageRule.htm
title: MessageRule Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_MessageRule.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: apex_namespace_runtime_industries_cpq.htm
fetched_at: 2026-06-09
---

# MessageRule Class

Represents a message rule that is evaluated during product configuration. Message rules display informational, warning, or error messages to users based on configuration conditions.

## Namespace

[runtime\_industries\_cpq](./apex_namespace_runtime_industries_cpq.htm.md "The runtime_industries_cpq namespace provides classes and methods to search products or to manage products, catalogs, and categories.")

- **[MessageRule Constructor](./apex_class_runtime_industries_cpq_MessageRule.htm.md#apex_runtime_industries_cpq_MessageRule_constructors)**  
  Learn more about the constructor that's available with the MessageRule class.
- **[MessageRule Properties](./apex_class_runtime_industries_cpq_MessageRule.htm.md#apex_runtime_industries_cpq_MessageRule_properties)**  
  Contains properties to store message rule details from configuration rule evaluation.

## MessageRule Constructor

Learn more about the constructor that's available with the MessageRule
class.

The `MessageRule` class includes this
constructor.

- **[MessageRule(stiId, severity, messages)](./apex_class_runtime_industries_cpq_MessageRule.htm.md#apex_runtime_industries_cpq_MessageRule_ctor)**  
  Constructor to create a MessageRule instance with the specified STI ID, severity, and messages.

### MessageRule(stiId, severity, messages)

Constructor to create a MessageRule instance with the specified STI ID, severity, and messages.

#### Signature

`public MessageRule(String stiId, String severity, List<String> messages)`

#### Parameters

stiId
:   Type: String
:   The ID of the Sales Transaction Item (STI) associated with this message rule.

severity
:   Type: String
:   The severity level of the message (for example, Error, Warning, or Info).

messages
:   Type: List<String>
:   List of message strings to display to the user.

## MessageRule Properties

Contains properties to store message rule details from configuration rule evaluation.

The `MessageRule` class includes these
properties.

- **[messages](./apex_class_runtime_industries_cpq_MessageRule.htm.md#apex_runtime_industries_cpq_MessageRule_messages)**  
  Get the list of messages.
- **[severity](./apex_class_runtime_industries_cpq_MessageRule.htm.md#apex_runtime_industries_cpq_MessageRule_severity)**  
  Get the severity value.
- **[stiId](./apex_class_runtime_industries_cpq_MessageRule.htm.md#apex_runtime_industries_cpq_MessageRule_stiId)**  
  Get the ID of the sti.

### messages

Get the list of messages.

#### Signature

`public List<String> messages {get; set;}`

#### Property Value

Type: List<String>

### severity

Get the severity value.

#### Signature

`public String severity {get; set;}`

#### Property Value

Type: String

### stiId

Get the ID of the sti.

#### Signature

`public String stiId {get; set;}`

#### Property Value

Type: String
