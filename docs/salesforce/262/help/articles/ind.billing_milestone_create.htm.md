---
article_id: ind.billing_milestone_create.htm
title: "Method 2: Create Billing Milestone Plans and Plan Items"
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_milestone_create.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Method 2: Create Billing Milestone Plans and Plan Items

You are here:

SALESFORCE HELP
DOCS
AGENTFORCE REVENUE MANAGEMENT
Method 2: Create Billing Milestone Plans and Plan Items

Create billing milestone plans, and then create billing milestone plan items to specify how billings are scheduled based on the completion of specific project milestones throughout the lifecycle of the order product.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER PERMISSIONS
NEEDED
To create billing milestone plans and plan items:	

Billing Admin permission set

OR

Billing Operations User permission set

Create Billing Milestone Plans
From the App Launcher, find and select Billing Milestone Plans.
Click New.
Enter a name for the billing milestone plan.
Select a billing treatment for the billing milestone plan.
Select Draft as the status.
If necessary, enter a description.
Select a reference item for which you want to create a billing milestone plan.
You can select a billing schedule, order product, quote line item, or an external reference item.
Save your changes.
Create Billing Milestone Plan Items
Open the billing milestone plan that you want to create the plan item for.
Click Configure Milestones.
You can create up to 20 milestones at once.
Select Billing Schedule Start Date as the milestone commencement trigger.
Enter a name for the billing milestone plan item.
Specify whether to set date-based or event-based milestones.
For the billing checkpoint to occur when you manually activate the milestone trigger by selecting Milestone accomplished, select Event. For example, you can invoice a client after completing a project phase, delivering a key output, or reaching a specific goal. This type of milestone makes sure that billing is directly linked to project progress and measurable achievements.
For the billing checkpoint to occur on a predefined date, which is calculated from the activation date of an order product, select Date. For example, you can configure a billing milestone plan item such that an invoice for the billing milestone plan item is generated one month after an order product is activated. By specifying the milestone commencement offset and milestone commencement unit, you can define the exact duration after which the date-based billing milestone becomes ready for invoicing. This method provides a predictable billing timeline, supporting efficient cash flow management and financial planning.
Select Draft as the status.
If necessary, enter a description.
For a date-based milestone, enter these values.
For the offset, specify the wait time from the commencement trigger to determine the milestone's accomplishment date.
For the offset unit, specify the time unit for the milestone commencement offset, such as days, months, or years. For example, if you activate a product on January 1 and set a 30-day milestone commencement offset, the milestone completes on January 31.
Specify the distribution method for the milestone amount.
Enter the percentage of the total billable amount for the reference item to be invoiced for this milestone.
Enter a flat amount to be invoiced for this milestone.
You can combine both the distribution methods within a single milestone billing plan.
Click Add Item to add the required milestone items and enter the necessary values.
Save the changes.
Update the status of the billing milestone plan to Active, and save the changes.
If needed, modify the uninvoiced billing milestone plan items.

Alternatively, on the Related tab, in the Billing Milestone Plan Items section, click New and follow the same configuration steps. After activating the billing treatment, you can view the milestones and update only the Milestone accomplished field for event-based milestones.
