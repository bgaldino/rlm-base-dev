/**
 * Controller for the "Prepare for Activation" Order quick action (large deals).
 *
 * Large-deal (IsLargeDeal=true) orders bypass inline validation/treatment
 * resolution at activation. The platform instead requires an explicit
 * preProcessSalesTransaction call that runs asynchronously and stamps the
 * Order's PreprocessingStatus bits. Activation then only succeeds once bit 0
 * (Validation) is Completed ('C'). With invoicing disabled the billing/tax/usage
 * resolution steps self-skip (they gate on orgHasInvoicingEnabled), so passing
 * their flags as true is safe regardless of org settings.
 *
 * PreprocessingStatus is a 4-char string, one char per bit:
 *   index 0 = Validation, 1 = BillingTreatment, 2 = TaxTreatment, 3 = UsageRate
 *   'C' = Completed, 'N' = Not started/skipped, 'Q' = Queued, 'F' = Failed
 */
public with sharing class RLM_PreProcessOrderController {

    private static final Set<String> DONE_STATUSES = new Set<String>{ 'Completed' };
    private static final Set<String> FAILED_STATUSES = new Set<String>{ 'Failed', 'Failure', 'Canceled', 'Cancelled' };
    private static final String ACTIVATED_STATUS = 'Activated';

    /** Lightweight order context for the action UI (gating + current state). */
    @AuraEnabled(cacheable=false)
    public static String getOrderInfo(String orderId) {
        if (String.isBlank(orderId)) {
            return errorJson('No order id provided.');
        }
        try {
            List<Order> orders = [
                SELECT Id, OrderNumber, Status, IsLargeDeal, PreprocessingStatus
                FROM Order
                WHERE Id = :orderId
                LIMIT 1
            ];
            if (orders.isEmpty()) {
                return errorJson('Order not found or not accessible.');
            }
            Order o = orders[0];
            return JSON.serialize(new Map<String, Object>{
                'success' => true,
                'orderNumber' => o.OrderNumber,
                'status' => o.Status,
                'isLargeDeal' => o.IsLargeDeal == true,
                'preprocessingStatus' => o.PreprocessingStatus,
                'validationComplete' => isValidationComplete(o.PreprocessingStatus),
                'activated' => ACTIVATED_STATUS.equalsIgnoreCase(o.Status)
            });
        } catch (Exception e) {
            return errorJson(e.getMessage());
        }
    }

    /** Kicks off the async preprocess job. Returns the AsyncOperationTracker requestId. */
    @AuraEnabled(cacheable=false)
    public static String startPreprocess(String orderId) {
        if (String.isBlank(orderId)) {
            return errorJson('No order id provided.');
        }
        try {
            Invocable.Action action = Invocable.Action.createStandardAction('preProcessSalesTransaction');
            action.setInvocationParameter('salesTransactionId', String.valueOf(orderId));
            action.setInvocationParameter('shouldValidateDataShape', true);
            // Self-gated on orgHasInvoicingEnabled(); harmless (no-op) when invoicing is off.
            action.setInvocationParameter('shouldResolveBillingTreatments', true);
            action.setInvocationParameter('shouldResolveTaxTreatments', true);
            action.setInvocationParameter('shouldResolveUsageRates', true);
            List<Invocable.Action.Result> results = action.invoke();
            if (results == null || results.isEmpty()) {
                return errorJson('Preprocess action returned no result.');
            }
            Invocable.Action.Result r = results[0];
            if (!r.isSuccess()) {
                return errorJson('Preprocess failed: ' + String.valueOf(r.getErrors()));
            }
            Map<String, Object> out = r.getOutputParameters();
            String requestId = out != null ? String.valueOf(out.get('requestId')) : null;
            return JSON.serialize(new Map<String, Object>{
                'success' => true,
                'requestId' => requestId
            });
        } catch (Exception e) {
            return errorJson('Preprocess error: ' + e.getMessage());
        }
    }

    /** Polls the async job + current order state. LWC calls this on an interval. */
    @AuraEnabled(cacheable=false)
    public static String getStatus(String orderId, String requestId) {
        if (String.isBlank(orderId)) {
            return errorJson('No order id provided.');
        }
        try {
            String trackerStatus = null;
            if (String.isNotBlank(requestId)) {
                List<AsyncOperationTracker> trackers = [
                    SELECT Id, Status FROM AsyncOperationTracker WHERE Id = :requestId LIMIT 1
                ];
                if (!trackers.isEmpty()) {
                    trackerStatus = trackers[0].Status;
                }
            }
            // Fallback: most recent PreprocessOrder tracker for this order.
            if (trackerStatus == null && String.isNotBlank(orderId)) {
                List<AsyncOperationTracker> trackers = [
                    SELECT Id, Status FROM AsyncOperationTracker
                    WHERE ReferenceEntityId = :orderId AND JobType = 'PreprocessOrder'
                    ORDER BY CreatedDate DESC LIMIT 1
                ];
                if (!trackers.isEmpty()) {
                    trackerStatus = trackers[0].Status;
                }
            }
            List<Order> orders = [
                SELECT Id, Status, PreprocessingStatus FROM Order WHERE Id = :orderId LIMIT 1
            ];
            if (orders.isEmpty()) {
                return errorJson('Order not found or not accessible.');
            }
            Order o = orders[0];
            Boolean failed = trackerStatus != null && FAILED_STATUSES.contains(trackerStatus);
            Boolean trackerDone = trackerStatus != null && DONE_STATUSES.contains(trackerStatus);
            Boolean validationComplete = isValidationComplete(o.PreprocessingStatus);
            return JSON.serialize(new Map<String, Object>{
                'success' => true,
                'trackerStatus' => trackerStatus,
                'preprocessingStatus' => o.PreprocessingStatus,
                'orderStatus' => o.Status,
                'done' => trackerDone || validationComplete,
                'failed' => failed,
                'ready' => validationComplete,
                'activated' => ACTIVATED_STATUS.equalsIgnoreCase(o.Status)
            });
        } catch (Exception e) {
            return errorJson(e.getMessage());
        }
    }

    /** Sets the order to Activated. Surfaces the platform validation error if it still blocks. */
    @AuraEnabled(cacheable=false)
    public static String activateOrder(String orderId) {
        if (String.isBlank(orderId)) {
            return errorJson('No order id provided.');
        }
        try {
            update new Order(Id = orderId, Status = ACTIVATED_STATUS);
            return JSON.serialize(new Map<String, Object>{ 'success' => true });
        } catch (Exception e) {
            return errorJson(e.getMessage());
        }
    }

    /** Bit 0 (Validation) is the only bit activation unconditionally requires. */
    @TestVisible
    private static Boolean isValidationComplete(String preprocessingStatus) {
        return String.isNotBlank(preprocessingStatus)
            && preprocessingStatus.length() >= 1
            && preprocessingStatus.substring(0, 1).equalsIgnoreCase('C');
    }

    private static String errorJson(String msg) {
        return JSON.serialize(new Map<String, Object>{
            'success' => false,
            'errorMessage' => String.isBlank(msg) ? 'Unknown error' : msg
        });
    }
}
