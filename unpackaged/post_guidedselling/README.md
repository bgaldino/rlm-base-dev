# Guided Selling Metadata

This bundle deploys the guided selling metadata used by the QuantumBit setup. The current integration adds the retrieved `QuantumBit Solution Builder` OmniScript as `GuidedSelling_Wizard_English_1`, related AssessmentQuestion metadata, and the three RLM-prefixed Product2 fields used by the new guided-selling product attributes.

## Product Fields

The connected org fields were renamed to the repo-standard `RLM_` API names before integration:

- `Primary_Goal__c` -> `RLM_Primary_Goal__c`
- `Timeline__c` -> `RLM_Timeline__c`
- `Platform_Control__c` -> `RLM_Platform_Control__c`

Product values are loaded separately by `datasets/sfdmu/qb/en-US/qb-guidedselling-products` after this metadata deploy. `RLM_Guided_Selling` grants Product2 object access and field-level access for the three guided-selling fields, and is assigned after this bundle deploys.

## Follow-Up Work

- Product Discovery settings were not changed in this pass. The connected org differs from the current metadata: `prodDiscQualificationOrgValue` is `RLM Product Discovery Qualification Procedure`, `promoContextMappingNameOrgValue` is `ProductDiscoveryPromoMapping`, and `prodDiscDefaultCatalogOrgValue` contains the org-specific record Id `0ZSHn000000xTT5OAM` that must not be committed directly.
- Cleanup or replacement of older guided selling artifacts is intentionally deferred.
- Retrieved OmniStudio SFDMU data was not integrated into `qb-guidedselling`; any data-plan redesign should be handled separately.
