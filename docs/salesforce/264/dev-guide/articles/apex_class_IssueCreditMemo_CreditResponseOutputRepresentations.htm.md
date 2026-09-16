---
page_id: apex_class_IssueCreditMemo_CreditResponseOutputRepresentations.htm
title: CreditResponseOutputRepresentations Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_IssueCreditMemo_CreditResponseOutputRepresentations.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: apex_namespace_IssueCreditMemo.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# CreditResponseOutputRepresentations Class

Represents the result of a credit memo operation. Indicates success or failure and any additional information or message.

## Namespace

[IssueCreditMemo](./apex_namespace_IssueCreditMemo.htm.md)

## Usage

## Example

- 
**[CreditResponseOutputRepresentations Constructors](./apex_class_IssueCreditMemo_CreditResponseOutputRepresentations.htm.md#apex_IssueCreditMemo_CreditResponseOutputRepresentations_constructors)**  

- 
**[CreditResponseOutputRepresentations Properties](./apex_class_IssueCreditMemo_CreditResponseOutputRepresentations.htm.md#apex_IssueCreditMemo_CreditResponseOutputRepresentations_properties)**  

  

## CreditResponseOutputRepresentations Constructors

  
  
    
      

The `CreditResponseOutputRepresentations` class includes
        these constructors.

    

    
  

- 
**[CreditResponseOutputRepresentations(success, additionalInformation)](./apex_class_IssueCreditMemo_CreditResponseOutputRepresentations.htm.md#apex_IssueCreditMemo_CreditResponseOutputRepresentations_ctor)**  

Creates a response with the given success flag and additional information.

### CreditResponseOutputRepresentations(success, additionalInformation)

Creates a response with the given success flag and additional information.

#### Signature

`public CreditResponseOutputRepresentations(Boolean success, String additionalInformation)`

#### Parameters

**success**

: Type: Boolean

: Indicates whether the credit memo is issued successfully (`true`) or not (`false`).

**additionalInformation**

: Type: String

: Additional information or message, such as error details or confirmation.

  

## CreditResponseOutputRepresentations Properties

  
  
    
      

The `CreditResponseOutputRepresentations` class includes
        these properties.

    

    
  

- 
**[additionalInformation](./apex_class_IssueCreditMemo_CreditResponseOutputRepresentations.htm.md#apex_IssueCreditMemo_CreditResponseORs_additionalInformation)**  

Additional information or message, such as error details or confirmation.

- 
**[success](./apex_class_IssueCreditMemo_CreditResponseOutputRepresentations.htm.md#apex_IssueCreditMemo_CreditResponseOutputRepresentations_success)**  

Indicates whether the credit memo is issued successfully (true) or not     (false).

### additionalInformation

Additional information or message, such as error details or confirmation.

#### Signature

`public String additionalInformation {get; set;}`

#### Property Value

Type: String

### success

Indicates whether the credit memo is issued successfully (true) or not
    (false).

#### Signature

`public Boolean success {get; set;}`

#### Property Value

Type: Boolean
