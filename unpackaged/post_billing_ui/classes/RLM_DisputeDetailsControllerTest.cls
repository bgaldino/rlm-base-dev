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

    // A save naming a real item and an unknown one saves the real item and skips the unknown
    // one without reporting it. Run as a Billing Operations user (see billingUser). DisputeItem
    // and its ApprovedAmount are required by this bundle (RLM_BillingUIAccessTest checks them).
    @isTest
    static void saveApprovedAmounts_withAnUnknownItem_savesTheKnownOneAndSkipsTheOther() {
        User approver = billingUser();
        List<Id> itemIds = newDisputeItems(1, 5, approver.Id);
        List<Map<String, Object>> items = new List<Map<String, Object>>{
            new Map<String, Object>{ 'id' => String.valueOf(itemIds[0]), 'approvedAmount' => 30 },
            new Map<String, Object>{ 'id' => disputeItemFakeId(), 'approvedAmount' => 10 }
        };

        Exception caught;
        Test.startTest();
        System.runAs(approver) {
            try {
                RLM_DisputeDetailsController.saveApprovedAmounts(items);
            } catch (Exception e) {
                caught = e;
            }
        }
        Test.stopTest();

        Assert.isNull(caught, 'Known gap: an unmatched item id is skipped and the save reports success. '
            + 'Update this test when it is fixed.');
        assertAmount(30, approvedAmount(itemIds[0]), 'The known item\'s approved amount is saved.');
    }

    // Dispute and DisputeItem are createable (Invoice and InvoiceLine are not), so the save
    // path runs against real dispute items: the approved amount is written, and a blank
    // amount saves as zero. The saves run as a Billing Operations user (see billingUser).
    @isTest
    static void saveApprovedAmounts_writesTheApprovedAmount() {
        User approver = billingUser();
        List<Id> itemIds = newDisputeItems(2, 5, approver.Id);
        List<Map<String, Object>> items = new List<Map<String, Object>>{
            new Map<String, Object>{ 'id' => String.valueOf(itemIds[0]), 'approvedAmount' => 40 },
            new Map<String, Object>{ 'id' => String.valueOf(itemIds[1]), 'approvedAmount' => null }
        };

        Test.startTest();
        System.runAs(approver) {
            RLM_DisputeDetailsController.saveApprovedAmounts(items);
        }
        Test.stopTest();

        assertAmount(40, approvedAmount(itemIds[0]), 'The approved amount is saved.');
        assertAmount(0, approvedAmount(itemIds[1]), 'A blank approved amount saves as zero.');
    }

    // A save the database rejects surfaces as an AuraHandledException and leaves the record as
    // it was. The amount is one past what the field can hold, read from its describe.
    @isTest
    static void saveApprovedAmounts_rejectedSave_throwsAndKeepsTheAmount() {
        User approver = billingUser();
        List<Id> itemIds = newDisputeItems(1, 5, approver.Id);
        // Described as the approver, who can see the field.
        Integer integerDigits;
        System.runAs(approver) {
            Schema.DescribeFieldResult approvedField = Schema.getGlobalDescribe().get('DisputeItem').getDescribe()
                .fields.getMap().get('ApprovedAmount').getDescribe();
            integerDigits = approvedField.getPrecision() - approvedField.getScale();
        }
        Assert.isTrue(integerDigits > 0, 'PRECONDITION: ApprovedAmount has a bounded precision. Got ' + integerDigits);
        Decimal tooLarge = Decimal.valueOf(10).pow(integerDigits);
        List<Map<String, Object>> items = new List<Map<String, Object>>{
            new Map<String, Object>{ 'id' => String.valueOf(itemIds[0]), 'approvedAmount' => String.valueOf(tooLarge) }
        };
        // Control: the same user saves a valid amount on the same item.
        System.runAs(approver) {
            saveAmount(itemIds[0], 20);
        }
        assertAmount(20, approvedAmount(itemIds[0]), 'PRECONDITION: a valid amount saves on this item.');

        Boolean rejected = false;
        Test.startTest();
        System.runAs(approver) {
            try {
                RLM_DisputeDetailsController.saveApprovedAmounts(items);
            } catch (AuraHandledException e) {
                // The controller builds its message without setMessage, so in a test getMessage()
                // returns only 'Script-thrown exception'; the describe-derived amount is the
                // premise that ties the failure to the save.
                rejected = true;
            }
        }
        Test.stopTest();

        Assert.isTrue(rejected, 'An amount of ' + tooLarge + ' is rejected and reported to the page.');
        assertAmount(20, approvedAmount(itemIds[0]), 'The rejected save leaves the approved amount unchanged.');
    }

    // A user who cannot query DisputeItem cannot approve an amount: whichever check stops them
    // (no DisputeItem, no approved-amount field, or the user-mode query), the page gets an
    // AuraHandledException and the record is unchanged. A Billing Operations user saves the same
    // item first.
    @isTest
    static void saveApprovedAmounts_userWithoutDisputeAccess_isRejected() {
        User noAccess = RLM_BillingUITestUsers.create(new List<String>(), new List<String>());
        User approver = billingUser();
        List<Id> itemIds = newDisputeItems(1, 5, approver.Id);
        List<Map<String, Object>> items = new List<Map<String, Object>>{
            new Map<String, Object>{ 'id' => String.valueOf(itemIds[0]), 'approvedAmount' => 40 }
        };
        // Control: the Billing Operations user saves a valid amount on the same item.
        System.runAs(approver) {
            saveAmount(itemIds[0], 20);
        }
        assertAmount(20, approvedAmount(itemIds[0]), 'PRECONDITION: a billing user saves an amount on this item.');

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

    // The saves run as a Billing Operations user holding RLM_BillingUI rather than the deploying
    // admin: the admin's DisputeItem.ApprovedAmount access comes from RLM_RCB, which a build only
    // recalculates after this bundle deploys. The user takes a Billing seat for the test.
    private static User billingUser() {
        return RLM_BillingUITestUsers.create(
            new List<String>{ 'RLM_BillingUI', 'RevenueLifecycleManagementBillingOperations' },
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL });
    }

    // One dispute on its own case, owned by the given user (Dispute is private), with the given
    // number of items, each approved at the given amount. Created by name, as
    // RLM_AccountUtilitiesTest does; Dispute and DisputeItem are required by this bundle
    // (RLM_BillingUIAccessTest checks DisputeItem.ApprovedAmount).
    private static List<Id> newDisputeItems(Integer count, Decimal approved, Id ownerId) {
        Account a = new Account(Name = 'RLM Dispute Details Test');
        insert a;
        Case disputeCase = new Case(AccountId = a.Id, Subject = 'RLM Dispute Details case');
        insert disputeCase;
        SObject dispute = Schema.getGlobalDescribe().get('Dispute').newSObject();
        dispute.put('AccountId', a.Id);
        dispute.put('CaseId', disputeCase.Id);
        dispute.put('ReceivedDate', Date.today());
        dispute.put('OwnerId', ownerId);
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

    // A well-formed DisputeItem id that matches no record. DisputeItem is required by this bundle.
    private static Id disputeItemFakeId() {
        String prefix = Schema.getGlobalDescribe().get('DisputeItem').getDescribe().getKeyPrefix();
        return Id.valueOf(prefix + '000000000000');
    }
}
