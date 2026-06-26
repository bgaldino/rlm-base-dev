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

    @TestVisible
    private static Boolean isRunning = false;

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

        if (isRunning) {
            response.status = RevSignaling.TransactionStatus.SUCCESS;
            response.message = 'Skipped recursive execution.';
            return response;
        }

        String contextId = request != null ? request.ctxInstanceId : null;
        if (String.isBlank(contextId)) {
            response.status = RevSignaling.TransactionStatus.SUCCESS;
            response.message = 'No context id supplied; nothing to do.';
            return response;
        }

        try {
            isRunning = true;

            Set<String> aapItemCtxIds = queryAapItemCtxIds(contextId);
            if (aapItemCtxIds.isEmpty()) {
                response.status = RevSignaling.TransactionStatus.SUCCESS;
                response.message = 'No AAP product-family items in context; nothing to do.';
                return response;
            }

            Map<String, Map<String, Integer>> qtyByItemByResource =
                queryQuantitiesByItem(contextId, aapItemCtxIds);
            if (qtyByItemByResource.isEmpty()) {
                response.status = RevSignaling.TransactionStatus.SUCCESS;
                response.message = 'No matching SalesTransactionItemAttribute rows for AAP items; nothing to do.';
                return response;
            }

            Map<Id, String> resourceNameById = loadResourceNameById();

            List<Object> nodeUpdates =
                buildGrantUpdates(contextId, aapItemCtxIds, qtyByItemByResource, resourceNameById);

            if (!nodeUpdates.isEmpty()) {
                Map<String, Object> updateInput = new Map<String, Object>{
                    'contextId' => contextId,
                    'nodePathAndAttributes' => nodeUpdates
                };
                industriesContext.updateContextAttributes(updateInput);
            }

            response.status = RevSignaling.TransactionStatus.SUCCESS;
            response.message = 'AAP grant quantities updated: ' + nodeUpdates.size();
            return response;
        } catch (Exception e) {
            System.debug(LoggingLevel.ERROR, 'RLM_AAPGrantPostHook error: ' + e.getMessage()
                + ' stack=' + e.getStackTraceString());
            response.status = RevSignaling.TransactionStatus.FAILED;
            response.message = 'RLM_AAPGrantPostHook error: ' + e.getMessage();
            return response;
        } finally {
            isRunning = false;
        }
    }

    private Set<String> queryAapItemCtxIds(String contextId) {
        Map<String, Object> input = new Map<String, Object>{
            'contextId' => contextId,
            'tags' => new List<String>{ TAG_STI }
        };
        Map<String, Object> output = industriesContext.queryTags(input);
        List<Object> items = readNodes(output, TAG_STI);

        Set<String> ctxIds = new Set<String>();
        for (Object itemObj : items) {
            Map<String, Object> node = (Map<String, Object>) itemObj;
            Map<String, Object> tagMap = (Map<String, Object>) node.get('tagValue');
            if (tagMap == null) {
                continue;
            }
            String family = readTagString(tagMap, ITEM_FAMILY_ATTR);
            if (AAP_PRODUCT_FAMILY.equalsIgnoreCase(family)) {
                String itemCtxId = lastDataPathSegment(node);
                if (String.isNotBlank(itemCtxId)) {
                    ctxIds.add(itemCtxId);
                }
            }
        }
        return ctxIds;
    }

    private Map<String, Map<String, Integer>> queryQuantitiesByItem(
        String contextId,
        Set<String> aapItemCtxIds
    ) {
        Map<String, Object> input = new Map<String, Object>{
            'contextId' => contextId,
            'tags' => new List<String>{ TAG_STIA }
        };
        Map<String, Object> output = industriesContext.queryTags(input);
        List<Object> attrs = readNodes(output, TAG_STIA);

        Map<String, Map<String, Integer>> byItem = new Map<String, Map<String, Integer>>();
        for (Object attrObj : attrs) {
            Map<String, Object> node = (Map<String, Object>) attrObj;
            Map<String, Object> tagMap = (Map<String, Object>) node.get('tagValue');
            if (tagMap == null) {
                continue;
            }
            String parentItemCtxId = readTagString(tagMap, ATTR_STIA_PARENT);
            if (String.isBlank(parentItemCtxId) || !aapItemCtxIds.contains(parentItemCtxId)) {
                continue;
            }
            String attrName = readTagString(tagMap, ATTR_NAME);
            String resourceName = ATTR_NAME_TO_RESOURCE_NAME.get(attrName);
            if (resourceName == null) {
                continue;
            }
            String rawValue = readTagString(tagMap, ATTR_VALUE);
            if (String.isBlank(rawValue)) {
                continue;
            }
            Integer qty;
            try {
                qty = Integer.valueOf(rawValue.trim());
            } catch (Exception parseEx) {
                System.debug(LoggingLevel.WARN, 'RLM_AAPGrantPostHook: non-integer AttributeValue "'
                    + rawValue + '" for ' + attrName + ' on item ' + parentItemCtxId
                    + '; skipping (' + parseEx.getMessage() + ')');
                continue;
            }
            Map<String, Integer> byResource = byItem.get(parentItemCtxId);
            if (byResource == null) {
                byResource = new Map<String, Integer>();
                byItem.put(parentItemCtxId, byResource);
            }
            byResource.put(resourceName, qty);
        }
        return byItem;
    }

    private Map<Id, String> loadResourceNameById() {
        Map<Id, String> nameById = new Map<Id, String>();
        Set<String> wantedNames = new Set<String>(ATTR_NAME_TO_RESOURCE_NAME.values());
        for (UsageResource ur : [
            SELECT Id, Name
            FROM UsageResource
            WHERE Name IN :wantedNames
            WITH USER_MODE
        ]) {
            nameById.put(ur.Id, ur.Name);
        }
        return nameById;
    }

    private List<Object> buildGrantUpdates(
        String contextId,
        Set<String> aapItemCtxIds,
        Map<String, Map<String, Integer>> qtyByItemByResource,
        Map<Id, String> resourceNameById
    ) {
        List<Object> updates = new List<Object>();

        Map<String, Object> input = new Map<String, Object>{
            'contextId' => contextId,
            'tags' => new List<String>{ TAG_GRANT }
        };
        Map<String, Object> output = industriesContext.queryTags(input);
        List<Object> grants = readNodes(output, TAG_GRANT);

        for (Object grantObj : grants) {
            Map<String, Object> node = (Map<String, Object>) grantObj;
            Map<String, Object> tagMap = (Map<String, Object>) node.get('tagValue');
            if (tagMap == null) {
                continue;
            }
            String parentItemCtxId = readTagString(tagMap, ATTR_GRANT_PARENT);
            if (String.isBlank(parentItemCtxId) || !aapItemCtxIds.contains(parentItemCtxId)) {
                continue;
            }
            Map<String, Integer> queuedQtyByResource = qtyByItemByResource.get(parentItemCtxId);
            if (queuedQtyByResource == null || queuedQtyByResource.isEmpty()) {
                continue;
            }
            String resourceIdString = readTagString(tagMap, ATTR_GRANT_RESOURCE);
            if (String.isBlank(resourceIdString)) {
                continue;
            }
            Id resourceId;
            try {
                resourceId = Id.valueOf(resourceIdString);
            } catch (Exception idEx) {
                System.debug(LoggingLevel.WARN, 'RLM_AAPGrantPostHook: invalid UsageResource Id "'
                    + resourceIdString + '"; skipping (' + idEx.getMessage() + ')');
                continue;
            }
            String resourceName = resourceNameById.get(resourceId);
            if (resourceName == null) {
                continue;
            }
            Integer qty = queuedQtyByResource.get(resourceName);
            if (qty == null) {
                continue;
            }

            List<Object> grantPath = cloneDataPathWithoutContextId(node);
            if (grantPath == null || grantPath.isEmpty()) {
                continue;
            }

            updates.add(new Map<String, Object>{
                'nodePath' => new Map<String, Object>{ 'dataPath' => grantPath },
                'attributes' => new List<Object>{
                    new Map<String, Object>{
                        'attributeName' => GRANT_QUANTITY_ATTR,
                        'attributeValue' => qty
                    }
                }
            });
        }
        return updates;
    }

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

    private static List<Object> cloneDataPathWithoutContextId(Map<String, Object> node) {
        List<Object> dataPath = (List<Object>) node.get('dataPath');
        if (dataPath == null || dataPath.isEmpty()) {
            return null;
        }
        List<Object> copy = new List<Object>(dataPath);
        copy.remove(0);
        return copy;
    }

    public interface ContextClient {
        Map<String, Object> queryTags(Map<String, Object> input);
        Map<String, Object> updateContextAttributes(Map<String, Object> input);
    }

    private class RealContextClient implements ContextClient {
        private final Context.IndustriesContext delegateCtx = new Context.IndustriesContext();

        public Map<String, Object> queryTags(Map<String, Object> input) {
            return delegateCtx.queryTags(input);
        }

        public Map<String, Object> updateContextAttributes(Map<String, Object> input) {
            return delegateCtx.updateContextAttributes(input);
        }
    }
}
