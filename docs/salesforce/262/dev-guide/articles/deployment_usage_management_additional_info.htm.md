---
page_id: deployment_usage_management_additional_info.htm
title: Usage Management Additional Information
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/deployment_usage_management_additional_info.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Revenue Cloud Deployment
parent_page: deployment_appendix_C.htm
fetched_at: 2026-06-09
---

# Usage Management Additional Information

Get to know additional deployment information for Usage Management in Revenue Cloud,
including active or inactive states, object information, and migration
considerations.

## Object-Specific Information

| Object Name | Object API | Notes |
| --- | --- | --- |
| Rate Card | RateCard | - [Considerations for Migrating Decision   Tables](https://help.salesforce.com/s/articleView?id=ind.bre_decision_table_migration_considerations.htm&type=5&language=en_US) - [Considerations for Migrating Expression   Sets](https://help.salesforce.com/s/articleView?id=ind.considerations_for_migrating_expression_sets.htm&type=5&language=en_US) - [Migrate Context Definitions](https://help.salesforce.com/s/articleView?id=ind.context_service_context_definitions_packages.htm&type=5&language=en_US) |
| Price Book Rate Card | PriceBookRateCard | - [Considerations for Migrating Decision   Tables](https://help.salesforce.com/s/articleView?id=ind.bre_decision_table_migration_considerations.htm&type=5&language=en_US) - [Considerations for Migrating Expression   Sets](https://help.salesforce.com/s/articleView?id=ind.considerations_for_migrating_expression_sets.htm&type=5&language=en_US) - [Migrate Context Definitions](https://help.salesforce.com/s/articleView?id=ind.context_service_context_definitions_packages.htm&type=5&language=en_US) |
| Product Usage Resource | ProductUsageResource | Effective end date can be extended in Active state. |
| Rate Card Entry | RateCardEntry | - [Considerations for Migrating Decision   Tables](https://help.salesforce.com/s/articleView?id=ind.bre_decision_table_migration_considerations.htm&type=5&language=en_US) - [Considerations for Migrating Expression   Sets](https://help.salesforce.com/s/articleView?id=ind.considerations_for_migrating_expression_sets.htm&type=5&language=en_US) - [Migrate Context Definitions](https://help.salesforce.com/s/articleView?id=ind.context_service_context_definitions_packages.htm&type=5&language=en_US) - No updates are allowed in Active or Inactive state. |
| Product Usage Grant | ProductUsageGrant | The Effective End Date can be extended in Active state. |
| Rate Adjustment By Tier | RateAdjustmentByTier | - [Considerations for Migrating Decision   Tables](https://help.salesforce.com/s/articleView?id=ind.bre_decision_table_migration_considerations.htm&type=5&language=en_US) - [Considerations for Migrating Expression   Sets](https://help.salesforce.com/s/articleView?id=ind.considerations_for_migrating_expression_sets.htm&type=5&language=en_US) - [Migrate Context Definitions](https://help.salesforce.com/s/articleView?id=ind.context_service_context_definitions_packages.htm&type=5&language=en_US) |
| Rate Adjustment By Attribute | RateAdjustmentByAttribute | - [Considerations for Migrating Decision   Tables](https://help.salesforce.com/s/articleView?id=ind.bre_decision_table_migration_considerations.htm&type=5&language=en_US) - [Considerations for Migrating Expression   Sets](https://help.salesforce.com/s/articleView?id=ind.considerations_for_migrating_expression_sets.htm&type=5&language=en_US) - [Migrate Context Definitions](https://help.salesforce.com/s/articleView?id=ind.context_service_context_definitions_packages.htm&type=5&language=en_US) |
| Usage Commitment Asset Related Object | UsageCmtAssetRelatedObj | The RelatedObjectId lookup field is polymorphic. |

## Other Information

- For Selling (Revenue Cloud Advanced), perform these actions:
  - Confirm that Rates, Grants, and Policies for usage products are set up
    correctly.
  - Extend and sync the SalesTransaction context definition.
  - Confirm that the pricing procedure is active and set up correctly in Revenue
    Settings.
  - Refresh Decision Tables (DT) being referred in pricing procedures.
  - Set up and activate the rating discovery procedure.
  - Sync the RatingDiscovery context definition.
  - Refresh all Decision Tables (DTs) being used in the rating discovery procedure.
- For Consumption (Revenue Cloud Billing), perform these actions:
  - Clone and set up the Orchestration Flow.
  - Configure the Data Processing Engine (DPE) jobs.
  - Set up and activate the rating procedure.
  - Sync the Rate Management context definition.
  - Refresh all Decision Tables (DTs) being used in the rating procedure.

- These components have dependencies on Industries common Features:
  - Rating or Discovery Procedures: Expression Set
  - Rating, Discovery, or Selling Journey: Business Rules Engine and Context
    Service
  - Rating or summary creation: Batch and Data Processing Engine
- After migration, selling and consumption-related object records such as
  UnitOfMeasureClass, UsageResource, RateCardEntry, ProductUsageResource, ProductUsageGrant
  must be active before you use it.

For ProductUsageResource and ProductUsageGrant objects, review these
considerations.

- You can delete records in Draft or Inactive states. You can’t delete a record in Active
  state.
- After you activate a record, you can extend end date only.
- The applicable status transitions are Draft, Active, and Inactive.

You can edit a RateCardEntry object in Draft status only. You can’t edit this object
after you've activated it. The applicable status transitions are:

- Draft, Active, and Inactive
- Inactive and Active
