public class RLM_Utils_AccountOrderDeleter {

    public static void deleteOrders(String accountId) {
        List<Order> orders = [SELECT Id, OriginalOrderId, RelatedOrderId FROM Order WHERE AccountId = :accountId];
        if (orders.isEmpty()) return;

        Set<Id> orderIds = new Map<Id, Order>(orders).keySet();

        // Delete OrderSummaryRelationship (restrict-delete on Order)
        List<OrderSummaryRelationship> osrs = [
            SELECT Id FROM OrderSummaryRelationship WHERE MainAttachedToId IN :orderIds
        ];
        if (!osrs.isEmpty()) Database.delete(osrs, false);

        // Null out self-referential Order fields to break circular restrict-delete
        List<Order> toNullify = new List<Order>();
        for (Order o : orders) {
            Boolean needsUpdate = false;
            if (o.OriginalOrderId != null && orderIds.contains(o.OriginalOrderId)) {
                o.OriginalOrderId = null;
                needsUpdate = true;
            }
            if (o.RelatedOrderId != null && orderIds.contains(o.RelatedOrderId)) {
                o.RelatedOrderId = null;
                needsUpdate = true;
            }
            if (needsUpdate) toNullify.add(o);
        }
        if (!toNullify.isEmpty()) Database.update(toNullify, false);

        // Set all orders to Draft for deletion
        List<Order> toDraft = [SELECT Id, Status FROM Order WHERE AccountId = :accountId];
        for (Order o : toDraft) {
            o.Status = 'Draft';
        }
        Database.update(toDraft, false);

        // Delete orders
        Database.delete(toDraft, false);
    }

    public static void deleteFulfillment(String accountId) {
        // Query order/item IDs for fulfillment lookups
        List<Order> orders = [SELECT Id FROM Order WHERE AccountId = :accountId];
        Set<Id> orderIds = new Map<Id, Order>(orders).keySet();

        List<OrderItem> orderItems = [SELECT Id FROM OrderItem WHERE Order.AccountId = :accountId];
        Set<Id> orderItemIds = new Map<Id, OrderItem>(orderItems).keySet();

        // Source identifiers for FulfillmentPlan
        Set<String> sourceIds = new Set<String>();
        for (Id oid : orderIds) sourceIds.add(oid);
        for (Id oiid : orderItemIds) sourceIds.add(oiid);

        // FulfillmentOrders
        List<Invoice> invoices = [SELECT Id FROM Invoice WHERE BillingAccountId = :accountId];
        Set<Id> invoiceIds = new Map<Id, Invoice>(invoices).keySet();

        List<OrderSummary> summaries = [SELECT Id FROM OrderSummary WHERE AccountId = :accountId];
        Set<Id> summaryIds = new Map<Id, OrderSummary>(summaries).keySet();

        List<FulfillmentOrder> fos = [
            SELECT Id FROM FulfillmentOrder
            WHERE AccountId = :accountId
            OR OrderId IN :orderIds
            OR InvoiceId IN :invoiceIds
            OR OrderSummaryId IN :summaryIds
        ];
        Set<Id> foIds = new Map<Id, FulfillmentOrder>(fos).keySet();

        // FulfillmentOrderLineItems
        List<FulfillmentOrderLineItem> folis = foIds.isEmpty()
            ? new List<FulfillmentOrderLineItem>()
            : [SELECT Id FROM FulfillmentOrderLineItem WHERE FulfillmentOrderId IN :foIds];
        Set<Id> foliIds = new Map<Id, FulfillmentOrderLineItem>(folis).keySet();

        // FulfillmentPlans
        List<FulfillmentPlan> fps = sourceIds.isEmpty()
            ? new List<FulfillmentPlan>()
            : [SELECT Id FROM FulfillmentPlan
               WHERE SourceIdentifier IN :sourceIds
               AND (SourceType = 'StandardOrder' OR SourceType = 'OrderItem')];
        Set<Id> fpIds = new Map<Id, FulfillmentPlan>(fps).keySet();

        // FulfillmentSteps
        List<FulfillmentStep> steps = fpIds.isEmpty()
            ? new List<FulfillmentStep>()
            : [SELECT Id FROM FulfillmentStep WHERE FulfillmentPlanId IN :fpIds];
        Set<Id> stepIds = new Map<Id, FulfillmentStep>(steps).keySet();

        // FulfillmentAssets
        List<FulfillmentAsset> fas = [SELECT Id FROM FulfillmentAsset WHERE AccountId = :accountId];
        Set<Id> faIds = new Map<Id, FulfillmentAsset>(fas).keySet();

        // Delete in dependency order:
        // 1. FulfillmentLineSourceRel
        if (!orderItemIds.isEmpty() || !foliIds.isEmpty()) {
            List<FulfillmentLineSourceRel> flsrs = [
                SELECT Id FROM FulfillmentLineSourceRel
                WHERE SourceLineItemId IN :orderItemIds
                OR FulfilmentOrderLineId IN :foliIds
            ];
            if (!flsrs.isEmpty()) Database.delete(flsrs, false);
        }

        // 2. FulfillmentStepSource
        if (!stepIds.isEmpty() || !orderItemIds.isEmpty()) {
            List<FulfillmentStepSource> fsss = [
                SELECT Id FROM FulfillmentStepSource
                WHERE StepId IN :stepIds
                OR SourceLineItemId IN :orderItemIds
            ];
            if (!fsss.isEmpty()) Database.delete(fsss, false);
        }

        // 3. FulfillmentOrderLineItem
        if (!folis.isEmpty()) Database.delete(folis, false);

        // 4. FulfillmentOrder
        if (!fos.isEmpty()) Database.delete(fos, false);

        // 5. FulfillmentPlan
        if (!fps.isEmpty()) Database.delete(fps, false);

        // 6. AssetFulfillmentDecomp
        if (!faIds.isEmpty()) {
            List<AssetFulfillmentDecomp> afds = [
                SELECT Id FROM AssetFulfillmentDecomp
                WHERE FulfillmentSourceAssetId IN :faIds
                OR FulfillmentTargetAssetId IN :faIds
            ];
            if (!afds.isEmpty()) Database.delete(afds, false);
        }

        // 7. FulfillmentAsset
        if (!fas.isEmpty()) Database.delete(fas, false);
    }
}
