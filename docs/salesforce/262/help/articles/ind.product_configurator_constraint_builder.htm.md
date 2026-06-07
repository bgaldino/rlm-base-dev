---
article_id: ind.product_configurator_constraint_builder.htm
title: Use Constraint Builder With Constraint Rules Engine
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_constraint_builder.htm&type=5&release=262
release: 262
release_name: Summer '26
area: configurator
fetched_at: 2026-05-12
---

# Use Constraint Builder With Constraint Rules Engine

Use Constraint Builder to create constraint models that manage complex configuration and validation for your products. Constraint models describe real-world entities and define their relationships with one another. Constraint Builder uses constraints in addition to if-then rules to customize complex products quickly and accurately.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license

To define a constraint model, you add constraints and rules. The Constraint Builder uses Constraint Modeling Language (CML), the domain-specific language of the Constraint Rules Engine, to represent the constraint model. To work in the Constraint Builder, you can choose between two interfaces:

In the Visual Builder, use point-and-click tools to define constraints and rules, without needing to work directly with code.
In the CML Editor, write and edit CML code to define constraints and rules. For more information on CML, see the Constraint Modeling Language (CML) User Guide.

You can work in either of the interfaces. You can also switch between the Visual Builder and the CML Editor as you work. For example, you can define constraints and rules in the Visual Builder, and then view the code in the CML Editor to make additional changes.

Keep these considerations in mind when defining constraint models.

The maximum execution time for constraints is 10 seconds.
Constraint models don't support datetime attributes.
Constraint models don't support product variants.
Constraint Builder only supports unicode letters, numeric characters, and underscores. Using other characters can cause errors.
Create a Constraint Model
To create a constraint model, in the Constraint Models app, name the constraint model and specify a context definition.
