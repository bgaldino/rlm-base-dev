/**
 * Reusable Place Sales Transaction (PST) commit helper.
 *
 * PST (RevSalesTrxn.PlaceSalesTransactionExecutor.execute) is the supported Apex surface for
 * persisting Quote/Order graphs so bundles expand and the pricing procedure runs — a direct
 * QuoteLineItem insert does neither. The executor's 8-arg signature and the isSuccess /
 * errorResponse handling are boilerplate that was previously copy-pasted at each call site; this
 * class centralizes them so callers assemble a record graph and pick a commit "mode".
 *
 * Two ready modes cover the catalog's needs:
 *   - commitWithExpansion : pricing FORCE + configuration FORCE. Pass a single bundle root and PST
 *                           expands its components. Used by the plain "add products" path.
 *   - commitConfigured    : pricing FORCE + configuration SKIP. Pass an ALREADY-expanded/configured
 *                           tree (root + components + attributes + relationships) and PST persists
 *                           and prices it WITHOUT re-expanding — so user attribute/component choices
 *                           survive. Used by the configure-before-add path, which receives the fully
 *                           built tree from the Product Configurator's save event.
 *
 * Lower-level place(...) takes the two enums explicitly for any other combination.
 *
 * House conventions: WITH USER_MODE reads / `as user` DML happen inside PST itself; callers stay
 * free of SOQL/DML in loops.
 */
