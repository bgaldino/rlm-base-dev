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

    /**
     * Seed treatment (created by seed_large_deal_billing_treatment) used to make
     * large-deal billing-treatment resolution a no-op. ExcludeFromBilling=Yes,
     * Default-selection policy, no LegalEntity — avoids the non-bulk-safe
     * legal-entity resolver that fails at large-deal scale.
     */
    @TestVisible
    private static final String LARGE_DEAL_EXCLUDE_TREATMENT = 'RLM Large Deal - Exclude from Billing';
    private static Id largeDealExcludeTreatmentId;
    private static Boolean excludeTreatmentResolved = false;


    /** Lightweight order context for the action UI (gating + current state). */
    @AuraEnabled(cacheable=false)
    public static String getOrderInfo(String orderId) {
        if (String.isBlank(orderId)) {
            return errorJson('No order id provided.');
        }
        try {
            Id oid = Id.valueOf(orderId);
            List<Order> orders = [
                SELECT Id, OrderNumber, Status, IsLargeDeal, PreprocessingStatus
                FROM Order
                WHERE Id = :oid
                WITH USER_MODE
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
            Id oid = Id.valueOf(orderId);
            // Orders created via createOrdersFromQuote come back with stale pricing, so
            // preprocess validation (bit 0) fails with "the prices aren't updated. Click
            // Reprice All". Reprice large-deal orders up front so the button is one-click.
            // No-op for standard orders and for orders already priced.
            repriceLargeDealOrderIfNeeded(oid);

            // Large-deal billing fix: pre-stamp an Exclude-from-Billing treatment on
            // unresolved order items so the platform's legal-entity treatment resolver
            // (not bulk-safe at large-deal scale) finds nothing to fetch and bit 1
            // (BillingTreatment) completes instead of failing. No-op for standard orders.
            stampLargeDealExcludeTreatment(oid);

            Invocable.Action action = Invocable.Action.createStandardAction('preProcessSalesTransaction');
            action.setInvocationParameter('salesTransactionId', String.valueOf(oid));
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
            Id oid = Id.valueOf(orderId);
            String trackerStatus = null;
            if (String.isNotBlank(requestId)) {
                Id reqId = Id.valueOf(requestId);
                List<AsyncOperationTracker> trackers = [
                    SELECT Id, Status FROM AsyncOperationTracker WHERE Id = :reqId WITH USER_MODE LIMIT 1
                ];
                if (!trackers.isEmpty()) {
                    trackerStatus = trackers[0].Status;
                }
            }
            // Fallback: most recent PreprocessOrder tracker for this order.
            if (trackerStatus == null) {
                List<AsyncOperationTracker> trackers = [
                    SELECT Id, Status FROM AsyncOperationTracker
                    WHERE ReferenceEntityId = :oid AND JobType = 'PreprocessOrder'
                    WITH USER_MODE
                    ORDER BY CreatedDate DESC LIMIT 1
                ];
                if (!trackers.isEmpty()) {
                    trackerStatus = trackers[0].Status;
                }
            }
            List<Order> orders = [
                SELECT Id, Status, PreprocessingStatus FROM Order WHERE Id = :oid WITH USER_MODE LIMIT 1
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
            Id oid = Id.valueOf(orderId);
            // User-mode DML: the activating user must have edit on Order.Status.
            update as user new Order(Id = oid, Status = ACTIVATED_STATUS);
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

    /**
     * Reprice a large-deal order via a Place Sales Transaction (PATCH header, Force
     * pricing, Skip configuration). Orders created via createOrdersFromQuote report
     * a "completed" CalculationStatus but still fail preprocess validation with "the
     * prices aren't updated. Click Reprice All" until an explicit reprice runs — so
     * the reprice is unconditional for large deals rather than gated on
     * CalculationStatus. The executor returns once pricing is computed, and the
     * async preprocess job validates against the committed result. No-op for
     * standard orders and unknown ids.
     */
    @TestVisible
    private static void repriceLargeDealOrderIfNeeded(Id orderId) {
        List<Order> orders = [
            SELECT Id, IsLargeDeal FROM Order WHERE Id = :orderId WITH USER_MODE LIMIT 1
        ];
        if (orders.isEmpty() || orders[0].IsLargeDeal != true) {
            return;
        }
        RevSalesTrxn.RecordResource header =
            new RevSalesTrxn.RecordResource(Order.getSObjectType(), 'PATCH', orderId);
        header.fieldValues = new Map<String, Object>();
        List<RevSalesTrxn.RecordWithReferenceRequest> records =
            new List<RevSalesTrxn.RecordWithReferenceRequest>{
                new RevSalesTrxn.RecordWithReferenceRequest('refHeader', header)
            };
        RevSalesTrxn.GraphRequest graph =
            new RevSalesTrxn.GraphRequest('PrepareForActivationReprice', records);
        // Typed nulls so the overloaded execute() signature resolves unambiguously.
        RevSalesTrxn.CatalogRatesPreferenceEnum ratesPref = null;
        RevSalesTrxn.TaxPreferenceEnum taxPref = null;
        RevSalesTrxn.PlaceSalesTransactionResponse resp =
            RevSalesTrxn.PlaceSalesTransactionExecutor.execute(
                graph,
                RevSalesTrxn.PricingPreferenceEnum.FORCE,
                RevSalesTrxn.ConfigurationExecutionEnum.SKIP,
                new RevSalesTrxn.ConfigurationOptionsInput(),
                null,
                ratesPref,
                taxPref,
                null
            );
        if (resp == null || !resp.isSuccess) {
            throw new RLM_PreProcessException(
                'Reprice failed: ' + (resp != null ? String.valueOf(resp.errorResponse) : 'null response')
            );
        }
    }

    /**
     * For large-deal orders, stamp the Exclude-from-Billing treatment onto order
     * items that don't yet have a billing treatment. The resolver only fetches
     * treatments for items where BillingTreatmentId == null, so pre-stamping turns
     * the buggy bulk legal-entity query into a no-op. Idempotent (never overwrites
     * an existing treatment) and a no-op when the order isn't a large deal or the
     * seed treatment is absent (e.g. billing feature off).
     */
    @TestVisible
    private static void stampLargeDealExcludeTreatment(Id orderId) {
        List<Order> orders = [SELECT Id, IsLargeDeal FROM Order WHERE Id = :orderId WITH USER_MODE LIMIT 1];
        if (orders.isEmpty() || orders[0].IsLargeDeal != true) {
            return;
        }
        Id treatmentId = resolveLargeDealExcludeTreatmentId();
        if (treatmentId == null) {
            return;
        }
        List<OrderItem> toStamp = [
            SELECT Id FROM OrderItem
            WHERE OrderId = :orderId AND BillingTreatmentId = null
            WITH USER_MODE
        ];
        if (toStamp.isEmpty()) {
            return;
        }
        for (OrderItem oi : toStamp) {
            oi.BillingTreatmentId = treatmentId;
        }
        // 2,700-line repro is well within the 10k DML-row limit. Orders large
        // enough to exceed it can't be stamped in one synchronous transaction;
        // such scale would require an async/batch path (out of scope here).
        update as user toStamp;
    }

    /** Cached lookup of the seed Exclude-from-Billing treatment by name. */
    @TestVisible
    private static Id resolveLargeDealExcludeTreatmentId() {
        if (!excludeTreatmentResolved) {
            excludeTreatmentResolved = true;
            List<BillingTreatment> bts = [
                SELECT Id FROM BillingTreatment
                WHERE Name = :LARGE_DEAL_EXCLUDE_TREATMENT AND Status = 'Active'
                WITH USER_MODE
                LIMIT 1
            ];
            largeDealExcludeTreatmentId = bts.isEmpty() ? null : bts[0].Id;
        }
        return largeDealExcludeTreatmentId;
    }

    private static String errorJson(String msg) {
        return JSON.serialize(new Map<String, Object>{
            'success' => false,
            'errorMessage' => String.isBlank(msg) ? 'Unknown error' : msg
        });
    }

    public class RLM_PreProcessException extends Exception {}
}
