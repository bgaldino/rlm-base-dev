/**
 * Sales Transaction (Pricing) procedure-plan posthook that copies QuantumBit
 * "AAP" product-family included-quantity SalesTransactionItemAttribute values
 * onto the matching QuotLineItmUseRsrcGrant.GrantQuantity records.
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
 *   - QuotLineItmUseRsrcGrant.GrantQuantity (Integer) via direct DML
 *
 * WHY async DML (Queueable) instead of updateContextAttributes:
 *   1. Verified 2026-07-01 across four builds (V1.3-V1.6): calling
 *      updateContextAttributes with a grant node payload returns
 *      {isSuccess: true} but the transient write is never flushed to
 *      QuotLineItmUseRsrcGrant when invoked from the interactive
 *      "Get context price" path. Only SalesTransactionItem-level writes
 *      appear to persist through the context API's post-hook commit.
 *   2. Verified 2026-07-01 in V1.7: direct sync DML inside the post-hook
 *      raises `Too many DML statements: 1` -- procedure plan hooks run
 *      with a per-transaction DML statements limit of ZERO by design.
 *   So we read grant metadata through the context (queryTags), then
 *   enqueue a Queueable that runs in a fresh transaction (normal limits)
 *   and performs `update as user` on QuotLineItmUseRsrcGrant. Persistence
 *   is therefore async -- a few seconds after re-price, not synchronous.
 *   `System.enqueueJob()` counts against the async-job limit (50/txn),
 *   not the DML statements limit, so the enqueue itself is safe.
 *   The DmlClient seam keeps the enqueue mockable in tests.
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

    // ======================================================================
    // Naming layers (from `RLM_SalesTransactionContext.contextDefinition-meta.xml`):
    //   Layer 1  <contextNodes>/<contextAttributes><title>          semantic name (schema)
    //   Layer 2  <contextNodeMappings><contextAttribute>            persistence mapping name
    //   Layer 3  <contextTags><title>                               RUNTIME tag key
    //
    // RULE: keys passed to queryTags MUST be Layer 3 (contextTag title). The
    // Layer 1/2 names are declarative metadata only -- queryTags rejects them.
    //
    // Writes are done via direct SObject DML (see class header for the
    // "why"), NOT via updateContextAttributes, so we do NOT need the Layer 3
    // name for GrantQuantity here -- the SObject field is simply
    // `QuotLineItmUseRsrcGrant.GrantQuantity`.
    //
    // Verified in `RLM_SalesTransactionContext.contextDefinition-meta.xml`:
    //   line 23566  AttributeName -> contextTag 'Attribute'
    //   line 23828  SalesTransactionItem__std (grant->item lookup) -> contextTag 'STI_URGSTIId__std'
    //   line 23856  UsageResource__std (grant->resource lookup) -> contextTag 'STI_URGSTIURId__std'
    //   line 24021  SalesTrxnItemUseRsrcGrant__std (node) -> contextTag 'STIUseRsrcGrantTag__std'
    // Constants for SalesTransactionItem / SalesTransactionItemAttribute /
    // AttributeValue / SalesTransactionItemAttrParent / ItemProductFamily__c
    // work because their contextTag title equals their outer title.
    // ======================================================================

    private static final String TAG_STI = 'SalesTransactionItem';
    private static final String TAG_STIA = 'SalesTransactionItemAttribute';
    // The grant node is queryable as a TOP-LEVEL tag under its contextTag
    // title. Verified 2026-07-01: queryTags([this]) returns all grants in
    // the transaction, filterable by GRANT_STI_PARENT.
    private static final String TAG_GRANT = 'STIUseRsrcGrantTag__std';

    // Attribute (on SalesTransactionItemAttribute) tag keys. 'Attribute' is
    // the canonical contextTag title; 'AttributeName' is a defensive fallback.
    private static final List<String> ATTR_NAME_KEYS = new List<String>{ 'Attribute', 'AttributeName' };
    private static final String ATTR_VALUE = 'AttributeValue';
    private static final String ATTR_STIA_PARENT = 'SalesTransactionItemAttrParent';

    // Grant contextTag keys used for READS via queryTags.
    private static final String GRANT_STI_PARENT = 'STI_URGSTIId__std';   // grant -> parent item
    private static final String GRANT_RESOURCE   = 'STI_URGSTIURId__std'; // grant -> UsageResource lookup

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
    private static final String DEBUG_VERSION = 'V1.8';

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
    // always invokes the no-arg constructor; the @TestVisible constructors
    // are used by RLM_AAPGrantPostHookTest to inject mocks.
    @TestVisible
    private ContextClient industriesContext;

    // Same rationale for the DML seam: hoists the QuotLineItmUseRsrcGrant
    // update DML into a stubbable collaborator so the mock-based test can
    // capture the exact records that WOULD be updated without needing a
    // full Quote + QuoteLineItem + UsageResource fixture. Production wires
    // this to RealDmlClient (`update as user`).
    @TestVisible
    private DmlClient grantDml;

    public RLM_AAPGrantPostHook() {
        this.industriesContext = new RealContextClient();
        this.grantDml = new RealDmlClient();
    }

    @TestVisible
    private RLM_AAPGrantPostHook(ContextClient client) {
        this(client, new RealDmlClient());
    }

    @TestVisible
    private RLM_AAPGrantPostHook(ContextClient client, DmlClient dml) {
        this.industriesContext = client;
        this.grantDml = dml;
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
            Map<String, Map<String, Object>> aapItemsByCtxId = findAapItems(contextId);
            logInfo('execute() step 1/4 AAP items found=' + aapItemsByCtxId.size()
                + ' ctxIds=' + aapItemsByCtxId.keySet());
            if (aapItemsByCtxId.isEmpty()) {
                logInfo('execute() SKIP: no AAP items; returning SUCCESS no-op');
                response.status = RevSignaling.TransactionStatus.SUCCESS;
                response.message = 'No AAP product-family items in context; nothing to do.';
                return response;
            }

            Map<String, Map<String, Integer>> qtyByItemByResource =
                queryQuantitiesByItem(contextId, aapItemsByCtxId.keySet());
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

            List<QuotLineItmUseRsrcGrant> grantUpdates =
                buildGrantUpdates(contextId, aapItemsByCtxId.keySet(), qtyByItemByResource, resourceNameById);
            logInfo('execute() step 4/4 grant updates built=' + grantUpdates.size());

            // Enqueue an async Queueable to perform the DML. Procedure plan
            // hooks disallow sync DML (V1.7 raised "Too many DML statements: 1"),
            // so the actual update runs in a fresh transaction. Persistence
            // is therefore visible a few seconds AFTER this hook returns --
            // check the AsyncApexJob record or the debug log of the async
            // job for the final commit and post-commit verification.
            if (!grantUpdates.isEmpty()) {
                logFine('execute() enqueuing async DML for records='
                    + JSON.serializePretty(grantUpdates));
                grantDml.updateGrants(grantUpdates);
                logInfo('execute() async DML enqueued (' + grantUpdates.size()
                    + ' QuotLineItmUseRsrcGrant records) -- DB commit happens in a separate transaction');
            } else {
                logInfo('execute() no updates to submit; skipping async DML enqueue');
            }

            response.status = RevSignaling.TransactionStatus.SUCCESS;
            response.message = 'AAP grant quantity updates enqueued: ' + grantUpdates.size();
            logInfo('=== execute() EXIT status=SUCCESS updatesEnqueued=' + grantUpdates.size() + ' ===');
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
     * Returns: itemCtxId -> full SalesTransactionItem node (Map<String,Object>
     * with `tagValue` and `dataPath`). Keeping the full node -- not just the
     * id -- is essential because the STIUseRsrcGrantTag__std child
     * nodes are NESTED inside each SalesTransactionItem's tagValue, not
     * queryable as a top-level tag. The schema-level <contextNodes> block
     * (line 24024 of RLM_SalesTransactionContext.contextDefinition-meta.xml)
     * declares the grant's <inheritedFrom> as
     * `SalesTransaction/SalesTransactionItem/STIUseRsrcGrantTag__std`,
     * confirming it lives one level below SalesTransactionItem.
     *
     * Verified empirically 2026-06-30: queryTags with tags=[STIUseRsrcGrantTag__std]
     * fails with ContextModificationException "Invalid tag attribute name key".
     *
     * The returned key (itemCtxId) is a CONTEXT id (engine-assigned runtime
     * identifier), NOT a Salesforce record id. It is the cross-node join key
     * used by `SalesTransactionItemAttribute.SalesTransactionItemAttrParent`.
     * equalsIgnoreCase is defensive: picklist persists 'AAP' but we don't
     * want a casing drift to silently disable the hook.
     */
    private Map<String, Map<String, Object>> findAapItems(String contextId) {
        logFine('findAapItems() ENTER contextId=' + contextId);
        Map<String, Object> input = new Map<String, Object>{
            'contextId' => contextId,
            'tags' => new List<String>{ TAG_STI }
        };
        Map<String, Object> output = industriesContext.queryTags(input);
        List<Object> items = readNodes(output, TAG_STI);
        logInfo('findAapItems() queryTags returned ' + items.size() + ' ' + TAG_STI + ' node(s)');

        Map<String, Map<String, Object>> byCtxId = new Map<String, Map<String, Object>>();
        Integer skippedNoTagMap = 0;
        Integer skippedNonAap = 0;
        Integer skippedBlankCtxId = 0;
        Boolean dumpedFirstItemKeys = false;
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
                logFine('findAapItems() skip non-AAP item: family=' + family);
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
            byCtxId.put(itemCtxId, node);
            logFine('findAapItems() matched AAP item ctxId=' + itemCtxId);
            // Dump SalesTransactionItem tagMap keys once, on the first AAP
            // item, so the nested grant child key is visible in the log
            // (the full map is ~138 entries so we only do it once).
            if (!dumpedFirstItemKeys) {
                logFine('findAapItems() SalesTransactionItem tagMap keys for first AAP item ('
                    + itemCtxId + ')=' + tagMap.keySet());
                dumpedFirstItemKeys = true;
            }
        }
        logInfo('findAapItems() EXIT matched=' + byCtxId.size()
            + ' skipped_no_tagMap=' + skippedNoTagMap
            + ' skipped_non_aap=' + skippedNonAap
            + ' skipped_blank_ctxid=' + skippedBlankCtxId);
        return byCtxId;
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
            // Diagnostic: dump every tag key on AAP-parented attributes the
            // first time we walk them. Keeps the log small (only AAP items)
            // while making any future key-name drift trivial to spot.
            logFine('queryQuantitiesByItem() attribute on AAP item '
                + parentItemCtxId + ' has tagMap keys=' + tagMap.keySet());
            String attrName = readTagStringAny(tagMap, ATTR_NAME_KEYS);
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
     * Queries `STIUseRsrcGrantTag__std` grants at the top level of the
     * context (contextTag title), filters each grant by its parent
     * (STI_URGSTIId__std) against the AAP item ctx-id set and by its
     * resource lookup (STI_URGSTIURId__std) against our three AAP
     * UsageResource ids, then builds a `List<QuotLineItmUseRsrcGrant>`
     * ready for direct DML.
     *
     * The grant's own ctx id (leaf of `dataPath`) IS the underlying
     * `QuotLineItmUseRsrcGrant.Id` -- verified 2026-07-01: dataPath
     * segment 3 is an 18-char SObject Id with the QuotLineItmUseRsrcGrant
     * key prefix. So we can update by Id directly, no extra SOQL needed.
     * If a future context type changes this invariant, this method is the
     * one place that needs to change (swap the direct Id write for a
     * QuoteLineItemId + UsageResourceId lookup query).
     */
    private List<QuotLineItmUseRsrcGrant> buildGrantUpdates(
        String contextId,
        Set<String> aapItemCtxIds,
        Map<String, Map<String, Integer>> qtyByItemByResource,
        Map<Id, String> resourceNameById
    ) {
        logFine('buildGrantUpdates() ENTER aapItems=' + aapItemCtxIds.size()
            + ' itemsWithQty=' + qtyByItemByResource.size()
            + ' knownResources=' + resourceNameById.size());
        List<QuotLineItmUseRsrcGrant> updates = new List<QuotLineItmUseRsrcGrant>();
        Set<Id> updatedGrantIds = new Set<Id>();

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
        Integer skippedBadGrantId = 0;
        Integer skippedDuplicate = 0;
        Boolean dumpedFirstGrantKeys = false;
        for (Object grantObj : grants) {
            Map<String, Object> node = (Map<String, Object>) grantObj;
            Map<String, Object> tagMap = (Map<String, Object>) node.get('tagValue');
            if (tagMap == null) {
                skippedNoTagMap++;
                continue;
            }
            if (!dumpedFirstGrantKeys) {
                logFine('buildGrantUpdates() first grant tagMap keys=' + tagMap.keySet());
                dumpedFirstGrantKeys = true;
            }
            String parentItemCtxId = readTagString(tagMap, GRANT_STI_PARENT);
            if (String.isBlank(parentItemCtxId) || !aapItemCtxIds.contains(parentItemCtxId)) {
                skippedNonAapParent++;
                logFine('buildGrantUpdates() skip grant: parentItemCtxId=' + parentItemCtxId + ' not in AAP set');
                continue;
            }
            Map<String, Integer> queuedQtyByResource = qtyByItemByResource.get(parentItemCtxId);
            if (queuedQtyByResource == null || queuedQtyByResource.isEmpty()) {
                skippedNoQueuedQty++;
                continue;
            }
            String resourceIdString = readTagString(tagMap, GRANT_RESOURCE);
            if (String.isBlank(resourceIdString)) {
                skippedBlankResourceId++;
                continue;
            }
            // Id.valueOf inside try/catch per the apex-classes rule: untrusted
            // string -> Id conversion must never throw out of the loop.
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

            // The grant's own ctx id (leaf of dataPath) is its SObject Id.
            String grantIdStr = lastDataPathSegment(node);
            Id grantId;
            try {
                grantId = Id.valueOf(grantIdStr);
            } catch (Exception idEx) {
                skippedBadGrantId++;
                logWarn('buildGrantUpdates() invalid grant Id "' + grantIdStr
                    + '" on item ' + parentItemCtxId + '; skipping ('
                    + idEx.getMessage() + ')');
                continue;
            }
            // Same grant should never appear twice in one queryTags response,
            // but be defensive: an UPDATE-with-duplicate-Ids is a runtime DML
            // exception that would abort the whole batch.
            if (updatedGrantIds.contains(grantId)) {
                skippedDuplicate++;
                continue;
            }
            updatedGrantIds.add(grantId);

            updates.add(new QuotLineItmUseRsrcGrant(
                Id = grantId,
                GrantQuantity = qty
            ));
            logInfo('buildGrantUpdates() queued DML update grantId=' + grantId
                + ' item=' + parentItemCtxId + ' resource=' + resourceName
                + ' GrantQuantity=' + qty);
        }
        logInfo('buildGrantUpdates() EXIT updates=' + updates.size()
            + ' total_grants_walked=' + grants.size()
            + ' skipped_no_tagMap=' + skippedNoTagMap
            + ' skipped_non_aap_parent=' + skippedNonAapParent
            + ' skipped_no_queued_qty=' + skippedNoQueuedQty
            + ' skipped_blank_resource_id=' + skippedBlankResourceId
            + ' skipped_invalid_resource_id=' + skippedInvalidResourceId
            + ' skipped_unknown_resource=' + skippedUnknownResource
            + ' skipped_no_qty=' + skippedNoQty
            + ' skipped_bad_grant_id=' + skippedBadGrantId
            + ' skipped_duplicate=' + skippedDuplicate);
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

    /**
     * Tries each candidate key in order and returns the first non-blank
     * tagValue. Exists to absorb the AttributeName-vs-Attribute drift between
     * the context definition and the runtime payload (see ATTR_NAME_KEYS).
     */
    private static String readTagStringAny(Map<String, Object> tagMap, List<String> keys) {
        for (String k : keys) {
            String v = readTagString(tagMap, k);
            if (String.isNotBlank(v)) {
                return v;
            }
        }
        return null;
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
     * Narrow wrapper over the single Context.IndustriesContext method we
     * still use (queryTags). Exists solely so tests can substitute a
     * MockContextClient; Context.IndustriesContext is not stubbable.
     * Writes go through DmlClient (below), not the context API.
     */
    public interface ContextClient {
        Map<String, Object> queryTags(Map<String, Object> input);
    }

    private class RealContextClient implements ContextClient {
        private final Context.IndustriesContext delegateCtx = new Context.IndustriesContext();

        public Map<String, Object> queryTags(Map<String, Object> input) {
            // Tag list logged at INFO because it's small and high-value for
            // debugging "engine returned nothing" symptoms.
            logInfo('RealContextClient.queryTags() tags=' + input.get('tags'));
            return delegateCtx.queryTags(input);
        }
    }

    /**
     * DML seam so the mock-based test can assert exactly which
     * QuotLineItmUseRsrcGrant records the hook would update, without
     * needing a real Quote + QuoteLineItem + UsageResource + Grant
     * fixture. Production wires this to RealDmlClient, which enqueues
     * an AAPGrantUpdateQueueable that performs the DML in a separate
     * transaction (procedure plan hooks disallow sync DML).
     */
    public interface DmlClient {
        void updateGrants(List<QuotLineItmUseRsrcGrant> grants);
    }

    private class RealDmlClient implements DmlClient {
        public void updateGrants(List<QuotLineItmUseRsrcGrant> grants) {
            logInfo('RealDmlClient.updateGrants() enqueue batchSize=' + grants.size());
            Id jobId = System.enqueueJob(new AAPGrantUpdateQueueable(grants));
            logInfo('RealDmlClient.updateGrants() enqueued Queueable jobId=' + jobId);
        }
    }

    /**
     * Async DML worker. Runs in its own transaction with normal governor
     * limits (including standard DML statements allowance), so it can
     * safely call `update as user` on the grant records the post-hook
     * queued. Also does a read-back so the debug log records what
     * actually persisted (or which trigger/workflow rolled it back).
     *
     * `update as user` enforces object + FLS permissions on
     * QuotLineItmUseRsrcGrant / GrantQuantity for the ENQUEUING user
     * (Queueable inherits their identity); a missing permission raises
     * NoAccessException, which is logged and re-thrown so Salesforce's
     * standard async retry / failed-job tracking kicks in.
     */
    public class AAPGrantUpdateQueueable implements Queueable {
        private final List<QuotLineItmUseRsrcGrant> updates;

        public AAPGrantUpdateQueueable(List<QuotLineItmUseRsrcGrant> updates) {
            this.updates = updates;
        }

        public void execute(QueueableContext ctx) {
            if (updates == null || updates.isEmpty()) {
                logInfo('AAPGrantUpdateQueueable.execute() nothing to do (empty batch)');
                return;
            }
            logInfo('AAPGrantUpdateQueueable.execute() ENTER batchSize=' + updates.size()
                + ' jobId=' + (ctx != null ? ctx.getJobId() : null));
            try {
                update as user updates;
                logInfo('AAPGrantUpdateQueueable.execute() DML committed (' + updates.size() + ' records)');
                logPostUpdateVerification(updates);
            } catch (Exception e) {
                logError('AAPGrantUpdateQueueable.execute() DML FAILED: '
                    + e.getMessage() + ' stack=' + e.getStackTraceString());
                // Re-throw so Salesforce marks the async job as Failed
                // and the operator sees it in AsyncApexJob.
                throw e;
            }
        }

        /**
         * Reads the updated grants back and logs their persisted values.
         * If a trigger/workflow rolls the write back, this line is the
         * quickest way to spot it.
         */
        private void logPostUpdateVerification(List<QuotLineItmUseRsrcGrant> updated) {
            try {
                Set<Id> ids = new Set<Id>();
                for (QuotLineItmUseRsrcGrant g : updated) {
                    ids.add(g.Id);
                }
                for (QuotLineItmUseRsrcGrant g : [
                    SELECT Id, GrantQuantity, QuoteLineItemId, UsageResourceId
                    FROM QuotLineItmUseRsrcGrant
                    WHERE Id IN :ids
                    WITH USER_MODE
                ]) {
                    logInfo('post-DML verification grantId=' + g.Id
                        + ' QuoteLineItemId=' + g.QuoteLineItemId
                        + ' UsageResourceId=' + g.UsageResourceId
                        + ' persisted GrantQuantity=' + g.GrantQuantity);
                }
            } catch (Exception readEx) {
                logWarn('post-DML verification SOQL failed: ' + readEx.getMessage());
            }
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
