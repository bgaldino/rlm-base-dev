/**
 * RampCloneSalesTransaction — 264 / v68.0 variant. ASYNC-CAPABLE.
 *
 * ⚠ SECOND COPY BY DESIGN. The base bundle (unpackaged/post_mcp/) carries a
 * synchronous-only version of this same class compiled at 67.0, because the three
 * members this variant depends on do not exist on 262 / v67.0 — verified by compile
 * probe against a 262 org, which reports `Variable does not exist` for
 * input.contextId, options.contextId, and output.trackerId. ConnectApi input
 * representations also reject JSON.serialize/deserialize ("Only output types from
 * ConnectApi support serialization"), so there is no reflective way to set contextId
 * on a 67.0-compiled class and no single source file can serve both releases.
 *
 * This overlay deploys AFTER the base bundle and only on orgs at v68.0 or above; see
 * the deploy_post_mcp_264 task. On a 262 org it is skipped, leaving the sync class in
 * place. tests/test_mcp_overlay_parity.py pins the invariants that keep these two
 * copies from drifting apart in the wrong direction. When Foundations' baseline moves
 * to 264, collapse the two: promote this file into unpackaged/post_mcp/ and delete the
 * overlay, the task, and the parity test.
 *
 * WHY AN INVOCABLE AND NOT A CONNECT BINDING
 *   placeSalesTransaction carries @McpIntegration and can be bound declaratively as
 *   ApiSource=CONNECT. Clone does not, so the supported path for a custom server is an
 *   Apex invocable bound as ApiSource=CLASSIC at
 *   /actions/custom/apex/RampCloneSalesTransaction, which needs no @McpIntegration.
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
public with sharing class RampCloneSalesTransaction {

    public class Request {
        // The ramped QuoteLineGroup id(s) to clone. The Connect input accepts one.
        @InvocableVariable(required=true label='Record Ids')
        public List<String> recordIds;

        // Quote/Order header to clone from.
        @InvocableVariable(required=true label='Sales Transaction Id')
        public String salesTransactionId;

        // AllLines or RampedLinesOnly. Defaults to AllLines.
        @InvocableVariable(label='Line Scope')
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
        label='Clone Sales Transaction (Add Ramp Segment)'
        description='Clones a ramped sales-transaction group to add a ramp segment. Returns the async tracker handle when async clone is triggered; otherwise the clone is complete when this returns.'
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
        if (req == null || String.isBlank(req.salesTransactionId)
                || req.recordIds == null || req.recordIds.isEmpty()) {
            r.success = false;
            r.isAsync = false;
            r.errorMessage = 'salesTransactionId and at least one recordId are required.';
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
            options.lineScope = parseLineScope(req.lineScope);
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

    private static ConnectApi.LineScopeEnum parseLineScope(String value) {
        // Case-insensitive; anything unrecognised falls back to AllLines.
        if (String.isBlank(value)) {
            return ConnectApi.LineScopeEnum.AllLines;
        }
        if (value.trim().toLowerCase() == 'rampedlinesonly') {
            return ConnectApi.LineScopeEnum.RampedLinesOnly;
        }
        return ConnectApi.LineScopeEnum.AllLines;
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
