---
page_id: deployment_contracts_additional_info.htm
title: Salesforce Contracts Additional Information
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/deployment_contracts_additional_info.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Revenue Cloud Deployment
parent_page: deployment_appendix_C.htm
fetched_at: 2026-06-09
---

# Salesforce Contracts Additional Information

Get to know additional deployment information for Salesforce Contracts in Revenue
Cloud, including active or inactive states, and migration considerations.

Document clauses can be in different states, such as Draft, In Approval, Active, and
Archived. Keep these considerations in mind regarding the clause statuses.

- A clause is created in Draft status.
- During the import process, the clause must be in Draft status. You can update the status
  after you complete the import process.
- An archived clause can’t be updated.
- An active clause can’t be updated, but it can change to Draft status only if it’s not
  used.
- An active clause must be moved to Draft status before you update it to Active
  status.

- **[Clause Migration Considerations](./deployment_contracts_clause_migration.htm.md)**  
  Clause migration is a prerequisite for Microsoft 365 template migration. Review these considerations to understand how clause structure, versions, and relationships must exist in the target org before migrating document templates.
- **[Clause Validations and Migration Constraints](./deployment_contracts_clause_validation_migration_constraints.htm.md)**  
  Validation rules, data model constraints, and known migration behaviors that affect clause records during migration. Review this reference to understand sequencing, status handling, and dependency requirements that can impact migration success.
