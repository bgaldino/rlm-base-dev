public with sharing class RLM_MockPaymentControllerSupport {
    public static void validateAccountAccess(Id accountId, String message) {
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
            throw new AuraHandledException(message);
        }
    }

    public static PaymentGateway getActiveGateway(
        String identifier,
        Boolean includeMerchantAccount
    ) {
        if (String.isBlank(identifier)) {
            throw new AuraHandledException(
                'Set an active Payment Gateway record ID or unique name in the component properties.'
            );
        }

        Id gatewayId;
        try {
            gatewayId = Id.valueOf(identifier);
        } catch (Exception e) {
            String fields = includeMerchantAccount == true
                ? 'Id, MerchantAccountId'
                : 'Id';
            List<PaymentGateway> namedGateways = Database.query(
                'SELECT ' + fields +
                ' FROM PaymentGateway WHERE PaymentGatewayName = :identifier' +
                ' AND Status = \'Active\' WITH USER_MODE LIMIT 2'
            );
            if (namedGateways.size() != 1) {
                throw new AuraHandledException(
                    'The configured Payment Gateway name must match exactly one active gateway.'
                );
            }
            return namedGateways[0];
        }

        if (gatewayId.getSObjectType() != PaymentGateway.SObjectType) {
            throw new AuraHandledException(
                'Set an active Payment Gateway record ID or unique name in the component properties.'
            );
        }

        String fields = includeMerchantAccount == true
            ? 'Id, MerchantAccountId'
            : 'Id';
        List<PaymentGateway> gateways = Database.query(
            'SELECT ' + fields +
            ' FROM PaymentGateway WHERE Id = :gatewayId' +
            ' AND Status = \'Active\' WITH USER_MODE LIMIT 1'
        );
        if (gateways.isEmpty()) {
            throw new AuraHandledException(
                'The configured active Payment Gateway was not found.'
            );
        }
        return gateways[0];
    }
}
