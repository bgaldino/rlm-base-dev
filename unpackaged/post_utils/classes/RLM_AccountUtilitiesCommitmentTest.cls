/**
 * The Account Reset and the commitment junction (UsageCmtAssetRelatedObj), which links a
 * commitment asset (AssetId) to its anchor (RelatedObjectId).
 *
 * A junction can be created only for a commitment product the platform has already set
 * up. Measured live 264: a Commit product with a Token resource, an active product usage
 * resource and an active grant, all created in the same transaction, is refused ("Ensure
 * the selected Asset is related to a Product with Usage Model Type set to Token Commitment
 * ..."), even with the org's own Token resource; and a junction on assets without a
 * product fails with an internal error. So these tests read the org's own Commit and
 * Anchor products (SeeAllData, which is why they are not in RLM_AccountUtilitiesTest,
 * whose @TestSetup it forbids), and skip, with the reason logged, where the org has no
 * commitment product a junction accepts or the running user is not an admin. They make
 * their own account and assets, and the reset touches only that account.
 */
@IsTest(SeeAllData=true)
private without sharing class RLM_AccountUtilitiesCommitmentTest {
    private class Linked {
        Account account;
        Asset anchor;
        Asset commitment;
        Id junctionId;
    }

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

    // An account with an anchor asset and a commitment asset linked by a junction: the first
    // pair, by product Id, of an active Anchor product and an active Commit product whose
    // junction the platform accepts (which pairs it accepts depends on their tokens), with the
    // other assets removed. Null, with the reason logged, when no pair is accepted.
    private static Linked linkedAssets() {
        List<Product2> anchorProducts = [
            SELECT Id FROM Product2 WHERE IsActive = true AND UsageModelType = 'Anchor' ORDER BY Id LIMIT 5
        ];
        List<Product2> commitProducts = [
            SELECT Id FROM Product2 WHERE IsActive = true AND UsageModelType = 'Commit' ORDER BY Id LIMIT 5
        ];
        if (anchorProducts.isEmpty() || commitProducts.isEmpty()) {
            skipped('the org has no active Anchor or no active Commit product');
            return null;
        }
        Datetime start = Datetime.now().addDays(-10);
        Account a = new Account(Name = 'RLM Utilities Commitment Account');
        insert a;
        List<Asset> anchors = new List<Asset>();
        for (Product2 product : anchorProducts) {
            anchors.add(new Asset(Name = 'RLM Utilities Anchor', AccountId = a.Id, Product2Id = product.Id,
                LifecycleStartDate = start, LifecycleEndDate = start.addYears(1)));
        }
        List<Asset> commitments = new List<Asset>();
        for (Product2 product : commitProducts) {
            commitments.add(new Asset(Name = 'RLM Utilities Commitment', AccountId = a.Id, Product2Id = product.Id,
                LifecycleStartDate = start, LifecycleEndDate = start.addYears(1)));
        }
        insert anchors;
        insert commitments;
        for (Asset anchor : anchors) {
            for (Asset commitment : commitments) {
                Database.SaveResult made = Database.insert(new UsageCmtAssetRelatedObj(
                    AssetId = commitment.Id, RelatedObjectId = anchor.Id,
                    EffectiveStartDateTime = start, EffectiveEndDateTime = start.addYears(1)
                ), false);
                if (made.isSuccess()) {
                    List<Asset> others = new List<Asset>();
                    for (Asset other : [SELECT Id FROM Asset WHERE AccountId = :a.Id]) {
                        if (other.Id != anchor.Id && other.Id != commitment.Id) {
                            others.add(other);
                        }
                    }
                    delete others;
                    Linked linked = new Linked();
                    linked.account = a;
                    linked.anchor = anchor;
                    linked.commitment = commitment;
                    linked.junctionId = made.getId();
                    return linked;
                }
            }
        }
        skipped('no active Anchor and Commit product pair here takes a commitment junction');
        return null;
    }

    private static RLM_AccountUtilities.Result reset(Id accountId, Boolean deleteAssets) {
        RLM_AccountUtilities.InputVariables iv = new RLM_AccountUtilities.InputVariables();
        iv.accountId = accountId;
        iv.DeleteAssets = deleteAssets;
        iv.DeleteFulfillment = false;
        iv.DeleteBilling = false;
        return RLM_AccountUtilities.delAccountRelatedObjects(new List<RLM_AccountUtilities.InputVariables>{ iv })[0];
    }

    // Without Delete Assets the assets stay, and so does their commitment link.
    @IsTest
    static void aResetWithoutDeleteAssetsKeepsTheCommitmentLink() {
        if (!runnerIsAdmin()) return;
        Linked linked = linkedAssets();
        if (linked == null) return;

        Test.startTest();
        RLM_AccountUtilities.Result result = reset(linked.account.Id, false);
        Test.stopTest();

        Assert.areEqual(true, result.completed, 'The reset must complete. Reason: ' + result.reason);
        Assert.areEqual(2, [SELECT COUNT() FROM Asset WHERE AccountId = :linked.account.Id], 'Both assets stay');
        Assert.areEqual(1, [SELECT COUNT() FROM UsageCmtAssetRelatedObj WHERE Id = :linked.junctionId],
            'A kept asset keeps its commitment link');
    }

    // With Delete Assets the link goes first: an anchor cannot be deleted while it survives.
    @IsTest
    static void aResetWithDeleteAssetsDeletesTheLinkAndThenTheAnchor() {
        if (!runnerIsAdmin()) return;
        Linked linked = linkedAssets();
        if (linked == null) return;

        Test.startTest();
        RLM_AccountUtilities.Result result = reset(linked.account.Id, true);
        Test.stopTest();

        Assert.areEqual(true, result.completed, 'The reset must complete. Reason: ' + result.reason);
        Assert.areEqual(0, [SELECT COUNT() FROM UsageCmtAssetRelatedObj WHERE Id = :linked.junctionId],
            'The commitment link is deleted');
        Assert.areEqual(0, [SELECT COUNT() FROM Asset WHERE Id = :linked.anchor.Id], 'The anchor is deleted');
        Assert.areEqual(0, [SELECT COUNT() FROM Asset WHERE Id = :linked.commitment.Id], 'The commitment is deleted');
    }
}
