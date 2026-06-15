---
article_id: ind.approvals_preview_feature_limitations.htm
title: Preview Approvals Considerations
source_url: https://help.salesforce.com/s/articleView?id=ind.approvals_preview_feature_limitations.htm&type=5&release=262
release: 262
release_name: Summer '26
area: approvals
fetched_at: 2026-05-12
---

# Preview Approvals Considerations

Keep these considerations in mind when working with Preview Approvals.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions where Advanced Approvals is enabled
You can use Preview Approvals only with the Autolaunched Flow Approval Process (No Trigger) flow type.
Steps that have entry conditions based on runtime or asynchronous evaluations, such as subflows in background steps, aren’t shown during preview. As a workaround, set mock output values for these evaluations in Flow Builder.
Preview Approvals treats all referenced steps as required dependencies and doesn’t distinguish between AND and OR conditions. For example, if a step is configured to start after Step A OR Step B, the preview shows it as dependent on both.
You can’t pass input variables to the flow manually during preview. If the flow requires input variables, configure default values for them in Flow Builder.
The preview doesn’t show the dependencies between approval steps that belong to different chains. However, the steps are shown in their sequential order.
If an internal error occurs during preview, verify that each stage has a valid exit path and the steps aren't assigned to approvers of type Resource.
