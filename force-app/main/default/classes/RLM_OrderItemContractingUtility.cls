public with sharing class RLM_OrderItemContractingUtility {

    @InvocableMethod(label = 'Calculate Contract Info' description = 'Returns Contract End Date based on last Order Item')
    public static List<OrderInfoResults> calculateOrderInfoForContract(List<Id> inputOrderIds) {
        List<OrderInfoResults> results = new List<OrderInfoResults>();
        if (inputOrderIds.isEmpty()) {
            return results;
        }

        // Check field-level security before executing queries
        Boolean isOrderAccessible = Schema.sObjectType.Order.fields.EffectiveDate.isAccessible();
        Boolean isOrderItemAccessible = Schema.sObjectType.OrderItem.fields.ServiceDate.isAccessible() && Schema.sObjectType.OrderItem.fields.EndDate.isAccessible();
        Boolean isOrderActionAccessible = Schema.sObjectType.OrderAction.fields.Type.isAccessible();
        
        if (!isOrderAccessible || !isOrderItemAccessible || !isOrderActionAccessible) {
            System.debug('User does not have access to required fields on Order, OrderItem, or OrderAction objects.');
            return results;
        }

        Map<Id, Order> ordersMap = new Map<Id, Order>([
            SELECT Id, EffectiveDate,
                (SELECT Id, ServiceDate, EndDate, ProductSellingModel.SellingModelType
                 FROM OrderItems
                 WHERE ProductSellingModel.SellingModelType != 'One Time' AND EndDate != null
                 ORDER BY EndDate DESC LIMIT 1),
                (SELECT Id, Type FROM OrderActions WHERE Type IN ('Add', 'Amend', 'Renew'))
            FROM Order
            WHERE Id IN :inputOrderIds
        ]);

        for (Order o : ordersMap.values()) {
            OrderInfoResults result = new OrderInfoResults();
            processOrderItems(o, result);
            countOrderActions(o, result);
            results.add(result);
        }

        return results;
    }

    private static void processOrderItems(Order o, OrderInfoResults result) {
        result.subscriptionItemCount = o.OrderItems.size();
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