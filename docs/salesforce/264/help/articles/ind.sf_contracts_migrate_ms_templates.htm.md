---
article_id: ind.sf_contracts_migrate_ms_templates.htm
title: Considerations When Migrating Microsoft 365 Word Templates Across Environments
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_migrate_ms_templates.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_integration_ms365_overview.htm
fetched_at: 2026-10-13
---

# Considerations When Migrating Microsoft 365 Word Templates Across Environments

When you move Microsoft 365 document templates between Salesforce orgs, such as from a sandbox to a production org, the structure, clause relationships, and section-level access controls are preserved. Before migrating a template, keep these considerations in mind.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, Professional, and Developer Editions
How Reference Preservation Works

Template migration requires that all clause records, clause versions, and related profile data already exist in the target org. Migrate this data separately by using a data migration tool. If a referenced clause is missing in the target org, template migration stops to prevent broken references. See Clause Migration Considerations, and Clause Validations and Migration Constraints.

Template migration relies on built-in key mapping to resolve references in the target org. When the required data is available, migration preserves:

Clause references, including clause versions
Section structure within the template
Section-level access controls tied to profiles

This alignment helps maintain template integrity and reduces the need for manual corrections after migration.

Considerations
Before migrating a template, move all clause records, clause versions, and related profile data to the target org.
To prevent reference mismatches, don’t modify the clause data in the source or target org between clause migration and template migration.
If a template uses custom fields in token mappings, migrate those fields to the target org before migration.
Use unique names for clauses and clause sets to prevent references from failing or resolving incorrectly.
Before migrating, make sure that all referenced clauses are active in the target org.
Make sure that all referenced profiles exist and are uniquely named in the target org.
When creating a custom profile, don’t use the reserved profile names PT1 through PT14.
Depending on template content, migrating many templates at one time can exceed metadata size limits.
SEE ALSO
Export and Import of Document Templates in Salesforce Orgs
