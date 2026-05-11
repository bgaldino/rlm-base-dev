---
article_id: ind.billing_milestone_treatment_and_item_create.htm
title: "Method 1: Configure Billing Milestones Using Billing Treatments"
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_milestone_treatment_and_item_create.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
parent_article: ind.billing_milestone_methods.htm
fetched_at: 2026-05-11
---

# Method 1: Configure Billing Milestones Using Billing Treatments

Create billing milestone plans and billing milestone plan items from billing treatment and billing treatment items and apply them to one or more products. This method is ideal when multiple products follow the same milestone billing pattern. You can edit the billing milestone plans for individual order products without affecting the billing treatment.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER PERMISSIONS NEEDED
To create billing treatments and billing treatment items:	Billing Admin permission set
Configure Billing Treatments for Milestone Plan Items
Create a billing policy.
Create a billing treatment with Enable milestone billing selected.
Click Configure Milestones to create up to 20 milestones at once. For configuration steps, see Create Billing Milestone Plan Items.
Activate the Billing Treatment.

Alternatively, on the Related tab, in the Billing Treatment Items section, click New, and follow the configuration steps.

Configure Billing Treatment Items Template for Milestone Plan Items
Create a billing treatment item.
After you define the billing treatment item fields, enter these values in the billing milestone plan-specific fields before you save the changes.
OPTION	SELECTION
Zero Amount Behavior	None
Type	Percentage
Billing Type	None
Sequencing	None
Controller	None
Milestone Type	Specify whether the milestone is based on an event or a specific date. An event-based milestone is triggered when a specific event or task within a project is completed. Select the Milestone accomplished checkbox to manually trigger this checkpoint. A date-based milestone is scheduled on a specific date and is calculated from the activation date of an order product.
Milestone Commencement Trigger	For date-based milestones, specify that the milestone commencement aligns with the billing schedule start date.
Milestone Commencement Offset	For date-based milestones, specify the wait time from the commencement trigger to determine the milestone's accomplishment date.
Milestone Commencement Offset Unit	For date-based milestones, specify the time unit for the milestone commencement offset, such as days, months, or years. For example, if you activate a product on January 1 and set a 30-day milestone commencement offset, the milestone completes on January 31.

After you create an active billing treatment item, update the status of the related billing treatment to Active, and then update the status of the related billing policy to Active.

For milestone billing, activate the related order to automatically generate billing schedules, and create billing milestone plan and billing milestone plan items based on the specified billing treatment and billing treatment items inputs. The validation on the fields is run, and calculated fields are updated only when the order is activated.
