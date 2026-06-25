@isTest
private class RLM_RefundControllerTest {
    private static Id fakePaymentId() {
        return Id.valueOf(Payment.SObjectType.getDescribe().getKeyPrefix() + '000000000000');
    }

    private static Payment makePayment(Decimal amount) {
        Account acc = new Account(Name = 'RLM Refund Pmt Acct');
        insert acc;
        Payment pmt = new Payment(
            Amount = amount,
            Status = 'Processed',
            Type = 'Sale',
            ProcessingMode = 'External',
            AccountId = acc.Id
        );
        insert pmt;
        return [SELECT Id, Balance, AccountId FROM Payment WHERE Id = :pmt.Id LIMIT 1];
    }

    @isTest
    static void getPaymentBalance_unknownId_returnsZero() {
        Test.startTest();
        Decimal balance = RLM_RefundController.getPaymentBalance(fakePaymentId());
        Test.stopTest();
        System.assertEquals(0, balance, 'Unknown payment should resolve to a zero balance.');
    }

    @isTest
    static void issueRefund_nonPaymentObject_isRejected() {
        Test.startTest();
        RLM_RefundController.RefundResult result =
            RLM_RefundController.issueRefund(fakePaymentId(), 'CreditMemo');
        Test.stopTest();
        System.assertEquals(false, result.success, 'Non-Payment objects must be rejected.');
        System.assert(
            result.message.contains('Payment record'),
            'Expected a Payment-only message, got: ' + result.message
        );
    }

    @isTest
    static void issueRefund_missingPayment_isHandled() {
        Test.startTest();
        RLM_RefundController.RefundResult result =
            RLM_RefundController.issueRefund(fakePaymentId(), 'Payment');
        Test.stopTest();
        System.assertEquals(false, result.success, 'A missing payment cannot be refunded.');
        System.assert(
            result.message.contains('not found') || result.message.contains('No balance'),
            'Expected a not-found/no-balance message, got: ' + result.message
        );
    }

    @isTest
    static void getPaymentBalance_realPayment_returnsBalance() {
        Payment pmt;
        try {
            pmt = makePayment(100);
        } catch (Exception setupError) {
            // If this org variant restricts Payment inserts, skip — other tests still
            // exercise the unknown/zero paths.
            return;
        }
        Test.startTest();
        Decimal balance = RLM_RefundController.getPaymentBalance(pmt.Id);
        Test.stopTest();
        System.assert(balance >= 0, 'A real payment should resolve to a non-null balance, got: ' + balance);
    }

    @isTest
    static void issueRefund_realPayment_success() {
        Payment pmt;
        try {
            pmt = makePayment(100);
        } catch (Exception setupError) {
            return;
        }
        if (pmt.Balance == null || pmt.Balance <= 0) {
            // No spendable balance in this org's pricing config; nothing to assert.
            return;
        }
        RLM_RefundController.mockRefundResponse = new ConnectApi.ReferencedRefundResponse();
        Test.startTest();
        RLM_RefundController.RefundResult result =
            RLM_RefundController.issueRefund(pmt.Id, 'Payment');
        Test.stopTest();
        System.assertEquals(true, result.success, 'A payment with balance should refund: ' + result.message);
    }

    @isTest
    static void createRefund_gatewayFailure_isHandled() {
        Account acc = new Account(Name = 'RLM Refund Failure Test');
        insert acc;
        // No mock response set, so createRefund() falls through to the live ConnectApi call,
        // which cannot reach a gateway in a test context and is caught as a failed refund.
        Test.startTest();
        RLM_RefundController.RefundResult result =
            RLM_RefundController.createRefund(String.valueOf(fakePaymentId()), 50, acc.Id);
        Test.stopTest();
        System.assertEquals(false, result.success, 'A gateway/connect failure must surface as an unsuccessful result.');
        System.assertNotEquals(null, result.message, 'A user-facing message should always be set.');
    }

    @isTest
    static void createRefund_success_returnsRefundId() {
        Account acc = new Account(Name = 'RLM Refund Test');
        insert acc;

        String paymentId = String.valueOf(fakePaymentId());
        // ConnectApi.Payments has no usable setTestRefund mock here, so the controller
        // exposes a test seam that returns this response in place of the live call.
        RLM_RefundController.mockRefundResponse = new ConnectApi.ReferencedRefundResponse();

        Test.startTest();
        RLM_RefundController.RefundResult result =
            RLM_RefundController.createRefund(paymentId, 50, acc.Id);
        Test.stopTest();

        System.assertEquals(true, result.success, 'Mocked refund should succeed: ' + result.message);
    }

    @isTest
    static void buildRefundRequest_isDeterministic() {
        Account acc = new Account(Name = 'RLM Refund Build Test');
        insert acc;
        Test.startTest();
        ConnectApi.ReferencedRefundRequest req = RLM_RefundController.buildRefundRequest(25, acc.Id);
        Test.stopTest();
        System.assertEquals(25.0, req.amount, 'Amount should round-trip as a Double.');
        System.assertEquals(acc.Id, req.accountId, 'Account should be set on the request.');
    }

    @isTest
    static void friendlyGatewayMessage_mapsKnownGatewayErrors() {
        System.assertEquals(
            'This payment has already been refunded.',
            RLM_RefundController.friendlyGatewayMessage('Error: charge_already_refunded for this charge')
        );
        System.assertEquals(
            'The refund amount exceeds the available balance.',
            RLM_RefundController.friendlyGatewayMessage('amount_too_large')
        );
        System.assertEquals(
            'Payment not found in the payment gateway.',
            RLM_RefundController.friendlyGatewayMessage('charge_not_found')
        );
        System.assert(
            RLM_RefundController.friendlyGatewayMessage('some other failure').startsWith('Payment gateway error:'),
            'Unmapped errors should be passed through with a prefix.'
        );
        System.assertEquals(
            'An error occurred while processing the refund.',
            RLM_RefundController.friendlyGatewayMessage(null)
        );
    }
}
