/**
 * RLM_CloneSalesTransaction — ASYNC-CAPABLE (v68.0).
 *
 * ASYNC-CAPABLE (264 / v68.0 baseline). The async members (input.contextId,
 * options.contextId, output.trackerId) exist only from v68.0 / 264 on. Foundations is
 * owned for this class: edits belong here. A user calling this
 * through the CLASSIC action endpoint also needs class access; the RLM_McpSalesTransactions
 * permission set grants it.
 *
 * WHY AN INVOCABLE AND NOT A CONNECT BINDING
 *   placeSalesTransaction carries @McpIntegration and can be bound declaratively as
 *   ApiSource=CONNECT. Clone does not, so the supported path for a custom server is an
 *   Apex invocable bound as ApiSource=CLASSIC at
 *   /actions/custom/apex/RLM_CloneSalesTransaction, which needs no @McpIntegration.
 *
 * ASYNC CONTRACT
 *   Async clone is a server-side behavior triggered by passing a hydrated `contextId`
 *   whose sales-transaction header has IsLargeDeal=true, with the org's two large-deal
 *   gates open. It returns trackerId/trackerUrl IMMEDIATELY, before the work runs, so
 *   this wrapper is deliberately non-blocking: it fires the clone and hands back the
 *   tracker handle for the caller to poll on AsyncOperationTracker. When the async
 *   conditions are not met the platform quietly runs synchronously instead — trackerId
 *   and trackerUrl come back null and salesTransactionId is populated. Both cases are
 *   reported faithfully, and isAsync tells the caller which one it got.
 */
public with sharing class RLM_CloneSalesTransaction {

    public class Request {
        // The record to clone: a Quote, Order, QuoteLineItem, OrderItem, QuoteLineGroup or
        // OrderItemGroup id (a group clones all its items). A list because the Connect input
        // is String[], but it accepts exactly one; more is rejected here, not inside Connect.
        @InvocableVariable(required=true label='Record Ids'
            description='Exactly one id to clone: a Quote, Order, QuoteLineItem, OrderItem, QuoteLineGroup or OrderItemGroup.')
        public List<String> recordIds;

        // Quote/Order header to clone from.
        @InvocableVariable(required=true label='Sales Transaction Id')
        public String salesTransactionId;

        // AllLines or RampedLinesOnly (case-insensitive). Blank defaults to AllLines; any
        // other value is rejected, so a typo cannot silently widen the clone.
        @InvocableVariable(label='Line Scope'
            description='AllLines (default when blank) or RampedLinesOnly; any other value is rejected.')
        public String lineScope;

        // Hydrated sales-transaction context id. Supplying this, with IsLargeDeal=true
        // and the org gates open, is what triggers the async clone.
        @InvocableVariable(label='Context Id')
        public String contextId;

        // Optional target record type for the cloned segment.
        @InvocableVariable(label='Record Type Id')
        public String recordTypeId;
    }

    public class Result {
        @InvocableVariable(label='Success')
        public Boolean success;

        // Target header id. Populated when the clone ran synchronously.
        @InvocableVariable(label='Sales Transaction Id')
        public String salesTransactionId;

        // Non-null means async: poll AsyncOperationTracker on this id.
        @InvocableVariable(label='Tracker Id')
        public String trackerId;

        @InvocableVariable(label='Tracker Url')
        public String trackerUrl;

        @InvocableVariable(label='Request Id')
        public String requestId;

        // Derived from trackerId, so a caller does not have to infer the mode.
        @InvocableVariable(label='Is Async')
        public Boolean isAsync;

        // Populated on failure, or when Connect reports errors alongside a response.
        @InvocableVariable(label='Error Message')
        public String errorMessage;
    }

    @InvocableMethod(
        label='Clone Sales Transaction'
        description='Clones a quote or order, or one of its line items or groups (recordIds takes exactly one Quote, Order, QuoteLineItem, OrderItem, QuoteLineGroup or OrderItemGroup id; lineScope is AllLines or RampedLinesOnly). Returns the async tracker handle when async clone is triggered; otherwise the clone is complete when this returns.'
        category='Revenue Cloud'
    )
    public static List<Result> cloneSegments(List<Request> requests) {
        List<Result> results = new List<Result>();
        if (requests == null) {
            return results;
        }
        for (Request req : requests) {
            results.add(cloneOne(req));
        }
        return results;
    }

    private static Result cloneOne(Request req) {
        Result r = new Result();
        r.success = false;
        r.isAsync = false;
        if (req == null || String.isBlank(req.salesTransactionId)
                || req.recordIds == null || req.recordIds.size() != 1
                || String.isBlank(req.recordIds[0])) {
            r.errorMessage = 'salesTransactionId and exactly one recordId are required.';
            return r;
        }
        ConnectApi.LineScopeEnum lineScope = parseLineScope(req.lineScope);
        if (lineScope == null) {
            r.errorMessage = 'lineScope must be AllLines or RampedLinesOnly (or blank for AllLines); got "'
                + req.lineScope + '".';
            return r;
        }
        try {
            ConnectApi.CloneSalesTransactionInputRepresentation input =
                new ConnectApi.CloneSalesTransactionInputRepresentation();
            input.salesTransactionId = req.salesTransactionId;
            input.recordIds = req.recordIds;
            if (String.isNotBlank(req.contextId)) {
                input.contextId = req.contextId;
            }

            ConnectApi.CloneOptionsInputRepresentation options =
                new ConnectApi.CloneOptionsInputRepresentation();
            options.lineScope = lineScope;
            if (String.isNotBlank(req.recordTypeId)) {
                options.recordTypeId = req.recordTypeId;
            }
            input.options = options;

            ConnectApi.CloneSalesTransactionOutputRepresentation out =
                ConnectApi.CloneSalesTransactionConnect.cloneSalesTransaction(input);

            r.success            = out.success;
            r.salesTransactionId = out.salesTransactionId;
            r.trackerId          = out.trackerId;
            r.trackerUrl         = out.trackerUrl;
            r.requestId          = out.requestId;
            r.isAsync            = out.trackerId != null;
            if (out.errors != null && !out.errors.isEmpty()) {
                r.errorMessage = serializeErrors(out.errors);
            }
        } catch (Exception e) {
            r.success = false;
            r.isAsync = false;
            r.errorMessage = e.getTypeName() + ': ' + e.getMessage();
        }
        return r;
    }

    @TestVisible
    private static ConnectApi.LineScopeEnum parseLineScope(String value) {
        // Case-insensitive; blank means AllLines; anything unrecognised is null (rejected).
        if (String.isBlank(value)) {
            return ConnectApi.LineScopeEnum.AllLines;
        }
        String scope = value.trim().toLowerCase();
        if (scope == 'alllines') {
            return ConnectApi.LineScopeEnum.AllLines;
        }
        if (scope == 'rampedlinesonly') {
            return ConnectApi.LineScopeEnum.RampedLinesOnly;
        }
        return null;
    }

    private static String serializeErrors(
        List<ConnectApi.CloneSalesTransactionErrorResponseRepresentation> errors
    ) {
        List<String> messages = new List<String>();
        for (ConnectApi.CloneSalesTransactionErrorResponseRepresentation e : errors) {
            messages.add(String.valueOf(e));
        }
        return String.join(messages, ' | ');
    }
}
