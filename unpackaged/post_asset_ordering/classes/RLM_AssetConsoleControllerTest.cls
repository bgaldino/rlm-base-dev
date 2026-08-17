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
    private static Account childAcct;
    private static Asset asset;
    private static Asset relatedAsset;
    private static Contract ctr;

    @TestSetup
    static void setup() {
        Account a = new Account(Name = 'ABO Test Account');
        insert a;

        // A related account that is a CHILD of the primary account, so the
        // hierarchy traversal (walk up to root, then down) picks it up.
        Account childA = new Account(Name = 'ABO Child Account', ParentId = a.Id);
        insert childA;

        Product2 p = new Product2(Name = 'ABO Widget', ProductCode = 'ABO-WIDGET', IsActive = true);
        insert p;

        Asset ast = new Asset(
            Name = 'ABO Asset 1',
            AccountId = a.Id,
            Product2Id = p.Id,
            Quantity = 3,
            SerialNumber = 'SN-PARENT-001',
            HasLifecycleManagement = true,
            LifecycleStartDate = System.now(),
            LifecycleEndDate = System.now().addYears(1)
        );
        insert ast;

        // An asset that lives on the related (child) account - only visible when
        // the hierarchy is included.
        Asset relAst = new Asset(
            Name = 'ABO Related Asset',
            AccountId = childA.Id,
            Product2Id = p.Id,
            Quantity = 1,
            SerialNumber = 'SN-RELATED-001',
            HasLifecycleManagement = true,
            LifecycleStartDate = System.now(),
            LifecycleEndDate = System.now().addYears(1)
        );
        insert relAst;

        // Child bundle item - references the parent via ParentId so the
        // controller's parent/child hierarchy fields are exercised.
        Asset child = new Asset(
            Name = 'ABO Asset 1 - Child',
            AccountId = a.Id,
            Product2Id = p.Id,
            Quantity = 1,
            SerialNumber = 'SN-CHILD-001',
            ParentId = ast.Id,
            HasLifecycleManagement = true,
            LifecycleStartDate = System.now(),
            LifecycleEndDate = System.now().addYears(1)
        );
        insert child;

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
        childAcct = [SELECT Id FROM Account WHERE Name = 'ABO Child Account' LIMIT 1];
        asset = [SELECT Id FROM Asset WHERE Name = 'ABO Asset 1' LIMIT 1];
        relatedAsset = [SELECT Id FROM Asset WHERE Name = 'ABO Related Asset' LIMIT 1];
        ctr = [SELECT Id FROM Contract WHERE AccountId = :acct.Id LIMIT 1];
    }

    @IsTest
    static void getConsole_fromAccount_groupsByContract() {
        loadFixtures();
        Test.startTest();
        RLM_AssetConsoleController.ConsoleData data =
            RLM_AssetConsoleController.getConsole(acct.Id, 'Account', false);
        Test.stopTest();

        System.assertEquals(acct.Id, data.accountId);
        System.assertEquals(1, data.accountCount, 'Primary account only when hierarchy is off');
        System.assertEquals(2, data.totalAssetCount, 'Parent + child seeded assets (primary account only)');
        System.assert(!data.groups.isEmpty(), 'Expected at least one contract group');
        Boolean foundParent = false;
        Boolean foundChild = false;
        for (RLM_AssetConsoleController.ContractGroupView g : data.groups) {
            for (RLM_AssetConsoleController.AssetRow r : g.assets) {
                if (r.id == asset.Id) {
                    foundParent = true;
                    System.assertEquals('ABO Widget', r.productName);
                    System.assertEquals('ABO-WIDGET', r.productCode);
                    System.assertEquals('SN-PARENT-001', r.serialNumber, 'Serial number surfaced');
                } else if (r.serialNumber == 'SN-CHILD-001') {
                    foundChild = true;
                    System.assertEquals(asset.Id, r.parentId, 'Child keeps its parent relationship');
                }
            }
        }
        System.assert(foundParent, 'Seeded parent asset should appear in a group');
        System.assert(foundChild, 'Seeded child asset should appear with its parentId');
    }

    @IsTest
    static void getConsole_resolvesFromContractAndAsset() {
        loadFixtures();
        RLM_AssetConsoleController.ConsoleData fromContract =
            RLM_AssetConsoleController.getConsole(ctr.Id, 'Contract', false);
        System.assertEquals(acct.Id, fromContract.accountId, 'Contract context resolves account');

        RLM_AssetConsoleController.ConsoleData fromAsset =
            RLM_AssetConsoleController.getConsole(asset.Id, 'Asset', false);
        System.assertEquals(acct.Id, fromAsset.accountId, 'Asset context resolves account');
    }

    @IsTest
    static void getConsole_nullReturnsEmpty() {
        RLM_AssetConsoleController.ConsoleData data =
            RLM_AssetConsoleController.getConsole(null, 'Account', false);
        System.assertEquals(0, data.totalAssetCount);
        System.assert(data.groups.isEmpty());
    }

    @IsTest
    static void getConsole_includesHierarchyFromRelatedAccounts() {
        loadFixtures();
        Test.startTest();
        // Hierarchy OFF: related-account asset is not visible.
        RLM_AssetConsoleController.ConsoleData noHier =
            RLM_AssetConsoleController.getConsole(acct.Id, 'Account', false);
        // Hierarchy ON: the child account's asset is pulled in.
        RLM_AssetConsoleController.ConsoleData withHier =
            RLM_AssetConsoleController.getConsole(acct.Id, 'Account', true);
        Test.stopTest();

        System.assertEquals(2, noHier.totalAssetCount, 'Without hierarchy: primary account assets only');
        System.assertEquals(3, withHier.totalAssetCount, 'With hierarchy: adds the related-account asset');
        System.assert(withHier.accountCount >= 2, 'Hierarchy spans the primary + child account');

        Boolean foundRelated = false;
        String relatedAccountName;
        for (RLM_AssetConsoleController.ContractGroupView g : withHier.groups) {
            for (RLM_AssetConsoleController.AssetRow r : g.assets) {
                if (r.serialNumber == 'SN-RELATED-001') {
                    foundRelated = true;
                    relatedAccountName = r.accountName;
                    System.assertEquals(childAcct.Id, r.accountId, 'Row carries its owning account id');
                }
            }
        }
        System.assert(foundRelated, 'Related-account asset should appear when hierarchy is on');
        System.assertEquals('ABO Child Account', relatedAccountName, 'Row shows its source account name');
    }

    @IsTest
    static void getConsole_resolvesHierarchyFromChildContext() {
        loadFixtures();
        // Starting from the child account should still walk UP to the root and
        // back down, so the parent account's assets are included.
        Test.startTest();
        RLM_AssetConsoleController.ConsoleData data =
            RLM_AssetConsoleController.getConsole(childAcct.Id, 'Account', true);
        Test.stopTest();
        System.assertEquals(3, data.totalAssetCount,
            'From the child account, hierarchy still reaches the parent account assets');
    }

    @IsTest
    static void launchConsolidatedAction_crossAccountThrows() {
        loadFixtures();
        Boolean threw = false;
        String msg;
        try {
            RLM_AssetConsoleController.launchConsolidatedAction(
                new List<Id>{ asset.Id, relatedAsset.Id }, 'Amend', 'Quote',
                String.valueOf(Date.today()), 1, null, false);
        } catch (AuraHandledException e) {
            threw = true;
            msg = e.getMessage();
        }
        System.assert(threw, 'Selecting assets from two accounts should throw');
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
