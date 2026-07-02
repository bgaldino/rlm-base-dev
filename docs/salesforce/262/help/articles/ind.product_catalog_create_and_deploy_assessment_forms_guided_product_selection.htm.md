---
article_id: ind.product_catalog_create_and_deploy_assessment_forms_guided_product_selection.htm
title: Create and Deploy Requirement Assessment Forms for Guided Product Selection
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_create_and_deploy_assessment_forms_guided_product_selection.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Create and Deploy Requirement Assessment Forms for Guided Product Selection

For each requirement that you want to provide guidance for, create a set of questions, add the questions to a form, add logic to the form, and deploy the form. When your users (such as sales reps and customers) answer these questions, Guided Product Selection uses the answers to show the most suitable products.

REQUIRED EDITIONS
View supported products and editions.
USER PERMISSIONS NEEDED
To create and deploy assessment forms:	
Product Catalog Management Designer permission set
Create Assessment Questions
From the Product Catalog Management app’s home page, click Assessment Questions.
Create questions with Select as the data type. See Create Questions.
IMPORTANT It’s recommended that you add up to 4 response values.
Create a Form
Create a form by using one of these methods.
From the Assessment Questions page, select the assessment questions, and then click Select Questions. Then define the assessment steps.
From the Product Catalog Management app’s home page, click Create Form. Then select the assessment questions and define the assessment steps.
See Create a Form.
Click Build Omniscript.
In the Select Discovery Framework Usage Type window, select Guided Product Selection and then click Save.
IMPORTANT When users use guided product selection, only activated forms whose usage type is Guided Product Selection appear.
The form is created and appears on the Omniscripts tab.
Configure and Deploy a Form
From the Product Catalog Management app’s home page, click Omniscripts.
To add a description that appears to users when they use Guided Product Selection, click Edit and then enter a description.
NOTE All the Omniscript forms are available to users from all the catalogs. So, in the description, it’s recommended that you specify the name of the catalog from which a form must be used.
Configure the Omniscript form to specify the necessary logic. See Build the Layout of a Form.
IMPORTANT We recommend that you configure logic such that a maximum of 5 questions appear to users at run time.
For each step, in the Step Properties section of the Properties tab, deselect Allow Save for Later.
At run time, Guided Product Selection doesn’t support saving partially complete Omniscript forms and completing them later.
Delete the Save-Responses remote action element.
From the Build tab, in the Omniscript section, drag the ProductGuidedSelectionIntegration Omniscript to the canvas and ensure that it’s the last element.
The ProductGuidedSelectionIntegration Omniscript saves responses, and makes sure that the message framework and remote class are configured properly.
If needed, preview the form. See Preview a Form.
Activate and deploy the form. See Activate and Deploy the Form.

After the form is activated and deployed, it’s available to users when they click the Guide Me button on the Product List component. For example, users click the View Catalogs quick action to open the Product List component, and then click the Guide Me button to access the forms.
