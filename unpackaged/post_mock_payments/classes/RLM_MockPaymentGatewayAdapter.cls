global with sharing class RLM_MockPaymentGatewayAdapter
    implements commercepayments.PaymentGatewayAdapter {

    private static final commercepayments.SalesforceResultCodeInfo SUCCESS =
        new commercepayments.SalesforceResultCodeInfo(
            commercepayments.SalesforceResultCode.Success
        );
    private static final commercepayments.SalesforceResultCodeInfo DECLINE =
        new commercepayments.SalesforceResultCodeInfo(
            commercepayments.SalesforceResultCode.Decline
        );

    global RLM_MockPaymentGatewayAdapter() {}

    global commercepayments.GatewayResponse processRequest(
        commercepayments.PaymentGatewayContext gatewayContext
    ) {
        commercepayments.RequestType requestType =
            gatewayContext.getPaymentRequestType();
        commercepayments.PaymentGatewayRequest request =
            gatewayContext.getPaymentRequest();
        try {
            if (requestType == commercepayments.RequestType.Tokenize) {
                return tokenize(
                    (commercepayments.PaymentMethodTokenizationRequest)request
                );
            }
            if (requestType == commercepayments.RequestType.Authorize) {
                return authorize((commercepayments.AuthorizationRequest)request);
            }
            if (requestType == commercepayments.RequestType.Sale) {
                return sale((commercepayments.SaleRequest)request);
            }
            if (requestType == commercepayments.RequestType.Capture) {
                return capture((commercepayments.CaptureRequest)request);
            }
            if (requestType == commercepayments.RequestType.ReferencedRefund) {
                return refund(
                    (commercepayments.ReferencedRefundRequest)request
                );
            }
            if (requestType == commercepayments.RequestType.UnreferencedRefund) {
                return unreferencedRefund(
                    (commercepayments.UnreferencedRefundRequest)request
                );
            }
            if (requestType == commercepayments.RequestType.AuthorizationReversal) {
                return reverseAuthorization(
                    (commercepayments.AuthorizationReversalRequest)request
                );
            }
        } catch (Exception e) {
            // Avoid returning request data or tokens in gateway errors/logs.
            return new commercepayments.GatewayErrorResponse(
                '500',
                'Mock gateway could not process this payment request.'
            );
        }
        return new commercepayments.GatewayErrorResponse(
            '501',
            'Mock gateway does not support this payment operation.'
        );
    }

    private static commercepayments.GatewayResponse tokenize(
        commercepayments.PaymentMethodTokenizationRequest request
    ) {
        String scenario = 'SUCCESS';
        if (request.additionalData != null &&
            request.additionalData.containsKey('mockScenario')) {
            scenario = request.additionalData.get('mockScenario').toUpperCase();
        }
        if (scenario == 'INVALID') {
            return new commercepayments.GatewayErrorResponse(
                '400',
                'Mock payment method is invalid.'
            );
        }
        if (scenario == 'ERROR') {
            return new commercepayments.GatewayErrorResponse(
                '503',
                'Mock gateway processing error.'
            );
        }
        commercepayments.PaymentMethodTokenizationResponse response =
            new commercepayments.PaymentMethodTokenizationResponse();
        response.setGatewayTokenEncrypted('MOCK:' + scenario + ':' + newGatewayReference());
        response.setGatewayDate(System.now());
        response.setGatewayResultCode('MOCK_APPROVED');
        response.setGatewayResultCodeDescription('Mock token created.');
        response.setSalesforceResultCodeInfo(SUCCESS);
        return response;
    }

    private static commercepayments.GatewayResponse authorize(
        commercepayments.AuthorizationRequest request
    ) {
        String token = getPaymentMethodToken(request.paymentMethod.id);
        commercepayments.GatewayResponse error = scenarioError(token);
        if (error != null) return error;
        commercepayments.AuthorizationResponse response =
            new commercepayments.AuthorizationResponse();
        response.setAmount(request.amount);
        response.setGatewayDate(System.now());
        response.setGatewayReferenceNumber(newGatewayReference());
        response.setGatewayAuthCode(token);
        response.setPaymentMethodTokenizationResponse(tokenResult(token));
        if (isDecline(token)) {
            response.setGatewayResultCode('MOCK_DECLINED');
            response.setGatewayResultCodeDescription('Mock decline scenario.');
            response.setSalesforceResultCodeInfo(DECLINE);
        } else {
            response.setGatewayResultCode('MOCK_APPROVED');
            response.setGatewayResultCodeDescription('Mock authorization approved.');
            response.setSalesforceResultCodeInfo(SUCCESS);
        }
        return response;
    }

    private static commercepayments.GatewayResponse sale(
        commercepayments.SaleRequest request
    ) {
        String token = getPaymentMethodToken(request.paymentMethod.id);
        commercepayments.GatewayResponse error = scenarioError(token);
        if (error != null) return error;
        commercepayments.SaleResponse response = new commercepayments.SaleResponse();
        response.setAmount(request.amount);
        response.setGatewayDate(System.now());
        response.setGatewayReferenceNumber(newGatewayReference());
        response.setPaymentMethodTokenizationResponse(tokenResult(token));
        if (isDecline(token)) {
            response.setGatewayResultCode('MOCK_DECLINED');
            response.setGatewayResultCodeDescription('Mock decline scenario.');
            response.setSalesforceResultCodeInfo(DECLINE);
        } else {
            response.setGatewayResultCode('MOCK_APPROVED');
            response.setGatewayResultCodeDescription('Mock sale approved.');
            response.setSalesforceResultCodeInfo(SUCCESS);
        }
        return response;
    }

    private static commercepayments.GatewayResponse capture(
        commercepayments.CaptureRequest request
    ) {
        PaymentAuthorization authorization = [
            SELECT GatewayAuthCode
            FROM PaymentAuthorization
            WHERE Id = :request.paymentAuthorizationId
            WITH USER_MODE
            LIMIT 1
        ];
        String token = authorization.GatewayAuthCode;
        commercepayments.GatewayResponse error = scenarioError(token);
        if (error != null) return error;
        commercepayments.CaptureResponse response =
            new commercepayments.CaptureResponse();
        response.setAmount(request.amount);
        response.setGatewayDate(System.now());
        response.setGatewayReferenceNumber(newGatewayReference());
        response.setGatewayResultCode('MOCK_CAPTURED');
        response.setGatewayResultCodeDescription('Mock capture completed.');
        response.setSalesforceResultCodeInfo(
            isDecline(token) ? DECLINE : SUCCESS
        );
        return response;
    }

    private static commercepayments.GatewayResponse refund(
        commercepayments.ReferencedRefundRequest request
    ) {
        Payment payment = [
            SELECT PaymentAuthorization.GatewayAuthCode
            FROM Payment
            WHERE Id = :request.paymentId
            WITH USER_MODE
            LIMIT 1
        ];
        commercepayments.GatewayResponse error =
            scenarioError(payment.PaymentAuthorization.GatewayAuthCode);
        if (error != null) return error;
        commercepayments.ReferencedRefundResponse response =
            new commercepayments.ReferencedRefundResponse();
        response.setAmount(request.amount);
        response.setGatewayDate(System.now());
        response.setGatewayReferenceNumber(newGatewayReference());
        response.setGatewayResultCode('MOCK_REFUNDED');
        response.setGatewayResultCodeDescription('Mock refund completed.');
        response.setSalesforceResultCodeInfo(SUCCESS);
        return response;
    }

    private static commercepayments.GatewayResponse unreferencedRefund(
        commercepayments.UnreferencedRefundRequest request
    ) {
        String token = getPaymentMethodToken(request.paymentMethod.id);
        commercepayments.GatewayResponse error = scenarioError(token);
        if (error != null) return error;
        commercepayments.UnreferencedRefundResponse response =
            new commercepayments.UnreferencedRefundResponse();
        response.setAmount(request.amount);
        response.setGatewayDate(System.now());
        response.setGatewayReferenceNumber(newGatewayReference());
        response.setGatewayResultCode('MOCK_REFUNDED');
        response.setGatewayResultCodeDescription('Mock unreferenced refund completed.');
        response.setSalesforceResultCodeInfo(SUCCESS);
        return response;
    }

    private static commercepayments.GatewayResponse reverseAuthorization(
        commercepayments.AuthorizationReversalRequest request
    ) {
        PaymentAuthorization authorization = [
            SELECT GatewayAuthCode
            FROM PaymentAuthorization
            WHERE Id = :request.paymentAuthorizationId
            WITH USER_MODE
            LIMIT 1
        ];
        commercepayments.GatewayResponse error =
            scenarioError(authorization.GatewayAuthCode);
        if (error != null) return error;
        commercepayments.AuthorizationReversalResponse response =
            new commercepayments.AuthorizationReversalResponse();
        response.setAmount(request.amount);
        response.setGatewayDate(System.now());
        response.setGatewayReferenceNumber(newGatewayReference());
        response.setGatewayResultCode('MOCK_REVERSED');
        response.setGatewayResultCodeDescription('Mock authorization reversed.');
        response.setSalesforceResultCodeInfo(SUCCESS);
        return response;
    }

    private static commercepayments.PaymentMethodTokenizationResponse tokenResult(
        String token
    ) {
        commercepayments.PaymentMethodTokenizationResponse response =
            new commercepayments.PaymentMethodTokenizationResponse();
        response.setGatewayTokenEncrypted(token);
        response.setSalesforceResultCodeInfo(SUCCESS);
        return response;
    }

    private static String getPaymentMethodToken(Id paymentMethodId) {
        if (paymentMethodId == null) {
            return 'MOCK:SUCCESS';
        }
        Schema.SObjectType objectType = paymentMethodId.getSObjectType();
        if (objectType == SavedPaymentMethod.SObjectType) {
            List<SavedPaymentMethod> methods = [
                SELECT GatewayToken
                FROM SavedPaymentMethod
                WHERE Id = :paymentMethodId
                WITH USER_MODE
                LIMIT 1
            ];
            if (!methods.isEmpty()) {
                return methods[0].GatewayToken;
            }
        } else if (objectType == CardPaymentMethod.SObjectType) {
            List<CardPaymentMethod> methods = [
                SELECT GatewayToken, GatewayTokenEncrypted
                FROM CardPaymentMethod
                WHERE Id = :paymentMethodId
                WITH USER_MODE
                LIMIT 1
            ];
            if (!methods.isEmpty()) {
                return String.isNotBlank(methods[0].GatewayTokenEncrypted)
                    ? methods[0].GatewayTokenEncrypted
                    : methods[0].GatewayToken;
            }
        }
        throw new MockPaymentException();
    }

    private static Boolean isDecline(String token) {
        return token != null && token.toUpperCase().contains(':DECLINE');
    }

    private static commercepayments.GatewayResponse scenarioError(String token) {
        if (token != null && token.toUpperCase().contains(':INVALID')) {
            return new commercepayments.GatewayErrorResponse(
                '400',
                'Mock payment method is invalid.'
            );
        }
        if (token != null && (
            token.toUpperCase().contains(':ERROR') ||
            token.toUpperCase().contains(':GATEWAY_ERROR')
        )) {
            return new commercepayments.GatewayErrorResponse(
                '503',
                'Mock gateway processing error.'
            );
        }
        return null;
    }

    private static String newGatewayReference() {
        return 'MOCK-' + EncodingUtil.convertToHex(Crypto.generateAesKey(128));
    }

    private class MockPaymentException extends Exception {}
}
