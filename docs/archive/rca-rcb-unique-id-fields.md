# RCA / RCB Unique ID Fields (from Excel)

Objects with Unique ID Field values that are not NONE/blank.

## PCM (DATA)

| Object Name | Object API | Unique ID Field |
| --- | --- | --- |
| Tax Engine | TaxEngine | External Reference |

## QOC (DATA)

| Object Name | Object API | Unique ID Field |
| --- | --- | --- |
| App Usage Assignment | AppUsageAssignment | ID |
| Sales Transaction Type | SalesTransactionType | ID |
| Account | Account | ID |
| Contract | Contract | ID |
| Opportunity | Opportunity | ID |
| Opportunity Product | OpportunityLineItem | ID |
| Quote PDF | QuoteDocument | ID |
| Quote Template Rich Text Data | QuoteTemplateRichTextData | ID |
| Quote | Quote | ID |
| Quote Status | StandardValueSet | ID |
| Quote Action | QuoteAction | ID |
| Quote Line Group | QuoteLineGroup | ID |
| Quote Recipient Group | QuoteRecipientGroup | ID |
| Quote Recipient Group Member | QuoteRecipientGroupMember | ID |
| Quote Line Item | QuoteLineItem | ID |
| Quote Line Recipient | QuoteLineRecipient | ID |
| Quote Line Relationship | QuoteLineRelationship | ID |
| Quote Line Detail | QuoteLineDetail | ID |
| Quote Line Attribute | QuoteLineItemAttribute | ID |
| Quote Line Recipient | QuoteLineItemRecipient | ID |
| Quote Line Tax Line Item | QuoteItemTaxItem | ID |
| Quote Line Adjustment Line Item | QuoteLinePriceAdjustment | ID |
| Quote Line Rate Card Entry | QuoteLineRateCardEntry | ID |
| Quote Line Rate Adjustment | QuoteLineRateAdjustment | ID |
| Quote Line Usage Resource Grant | QuotLineItmUseRsrcGrant | ID |
| Quote Line Usage Resource Policy | QuotLineItmUsageRsrcPlcy | ID |
| Order | Order | ID |
| Order Status | StandardValueSet | ID |
| Order Action | OrderAction | ID |
| Order Delivery Method | OrderDeliveryMethod | ID |
| Order Delivery Group | OrderDeliveryGroup | ID |
| Order Product Group | OrderItemGroup | ID |
| Order Product | OrderItem | ID |
| Order Product Recipient | OrderItemRecipient | ID |
| Order Product Type | StandardValueSet | ID |
| Order Product Relationship | OrderItemRelationship | ID |
| Order Product Detail | OrderItemDetail | ID |
| Order Product Attribute | OrderItemAttribute | ID |
| Order Product Recipient | OrderItemRecipient | ID |
| Order Product Tax Line Item | OrderItemTaxLineItem | ID |
| Order Product Adjustment Line Item | OrderItemAdjustmentLineItem | ID |
| Order Product Rate Card Entry | OrderItemRateCardEntry | ID |
| Order Product Rate Adjustment | OrderItemRateAdjustment | ID |
| Order Product Usage Resource Grant | OrderItemUsageRsrcGrant | ID |
| Order Product Usage Resource Policy | OrderItemUsageRsrcPlcy | ID |
| Revenue Transaction Error Log | RevenueTransactionErrorLog | ID |
| Quote to Order Completed Event | QuoteToOrderCompletedEvent | ID |
| Place Order Completed Event | PlaceOrderCompletedEvent | ID |
| Quote Save Event | QuoteSaveEvent | ID |

## ASSET (DATA)

| Object Name | Object API | Unique ID Field |
| --- | --- | --- |
| Account | Account | ID |
| Asset | Asset | ID |
| Asset State Period | AssetStatePeriod | ID |
| Asset State Period Attribute | AssetStatePeriodAttribute | ID |
| Asset Action | AssetAction | ID |
| Asset Action Source | AssetActionSource | ID |
| Asset Relationship | AssetRelationship | ID |
| Asset Rate Card Entry | AssetRateCardEntry | ID |
| Asset Rate Adjustment | AssetRateAdjustment | ID |
| Usage Commitment Asset Related Object | UsageCmtAssetRelatedObj | ID |
| Revenue Transaction Error Log | RevenueTransactionErrorLog | ID |
| Create Asset Order Event | CreateAssetOrderEvent | ID |

## DRO (DATA)

| Object Name | Object API | Unique ID Field |
| --- | --- | --- |
| CustomFulfillmentScopeCnfg | Custom Fulfillment Scope Config | DeveloperName |

## CONTRACTS (DATA)

| Object Name | Object API | Unique ID Field |
| --- | --- | --- |
| Clause Category Configuration | ClauseCatgConfiguration | DeveloperName |
| Document Clause Set | DocumentClauseSet | ID |
| Document Clause | DocumentClause | ID |
| Document Template | DocumentTemplate | ID |

## USAGE (DATA)

| Object Name | Object API | Unique ID Field |
| --- | --- | --- |
| Usage Overage Policy | UsageOveragePolicy | OverageChargeable |
| Usage Commitment Policy | UsageCommitmentPolicy | Commitment Rate |
| Binding Object Custom Extension | BindingObjectCustomExtension | Name |
| Rating Frequency Policy | RatingFrequencyPolicy | Product
Usage Resource |
| Product Usage Resource | ProductUsageResource | Product
Usage Resource
Effective Start Date
Effective End Date |
| Rate Card Entry | RateCardEntry | Rate Card
EffectiveFrom
RateUoM
Product
Usage Resource
Product Selling Model
Status (Only when Active) |
| Usage Resource Policy | UsageResourcePolicy | Usage Resource |
| Product Usage Resource Policy | ProductUsageResourcePolicy | Product Usage Resource
Product Selling Model |
| Rate Adjustment By Tier | RateAdjustmentByTier | Rate Card Entry
Adjustment Type
Adjustment Value
Lower Bound |
| Rate Adjustment By Attribute | RateAdjustmentByAttribute | Rate Card Entry
Adjustment Type
Adjustment Value |
| Usage Commitment Asset Related Object | UsageCmtAssetRelatedObj | Asset
Related Object
Effective Start Date Time |

## Common Components (DATA)

| Object Name | Object API | Unique ID Field |
| --- | --- | --- |
| ContextDefinition | ContextDefinition | Title |
| ContextNode | ContextNode | ContextDefinitionVersion+Title |
| ContextAttribute | ContextAttribute | ContextNode+Title |
| ContextDefinitionFilter | ContextDefinitionFilter | ContextDefinitionVersion+ApiName |
| ContextDefinitionReference | ContextDefinitionReference | ContextDefinition+ReferenceContextDefinition |
| ContextMapping | ContextMapping | ContextDefinitionVersion+Title |
| ContextMappingIntent | ContextMappingIntent | MappingIntent+ContextMapping |
| Expression Set Definition | ExpressionSetDefinition | For every setup entity, the developer name is the unique ID |
| Expression Set Definition Version | ExpressionSetDefinitionVersion | For every setup entity, the developer name is the unique ID |
| Decision Table | DecisionTable | For every setup entity, the developer name is the unique ID |
| ExpsSetDefVersionExtlRef | ExpsSetDefVersionExtlRef | For every setup entity, the developer name is the unique ID |
| ExpsSetDefinitionExtlRef | ExpsSetDefinitionExtlRef | For every setup entity, the developer name is the unique ID |
