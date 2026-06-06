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

    // AsyncOperationTracker terminal statuses (the job is no longer running).
    private static final Set<String> TRACKER_TERMINAL_STATUSES = new Set<String>{
        'Completed', 'Failed', 'Failure', 'Canceled', 'Cancelled'
    };

    // Order.CalculationStatus buckets (core OrderCalculationStatus enum — see
    // docs/analysis/large-stx-reprice-core-code-answers.md). Used to classify a
    // large-deal reprice as in-progress / failed / committed before the preprocess
    // job is enqueued. NEGATIVE model (as the quote wizard uses): a value in NEITHER
    // the in-progress NOR the failed/investigate set is a terminal-success candidate.
    // The authoritative "safe to preprocess" gate, however, is
    // Order.ValidationResult == null — the field the platform preprocess validation
    // actually checks ("the prices aren't updated" fires while it is non-null).
    private static final Set<String> PRICING_IN_PROGRESS_STATUSES = new Set<String>{
        'NotStarted', 'ContextHydrationInProgress', 'QueuedForConfiguration',
        'ConfigurationInProgress', 'QueuedForPricing', 'QueuedForPricingAndSaving',
        'PriceCalculationInProgress', 'TaxCalculationWaiting', 'QueuedForSaving',
        'Saving', 'ReconciliationInProgress'
    };
    private static final Set<String> PRICING_FAILED_STATUSES = new Set<String>{
        'PstBaseStepFailed', 'ConfigurationFailed', 'GroupRampConfigurationFailed',
        'PriceCalculationFailed', 'TaxCalculationFailed', 'SaveFailedOrIncomplete',
        'ReconciliationFailed', 'OrderRequestFailed'
    };
    // Partial-save states — surface for investigation, never auto-retry.
    private static final Set<String> PRICING_INVESTIGATE_STATUSES = new Set<String>{
        'OrderRequestPartiallySaved', 'PartialSaveSuccess'
    };

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

    /**
     * Phase 1 of Prepare-for-Activation. For a large deal, kick the async reprice
     * (orders created via createOrdersFromQuote carry ValidationResult=
     * TransactionIncomplete, which the preprocess job rejects as "the prices aren't
     * updated") and pre-stamp the exclude-billing treatment. Does NOT enqueue the
     * preprocess job — that is enqueuePreprocess(), called by the LWC only after it
     * polls getPricingStatus() and confirms pricing committed. This split removes
     * the race where preprocess validated against still-async pricing and failed on
     * the first click. Standard orders return phase='ready_to_enqueue' (reprice +
     * stamp are no-ops) so the LWC enqueues immediately, preserving prior behavior.
     */
    @AuraEnabled(cacheable=false)
    public static String startPreprocess(String orderId) {
        if (String.isBlank(orderId)) {
            return errorJson('No order id provided.');
        }
        try {
            Id oid = Id.valueOf(orderId);
            Boolean isLarge = isLargeDealOrder(oid);
            // Large-deal reprice prices ASYNCHRONOUSLY (dispatch keyed on IsLargeDeal);
            // throws only on a synchronous accept failure. No-op for standard/unknown.
            repriceLargeDealOrderIfNeeded(oid);
            // Pre-stamp the exclude-from-billing treatment (idempotent; no-op for
            // standard orders / when the seed treatment is absent).
            stampLargeDealExcludeTreatment(oid);
            return JSON.serialize(new Map<String, Object>{
                'success' => true,
                'isLargeDeal' => isLarge,
                'phase' => isLarge ? 'repricing' : 'ready_to_enqueue'
            });
        } catch (Exception e) {
            return errorJson('Preprocess error: ' + e.getMessage());
        }
    }

    /**
     * Phase 2. Classify the large-deal reprice's pricing state so the LWC poll can
     * wait, retry the reprice, or enqueue preprocess. Committed gate =
     * Order.ValidationResult == null (the field the platform preprocess validation
     * checks) AND a terminal-success CalculationStatus AND no pending async PST work.
     */
    @AuraEnabled(cacheable=false)
    public static String getPricingStatus(String orderId) {
        if (String.isBlank(orderId)) {
            return errorJson('No order id provided.');
        }
        try {
            Id oid = Id.valueOf(orderId);
            List<Order> orders = [
                SELECT Id, CalculationStatus, ValidationResult
                FROM Order WHERE Id = :oid WITH USER_MODE LIMIT 1
            ];
            if (orders.isEmpty()) {
                return errorJson('Order not found or not accessible.');
            }
            Order o = orders[0];
            Integer pendingAsyncCount = countPendingAsync(oid);
            return JSON.serialize(new Map<String, Object>{
                'success' => true,
                'phase' => classifyPricingPhase(o.CalculationStatus, o.ValidationResult, pendingAsyncCount),
                'calculationStatus' => o.CalculationStatus,
                'validationResult' => o.ValidationResult,
                'pendingAsyncCount' => pendingAsyncCount
            });
        } catch (Exception e) {
            return errorJson(e.getMessage());
        }
    }

    /**
     * Phase 3. Enqueue the async preprocess job — the ONLY place this happens.
     * Re-verifies committed pricing for large deals (guards a stale/racing client)
     * and runs a server-side idempotency guard (skips if validation already complete
     * or a preprocess job is already in flight) so re-opens / multiple tabs cannot
     * double-enqueue.
     */
    @AuraEnabled(cacheable=false)
    public static String enqueuePreprocess(String orderId) {
        if (String.isBlank(orderId)) {
            return errorJson('No order id provided.');
        }
        try {
            Id oid = Id.valueOf(orderId);
            List<Order> orders = [
                SELECT Id, IsLargeDeal, CalculationStatus, ValidationResult, PreprocessingStatus
                FROM Order WHERE Id = :oid WITH USER_MODE LIMIT 1
            ];
            if (orders.isEmpty()) {
                return errorJson('Order not found or not accessible.');
            }
            Order o = orders[0];
            // Large deals: do not enqueue until pricing has committed.
            if (o.IsLargeDeal == true) {
                Integer pendingAsyncCount = countPendingAsync(oid);
                if (classifyPricingPhase(o.CalculationStatus, o.ValidationResult, pendingAsyncCount) != 'pricing_committed') {
                    return JSON.serialize(new Map<String, Object>{
                        'success' => false,
                        'phase' => 'pricing_not_committed',
                        'errorMessage' => 'Pricing has not committed yet.'
                    });
                }
            }
            // Idempotency: validation already complete, or a preprocess job in flight.
            if (isValidationComplete(o.PreprocessingStatus)) {
                return JSON.serialize(new Map<String, Object>{
                    'success' => true, 'alreadyEnqueued' => true, 'requestId' => null
                });
            }
            List<AsyncOperationTracker> inflight = [
                SELECT Id, Status FROM AsyncOperationTracker
                WHERE ReferenceEntityId = :oid AND JobType = 'PreprocessOrder'
                  AND Status NOT IN :TRACKER_TERMINAL_STATUSES
                WITH USER_MODE
                ORDER BY CreatedDate DESC LIMIT 1
            ];
            if (!inflight.isEmpty()) {
                return JSON.serialize(new Map<String, Object>{
                    'success' => true, 'alreadyEnqueued' => true, 'requestId' => inflight[0].Id
                });
            }
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
            Map<String, Object> outParams = r.getOutputParameters();
            String requestId = outParams != null ? String.valueOf(outParams.get('requestId')) : null;
            return JSON.serialize(new Map<String, Object>{
                'success' => true, 'requestId' => requestId
            });
        } catch (Exception e) {
            return errorJson('Preprocess error: ' + e.getMessage());
        }
    }

    /** True when the order exists and is a large deal. */
    @TestVisible
    private static Boolean isLargeDealOrder(Id orderId) {
        List<Order> orders = [SELECT Id, IsLargeDeal FROM Order WHERE Id = :orderId WITH USER_MODE LIMIT 1];
        return !orders.isEmpty() && orders[0].IsLargeDeal == true;
    }

    /** Count of non-terminal AsyncOperationTracker rows for the order (pending PST/async work). */
    private static Integer countPendingAsync(Id orderId) {
        return [
            SELECT COUNT() FROM AsyncOperationTracker
            WHERE ReferenceEntityId = :orderId AND Status NOT IN :TRACKER_TERMINAL_STATUSES
            WITH USER_MODE
        ];
    }

    /**
     * Pure classification of a large-deal reprice's pricing state. Param-based (no
     * SOQL/DML) so it is unit-testable — CalculationStatus and ValidationResult are
     * read-only platform fields that cannot be set via DML. Committed = pricing's
     * dirty flag cleared (ValidationResult null) AND a terminal-success
     * CalculationStatus (not in the in-progress / failed / investigate sets) AND no
     * pending async work. Failed/investigate are keyed on CalculationStatus (current
     * order state, authoritative); everything else is still in progress.
     */
    @TestVisible
    private static String classifyPricingPhase(String calcStatus, String validationResult, Integer pendingAsyncCount) {
        if (calcStatus != null && PRICING_FAILED_STATUSES.contains(calcStatus)) {
            return 'pricing_failed';
        }
        if (calcStatus != null && PRICING_INVESTIGATE_STATUSES.contains(calcStatus)) {
            return 'pricing_investigate';
        }
        Boolean pricingFinished = String.isNotBlank(calcStatus)
            && !PRICING_IN_PROGRESS_STATUSES.contains(calcStatus);
        Boolean noPending = (pendingAsyncCount == null || pendingAsyncCount <= 0);
        if (String.isBlank(validationResult) && pricingFinished && noPending) {
            return 'pricing_committed';
        }
        return 'pricing_in_progress';
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
                // Scope the requestId to THIS order's preprocess job so a stale/foreign
                // tracker Id from the client can't report an unrelated job's status. A
                // non-match yields no rows and falls through to the per-order fallback below.
                List<AsyncOperationTracker> trackers = [
                    SELECT Id, Status FROM AsyncOperationTracker
                    WHERE Id = :reqId AND ReferenceEntityId = :oid AND JobType = 'PreprocessOrder'
                    WITH USER_MODE
                    LIMIT 1
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
     * CalculationStatus. For a large deal the executor returns on ACCEPT — pricing
     * runs ASYNCHRONOUSLY (dispatch keyed on IsLargeDeal), so a true `isSuccess`
     * here does NOT mean pricing has committed. The caller must not enqueue
     * preprocess off this return: the LWC polls getPricingStatus() until
     * `ValidationResult == null` (pricing committed) first. This method only throws
     * on a synchronous accept failure. No-op for standard orders and unknown ids.
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

    /**
     * Cached lookup of the seed Exclude-from-Billing treatment. Name isn't a unique
     * key, so also require ExcludeFromBilling = 'Yes': we must never stamp a billable
     * same-named treatment onto large-deal order items (that would re-introduce the
     * billing-schedule rejection this seed exists to avoid).
     */
    @TestVisible
    private static Id resolveLargeDealExcludeTreatmentId() {
        if (!excludeTreatmentResolved) {
            excludeTreatmentResolved = true;
            List<BillingTreatment> bts = [
                SELECT Id FROM BillingTreatment
                WHERE Name = :LARGE_DEAL_EXCLUDE_TREATMENT
                  AND Status = 'Active'
                  AND ExcludeFromBilling = 'Yes'
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
