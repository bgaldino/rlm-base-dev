@isTest
private class RLM_DisputeDetailsControllerTest {

    private static Id fakeId(Schema.SObjectType sot) {
        String prefix = sot.getDescribe().getKeyPrefix();
        // Defensive: a type with no key prefix would otherwise build 'null000...' and throw an
        // unhelpful StringException. Fall back to the Account prefix for such (unused) types.
        if (String.isBlank(prefix)) {
            prefix = Account.SObjectType.getDescribe().getKeyPrefix();
        }
        return Id.valueOf(prefix + '000000000000');
    }

    @isTest
    static void getRelatedNames_nullLists_returnsEmptyMaps() {
        Test.startTest();
        Map<String, Object> result = RLM_DisputeDetailsController.getRelatedNames(null, null);
        Test.stopTest();
        System.assertNotEquals(null, result, 'A non-null result map should always be returned.');
        System.assert(result.containsKey('invoiceNames'), 'invoiceNames key expected.');
        System.assert(result.containsKey('lineNames'), 'lineNames key expected.');
        System.assert(result.containsKey('lineBalances'), 'lineBalances key expected.');
        System.assertEquals(0, ((Map<String, String>) result.get('invoiceNames')).size(),
            'Null invoice ids yield an empty name map.');
    }

    @isTest
    static void getRelatedNames_unknownIds_returnsEmptyMaps() {
        List<Id> invoiceIds = new List<Id>{ fakeId(Invoice.SObjectType) };
        List<Id> invoiceLineIds = new List<Id>{ fakeId(InvoiceLine.SObjectType) };
        Test.startTest();
        Map<String, Object> result = RLM_DisputeDetailsController.getRelatedNames(invoiceIds, invoiceLineIds);
        Test.stopTest();
        System.assertNotEquals(null, result, 'A non-null result map should always be returned.');
        System.assertEquals(0, ((Map<String, String>) result.get('lineNames')).size(),
            'Non-existent line ids yield an empty name map.');
    }

    @isTest
    static void saveApprovedAmounts_nullAndEmpty_noOp() {
        Test.startTest();
        RLM_DisputeDetailsController.saveApprovedAmounts(null);
        RLM_DisputeDetailsController.saveApprovedAmounts(new List<Map<String, Object>>());
        Test.stopTest();
        System.assert(true, 'Null/empty input short-circuits without error.');
    }

    // Exercises the DisputeItem field-discovery + query path with a non-existent item id: a fake
    // id matches no record, so the method must never persist an update. DisputeItem and its
    // ApprovedAmount are required by this bundle (RLM_BillingUIAccessTest checks them).
    @isTest
    static void saveApprovedAmounts_unknownItem_persistsNothing() {
        List<Map<String, Object>> items = new List<Map<String, Object>>{
            new Map<String, Object>{ 'id' => disputeItemFakeId(), 'approvedAmount' => 10 }
        };

        Test.startTest();
        Integer rowsBefore = Limits.getDmlRows();
        try {
            RLM_DisputeDetailsController.saveApprovedAmounts(items);
        } catch (AuraHandledException e) {
            // Either outcome persists nothing; the zero-DML assertion below is the contract.
        }
        Integer rowsAfter = Limits.getDmlRows();
        Test.stopTest();

        System.assertEquals(rowsBefore, rowsAfter,
            'A non-existent DisputeItem id must never cause a record to be updated.');
    }

    // Dispute and DisputeItem are createable (Invoice and InvoiceLine are not), so the save
    // path runs against real dispute items: the approved amount is written, and a blank
    // amount saves as zero.
    @isTest
    static void saveApprovedAmounts_writesTheApprovedAmount() {
        List<Id> itemIds = newDisputeItems(2, 5);
        List<Map<String, Object>> items = new List<Map<String, Object>>{
            new Map<String, Object>{ 'id' => String.valueOf(itemIds[0]), 'approvedAmount' => 40 },
            new Map<String, Object>{ 'id' => String.valueOf(itemIds[1]), 'approvedAmount' => null }
        };

        Test.startTest();
        RLM_DisputeDetailsController.saveApprovedAmounts(items);
        Test.stopTest();

        assertAmount(40, approvedAmount(itemIds[0]), 'The approved amount is saved.');
        assertAmount(0, approvedAmount(itemIds[1]), 'A blank approved amount saves as zero.');
    }

    // A save the database rejects surfaces as an AuraHandledException and leaves the record as
    // it was. The amount is one past what the field can hold, read from its describe.
    @isTest
    static void saveApprovedAmounts_rejectedSave_throwsAndKeepsTheAmount() {
        List<Id> itemIds = newDisputeItems(1, 5);
        Schema.DescribeFieldResult approvedField = Schema.getGlobalDescribe().get('DisputeItem').getDescribe()
            .fields.getMap().get('ApprovedAmount').getDescribe();
        Integer integerDigits = approvedField.getPrecision() - approvedField.getScale();
        Assert.isTrue(integerDigits > 0, 'PRECONDITION: ApprovedAmount has a bounded precision. Got ' + integerDigits);
        Decimal tooLarge = Decimal.valueOf(10).pow(integerDigits);
        List<Map<String, Object>> items = new List<Map<String, Object>>{
            new Map<String, Object>{ 'id' => String.valueOf(itemIds[0]), 'approvedAmount' => String.valueOf(tooLarge) }
        };
        // Control: a valid amount on the same item saves.
        saveAmount(itemIds[0], 20);
        assertAmount(20, approvedAmount(itemIds[0]), 'PRECONDITION: a valid amount saves on this item.');

        Boolean rejected = false;
        Test.startTest();
        try {
            RLM_DisputeDetailsController.saveApprovedAmounts(items);
        } catch (AuraHandledException e) {
            // The controller builds its message without setMessage, so in a test getMessage()
            // returns only 'Script-thrown exception'; the describe-derived amount is the premise
            // that ties the failure to the save.
            rejected = true;
        }
        Test.stopTest();

        Assert.isTrue(rejected, 'An amount of ' + tooLarge + ' is past the field\'s range and is reported to the page.');
        assertAmount(20, approvedAmount(itemIds[0]), 'The rejected save leaves the approved amount unchanged.');
    }

