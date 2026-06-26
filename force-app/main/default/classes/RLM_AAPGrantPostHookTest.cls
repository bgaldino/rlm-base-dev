/**
 * Test class for RLM_AAPGrantPostHook.
 *
 * Uses a MockContextClient that implements RLM_AAPGrantPostHook.ContextClient
 * so the tests run without a live Context.IndustriesContext instance. The
 * tests insert real UsageResource records (no @SeeAllData) so the in-class
 * SOQL has data to resolve names from ids.
 */
@IsTest(IsParallel=false)
private class RLM_AAPGrantPostHookTest {

    private static final String CTX_ID = 'CTX-UNIT';
    private static final String STX_ID = 'STX-001';
    private static final String AAP_ITEM_CTX = 'ITEM-AAP-1';
    private static final String OTHER_ITEM_CTX = 'ITEM-QB-1';

    private static final String NAME_TRAFFIC = 'AAP Traffic';
    private static final String NAME_BANDWIDTH = 'AAP Bandwidth';
    private static final String NAME_REQUESTS = 'AAP Requests';

    @TestSetup
    static void seedUsageResources() {
        insert new List<UsageResource>{
            new UsageResource(Name = NAME_TRAFFIC, Code = 'AAP-TRF', Category = 'Usage', Status = 'Draft'),
            new UsageResource(Name = NAME_BANDWIDTH, Code = 'AAP-BW',  Category = 'Usage', Status = 'Draft'),
            new UsageResource(Name = NAME_REQUESTS,  Code = 'AAP-REQ', Category = 'Usage', Status = 'Draft')
        };
    }

    @IsTest
    static void happyPath_updatesAllThreeGrants() {
        Map<String, Id> resourceIdByName = loadResourceIdByName();

        MockContextClient mock = new MockContextClient();
        mock.itemsPayload(new List<Map<String, Object>>{
            aapItemNode(AAP_ITEM_CTX)
        });
        mock.attrsPayload(new List<Map<String, Object>>{
            attrNode(AAP_ITEM_CTX, 'A1', 'IncludedTrafficText',       '100'),
            attrNode(AAP_ITEM_CTX, 'A2', 'IncludedBandwidthText',     '250'),
            attrNode(AAP_ITEM_CTX, 'A3', 'IncludedMillionHitsGBText', '5000')
        });
        mock.grantsPayload(new List<Map<String, Object>>{
            grantNode(AAP_ITEM_CTX, 'G1', resourceIdByName.get(NAME_TRAFFIC)),
            grantNode(AAP_ITEM_CTX, 'G2', resourceIdByName.get(NAME_BANDWIDTH)),
            grantNode(AAP_ITEM_CTX, 'G3', resourceIdByName.get(NAME_REQUESTS))
        });

        RLM_AAPGrantPostHook hook = new RLM_AAPGrantPostHook(mock);
        Test.startTest();
        RevSignaling.TransactionResponse response = hook.execute(buildRequest(CTX_ID));
        Test.stopTest();

        System.assertEquals(RevSignaling.TransactionStatus.SUCCESS, response.status, response.message);
        System.assertEquals(1, mock.updateCallCount, 'updateContextAttributes should be called once');
        List<Object> updates = mock.lastUpdates;
        System.assertEquals(3, updates.size(), 'Expected 3 grant updates');

        Map<String, Integer> qtyByGrantLeaf = readGrantQuantitiesByLeaf(updates);
        System.assertEquals(100,  qtyByGrantLeaf.get('G1'), 'Traffic grant quantity');
        System.assertEquals(250,  qtyByGrantLeaf.get('G2'), 'Bandwidth grant quantity');
        System.assertEquals(5000, qtyByGrantLeaf.get('G3'), 'Requests grant quantity');
    }

