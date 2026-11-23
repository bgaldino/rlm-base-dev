---
article_id: ind.pricing_procedure_plan_limits.htm
title: Procedure Plan Limits
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_procedure_plan_limits.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pricing
parent_article: ind.pricing_procedure_plan_framework.htm
fetched_at: 2026-11-23
---

# Procedure Plan Limits

Multiple pricing procedures can be stitched together within a single procedure plan. If you need to configure multiple procedures sequentially, consider these limitations.

The Price Waterfall displays execution results for only the last pricing procedure in the sequence. Sales reps can't view the end-to-end history of a line item. The final waterfall view doesn't carry over the logic, calculations, or intermediate values from earlier procedures, which can make it harder to explain how the final price was derived. Consider keeping related calculations within a single procedure.
A Derived Price element calculates using the pricing context available during its run time. It doesn't automatically pick up discounts applied in a later procedure. For example, if a product receives a volume discount in Procedure 1 and an attribute-based discount in Procedure 2, a Derived Price element placed in Procedure 1 calculates from the Net Unit Price at the end of Procedure 1 only, and won't reflect the Procedure 2 discount. Consider placing Derived Price element as late as possible in your procedure sequence, ideally in the final procedure. So they have access to the most complete set of applied adjustments.
For bundled products configured with an Inclusive Price, the instruction to skip pricing doesn't persist between procedures. In the first procedure, the Bundle Based Adjustment element sets the child item's list price to zero and skips further calculations. However, when the quote moves to the second procedure, the line item loses the flag to skip calculation. Consequently, the second procedure treats the child item as a standard line item and sometimes incorrectly applies manual discounts or other adjustments.

Workaround: Configure the second procedure to check if InclusivePrice is true and stop pricing for those lines.

When parallelization is enabled, the pricing procedure caches metadata about custom tag mappings during activation. If you modify custom tag mappings in a rule library version after a procedure is activated, deactivate and reactivate the procedure to refresh this metadata. Otherwise, the procedure might apply promotions incorrectly during execution.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.pricing_procedure_plan_limits.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
