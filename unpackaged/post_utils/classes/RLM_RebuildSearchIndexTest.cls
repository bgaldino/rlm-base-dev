/**
 * Tests for RLM_RebuildSearchIndex: the PCM index deploy callout, its request shape, and
 * how each response (success with and without index details, HTTP error, unparseable body,
 * transport failure) maps onto the LWC result map and the invocable result. The unparseable
 * success body is tested on the LWC path only; the invocable reports it through the same
 * catch as a transport failure, which is tested.
 *
 * The invocable sends one deploy per distinct buildType (not one per request), so a batch of
 * identical requests makes one callout and gets one result each. The request's buildType is
 * forwarded; a blank value falls back to FULL, and an unknown value is rejected with a failed
 * result and no callout. The activation type is always IMMEDIATE, the only documented value.
 *
 * Not covered: getApiSessionId's non-test path (Page.RLM_SessionId.getContent()), which
 * Test.isRunningTest() makes unreachable.
 */
@IsTest
private with sharing class RLM_RebuildSearchIndexTest {

    // The class pins an API version in its path; match around it so a version bump there does
    // not break this test.
    private static final String API_PREFIX = '/services/data/v';
    private static final String PCM_INDEX_SUFFIX = '/connect/pcm/index/deploy';

    private static final String FULL_SUCCESS_BODY =
        '{"snapshot":{' +
            '"id":"0XSxx0000000001",' +
            '"activationStatus":"InProgress",' +
            '"activationType":"IMMEDIATE",' +
            '"snapshotIndexes":[' +
                '{"id":"1XIxx0000000001","indexBuildType":"FULL","indexType":"PRODUCT","lastBuildStatus":"Queued"},' +
                // Differs from the first entry in every field, so reading the wrong entry fails.
                '{"id":"1XIxx0000000002","indexBuildType":"INCREMENTAL","indexType":"OTHER","lastBuildStatus":"Completed"}' +
            ']' +
        '}}';

    /**
     * Returns a canned response (or throws) and records the request it was sent, so tests can
     * assert both what the class sends and how it reads the answer.
     */
    private with sharing class PcmDeployMock implements HttpCalloutMock {
        private final Integer statusCode;
        private final String status;
        private final String body;
        private final Boolean throwCalloutError;
        public final List<HttpRequest> received = new List<HttpRequest>();

        public PcmDeployMock(Integer statusCode, String status, String body) {
            this.statusCode = statusCode;
            this.status = status;
            this.body = body;
            this.throwCalloutError = false;
        }

        /** A mock whose every callout throws a CalloutException; built only by throwingMock(). */
        private PcmDeployMock() {
            this.statusCode = null;
            this.status = null;
            this.body = null;
            this.throwCalloutError = true;
        }

        public HttpResponse respond(HttpRequest req) {
            received.add(req);
            if (throwCalloutError) {
                throw new CalloutException('Simulated transport failure');
            }
            HttpResponse res = new HttpResponse();
            res.setStatusCode(statusCode);
            res.setStatus(status);
            res.setHeader('Content-Type', 'application/json');
            res.setBody(body);
            return res;
        }
    }

    /** A mock whose callouts fail at the transport level, before any HTTP response exists. */
    private static PcmDeployMock throwingMock() {
        return new PcmDeployMock();
    }

    // ─── deployIndex (LWC) ──────────────────────────────────────────────

    @IsTest
    static void deployIndexSendsFullImmediateBuildRequest() {
        PcmDeployMock mock = new PcmDeployMock(201, 'Created', FULL_SUCCESS_BODY);
        Test.setMock(HttpCalloutMock.class, mock);

        Test.startTest();
        RLM_RebuildSearchIndex.deployIndex();
        Test.stopTest();

        Assert.areEqual(1, mock.received.size(), 'Exactly one callout is made per deploy');
        HttpRequest sent = mock.received[0];
        Assert.areEqual('POST', sent.getMethod(), 'The index deploy is a POST');
        Assert.isTrue(
            sent.getEndpoint().startsWith(URL.getOrgDomainUrl().toExternalForm() + API_PREFIX),
            'The callout targets the org domain REST API: ' + sent.getEndpoint()
        );
        Assert.isTrue(
            sent.getEndpoint().endsWith(PCM_INDEX_SUFFIX),
            'The callout targets the PCM index deploy resource: ' + sent.getEndpoint()
        );
        Assert.areEqual('application/json', sent.getHeader('Content-Type'), 'The body is JSON');
        Assert.areEqual(
            'Bearer fake-session-id',
            sent.getHeader('Authorization'),
            'The test-context session id is sent as a bearer token'
        );

        Map<String, Object> body = (Map<String, Object>) JSON.deserializeUntyped(sent.getBody());
        Assert.areEqual('FULL', body.get('buildType'), 'A full build is requested');
        Map<String, Object> snapshot = (Map<String, Object>) body.get('snapshot');
        Assert.isNotNull(snapshot, 'The request body has a snapshot object');
        Assert.areEqual('IMMEDIATE', snapshot.get('activationType'), 'The snapshot activates immediately');
    }

    @IsTest
    static void deployIndexMapsSuccessResponseIncludingFirstIndex() {
        Test.setMock(HttpCalloutMock.class, new PcmDeployMock(201, 'Created', FULL_SUCCESS_BODY));

        Test.startTest();
        Map<String, Object> result = RLM_RebuildSearchIndex.deployIndex();
        Test.stopTest();

        Assert.areEqual(true, result.get('isSuccess'), 'A 201 is a success');
        Assert.areEqual('201', result.get('statusCode'), 'The status code is reported as text');
        Assert.areEqual('PCM Index deployment initiated successfully', result.get('message'), 'Success message');
        Assert.areEqual('0XSxx0000000001', result.get('snapshotId'), 'Snapshot id is read from the response');
        Assert.areEqual('InProgress', result.get('activationStatus'), 'Activation status is read from the response');
        Assert.areEqual('IMMEDIATE', result.get('activationType'), 'Activation type is read from the response');
        Assert.areEqual('1XIxx0000000001', result.get('indexId'), 'Only the FIRST snapshot index is reported');
        Assert.areEqual('FULL', result.get('indexBuildType'), 'Index build type comes from the first index');
        Assert.areEqual('PRODUCT', result.get('indexType'), 'Index type comes from the first index');
        Assert.areEqual('Queued', result.get('lastBuildStatus'), 'Last build status comes from the first index');
    }

    @IsTest
    static void deployIndexOmitsIndexDetailsWhenResponseHasNone() {
        String body = '{"snapshot":{"id":"0XSxx0000000003","activationStatus":"Completed","activationType":"IMMEDIATE"}}';
        Test.setMock(HttpCalloutMock.class, new PcmDeployMock(200, 'OK', body));

        Test.startTest();
        Map<String, Object> result = RLM_RebuildSearchIndex.deployIndex();
        Test.stopTest();

        Assert.areEqual(true, result.get('isSuccess'), 'A 200 is a success');
        Assert.areEqual('200', result.get('statusCode'), 'The status code is reported as text');
        Assert.areEqual('0XSxx0000000003', result.get('snapshotId'), 'Snapshot id is still reported');
        Assert.isFalse(result.containsKey('indexId'), 'No snapshotIndexes means no index id key');
        Assert.isFalse(result.containsKey('indexBuildType'), 'No snapshotIndexes means no build type key');
        Assert.isFalse(result.containsKey('indexType'), 'No snapshotIndexes means no index type key');
        Assert.isFalse(result.containsKey('lastBuildStatus'), 'No snapshotIndexes means no build status key');
    }

    @IsTest
    static void deployIndexOmitsIndexDetailsWhenIndexListIsEmpty() {
        String body = '{"snapshot":{"id":"0XSxx0000000004","activationStatus":"InProgress",' +
            '"activationType":"IMMEDIATE","snapshotIndexes":[]}}';
        Test.setMock(HttpCalloutMock.class, new PcmDeployMock(201, 'Created', body));

        Test.startTest();
        Map<String, Object> result = RLM_RebuildSearchIndex.deployIndex();
        Test.stopTest();

        Assert.areEqual(true, result.get('isSuccess'), 'An empty index list is still a success');
        Assert.isFalse(result.containsKey('indexId'), 'An empty snapshotIndexes list yields no index id');
    }

    @IsTest
    static void deployIndexReportsHttpErrorWithoutThrowing() {
        Test.setMock(
            HttpCalloutMock.class,
            new PcmDeployMock(500, 'Internal Server Error', '[{"errorCode":"UNKNOWN_EXCEPTION"}]')
        );

        Test.startTest();
        Map<String, Object> result = RLM_RebuildSearchIndex.deployIndex();
        Test.stopTest();

        Assert.areEqual(false, result.get('isSuccess'), 'A 500 is not a success');
        Assert.areEqual('500', result.get('statusCode'), 'The failing status code is reported');
        Assert.areEqual(RLM_RebuildSearchIndex.DEPLOY_NOT_ACCEPTED_MESSAGE, result.get('message'),
            'The message is a fixed sentence; the response body goes to the debug log only');
        Assert.isFalse(result.containsKey('snapshotId'), 'A failed call reports no snapshot');
    }

    @IsTest
    static void deployIndexWrapsTransportFailureInAuraHandledException() {
        PcmDeployMock mock = throwingMock();
        Test.setMock(HttpCalloutMock.class, mock);

        Test.startTest();
        Boolean threw = false;
        try {
            RLM_RebuildSearchIndex.deployIndex();
        } catch (AuraHandledException e) {
            threw = true;
            Assert.areEqual(RLM_RebuildSearchIndex.DEPLOY_FAILED_MESSAGE, e.getMessage(),
                'The LWC gets a fixed sentence, not the callout exception text');
            Assert.isNotNull(e.getCause(), 'The callout exception is kept as the cause');
        }
        Test.stopTest();

        Assert.isTrue(threw, 'A callout failure surfaces to the LWC as an AuraHandledException');
        Assert.areEqual(1, mock.received.size(), 'The exception came from the one callout attempt');
    }

    @IsTest
    static void deployIndexWrapsUnparseableSuccessBodyInAuraHandledException() {
        PcmDeployMock mock = new PcmDeployMock(200, 'OK', 'not json');
        Test.setMock(HttpCalloutMock.class, mock);

        Test.startTest();
        Boolean threw = false;
        try {
            RLM_RebuildSearchIndex.deployIndex();
        } catch (AuraHandledException e) {
            threw = true;
        }
        Test.stopTest();

        Assert.isTrue(threw, 'A 200 whose body is not JSON surfaces as an AuraHandledException');
        Assert.areEqual(1, mock.received.size(), 'The callout was made; the failure is in reading its body');
    }

    // ─── deployPCMIndex (invocable) ─────────────────────────────────────

    @IsTest
    static void deployPcmIndexReturnsOneMappedResultPerRequest() {
        PcmDeployMock mock = new PcmDeployMock(201, 'Created', FULL_SUCCESS_BODY);
        Test.setMock(HttpCalloutMock.class, mock);

        List<RLM_RebuildSearchIndex.PCMDeployRequest> requests = new List<RLM_RebuildSearchIndex.PCMDeployRequest>{
            new RLM_RebuildSearchIndex.PCMDeployRequest(),
            new RLM_RebuildSearchIndex.PCMDeployRequest()
        };

        Test.startTest();
        List<RLM_RebuildSearchIndex.PCMDeployResult> results = RLM_RebuildSearchIndex.deployPCMIndex(requests);
        Test.stopTest();

        Assert.areEqual(2, results.size(), 'One result per request');
        Assert.areEqual(1, mock.received.size(), 'Identical requests share one deploy callout');
        for (RLM_RebuildSearchIndex.PCMDeployResult r : results) {
            Assert.areEqual(true, r.isSuccess, 'Each request succeeds');
            Assert.areEqual('201', r.statusCode, 'Status code is mapped');
            Assert.areEqual('PCM Index deployment initiated successfully', r.message, 'Message is mapped');
            Assert.areEqual('0XSxx0000000001', r.snapshotId, 'Snapshot id is mapped');
            Assert.areEqual('InProgress', r.activationStatus, 'Activation status is mapped');
            Assert.areEqual('IMMEDIATE', r.activationType, 'Activation type is mapped');
            Assert.areEqual('1XIxx0000000001', r.indexId, 'Index id is mapped');
            Assert.areEqual('FULL', r.indexBuildType, 'Index build type is mapped');
            Assert.areEqual('PRODUCT', r.indexType, 'Index type is mapped');
            Assert.areEqual('Queued', r.lastBuildStatus, 'Last build status is mapped');
        }
    }

    // activationType has one documented value (IMMEDIATE), so forwarding it cannot be told apart
    // from the fallback; only the build type is proven here.
    @IsTest
    static void deployPcmIndexForwardsRequestBuildType() {
        PcmDeployMock mock = new PcmDeployMock(201, 'Created', FULL_SUCCESS_BODY);
        Test.setMock(HttpCalloutMock.class, mock);

        RLM_RebuildSearchIndex.PCMDeployRequest request = new RLM_RebuildSearchIndex.PCMDeployRequest();
        request.buildType = ' incremental ';

        Test.startTest();
        RLM_RebuildSearchIndex.deployPCMIndex(new List<RLM_RebuildSearchIndex.PCMDeployRequest>{ request });
        Test.stopTest();

        Assert.areEqual(1, mock.received.size(), 'One callout for one request');
        Map<String, Object> body = (Map<String, Object>) JSON.deserializeUntyped(mock.received[0].getBody());
        Assert.areEqual('INCREMENTAL', body.get('buildType'), 'The request\'s buildType is trimmed and upper-cased before it is sent');
    }

    // An undocumented buildType is rejected: a failed result and no callout, never a silent FULL.
    @IsTest
    static void deployPcmIndexRejectsAnUnknownBuildType() {
        PcmDeployMock mock = new PcmDeployMock(201, 'Created', FULL_SUCCESS_BODY);
        Test.setMock(HttpCalloutMock.class, mock);

        RLM_RebuildSearchIndex.PCMDeployRequest bad = new RLM_RebuildSearchIndex.PCMDeployRequest();
        bad.buildType = 'PARTIAL';

        Test.startTest();
        List<RLM_RebuildSearchIndex.PCMDeployResult> results = RLM_RebuildSearchIndex.deployPCMIndex(
            new List<RLM_RebuildSearchIndex.PCMDeployRequest>{ bad, new RLM_RebuildSearchIndex.PCMDeployRequest() }
        );
        Test.stopTest();

        Assert.areEqual(2, results.size(), 'One result per request');
        Assert.areEqual(false, results[0].isSuccess, 'The unknown buildType is a failed result');
        Assert.isTrue(results[0].message.contains('PARTIAL') && results[0].message.contains('FULL or INCREMENTAL'),
            'The message names the rejected value and the allowed ones: ' + results[0].message);
        Assert.areEqual(true, results[1].isSuccess, 'The valid request in the same batch still runs');
        Assert.areEqual(1, mock.received.size(), 'Only the valid request makes a callout');
    }

    @IsTest
    static void deployPcmIndexDefaultsBlankBuildType() {
        PcmDeployMock mock = new PcmDeployMock(201, 'Created', FULL_SUCCESS_BODY);
        Test.setMock(HttpCalloutMock.class, mock);

        RLM_RebuildSearchIndex.PCMDeployRequest request = new RLM_RebuildSearchIndex.PCMDeployRequest();
        request.buildType = null;
        request.activationType = 'DEFERRED';

        Test.startTest();
        RLM_RebuildSearchIndex.deployPCMIndex(new List<RLM_RebuildSearchIndex.PCMDeployRequest>{ request });
        Test.stopTest();

        Map<String, Object> body = (Map<String, Object>) JSON.deserializeUntyped(mock.received[0].getBody());
        Assert.areEqual('FULL', body.get('buildType'), 'A blank buildType falls back to FULL');
        Assert.areEqual('IMMEDIATE', ((Map<String, Object>) body.get('snapshot')).get('activationType'),
            'Any activationType is sent as IMMEDIATE, the only documented value');
    }

    @IsTest
    static void deployPcmIndexMakesOneCalloutPerDistinctBuildType() {
        PcmDeployMock mock = new PcmDeployMock(201, 'Created', FULL_SUCCESS_BODY);
        Test.setMock(HttpCalloutMock.class, mock);

        RLM_RebuildSearchIndex.PCMDeployRequest incremental = new RLM_RebuildSearchIndex.PCMDeployRequest();
        incremental.buildType = 'INCREMENTAL';

        Test.startTest();
        List<RLM_RebuildSearchIndex.PCMDeployResult> results = RLM_RebuildSearchIndex.deployPCMIndex(
            new List<RLM_RebuildSearchIndex.PCMDeployRequest>{
                new RLM_RebuildSearchIndex.PCMDeployRequest(),
                incremental,
                new RLM_RebuildSearchIndex.PCMDeployRequest()
            }
        );
        Test.stopTest();

        Assert.areEqual(3, results.size(), 'One result per request');
        Assert.areEqual(2, mock.received.size(), 'FULL (twice) and INCREMENTAL: two callouts');
    }

    @IsTest
    static void deployPcmIndexReportsHttpErrorAsFailedResult() {
        Test.setMock(HttpCalloutMock.class, new PcmDeployMock(400, 'Bad Request', 'bad request body'));

        Test.startTest();
        List<RLM_RebuildSearchIndex.PCMDeployResult> results = RLM_RebuildSearchIndex.deployPCMIndex(
            new List<RLM_RebuildSearchIndex.PCMDeployRequest>{ new RLM_RebuildSearchIndex.PCMDeployRequest() }
        );
        Test.stopTest();

        Assert.areEqual(1, results.size(), 'One result for one request');
        Assert.areEqual(false, results[0].isSuccess, 'A 400 is a failed result');
        Assert.areEqual('400', results[0].statusCode, 'The failing status code is mapped');
        Assert.areEqual(RLM_RebuildSearchIndex.DEPLOY_NOT_ACCEPTED_MESSAGE, results[0].message,
            'A deploy that was not accepted maps to the fixed sentence, not the response body');
        Assert.isNull(results[0].snapshotId, 'No snapshot id on failure');
        Assert.isNull(results[0].indexId, 'No index id on failure');
    }

    @IsTest
    static void deployPcmIndexCatchesTransportFailurePerRequest() {
        PcmDeployMock mock = throwingMock();
        Test.setMock(HttpCalloutMock.class, mock);

        Test.startTest();
        List<RLM_RebuildSearchIndex.PCMDeployResult> results = RLM_RebuildSearchIndex.deployPCMIndex(
            new List<RLM_RebuildSearchIndex.PCMDeployRequest>{
                new RLM_RebuildSearchIndex.PCMDeployRequest(),
                new RLM_RebuildSearchIndex.PCMDeployRequest()
            }
        );
        Test.stopTest();

        Assert.isTrue(mock.received.size() >= 1, 'The failure came from a callout attempt');
        Assert.areEqual(2, results.size(), 'Each request still yields its own result, not an exception');
        for (RLM_RebuildSearchIndex.PCMDeployResult r : results) {
            Assert.areEqual(false, r.isSuccess, 'The result is marked failed');
            Assert.areEqual(RLM_RebuildSearchIndex.DEPLOY_FAILED_MESSAGE, r.message,
                'The flow gets a fixed sentence; the exception text goes to the debug log');
            Assert.isNull(r.statusCode, 'No HTTP status when the callout itself failed');
        }
    }

    @IsTest
    static void deployPcmIndexReturnsNoResultsForNoRequests() {
        PcmDeployMock mock = new PcmDeployMock(201, 'Created', FULL_SUCCESS_BODY);
        Test.setMock(HttpCalloutMock.class, mock);

        Test.startTest();
        List<RLM_RebuildSearchIndex.PCMDeployResult> results = RLM_RebuildSearchIndex.deployPCMIndex(
            new List<RLM_RebuildSearchIndex.PCMDeployRequest>()
        );
        Test.stopTest();

        Assert.isTrue(results.isEmpty(), 'No requests, no results');
        Assert.areEqual(0, mock.received.size(), 'No requests, no callouts');
    }

    @IsTest
    static void deployPcmIndexGuardsANullListAndFailsNullElementsInPlace() {
        PcmDeployMock mock = new PcmDeployMock(201, 'Created', FULL_SUCCESS_BODY);
        Test.setMock(HttpCalloutMock.class, mock);

        Test.startTest();
        List<RLM_RebuildSearchIndex.PCMDeployResult> fromNull = RLM_RebuildSearchIndex.deployPCMIndex(null);
        List<RLM_RebuildSearchIndex.PCMDeployResult> fromMixed = RLM_RebuildSearchIndex.deployPCMIndex(
            new List<RLM_RebuildSearchIndex.PCMDeployRequest>{
                null,
                new RLM_RebuildSearchIndex.PCMDeployRequest(),
                null
            }
        );
        Test.stopTest();

        Assert.isTrue(fromNull.isEmpty(), 'A null request list yields no results and no exception');
        Assert.areEqual(3, fromMixed.size(), 'One result per input, null elements included');
        Assert.areEqual(false, fromMixed[0].isSuccess, 'The first null element gets a failed result');
        Assert.areEqual(RLM_RebuildSearchIndex.NULL_REQUEST_MESSAGE, fromMixed[0].message, 'It says why');
        Assert.areEqual(true, fromMixed[1].isSuccess, 'The real request keeps its own position and runs');
        Assert.areEqual(false, fromMixed[2].isSuccess, 'The last null element gets a failed result');
        Assert.areEqual(RLM_RebuildSearchIndex.NULL_REQUEST_MESSAGE, fromMixed[2].message, 'It says why');
        Assert.areEqual(1, mock.received.size(), 'Only the real request makes a callout');
    }
}
