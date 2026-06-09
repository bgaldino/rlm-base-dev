---
page_id: cml_variable_domains_and_domain_restrictions.htm
title: Variable Domains and Domain Restrictions
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_variable_domains_and_domain_restrictions.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: cml_variables.htm
fetched_at: 2026-06-09
---

# Variable Domains and Domain Restrictions

A variable can have a fixed domain that defines a set of permitted values. You can
specify the domain as a list of discrete values, a continuous range, or a combination.

## Variable Domains and Domain Restrictions

A variable can have a fixed domain that defines a set of permitted values. You can specify the domain as:

- A list of discrete values
- A continuous range
- A combination of ranges and discrete values

For more information, see domainComputation in [Variable Annotations](./cml_variable_annotations.htm.md "You can annotate variables with properties such as configurable, defaultValue, domainComputation, and relatedAttributes.").

## Example

This example defines a `SwitchgearBay` type with three
variables, each having a fixed domain.

- `BayType` can be one of the specified string
  values.
- `Bay_Number` can be any integer from 1 through 9
  (inclusive).
- `Total_Power_Required_kW` can be any integer from 1
  through 100000 (inclusive).

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=revenue_lifecycle_management_dev_guide)

#### Note

For string (picklist) variables, if you don't specify a `defaultValue` annotation and don't define a default in the
Product Attribute Definition in Product Catalog Management (PCM), the configurator uses the
first value in the domain as the initial value. In the example, `BayType` defaults to `"load"`. To set a
different default, use the  `defaultValue` annotation on
the variable. To avoid inconsistent behavior at run time, use the same default value in CML
as the default value you define in PCM.

```
type SwitchgearBay {
  string BayType = ["load", "lv", "mv"];
  int Bay_Number = [1..9];
  int Total_Power_Required_kW = [1..100000];
}
```
