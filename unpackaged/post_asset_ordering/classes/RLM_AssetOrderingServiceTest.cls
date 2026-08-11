/**
 * Unit tests for RLM_AssetOrderingService. The native standard-action
 * invocation is replaced through the @TestVisible mockOutcome seam, so these
 * tests exercise request building, contract-group chaining, and result
 * aggregation without invoking live platform actions. End-to-end behavior of
 * the real actions is covered by the Phase 1 live verification (see the feature
 * doc) - a test pass here is NOT a substitute for that.
 */
@IsTest
private class RLM_AssetOrderingServiceTest {

    private static RLM_AssetOrderingService.ConsolidationRequest buildReq(
        String actionType,
        Integer numGroups
    ) {
        RLM_AssetOrderingService.ConsolidationRequest req =
            new RLM_AssetOrderingService.ConsolidationRequest();
        req.actionType = actionType;
        req.outputType = 'Quote';
        req.effectiveDate = Date.today();
        req.quantityChange = 2;
        req.renewalEndDate = Date.today().addYears(1);
        req.groups = new List<RLM_AssetOrderingService.ContractAssetGroup>();
        for (Integer i = 0; i < numGroups; i++) {
            RLM_AssetOrderingService.ContractAssetGroup g =
                new RLM_AssetOrderingService.ContractAssetGroup();
            // Fake asset ids (unused by the mocked action).
            g.assetIds = new List<Id>{ fakeId(Asset.SObjectType) };
            req.groups.add(g);
        }
        return req;
    }

    private static Integer idCounter = 1;
    private static Id fakeId(Schema.SObjectType t) {
        String prefix = t.getDescribe().getKeyPrefix();
        String suffix = String.valueOf(idCounter++).leftPad(12, '0');
        return Id.valueOf(prefix + suffix); // prefix(3) + 12 = valid 15-char Id
    }

    private static RLM_AssetOrderingService.ActionOutcome successOutcome() {
        RLM_AssetOrderingService.ActionOutcome o =
            new RLM_AssetOrderingService.ActionOutcome();
        o.isSuccess = true;
        o.outputRecordId = fakeId(Quote.SObjectType);
        o.requestIdentifier = 'req-123';
        return o;
    }

    @IsTest
    static void runConsolidation_success_chainsAcrossGroups() {
        RLM_AssetOrderingService.mockOutcome = successOutcome();
        Test.startTest();
        RLM_AssetOrderingService.ConsolidationResult res =
            RLM_AssetOrderingService.runConsolidation(buildReq('Amend', 2));
        Test.stopTest();
        System.assert(res.isSuccess, 'Expected success');
        System.assertNotEquals(null, res.outputRecordId, 'Expected a single output record');
        System.assertEquals('Quote', res.outputType);
        System.assertEquals(2, res.requestIdentifiers.size(), 'One request id per chained group');
    }

    @IsTest
    static void runConsolidation_coversAllActionTypes() {
        RLM_AssetOrderingService.mockOutcome = successOutcome();
        Test.startTest();
        for (String a : new List<String>{ 'Amend', 'Upgrade', 'Downgrade', 'Renew', 'Cancel' }) {
            RLM_AssetOrderingService.ConsolidationResult res =
                RLM_AssetOrderingService.runConsolidation(buildReq(a, 1));
            System.assert(res.isSuccess, 'Expected success for ' + a);
        }
        Test.stopTest();
    }

    @IsTest
    static void runConsolidation_failureStopsChain() {
        RLM_AssetOrderingService.ActionOutcome bad =
            new RLM_AssetOrderingService.ActionOutcome();
        bad.isSuccess = false;
        bad.errors.add('boom');
        RLM_AssetOrderingService.mockOutcome = bad;
        Test.startTest();
        RLM_AssetOrderingService.ConsolidationResult res =
            RLM_AssetOrderingService.runConsolidation(buildReq('Amend', 2));
        Test.stopTest();
        System.assert(!res.isSuccess, 'Expected failure');
        System.assert(res.messages.contains('boom'), 'Expected error message propagated');
    }

