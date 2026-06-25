public with sharing class RLM_RefundController {
    private static final String CLIENT_CONTEXT = 'RLM_RefundButton';
    private static final String REFUND_COMMENT = 'Refund issued via Refund button';

    // Test seam: ConnectApi.Payments does not expose a usable setTestRefund mock in
    // this API version, and Connect in Apex calls can't hit a real gateway in tests.
    // When set in a test, createRefund() returns this in place of the live call.
    @TestVisible
    private static ConnectApi.ReferencedRefundResponse mockRefundResponse;

    @AuraEnabled(cacheable=true)
    public static Decimal getPaymentBalance(String recordId) {
        try {
            List<Payment> payments = [
                SELECT Balance FROM Payment WHERE Id = :recordId WITH USER_MODE LIMIT 1
            ];
            if (payments.isEmpty() || payments[0].Balance == null) {
                return 0;
            }
            return payments[0].Balance;
        } catch (Exception e) {
            return 0;
        }
    }

    @AuraEnabled
    public static RefundResult issueRefund(String recordId, String objectType) {
        RefundResult result = new RefundResult();
        try {
            // Refunds are issued against an existing Payment only. CreditMemo refunds
            // follow a different (apply-credit-memo) flow and are intentionally out of scope.
            if (objectType != 'Payment') {
                result.success = false;
                result.message = 'Refunds can only be issued from a Payment record.';
                return result;
            }

            List<Payment> payments = [
                SELECT Balance, AccountId FROM Payment WHERE Id = :recordId WITH USER_MODE LIMIT 1
            ];
            if (payments.isEmpty()) {
                result.success = false;
                result.message = 'Payment record not found or not accessible.';
                return result;
            }

            Payment payment = payments[0];
            Decimal balanceAmount = payment.Balance;
            if (balanceAmount == null || balanceAmount <= 0) {
                result.success = false;
                result.message = 'No balance available to refund.';
                return result;
            }

            result = createRefund(recordId, balanceAmount, payment.AccountId);
        } catch (Exception e) {
            result.success = false;
            result.message = 'Error issuing refund: ' + e.getMessage();
        }
        return result;
    }

    @TestVisible
    private static ConnectApi.ReferencedRefundRequest buildRefundRequest(Decimal amount, Id accountId) {
        ConnectApi.ReferencedRefundRequest request = new ConnectApi.ReferencedRefundRequest();
        request.amount = amount == null ? null : amount.doubleValue();
        request.accountId = accountId;
        request.clientContext = CLIENT_CONTEXT;
        request.comments = REFUND_COMMENT;
        // effectiveDate is intentionally omitted; the platform defaults it to the
        // processing time, and leaving it unset keeps the request deterministic.
        return request;
    }

    @TestVisible
    private static RefundResult createRefund(String paymentId, Decimal amount, Id accountId) {
        RefundResult result = new RefundResult();
        try {
            ConnectApi.ReferencedRefundRequest request = buildRefundRequest(amount, accountId);
            // In-org Connect API call (no callout / named credential). Target-agnostic:
            // routes through the payment's own gateway adapter using the running user's context.
            ConnectApi.ReferencedRefundResponse response =
                (Test.isRunningTest() && mockRefundResponse != null)
                    ? mockRefundResponse
                    : ConnectApi.Payments.refund(request, paymentId);

            result.success = true;
            result.refundId = extractRefundId(response);
            result.message = String.isNotBlank(result.refundId)
                ? 'Refund issued successfully. Refund ID: ' + result.refundId
                : 'Refund issued successfully.';
        } catch (ConnectApi.ConnectApiException ce) {
            result.success = false;
            result.message = friendlyGatewayMessage(ce.getMessage());
        } catch (Exception e) {
            result.success = false;
            result.message = 'Error creating refund: ' + e.getMessage();
        }
        return result;
    }

    // The response representation varies by release, so the id is read defensively
    // from the serialized payload rather than a fixed getter.
    private static String extractRefundId(ConnectApi.ReferencedRefundResponse response) {
        if (response == null) {
            return null;
        }
        try {
            Map<String, Object> parsed =
                (Map<String, Object>) JSON.deserializeUntyped(JSON.serialize(response));
            Object idValue = parsed.get('refundId') != null ? parsed.get('refundId') : parsed.get('id');
            return idValue != null ? String.valueOf(idValue) : null;
        } catch (Exception e) {
            return null;
        }
    }

    @TestVisible
    private static String friendlyGatewayMessage(String rawMessage) {
        if (String.isBlank(rawMessage)) {
            return 'An error occurred while processing the refund.';
        }
        String lower = rawMessage.toLowerCase();
        if (lower.contains('charge_already_refunded')) {
            return 'This payment has already been refunded.';
        }
        if (lower.contains('amount_too_large')) {
            return 'The refund amount exceeds the available balance.';
        }
        if (lower.contains('charge_not_found')) {
            return 'Payment not found in the payment gateway.';
        }
        return 'Payment gateway error: ' + rawMessage;
    }

    public class RefundResult {
        @AuraEnabled public Boolean success;
        @AuraEnabled public String message;
        @AuraEnabled public String refundId;
    }
}
