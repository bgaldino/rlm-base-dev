---
page_id: cml-types
title: Types
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/cml-types.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Configurator
parent_page: cml-cml-core-concepts
legacy_page_id: cml_types.htm
fetched_at: 2026-11-25
---

# Types

In Constraint Modeling Language (CML), you define types to represent entities or objects in the model. Types are the foundational building blocks of CML. A type encapsulates the property, relationships, constraint, and rules for the entity.

A type is similar to a class in object-oriented programming. You can define relationships that represent associations between different types. See [Relationships](./cml-relationships.md).

**Note:**

To define a constraint for a child product in a bundle, you must include the entire bundle in the constraint model. For example, if you define a constraint for a laptop, and the laptop is a child product in the Laptop Pro Bundle, you must include the Laptop Pro Bundle in the constraint model for the constraint on the laptop to run.

**Note:**

Product variants aren’t supported in constraint models.

## Generic Structure of a Type

This table explains the generic structure of types with examples.

| Element | Purpose | Example |
| --- | --- | --- |
| Declaration | Defines the entity name, optionally preceded by annotations and optionally followed by inheritance, if applicable. | `type Product {}` `Or optionally: @annotation_name("annotation parameters") type Product: BaseProduct {}`. |
| Variables (Attributes) | Defines the properties or characteristics of the entity, including data type and domain. | `int requiredKW = [101..10000]; string color = ["Red", "Blue"];` |
| Relations | Defines one-to-many associations with other types, specifying cardinality (the quantity range) and optionally, the configuration order. | `relation items: LineItem[1..10] {}`. |
| Constraints and Rules | Enforces business logic and restrictions that must be satisfied by the entity’s variables and relationships. | `constraint(condition); require(condition, items [type]);` |

## Example: Basic Type Declaration with Variables

This example shows the declaration of the main `GeneratorSet` type. It defines several core attributes (variables) that characterize the product.

```
type GeneratorSet{
// Declaration only (inherits LineItem properties)
// Attributes with explicit domains
int requiredKW = [101..10000];
string Voltage = ["220/380", "240/416", "255/440", "277/480", "347/600", "2400/4160", "7200/12470", "7621/13200", "7976/13800];
string DutyRating = ["Prime Power (PRP)", "Continuous Power (COP)", "Data Center Continuous (DCC)", "Emergency Standby Power (ESP)"];
}
```

- 

**[Type Hierarchies](./cml-type-hierarchies.md)**

Constraint Modeling Language (CML) supports inheritance and overriding, which allow you to create hierarchies between types. By establishing these hierarchies, constraint models become more modular and efficient.

- 

**[Type Annotations](./cml-type-annotations.md)**

You can annotate types to add information. Type annotations are metadata applied to a type declaration to provide instructions to the constraint engine regarding how instances of that type should be handled, instantiated, or used in the configuration structure.

- 

**[Group Type](./cml-group-type.md)**

In Constraint Modeling Language (CML), a Group Type is used to logically containerize related components within a bundle configuration, primarily when product component groups are imported from Product Catalog Management (PCM).

- 

**[Define Constraints for Quote Groups, Ramps, and Ramp Segments](./cml-quote-group-ramp-segment-constraints.md#define-constraints-for-quote-groups-ramps-and-ramp-segments)**

Apply rules to quote groups, ramps, and ramp segments by using the SalesTransactionItemGroup context tag. Assign a groupby value to messages defined in Constraint Rules Engine to include the messages in custom grouping strategies.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/cml-types.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