    @IsTest
    static void nonAapItem_skipped() {
        Map<String, Id> resourceIdByName = loadResourceIdByName();

        MockContextClient mock = new MockContextClient();
        mock.itemsPayload(new List<Map<String, Object>>{
            itemNode(OTHER_ITEM_CTX, 'QB')
        });
        mock.attrsPayload(new List<Map<String, Object>>{
            attrNode(OTHER_ITEM_CTX, 'A1', 'IncludedTrafficText', '100')
        });
        mock.grantsPayload(new List<Map<String, Object>>{
            grantNode(OTHER_ITEM_CTX, 'G1', resourceIdByName.get(NAME_TRAFFIC))
        });

        RLM_AAPGrantPostHook hook = new RLM_AAPGrantPostHook(mock);
        Test.startTest();
        RevSignaling.TransactionResponse response = hook.execute(buildRequest(CTX_ID));
        Test.stopTest();

        System.assertEquals(RevSignaling.TransactionStatus.SUCCESS, response.status);
        System.assertEquals(0, mock.updateCallCount, 'No updates expected when no items are AAP');
    }

    @IsTest
    static void nullAttributeValue_skipsThatResourceOnly() {
        Map<String, Id> resourceIdByName = loadResourceIdByName();

        MockContextClient mock = new MockContextClient();
        mock.itemsPayload(new List<Map<String, Object>>{
            aapItemNode(AAP_ITEM_CTX)
        });
        mock.attrsPayload(new List<Map<String, Object>>{
            attrNode(AAP_ITEM_CTX, 'A1', 'IncludedTrafficText',       null),
            attrNode(AAP_ITEM_CTX, 'A2', 'IncludedBandwidthText',     '250'),
            attrNode(AAP_ITEM_CTX, 'A3', 'IncludedMillionHitsGBText', '5000')
        });
        mock.grantsPayload(new List<Map<String, Object>>{
            grantNode(AAP_ITEM_CTX, 'G1', resourceIdByName.get(NAME_TRAFFIC)),
            grantNode(AAP_ITEM_CTX, 'G2', resourceIdByName.get(NAME_BANDWIDTH)),
            grantNode(AAP_ITEM_CTX, 'G3', resourceIdByName.get(NAME_REQUESTS))
        });

        RLM_AAPGrantPostHook hook = new RLM_AAPGrantPostHook(mock);
        Test.startTest();
        RevSignaling.TransactionResponse response = hook.execute(buildRequest(CTX_ID));
        Test.stopTest();

        System.assertEquals(RevSignaling.TransactionStatus.SUCCESS, response.status);
        Map<String, Integer> qtyByGrantLeaf = readGrantQuantitiesByLeaf(mock.lastUpdates);
        System.assertEquals(2, qtyByGrantLeaf.size(), 'Only two resources should be updated');
        System.assert(!qtyByGrantLeaf.containsKey('G1'), 'Traffic grant must not be updated (null value)');
        System.assertEquals(250,  qtyByGrantLeaf.get('G2'));
        System.assertEquals(5000, qtyByGrantLeaf.get('G3'));
    }

    @IsTest
    static void missingUsageResource_skipsThatResourceOnly() {
        Map<String, Id> resourceIdByName = loadResourceIdByName();
        delete [SELECT Id FROM UsageResource WHERE Name = :NAME_REQUESTS];

        MockContextClient mock = new MockContextClient();
        mock.itemsPayload(new List<Map<String, Object>>{
            aapItemNode(AAP_ITEM_CTX)
        });
        mock.attrsPayload(new List<Map<String, Object>>{
            attrNode(AAP_ITEM_CTX, 'A1', 'IncludedTrafficText',       '100'),
            attrNode(AAP_ITEM_CTX, 'A2', 'IncludedBandwidthText',     '250'),
            attrNode(AAP_ITEM_CTX, 'A3', 'IncludedMillionHitsGBText', '5000')
        });
        mock.grantsPayload(new List<Map<String, Object>>{
            grantNode(AAP_ITEM_CTX, 'G1', resourceIdByName.get(NAME_TRAFFIC)),
            grantNode(AAP_ITEM_CTX, 'G2', resourceIdByName.get(NAME_BANDWIDTH)),
            grantNode(AAP_ITEM_CTX, 'G3', resourceIdByName.get(NAME_REQUESTS))
        });

        RLM_AAPGrantPostHook hook = new RLM_AAPGrantPostHook(mock);
        Test.startTest();
        RevSignaling.TransactionResponse response = hook.execute(buildRequest(CTX_ID));
        Test.stopTest();

        System.assertEquals(RevSignaling.TransactionStatus.SUCCESS, response.status);
        Map<String, Integer> qtyByGrantLeaf = readGrantQuantitiesByLeaf(mock.lastUpdates);
        System.assertEquals(2, qtyByGrantLeaf.size(), 'Only the resolvable resources should be updated');
        System.assertEquals(100, qtyByGrantLeaf.get('G1'));
        System.assertEquals(250, qtyByGrantLeaf.get('G2'));
        System.assert(!qtyByGrantLeaf.containsKey('G3'), 'Requests grant must not be updated (resource deleted)');
    }

