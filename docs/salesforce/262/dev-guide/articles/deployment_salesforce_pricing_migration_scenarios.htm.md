---
page_id: deployment_salesforce_pricing_migration_scenarios.htm
title: Salesforce Pricing Migration Scenarios
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/deployment_salesforce_pricing_migration_scenarios.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Revenue Cloud Deployment
parent_page: deployment_salesforce_pricing_additional_info.htm
fetched_at: 2026-06-09
---

# Salesforce Pricing Migration Scenarios

Review these considerations to understand the Salesforce Pricing data migration process
along with migration order and prerequisites.

Here are the possible migration scenarios.

- One sandbox org to another sandbox org
- Sandbox org to production org

To migrate pricing procedures, see [Export and Import Procedure
Plans](https://help.salesforce.com/s/articleView?id=ind.pricing_export_and_import_procedure_plans.htm&language=en_US "HTML (New Window)").

To import and export pricing data, see [Considerations for Importing and
Exporting Pricing Data](https://help.salesforce.com/s/articleView?id=ind.pricing_considerations_for_importing_and_exporting_pricing_data.htm&language=en_US "HTML (New Window)"). Keep these considerations in mind for first-time
migration.

## First-Time Migration

- You must migrate metadata in this specific sequence to ensure a successful deployment.
  - You must migrate context definitions before any pricing procedures. If multiple
    pricing procedures are linked to various context definitions, include all associated
    definitions in the migration.
  - You must deploy all decision tables (DTs) before you migrate the pricing procedures
    that reference them.
  - Pricing recipe migration also migrates the associated default pricing
    procedure.
- You must manually refresh decision tables after migration within the target environment
  to make sure that the data is updated and active. If a decision table migration encounters
  missing metadata, such as a custom field or element, the deployment fails.
- You must manually update any pricing procedure constants that contain reference sandbox
  org IDs to the corresponding production org IDs. This step is required before migration to
  avoid logic failures in the production environment.
- You must manually update the price adjustment schedule IDs in the pricing procedure
  constants of the production org before or after migration.

## Subsequent Production Migrations

- You must migrate context definitions before you migrate pricing procedures. If multiple
  pricing procedures are linked to various context definitions, then you must migrate all
  associated metadata to ensure system integrity.
- You must migrate decision tables along with any relevant metadata changes. If a decision
  table migration fails, the system must roll back to the previous snapshot, making sure
  that the existing decision tables are usable.
- You must migrate pricing procedures and expression set versions after the successful
  deployment of context definitions, decision tables, and pricing recipes in a sequential
  order.
