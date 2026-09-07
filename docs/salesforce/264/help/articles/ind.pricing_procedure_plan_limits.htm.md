---
article_id: ind.pricing_procedure_plan_limits.htm
title: Procedure Plan Limits
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_procedure_plan_limits.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pricing
parent_article: ind.pricing_procedure_plan_framework.htm
fetched_at: 2026-09-07
---

# Procedure Plan Limits

Don't stitch multiple pricing procedures together within a single procedure plan. Sequencing multiple procedures can result in data loss and calculation errors. If you need to configure multiple procedures sequentially, consider these limitations.

The Price Waterfall displays execution results for only the last pricing procedure in the sequence. Sales reps can't view the end-to-end history of a line item. The final waterfall view overwrites or loses access to the logic, calculations, and intermediate values from the first procedure, making it difficult to explain the final price derivation.
Derived pricing calculations don't capture the complete pricing context when a contributing product's calculation spans across multiple procedures. For example, a product receives a volume discount in Procedure 1 and an attribute-based discount in Procedure 2. If the Derived Price element is in Procedure 1, it calculates the price based only on the Net Unit Price available at the end of Procedure 1. The calculation ignores the attribute discount applied in Procedure 2 because context isn't shared between procedures.
For bundled products configured with an Inclusive Price, the instruction to skip pricing doesn't persist between procedures. In the first procedure, the Bundle Based Adjustment element sets the child item's list price to zero and skips further calculations. However, when the quote moves to the second procedure, the line item loses the flag to skip calculation. Consequently, the second procedure treats the child item as a standard line item and sometimes incorrectly applies manual discounts or other adjustments.

Workaround: Configure the second procedure to check if InclusivePrice is true and stop pricing for those lines.

When parallelization is enabled, the pricing procedure caches metadata about custom tag mappings during activation. If you modify custom tag mappings in a rule library version after a procedure is activated, deactivate and reactivate the procedure to refresh this metadata. Otherwise, the procedure might apply promotions incorrectly during execution.