    @IsTest
    static void recursionGuard_shortCircuits() {
        MockContextClient mock = new MockContextClient();
        mock.itemsPayload(new List<Map<String, Object>>{ aapItemNode(AAP_ITEM_CTX) });
        mock.attrsPayload(new List<Map<String, Object>>());
        mock.grantsPayload(new List<Map<String, Object>>());

        RLM_AAPGrantPostHook hook = new RLM_AAPGrantPostHook(mock);

        Test.startTest();
        RLM_AAPGrantPostHook.isRunning = true;
        RevSignaling.TransactionResponse response = hook.execute(buildRequest(CTX_ID));
        RLM_AAPGrantPostHook.isRunning = false;
        Test.stopTest();

        System.assertEquals(RevSignaling.TransactionStatus.SUCCESS, response.status);
        System.assertEquals(0, mock.queryCallCount, 'Recursion guard should short-circuit before any queryTags');
        System.assertEquals(0, mock.updateCallCount, 'Recursion guard should short-circuit before any updateContextAttributes');
    }

    @IsTest
    static void blankContextId_returnsSuccessNoOp() {
        MockContextClient mock = new MockContextClient();
        RLM_AAPGrantPostHook hook = new RLM_AAPGrantPostHook(mock);

        Test.startTest();
        RevSignaling.TransactionResponse response = hook.execute(buildRequest(null));
        Test.stopTest();

        System.assertEquals(RevSignaling.TransactionStatus.SUCCESS, response.status);
        System.assertEquals(0, mock.queryCallCount);
        System.assertEquals(0, mock.updateCallCount);
    }

    private static RevSignaling.TransactionRequest buildRequest(String contextId) {
        RevSignaling.ProcedurePlan dummyPlan = new RevSignaling.ProcedurePlan();
        return new RevSignaling.TransactionRequest(dummyPlan, contextId);
    }

    private static Map<String, Id> loadResourceIdByName() {
        Map<String, Id> byName = new Map<String, Id>();
        for (UsageResource ur : [SELECT Id, Name FROM UsageResource WHERE Name LIKE 'AAP %']) {
            byName.put(ur.Name, ur.Id);
        }
        return byName;
    }

    private static Map<String, Object> aapItemNode(String itemCtxId) {
        return itemNode(itemCtxId, 'AAP');
    }

    private static Map<String, Object> itemNode(String itemCtxId, String family) {
        return new Map<String, Object>{
            'dataPath' => new List<Object>{ CTX_ID, STX_ID, itemCtxId },
            'tagValue' => new Map<String, Object>{
                'ItemProductFamily__c' => new Map<String, Object>{ 'tagValue' => family }
            }
        };
    }

    private static Map<String, Object> attrNode(String parentItemCtxId, String attrCtxId, String attributeName, String attributeValue) {
        return new Map<String, Object>{
            'dataPath' => new List<Object>{ CTX_ID, STX_ID, parentItemCtxId, attrCtxId },
            'tagValue' => new Map<String, Object>{
                'AttributeName'                  => new Map<String, Object>{ 'tagValue' => attributeName },
                'AttributeValue'                 => new Map<String, Object>{ 'tagValue' => attributeValue },
                'SalesTransactionItemAttrParent' => new Map<String, Object>{ 'tagValue' => parentItemCtxId }
            }
        };
    }

