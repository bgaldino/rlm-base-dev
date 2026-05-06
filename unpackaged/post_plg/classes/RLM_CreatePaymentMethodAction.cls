public with sharing class RLM_CreatePaymentMethodAction {

    public class Request {
        @InvocableVariable(label='Card Token' required=true)
        public String cardToken;
        @InvocableVariable(label='Account ID' required=true)
        public String accountId;
        @InvocableVariable(label='Billing First Name')
        public String billingFirstName;
        @InvocableVariable(label='Billing Last Name')
        public String billingLastName;
        @InvocableVariable(label='Billing Street')
        public String billingStreet;
        @InvocableVariable(label='Billing City')
        public String billingCity;
        @InvocableVariable(label='Billing State')
        public String billingState;
        @InvocableVariable(label='Billing Postal Code')
        public String billingPostalCode;
    }

    public class Result {
        @InvocableVariable(label='Payment Method ID')
        public String paymentMethodId;
        @InvocableVariable(label='Response JSON')
        public String responseJson;
        @InvocableVariable(label='Is Success')
        public Boolean isSuccess;
        @InvocableVariable(label='Error Message')
        public String errorMessage;
    }

    @InvocableMethod(
        label='Create Payment Method (RLM)'
        description='POST /commerce/payments/payment-methods — Tokenizes and stores a payment method'
        category='Revenue Cloud'
    )
    public static List<Result> execute(List<Request> requests) {
        List<Result> results = new List<Result>();
        for (Request req : requests) {
            Result res = new Result();
            try {
                Map<String, Object> payReq = new Map<String, Object>{
                    'accountId' => req.accountId,
                    'cardPaymentMethod' => new Map<String, Object>{
                        'cardToken' => req.cardToken
                    },
                    'address' => new Map<String, Object>{
                        'firstName' => req.billingFirstName,
                        'lastName' => req.billingLastName,
                        'street' => req.billingStreet,
                        'city' => req.billingCity,
                        'state' => req.billingState,
                        'postalCode' => req.billingPostalCode
                    }
                };
                Map<String, Object> response = RLM_RevenueCloudService.createPaymentMethod(payReq);
                res.paymentMethodId = (String) response.get('id');
                res.responseJson = JSON.serialize(response);
                res.isSuccess = true;
            } catch (Exception e) {
                res.isSuccess = false;
                res.errorMessage = e.getMessage();
            }
            results.add(res);
        }
        return results;
    }
}