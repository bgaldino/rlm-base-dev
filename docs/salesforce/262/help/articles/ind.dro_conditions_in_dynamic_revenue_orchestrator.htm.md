---
article_id: ind.dro_conditions_in_dynamic_revenue_orchestrator.htm
title: Understand Execution Conditions for Order Fulfillment
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_conditions_in_dynamic_revenue_orchestrator.htm&type=5&release=262
release: 262
release_name: Summer '26
area: dro
fetched_at: 2026-05-12
---

# Understand Execution Conditions for Order Fulfillment

When you configure fulfillment plans, Dynamic Revenue Orchestrator directs you to create conditions that control when those fulfillment steps are executed.

REQUIRED EDITIONS
Available in: Enterprise, Unlimited, and Developer Editions

For example, set a condition so that a representative follows up by phone only if the customer lives in the same country. Or a condition that says that after a pause, fulfillment doesn’t continue until a credit check comes through.

When an entity in DRO requires, or allows, conditions to be set, it launches the Condition Builder pane.

Condition Builder Fields
Based OnBased On: Select either Order Line Items or Fulfillment Line Items. Your choice determines the characteristics that you can build the conditions on. If you want conditions based on both order line items and fulfillment line items, create two sets of conditions.
Condition Requirements: Select whether all the conditions must be met, any condition must be met, or create your own custom Boolean logic.
All Conditions Are Met (AND): Every condition that you add must be met, or the entity doesn't run.
Any Condition Is Met (OR): If a single condition is met, then the entity runs.
Custom Logic Is Met: Create your own logic by using Boolean principles.
Resource: The tags or attributes that are available for defining the conditions. The options are based on what you chose in the Based On field. Then choose the operator, such as Equals, and then a value.
EXAMPLE This image shows three conditions.
Condition #1: There's a fulfillment order line item tag called FulfillmentItemAction that equals Add.
Condition #2: There's a tag called OriginalQuantity that's greater than 100.
Condition #3: There's a tag called FulfillmentOrderID that doesn't equal 1221.

The Custom Condition Logic says (1 OR 2) AND 3. That means that condition #3 must be met, and that either condition #1 or #2, or both, must be met.

Let's look at some possible examples after an order is submitted.

Order #1:

FulfillmentItemAction equals Add. Condition one is met.
OriginalQuantity equals 150. Condition two is met.
FulfillmentOrderID is 1221. Condition three isn't met. The condition requires that FulfillmentOrderID type is something other than 1221.

Because condition #3 isn't met, the set of conditions isn't met, and the entity associated with this rule doesn't run.

Order #2:
FulfillmentItemAction tag equals Add. Condition one is met.
OriginalQuantity equals 90. Condition two isn't met. The condition requires the value to be greater than 100.
FulfillmentOrderID is 1000. Condition three is met. The condition requires the value type to be anything except 1221, and it is.

This set of conditions is met according to the custom logic and the entity associated with this rule runs.
