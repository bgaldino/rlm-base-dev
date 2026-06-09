---
page_id: cml_variable_data_types.htm
title: Variable Data Types
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_variable_data_types.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Constraint Modeling Language
parent_page: cml_variables.htm
fetched_at: 2026-06-09
---

# Variable Data Types

Variables support multiple data types including boolean, date, decimal, and so on.
Variables without a domain definition may remain unbound, leading to errors.

| Data Type | Description | Defaulting Example |
| --- | --- | --- |
| boolean | Only true, false, or null can be assigned as a value. | `@(defaultValue="true") boolean isActive;` |
| date | A value that indicates a particular day, the same as local date in Java. | `date shipDate = ["2023-01-01", "2023-12-31"];` If there's no `defaultValue` specified, the variable defaults to the first value in the domain. See the [Constraints using Format Specifiers (%s, %d) and Dates example](./cml_core_concept_examples.htm.md "These examples illustrate core Constraint Modeling Language (CML) concepts including type, relationships, constraints, and so on."). |
| double(n) | A 64-bit number that includes a decimal point, the same as double in Java. | `double(2) percentage = [0.00..100.00];` If there's no defaultValue specified, the variable defaults to the first value in the domain. |
| decimal(n) | A fixed-point numeric value with n decimal places. Note: The decimal variable data type isn't supported for the quantity field in quote line items. Use the integer data type for the quantity field. | `decimal(2) TaxRate = 0.08;` |
| int | Integer. A 32-bit number that doesn't include a decimal point, the same as int in Java. | `@(defaultValue = "5") int defaultQty = [1..10];` If there's no `defaultValue` specified, the variable defaults to the first value in the domain. |
| string | Any set of characters surrounded by double quotes (") | `@(defaultValue = "Red") string color = ["Red", "Green", "Blue"];` If there's no `defaultValue` specified, the attribute defaults to the first value in the domain. |
| string[] | Used in multi-select picklists for the user to select more than one item from multiple options. For example, if a user selects "Red", "Green", and "Blue" values in a color picker, this variable holds those selected values. | `@(defaultValue = '["Red", "Green"]') string[] selectedColors;` If there's no `defaultValue` specified, the attribute picklist defaults to the first value in the domain. |
