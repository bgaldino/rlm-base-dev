---
page_id: apex_class_RevSignaling_ProcedurePlan.htm
title: ProcedurePlan Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_RevSignaling_ProcedurePlan.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: apex_namespace_RevSignaling.htm
fetched_at: 2026-06-09
---

# ProcedurePlan Class

Represents the instance of the current pricing procedure plan that you're working
on.

## Namespace

[RevSignaling](./apex_namespace_RevSignaling.htm.md "The RevSignaling Namespace includes properties and methods to extend the standard procedure plan implementation through custom logic. Using this extension support, you can tailor implementations to your unique requirements.")

- **[ProcedurePlan Properties](./apex_class_RevSignaling_ProcedurePlan.htm.md#apex_RevSignaling_ProcedurePlan_properties)**  
  Learn more about the properties that are available with the ProcedurePlan class.

## ProcedurePlan Properties

Learn more about the properties that are available with the ProcedurePlan
class.

The `ProcedurePlan` class includes these properties.

- **[prevStepOutput](./apex_class_RevSignaling_ProcedurePlan.htm.md#apex_RevSignaling_ProcedurePlan_prevStepOutput)**  
  Output of the previous step that's executed and passed to the next step.

### prevStepOutput

Output of the previous step that's executed and passed to the next step.

#### Signature

`public Map<String,ANY> prevStepOutput {get; set;}`

```
RevSignaling.ProcedurePlan, prevStepOutput
```

#### Property Value

Type: Map<String,Object>
