/**
 * Tests for RLM_RebuildSearchIndex: the PCM index deploy callout, its request shape, and
 * how each response (success with and without index details, HTTP error, unparseable body,
 * transport failure) maps onto the LWC result map and the invocable result.
 */
@IsTest
private class RLM_RebuildSearchIndexTest {

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
    private class PcmDeployMock implements HttpCalloutMock {
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

        /** A mock whose every callout throws a CalloutException; use throwingMock(). */
        public PcmDeployMock() {
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
        Assert.isNotNull(snapshot, 'The request carries a snapshot block');
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
        Assert.areEqual(
            'API call failed: Internal Server Error - [{"errorCode":"UNKNOWN_EXCEPTION"}]',
            result.get('message'),
            'The message carries the HTTP status text and the raw body'
        );
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
        Assert.areEqual(2, mock.received.size(), 'One callout per request');
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

    /**
     * Records CURRENT behaviour, not the intended contract. PCMDeployRequest exposes Build Type
     * and Activation Type as invocable inputs, but callPcmDeploy always sends FULL / IMMEDIATE,
     * so the inputs are a known gap. When they are wired through, change this test to expect
     * the request's values in the callout body.
     */
    @IsTest
    static void deployPcmIndexDoesNotYetForwardRequestBuildAndActivationType() {
        PcmDeployMock mock = new PcmDeployMock(201, 'Created', FULL_SUCCESS_BODY);
        Test.setMock(HttpCalloutMock.class, mock);

        RLM_RebuildSearchIndex.PCMDeployRequest request = new RLM_RebuildSearchIndex.PCMDeployRequest();
        request.buildType = 'INCREMENTAL';
        request.activationType = 'DEFERRED';

        Test.startTest();
        RLM_RebuildSearchIndex.deployPCMIndex(new List<RLM_RebuildSearchIndex.PCMDeployRequest>{ request });
        Test.stopTest();

        Assert.areEqual(1, mock.received.size(), 'One callout for one request');
        Map<String, Object> body = (Map<String, Object>) JSON.deserializeUntyped(mock.received[0].getBody());
        Assert.areEqual(
            'FULL',
            body.get('buildType'),
            'Known gap: the request\'s buildType is not forwarded yet; update this test when it is fixed'
        );
        Assert.areEqual(
            'IMMEDIATE',
            ((Map<String, Object>) body.get('snapshot')).get('activationType'),
            'Known gap: the request\'s activationType is not forwarded yet; update this test when it is fixed'
        );
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
        Assert.areEqual('API call failed: Bad Request - bad request body', results[0].message, 'Error message is mapped');
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

        Assert.areEqual(2, mock.received.size(), 'The first failure does not stop the second request\'s callout');
        Assert.areEqual(2, results.size(), 'Each failing callout still yields its own result, not an exception');
        for (RLM_RebuildSearchIndex.PCMDeployResult r : results) {
            Assert.areEqual(false, r.isSuccess, 'The result is marked failed');
            Assert.isTrue(
                r.message.startsWith('Exception occurred: '),
                'The exception is reported in the message: ' + r.message
            );
            Assert.isTrue(
                r.message.contains('Simulated transport failure'),
                'The original exception text is preserved: ' + r.message
            );
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
}
