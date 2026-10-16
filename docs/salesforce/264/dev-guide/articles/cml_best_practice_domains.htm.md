---
page_id: cml_best_practice_domains.htm
title: "Variable Domains: Keep Domains as Small as Possible"
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_best_practice_domains.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: cml_cml_best_practices.htm
fetched_at: 2026-09-29
---

# Variable Domains: Keep Domains as Small as Possible

A variable domain is the set of all possible values that the variable can take. Keep
    domains as small as possible to reduce the combinations that the constraint engine
    tests.

    

A variable domain is the set of all possible values that the variable can take. In this
      example, the variable color has a domain with three values:

    

```
string color = ["Red", "Yellow", "Green"];
```

    

The larger the domain, the more possible values for the variable, which means more
      combinations for the engine to test. A large domain can impact performance and lead to
      slower searches, errors, or unexpected behaviors.
