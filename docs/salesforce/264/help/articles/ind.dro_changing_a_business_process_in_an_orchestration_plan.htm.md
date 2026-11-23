---
article_id: ind.dro_changing_a_business_process_in_an_orchestration_plan.htm
title: Business Process Changes in an Orchestration Plan
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_changing_a_business_process_in_an_orchestration_plan.htm&type=5&release=264
release: 264
release_name: Winter '27
area: dro
parent_article: ind.dro_dynamic_revenue_orchestrator_concepts_and_references.htm
fetched_at: 2026-11-23
---

# Business Process Changes in an Orchestration Plan

When you roll out a phased implementation of Dynamic Revenue Orchestrator, each rollout phase can change a business process or require multiple configurations of it to coexist.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud

A condition is a rule that checks an attribute of the order, product, or account and determines whether a step, step group, or scenario applies. The attribute you select determines how the condition behaves: use a date-based condition for a single cutover across all orders, a product-attribute condition for logic that varies by service type, an account-attribute condition for pilots or specific segments, an order-value condition for risk-based workflows, and a business-milestone condition that applies when an order or fulfillment event occurs. Combine conditions when a change depends on more than one factor. For more on building conditions, see Understand Execution Conditions for Order Fulfillment.

Whenever you need to replace, add, or change a business process in an orchestration plan during a rollout phase, don't edit the active configuration in place. Long-running orders are often still in-flight when the next rollout phase happens, and editing in place can disrupt them. Instead, apply a condition to each change and, where the change is significant, run the old and new configurations in parallel.

Legacy configurations then retire naturally as their orders finish. Allow time for sandbox testing, documentation updates, and customer notification when a change affects service levels, and give more lead time for larger changes, such as replacing a business process or introducing a new scenario.

The following patterns are recommendations you can adapt to your own rollout, not the only way to make these changes. For each, model the change so that it applies to new orders without disrupting orders that are already running. A single rollout phase can combine more than one of these changes—choose the combination that fits the business scenario and the types of orders in-flight so that risk stays minimal.

Replace an existing business process
Deploy the replacement as a new step group or scenario and route new orders to it with a condition. Keep the existing step group in place for orders that already use it, and retire it after those orders complete.
Add a new business process
Add a new step group (or a new step for an external callout) and link it to a scenario with a condition so that it qualifies only for the orders that need it. Orders already in flight aren't affected.
Change how a business process runs, such as manual to automated
Model the new execution as a new step definition or a new scenario controlled by a condition, rather than editing the running step in place. New orders use the automated path, and in-flight orders complete with the process they started on.
Change part of a business process
Apply conditions to the specific steps that change, so that only qualifying orders pick up the new behavior. The conditions suppress the old steps for new orders instead of deleting them while in-flight orders still reference them.
Replace the fulfillment system behind a business process
When the change replaces an entire downstream or backend system, choose the level of isolation. If the same technical product still applies, route new orders to a different scenario or step group, as when replacing a business process. If the fulfillment logic must be fully separate—for example, because in-flight orders need to keep being amended or canceled against the old system until they complete—route to a different technical product instead, using an execution rule based on a product or order attribute. For how execution rules select a technical product, see Decomposition Relationship Types. To configure the condition behind an execution rule, see Define Execution Rules for a Decomposition Rule.

For example, here's how the "Change part of a business process" pattern looks when the change is inserting a new, conditionally run step into an existing process:

Choose How to Model a New or Replacement Business Process

When a pattern above introduces a new or replacement business process, decide whether to model it as a step group or a step. Your choice determines how easily you can change it again later.

As a fulfillment step definition group
Model a business process that runs entirely within Salesforce as a fulfillment step definition group, also called a step group. The step group holds the ordered steps of the process. A larger business process doesn't have to map to a single step group—multiple step groups can each represent a fragment of it. For more on defining step groups and steps in an orchestration plan, see Define Orchestration Plan Components.
As a step
Model a business process that calls a downstream or external fulfillment system as a single step within a step group, such as a callout step.

