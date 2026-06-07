---
article_id: ind.pricing_create_a_custom_procedure_plan_definition.htm
title: Create a Custom Procedure Plan Definition
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_create_a_custom_procedure_plan_definition.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Create a Custom Procedure Plan Definition

Create custom procedure plan definitions that contain only selected types of procedures. You can further filter these definitions by configuring multiple criteria and conditions within a procedure.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Salesforce Pricing is enabled
USER PERMISSIONS NEEDED
To create and update procedure plan definitions:	

Procedure Plan Access

AND

Salesforce Pricing Design Time User

From Setup, in the Quick Find box, enter Procedure Plan Definitions, and then select Procedure Plan Definitions.
Select New, provide the procedure plan definition details, and save the details to create your procedure.
NOTE The Primary Object field is optional. However, if you don’t provide a source object, you can’t create a procedure with rule-based criteria.
Open the newly created procedure plan definition.
If necessary, set the context mapping to read and save data from a mapped object.
The context definition that you select when you create the procedure plan definition record is auto-populated.
To add the procedures that you want in the Procedure Plan Sections, select Add.
Specify the procedure plan section that you want to create.
Standard	Choose from a list of default procedure plans included with Agentforce Revenue Management, filtered by their usage type.
Custom	Configure your procedure without a usage type filter.
To map your procedure to different stages of the business lifecycle, associate your procedure with a phase.
Based on the procedure plan section that you selected, set a resolution type.
Default	Select a procedure from the list of procedures available in your org.
Rule-Based	Set selection criteria to verify how a procedure can be configured for a selected procedure plan section record.
IMPORTANT Ensure that the context definition related to your procedure plan definition and pricing procedures is the same.
To set the order that the procedures are executed in, select Manage Sections.
If necessary, modify the effective date ranges for this procedure plan definition record.
Save your changes and activate the definition of your procedure plan.
