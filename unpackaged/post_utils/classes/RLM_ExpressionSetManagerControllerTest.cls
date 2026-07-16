@IsTest
private class RLM_ExpressionSetManagerControllerTest {

    // Fake Ids for read-only paths that should return empty results without
    // matching any platform records. RLM Setup-object records (ContextDefinition,
    // ExpressionSetDefinition, etc.) cannot be inserted via Apex DML, so all
    // coverage uses no-results data paths plus mocked HTTP responses for the
    // queueables.
    private static final Id FAKE_CONTEXT_ID = '11O000000000000AAA';
    private static final Id FAKE_DEF_ID = '11N000000000000AAA';
    private static final Id FAKE_JOB_ID = '707000000000000AAA';

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
    static void getJobStatus_unknownJob_returnsUnknown() {
        RLM_ExpressionSetManagerController.JobStatus status =
            RLM_ExpressionSetManagerController.getJobStatus(FAKE_JOB_ID);
        System.assertEquals('unknown', status.state, 'Unknown job id should not be treated as running');
        System.assertNotEquals(null, status.message, 'Unknown status should explain the missing job');
    }

    @IsTest
    static void getJobStatus_nullJob_returnsUnknown() {
        RLM_ExpressionSetManagerController.JobStatus status =
            RLM_ExpressionSetManagerController.getJobStatus(null);
        System.assertEquals('unknown', status.state, 'Null job id should not be treated as running');
        System.assertNotEquals(null, status.message, 'Unknown status should explain the missing job');
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
    static void deactivateExpressionSets_unscopedDefinition_rejected() {
        try {
            RLM_ExpressionSetManagerController.deactivateExpressionSets(
                FAKE_CONTEXT_ID, new List<Id>{ FAKE_DEF_ID }
            );
            System.assert(false, 'Unscoped definition ids should be rejected before enqueue');
        } catch (AuraHandledException e) {
            System.assertNotEquals(null, e, 'Expected deactivate scope rejection');
        }
    }

    @IsTest
    static void activateExpressionSets_unscopedDefinition_rejected() {
        try {
            RLM_ExpressionSetManagerController.activateExpressionSets(
                FAKE_CONTEXT_ID, new List<Id>{ FAKE_DEF_ID }
            );
            System.assert(false, 'Unscoped definition ids should be rejected before enqueue');
        } catch (AuraHandledException e) {
            System.assertNotEquals(null, e, 'Expected activate scope rejection');
        }
    }

    @IsTest
    static void normalizeDefinitionIds_rejectsEmptySelection() {
        try {
            RLM_ExpressionSetManagerController.normalizeDefinitionIds(new List<Id>());
            System.assert(false, 'Empty selections should be rejected');
        } catch (AuraHandledException e) {
            System.assertNotEquals(null, e, 'Expected empty-selection rejection');
        }
    }

    @IsTest
    static void normalizeDefinitionIds_dedupesSelection() {
        List<Id> normalized = RLM_ExpressionSetManagerController.normalizeDefinitionIds(
            new List<Id>{ FAKE_DEF_ID, FAKE_DEF_ID }
        );
        System.assertEquals(1, normalized.size(), 'Duplicate ids should be removed');
        System.assertEquals(FAKE_DEF_ID, normalized[0], 'The selected id should be preserved');
    }

    @IsTest
    static void dtoConstructors_mapFields() {
        ExpressionSetDefinition def = new ExpressionSetDefinition(
            DeveloperName = 'Test_Definition',
            MasterLabel = 'Test Definition'
        );
        ExpressionSetVersion version = new ExpressionSetVersion(
            VersionNumber = 2,
            IsActive = true,
            Rank = 1
        );

        RLM_ExpressionSetManagerController.ExpressionSetInfo info =
            new RLM_ExpressionSetManagerController.ExpressionSetInfo(
                def,
                null,
                'Constraint',
                version,
                true,
                true
            );

        System.assertEquals(null, info.definitionId, 'Unset in-memory ids should map through as null');
        System.assertEquals('Test_Definition', info.developerName, 'Developer name should map through');
        System.assertEquals(2, info.latestVersionNumber, 'Latest version number should map through');
        System.assertEquals(1, info.versions.size(), 'Compatibility version list should include latest version');
        System.assertEquals(2, info.versions[0].versionNumber, 'Compatibility version number should map through');
    }

    @IsTest
    static void deactivateQueueable_noData_runsWithoutCallout() {
        Test.setMock(HttpCalloutMock.class, new CompositeMock());
        new RLM_ExpressionSetManagerController.DeactivateQueueable(
            FAKE_CONTEXT_ID,
            new List<Id>{ FAKE_DEF_ID },
            new Set<Id>(),
            'fake-session-id'
        ).execute(null);
        // No ExpressionSet records for the fake def → queueable exits cleanly without callouts.
    }

    @IsTest
    static void activateQueueable_noData_runsWithoutCallout() {
        Test.setMock(HttpCalloutMock.class, new CompositeMock());
        new RLM_ExpressionSetManagerController.ActivateQueueable(
            FAKE_CONTEXT_ID,
            new List<Id>{ FAKE_DEF_ID },
            new Set<Id>(),
            'fake-session-id'
        ).execute(null);
        // No matching versions/junctions → queueable exits cleanly without callouts.
    }

    @IsTest
    static void activateQueueable_missingJunction_sendsCompositeCallout() {
        RecordingHttpMock mock = new RecordingHttpMock();
        Test.setMock(HttpCalloutMock.class, mock);
        new RLM_ExpressionSetManagerController.ActivateQueueable(
            FAKE_CONTEXT_ID,
            new List<Id>{ FAKE_DEF_ID },
            new Set<Id>{ FAKE_DEF_ID },
            'fake-session-id'
        ).execute(null);

        // Assert the junction POST actually went out and carried the right ids —
        // otherwise the test would pass even if the callout were removed.
        System.assertEquals(1, mock.requests.size(),
            'Expected exactly one composite callout for the junction POST');
        HttpRequest captured = mock.requests[0];
        System.assert(captured.getEndpoint().endsWith('/composite'),
            'Callout should target the Composite REST endpoint: ' + captured.getEndpoint());
        System.assertEquals('POST', captured.getMethod(), 'Composite request should be a POST');
        String body = captured.getBody();
        System.assert(body.contains('ExpressionSetDefinitionContextDefinition'),
            'Composite body should POST the context-definition junction: ' + body);
        System.assert(body.contains(String.valueOf(FAKE_DEF_ID)),
            'Composite body should carry the Expression Set Definition id');
        System.assert(body.contains(String.valueOf(FAKE_CONTEXT_ID)),
            'Composite body should carry the Context Definition id');
    }

    @IsTest
    static void compositeSubrequestFailure_throws() {
        try {
            RLM_ExpressionSetManagerController.assertNoCompositeSubrequestFailures(
                '{"compositeResponse":[{"httpStatusCode":400,"body":[{"message":"bad request"}]}]}'
            );
            System.assert(false, 'Failed composite subrequests should throw');
        } catch (CalloutException e) {
            System.assert(e.getMessage().contains('Composite subrequest'),
                'Expected composite subrequest failure: ' + e.getMessage());
        }
    }

    @IsTest
    static void compositeSubrequestSuccess_doesNotThrow() {
        RLM_ExpressionSetManagerController.assertNoCompositeSubrequestFailures(
            '{"compositeResponse":[{"httpStatusCode":204}]}'
        );
    }

    @IsTest
    static void compositeDeleteFailure_throws() {
        try {
            RLM_ExpressionSetManagerController.assertNoCompositeDeleteFailures(
                '[{"id":null,"success":false,"errors":[{"message":"delete failed"}]}]'
            );
            System.assert(false, 'Failed composite deletes should throw');
        } catch (CalloutException e) {
            System.assert(e.getMessage().contains('Composite delete'),
                'Expected composite delete failure: ' + e.getMessage());
        }
    }

    @IsTest
    static void compositeDeleteSuccess_doesNotThrow() {
        RLM_ExpressionSetManagerController.assertNoCompositeDeleteFailures(
            '[{"id":"a00000000000000AAA","success":true,"errors":[]}]'
        );
    }

    @IsTest
    static void sendCompositeInChunks_successfulResponses_doNotThrow() {
        Test.setMock(HttpCalloutMock.class, new CompositeMock());
        List<Object> subrequests = new List<Object>();
        for (Integer i = 0; i < 26; i++) {
            subrequests.add(new Map<String, Object>{
                'method' => 'PATCH',
                'url' => '/services/data/v67.0/sobjects/ExpressionSetVersion/a00000000000000AAA',
                'referenceId' => 'patch_' + i,
                'body' => new Map<String, Object>{ 'IsActive' => true }
            });
        }

        RLM_ExpressionSetManagerController.sendCompositeInChunks(
            'https://example.my.salesforce.com',
            'fake-session-id',
            subrequests
        );
    }

    @IsTest
    static void sendCompositeInChunks_httpFailure_throws() {
        Test.setMock(HttpCalloutMock.class, new HttpFailureMock());
        try {
            RLM_ExpressionSetManagerController.sendCompositeInChunks(
                'https://example.my.salesforce.com',
                'fake-session-id',
                new List<Object>{ new Map<String, Object>{ 'method' => 'PATCH', 'url' => '/services/data/v67.0/sobjects/ExpressionSetVersion/a00000000000000AAA' } }
            );
            System.assert(false, 'HTTP failures should throw');
        } catch (CalloutException e) {
            System.assert(e.getMessage().contains('Composite request failed'),
                'Expected HTTP-level composite failure: ' + e.getMessage());
        }
    }

    @IsTest
    static void deleteRecords_successfulResponses_doNotThrow() {
        Test.setMock(HttpCalloutMock.class, new DeleteSuccessMock());
        RLM_ExpressionSetManagerController.deleteRecords(
            'https://example.my.salesforce.com',
            'fake-session-id',
            new List<String>{ 'a00000000000000AAA' }
        );
    }

    @IsTest
    static void deleteRecords_httpFailure_throws() {
        Test.setMock(HttpCalloutMock.class, new HttpFailureMock());
        try {
            RLM_ExpressionSetManagerController.deleteRecords(
                'https://example.my.salesforce.com',
                'fake-session-id',
                new List<String>{ 'a00000000000000AAA' }
            );
            System.assert(false, 'HTTP failures should throw');
        } catch (CalloutException e) {
            System.assert(e.getMessage().contains('Composite delete failed'),
                'Expected HTTP-level delete failure: ' + e.getMessage());
        }
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

    /**
     * Records each HttpRequest so a test can assert a callout occurred and
     * inspect its method, endpoint, and body. Returns a successful composite
     * response so the queueable does not throw.
     */
    private class RecordingHttpMock implements HttpCalloutMock {
        public List<HttpRequest> requests = new List<HttpRequest>();
        public HttpResponse respond(HttpRequest req) {
            requests.add(req);
            HttpResponse res = new HttpResponse();
            res.setHeader('Content-Type', 'application/json');
            res.setStatusCode(200);
            res.setBody('{"compositeResponse":[{"httpStatusCode":201,"referenceId":"junction_0"}]}');
            return res;
        }
    }

    private class DeleteSuccessMock implements HttpCalloutMock {
        public HttpResponse respond(HttpRequest req) {
            HttpResponse res = new HttpResponse();
            res.setHeader('Content-Type', 'application/json');
            res.setStatusCode(200);
            res.setBody('[{"id":"a00000000000000AAA","success":true,"errors":[]}]');
            return res;
        }
    }

    private class HttpFailureMock implements HttpCalloutMock {
        public HttpResponse respond(HttpRequest req) {
            HttpResponse res = new HttpResponse();
            res.setHeader('Content-Type', 'application/json');
            res.setStatusCode(500);
            res.setBody('{"message":"server error"}');
            return res;
        }
    }
}
