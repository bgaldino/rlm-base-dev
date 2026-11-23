---
page_id: dynamic_revenue_orchestrator_input_output_processors.htm
title: Input and Output Transformation Processors
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/dynamic_revenue_orchestrator_input_output_processors.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_callouts_overview.htm
fetched_at: 2026-11-23
---

# Input and Output Transformation Processors

Use input and output processors to process a standard fulfillment request before
sending it to an external system.

## Prerequisites

- Omnistudio license is required.
- Omnistudio Admin permission set license is assigned to Integration Configuration User
  (Fulfillment Designer).
- The input and output procedure attributes of an integration definition, which are
  available from Setup, are assigned with the Omnistudio Integration Procedure request and
  response. You can use `Type_Subtype` or `Id` of OmniProcess as the values for attributes.

When a callout step is executed, these steps are followed.

- The defined integration procedures are identified for request and response handling from
  an integration definition.
- The input processor generates the request by using `Fulfillment Step Source > SourceIdentifier` as the `InputRecordId` input parameter value. For example, the ID of an order
  item.
- The output processor handles the response by passing a map to the Integration Procedure
  service. The results from the Integration Procedure are used to identify any errors and
  details are passed to Dynamic Revenue Orchestrator.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/dynamic_revenue_orchestrator_input_output_processors.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
