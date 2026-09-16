---
article_id: ind.qocal_extend_context_definitions.htm
title: Link Context Definitions to Pricing Procedures
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_extend_context_definitions.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_extend_your_transactions_with_custom_field_support.htm
fetched_at: 2026-09-04
---

# Link Context Definitions to Pricing Procedures

Link your pricing procedure to your extended context definition to enable efficient data access.

From the App Launcher, find and select Pricing Procedures.
Select your pricing procedure and deactivate the current version.
Click Edit and select your extended context definition in the Context Definition field.
Save your changes.
Update the Pricing Procedure Properties start date to a time after you created the extended context definition.
Save and activate the pricing procedure.
In Revenue Settings within Setup, select this pricing procedure to apply it to all quotes and orders.

Context Definition Troubleshooting

If you encounter pricing errors after extending a context definition, check for these common issues:

Context definition has both ClonedFrom and InheritedFrom populated
If a context definition record has values in both the ClonedFrom and InheritedFrom fields, it can cause pricing errors. If you find affected records, delete them and recreate the context definition extension.
Something went wrong while hydrating additional context fields
This error can occur when the context definition is out of sync with the pricing procedure, when the context definition was cloned instead of extended, or when the context definition was created without the required permissions. Verify that you extended (not cloned) the context definition and that the pricing procedure references the correct extended context definition.
