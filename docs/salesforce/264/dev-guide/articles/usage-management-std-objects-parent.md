---
page_id: usage-management-std-objects-parent
title: Usage Management Standard Objects
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/usage-management-std-objects-parent.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Usage Management
parent_page: usage-management-overview
legacy_page_id: usage_management_std_objects_parent.htm
fetched_at: 2026-11-25
---

# Usage Management Standard Objects

The Usage Management data model provides objects and fields to set up and manage consumption of usage-based products.

- 

**[ProductUsageGrant](./sforce-api-objects-productusagegrant.md)**

Represents the details of a grant associated with a resource, product, or service, such as the purchased quantity, renewal and rollover policy, and validity of the grant. This object is available in API version 62.0 and later.

- 

**[ProductUsageResource](./sforce-api-objects-productusageresource.md)**

Represents the mapping of a product and its usage resources. This object is available in API version 64.0 and later.

- 

**[ProductUsageResourcePolicy](./sforce-api-objects-productusageresourcepolicy.md)**

Represents the policies applicable to the usage resource when it’s associated with a sellable product. These policies are derived from the parent usage resource and can be overridden when setting up usage modeling.This object is available in API version 65 and later.

- 

**[TransactionUsageEntitlement](./sforce-api-objects-transactionusageentitlement.md)**

Represents the details of each usage entitlement that’s granted with the purchased sellable product, such as quantity and date when the entitlements were granted. This object is available in API version 63.0 and later.

- 

**[TransactionJournal](./sforce-api-objects-transactionjournal.md)**

Represents consumption details of a usage resource that are recorded for creating usage summaries. This object is available for usage management in API version 63.0 and later.

- 

**[UnitOfMeasure](./sforce-api-objects-unitofmeasure.md)**

Defines the units and systems of units used to account for quantities of a usage resource. This object is available for usage management in API version 62.0 and later.

- 

**[UnitOfMeasureClass](./sforce-api-objects-unitofmeasureclass.md)**

Represents a standard unit of measure dimension. This object is available in API version 63.0 and later.

- 

**[UsageBillingPeriodItem](./sforce-api-objects-usagebillingperioditem.md)**

Represents the calculated overages for the usage entitlement and the amount that’s charged for these overages. This object is available in API version 63.0 and later.

- 

**[UsageCmtAssetRelatedObj](./sforce-api-objects-usagecmtassetrelatedobj.md)**

Represents the relation between an asset for the commitment-based usage product and an asset, account, contract, or custom object. This object is available in API version 64.0 and later.

- 

**[UsageCommitmentPolicy](./sforce-api-objects-usagecommitmentpolicy.md)**

Represents the set of rules that determines how commitments are applied to a usage resource. This object is available in API version 65 and later.

- 

**[UsageEntitlementAccount](./sforce-api-objects-usageentitlementaccount.md)**

Represents the entitlement account details related to the asset that holds the wallet with the granted units. This object is available in API version 63.0 and later.

- 

**[UsageEntitlementBucket](./sforce-api-objects-usageentitlementbucket.md)**

Represents a usage entitlement that’s granted with the sellable product. This object is available in API version 63.0 and later.

- 

**[UsageEntitlementEntry](./sforce-api-objects-usageentitlemententry.md)**

Represents the usage entitlement details, such as the usage consumption, rollovers, and details of expired units for each tenure. This object is available in API version 63.0 and later.

- 

**[UsageGrantRenewalPolicy](./sforce-api-objects-usagegrantrenewalpolicy.md)**

Represents a policy about the rollover of a usage grant. This object is available in API version 62.0 and later.

- 

**[UsageGrantRolloverPolicy](./sforce-api-objects-usagegrantrolloverpolicy.md)**

Represents a policy about the rollover of a usage grant.This object is available in API version 62.0 and later.

- 

**[UsageOveragePolicy](./sforce-api-objects-usageoveragepolicy.md)**

Represents the set of rules that determine the management of usage resource’s units consumed beyond the granted limit. This object is available in API version 65 and later.

- 

**[UsagePrdGrantBindingPolicy](./sforce-api-objects-usageprdgrantbindingpolicy.md)**

Represents the association of a usage resource’s grants with a sellable product. This object is available in API version 63.0 and later.

- 

**[UsageRatableSummary](./sforce-api-objects-usageratablesummary.md)**

Represents the aggregation of the usage summaries that are used to calculate the rate at which the overages are charged. This object is available in API version 63.0 and later.

- 

**[UsageRatableSumCmtAssetRt](./sforce-api-objects-usageratablesumcmtassetrt.md)**

Represents the rate that’s calculated and applicable for the usage resource associated with the commitment assets related to an anchor. This object is available in API version 65.0 and later.

- 

**[UsageResource](./sforce-api-objects-usageresource.md)**

Represents an entitlement granted to a user or party by a provider, such as data storage, computing power, bandwidth, or any other product or service. Additionally, this object is used to represent resources consumed over time. This object is available in API version 62.0 and later.

- 

**[UsageResourcePolicy](./sforce-api-objects-usageresourcepolicy.md)**

Represents the policies applicable to the usage resource whether it’s associated with a sellable product or not. This object is available in API version 65 and later.

- 

**[UsageResourceBillingPolicy](./sforce-api-objects-usageresourcebillingpolicy.md)**

Represents information about how the usage is accumulated before rating a usage resource.This object is available in API version 62.0 and later.

- 

**[UsageSummary](./sforce-api-objects-usagesummary.md)**

Represents the aggregation of the entries in the transaction journal for a usage entitlement for a specified period. This object is available in API version 63.0 and later.

**See Also**

- [*Object Reference for the platform*: Overview of Salesforce Objects and Fields](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_concepts.htm)

- [*SOAP API Developer Guide*: Introduction to SOAP API](https://developer.salesforce.com/docs/atlas.en-us.api.meta/api/sforce_api_quickstart_intro.htm)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/usage-management-std-objects-parent.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
