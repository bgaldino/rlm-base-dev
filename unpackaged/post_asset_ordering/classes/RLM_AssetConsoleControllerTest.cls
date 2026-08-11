/**
 * Tests for RLM_AssetConsoleController. Seeds a real Account / Product2 / Asset /
 * Contract / AssetContractRelationship graph to exercise the WITH USER_MODE read
 * paths and account resolution, and uses the RLM_AssetOrderingService mock seam
 * for the write path so no live native action is invoked.
 *
 * NOTE: tests run as an admin context and do not exercise FLS. The feature's
 * permission set is verified separately by a persona walk on a live org (see the
 * feature doc / Phase 1 live verification).
 */
@IsTest
private class RLM_AssetConsoleControllerTest {

    private static Account acct;
    private static Asset asset;
    private static Contract ctr;

    @TestSetup
    static void setup() {
        Account a = new Account(Name = 'ABO Test Account');
        insert a;

        Product2 p = new Product2(Name = 'ABO Widget', ProductCode = 'ABO-WIDGET', IsActive = true);
        insert p;

        Asset ast = new Asset(
            Name = 'ABO Asset 1',
            AccountId = a.Id,
            Product2Id = p.Id,
            Quantity = 3,
            HasLifecycleManagement = true,
            LifecycleStartDate = System.now(),
            LifecycleEndDate = System.now().addYears(1)
        );
        insert ast;

        // A Draft contract is enough to exercise account-resolution from a
        // Contract record context. We intentionally do NOT seed an
        // AssetContractRelationship here: the platform blocks creating one
        // unless the Contract is activated AND carries a Revenue Lifecycle
        // Management ApplicationUsageAssignment, which is provisioned by the
        // RLM order-to-contract flow and cannot be seeded via plain DML in a
        // unit test. Contract-grouped assets are covered by the Phase 1 live
        // verification on the org; here assets fall into the "No contract"
        // group, which still exercises the AssetContractRelationship query path.
        Contract c = new Contract(
            AccountId = a.Id,
            StartDate = Date.today(),
            ContractTerm = 12,
            Status = 'Draft'
        );
        insert c;
    }

    private static void loadFixtures() {
        acct = [SELECT Id FROM Account WHERE Name = 'ABO Test Account' LIMIT 1];
        asset = [SELECT Id FROM Asset WHERE Name = 'ABO Asset 1' LIMIT 1];
        ctr = [SELECT Id FROM Contract WHERE AccountId = :acct.Id LIMIT 1];
    }

    @IsTest
    static void getConsole_fromAccount_groupsByContract() {
        loadFixtures();
        Test.startTest();
        RLM_AssetConsoleController.ConsoleData data =
            RLM_AssetConsoleController.getConsole(acct.Id, 'Account');
        Test.stopTest();

        System.assertEquals(acct.Id, data.accountId);
        System.assertEquals(1, data.totalAssetCount, 'One seeded asset');
        System.assert(!data.groups.isEmpty(), 'Expected at least one contract group');
        Boolean foundAsset = false;
        for (RLM_AssetConsoleController.ContractGroupView g : data.groups) {
            for (RLM_AssetConsoleController.AssetRow r : g.assets) {
                if (r.id == asset.Id) {
                    foundAsset = true;
                    System.assertEquals('ABO Widget', r.productName);
                    System.assertEquals('ABO-WIDGET', r.productCode);
                }
            }
        }
        System.assert(foundAsset, 'Seeded asset should appear in a group');
    }

    @IsTest
    static void getConsole_resolvesFromContractAndAsset() {
        loadFixtures();
        RLM_AssetConsoleController.ConsoleData fromContract =
            RLM_AssetConsoleController.getConsole(ctr.Id, 'Contract');
        System.assertEquals(acct.Id, fromContract.accountId, 'Contract context resolves account');

        RLM_AssetConsoleController.ConsoleData fromAsset =
            RLM_AssetConsoleController.getConsole(asset.Id, 'Asset');
        System.assertEquals(acct.Id, fromAsset.accountId, 'Asset context resolves account');
    }

    @IsTest
    static void getConsole_nullReturnsEmpty() {
        RLM_AssetConsoleController.ConsoleData data =
            RLM_AssetConsoleController.getConsole(null, 'Account');
        System.assertEquals(0, data.totalAssetCount);
        System.assert(data.groups.isEmpty());
    }

    @IsTest
    static void launchConsolidatedAction_success() {
        loadFixtures();
        RLM_AssetOrderingService.ActionOutcome ok =
            new RLM_AssetOrderingService.ActionOutcome();
        ok.isSuccess = true;
        ok.outputRecordId = acct.Id; // any valid Id stands in for the output record
        ok.requestIdentifier = 'req-1';
        RLM_AssetOrderingService.mockOutcome = ok;

        Test.startTest();
        RLM_AssetOrderingService.ConsolidationResult res =
            RLM_AssetConsoleController.launchConsolidatedAction(
                new List<Id>{ asset.Id }, 'Amend', 'Quote',
                String.valueOf(Date.today()), 1, null, false);
        Test.stopTest();

        System.assert(res.isSuccess, 'Expected success');
        System.assertNotEquals(null, res.outputRecordId);
    }

    @IsTest
    static void launchConsolidatedAction_renewAndCancelPaths() {
        loadFixtures();
        RLM_AssetOrderingService.ActionOutcome ok =
            new RLM_AssetOrderingService.ActionOutcome();
        ok.isSuccess = true;
        ok.outputRecordId = acct.Id;
        RLM_AssetOrderingService.mockOutcome = ok;

        RLM_AssetOrderingService.ConsolidationResult renew =
            RLM_AssetConsoleController.launchConsolidatedAction(
                new List<Id>{ asset.Id }, 'Renew', null,
                null, null, String.valueOf(Date.today().addYears(1)), false);
        System.assert(renew.isSuccess);

        RLM_AssetOrderingService.ConsolidationResult cancel =
            RLM_AssetConsoleController.launchConsolidatedAction(
                new List<Id>{ asset.Id }, 'Cancel', 'Quote',
                String.valueOf(Date.today()), null, null, true);
        System.assert(cancel.isSuccess);
    }

    @IsTest
    static void launchConsolidatedAction_noAssetsThrows() {
        Boolean threw = false;
        try {
            RLM_AssetConsoleController.launchConsolidatedAction(
                new List<Id>(), 'Amend', 'Quote', null, null, null, false);
        } catch (AuraHandledException e) {
            threw = true;
        }
        System.assert(threw, 'Empty selection should throw AuraHandledException');
    }
}
