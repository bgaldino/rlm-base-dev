/**
 * Tests for RLM_BillingScheduleGroupService.
 *
 * The native standard-action invoke (createBillingSchedulesFromTrxn) cannot be
 * executed deterministically in a unit test, so the create-via-API path is
 * covered through the @TestVisible mock seam (mockActionOutputs) plus direct
 * coverage of the pure payload-build and result-parse helpers. Validation guards
 * are covered by asserting AuraHandledException on bad input.
 */
@isTest
private class RLM_BillingScheduleGroupServiceTest {
    private static Id fakeId(Schema.SObjectType t) {
        return (Id) (t.getDescribe().getKeyPrefix() + '000000000000');
    }

    @isTest
    static void getAccountBillingInfo_nullArg_throws() {
        Boolean threw = false;
        try {
            RLM_BillingScheduleGroupService.getAccountBillingInfo(null);
        } catch (AuraHandledException e) {
            threw = true;
        }
        System.assert(threw, 'Expected AuraHandledException for null accountId');
    }

    @isTest
    static void getAccountBillingInfo_accountNotFound_throws() {
        Boolean threw = false;
        try {
            RLM_BillingScheduleGroupService.getAccountBillingInfo(fakeId(Account.SObjectType));
        } catch (AuraHandledException e) {
            threw = true;
        }
        System.assert(threw, 'Expected AuraHandledException for missing account');
    }

    @isTest
    static void getAccountBillingInfo_realAccount_returnsName() {
        Account a = new Account(Name = 'BSG Test Acct');
        insert a;
        BillingAccount ba = new BillingAccount(Name = 'BSG Test BA', AccountId = a.Id);
        insert ba;
        Test.startTest();
        RLM_BillingScheduleGroupService.AccountInfo info =
            RLM_BillingScheduleGroupService.getAccountBillingInfo(a.Id);
        Test.stopTest();
        System.assertEquals('BSG Test Acct', info.accountName);
        System.assertEquals('BSG Test BA', info.billingAccountName, 'Billing account surfaced');
    }

    @isTest
    static void optionQueries_doNotThrow() {
        insert new Product2(Name = 'BSG Software Product', Family = 'Software', IsActive = true);
        Test.startTest();
        RLM_BillingScheduleGroupService.getProducts();
        RLM_BillingScheduleGroupService.getLegalEntities();
        RLM_BillingScheduleGroupService.getTaxTreatments();
        List<RLM_BillingScheduleGroupService.PicklistOption> btu =
            RLM_BillingScheduleGroupService.getBillingScheduleBillingTermUnitOptions();
        List<RLM_BillingScheduleGroupService.PicklistOption> ptu =
            RLM_BillingScheduleGroupService.getPricingTermUnitOptions();
        Test.stopTest();
        System.assert(!btu.isEmpty(), 'Billing term unit options should never be empty (fallback)');
        System.assert(!ptu.isEmpty(), 'Pricing term unit options should never be empty (fallback)');
    }

    @isTest
    static void createViaAPI_validationGuards() {
        // Null billing account -> throws before any query.
        System.assert(throwsViaApi(null), 'null billing account throws');
        // Valid-shaped but non-existent billing account -> "not found".
        System.assert(throwsViaApi(fakeId(BillingAccount.SObjectType)), 'missing billing account throws');
    }

    @isTest
    static void createViaAPI_happyPath_returnsRequestId() {
        Account a = new Account(Name = 'BSG ViaApi Acct');
        insert a;
        BillingAccount ba = new BillingAccount(Name = 'BSG ViaApi BA', AccountId = a.Id);
        insert ba;

        RLM_BillingScheduleGroupService.mockActionOutputs = new Map<String, Object>{
            'requestId' => '16PWt000005Dsir',
            'statusUrl' => '/services/data/v67.0/sobjects/AsyncOperationTracker/16PWt000005DsirMAC'
        };

        Test.startTest();
        RLM_BillingScheduleGroupService.CreateResult r =
            RLM_BillingScheduleGroupService.createBillingScheduleGroupAndScheduleViaAPI(
                ba.Id, 'Month', 12, 'Advance', 2, fakeId(LegalEntity.SObjectType),
                fakeId(TaxTreatment.SObjectType), 'USD', 10, 240, 'San Francisco',
                fakeId(Product2.SObjectType), 'Widget', Date.newInstance(2026, 1, 1),
                1, 1, 'Termed', Date.newInstance(2026, 12, 31)
            );
        Test.stopTest();

        System.assertEquals('16PWt000005Dsir', r.requestId, 'requestId surfaced from action output');
    }

    @isTest
    static void buildTransactionDetailsJson_termedIncludesEndAndTotal() {
        String json = RLM_BillingScheduleGroupService.buildTransactionDetailsJson(
            fakeId(Account.SObjectType), fakeId(BillingAccount.SObjectType),
            'Month', 2, fakeId(LegalEntity.SObjectType), fakeId(TaxTreatment.SObjectType),
            'USD', 10, 240, 'San Francisco', fakeId(Product2.SObjectType), 'Widget',
            Date.newInstance(2026, 1, 5), 5, 1, 'Termed', Date.newInstance(2027, 1, 4)
        );
        System.assert(json.contains('"Transaction"'), 'Wrapper present');
        System.assert(json.contains('TransactionId__std'), 'Transaction id present');
        System.assert(json.contains('TotalPrice__std'), 'Termed includes total price');
        System.assert(json.contains('EndDate__std'), 'Termed includes end date');
        System.assert(json.contains('2026-01-05'), 'Start date formatted');
    }

