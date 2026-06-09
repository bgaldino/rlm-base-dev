---
page_id: deployment_context_service_additional_info.htm
title: Context Service Additional Information
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/deployment_context_service_additional_info.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Revenue Cloud Deployment
parent_page: deployment_appendix_C.htm
fetched_at: 2026-06-09
---

# Context Service Additional Information

Get to know additional deployment information for Context Service in Revenue
Cloud.

## Helpful Links

- [Migrate Context Definitions](https://help.salesforce.com/s/articleView?id=ind.context_service_context_definitions_packages.htm&language=en_US "HTML (New Window)")

## Deployment Considerations

- Context tags and individual sObject mappings must
  be unique for every definition.
- Deployment can lead to conflict if there are multiple tags
  with the same name, or if there are multiple mappings to the same sObject and sObject
  fields.
- Standard definitions are versioned and new changes must have a higher version than the
  version, which is available in the org.
- You can deploy updates that introduce new custom nodes, attributes, and their
  corresponding mappings to existing context definitions.
- Deployments that modify (update or delete) existing custom mappings for context
  definitions in an activated or a deactivated state are supported.

## Unsupported Deployment Scenarios

- Deploying context definitions from the current release to an older release is not
  supported.
- Modifying custom nodes and attributes for context definitions that are in a deactivated
  state aren’t supported. To make changes, replicate your desired modifications manually on
  the target context definition. You can also delete the context definition on the target
  org and deploy again.
- Modifying standard nodes and attributes for context definitions that are in an activated
  state isn't supported. To make changes, deactivate the definition on the target org first,
  make your desired modifications, and then activate the context definition again.
- You can’t activate or deactivate an active context definition as an action within a
  deployment package. Activation or deactivation must be performed as a separate, manual
  step outside the deployment process.
- You can’t make a context mapping default or non-default as an action within a
  deployment. Changing the default status of context mappings must be done as a separate,
  manual step.
