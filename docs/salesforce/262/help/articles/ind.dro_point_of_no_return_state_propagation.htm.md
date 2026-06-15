---
article_id: ind.dro_point_of_no_return_state_propagation.htm
title: Point of No Return State Propagation
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_point_of_no_return_state_propagation.htm&type=5&release=262
release: 262
release_name: Summer '26
area: dro
fetched_at: 2026-05-12
---

# Point of No Return State Propagation

After an order item reaches Point of No Return (PONR), you can’t cancel or amend the order. When a PONR-marked fulfillment step transitions to an In Progress status, the PONR state change applies to the related commercial and technical products within the bundle, depending on the product type.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Agentforce Revenue Management where Dynamic Revenue Orchestrator is enabled

Here’s how the PONR state propagates to the associated items within the product bundle.

PRODUCT ITEM TYPE IN PONR STATE	PROPAGATES PONR STATE TO PRODUCT ITEM TYPE
Commercial product parent item	All commercial product child items
Commercial product child item	Commercial product parent item
Technical product parent item	
All technical product child items
All commercial product items associated directly as well as through technical child items
Technical product parent item
All commercial product items associated directly as well as through the technical product parent item
Step Status Changes from Supplemental Actions

Here’s how step statuses change when supplemental actions are applied to in-flight orders.

NEW SUPPLEMENTAL ACTION APPLIED TO SUPPLEMENTAL ORDER	STATUS FOR APPLYING THE ACTION	CHANGE IN STEP STATUS
Add	Pending	—
Amend	

Pending

Completed

Skipped

Scheduled

Failed (applies only to the Callout and Autotask steps)

Fatally Failed (applies only to the Callout and Autotask steps)

	

—

Amended

—

Pending

Failed

Fatally Failed


Cancel	

Pending

Completed

Scheduled

Skipped

Failed (applies only to the Callout and Autotask steps)

Fatally Failed (applies only to the Callout and Autotask steps)

Canceled

	

Discarded

Canceled

Discarded

Discarded

Discarded (applies only to the Callout and Autotask steps)

Discarded (applies only to the Callout and Autotask steps)

No change (All compensation steps)


No Change	

Pending

Scheduled

Completed

Failed

Fatally Failed

Skipped

Amended

Canceled

	

—

—

—

—

—

—

No change (All compensation steps)

No change (All compensation steps)

Actions Not Applicable to Step Statuses

Here are the actions that aren’t applied to the steps that are in these statuses:

ACTION	STEP STATUSES WHEN THE ACTION ISN'T APPLIED
Amend	Ready, In Progress, Failed, Fatally Failed, Amended, Discarded, and Canceled
No Change	Ready, In Progress, Amended, Discarded, and Canceled
Cancel	

Ready, In Progress, Amended, Discarded, Canceled, Failed, and Fatally Failed

Failed and Fatally Failed (applies only to the Callout and Autotask steps)
