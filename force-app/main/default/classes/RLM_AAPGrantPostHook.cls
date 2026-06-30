/**
 * Sales Transaction (Pricing) procedure-plan posthook that copies QuantumBit
 * "AAP" product-family included-quantity SalesTransactionItemAttribute values
 * onto the matching SalesTrxnItemUseRsrcGrant__std.GrantQuantity__std fields.
 *
 * Wiring (manual, in Setup -> Procedure Plan Definitions): add an Apex section
 * after the Pricing section that points to RLM_AAPGrantPostHook. The Apex
 * section must be the last element in the procedure plan for the Agentforce
 * Revenue Management process type (see Help: Customize Your Procedure Plans
 * With Apex Hooks).
 *
 * Filter:
 *   - Only SalesTransactionItem nodes where ItemProductFamily__c == 'AAP'.
 * Attribute -> resource map:
 *   - IncludedTrafficText       -> UsageResource.Name 'AAP Traffic'
 *   - IncludedBandwidthText     -> UsageResource.Name 'AAP Bandwidth'
 *   - IncludedMillionHitsGBText -> UsageResource.Name 'AAP Requests'
 * Writes:
 *   - SalesTrxnItemUseRsrcGrant__std.GrantQuantity__std (Integer)
 */
global with sharing class RLM_AAPGrantPostHook implements RevSignaling.SignalingApexProcessor {

    public virtual class BaseException extends Exception {}
    public class HookException extends BaseException {}

    // All context tag / attribute names are kept as constants because queryTags
    // returns nested String-keyed Maps; a typo here silently yields null instead
    // of a compile error. The trailing `__std` suffix on context-tag names is
    // the RLM context-definition naming convention (NOT a Salesforce custom
    // field suffix — the backing SObjects are standard, e.g. UsageResource).
    private static final String AAP_PRODUCT_FAMILY = 'AAP';
    private static final String ITEM_FAMILY_ATTR = 'ItemProductFamily__c';
    private static final String GRANT_QUANTITY_ATTR = 'GrantQuantity__std';

    private static final String TAG_STI = 'SalesTransactionItem';
    private static final String TAG_STIA = 'SalesTransactionItemAttribute';
    private static final String TAG_GRANT = 'SalesTrxnItemUseRsrcGrant__std';

    private static final String ATTR_NAME = 'AttributeName';
    private static final String ATTR_VALUE = 'AttributeValue';
    private static final String ATTR_STIA_PARENT = 'SalesTransactionItemAttrParent';
    private static final String ATTR_GRANT_PARENT = 'SalesTransactionItem__std';
    private static final String ATTR_GRANT_RESOURCE = 'UsageResource__std';

    private static final Map<String, String> ATTR_NAME_TO_RESOURCE_NAME = new Map<String, String>{
        'IncludedTrafficText'       => 'AAP Traffic',
        'IncludedBandwidthText'     => 'AAP Bandwidth',
        'IncludedMillionHitsGBText' => 'AAP Requests'
    };

    // Prefix every System.debug line so they're trivially grep-able in the
    // raw debug log. DEBUG_VERSION is bumped when behavior changes so an
    // operator can confirm which build is actually running in the org
    // (Apex caches compiled classes; a stale post-deploy can otherwise hide).
    private static final String DEBUG_PREFIX = 'RLM_AAPGrantPostHook';
    private static final String DEBUG_VERSION = 'V1.0';

    // Recursion guard. updateContextAttributes() can re-trigger a pricing pass,
    // which would re-fire this posthook -> infinite loop (and CPU governor
    // exhaustion). Pattern lifted from the External Pricing posthook sample in
    // ind.product_catalog_sample_apex_class_for_product_discovery_external_pricing.htm.
    // @TestVisible so the test class can prove the short-circuit branch.
    @TestVisible
    private static Boolean isRunning = false;

    // Indirection through the ContextClient interface (see bottom of file) is
    // the only way to test this hook without a live pricing context:
    // Context.IndustriesContext is not stubbable directly. The pricing engine
    // always invokes the no-arg constructor; the @TestVisible constructor is
    // used by RLM_AAPGrantPostHookTest to inject a MockContextClient.
    @TestVisible
    private ContextClient industriesContext;

    public RLM_AAPGrantPostHook() {
        this.industriesContext = new RealContextClient();
    }

    @TestVisible
    private RLM_AAPGrantPostHook(ContextClient client) {
        this.industriesContext = client;
    }

    global RevSignaling.TransactionResponse execute(RevSignaling.TransactionRequest request) {
        RevSignaling.TransactionResponse response = new RevSignaling.TransactionResponse();
        logInfo('=== execute() ENTER version=' + DEBUG_VERSION + ' ===');

        if (isRunning) {
            logInfo('execute() SKIP: recursion guard latched (isRunning=true); returning SUCCESS no-op');
            response.status = RevSignaling.TransactionStatus.SUCCESS;
            response.message = 'Skipped recursive execution.';
            return response;
        }

        // Returning SUCCESS on blank ctxId is intentional: the pricing engine
        // wraps every transaction in this posthook, and a FAILED response would
        // mark the transaction as errored. A missing context id means "nothing
        // priced here", not "pricing should fail".
        String contextId = request != null ? request.ctxInstanceId : null;
        logInfo('execute() contextId=' + contextId);
        if (String.isBlank(contextId)) {
            logInfo('execute() SKIP: blank contextId; returning SUCCESS no-op');
            response.status = RevSignaling.TransactionStatus.SUCCESS;
            response.message = 'No context id supplied; nothing to do.';
            return response;
        }

        try {
            isRunning = true;
            logFine('execute() recursion guard SET (isRunning=true)');

            // Same SUCCESS-on-empty rationale for the three early-out branches
            // below: a Sales Transaction with zero AAP-family lines (or AAP
            // lines without the three included-* attributes) is a normal,
            // non-error case. We only want to fail the procedure plan if an
            // unexpected exception escapes.
            Set<String> aapItemCtxIds = queryAapItemCtxIds(contextId);
            logInfo('execute() step 1/4 AAP items found=' + aapItemCtxIds.size()
                + ' ctxIds=' + aapItemCtxIds);
            if (aapItemCtxIds.isEmpty()) {
                logInfo('execute() SKIP: no AAP items; returning SUCCESS no-op');
                response.status = RevSignaling.TransactionStatus.SUCCESS;
                response.message = 'No AAP product-family items in context; nothing to do.';
                return response;
            }

            Map<String, Map<String, Integer>> qtyByItemByResource =
                queryQuantitiesByItem(contextId, aapItemCtxIds);
            logInfo('execute() step 2/4 items with queued quantities=' + qtyByItemByResource.size());
            logFine('execute() step 2/4 qtyByItemByResource=' + qtyByItemByResource);
            if (qtyByItemByResource.isEmpty()) {
                logInfo('execute() SKIP: no matching SalesTransactionItemAttribute rows; returning SUCCESS no-op');
                response.status = RevSignaling.TransactionStatus.SUCCESS;
                response.message = 'No matching SalesTransactionItemAttribute rows for AAP items; nothing to do.';
                return response;
            }

            Map<Id, String> resourceNameById = loadResourceNameById();
            logInfo('execute() step 3/4 UsageResource records resolved=' + resourceNameById.size());

            List<Object> nodeUpdates =
                buildGrantUpdates(contextId, aapItemCtxIds, qtyByItemByResource, resourceNameById);
            logInfo('execute() step 4/4 grant updates built=' + nodeUpdates.size());

            // Batched in a single updateContextAttributes call so the engine
            // sees ONE atomic update event per posthook run, not N events
            // (which would trip the recursion guard once and stop the rest).
            if (!nodeUpdates.isEmpty()) {
                Map<String, Object> updateInput = new Map<String, Object>{
                    'contextId' => contextId,
                    'nodePathAndAttributes' => nodeUpdates
                };
                logFine('execute() submitting updateContextAttributes input=' + JSON.serializePretty(updateInput));
                industriesContext.updateContextAttributes(updateInput);
                logInfo('execute() updateContextAttributes returned OK (' + nodeUpdates.size() + ' updates submitted)');
            } else {
                logInfo('execute() no updates to submit; skipping updateContextAttributes call');
            }

            response.status = RevSignaling.TransactionStatus.SUCCESS;
            response.message = 'AAP grant quantities updated: ' + nodeUpdates.size();
            logInfo('=== execute() EXIT status=SUCCESS updatesSubmitted=' + nodeUpdates.size() + ' ===');
            return response;
        } catch (Exception e) {
            logError('execute() FAILED: ' + e.getMessage() + ' stack=' + e.getStackTraceString());
            response.status = RevSignaling.TransactionStatus.FAILED;
            response.message = DEBUG_PREFIX + ' error: ' + e.getMessage();
            logInfo('=== execute() EXIT status=FAILED ===');
            return response;
        } finally {
            // MUST reset in finally, not at the bottom of try: an uncaught
            // exception (or a return-from-try above) would otherwise leave the
            // guard latched true for the rest of the request, silently
            // disabling the posthook for every subsequent transaction in the
            // same execution context.
            isRunning = false;
            logFine('execute() recursion guard CLEARED (isRunning=false)');
        }
    }

    /**
     * The returned ids are CONTEXT ids (the runtime identifiers the engine
     * assigns to each node), NOT Salesforce record ids. They are the cross-
     * node join key used by both `SalesTransactionItemAttribute.SalesTransactionItemAttrParent`
     * and `SalesTrxnItemUseRsrcGrant__std.SalesTransactionItem__std` to point
     * back at their owning item -- so this set is what later queries match
     * against. equalsIgnoreCase is defensive: the picklist persists 'AAP' but
     * we don't want a casing drift to silently disable the hook.
     */
    private Set<String> queryAapItemCtxIds(String contextId) {
        logFine('queryAapItemCtxIds() ENTER contextId=' + contextId);
        Map<String, Object> input = new Map<String, Object>{
            'contextId' => contextId,
            'tags' => new List<String>{ TAG_STI }
        };
        Map<String, Object> output = industriesContext.queryTags(input);
        List<Object> items = readNodes(output, TAG_STI);
        logInfo('queryAapItemCtxIds() queryTags returned ' + items.size() + ' ' + TAG_STI + ' node(s)');

        Set<String> ctxIds = new Set<String>();
        Integer skippedNoTagMap = 0;
        Integer skippedNonAap = 0;
        Integer skippedBlankCtxId = 0;
        for (Object itemObj : items) {
            Map<String, Object> node = (Map<String, Object>) itemObj;
            Map<String, Object> tagMap = (Map<String, Object>) node.get('tagValue');
            if (tagMap == null) {
                skippedNoTagMap++;
                continue;
            }
            String family = readTagString(tagMap, ITEM_FAMILY_ATTR);
            if (!AAP_PRODUCT_FAMILY.equalsIgnoreCase(family)) {
                skippedNonAap++;
                logFine('queryAapItemCtxIds() skip non-AAP item: family=' + family);
                continue;
            }
            // The item's own ctx id is always the leaf of its dataPath;
            // the engine guarantees the path is rooted at the context id
            // and ends at the node being described.
            String itemCtxId = lastDataPathSegment(node);
            if (String.isBlank(itemCtxId)) {
                skippedBlankCtxId++;
                continue;
            }
            ctxIds.add(itemCtxId);
            logFine('queryAapItemCtxIds() matched AAP item ctxId=' + itemCtxId);
        }
        logInfo('queryAapItemCtxIds() EXIT matched=' + ctxIds.size()
            + ' skipped_no_tagMap=' + skippedNoTagMap
            + ' skipped_non_aap=' + skippedNonAap
            + ' skipped_blank_ctxid=' + skippedBlankCtxId);
        return ctxIds;
    }

    /**
     * Returns: itemCtxId -> ( UsageResource.Name -> requested integer quantity ).
     * We can't filter the queryTags call by parent, so we get all attributes
     * across the transaction and filter in-memory. The parent-set check is
     * therefore essential: a stray IncludedTrafficText attribute on a non-AAP
     * line must NOT be allowed to overwrite any grant.
     */
    private Map<String, Map<String, Integer>> queryQuantitiesByItem(
        String contextId,
        Set<String> aapItemCtxIds
    ) {
        logFine('queryQuantitiesByItem() ENTER contextId=' + contextId
            + ' aapItemCtxIds=' + aapItemCtxIds);
        Map<String, Object> input = new Map<String, Object>{
            'contextId' => contextId,
            'tags' => new List<String>{ TAG_STIA }
        };
        Map<String, Object> output = industriesContext.queryTags(input);
        List<Object> attrs = readNodes(output, TAG_STIA);
        logInfo('queryQuantitiesByItem() queryTags returned ' + attrs.size() + ' ' + TAG_STIA + ' node(s)');

        Map<String, Map<String, Integer>> byItem = new Map<String, Map<String, Integer>>();
        Integer skippedNoTagMap = 0;
        Integer skippedNonAapParent = 0;
        Integer skippedUnmappedAttrName = 0;
        Integer skippedBlankValue = 0;
        Integer skippedNonInteger = 0;
        Integer captured = 0;
        for (Object attrObj : attrs) {
            Map<String, Object> node = (Map<String, Object>) attrObj;
            Map<String, Object> tagMap = (Map<String, Object>) node.get('tagValue');
            if (tagMap == null) {
                skippedNoTagMap++;
                continue;
            }
            String parentItemCtxId = readTagString(tagMap, ATTR_STIA_PARENT);
            if (String.isBlank(parentItemCtxId) || !aapItemCtxIds.contains(parentItemCtxId)) {
                skippedNonAapParent++;
                continue;
            }
            String attrName = readTagString(tagMap, ATTR_NAME);
            String resourceName = ATTR_NAME_TO_RESOURCE_NAME.get(attrName);
            if (resourceName == null) {
                skippedUnmappedAttrName++;
                logFine('queryQuantitiesByItem() skip unmapped attrName=' + attrName
                    + ' on item ' + parentItemCtxId);
                continue;
            }
            String rawValue = readTagString(tagMap, ATTR_VALUE);
            if (String.isBlank(rawValue)) {
                skippedBlankValue++;
                logFine('queryQuantitiesByItem() skip blank AttributeValue for '
                    + attrName + ' on item ' + parentItemCtxId);
                continue;
            }
            // Per-row try/catch (rather than failing the whole posthook) so
            // one malformed attribute on one line doesn't take down pricing
            // for every other line in the transaction.
            Integer qty;
            try {
                qty = Integer.valueOf(rawValue.trim());
            } catch (Exception parseEx) {
                skippedNonInteger++;
                logWarn('queryQuantitiesByItem() non-integer AttributeValue "' + rawValue
                    + '" for ' + attrName + ' on item ' + parentItemCtxId
                    + '; skipping (' + parseEx.getMessage() + ')');
                continue;
            }
            Map<String, Integer> byResource = byItem.get(parentItemCtxId);
            if (byResource == null) {
                byResource = new Map<String, Integer>();
                byItem.put(parentItemCtxId, byResource);
            }
            byResource.put(resourceName, qty);
            captured++;
            logFine('queryQuantitiesByItem() captured item=' + parentItemCtxId
                + ' resource=' + resourceName + ' qty=' + qty);
        }
        logInfo('queryQuantitiesByItem() EXIT items_with_qty=' + byItem.size()
            + ' captured_attrs=' + captured
            + ' skipped_no_tagMap=' + skippedNoTagMap
            + ' skipped_non_aap_parent=' + skippedNonAapParent
            + ' skipped_unmapped_attr=' + skippedUnmappedAttrName
            + ' skipped_blank_value=' + skippedBlankValue
            + ' skipped_non_integer=' + skippedNonInteger);
        return byItem;
    }

    /**
     * Round-trip through the SObject because the SalesTransaction context
     * exposes `UsageResource__std` ONLY as an id reference on each grant --
     * there is no sibling UsageResource node with a queryable Name attribute.
     * Scoped to just our three resource names so this is one indexed query
     * (Name is idLookup) regardless of how many UsageResource records exist
     * in the org. WITH USER_MODE per the apex-security-hardening skill; the
     * matching `allowRead=true` on UsageResource lives in RLM_QuantumBit.permissionset.
     */
    private Map<Id, String> loadResourceNameById() {
        Set<String> wantedNames = new Set<String>(ATTR_NAME_TO_RESOURCE_NAME.values());
        logFine('loadResourceNameById() ENTER wantedNames=' + wantedNames);
        Map<Id, String> nameById = new Map<Id, String>();
        for (UsageResource ur : [
            SELECT Id, Name
            FROM UsageResource
            WHERE Name IN :wantedNames
            WITH USER_MODE
        ]) {
            nameById.put(ur.Id, ur.Name);
            logFine('loadResourceNameById() resolved Name=' + ur.Name + ' Id=' + ur.Id);
        }
        // A missing UsageResource isn't fatal (buildGrantUpdates simply skips
        // the affected grants) but it's almost always a deployment/data bug,
        // so surface it loudly so it's easy to spot in the debug log.
        Set<String> foundNames = new Set<String>(nameById.values());
        Set<String> missingNames = new Set<String>(wantedNames);
        missingNames.removeAll(foundNames);
        if (!missingNames.isEmpty()) {
            logWarn('loadResourceNameById() missing UsageResource records by Name: '
                + missingNames + ' (grants pointing at these will not be updated)');
        }
        logInfo('loadResourceNameById() EXIT resolved=' + nameById.size()
            + '/' + wantedNames.size());
        return nameById;
    }

    /**
     * Return type is List<Object> (not List<Map<String, Object>>) because
     * Apex's generics are invariant: putting the result into the
     * `nodePathAndAttributes` slot of a Map<String, Object> and reading it
     * back as List<Object> elsewhere (notably the mock in the test class)
     * would throw "Illegal assignment" otherwise. The elements are still
     * Map<String, Object> at runtime; the engine reads them positionally.
     *
     * Grants are matched to their parent line via the SalesTransactionItem__std
     * tag rather than by parsing dataPath positions -- the tag is the contract
     * the engine guarantees; dataPath depth/layout is not.
     */
    private List<Object> buildGrantUpdates(
        String contextId,
        Set<String> aapItemCtxIds,
        Map<String, Map<String, Integer>> qtyByItemByResource,
        Map<Id, String> resourceNameById
    ) {
        logFine('buildGrantUpdates() ENTER aapItems=' + aapItemCtxIds.size()
            + ' itemsWithQty=' + qtyByItemByResource.size()
            + ' knownResources=' + resourceNameById.size());
        List<Object> updates = new List<Object>();

        Map<String, Object> input = new Map<String, Object>{
            'contextId' => contextId,
            'tags' => new List<String>{ TAG_GRANT }
        };
        Map<String, Object> output = industriesContext.queryTags(input);
        List<Object> grants = readNodes(output, TAG_GRANT);
        logInfo('buildGrantUpdates() queryTags returned ' + grants.size() + ' ' + TAG_GRANT + ' node(s)');

        Integer skippedNoTagMap = 0;
        Integer skippedNonAapParent = 0;
        Integer skippedNoQueuedQty = 0;
        Integer skippedBlankResourceId = 0;
        Integer skippedInvalidResourceId = 0;
        Integer skippedUnknownResource = 0;
        Integer skippedNoQty = 0;
        Integer skippedBadPath = 0;
        for (Object grantObj : grants) {
            Map<String, Object> node = (Map<String, Object>) grantObj;
            Map<String, Object> tagMap = (Map<String, Object>) node.get('tagValue');
            if (tagMap == null) {
                skippedNoTagMap++;
                continue;
            }
            String parentItemCtxId = readTagString(tagMap, ATTR_GRANT_PARENT);
            if (String.isBlank(parentItemCtxId) || !aapItemCtxIds.contains(parentItemCtxId)) {
                skippedNonAapParent++;
                continue;
            }
            Map<String, Integer> queuedQtyByResource = qtyByItemByResource.get(parentItemCtxId);
            if (queuedQtyByResource == null || queuedQtyByResource.isEmpty()) {
                skippedNoQueuedQty++;
                continue;
            }
            String resourceIdString = readTagString(tagMap, ATTR_GRANT_RESOURCE);
            if (String.isBlank(resourceIdString)) {
                skippedBlankResourceId++;
                continue;
            }
            // Id.valueOf inside try/catch per the apex-classes rule: untrusted
            // string -> Id conversion must never throw out of the loop and
            // abort processing of the remaining grants.
            Id resourceId;
            try {
                resourceId = Id.valueOf(resourceIdString);
            } catch (Exception idEx) {
                skippedInvalidResourceId++;
                logWarn('buildGrantUpdates() invalid UsageResource Id "'
                    + resourceIdString + '" on item ' + parentItemCtxId
                    + '; skipping (' + idEx.getMessage() + ')');
                continue;
            }
            // resourceName == null means the grant's resource isn't one of
            // the three AAP resources (or wasn't returned by the SOQL because
            // it doesn't exist in the org). Either way: leave the grant alone.
            String resourceName = resourceNameById.get(resourceId);
            if (resourceName == null) {
                skippedUnknownResource++;
                logFine('buildGrantUpdates() skip grant on item=' + parentItemCtxId
                    + ' resourceId=' + resourceId + ' (not in our AAP resource set)');
                continue;
            }
            Integer qty = queuedQtyByResource.get(resourceName);
            if (qty == null) {
                skippedNoQty++;
                logFine('buildGrantUpdates() skip grant on item=' + parentItemCtxId
                    + ' resource=' + resourceName + ' (no queued attribute value)');
                continue;
            }

            List<Object> grantPath = cloneDataPathWithoutContextId(node);
            if (grantPath == null || grantPath.isEmpty()) {
                skippedBadPath++;
                logWarn('buildGrantUpdates() grant on item=' + parentItemCtxId
                    + ' has empty/null dataPath; skipping');
                continue;
            }

            // Payload shape lifted from the prehook/posthook samples in
            // ind.pricing_customize_pricing_procedures_with_apex_hooks.htm.
            // Keys are case-sensitive and required by the engine; do not
            // rename without changing the engine contract.
            updates.add(new Map<String, Object>{
                'nodePath' => new Map<String, Object>{ 'dataPath' => grantPath },
                'attributes' => new List<Object>{
                    new Map<String, Object>{
                        'attributeName' => GRANT_QUANTITY_ATTR,
                        'attributeValue' => qty
                    }
                }
            });
            logInfo('buildGrantUpdates() queued update item=' + parentItemCtxId
                + ' resource=' + resourceName + ' ' + GRANT_QUANTITY_ATTR + '=' + qty
                + ' grantPath=' + grantPath);
        }
        logInfo('buildGrantUpdates() EXIT updates=' + updates.size()
            + ' skipped_no_tagMap=' + skippedNoTagMap
            + ' skipped_non_aap_parent=' + skippedNonAapParent
            + ' skipped_no_queued_qty=' + skippedNoQueuedQty
            + ' skipped_blank_resource_id=' + skippedBlankResourceId
            + ' skipped_invalid_resource_id=' + skippedInvalidResourceId
            + ' skipped_unknown_resource=' + skippedUnknownResource
            + ' skipped_no_qty=' + skippedNoQty
            + ' skipped_bad_path=' + skippedBadPath);
        return updates;
    }

    // queryTags response shape: { "queryResult": { "<TagName>": [ <nodes...> ] } }.
    // All three layers are null-checked because in the mock/test path one of
    // them may legitimately be absent, and in the production path a context
    // with no matching nodes returns an empty queryResult rather than the tag
    // key.
    private static List<Object> readNodes(Map<String, Object> queryOutput, String tag) {
        if (queryOutput == null) {
            return new List<Object>();
        }
        Map<String, Object> result = (Map<String, Object>) queryOutput.get('queryResult');
        if (result == null) {
            return new List<Object>();
        }
        List<Object> nodes = (List<Object>) result.get(tag);
        return nodes != null ? nodes : new List<Object>();
    }

    /**
     * Each context attribute is wrapped as { "tagValue": <actualValue> } in
     * the queryTags response (matching the sample shape in
     * ind.pricing_customize_pricing_procedures_with_apex_hooks.htm). The
     * instanceof check accepts a bare primitive too so this helper degrades
     * gracefully if the engine ever changes to inlining scalar values.
     */
    private static String readTagString(Map<String, Object> tagMap, String key) {
        Object wrapper = tagMap.get(key);
        if (wrapper == null) {
            return null;
        }
        if (wrapper instanceof Map<String, Object>) {
            Object val = ((Map<String, Object>) wrapper).get('tagValue');
            return val == null ? null : String.valueOf(val);
        }
        return String.valueOf(wrapper);
    }

    private static String lastDataPathSegment(Map<String, Object> node) {
        List<Object> dataPath = (List<Object>) node.get('dataPath');
        if (dataPath == null || dataPath.isEmpty()) {
            return null;
        }
        Object last = dataPath.get(dataPath.size() - 1);
        return last == null ? null : String.valueOf(last);
    }

    /**
     * updateContextAttributes wants dataPath RELATIVE to the context root,
     * but queryTags returns the FULL path with the contextId as the first
     * element. Mirror the `dataPath.remove(0); // Remove contextId` step
     * shown in every Apex-hook sample in the Help docs. We copy first so we
     * don't mutate the engine's response map (it may be reused).
     */
    private static List<Object> cloneDataPathWithoutContextId(Map<String, Object> node) {
        List<Object> dataPath = (List<Object>) node.get('dataPath');
        if (dataPath == null || dataPath.isEmpty()) {
            return null;
        }
        List<Object> copy = new List<Object>(dataPath);
        copy.remove(0);
        return copy;
    }

    /**
     * Narrow wrapper over the two Context.IndustriesContext methods we use.
     * Exists solely so tests can substitute a MockContextClient. Keep the
     * surface minimal: every method added here must also be added to every
     * test mock.
     */
    public interface ContextClient {
        Map<String, Object> queryTags(Map<String, Object> input);
        Map<String, Object> updateContextAttributes(Map<String, Object> input);
    }

    private class RealContextClient implements ContextClient {
        private final Context.IndustriesContext delegateCtx = new Context.IndustriesContext();

        public Map<String, Object> queryTags(Map<String, Object> input) {
            // Tag list logged at INFO because it's small and high-value for
            // debugging "engine returned nothing" symptoms.
            logInfo('RealContextClient.queryTags() tags=' + input.get('tags'));
            return delegateCtx.queryTags(input);
        }

        public Map<String, Object> updateContextAttributes(Map<String, Object> input) {
            Object nodes = input.get('nodePathAndAttributes');
            Integer batchSize = (nodes instanceof List<Object>) ? ((List<Object>) nodes).size() : 0;
            logInfo('RealContextClient.updateContextAttributes() batchSize=' + batchSize);
            return delegateCtx.updateContextAttributes(input);
        }
    }

    // Logging helpers keep call sites short and the DEBUG_PREFIX consistent.
    // Centralised so log format, prefix, or future routing (e.g. Platform
    // Event emission) can change in one place. Use logFine for per-iteration
    // detail (only shown when the FINE category is raised), logInfo for
    // lifecycle/summary, logWarn for non-fatal skips, logError for caught
    // exceptions only.
    private static void logInfo(String msg) {
        System.debug(LoggingLevel.INFO, DEBUG_PREFIX + ': ' + msg);
    }

    private static void logFine(String msg) {
        System.debug(LoggingLevel.FINE, DEBUG_PREFIX + ': ' + msg);
    }

    private static void logWarn(String msg) {
        System.debug(LoggingLevel.WARN, DEBUG_PREFIX + ': ' + msg);
    }

    private static void logError(String msg) {
        System.debug(LoggingLevel.ERROR, DEBUG_PREFIX + ': ' + msg);
    }
}
