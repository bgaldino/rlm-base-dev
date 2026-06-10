@IsTest
private class RLM_ExpressionSetManagerControllerTest {

    // Fake Ids for read-only paths that should return empty results without
    // matching any platform records. RLM Setup-object records (ContextDefinition,
    // ExpressionSetDefinition, etc.) cannot be inserted via Apex DML, so all
    // coverage uses no-results data paths plus mocked HTTP responses for the
    // queueables.
    private static final Id FAKE_CONTEXT_ID = '11O000000000000AAA';
    private static final Id FAKE_DEF_ID = '11N000000000000AAA';

    @IsTest
    static void getContextDefinitions_returnsList() {
        List<RLM_ExpressionSetManagerController.ContextDefinitionWrapper> results =
            RLM_ExpressionSetManagerController.getContextDefinitions();
        System.assertNotEquals(null, results, 'Should return a non-null list');
    }

    @IsTest
    static void getLinkedExpressionSets_unknownContext_returnsNonNull() {
        // An unknown context returns no linked rows, but the method also surfaces
        // unlinked Constraint ExpressionSets — count varies by org, so we only
        // assert the call succeeds and every row is flagged isLinked = false.
        List<RLM_ExpressionSetManagerController.ExpressionSetInfo> results =
            RLM_ExpressionSetManagerController.getLinkedExpressionSets(FAKE_CONTEXT_ID);
        System.assertNotEquals(null, results, 'Should return a non-null list');
        for (RLM_ExpressionSetManagerController.ExpressionSetInfo info : results) {
            System.assertEquals(false, info.isLinked,
                'Unknown context cannot have any linked rows');
        }
    }

    @IsTest
    static void getActiveJobStatus_noJobs_returnsNone() {
        String status = RLM_ExpressionSetManagerController.getActiveJobStatus();
        System.assertEquals('none', status, 'No prior jobs should yield none');
    }

    @IsTest
    static void getDeactivateStatus_noVersions_returnsComplete() {
        String status = RLM_ExpressionSetManagerController.getDeactivateStatus(
            FAKE_CONTEXT_ID, new List<Id>{ FAKE_DEF_ID }
        );
        System.assertEquals('complete', status, 'No active versions and no junctions implies complete');
    }

    @IsTest
    static void getActivateStatus_noJunctions_returnsInProgress() {
        String status = RLM_ExpressionSetManagerController.getActivateStatus(
            FAKE_CONTEXT_ID, new List<Id>{ FAKE_DEF_ID }
        );
        System.assertEquals('in_progress', status, 'Missing junctions should report in_progress');
    }

    @IsTest
    static void deactivateExpressionSets_noData_runsQueueableWithoutCallout() {
        Test.setMock(HttpCalloutMock.class, new CompositeMock());
        Test.startTest();
        RLM_ExpressionSetManagerController.deactivateExpressionSets(
            FAKE_CONTEXT_ID, new List<Id>{ FAKE_DEF_ID }
        );
        Test.stopTest();
        // No ExpressionSet records for the fake def → queueable exits cleanly without callouts.
    }

    @IsTest
    static void activateExpressionSets_noData_runsQueueableWithoutCallout() {
        Test.setMock(HttpCalloutMock.class, new CompositeMock());
        Test.startTest();
        RLM_ExpressionSetManagerController.activateExpressionSets(
            FAKE_CONTEXT_ID, new List<Id>{ FAKE_DEF_ID }
        );
        Test.stopTest();
        // No matching versions/junctions → queueable exits cleanly without callouts.
    }

    /**
     * Returns a successful Composite REST response shape so any callout
     * triggered by the queueables (none expected with empty seed data, but
     * defensive) does not throw.
     */
    private class CompositeMock implements HttpCalloutMock {
        public HttpResponse respond(HttpRequest req) {
            HttpResponse res = new HttpResponse();
            res.setHeader('Content-Type', 'application/json');
            res.setStatusCode(200);
            res.setBody('{"compositeResponse":[]}');
            return res;
        }
    }
}
