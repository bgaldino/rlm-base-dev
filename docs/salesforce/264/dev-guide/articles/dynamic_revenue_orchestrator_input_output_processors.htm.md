---
page_id: dynamic_revenue_orchestrator_input_output_processors.htm
title: Input and Output Transformation Processors
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/dynamic_revenue_orchestrator_input_output_processors.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_callouts_overview.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

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
