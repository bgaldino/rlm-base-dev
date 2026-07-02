---
page_id: cml_external_variables.htm
title: External Variables
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_external_variables.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: cml_variables.htm
fetched_at: 2026-06-09
---

# External Variables

External variables are global Constraint Modeling Language (CML) variables defined
within a virtual CML type.

See virtual in [Type Annotations](./cml_type_annotations.htm.md "You can annotate types to add information. Type annotations are metadata applied to a type declaration to provide instructions to the constraint engine regarding how instances of that type should be handled, instantiated, or used in the configuration structure."). The values for external variables are usually set by the
environment that launches the constraint solver engine. Use external variables to import
runtime data from the context header (such as Quote or Sales Transaction) into the
configuration model, with the contextPath annotation to denote header fields, or with
tagName annotation to denote lineItem fields. See External Variable Annotations section.

If the external variable isn't mapped to any
external data source, it must have a default value. Otherwise, it may remain unbound and
cause errors.

Here's a basic declaration
syntax.

```
extern int MAX_VALUE = 9999;
extern decimal(2) threshold = 1.5;
```

## Example: Using External Variables with Context Path Annotation

In this example, the constraint engine needs access to the quote header (Sales Transaction)
field, which defines the shipping location to enforce region-specific compliance
requirements. The `contextPath` annotation is used to map
the field (`SalesTransaction.ShippingCountry`) to an
external CML variable (`ShippingCountry`).

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=revenue_lifecycle_management_dev_guide)

#### Note

The CML variable name can be different from the context path value.

```
// External variable declaration with context path annotation
@(contextPath = "SalesTransaction.ShippingCountry")
extern string ShippingCountry; // ShippingCountry Value is pulled from the Quote/Order header
```

See the full example in [Using ContextPath and tagName annotations](./cml_core_concept_examples.htm.md "These examples illustrate core Constraint Modeling Language (CML) concepts including type, relationships, constraints, and so on.").

## External Variable Annotations

Here are the details of external variable annotations.

| Annotation | Possible Value | Description |
| --- | --- | --- |
| contextPath | "SalesTransaction.<ST\_FIELD>", where the sales transaction field is pulled directly from the context definition. | References sales transaction values directly from their context definition, such as account name, sales transaction total, or address. The contextPath annotation can only be used for header fields.  To create a variable linked to a SalesTransactionItem, use the tagName annotation to reference context tags on SalesTransactionItem within a type. See tagName in [Variable Annotations](./cml_variable_annotations.htm.md "You can annotate variables with properties such as configurable, defaultValue, domainComputation, and relatedAttributes."). |
