---
page_id: apex_namespace_RevSignaling.htm
title: RevSignaling Namespace
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_namespace_RevSignaling.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_apex_reference.htm
fetched_at: 2026-06-09
---

# RevSignaling Namespace

The RevSignaling Namespace includes properties and methods to extend the standard
procedure plan implementation through custom logic. Using this extension support, you can tailor
implementations to your unique requirements.

## Usage

To use this namespace, enable the **Procedure Plan Orchestration for
Pricing** toggle from the Revenue Settings page from Setup.

The `RevSignaling` namespace includes these classes.

- **[ProcedurePlan Class](./apex_class_RevSignaling_ProcedurePlan.htm.md#apex_class_RevSignaling_ProcedurePlan)**  
  Represents the instance of the current pricing procedure plan that you're working on.
- **[SignalingApexProcessor Interface](./apex_interface_RevSignaling_SignalingApexProcessor.htm.md#apex_interface_RevSignaling_SignalingApexProcessor)**  
  Defines the context-driven orchestration logic based on procedure plan instance and contextual instance.
- **[TransactionRequest Class](./apex_class_RevSignaling_TransactionRequest.htm.md#apex_class_RevSignaling_TransactionRequest)**  
  Represents the transaction request to the signaling Apex processor.
- **[TransactionResponse Class](./apex_class_RevSignaling_TransactionResponse.htm.md#apex_class_RevSignaling_TransactionResponse)**  
  Represents the transaction response from the signaling Apex processor.
- **[TransactionStatus Enum](./apex_enum_RevSignaling_TransactionStatus.htm.md)**  
  Specifies the status of the transaction request.
