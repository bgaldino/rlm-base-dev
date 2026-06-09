---
page_id: cml_variables.htm
title: Variables
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_variables.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Constraint Modeling Language
parent_page: cml_cml_core_concepts.htm
fetched_at: 2026-06-09
---

# Variables

Variables are the properties or characteristics defined within a type. Variables can hold
different types of data and can be calculated from other values.

- **[Variable Domains and Domain Restrictions](./cml_variable_domains_and_domain_restrictions.htm.md)**  
  A variable can have a fixed domain that defines a set of permitted values. You can specify the domain as a list of discrete values, a continuous range, or a combination.
- **[Variable Data Types](./cml_variable_data_types.htm.md)**  
  Variables support multiple data types including boolean, date, decimal, and so on. Variables without a domain definition may remain unbound, leading to errors.
- **[Mathematical Functions (Numerical Derivation)](./cml_mathematical_functions_numerical_derivation.htm.md)**  
  Mathematical functions and operators are used to calculate derived values based on arithmetic relationships between variables.
- **[String Variable Functions and Operators](./cml_string_variable_functions_and_operators.htm.md)**  
  Constraint Modeling Language (CML) provides string manipulation and conversion functions, and string comparison and validation operators.
- **[Variable Annotations](./cml_variable_annotations.htm.md)**  
  You can annotate variables with properties such as configurable, defaultValue, domainComputation, and relatedAttributes.
- **[External Variables](./cml_external_variables.htm.md)**  
  External variables are global Constraint Modeling Language (CML) variables defined within a virtual CML type.
