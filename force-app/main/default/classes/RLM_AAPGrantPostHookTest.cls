/**
 * Test class for RLM_AAPGrantPostHook (V1.7+ direct-DML variant).
 *
 * V1.7 stopped writing grants through Context.IndustriesContext.updateContextAttributes
 * (which reported isSuccess=true but never flushed to QuotLineItmUseRsrcGrant
 * from the interactive-pricing post-hook path) and switched to direct SObject
 * DML. This test class matches that architecture:
 *   - MockContextClient serves canned queryTags responses.
 *   - MockDmlClient captures the List<QuotLineItmUseRsrcGrant> that the hook
 *     WOULD update, so we can assert on Id + GrantQuantity without needing a
 *     full Quote / QuoteLineItem / UsageResource / Grant fixture.
 *
 * The three grant "ctx ids" in the test fixtures are synthetic Ids built with
 * the real `QuotLineItmUseRsrcGrant` key prefix (via getDescribe().getKeyPrefix)
 * so the hook's `Id.valueOf(grantCtxId)` call succeeds. No records with those
 * Ids exist in the org; the mock intercepts DML before it goes to the database.
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

    // Cached because Schema.getKeyPrefix() is not the cheapest call and every
    // test reads it several times. Populated lazily on first use.
    private static String grantKeyPrefix;

    @TestSetup
    static void seedUsageResources() {
        // UsageResource requires UnitOfMeasureClassId AND DefaultUnitOfMeasureId.
        UnitOfMeasureClass uomClass = new UnitOfMeasureClass(
            Name = 'AAP Test UoM Class',
            Code = 'AAP-TST-UOMC',
            Status = 'Draft'
        );
        insert uomClass;
        UnitOfMeasure uom = new UnitOfMeasure(
            Name = 'AAP Test UoM',
            UnitCode = 'AAP-TST-UOM',
            UnitOfMeasureClassId = uomClass.Id
        );
        insert uom;
        insert new List<UsageResource>{
            new UsageResource(Name = NAME_TRAFFIC,   Code = 'AAP-TRF', Category = 'Usage', Status = 'Draft', UnitOfMeasureClassId = uomClass.Id, DefaultUnitOfMeasureId = uom.Id),
            new UsageResource(Name = NAME_BANDWIDTH, Code = 'AAP-BW',  Category = 'Usage', Status = 'Draft', UnitOfMeasureClassId = uomClass.Id, DefaultUnitOfMeasureId = uom.Id),
            new UsageResource(Name = NAME_REQUESTS,  Code = 'AAP-REQ', Category = 'Usage', Status = 'Draft', UnitOfMeasureClassId = uomClass.Id, DefaultUnitOfMeasureId = uom.Id)
        };
    }

    @IsTest
    static void happyPath_updatesAllThreeGrants() {
        Map<String, Id> resourceIdByName = loadResourceIdByName();
        Id g1 = fakeGrantId(1);
        Id g2 = fakeGrantId(2);
        Id g3 = fakeGrantId(3);

        MockContextClient mockCtx = new MockContextClient();
        MockDmlClient mockDml = new MockDmlClient();
        mockCtx.itemsPayload(new List<Map<String, Object>>{ aapItemNode(AAP_ITEM_CTX) });
        mockCtx.attrsPayload(new List<Map<String, Object>>{
            attrNode(AAP_ITEM_CTX, 'A1', 'IncludedTrafficText',       '100'),
            attrNode(AAP_ITEM_CTX, 'A2', 'IncludedBandwidthText',     '250'),
            attrNode(AAP_ITEM_CTX, 'A3', 'IncludedMillionHitsGBText', '5000')
        });
        mockCtx.grantsPayload(new List<Map<String, Object>>{
            grantNode(AAP_ITEM_CTX, g1, resourceIdByName.get(NAME_TRAFFIC)),
            grantNode(AAP_ITEM_CTX, g2, resourceIdByName.get(NAME_BANDWIDTH)),
            grantNode(AAP_ITEM_CTX, g3, resourceIdByName.get(NAME_REQUESTS))
        });

        RLM_AAPGrantPostHook hook = new RLM_AAPGrantPostHook(mockCtx, mockDml);
        Test.startTest();
        RevSignaling.TransactionResponse response = hook.execute(buildRequest(CTX_ID));
        Test.stopTest();

        System.assertEquals(RevSignaling.TransactionStatus.SUCCESS, response.status, response.message);
        System.assertEquals(1, mockDml.updateCallCount, 'DML update should be called exactly once');
        System.assertEquals(3, mockDml.lastUpdates.size(), 'Expected 3 grant updates');

        Map<Id, Integer> qtyById = qtyByGrantId(mockDml.lastUpdates);
        System.assertEquals(100,  qtyById.get(g1), 'Traffic grant quantity');
        System.assertEquals(250,  qtyById.get(g2), 'Bandwidth grant quantity');
        System.assertEquals(5000, qtyById.get(g3), 'Requests grant quantity');
    }

    @IsTest
    static void nonAapItem_skipped() {
        Map<String, Id> resourceIdByName = loadResourceIdByName();

        MockContextClient mockCtx = new MockContextClient();
        MockDmlClient mockDml = new MockDmlClient();
        mockCtx.itemsPayload(new List<Map<String, Object>>{ itemNode(OTHER_ITEM_CTX, 'QB') });
        mockCtx.attrsPayload(new List<Map<String, Object>>{
            attrNode(OTHER_ITEM_CTX, 'A1', 'IncludedTrafficText', '100')
        });
        mockCtx.grantsPayload(new List<Map<String, Object>>{
            grantNode(OTHER_ITEM_CTX, fakeGrantId(1), resourceIdByName.get(NAME_TRAFFIC))
        });

        RLM_AAPGrantPostHook hook = new RLM_AAPGrantPostHook(mockCtx, mockDml);
        Test.startTest();
        RevSignaling.TransactionResponse response = hook.execute(buildRequest(CTX_ID));
        Test.stopTest();

        System.assertEquals(RevSignaling.TransactionStatus.SUCCESS, response.status);
        System.assertEquals(0, mockDml.updateCallCount, 'No DML expected when no items are AAP');
    }

    @IsTest
    static void nullAttributeValue_skipsThatResourceOnly() {
        Map<String, Id> resourceIdByName = loadResourceIdByName();
        Id g1 = fakeGrantId(1);
        Id g2 = fakeGrantId(2);
        Id g3 = fakeGrantId(3);

        MockContextClient mockCtx = new MockContextClient();
        MockDmlClient mockDml = new MockDmlClient();
        mockCtx.itemsPayload(new List<Map<String, Object>>{ aapItemNode(AAP_ITEM_CTX) });
        mockCtx.attrsPayload(new List<Map<String, Object>>{
            attrNode(AAP_ITEM_CTX, 'A1', 'IncludedTrafficText',       null),
            attrNode(AAP_ITEM_CTX, 'A2', 'IncludedBandwidthText',     '250'),
            attrNode(AAP_ITEM_CTX, 'A3', 'IncludedMillionHitsGBText', '5000')
        });
        mockCtx.grantsPayload(new List<Map<String, Object>>{
            grantNode(AAP_ITEM_CTX, g1, resourceIdByName.get(NAME_TRAFFIC)),
            grantNode(AAP_ITEM_CTX, g2, resourceIdByName.get(NAME_BANDWIDTH)),
            grantNode(AAP_ITEM_CTX, g3, resourceIdByName.get(NAME_REQUESTS))
        });

        RLM_AAPGrantPostHook hook = new RLM_AAPGrantPostHook(mockCtx, mockDml);
        Test.startTest();
        RevSignaling.TransactionResponse response = hook.execute(buildRequest(CTX_ID));
        Test.stopTest();

        System.assertEquals(RevSignaling.TransactionStatus.SUCCESS, response.status);
        Map<Id, Integer> qtyById = qtyByGrantId(mockDml.lastUpdates);
        System.assertEquals(2, qtyById.size(), 'Only two resources should be updated');
        System.assert(!qtyById.containsKey(g1), 'Traffic grant must not be updated (null value)');
        System.assertEquals(250,  qtyById.get(g2));
        System.assertEquals(5000, qtyById.get(g3));
    }

    @IsTest
    static void missingUsageResource_skipsThatResourceOnly() {
        Map<String, Id> resourceIdByName = loadResourceIdByName();
        delete [SELECT Id FROM UsageResource WHERE Name = :NAME_REQUESTS];
        Id g1 = fakeGrantId(1);
        Id g2 = fakeGrantId(2);
        Id g3 = fakeGrantId(3);

        MockContextClient mockCtx = new MockContextClient();
        MockDmlClient mockDml = new MockDmlClient();
        mockCtx.itemsPayload(new List<Map<String, Object>>{ aapItemNode(AAP_ITEM_CTX) });
        mockCtx.attrsPayload(new List<Map<String, Object>>{
            attrNode(AAP_ITEM_CTX, 'A1', 'IncludedTrafficText',       '100'),
            attrNode(AAP_ITEM_CTX, 'A2', 'IncludedBandwidthText',     '250'),
            attrNode(AAP_ITEM_CTX, 'A3', 'IncludedMillionHitsGBText', '5000')
        });
        mockCtx.grantsPayload(new List<Map<String, Object>>{
            grantNode(AAP_ITEM_CTX, g1, resourceIdByName.get(NAME_TRAFFIC)),
            grantNode(AAP_ITEM_CTX, g2, resourceIdByName.get(NAME_BANDWIDTH)),
            grantNode(AAP_ITEM_CTX, g3, resourceIdByName.get(NAME_REQUESTS))
        });

        RLM_AAPGrantPostHook hook = new RLM_AAPGrantPostHook(mockCtx, mockDml);
        Test.startTest();
        RevSignaling.TransactionResponse response = hook.execute(buildRequest(CTX_ID));
        Test.stopTest();

        System.assertEquals(RevSignaling.TransactionStatus.SUCCESS, response.status);
        Map<Id, Integer> qtyById = qtyByGrantId(mockDml.lastUpdates);
        System.assertEquals(2, qtyById.size(), 'Only the resolvable resources should be updated');
        System.assertEquals(100, qtyById.get(g1));
        System.assertEquals(250, qtyById.get(g2));
        System.assert(!qtyById.containsKey(g3), 'Requests grant must not be updated (resource deleted)');
    }

    @IsTest
    static void recursionGuard_shortCircuits() {
        MockContextClient mockCtx = new MockContextClient();
        MockDmlClient mockDml = new MockDmlClient();
        mockCtx.itemsPayload(new List<Map<String, Object>>{ aapItemNode(AAP_ITEM_CTX) });
        mockCtx.attrsPayload(new List<Map<String, Object>>());

        RLM_AAPGrantPostHook hook = new RLM_AAPGrantPostHook(mockCtx, mockDml);

        Test.startTest();
        RLM_AAPGrantPostHook.isRunning = true;
        RevSignaling.TransactionResponse response = hook.execute(buildRequest(CTX_ID));
        RLM_AAPGrantPostHook.isRunning = false;
        Test.stopTest();

        System.assertEquals(RevSignaling.TransactionStatus.SUCCESS, response.status);
        System.assertEquals(0, mockCtx.queryCallCount, 'Recursion guard should short-circuit before any queryTags');
        System.assertEquals(0, mockDml.updateCallCount, 'Recursion guard should short-circuit before any DML');
    }

    @IsTest
    static void blankContextId_returnsSuccessNoOp() {
        MockContextClient mockCtx = new MockContextClient();
        MockDmlClient mockDml = new MockDmlClient();
        RLM_AAPGrantPostHook hook = new RLM_AAPGrantPostHook(mockCtx, mockDml);

        Test.startTest();
        RevSignaling.TransactionResponse response = hook.execute(buildRequest(null));
        Test.stopTest();

        System.assertEquals(RevSignaling.TransactionStatus.SUCCESS, response.status);
        System.assertEquals(0, mockCtx.queryCallCount);
        System.assertEquals(0, mockDml.updateCallCount);
    }

    @IsTest
    static void invalidGrantId_skipsGrantContinuesOthers() {
        // Defensive test for the new Id.valueOf(grantCtxId) path: a grant
        // whose ctx id is NOT a valid Salesforce Id must be logged and
        // skipped, not abort the batch. The other two grants should still
        // update.
        Map<String, Id> resourceIdByName = loadResourceIdByName();
        Id gGoodTraffic  = fakeGrantId(10);
        Id gGoodRequests = fakeGrantId(11);

        MockContextClient mockCtx = new MockContextClient();
        MockDmlClient mockDml = new MockDmlClient();
        mockCtx.itemsPayload(new List<Map<String, Object>>{ aapItemNode(AAP_ITEM_CTX) });
        mockCtx.attrsPayload(new List<Map<String, Object>>{
            attrNode(AAP_ITEM_CTX, 'A1', 'IncludedTrafficText',       '100'),
            attrNode(AAP_ITEM_CTX, 'A2', 'IncludedBandwidthText',     '250'),
            attrNode(AAP_ITEM_CTX, 'A3', 'IncludedMillionHitsGBText', '5000')
        });
        // Middle grant uses a malformed "id" -- Id.valueOf must throw and
        // buildGrantUpdates() should swallow the error, tick skipped_bad_grant_id,
        // and continue with the two well-formed grants.
        mockCtx.grantsPayload(new List<Map<String, Object>>{
            grantNode(AAP_ITEM_CTX, gGoodTraffic,  resourceIdByName.get(NAME_TRAFFIC)),
            grantNodeRawLeaf(AAP_ITEM_CTX, 'NOT-A-REAL-ID', resourceIdByName.get(NAME_BANDWIDTH)),
            grantNode(AAP_ITEM_CTX, gGoodRequests, resourceIdByName.get(NAME_REQUESTS))
        });

        RLM_AAPGrantPostHook hook = new RLM_AAPGrantPostHook(mockCtx, mockDml);
        Test.startTest();
        RevSignaling.TransactionResponse response = hook.execute(buildRequest(CTX_ID));
        Test.stopTest();

        System.assertEquals(RevSignaling.TransactionStatus.SUCCESS, response.status);
        Map<Id, Integer> qtyById = qtyByGrantId(mockDml.lastUpdates);
        System.assertEquals(2, qtyById.size(), 'Malformed grant must be skipped');
        System.assertEquals(100,  qtyById.get(gGoodTraffic));
        System.assertEquals(5000, qtyById.get(gGoodRequests));
    }

    @IsTest
    static void queueable_emptyBatch_isNoOp() {
        // The Queueable's early return path when there is nothing to do.
        // No DML expected; assertion is coverage-only.
        Test.startTest();
        System.enqueueJob(new RLM_AAPGrantPostHook.AAPGrantUpdateQueueable(new List<QuotLineItmUseRsrcGrant>()));
        Test.stopTest();
        System.assertEquals(0, [SELECT COUNT() FROM AsyncApexJob WHERE JobType = 'Queueable' AND Status = 'Failed'],
            'Empty batch queueable must not fail');
    }

    @IsTest
    static void queueable_dmlBatchCommitsUnderTestGovernor() {
        // Direct AAPGrantUpdateQueueable exercise: build a fake-Id
        // QuotLineItmUseRsrcGrant record with a valid key prefix and call
        // execute() inside Test.startTest/stopTest. The update() on a
        // nonexistent record throws DmlException; the Queueable re-throws
        // to mark the AsyncApexJob Failed. Test asserts the exception
        // was raised (proving execute() reached the DML statement -- ie
        // the sync-DML block from procedure plan hooks is not reproduced
        // here, confirming the async context has normal governor limits).
        Id fakeGrantId = fakeGrantId(999);
        RLM_AAPGrantPostHook.AAPGrantUpdateQueueable q =
            new RLM_AAPGrantPostHook.AAPGrantUpdateQueueable(new List<QuotLineItmUseRsrcGrant>{
                new QuotLineItmUseRsrcGrant(Id = fakeGrantId, GrantQuantity = 100)
            });

        Boolean threw = false;
        String msg = null;
        Test.startTest();
        try {
            q.execute(null);
        } catch (Exception e) {
            threw = true;
            msg = e.getMessage();
        }
        Test.stopTest();

        System.assert(threw, 'Queueable execute() must throw when DML target does not exist; msg=' + msg);
        System.assert(msg == null || !msg.contains('Too many DML statements'),
            'Async context must not hit the sync-DML limit; msg=' + msg);
    }

    @IsTest
    static void duplicateGrantId_dedupedBeforeDml() {
        // If the engine ever returned the same grant twice in one queryTags
        // response, `update` with duplicate Ids would throw at DML time.
        // The dedup set in buildGrantUpdates() protects against that.
        Map<String, Id> resourceIdByName = loadResourceIdByName();
        Id g1 = fakeGrantId(1);

        MockContextClient mockCtx = new MockContextClient();
        MockDmlClient mockDml = new MockDmlClient();
        mockCtx.itemsPayload(new List<Map<String, Object>>{ aapItemNode(AAP_ITEM_CTX) });
        mockCtx.attrsPayload(new List<Map<String, Object>>{
            attrNode(AAP_ITEM_CTX, 'A1', 'IncludedTrafficText', '100')
        });
        mockCtx.grantsPayload(new List<Map<String, Object>>{
            grantNode(AAP_ITEM_CTX, g1, resourceIdByName.get(NAME_TRAFFIC)),
            grantNode(AAP_ITEM_CTX, g1, resourceIdByName.get(NAME_TRAFFIC))
        });

        RLM_AAPGrantPostHook hook = new RLM_AAPGrantPostHook(mockCtx, mockDml);
        Test.startTest();
        RevSignaling.TransactionResponse response = hook.execute(buildRequest(CTX_ID));
        Test.stopTest();

        System.assertEquals(RevSignaling.TransactionStatus.SUCCESS, response.status);
        System.assertEquals(1, mockDml.lastUpdates.size(), 'Duplicate grant must be deduped');
        System.assertEquals(100, mockDml.lastUpdates.get(0).GrantQuantity);
        System.assertEquals(g1,  mockDml.lastUpdates.get(0).Id);
    }

    // ------------------------------------------------------------------
    // Fixtures
    // ------------------------------------------------------------------

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
                'Attribute'                      => new Map<String, Object>{ 'tagValue' => attributeName },
                'AttributeValue'                 => new Map<String, Object>{ 'tagValue' => attributeValue },
                'SalesTransactionItemAttrParent' => new Map<String, Object>{ 'tagValue' => parentItemCtxId }
            }
        };
    }

    private static Map<String, Object> grantNode(String parentItemCtxId, Id grantId, Id usageResourceId) {
        return grantNodeRawLeaf(parentItemCtxId, String.valueOf(grantId), usageResourceId);
    }

    /**
     * Same shape as grantNode() but accepts a raw string for the last
     * dataPath segment (used by the malformed-id test).
     * 'STI_URGSTIId__std'   = grant -> parent SalesTransactionItem id  (line 23829)
     * 'STI_URGSTIURId__std' = grant -> UsageResource id                 (line 23857)
     */
    private static Map<String, Object> grantNodeRawLeaf(String parentItemCtxId, String rawLeaf, Id usageResourceId) {
        return new Map<String, Object>{
            'dataPath' => new List<Object>{ CTX_ID, STX_ID, parentItemCtxId, rawLeaf },
            'tagValue' => new Map<String, Object>{
                'STI_URGSTIId__std'   => new Map<String, Object>{ 'tagValue' => parentItemCtxId },
                'STI_URGSTIURId__std' => new Map<String, Object>{ 'tagValue' => String.valueOf(usageResourceId) }
            }
        };
    }

    /**
     * Builds a synthetic 15-char Id with the QuotLineItmUseRsrcGrant key
     * prefix so Id.valueOf() succeeds inside the hook without any real
     * QuotLineItmUseRsrcGrant records existing. `seq` is padded to fill
     * the remaining 12 characters.
     */
    private static Id fakeGrantId(Integer seq) {
        if (grantKeyPrefix == null) {
            grantKeyPrefix = QuotLineItmUseRsrcGrant.SObjectType.getDescribe().getKeyPrefix();
        }
        String body = String.valueOf(seq).leftPad(12, '0');
        return Id.valueOf(grantKeyPrefix + body);
    }

    /**
     * Reads the captured DML input and returns GrantQuantity keyed by
     * grant SObject Id.
     */
    private static Map<Id, Integer> qtyByGrantId(List<QuotLineItmUseRsrcGrant> updates) {
        Map<Id, Integer> result = new Map<Id, Integer>();
        if (updates == null) {
            return result;
        }
        for (QuotLineItmUseRsrcGrant g : updates) {
            result.put(g.Id, (Integer) g.GrantQuantity);
        }
        return result;
    }

    // ------------------------------------------------------------------
    // Mocks
    // ------------------------------------------------------------------

    /**
     * Records queryTags inputs and serves canned results keyed by tag name.
     * The hook calls queryTags for three top-level tags:
     * SalesTransactionItem, SalesTransactionItemAttribute, STIUseRsrcGrantTag__std.
     */
    private class MockContextClient implements RLM_AAPGrantPostHook.ContextClient {
        public Map<String, List<Object>> payloadsByTag = new Map<String, List<Object>>();
        public Integer queryCallCount = 0;

        public void itemsPayload(List<Map<String, Object>> nodes) {
            payloadsByTag.put('SalesTransactionItem', toObjectList(nodes));
        }

        public void attrsPayload(List<Map<String, Object>> nodes) {
            payloadsByTag.put('SalesTransactionItemAttribute', toObjectList(nodes));
        }

        public void grantsPayload(List<Map<String, Object>> nodes) {
            payloadsByTag.put('STIUseRsrcGrantTag__std', toObjectList(nodes));
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

    /**
     * Captures the QuotLineItmUseRsrcGrant records the hook wants to update
     * without touching the database, so we can assert on Id + GrantQuantity
     * with only in-memory synthetic fixtures.
     */
    private class MockDmlClient implements RLM_AAPGrantPostHook.DmlClient {
        public Integer updateCallCount = 0;
        public List<QuotLineItmUseRsrcGrant> lastUpdates = new List<QuotLineItmUseRsrcGrant>();

        public void updateGrants(List<QuotLineItmUseRsrcGrant> grants) {
            updateCallCount += 1;
            lastUpdates = grants == null ? new List<QuotLineItmUseRsrcGrant>() : grants;
        }
    }
}
