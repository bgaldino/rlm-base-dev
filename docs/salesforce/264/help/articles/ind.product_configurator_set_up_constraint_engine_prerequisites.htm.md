---
article_id: ind.product_configurator_set_up_constraint_engine_prerequisites.htm
title: Create Custom Field and Define Apex Triggers
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_set_up_constraint_engine_prerequisites.htm&type=5&release=264
release: 264
release_name: Winter '27
area: configurator
parent_article: ind.product_configurator_set_up_constraints_engine.htm
fetched_at: 2026-09-04
---

# Create Custom Field and Define Apex Triggers

Create the necessary custom fields and define Apex triggers on the Quote Line Item and Order Product (OrderItem) objects.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Growth license or the Revenue Cloud Advanced license
Create the ConstraintEngineNodeStatus Custom Field

Create a custom field on the Quote Line Item, Order Product, and Asset Action Source objects to store data that Constraint Rules Engine uses for internal processing.

Go to the object management settings of these objects, and create a custom field with these values:

Select Text Area (Long) as the data type.
Enter Constraint Engine Node Status as the field label.
Enter 131072 as the length.
Enter ConstraintEngineNodeStatus as the field name.
Select Visible access and deselect Read-Only access for the profiles of the users who'll use Constraint Rules Engine, and Customer Community and Partner Community users.
Deselect the page layouts.

See Create a Custom Field.

Define Apex Triggers for Quote and Order Line Items

Define triggers for the Quote Line Item and Order Product (OrderItem) objects by using Apex code.

Use this Apex code for the Quote Line Item object.

trigger QuoteItemTrigger on QuoteLineItem (before insert) {
   //collect QuoteActionIds 
   Set<Id> quoteActionIds = new Set<Id>();
   
   for (QuoteLineItem qi : Trigger.new) {
   if (qi.QuoteActionId != null && qi.ConstraintEngineNodeStatus__c == null) {
   quoteActionIds.add(qi.QuoteActionId);
   }
   }
   
   if (!quoteActionIds.isEmpty()) {
   // Step 1: Get QuoteAction → SourceAsset
   Map<Id, Id> quoteActionToAssetId = new Map<Id, Id>();
   for (QuoteAction qAction : [
   SELECT Id, SourceAssetId 
   FROM QuoteAction 
   WHERE SourceAssetId != null 
   AND Id IN :quoteActionIds
   ]) {
   quoteActionToAssetId.put(qAction.Id, qAction.SourceAssetId);
   }
   
   // Step 2: Get AssetActions
   List<AssetAction> assetActions = [
   SELECT Id, AssetId, ActionDate 
   FROM AssetAction 
   WHERE AssetId IN :quoteActionToAssetId.values()
   ];
   
   // Step 3: Get latest AssetAction per Asset
   Map<Id, AssetAction> assetIdToLatestAction = new Map<Id, AssetAction>();
   for (AssetAction aAction : assetActions) {
   AssetAction existing = assetIdToLatestAction.get(aAction.AssetId);
   if (existing == null || aAction.ActionDate > existing.ActionDate) {
   assetIdToLatestAction.put(aAction.AssetId, aAction);
   }
   }
   
   // Step 4: Get related AssetActionSource records
   Map<Id, Id> assetIdToActionId = new Map<Id, Id>();
   for (Id assetId : assetIdToLatestAction.keySet()) {
   assetIdToActionId.put(assetId, assetIdToLatestAction.get(assetId).Id);
   }
   
   List<AssetActionSource> assetActionSources = [
   SELECT ConstraintEngineNodeStatus__c, AssetAction.AssetId 
   FROM AssetActionSource 
   WHERE AssetActionId IN :assetIdToActionId.values() ORDER BY CreatedDate DESC
   ];
   // Step 5: Map AssetId → Status
   Map<Id, String> assetIdToStatus = new Map<Id, String>();
   for (AssetActionSource actionSource : assetActionSources) {
   if (!assetIdToStatus.containsKey(actionSource.AssetAction.AssetId) && 
   actionSource.ConstraintEngineNodeStatus__c != null) {
   assetIdToStatus.put(
   actionSource.AssetAction.AssetId, 
   actionSource.ConstraintEngineNodeStatus__c
   );
   }
   }
   List<QuoteLineItem> toUpdate = new List<QuoteLineItem>();
   // Step 6: Set ConstraintEngineNodeStatus__c directly on Trigger.new records
   for (QuoteLineItem qi : Trigger.new) {            
   if (qi.QuoteActionId != null && qi.ConstraintEngineNodeStatus__c == null) {
   Id assetId = quoteActionToAssetId != null ? quoteActionToAssetId.get(qi.QuoteActionId) : null;
   if (assetId != null && assetIdToStatus != null) {
   String status = assetIdToStatus.get(assetId);
   if (status != null) {
   qi.ConstraintEngineNodeStatus__c = status;
   }
   }
   }
   }
   }
   }

