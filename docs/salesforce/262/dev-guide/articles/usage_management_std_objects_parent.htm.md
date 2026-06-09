---
page_id: usage_management_std_objects_parent.htm
title: Usage Management Standard Objects
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/usage_management_std_objects_parent.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_overview.htm
fetched_at: 2026-06-09
---

# Usage Management Standard Objects

The Usage Management data model provides objects and fields to set up and manage
consumption of usage-based products.

- **[ProductUsageGrant](./sforce_api_objects_productusagegrant.htm.md)**  
  Represents the details of a grant associated with a resource, product, or service, such as the purchased quantity, renewal and rollover policy, and validity of the grant. This object is available in API version 62.0 and later.
- **[ProductUsageResource](./sforce_api_objects_productusageresource.htm.md)**  
  Represents the mapping of a product and its usage resources. This object is available in API version 64.0 and later.
- **[ProductUsageResourcePolicy](./sforce_api_objects_productusageresourcepolicy.htm.md)**  
  Represents the policies applicable to the usage resource when it’s associated with a sellable product. These policies are derived from the parent usage resource and can be overridden when setting up usage modeling.This object is available in API version 65 and later.
- **[TransactionUsageEntitlement](./sforce_api_objects_transactionusageentitlement.htm.md)**  
  Represents the details of each usage entitlement that's granted with the purchased sellable product, such as quantity and date when the entitlements were granted. This object is available in API version 63.0 and later.
- **[TransactionJournal](./sforce_api_objects_transactionjournal.htm.md)**  
  Represents consumption details of a usage resource that are recorded for creating usage summaries. This object is available for usage management in API version 63.0 and later.
- **[UnitOfMeasure](./sforce_api_objects_unitofmeasure.htm.md)**  
  Defines the units and systems of units used to account for quantities of a usage resource. This object is available for usage management in API version 62.0 and later.
- **[UnitOfMeasureClass](./sforce_api_objects_unitofmeasureclass.htm.md)**  
  Represents a standard unit of measure dimension. This object is available in API version 63.0 and later.
- **[UsageBillingPeriodItem](./sforce_api_objects_usagebillingperioditem.htm.md)**  
  Represents the calculated overages for the usage entitlement and the amount that's charged for these overages. This object is available in API version 63.0 and later.
- **[UsageCmtAssetRelatedObj](./sforce_api_objects_usagecmtassetrelatedobj.htm.md)**  
  Represents the relation between an asset for the commitment-based usage product and an asset, account, contract, or custom object. This object is available in API version 64.0 and later.
- **[UsageCommitmentPolicy](./sforce_api_objects_usagecommitmentpolicy.htm.md)**  
  Represents the set of rules that determines how commitments are applied to a usage resource. This object is available in API version 65 and later.
- **[UsageEntitlementAccount](./sforce_api_objects_usageentitlementaccount.htm.md)**  
  Represents the entitlement account details related to the asset that holds the wallet with the granted units. This object is available in API version 63.0 and later.
- **[UsageEntitlementBucket](./sforce_api_objects_usageentitlementbucket.htm.md)**  
  Represents a usage entitlement that's granted with the sellable product. This object is available in API version 63.0 and later.
- **[UsageEntitlementEntry](./sforce_api_objects_usageentitlemententry.htm.md)**  
  Represents the usage entitlement details, such as the usage consumption, rollovers, and details of expired units for each tenure. This object is available in API version 63.0 and later.
- **[UsageGrantRenewalPolicy](./sforce_api_objects_usagegrantrenewalpolicy.htm.md)**  
  Represents a policy about the rollover of a usage grant. This object is available in API version 62.0 and later.
- **[UsageGrantRolloverPolicy](./sforce_api_objects_usagegrantrolloverpolicy.htm.md)**  
  Represents a policy about the rollover of a usage grant.This object is available in API version 62.0 and later.
- **[UsageOveragePolicy](./sforce_api_objects_usageoveragepolicy.htm.md)**  
  Represents the set of rules that determine the management of usage resource’s units consumed beyond the granted limit. This object is available in API version 65 and later.
- **[UsagePrdGrantBindingPolicy](./sforce_api_objects_usageprdgrantbindingpolicy.htm.md)**  
  Represents the association of a usage resource's grants with a sellable product. This object is available in API version 63.0 and later.
- **[UsageRatableSummary](./sforce_api_objects_usageratablesummary.htm.md)**  
  Represents the aggregation of the usage summaries that are used to calculate the rate at which the overages are charged. This object is available in API version 63.0 and later.
- **[UsageRatableSumCmtAssetRt](./sforce_api_objects_usageratablesumcmtassetrt.htm.md)**  
  Represents the rate that’s calculated and applicable for the usage resource associated with the commitment assets related to an anchor. This object is available in API version 65.0 and later.
- **[UsageResource](./sforce_api_objects_usageresource.htm.md)**  
  Represents an entitlement granted to a user or party by a provider, such as data storage, computing power, bandwidth, or any other product or service. Additionally, this object is used to represent resources consumed over time. This object is available in API version 62.0 and later.
- **[UsageResourcePolicy](./sforce_api_objects_usageresourcepolicy.htm.md)**  
  Represents the policies applicable to the usage resource whether it’s associated with a sellable product or not. This object is available in API version 65 and later.
- **[UsageResourceBillingPolicy](./sforce_api_objects_usageresourcebillingpolicy.htm.md)**  
  Represents information about how the usage is accumulated before rating a usage resource.This object is available in API version 62.0 and later.
- **[UsageSummary](./sforce_api_objects_usagesummary.htm.md)**  
  Represents the aggregation of the entries in the transaction journal for a usage entitlement for a specified period. This object is available in API version 63.0 and later.

#### See Also

- [*Object Reference for the Salesforce Platform*: Overview of Salesforce Objects
  and Fields](https://developer.salesforce.com/docs/atlas.en-us.262.0.object_reference.meta/object_reference/sforce_api_objects_concepts.htm "Object Reference for the Salesforce Platform: Overview of Salesforce Objects
         and Fields  - HTML (New Window)")
- [*SOAP API Developer Guide*: Introduction to SOAP API](https://developer.salesforce.com/docs/atlas.en-us.262.0.api.meta/api/sforce_api_quickstart_intro.htm "SOAP API Developer Guide: Introduction to SOAP API - HTML (New Window)")
