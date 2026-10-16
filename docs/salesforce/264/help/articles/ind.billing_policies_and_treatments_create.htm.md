---
article_id: ind.billing_policies_and_treatments_create.htm
title: Create Billing Policies, Treatments, and Treatment Items
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_policies_and_treatments_create.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_policies_and_treatments.htm
fetched_at: 2026-09-04
---

# Create Billing Policies, Treatments, and Treatment Items

Define billing policies, treatments, and treatment items to generate invoices that suit your sales models.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
USER PERMISSIONS
NEEDED
To create billing policies, treatments, and treatment items:	

Billing Admin permission set

OR

Billing Operations User permission set

Create Billing Policies

A billing policy is a group of billing treatments that consist of the rules to establish billing schedules for generating invoices. The billing policies are linked to products and applied to the resulting order product items.

From the App Launcher, find and select Billing Policies.
Click New.
Enter a name for the billing policy.
Select Draft as the status.
You can create billing policies only in the Draft status when there are no related active billing treatments.
Select how you want to assign billing treatments to the order items associated with the billing policy.
To use the billing treatment mentioned in the Default Billing Treatment field, select Default.
To use the billing treatment of the related order product, select Manual.
To use the billing treatment of the legal entity, select Legal Entity.
Select a default billing treatment.
To activate the billing policy, you must define a default billing treatment.
If necessary, enter a description.
Save your changes.

After you create a billing policy, create the related billing treatment.

Create Billing Treatments

Billing treatments are the set of rules that determine how an order item is billed.

From the App Launcher, find and select Billing Treatments.
Click New.
Enter a name for the billing treatment.
Select the billing policy for the billing treatment.
Multiple billing treatments are grouped to create a billing policy.
Select the legal entity.
Select Draft as the Status.
You can create billing treatments only in the Draft status when there are no related active billing treatment items.
If necessary, enter a description.
If you don't want to create billing schedules for the order items related to the billing treatment, select Yes as the Exclude From Billing value.
Save your changes.

After you create a billing treatment, create and activate a related billing treatment item.

Create Billing Treatment Items

Billing treatment items define how the order item’s total amount is distributed into billing schedules across the lifecycle of the order item.

You can create only one billing treatment item for each billing treatment.

From the App Launcher, find and select Billing Treatment Items.
Click New.
Enter a name for the billing treatment item.
Select a billing treatment for the billing treatment item.
Select Active as the status.
You can create billing treatment items in the Draft state also.
Enter the processing order in which you want to create billing schedules for the treatment item.
If necessary, enter a description.
Select how you want to bill the customers.
To bill the order product in advance, select Advance. The product is billed on the date that falls on or before the start date of the order product. For example, if a monthly order starts on January 1 and the billing date is the 15th, the first billing date is December 15.
To bill the order product after its start date, select Arrears. The item is billed on the date that falls after the start date of the order product. For example, if a monthly order starts on January 1 and the billing date is the 15th, the first billing date is January 15.
If your billing is based on milestones, select None to align charges with milestones.
When billing schedule group and billing schedule have a shared field with different values, select Billing Schedule Group as the controller to use the group's value.
Save your changes.

The Zero Amount Behavior, Type, Percentage, Flat Amount, and Sequencing values aren't considered when generating invoices. However, you must specify these values because they’re required to create a billing treatment item.

After you create an active billing treatment item, update the status of the related billing treatment to Active, and then update the status of the related billing policy to Active.

NOTE You can’t deactivate a billing treatment that is set as the default on an active billing policy.
