---
article_id: ind.pricing_procedure_plan_framework.htm
title: Build and Manage Your Procedure Execution
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_procedure_plan_framework.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Build and Manage Your Procedure Execution

Use the Procedure Plan Setup framework to set up your procedures, configure the procedure execution settings, and relate them to a context definition in one centralized location. You can use the predefined templates to build your procedure plan definitions or create a custom definition for your unique use cases.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer editions of Agentforce Revenue Management where Salesforce Pricing is enabled.

Procedure plan definitions consist of various sections that you can organize in any order. Each section must have at least one procedure or contain a set of procedures that can be executed based on specific criteria. You can configure these criteria by using default settings or rule-based criteria that best fit your business needs.

Before you create a procedure plan, understand these key terms.

TERM	DESCRIPTION
Procedure Plan Definition	A procedure plan definition combines multiple procedures into a single, unified plan. You can arrange these procedures in any order to meet your business needs. Each plan contains sections and subsections that are configured using simple decision tables or complex, rule-based criteria.
Procedure Plan Section	The various sections added to define a procedure plan. Each section allows you to set up a specific type of procedure.
Phase	A phase represents a stage in your business lifecycle, used to organize procedures and link them to the correct business context.
Resolution Type	A resolution type determines how a procedure is selected for a section of your plan. You can either set it to Default, which allows you to manually pick a procedure from a list, or you can choose Rule-Based, which lets the system automatically select the correct procedure by evaluating a set of predefined criteria.
Read Context Mapping	This mapping is used at the start of the procedure. It reads necessary input data from a Salesforce object such as Quote or Order the to the context definition to set the context for pricing logic execution.
Save Context Mapping	This mapping is used at the end of the procedure. It saves the calculated results from the context definition such as prices or discounts back to the fields in the associated Salesforce objects storing in the final output.
IMPORTANT
Before you begin creating your procedure plan definitions, you must enable Context Service in your org. To enable Context Service, go to Setup, in the Quick Find box, search and select Context Service Settings. Turn on Context Definitions.
Understand the Order of Execution for Place Sales Transaction
When you create or update a quote or order using the Place Sales Transaction API, Agentforce Revenue Management processes the request through a defined order of execution. This order describes how configuration, pricing, Apex hooks, and automation run during transaction processing. Understanding this order helps you determine where pricing logic runs and how context data is processed when using Place Sales Transaction.
Create Procedure Plans
To create a flexible and comprehensive workflow that adapts to your business needs, use a Procedure Plan Definition to combine and sequence individual procedures into a single, unified plan. You can start quickly with a predefined template or customize one from scratch to meet your unique requirements.
Customize Your Procedure Plans With Apex Hooks
To support unique pricing scenarios, add custom Apex logic to your pricing procedure plans. You can use Apex hooks to apply custom business logic that modifies the pricing context after a quote line is configured. Use an Apex prehook to adjust pricing based on product attributes before it's priced, and an Apex posthook to handle pricing changes for groups and other Quote object elements after pricing. When a sales rep configures a product or changes a group of quote line items, the pricing procedure plan changes the pricing based on the instructions in Apex.
Use the Procedure Plan Framework
To ensure your procedures run in the correct order and pricing is applied consistently to a quote, create a new procedure plan.
Export and Import Procedure Plans
Package procedure plans to export and import them across Salesforce orgs.
Procedure Plan Limits
Don't stitch multiple pricing procedures together within a single procedure plan. Sequencing multiple procedures can result in data loss and calculation errors. If you need to configure multiple procedures sequentially, consider these limitations.
