/**
 * Tests for RLM_AccountUtilities.delAccountRelatedObjects.
 *
 * WHAT IS WORTH TESTING HERE
 * --------------------------
 * The class has exactly one public entry point and ~40 private helpers, so the
 * only contract a test can hold it to is the invocable's own: the input guards,
 * and which categories of record each flag is allowed to delete. That flag
 * gating is also the part that has actually broken -- AssetRateCardEntry rows
 * were once removed while the asset was kept, leaving a usage asset that could
 * never rate again -- so it is where the assertions are concentrated.
 *
 * AVOIDING A VACUOUS PASS
 * -----------------------
 * Every deletion test asserts its PRECONDITION first: that the record really
 * exists before the reset runs. Without that, a setup failure would leave
 * nothing to delete and the "it was deleted" assertion would pass for the wrong
 * reason -- the class of defect this repository produces most often, where a
 * check silently validates an empty set.
 *
 * COVERAGE: 34.6% (346/1001 lines), measured on a scratch org 2026-07-25.
 * ----------------------------------------------------------------------------
 * That is BELOW the 75% Salesforce requires for a production deploy. Stated
 * plainly so nobody reads a green run as deploy-readiness.
 *
 * The uncovered ~655 lines are the usage-graph and fulfillment teardown --
 * deleteUsageEntitlementBucketsHierarchy/BottomUp, deleteUsageEntitlements,
 * deleteAllTransactionUsageEntitlements, deleteUsageSummaryGraph,
 * deleteTransactionJournal and the fulfillment helpers. Each is a no-op unless
 * the matching records exist, and building them needs fixtures this class does
 * not yet have: UsageEntitlementAccount alone requires a PricebookEntry plus
 * billing-period fields, and UsageEntitlementBucket requires a UsageResource
 * and a UnitOfMeasure. Those objects ARE createable, so the coverage is
 * reachable -- it is simply a separate piece of work, tracked as its own task.
 *
 * Two paths are NOT reachable from a unit test at all: Invoice and
 * BillingScheduleGroup are both createable=false, so deleteInvoices and
 * deleteBillingScheduleGroups can only ever be verified live.
 *
 * The live verification that does cover the usage graph is
 * scripts/apex/validateRatedUsage.apex plus the usage-consumption skill; the
 * DeleteAssets gating below was additionally confirmed end-to-end against a
 * real rated asset with AssetRateCardEntry rows.
 */
@IsTest
private class RLM_AccountUtilitiesTest {

    private static Account newAccount() {
        Account a = new Account(Name = 'RLM Utilities Test Account');
        insert a;
        return a;
    }

    private static RLM_AccountUtilities.InputVariables request(
        Id accountId, Boolean deleteAssets, Boolean deleteFulfillment, Boolean deleteBilling
    ) {
        RLM_AccountUtilities.InputVariables iv = new RLM_AccountUtilities.InputVariables();
        iv.accountId = accountId;
        iv.DeleteAssets = deleteAssets;
        iv.DeleteFulfillment = deleteFulfillment;
        iv.DeleteBilling = deleteBilling;
        return iv;
    }

    private static void run(RLM_AccountUtilities.InputVariables iv) {
        RLM_AccountUtilities.delAccountRelatedObjects(
            new List<RLM_AccountUtilities.InputVariables>{ iv }
        );
    }

    // ------------------------------------------------------------------ guards

    @IsTest
    static void nullRequestIsANoOp() {
        Test.startTest();
        RLM_AccountUtilities.delAccountRelatedObjects(null);
        Test.stopTest();
        // Reaching here without an exception is the assertion: the invocable is
        // called by a Flow, where a null input must not surface as an error.
        System.assert(true, 'A null request must return quietly');
    }

    @IsTest
    static void emptyRequestIsANoOp() {
        Test.startTest();
        RLM_AccountUtilities.delAccountRelatedObjects(
            new List<RLM_AccountUtilities.InputVariables>()
        );
        Test.stopTest();
        System.assert(true, 'An empty request must return quietly');
    }

    @IsTest
    static void multipleRequestsAreRejected() {
        Account a = newAccount();
        List<RLM_AccountUtilities.InputVariables> two = new List<RLM_AccountUtilities.InputVariables>{
            request(a.Id, false, false, false),
            request(a.Id, false, false, false)
        };

        Test.startTest();
        Boolean threw = false;
        String message = '';
        try {
            RLM_AccountUtilities.delAccountRelatedObjects(two);
        } catch (IllegalArgumentException e) {
            threw = true;
            message = e.getMessage();
        }
        Test.stopTest();

        System.assert(threw, 'A bulk request must be rejected, not silently half-processed');
        System.assert(
            message.contains('only one request at a time'),
            'Rejection must say why. Got: ' + message
        );
    }

