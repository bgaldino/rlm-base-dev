# CLM Setup and Diagnostics

Use release-matched Salesforce Contracts Help as the operational checklist.
Begin with the implementation landing page, then follow the setup articles for
the feature in use. For 264, the key entry points are:

- [Implementation overview](../../../docs/salesforce/264/help/articles/ind.sf_contracts_get_started_with_salesforce_contracts_implementation.htm.md)
- [Personas and permission-set licenses](../../../docs/salesforce/264/help/articles/ind.sf_contracts_permission_set_licenses_for_salesforce_contracts_.htm.md)
- [Permission-set combinations](../../../docs/salesforce/264/help/articles/ind.sf_contracts_permission_sets_combination_for_salesforce_contracts.htm.md)
- [Contract types and record types](../../../docs/salesforce/264/help/articles/ind.sf_contracts_contract_types_contract_record_types_and_contract_type_configs.htm.md)
- [State models and transitions](../../../docs/salesforce/264/help/articles/ind.sf_contracts_state_models_transitions_and_actions.htm.md)
- [Context Service for contract creation and updates](../../../docs/salesforce/264/help/articles/ind.sf_contracts_configure_context_services_to_create_and_update_contracts.htm.md)

## Setup areas to inspect

1. **Availability and access:** CLM feature enablement, org edition and licenses,
   user permission-set licenses, permission sets, profiles, sharing, and file
   access. The exact combination depends on persona and enabled features; follow
   the snapshot's persona/license table rather than assigning every CLM license.
2. **Contract creation:** contract and document record types, contract types and
   type configurations, default record types, and any applicable Context Service
   use-case, hydration, and persistence mappings.
3. **Lifecycle:** state definitions, values, transitions, transition actions,
   access/sharing, and status picklist alignment. Check whether the configuration
   applies to Contract or another object and its `AppUsageType`.
4. **Authoring:** clause category configuration, document clause sets and clause
   versions; document template records and related content files; token and
   document-generation settings.
5. **Integrations:** treat Microsoft 365/Azure, e-signature, community users,
   Contracts AI, contract search, analytics, and obligations as separate optional
   capabilities with their own licensing and prerequisites.

## Foundations-specific setup

- `clm` gates Salesforce Contracts metadata/permissions and related context
  extensions; `clm_data` controls loading CLM sample data. Inspect current
  `cumulusci.yml` before changing the feature plan.
- `assign_feature_psls` assigns the repository's CLM permission-set licenses
  when `clm` is enabled. The `RLM_CLM` permission-set group contains CLM admin,
  clause designer, document-generation designer, Microsoft Word designer, and
  obligation manager permissions. This is what the repo ships; check the target
  release and user's task before assuming those assignments are sufficient.
- The `qb-clm` data plan seeds clause category configurations, clause sets, and
  state-model definitions, values, transitions, and actions. It does not seed
  clause bodies or a complete template library.
- Contract context extensions are included in the context-definition build flow
  behind the `clm` flag. Trace the flow sequence and enabled feature flags before
  diagnosing a missing context definition.

## Troubleshooting sequence

1. Confirm the org release/API version and the specific CLM capability involved.
2. Check feature enablement and required license assignment.
3. Check object permissions, record sharing, file access, and record types for the
   affected persona.
4. Verify required metadata and record configuration exist and are active.
5. Follow lookup and lifecycle dependencies with the data-model and query guide.
6. For generated documents, verify template status/version, related file, token
   data, and generation settings; continue in `document-generation`/`odt-authoring`.
7. For creation/update failures, verify Context Service mappings and use-case
   configuration; continue in `context-service`.

Never diagnose a permission failure as a missing record without checking access.
A zero-row query can mean no data, sharing restrictions, or a filter that does not
match; use an appropriately privileged sandbox admin for controlled diagnosis.