Use this Apex code for the Order Product (OrderItem) object.

trigger OrderItemTrigger on OrderItem  (before insert) {
  //collect orderActionIds
  Set<Id> orderActionIds = new Set<Id>();
 
  for (OrderItem oi : Trigger.new) {
  if (oi.OrderActionId != null && oi.ConstraintEngineNodeStatus__c == null) {
  orderActionIds.add(oi.OrderActionId);
  }
  }
 
  if (!orderActionIds.isEmpty()) {
  // Step 1: Get OrderAction → SourceAsset
  Map<Id, Id> orderActionToAssetId = new Map<Id, Id>();
  for (OrderAction oAction : [
  SELECT Id, SourceAssetId
  FROM OrderAction
  WHERE SourceAssetId != null
  AND Id IN :orderActionIds
  ]) {
  orderActionToAssetId.put(oAction.Id, oAction.SourceAssetId);
  }
 
  // Step 2: Get AssetActions
  List<AssetAction> assetActions = [
  SELECT Id, AssetId, ActionDate
  FROM AssetAction
  WHERE AssetId IN :orderActionToAssetId.values()
  ];
 
  // Step 3: Get latest AssetAction per Asset
  Map<Id, AssetAction> assetIdToLatestAction = new Map<Id, AssetAction>();
  for (AssetAction aAction : assetActions) {
  AssetAction existing = assetIdToLatestAction.get(aAction.AssetId);
  if (existing == null || aAction.ActionDate > existing.ActionDate) {
  assetIdToLatestAction.put(aAction.AssetId, aAction);
  }
  }
 
  // Step 4: Get related AssetActionSource records
  Map<Id, Id> assetIdToActionId = new Map<Id, Id>();
  for (Id assetId : assetIdToLatestAction.keySet()) {
  assetIdToActionId.put(assetId, assetIdToLatestAction.get(assetId).Id);
  }
 
  List<AssetActionSource> assetActionSources = [
  SELECT ConstraintEngineNodeStatus__c, AssetAction.AssetId
  FROM AssetActionSource
  WHERE AssetActionId IN :assetIdToActionId.values() ORDER BY CreatedDate DESC
  ];
  // Step 5: Map AssetId → Status
  Map<Id, String> assetIdToStatus = new Map<Id, String>();
  for (AssetActionSource actionSource : assetActionSources) {
  if (!assetIdToStatus.containsKey(actionSource.AssetAction.AssetId) &&
  actionSource.ConstraintEngineNodeStatus__c != null) {
  assetIdToStatus.put(
  actionSource.AssetAction.AssetId,
  actionSource.ConstraintEngineNodeStatus__c
  );
  }
  }
  List<OrderItem> toUpdate = new List<OrderItem>();
  // Step 6: Set ConstraintEngineNodeStatus__c directly on Trigger.new records
  for (OrderItem oi : Trigger.new) {           
  if (oi.OrderActionId != null && oi.ConstraintEngineNodeStatus__c == null) {
  Id assetId = orderActionToAssetId != null ? orderActionToAssetId.get(oi.OrderActionId) : null;
  if (assetId != null && assetIdToStatus != null) {
  String status = assetIdToStatus.get(assetId);
  if (status != null) {
  oi.ConstraintEngineNodeStatus__c = status;
  }
  }
  }
  }
  }
  }


See Define Apex Triggers.

After you define the Apex triggers, set up constraint rules engine.
