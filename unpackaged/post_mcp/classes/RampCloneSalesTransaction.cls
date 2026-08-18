/**
 * RampCloneSalesTransaction — @InvocableMethod wrapper over the clone Sales Transaction
 * Connect resource, so the clone/add-ramp-segment operation can be surfaced as a typed
 * tool on a custom MCP server through ApiSource=CLASSIC (invocable-action binding).
 *
 * WHY AN INVOCABLE AND NOT A CONNECT BINDING
 *   placeSalesTransaction carries @McpIntegration and can be bound declaratively as
 *   ApiSource=CONNECT. Clone does not, so the supported path for a custom server is an
 *   Apex invocable bound as ApiSource=CLASSIC at
 *   /actions/custom/apex/RampCloneSalesTransaction, which needs no @McpIntegration.
 *
 * WHY ConnectApi AND NOT A CALLOUT TO SELF
 *   The clone resource exposes an Apex surface, so no Named Credential is involved:
 *   ConnectApi.CloneSalesTransactionConnect.cloneSalesTransaction(
 *       CloneSalesTransactionInputRepresentation) -> CloneSalesTransactionOutputRepresentation
 *
 * SYNCHRONOUS ON THIS RELEASE — DO NOT ADD A TRACKER CONTRACT HERE
 *   Async clone is requested by passing a hydrated `contextId` whose sales-transaction
 *   header has IsLargeDeal=true, and is reported back as trackerId/trackerUrl. None of
 *   those three members exist on the 262 / v67.0 representations (verified by compile
 *   probe against a 262 org: `Variable does not exist` for input.contextId,
 *   options.contextId, and output.trackerId). So on this release the clone is always
 *   synchronous and there is nothing to poll. Tracker fields are deliberately absent
 *   from Result rather than present-and-always-null, because an always-null trackerId
 *   invites a caller — especially an LLM driving this as an MCP tool — to poll a handle
 *   that will never exist. The async-capable variant targets 264 / v68.0 and lives in
 *   the ramp-demo-kit repo; see .cursor/skills/mcp-integration/SKILL.md.
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

        // Optional target record type for the cloned segment.
        @InvocableVariable(label='Record Type Id')
        public String recordTypeId;
    }

    public class Result {
        @InvocableVariable(label='Success')
        public Boolean success;

        // Target header id. Populated on success.
        @InvocableVariable(label='Sales Transaction Id')
        public String salesTransactionId;

        @InvocableVariable(label='Request Id')
        public String requestId;

        // Populated on failure, or when Connect reports errors alongside a response.
        @InvocableVariable(label='Error Message')
        public String errorMessage;
    }

    @InvocableMethod(
        label='Clone Sales Transaction (Add Ramp Segment)'
        description='Clones a ramped sales-transaction group to add a ramp segment. Synchronous: the clone is complete when this returns.'
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
            r.errorMessage = 'salesTransactionId and at least one recordId are required.';
            return r;
        }
        try {
            ConnectApi.CloneSalesTransactionInputRepresentation input =
                new ConnectApi.CloneSalesTransactionInputRepresentation();
            input.salesTransactionId = req.salesTransactionId;
            input.recordIds = req.recordIds;

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
            r.requestId          = out.requestId;
            if (out.errors != null && !out.errors.isEmpty()) {
                r.errorMessage = serializeErrors(out.errors);
            }
        } catch (Exception e) {
            r.success = false;
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
