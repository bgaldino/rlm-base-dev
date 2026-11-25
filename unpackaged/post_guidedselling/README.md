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

## Step Images

The `Solution Explorer` OmniScript (`omniScripts/QuantumBit_GuidedSelling_English_1.os-meta.xml`) shows the QuantumBit logo in the instruction text of `Step1` and `Step2`. Each image references the `RLM_quantum_bit_logo` static resource by the relative path `/resource/RLM_quantum_bit_logo`, so it resolves in whichever org the bundle is deployed to. The resource ships in `force-app/main/default/staticresources/` (deployed by `deploy_full` on every build) rather than in this bundle or `unpackaged/post_quantumbit`, so within a full build, where `prepare_rlm_org` step 5 → `deploy_full` runs before `prepare_rlm_org` step 25 → `prepare_guidedselling`, the image resolves whatever the `guidedselling` and `quantumbit` flags are set to.

An org built before this change with `quantumbit` off has no `RLM_quantum_bit_logo`. On such an org, deploy that static resource (or run `deploy_full`) before running `deploy_post_guidedselling` on its own; until then both step images point at a resource that does not resolve. Orgs built from this version onward get it from `deploy_full` whatever the flags.

To add or change a step image, ship the file as a static resource and reference it as `/resource/<name>`. Do not retrieve an image inserted through the designer's rich-text editor as it stands: the two images this bundle used to carry were stored that way, as absolute `servlet.ImageServer` URLs naming the source org's host, org ID and Document IDs, and broke once that org expired.

## Follow-Up Work

- The connected org has additional Product Discovery setting values (`prodDiscQualificationOrgValue`, `promoContextMappingNameOrgValue`, `prodDiscDefaultCatalogOrgValue`) that differ from what's currently deployed. These require either Robot-based configuration or a non-hardcoded approach (the default catalog contains an org-specific record Id).
- Cleanup or replacement of older guided selling artifacts is intentionally deferred.
