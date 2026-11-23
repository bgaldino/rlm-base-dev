public with sharing class RLM_OrderItemContractingUtility {

    /**
     * One result per input, in input order, each stamped with its order id (the Flow bulk contract).
     * An order that cannot be read (no field access, or no such order) gets a result with errorMessage
     * set and null counts instead of no result; a caller must check errorMessage first.
     */
    @InvocableMethod(label = 'Calculate Contract Info' description = 'Returns Contract End Date based on last Order Item')
    public static List<OrderInfoResults> calculateOrderInfoForContract(List<Id> inputOrderIds) {
        List<OrderInfoResults> results = new List<OrderInfoResults>();
        if (inputOrderIds == null || inputOrderIds.isEmpty()) {
            return results;
        }

        // Check field-level security before executing queries
        Boolean isOrderAccessible = Schema.sObjectType.Order.fields.EffectiveDate.isAccessible();
        Boolean isOrderItemAccessible = Schema.sObjectType.OrderItem.fields.ServiceDate.isAccessible() && Schema.sObjectType.OrderItem.fields.EndDate.isAccessible();
        Boolean isOrderActionAccessible = Schema.sObjectType.OrderAction.fields.Type.isAccessible();
        
        if (!isOrderAccessible || !isOrderItemAccessible || !isOrderActionAccessible) {
            System.debug('User does not have access to required fields on Order, OrderItem, or OrderAction objects.');
            for (Id orderId : inputOrderIds) {
                results.add(failedResult(orderId, 'The running user cannot read the Order, OrderItem or OrderAction fields this action needs.'));
            }
            return results;
        }

        // The item subquery keeps LIMIT 1: ordered latest end date first, its one row drives the term.
        // A child subquery with no LIMIT throws "Aggregate query has too many rows" past 200 items per
        // order (large transactions), so the item count comes from a separate aggregate query. Its COUNT(Id)
        // still counts every aggregated row toward the 50,000 query-row limit.
        // WITH USER_MODE also enforces object access and the fields the check above does not name
        // (ProductSellingModel.SellingModelType, OrderItem and OrderAction rows), applies to the subqueries,
        // and enforces sharing.
        // The OrderActions subquery has no LIMIT on purpose: the counts are per action type, so a cap would
        // undercount. countOrderActions reads o.OrderActions with a for loop, the documented safe way to
        // read more than 200 child rows.
        Map<Id, Order> ordersMap;
        Map<Id, Integer> itemCountByOrder = new Map<Id, Integer>();
        try {
            ordersMap = new Map<Id, Order>([
            SELECT Id, EffectiveDate,
                (SELECT Id, ServiceDate, EndDate, ProductSellingModel.SellingModelType
                 FROM OrderItems
                 WHERE ProductSellingModel.SellingModelType != 'OneTime' AND EndDate != null
                 ORDER BY EndDate DESC LIMIT 1),
                (SELECT Id, Type FROM OrderActions WHERE Type IN ('Add', 'Amend', 'Renew'))
            FROM Order
            WHERE Id IN :inputOrderIds
            WITH USER_MODE
            ]);

            for (AggregateResult ar : [SELECT OrderId, COUNT(Id) itemCount
                                   FROM OrderItem
                                   WHERE OrderId IN :inputOrderIds
                                     AND ProductSellingModel.SellingModelType != 'OneTime' AND EndDate != null
                                   WITH USER_MODE
                                   GROUP BY OrderId]) {
                itemCountByOrder.put((Id) ar.get('OrderId'), Integer.valueOf(ar.get('itemCount')));
            }
        } catch (QueryException e) {
            // Mostly a missing object or field permission for the running user, which the field check above
            // cannot see (for example ProductSellingModel); any other query failure is reported the same way.
            for (Id orderId : inputOrderIds) {
                results.add(failedResult(orderId, 'The orders could not be read as the running user (a missing object or field permission, or another query error): ' + e.getMessage()));
            }
            return results;
        }

        for (Id orderId : inputOrderIds) {
            Order o = ordersMap.get(orderId);
            if (o == null) {
                results.add(failedResult(orderId, 'Order ' + orderId + ' was not found or is not visible to the running user.'));
                continue;
            }
            OrderInfoResults result = new OrderInfoResults();
            result.orderId = orderId;
            processOrderItems(o, result, itemCountByOrder.containsKey(orderId) ? itemCountByOrder.get(orderId) : 0);
            countOrderActions(o, result);
            results.add(result);
        }

        return results;
    }

    private static OrderInfoResults failedResult(Id orderId, String message) {
        OrderInfoResults result = new OrderInfoResults();
        result.orderId = orderId;
        // Counts stay null: zero would read as "no subscriptions on the order" to a calling flow.
        result.errorMessage = message;
        return result;
    }

    private static void processOrderItems(Order o, OrderInfoResults result, Integer itemCount) {
        result.subscriptionItemCount = itemCount;
        if (!o.OrderItems.isEmpty()) {
            OrderItem lastItem = o.OrderItems[0];
            result.outEndDate = lastItem.EndDate;
            result.outContractTerm = o.EffectiveDate.monthsBetween(lastItem.EndDate);
            if (lastItem.EndDate.day() > o.EffectiveDate.day()) {
                result.outContractTerm++;
            }
        } else {
            result.outEndDate = null;
            result.outContractTerm = 1;
        }
    }

    private static void countOrderActions(Order o, OrderInfoResults result) {
        result.addOrderActionCount = 0;
        result.amendOrderActionCount = 0;
        result.renewOrderActionCount = 0;
        for (OrderAction action : o.OrderActions) {
            switch on action.Type {
                when 'Add' {
                    result.addOrderActionCount++;
                }
                when 'Amend' {
                    result.amendOrderActionCount++;
                }
                when 'Renew' {
                    result.renewOrderActionCount++;
                }
            }
        }
    }

    public class OrderInfoResults {
        @InvocableVariable
        public Id orderId;
        @InvocableVariable
        public String errorMessage;
        @InvocableVariable
        public Date outEndDate;
        @InvocableVariable
        public Integer outContractTerm;
        @InvocableVariable
        public Integer subscriptionItemCount;
        @InvocableVariable
        public Integer addOrderActionCount;
        @InvocableVariable
        public Integer amendOrderActionCount;
        @InvocableVariable
        public Integer renewOrderActionCount;
    }
}