A fulfillment scenario links products to the step groups that run for an order. Group steps by lifecycle stage from the start—identify the steps that are common across products first, then split only the product-specific logic into separate step groups, and apply conditions at the scenario level when possible. This structure makes it easier to add logic paths later without refactoring.

Maintain Multiple Configurations of a Business Process

A rollout phase often means that more than one configuration of the same business process must coexist for some period. Choose the coexistence model that fits how long the old and new configurations need to run together.

Coexist for the long term
Keep the parallel scenarios in place indefinitely, routed by durable conditions. Use this model when the business intends to keep both variants, for example, for different products or regions.
Coexist until orders on the old configuration complete
Suppress the old configuration for new orders with a condition and let running orders age out on it. After all orders that reference the old configuration complete, retire the old step group, steps, or scenario. Dynamic Revenue Orchestrator blocks this deletion while incomplete steps still reference the step group, steps, or scenario—don't force a metadata override to bypass the block, since it risks corrupting in-flight orders. Periodically check for suppressed steps and retired scenarios whose orders have all completed, and remove them. Plans with many conditions add processing latency and can approach platform limits, especially for high-scale orders. For specific limits, see Dynamic Revenue Orchestrator Limits.
New configuration overrides the old after a cutoff
Use a date-based condition so that orders before the cutoff use the old configuration, and orders on or after the cutoff use the new one. This model gives a clean, time-based transition with no mixing of logic.
When to Use Code for an Orchestration Change

You can handle most orchestration plan changes using a configuration—modifying scenarios, step definitions, conditions, and step dependencies—rather than custom code. Configuration changes are safer to deploy across a phased rollout because you can control them with conditions and run them in parallel with existing logic. Use custom code, such as Apex or Flow, only when the change requires logic that conditions can't express.

TASK	HOW TO USE CODE
Transform data	Use code to reshape, map, or enrich payload data that a step passes to a downstream system.
Calculate a business value	Use code for calculations that go beyond a condition's comparison of field values, such as pricing or eligibility logic.
Call an integration endpoint	Use code to connect a step to an external fulfillment system through a callout.
Enforce an API contract	Use code when a step must produce or consume a specific request or response contract that a downstream system requires.

Modifying underlying logic, such as Apex or Flow, while keeping the same step definition is safe only if the input and output contract stays identical. Any change to parameters or required payload properties can cause a running step to fail.

Impact of Entity-Level Changes by Order State

The patterns and coexistence models above work by editing one or more of four entities—fulfillment scenarios, step definitions, conditions, and step dependencies. This table lists the full effect of each entity-level change on new, running, and supplemental orders, so you can check the outcome for the specific change you're making.

