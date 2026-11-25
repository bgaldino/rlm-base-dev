---
page_id: cml-type-hierarchies
title: Type Hierarchies
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/cml-type-hierarchies.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Configurator
parent_page: cml-types
legacy_page_id: cml_type_hierarchies.htm
fetched_at: 2026-11-25
---

# Type Hierarchies

Constraint Modeling Language (CML) supports inheritance and overriding, which allow you to create hierarchies between types. By establishing these hierarchies, constraint models become more modular and efficient.

## How Hierarchies Function

- Inheritance: This mechanism enables a specialized child type to automatically share common variables (attributes) and relationships defined in its parent type. By inheriting from a base type, child types don’t need to redefine shared properties, which ensures consistency across the model.

- Overriding: While child types inherit the structure of the parent, they can override or specialize those properties. For example, a parent type might define a variable with a broad range of possible values, while a child type overrides that variable with a fixed value specific to that individual product.

## Practical Examples of Hierarchy

- 

Simple Product Extension: A `BaseProduct` might define an `id` and `name`. A `PhysicalProduct` can then inherit from `BaseProduct` to gain those fields while adding its own unique characteristics, such as `weight` or `color`.

- 

Multi-Level Nesting: Hierarchies can extend through multiple layers. For instance, a `Room` type can be the parent to a `Bedroom` type, and a `MasterBedroom` can further inherit from the `Bedroom` type, carrying all properties down the chain.

- 

Abstract Base Models: In complex configurations such as a `GeneratorSet`, a parent type such as `GeneralModel` defines the necessary attributes (such as `powerKW` and `dB`), while specific child types such as `GeneralModel900` or `GeneralModel1200` inherit those attributes and override them with their specific ratings.

**Note:**

To define a relationship with an abstract type, associate the abstract type with at least one product. If an abstract type declares a relationship when it isn’t associated with a product, it causes a missing association error. Define relationships on concrete child types instead.

## Core Benefits

By establishing these hierarchies, constraint models become more modular and efficient. You can create header-level declarations and base types to serve as a foundation for the entire model, allowing you to reference reusable components multiple times rather than writing redundant code for every product variation. This structural organization allows the constraint engine to effectively enforce business logic and validate configurations across all related types.

## Example 1: Simple Product Extension

In this pattern, a specialized type inherits from a broader base type. In the provided generator set model, the `GeneratorSet` type inherits from `LineItem`, gaining any properties defined at the line-item level while adding its own specific configuration fields like `requiredKW` and `Voltage`.

```
// The ultimate base type in the system
type LineItem;
// Child type extending LineItem with generator-specific attributes
type GeneratorSet : LineItem {
int requiredKW = [101..10000];
string Voltage = ["220/380", "240/416", "255/440"];
string DutyRating;
}
```

## Example 2: Multi-Level Nesting

CML supports hierarchies with multiple layers of depth. In this example, properties flow from the top-level `LineItem` down to the `GeneratorSet`, and finally to a highly specialized `EmergencyGenerator`. Each level inherits all attributes from the levels above it.

```
type LineItem;
// Level 2: Adds basic generator capacity attributes
type GeneratorSet : LineItem {
int requiredKW = [101..10000];
decimal(2) surgeLoadKW = requiredKW * 1.25; // Calculation shared down the chain
}
// Level 3: Specialized version inheriting everything from GeneratorSet and LineItem
type EmergencyGenerator : GeneratorSet {
// Automatically inherits requiredKW and surgeLoadKW
string DutyRating = "Emergency Standby Power (ESP)"; // Specific fixed rating
}
```

## Example 3: Abstract Base Models (Polymorphism & Overriding)

This pattern uses an abstract type as a structural blueprint. Specific components (the “General Models”) inherit from this blueprint and override its generic attributes with fixed, real-world ratings.

```
// Base model acting as a blueprint for all engine options
type GeneralModel{
int powerKW = [100..2000]; // Broad domain
int dB = [60..100];
}
// Specific product type that overrides parent domains with fixed values
type GeneralModel900 : GeneralModel {
int powerKW = 900; // Overrides broad range with exact value
int dB = 78;
}
// Another specialized model with different fixed properties
type GeneralModel1500 : GeneralModel {
int powerKW = 1500;
int dB = 83;
}
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/cml-type-hierarchies.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
