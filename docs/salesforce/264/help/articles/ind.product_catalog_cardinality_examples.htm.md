---
article_id: ind.product_catalog_cardinality_examples.htm
title: Group Cardinality Examples
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_cardinality_examples.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pcm
parent_article: ind.product_catalog_group_cardinality.htm
fetched_at: 2026-09-04
---

# Group Cardinality Examples

To better understand how group cardinality works in Product Catalog Management, refer to these examples.

REQUIRED EDITIONS
View supported products and editions.

These examples demonstrate how the group cardinality and the product component relationship settings dictate how many products you can add to the run-time cart.

EXAMPLE Example 1

Group

Min Number of Components: 3
Max Number of Components: 5
 	Min Quantity	Max Quantity	Default Quantity	Is Component Required	Is Default Component
Child 1	1	20	4	No	No

This is an invalid configuration because the group requires at least three distinct components and the user can add only one distinct component in the run time.

EXAMPLE Example 2

Group

Min Number of Components: 3
Max Number of Components: 5
 	Min Quantity	Max Quantity	Default Quantity	Is Component Required	Is Default Component
Child 1	1	20	4	No	No
Child 2	1	20	4	No	No
Child 3	1	20	4	No	No
Child 4	1	20	4	No	No
Child 5	1	20	4	No	No
Child 6	1	20	4	No	No

All the child components here are distinct. This is a valid configuration if a minimum of three and a maximum of five child components are added to the cart during run time.

EXAMPLE Example 3

This example explains the scenario when the Minimum Number of Components and Maximum Number of Components fields are left blank.

Group

Min Number of Components: Null
Max Number of Components: Null

This is a valid configuration and users can add a child component to this group. When the Min Components field is left blank it implies that the minimum number of distinct components in the group can be zero. When the Max Components field is left blank it implies that the maximum number of distinct components in the group can be infinite.

EXAMPLE Example 4

Group

Min Number of Components: 3
Max Number of Components: 5
 	Min Quantity	Max Quantity	Default Quantity	Is Component Required	Is Default Component
Child 1	1	20	4	Yes	Yes
Child 2	1	20	4	Yes	Yes
Child 2	1	20	4	Yes	Yes
Child 3	1	20	4	Yes	Yes
Child 3	1	20	4	Yes	Yes
Child 4	1	20	4	Yes	Yes

This configuration violates the group cardinality because a user can only add a maximum of five distinct and required child components to the bundle.

Group Cardinality and Product Classification Component Cardinality

Here are a few examples that demonstrate how the group and product classification cardinalities determine how many products you can add in your cart at run time.

EXAMPLE Example 1

Group A cardinality:

Min Number of Components: 2
Max Number of Components: 2

Product Classification B cardinality:

Min Quantity: 1
Max Quantity: 5
Quantity: 2

Products based on Product Classification B:

Product 1
Product 2
Product 3
Product 4
Product 5

At run time, the user can select exactly two products out of the five, because the group cardinality allows a minimum and maximum of two product components. Let’s suppose the user selects Product 3 and Product 5 in the runtime.

The default quantity for Product 3 is two. However, the user can change the quantity of Product 3 to a minimum of one and a maximum of five. The user must select between one and five numbers of Product 3 products because the product classification cardinality allows a minimum of one and a maximum of five products.

The default quantity for Product 5 is two. However, the user can change the quantity of Product 5 to a minimum of one and a maximum of five. The user must select between one and five numbers of Product 5 products because the product classification cardinality allows a minimum of one and a maximum of five products.

EXAMPLE Example 2

Group X cardinality:

Min Number of Components: 2
Max Number of Components: 5

Product Classification YY cardinality:

Min Quantity: 2
Max Quantity: 4
Quantity: 3

Products based on Product Classification YY

ProductYY 1
ProductYY 2
ProductYY 3
ProductYY 4
ProductYY 5
ProductYY 6

At run time, the user can select between two and five products because the group cardinality allows a minimum of two and a maximum of five product components. Let’s suppose the user selects Product YY1 and Product YY4 in the runtime.

The default quantity for Product YY1 is three. However, the user can change the quantity of Product YY1 to a minimum of two and a maximum of four. The user must select between two and four numbers of Product YY1 products because the product classification cardinality allows a minimum of two and a maximum of four products.

The default quantity for Product YY4 is three. However, the user can change the quantity of Product YY4 to a minimum of two and a maximum of four. The user must select between two and four numbers of Product YY4 products because the product classification cardinality allows a minimum of two and a maximum of four products.
