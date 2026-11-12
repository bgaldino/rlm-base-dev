/**
 * Stamps the Constraint Rules Engine node status on each new asset action source from the order
 * product that produced it, so the next amendment's lines start from the configurator's state.
 *
 * RLM_QuoteItemTrigger copies this field from an asset's latest action onto amendment lines. On 264,
 * activation leaves it blank on every source the order didn't already fill:
 * - without an Order-to-Asset rule in the Sales Transaction context, every source is blank;
 * - with the rule, a source made from an OrderItemDetail (the cancel-and-reprice pair an attribute
 *   amendment produces) is still blank, because the detail node carries no node status.
 *   Those rows hold the OrderItemDetail Id in ReferenceEntityItemId, though the 264 object
 *   reference lists only OrderItem and WorkOrderLineItem for that field (measured on a fresh
 *   264 scratch org, 2026-11-11).
 * A blank status makes the next solve reset every unchanged answer to its CML default.
 *
 * A status already set (by the context rule, or by a caller) is kept. System-mode SOQL: this
 * fills a platform-owned field during assetization and isn't a user-facing entry point, the same
 * as RLM_QuoteItemTrigger.
 */
trigger RLM_AssetActionSourceTrigger on AssetActionSource (before insert) {
    Set<Id> orderItemIds = new Set<Id>();
    Set<Id> detailIds = new Set<Id>();
    for (AssetActionSource src : Trigger.new) {
        if (String.isBlank(src.RLM_ConstraintEngineNodeStatus__c) && src.ReferenceEntityItemId != null) {
            Schema.SObjectType refType = src.ReferenceEntityItemId.getSObjectType();
            if (refType == OrderItem.SObjectType) {
                orderItemIds.add(src.ReferenceEntityItemId);
            } else if (refType == OrderItemDetail.SObjectType) {
                detailIds.add(src.ReferenceEntityItemId);
            }
        }
    }
    if (orderItemIds.isEmpty() && detailIds.isEmpty()) {
        return;
    }

    Map<Id, Id> detailToOrderItem = new Map<Id, Id>();
    if (!detailIds.isEmpty()) {
        for (OrderItemDetail detail : [SELECT Id, OrderItemId FROM OrderItemDetail WHERE Id IN :detailIds]) {
            detailToOrderItem.put(detail.Id, detail.OrderItemId);
            orderItemIds.add(detail.OrderItemId);
        }
    }

    Map<Id, String> statusByOrderItem = new Map<Id, String>();
    for (OrderItem item : [
        SELECT Id, RLM_ConstraintEngineNodeStatus__c FROM OrderItem WHERE Id IN :orderItemIds
    ]) {
        if (String.isNotBlank(item.RLM_ConstraintEngineNodeStatus__c)) {
            statusByOrderItem.put(item.Id, item.RLM_ConstraintEngineNodeStatus__c);
        }
    }

    for (AssetActionSource src : Trigger.new) {
        if (String.isBlank(src.RLM_ConstraintEngineNodeStatus__c) && src.ReferenceEntityItemId != null) {
            Id orderItemId = detailToOrderItem.containsKey(src.ReferenceEntityItemId)
                ? detailToOrderItem.get(src.ReferenceEntityItemId)
                : src.ReferenceEntityItemId;
            String status = statusByOrderItem.get(orderItemId);
            if (status != null) {
                src.RLM_ConstraintEngineNodeStatus__c = status;
            }
        }
    }
}