public with sharing class RLM_DeltaPlaceSalesTransaction {

    /** Outcome of a PST commit: success flag, a human-readable error, the ref→id map, and the raw response. */
    public class Result {
        public Boolean isSuccess;
        public String errorMessage;
        public Map<String, Object> referenceIds;
        public RevSalesTrxn.PlaceSalesTransactionResponse response;

        private Result(Boolean ok, String msg, Map<String, Object> refs, RevSalesTrxn.PlaceSalesTransactionResponse resp) {
            this.isSuccess = ok;
            this.errorMessage = msg;
            this.referenceIds = (refs != null) ? refs : new Map<String, Object>();
            this.response = resp;
        }
    }

    /** Pricing FORCE + configuration FORCE: pass a bundle root, let PST expand its components. */
    public static Result commitWithExpansion(String graphName, List<RevSalesTrxn.RecordWithReferenceRequest> records) {
        return place(graphName, records,
            RevSalesTrxn.PricingPreferenceEnum.FORCE,
            RevSalesTrxn.ConfigurationExecutionEnum.FORCE);
    }

    /**
     * Persist an ALREADY-expanded/configured tree exactly as the Product Configurator built it.
     *
     * Configuration is SKIPPED, not FORCED: the configurator already expanded the bundle (root +
     * components + relationships + attributes) and we POST every node ourselves. Running PST's
     * configuration step (config FORCE) on top of a complete tree RE-EXPANDS it — configuration
     * rules re-add required components (e.g. a bundle's included service line) on top of the ones
     * we submitted, producing DUPLICATE lines (live-confirmed: a second QB-SRV-OG-PSH appeared
     * carrying a raw `ref_<uuid>` price-waterfall id instead of one of our `refLine{n}` graph
     * tokens — i.e. minted by PST's own config pass, not our graph). SKIP persists the tree
     * verbatim. The caller therefore sets the date/term/billing fields explicitly per line
     * (END_DATE_MISSING / "BillingFrequency can't be null" otherwise — derivation only runs under
     * config FORCE, which we can't use here). Pricing FORCE still runs the pricing procedure so
     * totals recompute server-side.
     */
    public static Result commitConfigured(String graphName, List<RevSalesTrxn.RecordWithReferenceRequest> records) {
        return place(graphName, records,
            RevSalesTrxn.PricingPreferenceEnum.FORCE,
            RevSalesTrxn.ConfigurationExecutionEnum.SKIP);
    }

    /** Core commit with default (empty) configuration options. */
    public static Result place(
        String graphName,
        List<RevSalesTrxn.RecordWithReferenceRequest> records,
        RevSalesTrxn.PricingPreferenceEnum pricingPref,
        RevSalesTrxn.ConfigurationExecutionEnum configExec
    ) {
        return place(graphName, records, pricingPref, configExec, new RevSalesTrxn.ConfigurationOptionsInput());
    }

    /** Core commit: caller controls pricing, configuration execution, and the configuration options. */
    public static Result place(
        String graphName,
        List<RevSalesTrxn.RecordWithReferenceRequest> records,
        RevSalesTrxn.PricingPreferenceEnum pricingPref,
        RevSalesTrxn.ConfigurationExecutionEnum configExec,
        RevSalesTrxn.ConfigurationOptionsInput options
    ) {
        if (records == null || records.isEmpty()) {
            return new Result(false, 'No records to commit.', null, null);
        }
        RevSalesTrxn.GraphRequest graph = new RevSalesTrxn.GraphRequest(graphName, records);
        // Debug: log the field maps we submit per record (objects, field values, ref tokens) —
        // invaluable when a commit fails with a per-referenceId validation. We log the field maps
        // rather than JSON.serialize(graph): GraphRequest holds Schema.SObjectType, which is not
        // JSON-serializable ("Apex Type unsupported in JSON: Schema.SObjectType").
        System.debug(LoggingLevel.INFO, 'RLM_DeltaPlaceSalesTransaction graph [' + graphName + '] = ' + describeGraph(records));
        RevSalesTrxn.PlaceSalesTransactionResponse resp = RevSalesTrxn.PlaceSalesTransactionExecutor.execute(
            graph,
            pricingPref,
            configExec,
            (options != null) ? options : new RevSalesTrxn.ConfigurationOptionsInput(),
            null,
            (RevSalesTrxn.CatalogRatesPreferenceEnum) null,
            (RevSalesTrxn.TaxPreferenceEnum) null,
            null
        );
        // String.valueOf (not JSON.serialize) — the response may also carry non-serializable members.
        System.debug(LoggingLevel.INFO, 'RLM_DeltaPlaceSalesTransaction response [' + graphName + '] = ' + String.valueOf(resp));
        if (resp == null || !resp.isSuccess) {
            String msg = (resp != null && resp.errorResponse != null)
                ? String.valueOf(resp.errorResponse)
                : 'Place Sales Transaction failed.';
            return new Result(false, msg, referenceIdMap(resp), resp);
        }
        return new Result(true, null, referenceIdMap(resp), resp);
    }

    /**
     * JSON-safe rendering of the graph's records for debug logs. GraphRequest / RecordResource hold
     * Schema.SObjectType (not JSON-serializable), so we project each record to a plain map of its
     * referenceId, method, object name, and field values.
     */
    private static String describeGraph(List<RevSalesTrxn.RecordWithReferenceRequest> records) {
        List<Object> rows = new List<Object>();
        for (RevSalesTrxn.RecordWithReferenceRequest r : records) {
            RevSalesTrxn.RecordResource rec = (r != null) ? r.record : null;
            rows.add(new Map<String, Object>{
                'referenceId' => (r != null) ? r.referenceId : null,
                'method' => (rec != null) ? rec.method : null,
                'id' => (rec != null) ? rec.id : null,
                'object' => (rec != null && rec.type != null) ? String.valueOf(rec.type) : null,
                'fieldValues' => (rec != null) ? rec.fieldValues : null
            });
        }
        return JSON.serialize(rows);
    }

    // ---------- graph-assembly conveniences ----------

    /** A new POST record of the given type with the supplied field values. */
    public static RevSalesTrxn.RecordWithReferenceRequest post(String refName, Schema.SObjectType type, Map<String, Object> fieldValues) {
        RevSalesTrxn.RecordResource rec = new RevSalesTrxn.RecordResource(type, 'POST');
        rec.fieldValues = (fieldValues != null) ? fieldValues : new Map<String, Object>();
        return new RevSalesTrxn.RecordWithReferenceRequest(refName, rec);
    }

    /** A PATCH record (update-in-place) of the given type / id with the supplied field values. */
    public static RevSalesTrxn.RecordWithReferenceRequest patch(String refName, Schema.SObjectType type, Id recordId, Map<String, Object> fieldValues) {
        RevSalesTrxn.RecordResource rec = new RevSalesTrxn.RecordResource(type, 'PATCH', recordId);
        rec.fieldValues = (fieldValues != null) ? fieldValues : new Map<String, Object>();
        return new RevSalesTrxn.RecordWithReferenceRequest(refName, rec);
    }

    /**
     * A DELETE record (remove-in-place) of the given type / id. PST supports a 'DELETE' verb on
     * RecordResource alongside POST/PATCH (official PST help: create, update, AND delete), so a
     * delete can ride in the SAME graph as the PATCH/POST records — one atomic transaction, one
     * pricing pass over the final state. Used by the reconfigure path to drop bundle components the
     * user removed in the configurator (whose Save & Exit returns the surviving tree, not delete
     * markers). Order DELETE nodes dependency-safe child → parent within the graph; the platform may
     * also cascade-remove a deleted line's attributes/relationships (confirm live before relying on
     * it — see the reconfigure commit's Spike B' note).
     */
    public static RevSalesTrxn.RecordWithReferenceRequest del(String refName, Schema.SObjectType type, Id recordId) {
        return new RevSalesTrxn.RecordWithReferenceRequest(refName, new RevSalesTrxn.RecordResource(type, 'DELETE', recordId));
    }

    /** A graph reference token (@{ref.id}) resolving to a record created earlier in the same graph. */
    public static String referenceToken(String refName) {
        return '@{' + refName + '.id}';
    }

    /**
     * Clear Quote.ValidationResult after a DIRECT-DML mutation (a discount/date/fare/name edit or a
     * line delete saved with `update`/`delete as user` rather than through PST).
     *
     * WHY THIS EXISTS. Direct DML persists "outside the standard pricing flow," so the platform stamps
     * ValidationResult = TransactionIncomplete (the UI's "Transaction Incomplete" badge) and leaves
     * prices stale — the pricing procedure never ran. A PST pricing pass is what clears the flag and
     * recomputes totals. We deliberately keep the direct DML for the field writes and only reprice
     * here, because PST's PATCH verb is a PRICING operation, NOT a general field-writer: live-verified
     * 2026-07-20 on Delta, a PST PATCH applies pricing-relevant fields (Discount) but SILENTLY DROPS
     * non-pricing custom fields (DL_FareCodes__c, and CustomProductName by the same rule). Routing the
     * whole edit through PST would therefore lose fare codes and term names. A header-only reprice, by
     * contrast, recomputes pricing over the already-persisted line state and leaves those custom fields
     * untouched (same-transaction test: direct DML wrote disc/fare/name → VR=TransactionIncomplete;
     * this reprice → VR=null with fare codes and name intact).
     *
     * The graph is a single header PATCH with no field values: PST requires a Quote in the record list
     * ("No quote found in the record list." otherwise), and pricing FORCE reads every persisted line,
     * so nothing else needs to be re-sent — no lines are re-expanded or duplicated (configuration SKIP).
     *
     * BEST-EFFORT. Callers invoke this AFTER their DML has committed and ignore the Result: a reprice
     * failure must not fail (or roll back) the mutation that already succeeded. commitConfigured
     * returns a non-success Result rather than throwing on a PST-level error, and this method wraps the
     * call in try/catch as a backstop so an unexpected executor exception can't roll back the caller's
     * committed work — the lines stay saved; only the staleness flag would remain set.
     */
    public static Result revalidate(Id quoteId) {
        if (quoteId == null) {
            return new Result(false, 'No quote to revalidate.', null, null);
        }
        try {
            return commitConfigured('DeltaRevalidate', new List<RevSalesTrxn.RecordWithReferenceRequest>{
                patch('refRevalidateHeader', Quote.getSObjectType(), quoteId, new Map<String, Object>())
            });
        } catch (Exception e) {
            System.debug(LoggingLevel.WARN,
                'RLM_DeltaPlaceSalesTransaction.revalidate failed (mutation already committed): ' + e.getMessage());
            return new Result(false, e.getMessage(), null, null);
        }
    }

    /** Best-effort extraction of the ref→id map from the PST response without binding to an exact shape. */
    public static Map<String, Object> referenceIdMap(RevSalesTrxn.PlaceSalesTransactionResponse resp) {
        Map<String, Object> out = new Map<String, Object>();
        if (resp == null) {
            return out;
        }
        try {
            Map<String, Object> asMap = (Map<String, Object>) JSON.deserializeUntyped(JSON.serialize(resp));
            Object refs = (asMap.get('referenceId') != null) ? asMap.get('referenceId') : asMap.get('references');
            if (refs instanceof Map<String, Object>) {
                out.putAll((Map<String, Object>) refs);
            }
        } catch (Exception e) {
            // Reference resolution is best-effort; absence is non-fatal.
        }
        return out;
    }
}
