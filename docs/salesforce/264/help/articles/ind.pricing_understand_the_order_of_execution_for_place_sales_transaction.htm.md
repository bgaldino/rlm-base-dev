---
article_id: ind.pricing_understand_the_order_of_execution_for_place_sales_transaction.htm
title: Understand the Order of Execution for Place Sales Transaction
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_understand_the_order_of_execution_for_place_sales_transaction.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pricing
parent_article: ind.pricing_procedure_plan_framework.htm
fetched_at: 2026-09-07
---

# Understand the Order of Execution for Place Sales Transaction

When you create or update a quote or order using the Place Sales Transaction API, Revenue Management (formerly Revenue Cloud)processes the request through a defined order of execution. This order describes how configuration, pricing, Apex hooks, and automation run during transaction processing. Understanding this order helps you determine where pricing logic runs and how context data is processed when using Place Sales Transaction.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Advanced license.

When Place Sales Transaction processes a request, Revenue Management performs these steps in sequence.

Saves the sales transaction header.
Executes triggers associated with the transaction header.
Synchronizes supported context data back into the transaction context when context data is included in the request payload.
Hydrates the transaction with data required for configuration and pricing.
Applies applicable configuration logic to the transaction.
Resolves Amend, Renew, and Cancel (ARC) data required for the transaction.
Validates the transaction using ARC validation rules.
IMPORTANT ARC validation runs before the pre-pricing Apex hook. If you use Apex hooks to modify fields such as Start Date or Quantity, those changes bypass ARC validation and can produce unexpected results. To ensure proper validation, update fields like Date and Quantity in the request payload before calling Place Sales Transaction.
Performs pricing.
Runs the pre-pricing Apex hook, if defined.
Runs pricing logic.
Runs the post-pricing Apex hook, if defined.
Persists data from the transaction context.
Executes triggers for affected records.
Synchronizes supported context data back into the response when context data is included in the request payload.
Executes record-triggered flows and other custom logic based on the persisted data.
