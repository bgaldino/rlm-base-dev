public with sharing class RLM_MockSavedPaymentMethodController {
    @AuraEnabled
    public static Id createMockPaymentMethod(
        Id accountId,
        String paymentGatewayId,
        String paymentMethodType,
        String scenario,
        String accountHolderName,
        String accountHolderEmail,
        Boolean saveAsDefault,
        String cardNumber,
        String cvv,
        Integer expiryMonth,
        Integer expiryYear,
        String bankAccountNumber,
        String bankRoutingNumber,
        String bankAccountType,
        String bankAccountHolderType,
        String billingStreet,
        String billingCity,
        String billingState,
        String billingPostalCode,
        String billingCountry
    ) {
        validateInput(
            accountId,
            paymentGatewayId,
            paymentMethodType,
            scenario,
            accountHolderName,
            accountHolderEmail,
            cardNumber,
            cvv,
            expiryMonth,
            expiryYear,
            bankAccountNumber,
            bankRoutingNumber,
            bankAccountType,
            bankAccountHolderType,
            billingStreet,
            billingCity,
            billingState,
            billingPostalCode,
            billingCountry
        );

        List<Account> accounts = [
            SELECT Id
            FROM Account
            WHERE Id = :accountId
            WITH USER_MODE
            LIMIT 1
        ];
        if (accounts.isEmpty()) {
            throw new AuraHandledException(
                'You must have access to the Account to add a payment method.'
            );
        }

        // Read gateway configuration in user mode too; the feature permission
        // set grants only the fields needed to validate this selected gateway.
        PaymentGateway gateway = getMockGateway(paymentGatewayId);
        if (gateway.MerchantAccountId == null) {
            throw new AuraHandledException('The configured Payment Gateway has no Merchant Account.');
        }

        ConnectApi.PaymentMethodTokenizationRequest tokenizeRequest =
            new ConnectApi.PaymentMethodTokenizationRequest();
        tokenizeRequest.paymentGatewayId = gateway.Id;
        tokenizeRequest.address = new ConnectApi.AddressRequest();
        tokenizeRequest.address.street = billingStreet.trim();
        tokenizeRequest.address.city = billingCity.trim();
        tokenizeRequest.address.state = billingState.trim();
        tokenizeRequest.address.postalCode = billingPostalCode.trim();
        tokenizeRequest.address.country = billingCountry.trim();

        Boolean isAch = paymentMethodType == 'ACH';
        if (isAch) {
            ConnectApi.BankPaymentMethodRequest bankRequest =
                new ConnectApi.BankPaymentMethodRequest();
            bankRequest.accountId = String.valueOf(accountId);
            bankRequest.accountHolderName = accountHolderName.trim();
            bankRequest.accountHolderType = bankAccountHolderType == 'Business'
                ? ConnectApi.AccountHolderType.Business
                : ConnectApi.AccountHolderType.Individual;
            bankRequest.accountNumber = bankAccountNumber;
            bankRequest.bankCode = bankRoutingNumber;
            bankRequest.accountType = bankAccountType == 'Savings'
                ? ConnectApi.AccountType.Savings
                : ConnectApi.AccountType.Checking;
            bankRequest.bankType = ConnectApi.BankType.Ach;
            bankRequest.email = accountHolderEmail.trim();
            bankRequest.mandate = 'RLM mock ACH authorization for testing only.';
            bankRequest.standardEntryClassCode = ConnectApi.StandardEntryClassCode.Web;
            tokenizeRequest.bankPaymentMethod = bankRequest;
        } else {
            ConnectApi.CardPaymentMethodRequest cardRequest =
                new ConnectApi.CardPaymentMethodRequest();
            cardRequest.accountId = String.valueOf(accountId);
            cardRequest.cardHolderName = accountHolderName.trim();
            cardRequest.email = accountHolderEmail.trim();
            cardRequest.cardNumber = cardNumber.replaceAll('\\s', '');
            cardRequest.cvv = cvv;
            cardRequest.cardType = 'Visa';
            cardRequest.expiryMonth = expiryMonth;
            cardRequest.expiryYear = expiryYear;
            tokenizeRequest.cardPaymentMethod = cardRequest;
        }
        tokenizeRequest.additionalData = new Map<String, String>{
            'mockScenario' => scenario.toUpperCase()
        };

        ConnectApi.PaymentMethodTokenizationResponse tokenizeResponse;
        try {
            tokenizeResponse = ConnectApi.Payments.tokenizePaymentMethod(
                tokenizeRequest
            );
        } catch (Exception e) {
            // Never include the exception message: platform or adapter errors
            // can contain payment request details.
            throw new AuraHandledException(
                'The payment provider could not tokenize this payment method.'
            );
        }
        if (tokenizeResponse == null || tokenizeResponse.gatewayResponse == null ||
            String.isBlank(tokenizeResponse.gatewayResponse.gatewayToken)) {
            throw new AuraHandledException(
                'The payment provider did not return a payment token.'
            );
        }
        String token = tokenizeResponse.gatewayResponse.gatewayToken;
        SavedPaymentMethod method = new SavedPaymentMethod(
            Name = isAch
                ? 'RLM ACH Payment Method'
                : 'RLM Card Payment Method ' + String.valueOf(expiryYear),
            ReferenceOwnerId = accountId,
            PaymentGatewayId = gateway.Id,
            MerchantAccountId = gateway.MerchantAccountId,
            Status = 'Active',
            UsageType = 'OffSession',
            IsDefault = saveAsDefault == true,
            IsMerchantCreated = true,
            Type = isAch ? 'us_bank_account' : 'card',
            ProcessingMode = 'External',
            GatewayReference = 'mock-owner-' + String.valueOf(accountId),
            GatewayToken = token,
            Checksum = EncodingUtil.convertToHex(
                Crypto.generateDigest('SHA-256', Blob.valueOf(token))
            ).substring(0, 63),
            AccountHolderName = accountHolderName.trim(),
            AccountHolderEmail = accountHolderEmail.trim(),
            BankCode = isAch ? bankRoutingNumber : null,
            BankName = isAch ? 'RLM Mock Bank' : null,
            BankAccountType = isAch ? bankAccountType : null,
            BankAccountHolderType = isAch ? bankAccountHolderType : null,
            ExpiryMonth = isAch ? null : expiryMonth,
            ExpiryYear = isAch ? null : expiryYear,
            Last4 = isAch
                ? bankAccountNumber.right(Math.min(4, bankAccountNumber.length()))
                : '4242',
            Network = isAch ? null : 'Visa',
            NickName = isAch
                ? bankAccountType + ' account'
                : 'Visa',
            BillingStreet = billingStreet.trim(),
            BillingCity = billingCity.trim(),
            BillingState = billingState.trim(),
            BillingPostalCode = billingPostalCode.trim(),
            BillingCountry = billingCountry.trim()
        );
        Database.SaveResult result = Database.insert(
            method,
            AccessLevel.USER_MODE
        );
        if (!result.isSuccess()) {
            throw new AuraHandledException(
                'Salesforce could not create the saved payment method. Check SavedPaymentMethod access and required fields.'
            );
        }
        return result.getId();
    }

    private static void validateInput(
        Id accountId,
        String paymentGatewayId,
        String paymentMethodType,
        String scenario,
        String accountHolderName,
        String accountHolderEmail,
        String cardNumber,
        String cvv,
        Integer expiryMonth,
        Integer expiryYear,
        String bankAccountNumber,
        String bankRoutingNumber,
        String bankAccountType,
        String bankAccountHolderType,
        String billingStreet,
        String billingCity,
        String billingState,
        String billingPostalCode,
        String billingCountry
    ) {
        if (accountId == null || accountId.getSObjectType() != Account.SObjectType) {
            throw new AuraHandledException('Open this component on an Account record.');
        }
        if (String.isBlank(paymentGatewayId)) {
            throw new AuraHandledException('Set a Payment Gateway record ID in the component properties.');
        }
        if (paymentMethodType != 'CARD' && paymentMethodType != 'ACH') {
            throw new AuraHandledException('Choose Card or ACH as the payment method type.');
        }
        if (!new Set<String>{ 'SUCCESS', 'DECLINE', 'INVALID', 'ERROR' }
            .contains(scenario == null ? '' : scenario.toUpperCase())) {
            throw new AuraHandledException('Select a valid payment response.');
        }
        if (String.isBlank(accountHolderName) || String.isBlank(accountHolderEmail)) {
            throw new AuraHandledException('Enter the account holder name and email.');
        }
        if (paymentMethodType == 'CARD') {
            if (String.isBlank(cardNumber) || String.isBlank(cvv)) {
                throw new AuraHandledException('Enter the card number and security code.');
            }
            if (cardNumber.replaceAll('\\s', '') != '4242424242424242' ||
                !Pattern.matches('^[0-9]{3,4}$', cvv)) {
                throw new AuraHandledException(
                    'Enter a valid card number and a 3- or 4-digit security code.'
                );
            }
            if (expiryMonth == null || expiryMonth < 1 || expiryMonth > 12 || expiryYear == null) {
                throw new AuraHandledException('Enter a valid card expiration date.');
            }
            Date today = Date.today();
            if (expiryYear < today.year() ||
                (expiryYear == today.year() && expiryMonth < today.month())) {
                throw new AuraHandledException('The expiration date must be in the future.');
            }
        } else {
            if (bankAccountNumber != '000123456789' ||
                bankRoutingNumber != '000000000') {
                throw new AuraHandledException(
                    'Enter valid bank account details.'
                );
            }
            if (!new Set<String>{ 'Checking', 'Savings' }.contains(bankAccountType) ||
                !new Set<String>{ 'Individual', 'Business' }.contains(bankAccountHolderType)) {
                throw new AuraHandledException('Choose a valid ACH account and holder type.');
            }
        }
        if (String.isBlank(billingStreet) || String.isBlank(billingCity) ||
            String.isBlank(billingState) || String.isBlank(billingPostalCode) ||
            String.isBlank(billingCountry)) {
            throw new AuraHandledException('Complete the billing address.');
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
                SELECT Id, MerchantAccountId
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
        // The CCI setup task validates the provider through Tooling API. Apex
        // uses the unique org-specific PaymentGateway ID selected in Builder.
        List<PaymentGateway> gateways = [
            SELECT Id, MerchantAccountId
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
