---
article_id: ind.approvals_preview_feature_limitations.htm
title: Preview Approvals Considerations
source_url: https://help.salesforce.com/s/articleView?id=ind.approvals_preview_feature_limitations.htm&type=5&release=264
release: 264
release_name: Winter '27
area: approvals
parent_article: ind.approvals_advanced_approvals_considerations.htm
fetched_at: 2026-11-23
---

# Preview Approvals Considerations

Keep these considerations in mind when working with Preview Approvals.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions where Advanced Approvals is enabled
You can use Preview Approvals only with the Autolaunched Flow Approval Process (No Trigger) flow type.
Steps that have entry conditions based on runtime or asynchronous evaluations, such as subflows in background steps, aren’t shown during preview. As a workaround, set mock output values for these evaluations in Flow Builder.
Preview Approvals treats all referenced steps as required dependencies and doesn’t distinguish between AND and OR conditions. For example, if a step is configured to start after Step A OR Step B, the preview shows it as dependent on both.
You can’t pass input variables to the flow manually during preview. If the flow requires input variables, configure default values for them in Flow Builder.
The preview doesn’t show the dependencies between approval steps that belong to different chains. However, the steps are shown in their sequential order.
If an internal error occurs during preview, verify that each stage has a valid exit path and the steps aren't assigned to approvers of type Resource.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.approvals_preview_feature_limitations.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
