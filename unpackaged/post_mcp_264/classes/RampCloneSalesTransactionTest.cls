/**
 * Coverage for the 264 / v68.0 async-capable clone invocable. Overlays the base
 * bundle's 67.0 test alongside the class it covers, so the deployed pair always match.
 *
 * The happy path is deliberately not asserted. ConnectApi calls are unsupported in a
 * test context without a platform-supplied mock, and none exists for
 * CloneSalesTransactionConnect, so neither a successful sync clone nor a triggered
 * async clone can be simulated. What these tests pin down is the contract an MCP client
 * actually depends on: the invocable never throws at its boundary, returns one Result
 * per Request, reports failure in Result.errorMessage, and — the reason this variant
 * exists at all — still compiles against the async members. Referencing contextId,
 * trackerId, trackerUrl, and isAsync here means a deploy of this bundle to an org that
 * lacks them fails loudly at validation instead of silently losing the async path.
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
            System.assertEquals(false, r.isAsync, 'A rejected request never went async');
            System.assertNotEquals(null, r.errorMessage, 'Failure must explain itself');
        }
    }

    @isTest
    static void surfacesConnectFailureInsteadOfThrowing() {
        // ConnectApi is unsupported in tests, so this exercises the catch path: the
        // invocable must convert that into a Result, not let it escape to the caller.
        RampCloneSalesTransaction.Request req = buildRequest();
        req.contextId = 'ctx-async-trigger';

        Test.startTest();
        List<RampCloneSalesTransaction.Result> results =
            RampCloneSalesTransaction.cloneSegments(
                new List<RampCloneSalesTransaction.Request>{ req }
            );
        Test.stopTest();

        System.assertEquals(1, results.size(), 'One Result per Request');
        RampCloneSalesTransaction.Result r = results[0];
        System.assertEquals(false, r.success, 'Unreachable Connect call is a failure');
        System.assertEquals(false, r.isAsync, 'A failed call did not go async');
        System.assertEquals(null, r.trackerId, 'No tracker handle without a live call');
        System.assertEquals(null, r.trackerUrl, 'No tracker handle without a live call');
        System.assertNotEquals(null, r.errorMessage, 'Failure must explain itself');
    }

    @isTest
    static void acceptsBothLineScopeSpellingsAndIgnoresGarbage() {
        // parseLineScope is private; drive it through the public entry point. Each of
        // these must come back as a Result rather than an enum failure.
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
