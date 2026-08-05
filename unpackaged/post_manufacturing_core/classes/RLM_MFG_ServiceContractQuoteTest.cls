@isTest
private class RLM_MFG_ServiceContractQuoteTest {

    // PST itself is not exercised here (it cannot run in an isolated unit-test context);
    // these tests cover the invocable's reachable input-validation and early-return branches.
    private static RLM_MFG_ServiceContractQuote.svcContractRequest makeRequest(
            List<SObject> assets, String productId, String priceBookId) {
        RLM_MFG_ServiceContractQuote.svcContractRequest r =
            new RLM_MFG_ServiceContractQuote.svcContractRequest();
        r.assets = assets;
        r.productId = productId;
        r.priceBookId = priceBookId;
        r.priceBookEntryId = null;
        r.productRelationshipTypeId = null;
        return r;
    }

    @isTest
    static void nullInput_returnsEmpty() {
        Test.startTest();
        List<String> r = RLM_MFG_ServiceContractQuote.createUpdateQuote(null);
        Test.stopTest();
        System.assertEquals(0, r.size(), 'Null input returns an empty list');
    }

    @isTest
    static void emptyAssets_returnsEmpty() {
        Test.startTest();
        List<String> r = RLM_MFG_ServiceContractQuote.createUpdateQuote(
            new List<RLM_MFG_ServiceContractQuote.svcContractRequest>{
                makeRequest(new List<Asset>(), null, null)
            });
        Test.stopTest();
        System.assertEquals(0, r.size(), 'Empty asset list returns an empty list before any PST call');
    }

    @isTest
    static void onlyChildAssets_returnsEmpty() {
        Account acct = new Account(Name = 'Test Account');
        insert acct;
        Product2 prod = new Product2(Name = 'Generator', IsActive = true);
        insert prod;
        Asset parent = new Asset(Name = 'Parent', AccountId = acct.Id, Product2Id = prod.Id);
        insert parent;
        Asset child = new Asset(Name = 'Child', AccountId = acct.Id, Product2Id = prod.Id, ParentId = parent.Id);
        insert child;

        Test.startTest();
        // Passing only the child asset: the ParentId = null filter discards it, so no root
        // asset remains and the method returns empty before reaching PST.
        List<String> r = RLM_MFG_ServiceContractQuote.createUpdateQuote(
            new List<RLM_MFG_ServiceContractQuote.svcContractRequest>{
                makeRequest(new List<Asset>{ child }, null, null)
            });
        Test.stopTest();
        System.assertEquals(0, r.size(), 'A request with only child assets returns empty');
    }

    @isTest
    static void invalidProductId_throwsFriendlyError() {
        Account acct = new Account(Name = 'Test Account');
        insert acct;
        Product2 prod = new Product2(Name = 'Generator', IsActive = true);
        insert prod;
        Asset root = new Asset(Name = 'Root', AccountId = acct.Id, Product2Id = prod.Id);
        insert root;

        Test.startTest();
        Boolean threw = false;
        try {
            // A real root asset lets execution reach the productId validation.
            RLM_MFG_ServiceContractQuote.createUpdateQuote(
                new List<RLM_MFG_ServiceContractQuote.svcContractRequest>{
                    makeRequest(new List<Asset>{ root }, 'not-an-id', Test.getStandardPricebookId())
                });
        } catch (RLM_MFG_ServiceContractQuote.RLM_MFG_ServiceContractQuoteException ex) {
            threw = true;
            System.assert(ex.getMessage().contains('Invalid product id'),
                'Expected friendly invalid-id message');
        }
        Test.stopTest();

        System.assert(threw, 'Malformed product id should throw a friendly, catchable error');
    }
}
