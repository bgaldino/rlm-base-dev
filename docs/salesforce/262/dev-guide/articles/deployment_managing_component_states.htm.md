---
page_id: deployment_managing_component_states.htm
title: Managing Component States
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/deployment_managing_component_states.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Revenue Cloud Deployment
parent_page: deployment_overview.htm
fetched_at: 2026-06-09
---

# Managing Component States

Manage activation, versioning, and dependencies for components and objects as part of
your deployment plan. A successful deployment makes sure that the system executes the intended,
final, and active logic, preventing failures caused by stale or inactive component
dependencies.

A component's state is its operational status, which includes the:

- Active, inactive, or draft state
- Component version
- Dependencies on other components and objects
- Component-specific attributes like rank on expression sets

Components like decision tables, expression sets, and context definitions must be deployed
taking their state into account. Also, some objects use an Active checkbox to determine if
their records must be used during run time operations or not.

You must also make sure that all related dependencies are moved correctly and in the proper
sequence from the source org to the target org.

## State Management Scenarios

Component deployments usually fall into one of these categories:

Deploy a New Component
:   If the target org doesn’t contain the component that you want to migrate, deploy it
    along with its versions from the source org to the target org.

Deploy Component Updates
:   When the target org already contains the component you want to migrate, then state and
    version management take effect. For example, with expression sets, you must deactivate
    the version in the target org where you want to deploy changes. If you try to deploy to
    an active version, the deployment fails.

Deploy Components with Dependencies
:   All related dependencies must be moved correctly and in the proper sequence from the
    source org to the target org. For example, expression sets reference elements such as
    decision matrices, decision tables, subexpressions, context definitions, field and
    object aliases, and explainability message templates. Migrate the dependent elements independently before you migrate the expression set version.

## Helpful Links

Refer to these links for examples and component-specific information:

- [Considerations for Migrating Decision Tables](https://help.salesforce.com/s/articleView?id=ind.bre_decision_table_migration_considerations.htm&language=en_US)
- [Considerations for Migrating Expression Sets](https://help.salesforce.com/s/articleView?id=ind.considerations_for_migrating_expression_sets.htm&language=en_US)
- [Migration of Expression Sets with
  Dependencies](https://help.salesforce.com/s/articleView?id=ind.how_to_migrate_expression_sets_with_dep.htm&language=en_US)
- [Migrate Context Definitions](https://help.salesforce.com/s/articleView?id=ind.context_service_context_definitions_packages.htm&language=en_US)

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=revenue_lifecycle_management_dev_guide)

#### Note

Some Revenue Cloud components have unique activation requirements. For
complete information about state management for these components, see [Additional Deployment Information](./deployment_appendix_C.htm.md "Get to know additional deployment information for each Revenue Cloud feature domain, ensuring successful deployments and migrations.").
