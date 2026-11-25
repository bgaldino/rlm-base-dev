---
page_id: dynamic-revenue-orchestrator-callout-configuration-steps
title: Configure Callout Settings
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/dynamic-revenue-orchestrator-callout-configuration-steps.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Dynamic Revenue Orchestrator
parent_page: dynamic-revenue-orchestrator-callouts-overview
legacy_page_id: dynamic_revenue_orchestrator_callout_configuration_steps.htm
fetched_at: 2026-11-25
---

# Configure Callout Settings

Before you set up a callout provider, configure the callout settings. The settings include the creation of a named credential and an external credential, the creation of an integration definition, and the configuration of a fulfillment step definition.

Meet these prerequisites before you configure the callout settings.

| Required Editions |
| --- |
| Available in: **Developer**, **Enterprise**, and **Unlimited** Editions |

| User Permissions Needed |  |
| --- | --- |
| To create authenticated callouts: | External Credentials Principal Access Permission |

- 

Configure named and external credentials to define access to an external system. Specify a named credential as the callout endpoint and an external credential to configure the authentication protocol.

See [Create Named Credentials and External Credentials](https://help.salesforce.com/s/articleView?id=xcloud.nc_named_creds_and_ext_creds.htm&type=5).

- 

Create integration definitions to connect Salesforce with an external system. Integration definitions use APIs to perform operations in both Salesforce and the external system. You can create Apex Defined, External Services Defined, or Standard integration definitions.

See [Create an Integration Definition](https://help.salesforce.com/s/articleView?id=ind.consumption_framework_integration_definitions.htm&type=5).

- 

Define a fulfillment step with `Callout` as the step type. Additionally, set the integration definition name and integration user.

See [Callout Fulfillment Step](https://help.salesforce.com/s/articleView?id=ind.dro_callout.htm&type=5).

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/dynamic-revenue-orchestrator-callout-configuration-steps.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
