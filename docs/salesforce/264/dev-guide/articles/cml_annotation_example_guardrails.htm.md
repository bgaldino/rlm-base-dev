---
page_id: cml_annotation_example_guardrails.htm
title: guardrails Annotation
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_annotation_example_guardrails.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: cml_annotation_examples.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# guardrails Annotation

guardrails is a CML annotation that prevent the constraint engine from changing
    specified attributes or relations when it resolves the constraint.

    
      

      
      
      

      

      

      

      
      

      

      

      
      

      

      

      
      

      

- 
- 

      

      

| Annotation | `guardrails` |
| --- | --- |
| Applicable to | Constraint |
| Value Type/Values | String. A comma-separated list of the attribute or relation names to protect. |
| Description | Prevents the constraint engine from altering the listed attributes or relations to satisfy the constraint. Defines protections at the constraint level instead of on individual attributes and relations, which avoids conflicts with other constraints that share the same elements. When you guard an attribute, the engine can't change its domain values. When you guard a relation, the engine can't change its cardinality. |

    

    

## Example 1: Guard an Attribute

      
      

In this generator set model, the UL 2200 compliance constraint requires a secondary voltage
        of 600V or less. The `Voltage` attribute is guarded, so
        the engine can't change its domain values to satisfy the constraint.

      

```
type GeneratorSet : LineItem {
    @(configurable = false)
    int requiredKW = [101..10000];
    string Voltage = ["220/380", "240/416", "277/480", "7976/13800"];
    string standardsAndCompliance = ["Certification-CSA", "Listing-UL 2200"];

    int Voltage3 = strtoint(regexpreplace(Voltage, VOLTAGE_REGEX, "$2"), 0);

    // Guard Voltage so the engine resolves the rule by adjusting the
    // compliance standard, not the domain values of Voltage.
    @(guardrails = "Voltage")
    constraint(standardsAndCompliance == "Listing-UL 2200" -> Voltage3 <= 600,
       "The UL 2200 standard covers stationary engine generator assemblies rated at 600 volts or less.");
}
```

    

    

## Example Description and Configurator Result

      
      

In example 1, the `guardrails` annotation set to
          "`Voltage`". As a result, if the user selects
        the "`Listing-UL 2200`" standard, the engine
        can't change the domain values of the `Voltage`
        attribute to resolve the conflict. Instead, the engine either satisfies the constraint by
        changing an unguarded element, such as `standardsAndCompliance`, or displays a conflict error message. Without the
          `guardrails` annotation, the engine restricts the
        domain values of `Voltage` to satisfy the constraint.
