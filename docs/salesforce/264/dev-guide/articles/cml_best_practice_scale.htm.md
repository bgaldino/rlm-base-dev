---
page_id: cml_best_practice_scale.htm
title: "Decimals and Doubles: Consider the Impact of Scale on Performance"
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_best_practice_scale.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: cml_cml_best_practices.htm
fetched_at: 2026-09-29
---

# Decimals and Doubles: Consider the Impact of Scale on Performance

Scale is the number of digits that follow the decimal point in a decimal or double.
    Consider its impact on performance before using decimals and doubles in expressions.

    

In a decimal or double, scale is the number of digits that follow the decimal point. Using
      decimals and doubles in expressions can cause performance problems due to the number of
      permutations.

    

In this example, myNumber is a double with a scale of 2. The value can be 0.00, 0.01, 0.02,
      all the way up to 2.99, which can impact constraint engine performance:

    

```
double(2) myNumber = [0..3];
```

    

In this example, myNumber is an integer. The value can only be 0, 1, 2 or 3, which has less
      impact on constraint engine performance:

    

```
int myNumber = [0..3];
```