    private static Map<String, Object> grantNode(String parentItemCtxId, String grantCtxId, Id usageResourceId) {
        return new Map<String, Object>{
            'dataPath' => new List<Object>{ CTX_ID, STX_ID, parentItemCtxId, grantCtxId },
            'tagValue' => new Map<String, Object>{
                'SalesTransactionItem__std' => new Map<String, Object>{ 'tagValue' => parentItemCtxId },
                'UsageResource__std'        => new Map<String, Object>{ 'tagValue' => String.valueOf(usageResourceId) }
            }
        };
    }

    /**
     * Reads the captured updateContextAttributes payload and returns
     * GrantQuantity__std values keyed by the last segment of each update's
     * dataPath (the grant ctx id, e.g. 'G1').
     */
    private static Map<String, Integer> readGrantQuantitiesByLeaf(List<Object> updates) {
        Map<String, Integer> result = new Map<String, Integer>();
        if (updates == null) {
            return result;
        }
        for (Object updObj : updates) {
            Map<String, Object> upd = (Map<String, Object>) updObj;
            Map<String, Object> nodePath = (Map<String, Object>) upd.get('nodePath');
            List<Object> dataPath = (List<Object>) nodePath.get('dataPath');
            String leaf = String.valueOf(dataPath.get(dataPath.size() - 1));
            List<Object> attrs = (List<Object>) upd.get('attributes');
            for (Object attrObj : attrs) {
                Map<String, Object> attr = (Map<String, Object>) attrObj;
                if ('GrantQuantity__std'.equals(attr.get('attributeName'))) {
                    Object val = attr.get('attributeValue');
                    if (val != null) {
                        result.put(leaf, Integer.valueOf(String.valueOf(val)));
                    }
                }
            }
        }
        return result;
    }

    /**
     * Records queryTags/updateContextAttributes inputs and serves canned
     * results keyed by tag name. The hook calls queryTags once per tag
     * (SalesTransactionItem, SalesTransactionItemAttribute,
     * SalesTrxnItemUseRsrcGrant__std); set each payload via the *Payload
     * helpers below.
     */
    private class MockContextClient implements RLM_AAPGrantPostHook.ContextClient {
        public Map<String, List<Object>> payloadsByTag = new Map<String, List<Object>>();
        public Integer queryCallCount = 0;
        public Integer updateCallCount = 0;
        public List<Object> lastUpdates;
        public Map<String, Object> lastUpdateInput;

        public void itemsPayload(List<Map<String, Object>> nodes) {
            payloadsByTag.put('SalesTransactionItem', toObjectList(nodes));
        }

        public void attrsPayload(List<Map<String, Object>> nodes) {
            payloadsByTag.put('SalesTransactionItemAttribute', toObjectList(nodes));
        }

        public void grantsPayload(List<Map<String, Object>> nodes) {
            payloadsByTag.put('SalesTrxnItemUseRsrcGrant__std', toObjectList(nodes));
        }

        public Map<String, Object> queryTags(Map<String, Object> input) {
            queryCallCount += 1;
            List<String> tags = (List<String>) input.get('tags');
            Map<String, Object> queryResult = new Map<String, Object>();
            for (String tag : tags) {
                List<Object> nodes = payloadsByTag.get(tag);
                queryResult.put(tag, nodes != null ? nodes : new List<Object>());
            }
            return new Map<String, Object>{ 'queryResult' => queryResult };
        }

        public Map<String, Object> updateContextAttributes(Map<String, Object> input) {
            updateCallCount += 1;
            lastUpdateInput = input;
            Object nodePathAndAttributes = input.get('nodePathAndAttributes');
            lastUpdates = nodePathAndAttributes == null ? new List<Object>() : (List<Object>) nodePathAndAttributes;
            return new Map<String, Object>{ 'status' => 'OK' };
        }

        private List<Object> toObjectList(List<Map<String, Object>> nodes) {
            List<Object> out = new List<Object>();
            if (nodes != null) {
                for (Map<String, Object> n : nodes) {
                    out.add(n);
                }
            }
            return out;
        }
    }
}
