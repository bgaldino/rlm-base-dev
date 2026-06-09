---
page_id: dynamic_revenue_orchestrator_callout_configuration_steps.htm
title: Configure Callout Settings
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/dynamic_revenue_orchestrator_callout_configuration_steps.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_callouts_overview.htm
fetched_at: 2026-06-09
---

# Configure Callout Settings

Before you set up a callout provider, configure the callout settings. The settings
include the creation of a named credential and an external credential, the creation of an
integration definition, and the configuration of a fulfillment step definition.

Meet these prerequisites before you configure the callout settings.

|  |
| --- |
| Available in: **Developer**, **Enterprise**, and **Unlimited** Editions |

| User Permissions Needed | |
| --- | --- |
| To create authenticated callouts: | External Credentials Principal Access Permission |

- Configure named and external credentials to define access to an external system. Specify a
  named credential as the callout endpoint and an external credential to configure the
  authentication protocol.

  See [Create Named
  Credentials and External Credentials](https://help.salesforce.com/s/articleView?id=xcloud.nc_named_creds_and_ext_creds.htm&type=5&language=en_US "HTML (New Window)").
- Create integration definitions to connect Salesforce with an external system. Integration
  definitions use APIs to perform operations in both Salesforce and the external system. You can
  create Apex Defined, External Services Defined, or Standard integration definitions.

  See [Create an
  Integration Definition](https://help.salesforce.com/s/articleView?id=ind.consumption_framework_integration_definitions.htm&type=5&language=en_US "HTML (New Window)").
- Define a fulfillment step with `Callout` as the step
  type. Additionally, set the integration definition name and integration user.

  See [Callout Fulfillment
  Step](https://help.salesforce.com/s/articleView?id=ind.dro_callout.htm&type=5&language=en_US "HTML (New Window)").
