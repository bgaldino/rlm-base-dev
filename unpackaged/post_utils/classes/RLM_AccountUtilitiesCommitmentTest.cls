/**
 * The Account Reset and commitment links (UsageCmtAssetRelatedObj), each of which links a
 * commitment asset (AssetId) to its anchor (RelatedObjectId: an asset, the account, a
 * contract or a custom object).
 *
 * A link can be created only for a commitment product the platform has already set up.
 * Measured live 264: a Commit product with a Token resource, an active product usage
 * resource and an active grant, all created in the same transaction, is refused ("Ensure
 * the selected Asset is related to a Product with Usage Model Type set to Token Commitment
 * ..."), even with the org's own Token resource; and a link on assets without a product
 * fails with an internal error. So these tests read the org's own Commit and Anchor
 * products (SeeAllData, which is why they are not in RLM_AccountUtilitiesTest, whose
 * @TestSetup it forbids), and skip, with the reason logged, where the org has no
 * commitment product a link accepts or the running user is not an admin. They make their
 * own accounts, assets and contracts, and the reset touches only the account it is given.
 */
@IsTest(SeeAllData=true)
private without sharing class RLM_AccountUtilitiesCommitmentTest {
    private static final Datetime START = Datetime.now().addDays(-10);

    private static void skipped(String reason) {
        System.debug(LoggingLevel.WARN, 'RLM_AccountUtilitiesCommitmentTest: skipped, ' + reason);
    }

    private static Boolean runnerIsAdmin() {
        Boolean admin = RLM_AccountUtilities.seesAndDeletesEverything();
        if (!admin) {
            skipped('the running user lacks Modify All Data or View All Data, and the reset is for admins only');
        }
        return admin;
    }

    private static Account newAccount(String name) {
        Account a = new Account(Name = name);
        insert a;
        return a;
    }

    private static Asset newAsset(Id accountId, Id productId, String name) {
        Asset asset = new Asset(Name = name, AccountId = accountId, Product2Id = productId,
            LifecycleStartDate = START, LifecycleEndDate = START.addYears(1));
        insert asset;
        return asset;
    }

    // A commitment asset on `commitmentAccountId` linked to `anchorId`, on the first active
    // Commit product by Id whose link the platform accepts (which it accepts depends on its
    // tokens and on the anchor). Null when none does; the commitments it tried are removed.
    private static UsageCmtAssetRelatedObj link(Id commitmentAccountId, Id anchorId) {
        for (Product2 commitProduct : [
            SELECT Id FROM Product2 WHERE IsActive = true AND UsageModelType = 'Commit' ORDER BY Id LIMIT 5
        ]) {
            Asset commitment = newAsset(commitmentAccountId, commitProduct.Id, 'RLM Utilities Commitment');
            UsageCmtAssetRelatedObj made = new UsageCmtAssetRelatedObj(AssetId = commitment.Id,
                RelatedObjectId = anchorId, EffectiveStartDateTime = START, EffectiveEndDateTime = START.addYears(1));
            if (Database.insert(made, false).isSuccess()) {
                return made;
            }
            delete commitment;
        }
        return null;
    }

    // An anchor asset on `accountId`, on the first active Anchor product by Id that takes a
    // link, with a commitment on `commitmentAccountId` linked to it. Null, with the reason
    // logged, when no pair is accepted.
    private static UsageCmtAssetRelatedObj linkToAnAnchorAsset(Id accountId, Id commitmentAccountId) {
        for (Product2 anchorProduct : [
            SELECT Id FROM Product2 WHERE IsActive = true AND UsageModelType = 'Anchor' ORDER BY Id LIMIT 5
        ]) {
            Asset anchor = newAsset(accountId, anchorProduct.Id, 'RLM Utilities Anchor');
            UsageCmtAssetRelatedObj made = link(commitmentAccountId, anchor.Id);
            if (made != null) {
                return made;
            }
            delete anchor;
        }
        skipped('no active Anchor and Commit product pair here takes a commitment link');
        return null;
    }

    private static RLM_AccountUtilities.Result reset(Id accountId, Boolean deleteAssets, Boolean preserve) {
        RLM_AccountUtilities.InputVariables iv = new RLM_AccountUtilities.InputVariables();
        iv.accountId = accountId;
        iv.DeleteAssets = deleteAssets;
        iv.DeleteFulfillment = false;
        iv.DeleteBilling = false;
        iv.PreserveContractsWithContractedPrices = preserve;
        return RLM_AccountUtilities.delAccountRelatedObjects(new List<RLM_AccountUtilities.InputVariables>{ iv })[0];
    }

    private static Integer linkCount(Id linkId) {
        return [SELECT COUNT() FROM UsageCmtAssetRelatedObj WHERE Id = :linkId];
    }

    // ------------------------------------------------------------ anchored on an asset

    // Without Delete Assets the assets stay, and so does their commitment link.
    @IsTest
    static void aResetWithoutDeleteAssetsKeepsTheCommitmentLink() {
        if (!runnerIsAdmin()) return;
        Account a = newAccount('RLM Utilities Commitment Account');
        UsageCmtAssetRelatedObj linked = linkToAnAnchorAsset(a.Id, a.Id);
        if (linked == null) return;

        Test.startTest();
        RLM_AccountUtilities.Result result = reset(a.Id, false, false);
        Test.stopTest();

        Assert.areEqual(true, result.completed, 'The reset must complete. Reason: ' + result.reason);
        Assert.areEqual(2, [SELECT COUNT() FROM Asset WHERE AccountId = :a.Id], 'Both assets stay');
        Assert.areEqual(1, linkCount(linked.Id), 'A kept asset keeps its commitment link');
    }

    // With Delete Assets the link and both assets go. (Deleting the commitment asset would
    // take the link with it; the next test covers a link only the explicit delete removes.)
    @IsTest
    static void aResetWithDeleteAssetsDeletesTheLinkAndThenTheAnchor() {
        if (!runnerIsAdmin()) return;
        Account a = newAccount('RLM Utilities Commitment Account');
        UsageCmtAssetRelatedObj linked = linkToAnAnchorAsset(a.Id, a.Id);
        if (linked == null) return;

        Test.startTest();
        RLM_AccountUtilities.Result result = reset(a.Id, true, false);
        Test.stopTest();

        Assert.areEqual(true, result.completed, 'The reset must complete. Reason: ' + result.reason);
        Assert.areEqual(0, linkCount(linked.Id), 'The commitment link is deleted');
        Assert.areEqual(0, [SELECT COUNT() FROM Asset WHERE AccountId = :a.Id], 'Both assets are deleted');
    }

    // The anchor is this account's, the commitment another account's: nothing the reset
    // deletes takes the link along, so it must delete the link itself before the anchor.
    @IsTest
    static void aLinkFromAnotherAccountsCommitmentIsDeletedBeforeTheAnchor() {
        if (!runnerIsAdmin()) return;
        Account a = newAccount('RLM Utilities Commitment Account');
        Account other = newAccount('RLM Utilities Commitment Other Account');
        UsageCmtAssetRelatedObj linked = linkToAnAnchorAsset(a.Id, other.Id);
        if (linked == null) return;

        Test.startTest();
        RLM_AccountUtilities.Result result = reset(a.Id, true, false);
        Test.stopTest();

        Assert.areEqual(true, result.completed, 'The anchor can go. Reason: ' + result.reason);
        Assert.areEqual(0, [SELECT COUNT() FROM Asset WHERE AccountId = :a.Id], 'The anchor is deleted');
        Assert.areEqual(0, linkCount(linked.Id), 'Its commitment link is deleted');
        Assert.areEqual(1, [SELECT COUNT() FROM Asset WHERE Id = :linked.AssetId],
            'The other account\'s commitment asset stays');
    }

    // ------------------------------------------------------------ anchored on a contract

    // A link anchored on a contract blocks the contract's delete (measured live 264), so it
    // goes with a contract the reset deletes, before it. The commitment asset stays: Delete
    // Assets is off.
    @IsTest
    static void aContractTheResetDeletesTakesItsCommitmentLink() {
        if (!runnerIsAdmin()) return;
        Account a = newAccount('RLM Utilities Commitment Account');
        Contract c = new Contract(AccountId = a.Id, StartDate = Date.today().addDays(-10), ContractTerm = 12, Status = 'Draft');
        insert c;
        UsageCmtAssetRelatedObj linked = link(a.Id, c.Id);
        if (linked == null) {
            skipped('no active Commit product here takes a link anchored on a contract');
            return;
        }

        Test.startTest();
        RLM_AccountUtilities.Result result = reset(a.Id, false, false);
        Test.stopTest();

        Assert.areEqual(true, result.completed, 'The contract can go. Reason: ' + result.reason);
        Assert.areEqual(0, [SELECT COUNT() FROM Contract WHERE Id = :c.Id], 'The contract is deleted');
        Assert.areEqual(0, linkCount(linked.Id), 'Its commitment link is deleted');
        Assert.areEqual(1, [SELECT COUNT() FROM Asset WHERE Id = :linked.AssetId], 'The commitment asset stays');
    }

    // A contract kept for its contracted prices keeps its commitment link.
    @IsTest
    static void aContractPreservedForItsPricesKeepsItsCommitmentLink() {
        if (!runnerIsAdmin()) return;
        if (!Schema.getGlobalDescribe().containsKey('ContractItemPrice')) {
            skipped('the org has no Contract Pricing');
            return;
        }
        Account a = newAccount('RLM Utilities Commitment Account');
        Contract c = new Contract(AccountId = a.Id, StartDate = Date.today().addDays(-10), ContractTerm = 12, Status = 'Draft');
        insert c;
        Product2 priced = new Product2(Name = 'RLM Utilities Contracted Product', IsActive = true);
        insert priced;
        SObject price = Schema.getGlobalDescribe().get('ContractItemPrice').newSObject();
        price.put('ContractId', c.Id);
        price.put('ItemId', priced.Id);
        price.put('StartDate', System.now());
        price.put('Price', 100.0);
        insert price;
        UsageCmtAssetRelatedObj linked = link(a.Id, c.Id);
        if (linked == null) {
            skipped('no active Commit product here takes a link anchored on a contract');
            return;
        }

        Test.startTest();
        RLM_AccountUtilities.Result result = reset(a.Id, false, true);
        Test.stopTest();

        Assert.areEqual(true, result.completed, 'The reset must complete. Reason: ' + result.reason);
        Assert.areEqual(1, [SELECT COUNT() FROM Contract WHERE Id = :c.Id], 'PRECONDITION: the contract is kept');
        Assert.areEqual(1, linkCount(linked.Id), 'A kept contract keeps its commitment link');
    }
}
