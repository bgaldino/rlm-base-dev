---
page_id: cml_best_practice_sequence.htm
title: "Sequence: Use the Sequence Variable Annotation to Specify the Order of Execution"
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_best_practice_sequence.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: cml_cml_best_practices.htm
fetched_at: 2026-09-29
---

# Sequence: Use the Sequence Variable Annotation to Specify the Order of Execution

Use the sequence variable annotation to specify the order in which the constraint engine
    sets values for a constraint model's attributes and relationships.

    

If a constraint model includes multiple attributes and relationships that should follow a
      certain order of execution, use the sequence variable annotation to specify the order. The
      constraint engine follows sequence designations in satisfying constraint requirements and
      resolving constraint violations.

    

In this example, for the Desktop type, the sequence annotation directs the constraint
      engine to set the default values for attributes in this order:

    
      
- Display: sequence=1

      
- Windows_Processor: sequence=2

      
- Display_Size: sequence=3

    

    

```
type Desktop {
    @(defaultValue = "1080p Built-in Display", sequence=1)
    string Display = ["1080p Built-in Display", "4k Built-in Display", "2k Built-in Display"];

    @(defaultValue = "15 Inch", sequence=3)
    string Display_Size = ["15 Inch", "24 Inch", "13 Inch", "27 Inch"];

    @(defaultValue = "i5-CPU 4.4GHz", sequence=2)
    string Windows_Processor = ["i5-CPU 4.4GHz", "i7-CPU 4.7GHz", "Intel Core i9 5.2 GHz"];

    constraint(Display == "1080p Built-in Display" && Display_Size == "15 Inch" -> Windows_Processor == "i7-CPU 4.7GHz");
}
```

    

For Desktop, Display is set to 1080p, Windows_Processor to i5-CPU, and Display_Size to 15
      Inch.

    

The constraint specifies that a type with Display of 1080p and Display_Size of 15 Inch must
      have a Windows_Processor of i7-CPU.

    

```
constraint(Display == "1080p Built-in Display" && Display_Size == "15 Inch" -> Windows_Processor == "i7-CPU 4.7GHz");
```

    

The Windows_Processor default value of i5-CPU for Desktop violates the constraint. In order
      to satisfy the constraint and resolve the violation, the constraint engine uses a different
      Display_Size for Desktop, such as 24 Inch.

    

If the user manually updates Display_Size for Desktop to 15 Inch in the Product
      Configurator, the constraint engine updates Windows_Processor to i7-CPU to satisfy the
      constraint.
