---
page_id: sforce_api_objects_approvalsubmission.htm
title: ApprovalSubmission
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_approvalsubmission.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Advanced Approvals
parent_page: advanced_approval_fields_on_standard_objects.htm
fetched_at: 2026-06-09
---

# ApprovalSubmission

Represents the instance of an approval request that's submitted for a record
of the related object. This object is available in API version 62.0 and
later.

## Supported Calls

`describeLayout()`,
`describeSObjects()`,
`getDeleted()`,
`getUpdated()`,
`query()`,
`retrieve()`

## Special Access Rules

This object is available in Enterprise, Unlimited,
and Developer Editions of Revenue Cloud.

## Fields

| Field | Details |
| --- | --- |
| Comments | Type  textarea  Properties  Nillable  Description  The comments about the request that's submitted for approval. |
| DoesSendApprovalEmail | Type  boolean  Properties  Defaulted on create, Filter, Group, Sort  Description  Required. Indicates whether approval request emails are sent to approvers and delegates (`true`) or not (`false`).  The default value is `false`. |
| FlowOrchestrationInstanceId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The ID of the flow orchestration instance record that's associated with the approval.  This field is a relationship field.  Relationship Name  FlowOrchestrationInstance  Refers To  FlowOrchestrationInstance |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  The auto-generated name for the approval submission. |
| OwnerId | Type  reference  Properties  Filter, Group, Sort  Description  The ID of the user or the group that owns the approval submission record.  This field is a polymorphic relationship field.  Relationship Name  Owner  Refers To  Group, User |
| RelatedRecordId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  Required. The ID of the related record that's submitted for approval.  This field is a polymorphic relationship field.  Relationship Name  RelatedRecord  Refers To  Account, AdAvailabilityViewConfig, Address, AnalyticsUserAttrFuncTkn, ApprovalSubmission, ApprovalSubmissionDetail, ApprovalWorkItem, Asset, AssetAction, AssetActionSource, AssetContractRelationship, AssetRateAdjustment, AssetRateCardEntry, AssetRelationship, AssetStatePeriod, AssociatedLocation, AsyncOperationTracker, AttrPicklistExcludedValue, AttributeAdjustmentCondition, AttributeBasedAdjRule, AttributeBasedAdjustment, AttributeCategory, AttributeCategoryAttribute, AttributeDefinition, AttributePicklist, AttributePicklistValue, AuthorizationForm, AuthorizationFormConsent, AuthorizationFormDataUse, AuthorizationFormText, BatchJob, BatchJobPart, BatchJobPartFailedRecord, BundleBasedAdjustment, BusinessBrand, Case, CaseComment, ChannelProgram, ChannelProgramLevel, ChannelProgramMember, CollaborationGroup, CommSubscription, CommSubscriptionChannelType, CommSubscriptionConsent, CommSubscriptionTiming, Contact, ContactPointAddress, ContactPointConsent, ContactPointEmail, ContactPointPhone, ContactPointTypeConsent, ContactRequest, ContextDefinitionSync, Contract, ContractItemPrice, ContractItemPriceAdjTier, CostBook, CostBookEntry, Customer, DTRecordsetReplica, DataUseLegalBasis, DataUsePurpose, DecisionTblFileImportData, DelegatedAccount, DocGenerationQueryResult, DocTemplateSectionCondition, DocumentEnvelope, DocumentGenerationProcess, DocumentRecipient, DocumentTemplate, DocumentTemplateContentDoc, DocumentTemplateSection, DocumentTemplateToken, DuplicateRecordItem, DuplicateRecordSet, EmailMessage, EngagementChannelType, ExpressionSetConstraintObj, ExternalEventMapping, FlowOrchestrationInstance, FulfillmentOrder, FulfillmentOrderItemAdjustment, FulfillmentOrderItemTax, FulfillmentOrderLineItem, GeneratedDocument, GeneratedDocumentSection, Idea, Image, Individual, IntegrationProviderDcsnRqmt, IntegrationProviderExecution, Lead, Location, LocationTrustMeasure, ManagedContentVariant, ObjectStateDefinition, ObjectStateTransition, ObjectStateValue, Obligation, Opportunity, OpportunityRelatedDeleteLog, Order, OrderAction, OrderAdjustmentGroup, OrderDeliveryGroup, OrderDeliveryMethod, OrderItem, OrderItemAdjustmentLineItem, OrderItemDetail, OrderItemRateAdjustment, OrderItemRateCardEntry, OrderItemRecipient, OrderItemRelationship, OrderItemTaxLineItem, OrgMetricScanResult, OrgMetricScanSummary, Organization, PartnerFundAllocation, PartnerFundClaim, PartnerFundRequest, PartnerMarketingBudget, PartyConsent, PriceBookEntryDerivedPrice, PriceBookRateCard, PricingAdjBatchJob, PricingAdjBatchJobLog, PricingApiExecution, PricingProcessExecution, ProcessException, Product2, ProductAttributeDefinition, ProductCatalog, ProductCategory, ProductCategoryDisqual, ProductCategoryProduct, ProductCategoryQualification, ProductClassification, ProductClassificationAttr, ProductComponentGroup, ProductComponentGrpOverride, ProductConfigFlowAssignment, ProductConfigurationFlow, ProductConfigurationRule, ProductDisqualification, ProductPriceHistoryLog, ProductPriceRange, ProductQualification, ProductRampSegment, ProductRelComponentOverride, ProductUsageGrant, ProfileSkill, ProfileSkillEndorsement, ProfileSkillUser, PromptAction, PromptError, QuickText, QuickTextUsage, Quote, QuoteLineDetail, QuoteLineItem, QuoteLineItemRecipient, QuoteLineRateAdjustment, QuoteLineRateCardEntry, RateAdjustmentByAttribute, RateAdjustmentByTier, RateCard, RateCardEntry, RatingFrequencyPolicy, SalesTransactionType, Seller, Shipment, ShipmentItem, Site, SocialPersona, SocialPost, Solution, StreamingChannel, TableauHostMapping, Topic, UnitOfMeasure, UnitOfMeasureClass, UsageGrantRenewalPolicy, UsageGrantRolloverPolicy, UsageResource, UsageResourceBillingPolicy, User, UserEsignVendorIdentifier, UserLicense, UserLocalWebServerIdentity, UserProvisioningRequest, WorkBadge, WorkBadgeDefinition, WorkOrder, WorkOrderLineItem, WorkThanks |
| RelatedRecordObjectName | Type  string  Properties  Filter, Group, Nillable, Sort  Description  Required. The type of record that was submitted for approval. |
| Status | Type  picklist  Properties  Filter, Group, Restricted picklist, Sort  Description  Required. The status of the approval.  Valid values are:  - `Approved` - `Canceled` - `Errored` - `InProgress` - `Recalled` - `Rejected` - `Suspended` |
| SubmittedById | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  Required. The ID of the user who submitted the record for approval.  This field is a relationship field.  Relationship Name  SubmittedBy  Refers To  User |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[ApprovalSubmissionOwnerSharingRule](./sforce_api_associated_objects_ownersharingrule.htm.md "StandardObjectNameOwnerSharingRule is the model for all owner sharing rule objects associated with standard objects. These objects represent a rule for sharing a standard object with users other than the owner.")
:   Sharing rules are available for the object.

[ApprovalSubmissionShare](./sforce_api_associated_objects_share.htm.md "StandardObjectNameShare is the model for all share objects associated with standard objects. These objects represent a sharing entry on the standard object.")
:   Sharing is available for the object.
