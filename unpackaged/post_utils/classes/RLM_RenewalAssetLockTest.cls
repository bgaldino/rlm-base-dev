@IsTest
private class RLM_RenewalAssetLockTest {

    @IsTest
    static void locksGivenAssets() {
        Account account = new Account(Name = 'Renewal Lock Test');
        insert account;
        Asset asset = new Asset(Name = 'Renewal Lock Asset', AccountId = account.Id);
        insert asset;

        RLM_RenewalAssetLock.Request request = new RLM_RenewalAssetLock.Request();
        request.assetIds = new List<String>{ asset.Id, '' };
        RLM_RenewalAssetLock.Request empty = new RLM_RenewalAssetLock.Request();

        Test.startTest();
        RLM_RenewalAssetLock.lockAssets(new List<RLM_RenewalAssetLock.Request>{ request, empty });
        Integer queries = Limits.getQueries();
        Test.stopTest();

        Assert.areEqual(1, queries, 'All requests are locked with one query');
    }

    @IsTest
    static void skipsQueryWithNoAssets() {
        RLM_RenewalAssetLock.Request request = new RLM_RenewalAssetLock.Request();
        request.assetIds = new List<String>();

        Test.startTest();
        RLM_RenewalAssetLock.lockAssets(new List<RLM_RenewalAssetLock.Request>{ request });
        Integer queries = Limits.getQueries();
        Test.stopTest();

        Assert.areEqual(0, queries, 'No query runs without assets');
    }
}
