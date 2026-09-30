---
page_id: cml_best_practice_calculations.htm
title: "Calculating Values: Put Calculations Inside of Constraints"
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_best_practice_calculations.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: cml_cml_best_practices.htm
fetched_at: 2026-09-29
---

# Calculating Values: Put Calculations Inside of Constraints

To calculate a value, put the calculation inside of a constraint instead of in an inline
    expression.

    

To calculate a value, put the calculation inside of a constraint, instead of in an inline
      expression.

    

For example, to calculate area, use this constraint:

    

```
constraint(area == length * width)
```

    

Avoid this example, which calculates the area with an inline expression, and can impact
      performance:

    

```
area = length * width.
```
