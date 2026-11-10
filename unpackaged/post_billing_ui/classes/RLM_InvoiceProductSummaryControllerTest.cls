@isTest
private class RLM_InvoiceProductSummaryControllerTest {

    private static Id fakeInvoiceId() {
        return Id.valueOf(Invoice.SObjectType.getDescribe().getKeyPrefix() + '000000000000');
    }

    private static Id fakeId(Schema.SObjectType objectType) {
        return Id.valueOf(objectType.getDescribe().getKeyPrefix() + '000000000000');
    }

    // A Minimum Access user with no license and no permission set: it can read no billing or
    // asset object, so every USER_MODE query the controller makes throws for it.
    private static User userWithoutBillingAccess() {
        return RLM_BillingUITestUsers.create(new List<String>(), new List<String>());
    }

    // Invoices/InvoiceLines are system-managed and not insertable in Apex tests. A non-existent
    // invoice makes the single-row Invoice query throw, surfaced as an AuraHandledException.
    @isTest
    static void getInvoiceProductSummary_unknownInvoice_throws() {
        Boolean threw = false;
        Test.startTest();
        try {
            RLM_InvoiceProductSummaryController.getInvoiceProductSummary(fakeInvoiceId());
        } catch (AuraHandledException e) {
            threw = true;
        }
        Test.stopTest();
        System.assert(threw, 'A non-existent invoice should raise an AuraHandledException.');
    }

    // No invoice lines -> nothing to update; the method must return without writing any records.
    @isTest
    static void saveLineAttributes_unknownInvoice_noOp() {
        Test.startTest();
        Integer rowsBefore = Limits.getDmlRows();
        RLM_InvoiceProductSummaryController.saveLineAttributes(fakeInvoiceId());
        Integer rowsAfter = Limits.getDmlRows();
        Test.stopTest();
        System.assertEquals(rowsBefore, rowsAfter,
            'A non-existent invoice has no lines, so no records may be updated.');
    }

