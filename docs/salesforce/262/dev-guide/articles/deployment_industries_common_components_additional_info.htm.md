---
page_id: deployment_industries_common_components_additional_info.htm
title: Business Rules Engine and Decision Tables Additional Information
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/deployment_industries_common_components_additional_info.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Revenue Cloud Deployment
parent_page: deployment_appendix_C.htm
fetched_at: 2026-06-09
---

# Business Rules Engine and Decision Tables Additional Information

Get to know additional Revenue Cloud deployment information for Industries common
features such as Business Rules Engine, Expression Sets, and Decision Tables.

## Object-Specific Information

| Object Name | Object API | Notes |
| --- | --- | --- |
| Expression Set Definition | ExpressionSetDefinition | Only call the setup object via Metadata API to get child setup objects. |
| Expression Set Definition Version | ExpressionSetDefinitionVersion | Only call the setup object via Metadata API to get child setup objects. |
| Rule Library | RuleLibrary | Not supported by Metadata API. |
| Rule Library Version | RuleLibraryVersion | Not supported by Metadata API. |

## Helpful Links

- [Considerations for Migrating
  Expression Sets](https://help.salesforce.com/s/articleView?id=ind.considerations_for_migrating_expression_sets.htm&language=en_US "HTML (New Window)")
- [Migration of Expression Sets with
  Dependencies](https://help.salesforce.com/s/articleView?id=ind.how_to_migrate_expression_sets_with_dep.htm&language=en_US "HTML (New Window)")

## Deployment Considerations

- Initial Deployment—Expression Sets Decision Tables can be deployed in any state
  during their first deployment to a target org.
- Subsequent Updates—To update an expression set that exists in the target org,
  migrate a new expression set version with the updates. You must not update the existing
  active version.
- When deploying an active decision table, it goes through activation again in the target
  org and may fail if the required custom object isn’t present in the target org.
- Two expression set versions of the same parent expression set can't have the same rank,
  regardless of the `Draft` or `Active` states. In this case:
  - Create an expression set version in the source org with the updates.
  - Activate the new version in the source org.
  - Then, migrate the new version or the entire expression set to the target org.
  - The migrated expression set version is invoked in the target org as per the
    specified rank.
  - Migration fails if the target org contains an expression set version with the
    specified rank.
- Activate and refresh of decision tables after deployment.
- Activate sub expressions after deployment.
- Dynamic rules are stored in platform objects, and not in setup objects. There's no
  platform support for deploying dynamic rules.

## Dependencies

- Industries common features can have dependencies among themselves. For example,
  expression sets can have sub expressions and reference decision tables or context
  definitions. Decision Tables can have a dependency on a custom object, and so on.
- For a deployment to be successful, all dependent components must be migrated correctly
  before the expression set version itself.
- You must migrate dependencies before the expression sets that reference them. If there
  are nested dependencies, you must migrate the lowest-level components first. Here's a
  general deployment order.
  - Standard and custom objects
  - Context Definitions, Decision Tables, Decision Matrices, Object Aliases, and
    Explainability Message Templates
  - Sub Expression Sets
  - Parent Expression Set Version

## Other Information

- Both Expression Set and Decision Matrix have versioned objects.
- Decision Tables don’t have versions.
