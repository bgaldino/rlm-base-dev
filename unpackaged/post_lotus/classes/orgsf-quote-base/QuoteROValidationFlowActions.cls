public class QuoteROValidationFlowActions {
    @InvocableMethod(label='Validate RevenueOwner')
    public static List<String> validateRevenueOwner(List<RevenueOwnerFlowActionRequest> requestList) {
        List<String> resultList = new  List<String>();
        if(requestList.size() ==0) return resultList;
        RevenueOwnerService revenueOwnerService = (RevenueOwnerService) ServiceRegistry.getInstance('IRevenueOwnerService');
        String billingrevOwner = revenueOwnerService.getRevenueOwner(requestList[0].billingCountry);
        String deliveryrevOwner = revenueOwnerService.getRevenueOwner(requestList[0].deliveryCountry);
        if (billingrevOwner != deliveryrevOwner) {
            resultList.add('Delivery Address and Billing Address should be part of the same Revenue Owner. Please update the address on the quote to proceed.');
        }
        return resultList;
    }

    public class RevenueOwnerFlowActionRequest {
        @InvocableVariable(required=true)
        public String billingCountry;
        @InvocableVariable(required=true)
        public String deliveryCountry;
    }
}