    // saveLineAttributes needs the line's BillingScheduleGroup to find its asset. For a user who
    // can't read BillingScheduleGroup, the save must fail rather than write nothing and report
    // success; the summary must still render, without attributes. A Billing-licensed user with
    // only RLM_BillingUI is such a user: the object also needs a billing role's user
    // permissions. The premise is checked first, so a platform change that opens the object
    // fails here as a broken premise rather than as a controller regression.
    @isTest
    static void bsgLookup_failsTheSaveButNotTheSummary_whenTheUserCannotReadIt() {
        User u = RLM_BillingUITestUsers.create(
            new List<String>{ 'RLM_BillingUI' },
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL });
        Id fakeBsg = Id.valueOf(BillingScheduleGroup.SObjectType.getDescribe().getKeyPrefix() + '000000000000');
        Boolean premise = false;
        Boolean saveThrew = false;
        Map<Id, Id> summaryResult;
        System.runAs(u) {
            try {
                Database.query('SELECT Id FROM BillingScheduleGroup LIMIT 1', AccessLevel.USER_MODE);
            } catch (QueryException e) {
                premise = true;
            }
            try {
                RLM_InvoiceProductSummaryController.resolveBsgToAsset(new Set<Id>{ fakeBsg }, true);
            } catch (QueryException e) {
                saveThrew = true;
            }
            summaryResult = RLM_InvoiceProductSummaryController.resolveBsgToAsset(new Set<Id>{ fakeBsg }, false);
        }
        Assert.isTrue(premise, 'Premise: this user must be unable to read BillingScheduleGroup.');
        Assert.isTrue(saveThrew, 'The save path must surface a BillingScheduleGroup read it may not run.');
        Assert.isTrue(summaryResult.isEmpty(), 'The summary path degrades to no assets.');
    }

    // Both helpers short-circuit on null or empty input, before any query, whichever caller
    // (the save or the summary) asks.
    @isTest
    static void resolveHelpers_nullOrEmptyInput_returnEmptyMapsWithoutQuerying() {
        Test.startTest();
        Integer queriesBefore = Limits.getQueries();
        Map<Id, Id> bsgFromNull = RLM_InvoiceProductSummaryController.resolveBsgToAsset(null, true);
        Map<Id, Id> bsgFromEmpty = RLM_InvoiceProductSummaryController.resolveBsgToAsset(new Set<Id>(), false);
        Map<Id, List<RLM_InvoiceProductSummaryController.AssetAttributeDetail>> attrsFromNull =
            RLM_InvoiceProductSummaryController.resolveAssetAttributes(null, true);
        Map<Id, List<RLM_InvoiceProductSummaryController.AssetAttributeDetail>> attrsFromEmpty =
            RLM_InvoiceProductSummaryController.resolveAssetAttributes(new Set<Id>(), false);
        Integer queriesAfter = Limits.getQueries();
        Test.stopTest();

        Assert.isTrue(bsgFromNull.isEmpty(), 'Null BSG ids resolve to no assets.');
        Assert.isTrue(bsgFromEmpty.isEmpty(), 'Empty BSG ids resolve to no assets.');
        Assert.isTrue(attrsFromNull.isEmpty(), 'Null asset ids resolve to no attributes.');
        Assert.isTrue(attrsFromEmpty.isEmpty(), 'Empty asset ids resolve to no attributes.');
        Assert.areEqual(queriesBefore, queriesAfter, 'Empty input must not run a query.');
    }

    // The other side of the BSG gate: a billing role can read BillingScheduleGroup, so even the
    // save path (failLoudly) runs the lookup without throwing; a group that does not exist maps
    // to no asset.
    @isTest
    static void resolveBsgToAsset_billingRole_runsTheLookupOnTheSavePath() {
        User u = RLM_BillingUITestUsers.create(
            new List<String>{ 'RLM_BillingUI', 'RevenueLifecycleManagementBillingOperations' },
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL });
        Id fakeBsg = fakeId(BillingScheduleGroup.SObjectType);
        String readError;
        Integer lookupQueries;
        Map<Id, Id> saveResult;
        Test.startTest();
        System.runAs(u) {
            try {
                Database.query('SELECT Id, ReferenceEntityId FROM BillingScheduleGroup LIMIT 1', AccessLevel.USER_MODE);
            } catch (QueryException e) {
                readError = e.getMessage();
            }
            Integer queriesBefore = Limits.getQueries();
            saveResult = RLM_InvoiceProductSummaryController.resolveBsgToAsset(new Set<Id>{ fakeBsg }, true);
            lookupQueries = Limits.getQueries() - queriesBefore;
        }
        Test.stopTest();
        Assert.isNull(readError, 'PRECONDITION: a billing operations user can read BillingScheduleGroup: ' + readError);
        Assert.areEqual(1, lookupQueries, 'The BillingScheduleGroup lookup runs.');
        Assert.isTrue(saveResult.isEmpty(), 'An unknown billing schedule group maps to no asset.');
    }

    // An asset with no state period has no attributes to show: the helper stops after the
    // state-period query and returns no entry for it.
    @isTest
    static void resolveAssetAttributes_assetWithoutStatePeriods_returnsNoEntry() {
        Account acc = new Account(Name = 'RLM Product Summary Asset Test');
        insert acc;
        Asset a = new Asset(Name = 'RLM Product Summary Asset', AccountId = acc.Id);
        insert a;

        Test.startTest();
        Integer queriesBefore = Limits.getQueries();
        Map<Id, List<RLM_InvoiceProductSummaryController.AssetAttributeDetail>> result =
            RLM_InvoiceProductSummaryController.resolveAssetAttributes(new Set<Id>{ a.Id }, true);
        Integer queriesAfter = Limits.getQueries();
        Test.stopTest();

        Assert.areEqual(1, queriesAfter - queriesBefore,
            'With no state period found, the attribute query must not run.');
        Assert.isTrue(result.isEmpty(), 'An asset with no state period has no attributes.');
    }

    // Once a state period exists, the helper runs the attribute query too. With no
    // AssetStatePeriodAttribute rows it still returns no entry: an asset only appears once it
    // has an attribute.
    @isTest
    static void resolveAssetAttributes_statePeriodWithoutAttributes_returnsNoEntry() {
        Account acc = new Account(Name = 'RLM Product Summary Period Test');
        insert acc;
        Asset a = new Asset(Name = 'RLM Product Summary Period Asset', AccountId = acc.Id);
        insert a;
        AssetStatePeriod period = new AssetStatePeriod(
            AssetId = a.Id,
            StartDate = Datetime.now().addDays(-30),
            EndDate = Datetime.now().addDays(335),
            Quantity = 1,
            Amount = 0,
            Mrr = 0
        );
        insert period;

        Test.startTest();
        Integer queriesBefore = Limits.getQueries();
        Map<Id, List<RLM_InvoiceProductSummaryController.AssetAttributeDetail>> result =
            RLM_InvoiceProductSummaryController.resolveAssetAttributes(new Set<Id>{ a.Id }, true);
        Integer queriesAfter = Limits.getQueries();
        Test.stopTest();

        Assert.areEqual(2, queriesAfter - queriesBefore,
            'A state period was found, so the attribute query must run after the period query.');
        Assert.isTrue(result.isEmpty(), 'A state period with no attributes resolves no attributes.');
    }

    // The attribute read follows the same rule as the BSG read: the save path (failLoudly)
    // surfaces a read the user may not run; the summary path degrades to no attributes.
    @isTest
    static void resolveAssetAttributes_failsTheSaveButNotTheSummary_whenTheUserCannotReadIt() {
        User u = userWithoutBillingAccess();
        Id fakeAsset = fakeId(Asset.SObjectType);
        Boolean premise = false;
        Boolean saveThrew = false;
        Map<Id, List<RLM_InvoiceProductSummaryController.AssetAttributeDetail>> summaryResult;
        Test.startTest();
        System.runAs(u) {
            try {
                Database.query('SELECT Id FROM AssetStatePeriod LIMIT 1', AccessLevel.USER_MODE);
            } catch (QueryException e) {
                premise = true;
            }
            try {
                RLM_InvoiceProductSummaryController.resolveAssetAttributes(new Set<Id>{ fakeAsset }, true);
            } catch (QueryException e) {
                saveThrew = true;
            }
            summaryResult = RLM_InvoiceProductSummaryController.resolveAssetAttributes(
                new Set<Id>{ fakeAsset }, false);
        }
        Test.stopTest();
        Assert.isTrue(premise, 'PRECONDITION: this user must be unable to read AssetStatePeriod.');
        Assert.isTrue(saveThrew, 'The save path must surface an AssetStatePeriod read it may not run.');
        Assert.isTrue(summaryResult.isEmpty(), 'The summary path returns no attributes instead of throwing.');
    }

    // For an unknown invoice the admin's save returns as a no-op. For a user who cannot read
    // invoice lines, the same call must report failure as a handled error rather than return
    // as if it had saved.
    @isTest
    static void saveLineAttributes_userWhoCannotReadInvoiceLines_failsWithAHandledError() {
        User u = userWithoutBillingAccess();
        Boolean premise = false;
        Boolean saveThrew = false;
        Test.startTest();
        // PRECONDITION: the admin's call returns; an exception here fails the test.
        RLM_InvoiceProductSummaryController.saveLineAttributes(fakeInvoiceId());
        System.runAs(u) {
            try {
                Database.query('SELECT Id FROM InvoiceLine LIMIT 1', AccessLevel.USER_MODE);
            } catch (QueryException e) {
                premise = true;
            }
            try {
                RLM_InvoiceProductSummaryController.saveLineAttributes(fakeInvoiceId());
            } catch (AuraHandledException e) {
                saveThrew = true;
            }
        }
        Test.stopTest();
        Assert.isTrue(premise, 'PRECONDITION: this user must be unable to read InvoiceLine.');
        Assert.isTrue(saveThrew, 'A save the user may not run must fail with an AuraHandledException.');
    }

    // getInvoiceProductSummary returns a new InvoiceSummaryResult for an invoice with no lines,
    // and accumulates totals onto new ProductSummary and InvoiceLineDetail objects: each must
    // start at zero totals, empty (never null) lists, and every bundle flag off.
    @isTest
    static void wrappers_defaultToZeroTotalsAndEmptyLists() {
        Test.startTest();
        RLM_InvoiceProductSummaryController.InvoiceSummaryResult result =
            new RLM_InvoiceProductSummaryController.InvoiceSummaryResult();
        RLM_InvoiceProductSummaryController.ProductSummary product =
            new RLM_InvoiceProductSummaryController.ProductSummary();
        RLM_InvoiceProductSummaryController.InvoiceLineDetail line =
            new RLM_InvoiceProductSummaryController.InvoiceLineDetail();
        RLM_InvoiceProductSummaryController.AssetBlock block =
            new RLM_InvoiceProductSummaryController.AssetBlock();
        Test.stopTest();

        Assert.isTrue(result.products.isEmpty(), 'A new result has no products.');
        Assert.areEqual(0, result.grandSubtotal, 'A new result has a zero subtotal.');
        Assert.areEqual(0, result.grandTax, 'A new result has zero tax.');
        Assert.areEqual(0, result.grandTotal, 'A new result has a zero total.');
        Assert.areEqual(0, result.totalLines, 'A new result has no lines.');
        Assert.isNull(result.currencyCode, 'The currency is set from the invoice, not defaulted.');

        Assert.areEqual(0, product.lineCount, 'A new product summary has no lines.');
        Assert.areEqual(0, product.subtotal, 'A new product summary has a zero subtotal.');
        Assert.areEqual(0, product.taxAmount, 'A new product summary has zero tax.');
        Assert.areEqual(0, product.totalWithTax, 'A new product summary has a zero total.');
        Assert.isTrue(product.lines.isEmpty(), 'A new product summary has an empty line list.');
        Assert.isTrue(product.assetBlocks.isEmpty(), 'A new product summary has no attribute blocks.');

        Assert.isFalse(line.isUsage, 'A line is not usage until its charge type says so.');
        Assert.isFalse(line.isParent, 'A line is not a bundle parent by default.');
        Assert.isFalse(line.isComponent, 'A line is not a bundle component by default.');
        Assert.isFalse(line.isSuppressedParent, 'A line is not suppressed by default.');
        Assert.isTrue(line.components.isEmpty(), 'A line has an empty component list.');
        Assert.isNull(line.bundleRole, 'A line has no bundle role by default.');

        Assert.isTrue(block.attributes.isEmpty(), 'A new attribute block has an empty attribute list.');
    }
}