Impact of Orchestration Configuration Changes by Order State
ENTITY	TYPE OF CHANGE	NEW ORDERS	RUNNING ORDERS	SUPPLEMENTAL ORDERS
Fulfillment scenario	Add a new record	Applies to the new order.	No impact.	New step groups with steps are added to a plan if the scenario qualifies for a supplemental order.
Delete a record	The linked step group isn't considered in the plan. Steps that belong to that step group aren't created.	No impact.	Steps that were created because this scenario existed are canceled or discarded, depending on the execution state of the step.
Change product or step group in an existing record	The new configuration applies to the new order. New conditions, if any, are evaluated, and the steps are created.	No impact.	Steps that were created under the old configuration are canceled or discarded, depending on the execution state of the step, and new step groups with steps are added to the plan if the new configuration qualifies for the supplemental order.
Condition on fulfillment scenario	Add a new condition	The new condition is evaluated, and if it qualifies, the steps are created.	No impact.	If the scenario stops qualifying because of the condition, the steps are canceled or discarded, depending on the execution state of the step.
Delete a condition	Step definitions that are part of the step group are used to create new steps.	No impact.	The scenario can start qualifying. If it does, the steps are added during the supplemental order's plan reconciliation process.
Change criteria of an existing condition	The new criteria are evaluated. Based on the outcome, steps are either created or ignored.	No impact.	If the scenario starts qualifying under the new criteria, the steps are added during the supplemental order's plan reconciliation process. If it stops qualifying, the steps are canceled or discarded, depending on the execution state of the step.
Fulfillment step definition	Add a new record	Steps are created for the new step definition.	No impact.	Steps are created for the new step definition.
Delete a record	Not allowed to delete if incomplete steps refer to it.	Not allowed to delete if incomplete steps refer to it.	Not allowed to delete if incomplete steps refer to it. If the step is completed, compensations are inserted into the plan.
Add a new step	If the scenario qualifies, the step is added to the plan.	No impact.	If the scenario continues to qualify, the step is added during the supplemental plan reconciliation process.
Delete a step	The deleted step definition is ignored. If any plan has an incomplete step based on the given step definition, the step definition can't be deleted.	Not allowed to delete if incomplete steps refer to it.	The step is canceled or discarded, depending on the state of execution. If any plan has an incomplete step based on the given step definition, the step definition can't be deleted.
Change step type	The step is created with the new step type.	No impact.	Ignored during plan reconciliation.
Change step scope	Steps are created in the new scope.	No impact.	The supplemental order is rejected.
Change point of no return (PONR)	Steps are created with the new PONR value.	No impact.	Ignored during plan reconciliation.
Change amend or cancel step group	Steps are created with reference to the amend and cancel groups.	No impact.	Ignored during plan reconciliation.
Change Apex, Flow, integration definitions, or assignment rules	Steps are created with reference to the new Apex or Flow. The latest active version of the flow is used.	Currently executing steps run the old version if execution started before the Apex or Flow was changed. If the step runs after the change, the new version runs. If the contract—input, output, or pre- and post-conditions—changes for the new implementation, the step can fail.	Depends on whether the step's contract—input, output, or implemented functionality—changes. If it does and the step runs, the step can fail. If you change the Apex class or flow in the definition but leave the old Apex class or flow as-is, the steps can run without issues, depending on other changes in dependent classes, configurations, and subflows.
Add a new condition	The new condition is referenced from the fulfillment step record that's created.	No impact.	Conditions added to the definition after the step is created are ignored.
Delete a condition	The fulfillment step record is created without a reference to the condition.	Conditions (execute or resume on ruleset lookup values) that are deleted from the definition are also removed from running steps.	Conditions deleted from the definition after the step is created are ignored, and the old condition is evaluated.
Change criteria of an existing condition	The fulfillment step record references the ruleset.	The fulfillment step record references the ruleset. A change in the condition affects execution by skipping or running the step.	The fulfillment step stores only the reference to the ruleset. If the criteria change, the new criteria are evaluated during orchestration execution.
Step dependency definition	Add a new dependency between existing steps	Applies to the new order.	No impact.	The new dependency record is added during plan reconciliation. This dependency record might or might not affect the actual orchestration execution.
Add a dependency between an existing step and a newly added step	Applies to the new order.	No impact.	The new dependency record is added during plan reconciliation.
Add a dependency between a newly added step and an existing step	Applies to the new order.	No impact.	The new dependency record is added during plan reconciliation. This dependency record might or might not affect the actual orchestration execution.
Add a dependency between two newly added steps	Steps are created with fulfillment step dependency records between them, as long as the steps are in the right scope.	No impact.	The new dependency record is added during plan reconciliation.
Delete a dependency	Steps are created without any fulfillment step dependency record between them.	No impact.	A dependency record, once created, isn't deleted.
Change dependency scope	Applies to the new order.	No impact.	No impact.
SEE ALSO
Design Your Order Orchestration

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.dro_changing_a_business_process_in_an_orchestration_plan.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
