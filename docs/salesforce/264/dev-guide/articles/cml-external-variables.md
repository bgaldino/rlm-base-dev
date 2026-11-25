---
page_id: cml-external-variables
title: External Variables
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/cml-external-variables.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Configurator
parent_page: cml-variables
legacy_page_id: cml_external_variables.htm
fetched_at: 2026-11-25
---

# External Variables

External variables are global Constraint Modeling Language (CML) variables defined within a virtual CML type.

See virtual in [Type Annotations](./cml-type-annotations.md). The values for external variables are usually set by the environment that launches the constraint solver engine. Use external variables to import runtime data from the context header (such as Quote or Sales Transaction) into the configuration model, with the contextPath annotation to denote header fields, or with tagName annotation to denote lineItem fields. See External Variable Annotations section.

If the external variable isn’t mapped to any external data source, it must have a default value. Otherwise, it may remain unbound and cause errors.

Here’s a basic declaration syntax.

```
extern int MAX_VALUE = 9999;
extern decimal(2) threshold = 1.5;
```

## Example: Using External Variables with Context Path Annotation

In this example, the constraint engine needs access to the quote header (Sales Transaction) field, which defines the shipping location to enforce region-specific compliance requirements. The `contextPath` annotation is used to map the field (`SalesTransaction.ShippingCountry`) to an external CML variable (`ShippingCountry`).

**Note:**

The CML variable name can be different from the context path value.

```
// External variable declaration with context path annotation
@(contextPath = "SalesTransaction.ShippingCountry")
extern string ShippingCountry; // ShippingCountry Value is pulled from the Quote/Order header
```

See the full example in [Using ContextPath and tagName annotations](./cml-core-concept-examples.md).

## External Variable Annotations

Here are the details of external variable annotations.

| Annotation | Possible Value | Description |
| --- | --- | --- |
| contextPath | ”SalesTransaction.<ST_FIELD>”, where the sales transaction field is pulled directly from the context definition. | References sales transaction values directly from their context definition, such as account name, sales transaction total, or address. The contextPath annotation can only be used for header fields. To create a variable linked to a SalesTransactionItem, use the tagName annotation to reference context tags on SalesTransactionItem within a type. See tagName in [Variable Annotations](./cml-variable-annotations.md). |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/cml-external-variables.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
