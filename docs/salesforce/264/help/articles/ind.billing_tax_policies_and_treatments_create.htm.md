---
article_id: ind.billing_tax_policies_and_treatments_create.htm
title: Create Tax Policies and Treatments
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_tax_policies_and_treatments_create.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_tax_additional_configuration.htm
fetched_at: 2026-09-04
---

# Create Tax Policies and Treatments

Create tax policies and their treatments to define the tax calculation for your invoices.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
USER PERMISSIONS
NEEDED
To create tax policies and tax treatments:	Tax Admin permission set
Create Tax Policies

Tax policies are related to order products, which pass the policy on to the resulting billing schedules. Each tax policy requires at least one tax treatment.

From the App Launcher, find and select Tax Policies.
Click New.
Enter a name for the tax policy.
Select the status as Draft.
Select the treatment selection.
To use the default tax treatment of the tax policy, select Default. If you don't specify a default tax treatment for the tax policy, the default tax treatment selected for your Salesforce org is used.
To use the tax treatment of the related order product, select Manual.
To use the tax treatment of the related order product's legal entity, select Legal Entity.

This table explains the usage of tax treatment.

TREATMENT SELECTION	SCENARIO	BEHAVIOR
Manual	No tax treatment selected for the related order product	Uses the default tax treatment of the tax policy
Manual	No default tax treatment selected for the tax policy	Uses the default tax treatment selected for your Salesforce org
Manual	No default tax treatment selected for your Salesforce org	The tax calculation fails
Legal Entity	No legal entity specified for the related order product or order	Uses the tax treatment of the default legal entity selected for your Salesforce org
Legal Entity	No default legal entity selected for your Salesforce org	Uses the tax treatment related to the tax policy that has the same legal entity as that of the related order product
Legal Entity	No matching legal entity	Uses the default tax treatment of the tax policy
Legal Entity	No default tax treatment selected for the tax policy	Uses the default tax treatment of the tax policy
Legal Entity	No default tax treatment selected for your Salesforce org	The tax calculation fails
If necessary, enter a description.
If the treatment selection is Default, specify a default tax treatment.
Save your changes.

After you create a tax policy, create and activate the related tax treatments.

Create Tax Treatments

Define the criteria for calculating taxes for invoices.

From the App Launcher, find and select Tax Treatments.
Click New.
Enter a name for the tax treatment.
If you select Is Taxable, select the tax engine for the tax treatment.
When tax is calculated for an order product, this tax engine of the product’s tax treatment is used.
If necessary, enter the code of the product that the tax treatment applies to.
Select the tax policy that you want to relate to the tax treatment.
If necessary, enter a description.
Enter the reference code that's used to calculate tax as the tax code.
The tax code of the tax engine is populated as the invoice line tax’s tax code.
To calculate taxes based on your product codes, select Use Tax Treatment Items.
When you select this option but don't have any tax treatment items for the tax treatment, Billing uses the tax code on the tax treatment. If you didn't define a tax code, Billing sends a null value to the tax engine.
If you selected Use Tax Treatment Items, set the status of the tax treatment to Draft, associate the required tax treatment items, and then set the status of the tax treatment to Active. If you didn't select the Use Tax Treatment Items option, select Active as the status.
To calculate tax for order products that are related to the tax policy, select Is Taxable.
If the treatment selection of the parent tax policy is Legal Entity, select the legal entity that you want to relate to the tax treatment.
Save your changes.

After you create an active tax treatment, change the status of the parent tax policy to Active. Only active tax policies can be used for tax calculation. Then, select the tax treatments for order products.

NOTE Make sure that the tax treatments or the orders products have a legal entity, or that a default legal entity is selected for the Salesforce org.
Create Tax Treatment Items

Use tax treatment items to define how individual products are taxed within a tax treatment. Resolve tax codes based on both the legal entity and the product, providing more granular and accurate tax calculations.

NOTE To calculate taxes based on a product code, select Use Tax Treatment Items on the tax treatment and associate the required tax treatment item. Billing resolves the applicable tax treatment item by using the product code on the transaction.
From the App Launcher, find and select Tax Treatment Items.
Click New.
Enter a name for the tax treatment item.
Select a tax treatment for the tax treatment item.
Enter the product code for the product associated with this tax treatment item.
Enter the tax code applicable for the selected product and for the legal entity.
Select the product that you're creating the tax treatment items for.
Save your changes.