    // A user who cannot query DisputeItem cannot approve an amount: whichever check stops them
    // (no DisputeItem, no approved-amount field, or the user-mode query), the page gets an
    // AuraHandledException and the record is unchanged. The admin saves the same item first.
    @isTest
    static void saveApprovedAmounts_userWithoutDisputeAccess_isRejected() {
        User noAccess = RLM_BillingUITestUsers.create(new List<String>(), new List<String>());
        List<Id> itemIds = newDisputeItems(1, 5);
        List<Map<String, Object>> items = new List<Map<String, Object>>{
            new Map<String, Object>{ 'id' => String.valueOf(itemIds[0]), 'approvedAmount' => 40 }
        };
        // Control: the admin saves a valid amount on the same item.
        saveAmount(itemIds[0], 20);
        assertAmount(20, approvedAmount(itemIds[0]), 'PRECONDITION: the admin saves an amount on this item.');

        Boolean rejected = false;
        Boolean canQuery = true;
        Test.startTest();
        System.runAs(noAccess) {
            try {
                Database.query('SELECT Id FROM DisputeItem LIMIT 1', AccessLevel.USER_MODE);
            } catch (Exception e) {
                canQuery = false;
            }
            try {
                RLM_DisputeDetailsController.saveApprovedAmounts(items);
            } catch (AuraHandledException e) {
                rejected = true;
            }
        }
        Test.stopTest();

        Assert.isFalse(canQuery, 'PRECONDITION: the user cannot query DisputeItem in user mode.');
        Assert.isTrue(rejected, 'A user without dispute access is refused.');
        assertAmount(20, approvedAmount(itemIds[0]), 'The refused save leaves the approved amount unchanged.');
    }

    // One dispute on its own case, with the given number of items, each approved at the given
    // amount. Created by name, as RLM_AccountUtilitiesTest does; Dispute and DisputeItem are
    // required by this bundle (RLM_BillingUIAccessTest checks DisputeItem.ApprovedAmount).
    private static List<Id> newDisputeItems(Integer count, Decimal approved) {
        Account a = new Account(Name = 'RLM Dispute Details Test');
        insert a;
        Case disputeCase = new Case(AccountId = a.Id, Subject = 'RLM Dispute Details case');
        insert disputeCase;
        SObject dispute = Schema.getGlobalDescribe().get('Dispute').newSObject();
        dispute.put('AccountId', a.Id);
        dispute.put('CaseId', disputeCase.Id);
        dispute.put('ReceivedDate', Date.today());
        insert dispute;
        List<SObject> items = new List<SObject>();
        for (Integer i = 0; i < count; i++) {
            SObject item = Schema.getGlobalDescribe().get('DisputeItem').newSObject();
            item.put('DisputeId', dispute.Id);
            item.put('TransactionDate', Date.today());
            item.put('DisputedAmount', (Decimal) 100);
            item.put('ApprovedAmount', approved);
            items.add(item);
        }
        insert items;
        List<Id> ids = new List<Id>();
        for (SObject item : items) {
            ids.add(item.Id);
        }
        return ids;
    }

    private static void saveAmount(Id itemId, Decimal amount) {
        RLM_DisputeDetailsController.saveApprovedAmounts(new List<Map<String, Object>>{
            new Map<String, Object>{ 'id' => String.valueOf(itemId), 'approvedAmount' => amount }
        });
    }

    private static Decimal approvedAmount(Id itemId) {
        List<SObject> rows = Database.query('SELECT ApprovedAmount FROM DisputeItem WHERE Id = :itemId');
        return (Decimal) rows[0].get('ApprovedAmount');
    }

    // Compares amounts by value, so 40 and 40.00 match.
    private static void assertAmount(Decimal expected, Decimal actual, String message) {
        Assert.isTrue(actual != null && actual == expected,
            message + ' Expected ' + expected + ', got ' + actual + '.');
    }

    private static Id disputeItemFakeId() {
        if (Schema.getGlobalDescribe().containsKey('DisputeItem')) {
            String prefix = Schema.getGlobalDescribe().get('DisputeItem').getDescribe().getKeyPrefix();
            if (String.isNotBlank(prefix)) {
                return Id.valueOf(prefix + '000000000000');
            }
        }
        // DisputeItem absent or prefix-less: any well-formed id drives the object-not-found path.
        return fakeId(Account.SObjectType);
    }
}