    @IsTest
    static void runConsolidation_guardsEmptyInput() {
        RLM_AssetOrderingService.ConsolidationResult noAction =
            RLM_AssetOrderingService.runConsolidation(
                new RLM_AssetOrderingService.ConsolidationRequest());
        System.assert(!noAction.isSuccess, 'Blank action should fail');

        RLM_AssetOrderingService.ConsolidationRequest emptyGroups = buildReq('Amend', 0);
        RLM_AssetOrderingService.ConsolidationResult res =
            RLM_AssetOrderingService.runConsolidation(emptyGroups);
        System.assert(!res.isSuccess, 'No groups should fail');
    }

    @IsTest
    static void runConsolidation_withContractGroupsAndSkipsEmpty() {
        RLM_AssetOrderingService.mockOutcome = successOutcome();

        RLM_AssetOrderingService.ConsolidationRequest req =
            new RLM_AssetOrderingService.ConsolidationRequest();
        req.actionType = 'Renew';
        req.outputType = null; // exercise the Quote default
        req.effectiveDate = Date.today();
        req.renewalEndDate = Date.today().addYears(1);
        req.groups = new List<RLM_AssetOrderingService.ContractAssetGroup>();

        // Group with an explicit contract id (covers the *ContractId params).
        RLM_AssetOrderingService.ContractAssetGroup withContract =
            new RLM_AssetOrderingService.ContractAssetGroup();
        withContract.contractId = fakeId(Contract.SObjectType);
        withContract.assetIds = new List<Id>{ fakeId(Asset.SObjectType) };
        req.groups.add(withContract);

        // A null group and an empty-asset group are both skipped.
        req.groups.add(null);
        RLM_AssetOrderingService.ContractAssetGroup empty =
            new RLM_AssetOrderingService.ContractAssetGroup();
        empty.assetIds = new List<Id>();
        req.groups.add(empty);

        Test.startTest();
        RLM_AssetOrderingService.ConsolidationResult res =
            RLM_AssetOrderingService.runConsolidation(req);
        Test.stopTest();

        System.assert(res.isSuccess, 'Expected success');
        System.assertEquals('Quote', res.outputType, 'Blank output type defaults to Quote');
        System.assertEquals(1, res.requestIdentifiers.size(), 'Only the non-empty group runs');
    }

    @IsTest
    static void runConsolidation_cancelWithContractGroup() {
        RLM_AssetOrderingService.mockOutcome = successOutcome();
        RLM_AssetOrderingService.ConsolidationRequest req = buildReq('Cancel', 1);
        req.groups[0].contractId = fakeId(Contract.SObjectType);
        Test.startTest();
        RLM_AssetOrderingService.ConsolidationResult res =
            RLM_AssetOrderingService.runConsolidation(req);
        Test.stopTest();
        System.assert(res.isSuccess, 'Cancel with contract group should succeed');
    }

    @IsTest
    static void runConsolidation_successButNoOutputRecord() {
        RLM_AssetOrderingService.ActionOutcome noOutput =
            new RLM_AssetOrderingService.ActionOutcome();
        noOutput.isSuccess = true;
        noOutput.outputRecordId = null; // action reported success but produced nothing
        RLM_AssetOrderingService.mockOutcome = noOutput;
        Test.startTest();
        RLM_AssetOrderingService.ConsolidationResult res =
            RLM_AssetOrderingService.runConsolidation(buildReq('Amend', 1));
        Test.stopTest();
        System.assert(!res.isSuccess, 'No output record should fail the result');
        System.assert(
            res.messages.contains('No output record was produced by the lifecycle action.'),
            'Expected no-output message');
    }

    @IsTest
    static void runConsolidation_noMockDefaultsToFailure() {
        // With no mockOutcome injected, the in-test seam returns a deterministic
        // failure (it never invokes the live standard action) - covers that guard.
        RLM_AssetOrderingService.mockOutcome = null;
        Test.startTest();
        RLM_AssetOrderingService.ConsolidationResult res =
            RLM_AssetOrderingService.runConsolidation(buildReq('Amend', 1));
        Test.stopTest();
        System.assert(!res.isSuccess, 'Missing mock outcome should fail in tests');
    }

    @IsTest
    static void runConsolidation_unsupportedActionThrows() {
        RLM_AssetOrderingService.mockOutcome = successOutcome();
        Boolean threw = false;
        try {
            RLM_AssetOrderingService.runConsolidation(buildReq('Teleport', 1));
        } catch (RLM_AssetOrderingService.AssetOrderingException e) {
            threw = true;
        }
        System.assert(threw, 'Unsupported action should throw AssetOrderingException');
    }
}
