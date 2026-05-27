# Guided Selling Metadata

This bundle deploys the guided selling metadata used by the QuantumBit setup. The current integration adds the retrieved `QuantumBit Solution Builder` OmniScript as `GuidedSelling_Wizard_English_1`, related AssessmentQuestion metadata, and the three RLM-prefixed Product2 fields used by the new guided-selling product attributes.

## Product Fields

The connected org fields were renamed to the repo-standard `RLM_` API names before integration:

- `Primary_Goal__c` -> `RLM_Primary_Goal__c`
- `Timeline__c` -> `RLM_Timeline__c`
- `Platform_Control__c` -> `RLM_Platform_Control__c`

Product values are loaded separately by `datasets/sfdmu/qb/en-US/qb-guidedselling-products` after this metadata deploy. `RLM_Guided_Selling` grants Product2 object access and field-level access for the three guided-selling fields, and is assigned after this bundle deploys.

## Product Discovery Settings

This bundle deploys only `enableGuidedSelling: true` via `settings/ProductDiscovery.settings-meta.xml`. The remaining Product Discovery settings (qualification procedure, pricing procedure, context definition, default catalog) are managed by `unpackaged/pre/2_settings` and the `configure_product_discovery_settings` Robot task. They are not part of this bundle.

## Follow-Up Work

- The connected org has additional Product Discovery setting values (`prodDiscQualificationOrgValue`, `promoContextMappingNameOrgValue`, `prodDiscDefaultCatalogOrgValue`) that differ from what's currently deployed. These require either Robot-based configuration or a non-hardcoded approach (the default catalog contains an org-specific record Id).
- Cleanup or replacement of older guided selling artifacts is intentionally deferred.
- Retrieved OmniStudio SFDMU data was not integrated into `qb-guidedselling`; any data-plan redesign should be handled separately.
