---
page_id: deployment_contracts_objects.htm
title: Salesforce Contracts Objects
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/deployment_contracts_objects.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Revenue Cloud Deployment
parent_page: deployment_appendix_A.htm
fetched_at: 2026-06-09
---

# Salesforce Contracts Objects

This table provides the deployment sequence, object types, API names, and lookup fields
for Salesforce Contracts in Revenue Cloud.

| Object Use Type | Object Name | Object API | Deployment Sequence | Lookup Fields (Foreign Keys) |
| --- | --- | --- | --- | --- |
| Metadata | Clause Category Configuration | ClauseCatgConfiguration | 1 | None |
| Configuration | Document Clause Set | DocumentClauseSet | 2 | ClauseCatgConfiguration |
| Configuration | Document Clause | DocumentClause | 3 | DocumentClauseSet, ContentDocument |
