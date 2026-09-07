---
article_id: ind.dro_configure_fulfillment_workspace_deep_cloning.htm
title: Configure Deep Cloning for Fulfillment Workspaces
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_configure_fulfillment_workspace_deep_cloning.htm&type=5&release=264
release: 264
release_name: Winter '27
area: dro
parent_article: ind.dro_advanced_setup.htm
fetched_at: 2026-09-05
---

# Configure Deep Cloning for Fulfillment Workspaces

Deep cloning uses the preconfigured context definition FulfillmentWorkspaceDeepCloneContext by default. Configure deep clone settings to include supported custom fields or objects, or to transform field values during cloning.

REQUIRED EDITIONS
Available in: Enterprise, Unlimited, and Developer Editions
USER PERMISSIONS
NEEDED
To configure deep cloning for fulfillment workspaces:	DRO Admin

Turn on Context Definitions to load the FulfillmentWorkspaceDeepCloneContext context definition. For more information, see Turn On Context Definitions.

By default, deep cloning uses this preconfigured FulfillmentWorkspaceDeepCloneContext context definition to copy the fulfillment workspace, workspace items, step definition groups, step definitions, and step dependency definitions. This configuration is optional. Configure deep cloning only when you want to:

Extend the context definition to include supported custom fields or objects. Create a context definition that extends FulfillmentWorkspaceDeepCloneContext, and then select it for deep cloning.
Select an expression set when you want to transform field values in the cloned records.
From Setup, in the Quick Find box, enter and then select Dynamic Revenue Orchestrator Settings.
Select Deep Clone Settings.
For Fulfillment Workspace Context Definition, select a context definition.
To copy the standard supported records, select FulfillmentWorkspaceDeepCloneContext.
To also copy supported custom fields or objects, select a context definition that extends FulfillmentWorkspaceDeepCloneContext.
Optional: To transform field values in the cloned records, select an expression set for Fulfillment Workspace Expression Set.
For example, use an expression set to append text to cloned record names or assign a different value to a custom field.

The selected context definition and expression set apply to all subsequent fulfillment workspace deep clones.

SEE ALSO
Clone a Fulfillment Workspace
Extend a Context Definition