    @isTest
    static void buildTransactionDetailsJson_evergreenIncludesTotalOmitsEnd() {
        String json = RLM_BillingScheduleGroupService.buildTransactionDetailsJson(
            fakeId(Account.SObjectType), fakeId(BillingAccount.SObjectType),
            'Month', 1, fakeId(LegalEntity.SObjectType), fakeId(TaxTreatment.SObjectType),
            'USD', 10, 30, 'San Francisco', fakeId(Product2.SObjectType), 'Widget',
            Date.newInstance(2026, 3, 9), 9, 3, 'Evergreen', null
        );
        // TotalPrice__std is Required for Evergreen new-sale transactions.
        System.assert(json.contains('TotalPrice__std'), 'Evergreen includes total price');
        // Evergreen has no end date.
        System.assert(!json.contains('EndDate__std'), 'Evergreen omits end date');
    }

    @isTest
    static void buildTransactionDetailsJson_oneTimeIncludesTotalOmitsEnd() {
        String json = RLM_BillingScheduleGroupService.buildTransactionDetailsJson(
            fakeId(Account.SObjectType), fakeId(BillingAccount.SObjectType),
            'OneTime', 5, fakeId(LegalEntity.SObjectType), fakeId(TaxTreatment.SObjectType),
            'USD', 10, 50, 'San Francisco', fakeId(Product2.SObjectType), 'Widget',
            Date.newInstance(2026, 2, 20), 20, 2, 'OneTime', null
        );
        // TotalPrice__std is Required for OneTime new-sale transactions.
        System.assert(json.contains('TotalPrice__std'), 'OneTime includes total price');
        // OneTime has no end date.
        System.assert(!json.contains('EndDate__std'), 'OneTime omits end date');
    }

    @isTest
    static void formatIsoDate_padsMonthAndDay() {
        System.assertEquals('2026-02-03',
            RLM_BillingScheduleGroupService.formatIsoDate(Date.newInstance(2026, 2, 3)));
    }

    @isTest
    static void invokeAndParse_viaMockSeam() {
        RLM_BillingScheduleGroupService.mockActionOutputs = new Map<String, Object>{
            'requestId' => '16PWt000005Dsir',
            'statusUrl' => '/services/data/v67.0/sobjects/AsyncOperationTracker/16PWt000005DsirMAC'
        };
        Map<String, Object> out =
            RLM_BillingScheduleGroupService.invokeStandaloneBillingScheduleCreate('{"Transaction":[]}');
        RLM_BillingScheduleGroupService.CreateResult r =
            RLM_BillingScheduleGroupService.parseCreateResult(out);
        System.assertEquals('16PWt000005Dsir', r.requestId);
        System.assert(r.statusUrl.contains('AsyncOperationTracker'), 'statusUrl mapped');
        System.assertNotEquals(null, r.apiResponse, 'apiResponse serialized');
    }

    @isTest
    static void parseCreateResult_handlesNullAndIds() {
        RLM_BillingScheduleGroupService.CreateResult empty =
            RLM_BillingScheduleGroupService.parseCreateResult(null);
        System.assertEquals(null, empty.requestId);

        Id anyId = fakeId(Account.SObjectType);
        Map<String, Object> out = new Map<String, Object>{
            'billingScheduleGroupId' => anyId,
            'billingScheduleIds' => new List<Object>{ anyId }
        };
        RLM_BillingScheduleGroupService.CreateResult r =
            RLM_BillingScheduleGroupService.parseCreateResult(out);
        System.assertEquals(anyId, r.billingScheduleGroupId);
        System.assertEquals(anyId, r.billingScheduleId);
    }

    @isTest
    static void innerClasses_construct() {
        Id acc = fakeId(Account.SObjectType);
        RLM_BillingScheduleGroupService.LegalEntityOption le =
            new RLM_BillingScheduleGroupService.LegalEntityOption(acc, 'LE');
        RLM_BillingScheduleGroupService.TaxTreatmentOption tt =
            new RLM_BillingScheduleGroupService.TaxTreatmentOption(acc, 'TT');
        RLM_BillingScheduleGroupService.ProductOption po =
            new RLM_BillingScheduleGroupService.ProductOption(acc, 'Prod');
        RLM_BillingScheduleGroupService.PicklistOption pl =
            new RLM_BillingScheduleGroupService.PicklistOption('Label', 'Value');
        RLM_BillingScheduleGroupService.AccountInfo ai =
            new RLM_BillingScheduleGroupService.AccountInfo('Acct', acc, 'BA', 'City');
        System.assertEquals('LE', le.name);
        System.assertEquals('TT', tt.name);
        System.assertEquals('Prod', po.name);
        System.assertEquals('Value', pl.value);
        System.assertEquals('City', ai.billingCity);
    }

    // ---- helpers ----
    private static Boolean throwsViaApi(Id billingAccountId) {
        try {
            RLM_BillingScheduleGroupService.createBillingScheduleGroupAndScheduleViaAPI(
                billingAccountId, 'Month', 1, 'Advance', 1, fakeId(LegalEntity.SObjectType),
                fakeId(TaxTreatment.SObjectType), 'USD', 10, 10, 'San Francisco',
                fakeId(Product2.SObjectType), 'Widget', Date.today(), 1, 1, 'Evergreen', null
            );
            return false;
        } catch (AuraHandledException e) {
            return true;
        }
    }
}
