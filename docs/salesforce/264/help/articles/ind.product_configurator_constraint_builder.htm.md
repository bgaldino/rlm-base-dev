---
article_id: ind.product_configurator_constraint_builder.htm
title: Use Constraint Builder With Constraint Rules Engine
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_constraint_builder.htm&type=5&release=264
release: 264
release_name: Winter '27
area: configurator
parent_article: ind.product_configurator_advanced.htm
fetched_at: 2026-09-04
---

# Use Constraint Builder With Constraint Rules Engine

Use Constraint Builder to create constraint models that manage complex configuration and validation for your products. Constraint models describe real-world entities and define their relationships with one another. Constraint Builder uses constraints in addition to if-then rules to customize complex products quickly and accurately.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Growth license or the Revenue Cloud Advanced license
Constraint Builder Interfaces

To define a constraint model, you add constraints and rules. The Constraint Builder uses Constraint Modeling Language (CML), the domain-specific language of the Constraint Rules Engine, to represent the constraint model. To work in the Constraint Builder, you can choose between two interfaces:

In the Visual Builder, use point-and-click tools to define constraints and rules, without needing to work directly with code.
In the CML Editor, write and edit CML code to define constraints and rules. For more information on CML, see the Constraint Modeling Language (CML) User Guide.

You can work in either of the interfaces. You can also switch between the Visual Builder and the CML Editor as you work. For example, you can define constraints and rules in the Visual Builder, and then view the code in the CML Editor to make additional changes.

Considerations and Limitations

Keep these limitations and considerations in mind when defining constraint models.

The maximum execution time for constraints is 10 seconds.
Constraint models don't support datetime attributes.
Constraint models don't support product variants.
Constraint Builder only supports unicode letters, numeric characters, and underscores. Using other characters can cause errors.
Configurator with Constraint Rules Engine doesn't support decimal quantities. Rules or constraints defined with decimal quantities can't be enforced precisely, and rules that set quantities to decimal values can pass incorrect quantities to downstream processes. For example, rules like "If quantity > 1.5 then..." or "If... then quantity = 1.5" won't be processed accurately.
Create a Constraint Model
To create a constraint model, in the Constraint Models app, name the constraint model and specify a context definition.
