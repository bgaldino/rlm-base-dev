/**
 * Coverage for the MCP-facing clone invocable.
 *
 * The happy path is deliberately not asserted here. ConnectApi calls are unsupported in
 * a test context without a platform-supplied mock, and no mock exists for
 * CloneSalesTransactionConnect, so a "successful clone" cannot be simulated. What these
 * tests do pin down is the contract the MCP tool depends on: the invocable never throws
 * at its boundary, always returns one Result per Request, and reports failure in
 * Result.errorMessage rather than as an unhandled exception — which is what an MCP
 * client sees. The live clone path is verified against an org, not here.
 */
@isTest
private class RampCloneSalesTransactionTest {

    private static RampCloneSalesTransaction.Request buildRequest() {
        RampCloneSalesTransaction.Request req = new RampCloneSalesTransaction.Request();
        req.salesTransactionId = '0Q0000000000000AAA';
        req.recordIds = new List<String>{ '0QG000000000000AAA' };
        return req;
    }

    @isTest
    static void returnsEmptyForNullAndEmptyInput() {
        Test.startTest();
        List<RampCloneSalesTransaction.Result> fromNull =
            RampCloneSalesTransaction.cloneSegments(null);
        List<RampCloneSalesTransaction.Result> fromEmpty =
            RampCloneSalesTransaction.cloneSegments(
                new List<RampCloneSalesTransaction.Request>()
            );
        Test.stopTest();

        System.assertEquals(0, fromNull.size(), 'Null input should yield no results');
        System.assertEquals(0, fromEmpty.size(), 'Empty input should yield no results');
    }

    @isTest
    static void reportsMissingRequiredFieldsAsFailure() {
        RampCloneSalesTransaction.Request noHeader = new RampCloneSalesTransaction.Request();
        noHeader.recordIds = new List<String>{ '0QG000000000000AAA' };

        RampCloneSalesTransaction.Request noRecords = new RampCloneSalesTransaction.Request();
        noRecords.salesTransactionId = '0Q0000000000000AAA';

        Test.startTest();
        List<RampCloneSalesTransaction.Result> results =
            RampCloneSalesTransaction.cloneSegments(
                new List<RampCloneSalesTransaction.Request>{ noHeader, noRecords }
            );
        Test.stopTest();

        System.assertEquals(2, results.size(), 'One Result per Request');
        for (RampCloneSalesTransaction.Result r : results) {
            System.assertEquals(false, r.success, 'Incomplete input must not report success');
            System.assertNotEquals(null, r.errorMessage, 'Failure must explain itself');
        }
    }

    @isTest
    static void surfacesConnectFailureInsteadOfThrowing() {
        // ConnectApi is unsupported in tests, so this exercises the catch path: the
        // invocable must convert that into a Result, not let it escape to the caller.
        Test.startTest();
        List<RampCloneSalesTransaction.Result> results =
            RampCloneSalesTransaction.cloneSegments(
                new List<RampCloneSalesTransaction.Request>{ buildRequest() }
            );
        Test.stopTest();

        System.assertEquals(1, results.size(), 'One Result per Request');
        System.assertEquals(false, results[0].success, 'Unreachable Connect call is a failure');
        System.assertNotEquals(null, results[0].errorMessage, 'Failure must explain itself');
    }

    @isTest
    static void acceptsBothLineScopeSpellingsAndIgnoresGarbage() {
        // parseLineScope is private; drive it through the public entry point. Each of
        // these must come back as a Result rather than a compile/enum failure.
        List<RampCloneSalesTransaction.Request> requests =
            new List<RampCloneSalesTransaction.Request>();
        for (String scope : new List<String>{ 'AllLines', 'rampedlinesonly', 'nonsense', null }) {
            RampCloneSalesTransaction.Request req = buildRequest();
            req.lineScope = scope;
            req.recordTypeId = '012000000000000AAA';
            requests.add(req);
        }

        Test.startTest();
        List<RampCloneSalesTransaction.Result> results =
            RampCloneSalesTransaction.cloneSegments(requests);
        Test.stopTest();

        System.assertEquals(4, results.size(), 'One Result per Request, whatever the scope');
    }
}
