---
page_id: cml_business-centric_cml_guidelines_quantity_and_aggregation_fun.htm
title: Business-Centric Constraint Modeling Language (CML) Guidelines
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_business-centric_cml_guidelines_quantity_and_aggregation_fun.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Constraint Modeling Language
parent_page: cml_what_is_constraint_modeling_language.htm
fetched_at: 2026-06-09
---

# Business-Centric Constraint Modeling Language (CML) Guidelines

Constraint Modeling Language (CML) must accurately calculate the total sum or aggregate
of specific attributes like quantity or userCount across child components, especially in complex
configurations requiring group-level aggregation

The main modeling obstacles when performing aggregation in CML involve:

- Initialization Errors: Preventing runtime errors, such as `NullPointerException`, which can occur if derived aggregate attributes lack
  explicit domains.
- Circular Dependencies: Avoiding calculation loops where the parent and children mutually rely on
  aggregated totals, often involving the `total()`
  function. If these loops are not broken, the aggregated variable becomes "not
  bound", which causes the solution to fail.

## User Workflow

As a sales representative, when I am configuring a bundle product in the Configurator window, I modify the quantities or specific attributes of the individual child components. I expect the constraint engine to immediately and accurately calculate the overall aggregated totals for the parent product, such as the totalItemCount or sumOfUsers.

- **[Business-Centric CML Examples](./cml_business_centric_cml_examples.htm.md)**  
  These Constraint Modeling Language (CML) structures implement quantity aggregation and resolve calculation dependencies.
