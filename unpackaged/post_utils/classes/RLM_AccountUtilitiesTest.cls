/**
 * RLM_AccountUtilitiesTest
 *
 * Regression coverage for the "Preserve Contracts with Contracted Prices" option
 * on RLM_AccountUtilities.delAccountRelatedObjects.
 *
 * The fixture is intentionally narrow (Account + two Draft Contracts, one carrying a
 * ContractItemPrice) so the tests exercise the contract-preservation branch without
 * depending on hard-to-instantiate usage/billing objects. These unit tests are
 * regression protection only; per repo policy the behavioral flow+Apex change is also
 * verified against a live org.
 */
@IsTest
private class RLM_AccountUtilitiesTest {

    /**
     * Seeds an Account with two Draft Contracts:
     *   - priced   : has one ContractItemPrice child (a "contracted price")
     *   - unpriced : has no ContractItemPrice children
     * Returns the Account Id.
     */
    private static Id seedAccountWithContracts() {
        Account acc = new Account(Name = 'RLM Reset Test Account');
        insert acc;

        Product2 prod = new Product2(Name = 'RLM Reset Test Product', IsActive = true);
        insert prod;

        // Back-date the contract start so the ContractItemPrice start (now) is comfortably
        // on/after it regardless of the org timezone offset from GMT.
        Date contractStart = Date.today().addDays(-7);
        Contract priced = new Contract(
            AccountId = acc.Id,
            StartDate = contractStart,
            ContractTerm = 12,
            Status = 'Draft'
        );
        Contract unpriced = new Contract(
            AccountId = acc.Id,
            StartDate = contractStart,
            ContractTerm = 12,
            Status = 'Draft'
        );
        insert new List<Contract>{ priced, unpriced };

        // Give the "priced" contract a contracted price. ContractItemPrice.ContractId is
        // master-detail, so this record is what the preserve semi-join keys on.
        ContractItemPrice cip = new ContractItemPrice(
            ContractId = priced.Id,
            ItemId = prod.Id,
            StartDate = System.now(),
            Price = 100
        );
        insert cip;

        return acc.Id;
    }

    /** Builds the invocable input with the deletion flags set. */
    private static RLM_AccountUtilities.InputVariables baseInput(Id accountId) {
        RLM_AccountUtilities.InputVariables iv = new RLM_AccountUtilities.InputVariables();
        iv.accountId = accountId;
        iv.DeleteAssets = true;
        iv.DeleteFulfillment = true;
        iv.DeleteBilling = true;
        return iv;
    }

    private static Integer contractsWithPricesCount(Id accountId) {
        return [
            SELECT COUNT()
            FROM Contract
            WHERE AccountId = :accountId
            AND Id IN (SELECT ContractId FROM ContractItemPrice)
        ];
    }

    /**
     * Preserve ON: the priced contract (and its ContractItemPrice) survives while the
     * unpriced contract is deleted.
     */
    @IsTest
    static void testPreserveOnKeepsPricedContract() {
        Id accountId = seedAccountWithContracts();

        RLM_AccountUtilities.InputVariables iv = baseInput(accountId);
        iv.PreserveContractsWithContractedPrices = true;

        Test.startTest();
        RLM_AccountUtilities.delAccountRelatedObjects(
            new List<RLM_AccountUtilities.InputVariables>{ iv });
        Test.stopTest();

        System.assertEquals(1, [SELECT COUNT() FROM Contract WHERE AccountId = :accountId],
            'Only the priced contract should remain');
        System.assertEquals(1, contractsWithPricesCount(accountId),
            'The surviving contract should still have its ContractItemPrice');
        System.assertEquals(1, [SELECT COUNT() FROM ContractItemPrice WHERE Contract.AccountId = :accountId],
            'The contracted price should be preserved along with its contract');
    }

    /**
     * Preserve OFF: legacy behavior — every contract on the account is deleted,
     * cascade-deleting its ContractItemPrice children.
     */
    @IsTest
    static void testPreserveOffDeletesAllContracts() {
        Id accountId = seedAccountWithContracts();

        RLM_AccountUtilities.InputVariables iv = baseInput(accountId);
        iv.PreserveContractsWithContractedPrices = false;

        Test.startTest();
        RLM_AccountUtilities.delAccountRelatedObjects(
            new List<RLM_AccountUtilities.InputVariables>{ iv });
        Test.stopTest();

        System.assertEquals(0, [SELECT COUNT() FROM Contract WHERE AccountId = :accountId],
            'All contracts should be deleted when preserve is off');
        System.assertEquals(0, [SELECT COUNT() FROM ContractItemPrice WHERE Contract.AccountId = :accountId],
            'ContractItemPrice records should cascade-delete with their contracts');
    }

    /**
     * Flag omitted (null): proves backward compatibility for callers that do not pass
     * the new invocable variable (e.g. the Draft RLM_Reset_Account flow) — behavior
     * matches preserve OFF.
     */
    @IsTest
    static void testFlagOmittedDeletesAllContracts() {
        Id accountId = seedAccountWithContracts();

        // Intentionally leave PreserveContractsWithContractedPrices unset (null).
        RLM_AccountUtilities.InputVariables iv = baseInput(accountId);

        Test.startTest();
        RLM_AccountUtilities.delAccountRelatedObjects(
            new List<RLM_AccountUtilities.InputVariables>{ iv });
        Test.stopTest();

        System.assertEquals(0, [SELECT COUNT() FROM Contract WHERE AccountId = :accountId],
            'A null preserve flag must behave like preserve off (delete all)');
    }
}