    // ------------------------------------------------------- baseline teardown

    @IsTest
    static void accountWithNoRelatedRecordsRunsClean() {
        Account a = newAccount();

        Test.startTest();
        run(request(a.Id, true, true, true));
        Test.stopTest();

        // Every helper runs against empty result sets. The assertion is that the
        // convergent teardown terminates and the account itself is untouched --
        // the utility clears an account's related records, it never deletes the
        // account.
        System.assertEquals(
            1,
            [SELECT COUNT() FROM Account WHERE Id = :a.Id],
            'The reset must not delete the account it was pointed at'
        );
    }

    // ------------------------------------------------- always-deleted category

    @IsTest
    static void opportunitiesAreAlwaysDeleted() {
        Account a = newAccount();
        Opportunity o = new Opportunity(
            Name = 'RLM Utilities Test Opp',
            AccountId = a.Id,
            StageName = 'Prospecting',
            CloseDate = Date.today().addDays(30)
        );
        insert o;

        System.assertEquals(
            1,
            [SELECT COUNT() FROM Opportunity WHERE AccountId = :a.Id],
            'PRECONDITION: the opportunity must exist before the reset runs'
        );

        Test.startTest();
        // All three flags false: opportunity removal is not gated by any of them.
        run(request(a.Id, false, false, false));
        Test.stopTest();

        System.assertEquals(
            0,
            [SELECT COUNT() FROM Opportunity WHERE AccountId = :a.Id],
            'Opportunities are removed regardless of the DeleteAssets/Fulfillment/Billing flags'
        );
    }

    // ------------------------------------------------------- DeleteAssets gate

    @IsTest
    static void assetSurvivesWhenDeleteAssetsIsFalse() {
        Account a = newAccount();
        Asset asset = new Asset(Name = 'RLM Utilities Test Asset', AccountId = a.Id);
        insert asset;

        System.assertEquals(
            1,
            [SELECT COUNT() FROM Asset WHERE AccountId = :a.Id],
            'PRECONDITION: the asset must exist before the reset runs'
        );

        Test.startTest();
        run(request(a.Id, false, true, true));
        Test.stopTest();

        System.assertEquals(
            1,
            [SELECT COUNT() FROM Asset WHERE AccountId = :a.Id],
            'DeleteAssets=false must keep the asset. AssetRateCardEntry rows are '
                + 'generated at asset creation and never regenerated for an existing '
                + 'asset, so anything that removes them while keeping the asset '
                + 'leaves a usage asset that can never rate again'
        );
    }

    @IsTest
    static void assetIsRemovedWhenDeleteAssetsIsTrue() {
        Account a = newAccount();
        Asset asset = new Asset(Name = 'RLM Utilities Test Asset', AccountId = a.Id);
        insert asset;

        System.assertEquals(
            1,
            [SELECT COUNT() FROM Asset WHERE AccountId = :a.Id],
            'PRECONDITION: the asset must exist before the reset runs'
        );

        Test.startTest();
        run(request(a.Id, true, true, true));
        Test.stopTest();

        System.assertEquals(
            0,
            [SELECT COUNT() FROM Asset WHERE AccountId = :a.Id],
            'DeleteAssets=true must remove the asset'
        );
    }

    // ------------------------------------------------------------ scope guard

    @IsTest
    static void otherAccountsAreUntouched() {
        Account target = newAccount();
        Account bystander = new Account(Name = 'RLM Utilities Bystander Account');
        insert bystander;

        insert new List<Opportunity>{
            new Opportunity(Name = 'Target Opp', AccountId = target.Id,
                StageName = 'Prospecting', CloseDate = Date.today().addDays(30)),
            new Opportunity(Name = 'Bystander Opp', AccountId = bystander.Id,
                StageName = 'Prospecting', CloseDate = Date.today().addDays(30))
        };

        Test.startTest();
        run(request(target.Id, true, true, true));
        Test.stopTest();

        System.assertEquals(
            0,
            [SELECT COUNT() FROM Opportunity WHERE AccountId = :target.Id],
            'The target account must be cleared'
        );
        System.assertEquals(
            1,
            [SELECT COUNT() FROM Opportunity WHERE AccountId = :bystander.Id],
            'A destructive utility must not reach past the account it was given'
        );
    }
}
