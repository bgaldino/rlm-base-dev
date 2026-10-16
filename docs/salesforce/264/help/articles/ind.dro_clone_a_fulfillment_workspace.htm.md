---
article_id: ind.dro_clone_a_fulfillment_workspace.htm
title: Clone a Fulfillment Workspace
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_clone_a_fulfillment_workspace.htm&type=5&release=264
release: 264
release_name: Winter '27
area: dro
parent_article: ind.dro_define_orchestration_components.htm
fetched_at: 2026-09-05
---

# Clone a Fulfillment Workspace

Copy a fulfillment workspace and its supported design-time records to create a starting point for a new orchestration design. Changes to the cloned workspace don’t affect the source workspace.

REQUIRED EDITIONS
Available in: Enterprise, Unlimited, and Developer Editions
USER PERMISSIONS
NEEDED
To clone a fulfillment workspace:	DRO Admin

When you deep clone a fulfillment workspace with the preconfigured context definition FulfillmentWorkspaceDeepCloneContext, it copies the fulfillment workspace, workspace items, step definition groups, step definitions, and step dependency definitions. To include supported custom fields or objects, configure a context definition that extends FulfillmentWorkspaceDeepCloneContext. Optionally, you can also configure an expression set to transform field values during cloning. See Configure Deep Cloning for Fulfillment Workspaces.

Before you clone a fulfillment workspace, review these considerations.

Records outside the workspace aren't cloned, such as flows, queues, users, integration definitions, OmniScripts, and expression sets. The cloned records continue to reference the external records.
Execute On and Resume On rulesets aren't copied. They're not included in the cloned workspace.
You can clone a maximum of 500 records, including records in the source workspace and records created in the cloned workspace.
From the App Launcher, find and select Dynamic Revenue Orchestrator.
From the app navigation menu, find and select Fulfillment Workspaces.
Open the fulfillment workspace that you want to clone.
From the action menu, select Deep Clone.
Enter a unique name for the cloned workspace, and then click Deep Clone.
The workspace name is prefilled with the source workspace name and a prefix.

The Deep Clone Fulfillment Workspace window confirms that cloning succeeded and lists the copied object types and record counts.

To continue designing the cloned workspace, click View Cloned Fulfillment Workspace.
