public with sharing class RLM_MockPaymentSaleController {
    public class SavedMethodOption {
        @AuraEnabled public Id id { get; set; }
        @AuraEnabled public String label { get; set; }
        @AuraEnabled public String currencyIsoCode { get; set; }
        @AuraEnabled public String paymentType { get; set; }

        public SavedMethodOption(SavedPaymentMethod method, String accountCurrency) {
            id = method.Id;
            paymentType = method.Type;
            if (method.Type == 'us_bank_account') {
                String bankName = String.isBlank(method.NickName)
                    ? method.BankAccountType + ' account'
                    : method.NickName;
                label = cleanDisplayName(bankName) + ' •••• ' + method.Last4;
            } else {
                String name = String.isBlank(method.NickName)
                    ? method.Name
                    : method.NickName;
                label = cleanDisplayName(name) + ' •••• ' + method.Last4 + ' (expires ' +
                    String.valueOf(method.ExpiryMonth) + '/' +
                    String.valueOf(method.ExpiryYear) + ')';
            }
            currencyIsoCode = accountCurrency;
        }

        private String cleanDisplayName(String value) {
            return value == null ? '' : value.replaceAll('(?i)\\bmock\\b\\s*', '').trim();
        }
    }

    public class SaleResult {
        @AuraEnabled public Id paymentId { get; set; }
        @AuraEnabled public String paymentNumber { get; set; }
        @AuraEnabled public String status { get; set; }
        @AuraEnabled public Decimal amount { get; set; }
        @AuraEnabled public String currencyIsoCode { get; set; }
        @AuraEnabled public String gatewayReferenceNumber { get; set; }
    }

    @AuraEnabled(cacheable=true)
    public static List<SavedMethodOption> getSavedPaymentMethods(
        Id accountId,
        String paymentGatewayId
    ) {
        validateAccountId(accountId);
        PaymentGateway gateway = getMockGateway(paymentGatewayId);
        List<SavedPaymentMethod> methods = [
            SELECT Id, Name, NickName, Last4, ExpiryMonth, ExpiryYear, Type,
                BankAccountType
            FROM SavedPaymentMethod
            WHERE ReferenceOwnerId = :accountId
                AND PaymentGatewayId = :gateway.Id
                AND Status = 'Active'
            WITH USER_MODE
            ORDER BY CreatedDate DESC
        ];
        String accountCurrency;
        if (UserInfo.isMultiCurrencyOrganization()) {
            List<Account> accounts = [
                SELECT CurrencyIsoCode
                FROM Account
                WHERE Id = :accountId
                WITH USER_MODE
                LIMIT 1
            ];
            accountCurrency = accounts[0].CurrencyIsoCode;
        }
        List<SavedMethodOption> options = new List<SavedMethodOption>();
        for (SavedPaymentMethod method : methods) {
            options.add(new SavedMethodOption(method, accountCurrency));
        }
        return options;
    }

    @AuraEnabled
    public static SaleResult createPaymentSale(
        Id accountId,
        String paymentGatewayId,
        Id savedPaymentMethodId,
        Decimal amount
    ) {
        validateAccountId(accountId);
        if (savedPaymentMethodId == null ||
            savedPaymentMethodId.getSObjectType() != SavedPaymentMethod.SObjectType) {
            throw new AuraHandledException('Select an active saved payment method.');
        }
        if (amount == null || amount <= 0 || amount.scale() > 2 || amount > 100000) {
            throw new AuraHandledException(
                'Enter an amount greater than zero, with up to two decimal places, and no more than 100,000.'
            );
        }

        PaymentGateway gateway = getMockGateway(paymentGatewayId);
        List<SavedPaymentMethod> methods = [
            SELECT Id, ReferenceOwnerId, PaymentGatewayId, Status
            FROM SavedPaymentMethod
            WHERE Id = :savedPaymentMethodId
                AND ReferenceOwnerId = :accountId
                AND PaymentGatewayId = :gateway.Id
                AND Status = 'Active'
            WITH USER_MODE
            LIMIT 1
        ];
        if (methods.isEmpty()) {
            throw new AuraHandledException(
                'The selected saved payment method is unavailable for this Account and gateway.'
            );
        }

        ConnectApi.SaleRequest request = new ConnectApi.SaleRequest();
        request.accountId = String.valueOf(accountId);
        request.amount = amount;
        request.paymentGatewayId = String.valueOf(gateway.Id);
        request.idempotencyKey = EncodingUtil.convertToHex(
            Crypto.generateAesKey(128)
        );
        request.paymentMethod = new ConnectApi.SaleApiPaymentMethodRequest();
        request.paymentMethod.id = String.valueOf(savedPaymentMethodId);
        if (UserInfo.isMultiCurrencyOrganization()) {
            List<Account> accounts = [
                SELECT CurrencyIsoCode
                FROM Account
                WHERE Id = :accountId
                WITH USER_MODE
                LIMIT 1
            ];
            request.currencyIsoCode = accounts[0].CurrencyIsoCode;
        }

        ConnectApi.SaleResponse response;
        try {
            response = ConnectApi.Payments.sale(request);
        } catch (Exception e) {
            // Do not expose ConnectApi exception text; it can include payment data.
            throw new AuraHandledException(
                'The payment could not be processed. Check the gateway log for details.'
            );
        }
        if (response == null || response.error != null || response.payment == null) {
            throw new AuraHandledException(
                'The payment provider did not return a payment. Check the gateway log for details.'
            );
        }

        SaleResult result = new SaleResult();
        result.paymentId = response.payment.id;
        result.paymentNumber = response.payment.paymentNumber;
        result.status = response.payment.status;
        result.amount = response.payment.amount;
        result.currencyIsoCode = response.payment.currencyIsoCode;
        result.gatewayReferenceNumber = response.gatewayResponse == null
            ? null
            : response.gatewayResponse.gatewayReferenceNumber;
        return result;
    }

    private static void validateAccountId(Id accountId) {
        if (accountId == null || accountId.getSObjectType() != Account.SObjectType) {
            throw new AuraHandledException('Open this component on an Account record.');
        }
        List<Account> accounts = [
            SELECT Id
            FROM Account
            WHERE Id = :accountId
            WITH USER_MODE
            LIMIT 1
        ];
        if (accounts.isEmpty()) {
            throw new AuraHandledException(
                'You must have access to the Account to create a payment.'
            );
        }
    }

    private static PaymentGateway getMockGateway(String paymentGatewayIdentifier) {
        if (String.isBlank(paymentGatewayIdentifier)) {
            throw new AuraHandledException(
                'Set an active Payment Gateway record ID or unique name in the component properties.'
            );
        }
        Id gatewayId;
        try {
            gatewayId = Id.valueOf(paymentGatewayIdentifier);
        } catch (Exception e) {
            List<PaymentGateway> namedGateways = [
                SELECT Id
                FROM PaymentGateway
                WHERE PaymentGatewayName = :paymentGatewayIdentifier
                    AND Status = 'Active'
                WITH USER_MODE
                LIMIT 2
            ];
            if (namedGateways.size() != 1) {
                throw new AuraHandledException(
                    'The configured Payment Gateway name must match exactly one active gateway.'
                );
            }
            return namedGateways[0];
        }
        if (gatewayId == null || gatewayId.getSObjectType() != PaymentGateway.SObjectType) {
            throw new AuraHandledException(
                'Set an active Payment Gateway record ID or unique name in the component properties.'
            );
        }
        // PaymentGatewayProvider is provisioned and checked by the CCI setup
        // task through Tooling API; Builder passes this gateway's unique ID.
        List<PaymentGateway> gateways = [
            SELECT Id
            FROM PaymentGateway
            WHERE Id = :gatewayId AND Status = 'Active'
            WITH USER_MODE
            LIMIT 1
        ];
        if (gateways.isEmpty()) {
            throw new AuraHandledException('The configured active Payment Gateway was not found.');
        }
        return gateways[0];
    }
}
