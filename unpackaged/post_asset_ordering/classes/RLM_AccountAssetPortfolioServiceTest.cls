/**
 * Tests for RLM_AccountAssetPortfolioService (the console's Portfolio Timeline
 * data source). Seeds Asset + AssetStatePeriod records and asserts the timeline
 * point mapping. All reads run WITH USER_MODE in the class under test.
 */
@IsTest
private class RLM_AccountAssetPortfolioServiceTest {

    @TestSetup
    static void setup() {
        Account a = new Account(Name = 'Portfolio Acct');
        insert a;

        Product2 p = new Product2(Name = 'Timeline Product', IsActive = true);
        insert p;

        Asset ast = new Asset(Name = 'Timeline Asset', AccountId = a.Id, Product2Id = p.Id);
        insert ast;

        insert new List<AssetStatePeriod>{
            new AssetStatePeriod(
                AssetId = ast.Id, StartDate = System.now().addMonths(-2),
                Quantity = 5, Amount = 500, Mrr = 100
            ),
            new AssetStatePeriod(
                AssetId = ast.Id, StartDate = System.now(),
                Quantity = 8, Amount = 800, Mrr = 160
            )
        };
    }

    @IsTest
    static void getAccountAssetTimeline_returnsPoints() {
        Account a = [SELECT Id FROM Account WHERE Name = 'Portfolio Acct' LIMIT 1];
        Test.startTest();
        RLM_AccountAssetPortfolioService.PortfolioResponse resp =
            RLM_AccountAssetPortfolioService.getAccountAssetTimeline(a.Id);
        Test.stopTest();

        System.assertEquals(1, resp.assets.size(), 'One asset');
        System.assertEquals('Timeline Product', resp.assets[0].productName);
        System.assertEquals(2, resp.points.size(), 'Two state periods');
        for (RLM_AccountAssetPortfolioService.PointWrapper pt : resp.points) {
            System.assertNotEquals(null, pt.startDate, 'ISO date string set');
            System.assert(pt.startDate.length() == 10, 'yyyy-MM-dd format');
        }
    }

    @IsTest
    static void getAccountAssetTimeline_nullAndEmpty() {
        RLM_AccountAssetPortfolioService.PortfolioResponse resp =
            RLM_AccountAssetPortfolioService.getAccountAssetTimeline(null);
        System.assert(resp.assets.isEmpty());

        Account empty = new Account(Name = 'No Assets Acct');
        insert empty;
        RLM_AccountAssetPortfolioService.PortfolioResponse resp2 =
            RLM_AccountAssetPortfolioService.getAccountAssetTimeline(empty.Id);
        System.assert(resp2.assets.isEmpty(), 'No assets -> empty');
    }
}
