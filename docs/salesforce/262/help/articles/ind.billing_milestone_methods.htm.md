---
article_id: ind.billing_milestone_methods.htm
title: Define Billing Milestones
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_milestone_methods.htm&type=5
release: "262"
release_name: "Summer '26"
fetched_at: "2026-05-11"
area: billing
parent_article: ind.billing_milestone_plans.htm
license_required: Revenue Cloud Billing
notes: |
  This article confirms Module 2 v2's two-method framing for milestone setup:
    - Method 1 = BTI templates on the Billing Treatment (auto-generates Plan + Items at order activation).
    - Method 2 = manual Billing Milestone Plan + Plan Items for a specific order product.
---

# Define Billing Milestones

Milestone billing is a flexible billing method where customers are billed at specific project checkpoints.

## Required Editions

Available in: Lightning Experience.

Available in: Enterprise, Performance, Unlimited, and Developer Editions with the **Revenue Cloud Billing** license. Contact your Salesforce account executive for more information.

## Methods to Create Billing Milestone Plans

Create billing milestone plans and milestone plan items from billing treatments and apply them to one or more products.

You can also create a billing milestone plan directly for an order product when the milestone requirement is specific to that product.

### Method 1: Configure Billing Milestones Using Billing Treatments (`ind.billing_milestone_treatment_and_item_create.htm`)

Create billing milestone plans and billing milestone plan items from billing treatment and billing treatment items and apply them to one or more products. This method is ideal when multiple products follow the same milestone billing pattern. You can edit the billing milestone plans for individual order products without affecting the billing treatment.

### Method 2: Create Billing Milestone Plans and Plan Items

Create billing milestone plans, and then create billing milestone plan items to specify how billings are scheduled based on the completion of specific project milestones throughout the lifecycle of the order product.

---

*Captured via the release-enablement skill's Chrome MCP shadow-DOM walker pattern. Body text is verbatim from the Salesforce Help portal as of the `fetched_at` date in the frontmatter.*
