@isTest
private class RLM_InvoiceProductSummaryControllerTest {

    private static Id fakeInvoiceId() {
        return fakeId(Invoice.SObjectType);
    }

    private static Id fakeId(Schema.SObjectType objectType) {
        return Id.valueOf(objectType.getDescribe().getKeyPrefix() + '000000000000');
    }

    // A Minimum Access user with no license and no permission set: it can read no billing or
    // asset object, so every USER_MODE query the controller makes throws for it.
    private static User userWithoutBillingAccess() {
        return RLM_BillingUITestUsers.create(new List<String>(), new List<String>());
    }

    // Positive paths run as this user, not the deploying admin: RLM_BillingUI is assigned only
    // after this bundle deploys, so the admin may not hold its grants yet.
    private static User billingOperationsUser() {
        return RLM_BillingUITestUsers.create(
            new List<String>{ 'RLM_BillingUI', 'RevenueLifecycleManagementBillingOperations' },
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL });
    }

    // Returns the error a USER_MODE query raises for the running user, or null if it runs.
    private static String userModeError(String soql) {
        try {
            Database.query(soql, AccessLevel.USER_MODE);
            return null;
        } catch (QueryException e) {
            return e.getMessage();
        }
    }

    // An asset on the account, owned by the user when the org exposes Asset.OwnerId (some orgs'
    // describe has no asset owner field).
    private static Asset newAssetOwnedBy(User u, String name, Id accountId) {
        Asset a = new Asset(Name = name, AccountId = accountId);
        if (Asset.SObjectType.getDescribe().fields.getMap().containsKey('OwnerId')) {
            a.put('OwnerId', u.Id);
        }
        insert a;
        return a;
    }

    private static final String ASSET_STATE_PERIOD_READ =
        'SELECT Id, AssetId, StartDate FROM AssetStatePeriod LIMIT 1';
    private static final String ASSET_ATTRIBUTE_READ =
        'SELECT AssetStatePeriodId, AttributeName, AttributeValue FROM AssetStatePeriodAttribute LIMIT 1';

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
            Assert.areEqual(RLM_InvoiceProductSummaryController.LOAD_FAILED_MESSAGE, e.getMessage(),
                'The page gets a fixed sentence, not the query error');
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
        User u = billingOperationsUser();
        Id fakeBsg = fakeId(BillingScheduleGroup.SObjectType);
        Integer lookupQueries;
        Map<Id, Id> saveResult;
        Test.startTest();
        System.runAs(u) {
            String readError = userModeError('SELECT Id, ReferenceEntityId FROM BillingScheduleGroup LIMIT 1');
            Assert.isNull(readError, 'PRECONDITION: a billing operations user can read BillingScheduleGroup: ' + readError);
            Integer queriesBefore = Limits.getQueries();
            saveResult = RLM_InvoiceProductSummaryController.resolveBsgToAsset(new Set<Id>{ fakeBsg }, true);
            lookupQueries = Limits.getQueries() - queriesBefore;
        }
        Test.stopTest();
        Assert.areEqual(1, lookupQueries, 'The BillingScheduleGroup lookup runs.');
        Assert.isTrue(saveResult.isEmpty(), 'An unknown billing schedule group maps to no asset.');
    }

    // An asset with no state period has no attributes to show: the helper stops after the
    // state-period query and returns no entry for it. The billing operations user owns the
    // account, and owns the asset only when Asset has an OwnerId field (newAssetOwnedBy checks).
    @isTest
    static void resolveAssetAttributes_assetWithoutStatePeriods_returnsNoEntry() {
        User u = billingOperationsUser();
        Account acc = new Account(Name = 'RLM Product Summary Asset Test', OwnerId = u.Id);
        insert acc;
        Asset a = newAssetOwnedBy(u, 'RLM Product Summary Asset', acc.Id);

        Integer lookupQueries;
        Map<Id, List<RLM_InvoiceProductSummaryController.AssetAttributeDetail>> result;
        Test.startTest();
        System.runAs(u) {
            String readError = userModeError(ASSET_STATE_PERIOD_READ);
            Assert.isNull(readError, 'PRECONDITION: a billing operations user can read AssetStatePeriod: ' + readError);
            Integer queriesBefore = Limits.getQueries();
            result = RLM_InvoiceProductSummaryController.resolveAssetAttributes(new Set<Id>{ a.Id }, true);
            lookupQueries = Limits.getQueries() - queriesBefore;
        }
        Test.stopTest();

        Assert.areEqual(1, lookupQueries, 'With no state period found, the attribute query must not run.');
        Assert.isTrue(result.isEmpty(), 'An asset with no state period has no attributes.');
    }

    // Once a state period exists, the helper runs the attribute query too. With no
    // AssetStatePeriodAttribute rows it still returns no entry: an asset only appears once it
    // has an attribute. The billing operations user owns the account, and owns the asset only
    // when Asset has an OwnerId field (newAssetOwnedBy checks). The state period has no owner to
    // set, so the test checks that the user can see it.
    @isTest
    static void resolveAssetAttributes_statePeriodWithoutAttributes_returnsNoEntry() {
        User u = billingOperationsUser();
        Account acc = new Account(Name = 'RLM Product Summary Period Test', OwnerId = u.Id);
        insert acc;
        Asset a = newAssetOwnedBy(u, 'RLM Product Summary Period Asset', acc.Id);
        AssetStatePeriod period = new AssetStatePeriod(
            AssetId = a.Id,
            StartDate = Datetime.now().addDays(-30),
            EndDate = Datetime.now().addDays(335),
            Quantity = 1,
            Amount = 0,
            Mrr = 0
        );
        insert period;

        Integer lookupQueries;
        Map<Id, List<RLM_InvoiceProductSummaryController.AssetAttributeDetail>> result;
        Test.startTest();
        System.runAs(u) {
            String periodError = userModeError(ASSET_STATE_PERIOD_READ);
            Assert.isNull(periodError, 'PRECONDITION: a billing operations user can read AssetStatePeriod: ' + periodError);
            String attributeError = userModeError(ASSET_ATTRIBUTE_READ);
            Assert.isNull(attributeError,
                'PRECONDITION: a billing operations user can read AssetStatePeriodAttribute: ' + attributeError);
            Assert.areEqual(1, [SELECT COUNT() FROM AssetStatePeriod WHERE Id = :period.Id WITH USER_MODE],
                'PRECONDITION: the billing operations user can see the state period.');
            Integer queriesBefore = Limits.getQueries();
            result = RLM_InvoiceProductSummaryController.resolveAssetAttributes(new Set<Id>{ a.Id }, true);
            lookupQueries = Limits.getQueries() - queriesBefore;
        }
        Test.stopTest();

        Assert.areEqual(2, lookupQueries,
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

    // For an unknown invoice a billing operations user's save returns as a no-op. For a user who
    // cannot read invoice lines, the same call must report failure as a handled error rather
    // than return as if it had saved.
    @isTest
    static void saveLineAttributes_userWhoCannotReadInvoiceLines_failsWithAHandledError() {
        User billingUser = billingOperationsUser();
        User u = userWithoutBillingAccess();
        Boolean premise = false;
        Boolean saveThrew = false;
        Test.startTest();
        System.runAs(billingUser) {
            String readError = userModeError(
                'SELECT Id, InvoiceId, BillingScheduleGroupId, RLM_Attributes__c FROM InvoiceLine LIMIT 1');
            Assert.isNull(readError,
                'PRECONDITION: a billing operations user can read the InvoiceLine fields the save reads: ' + readError);
            // The billing user's call returns; an exception here fails the test.
            RLM_InvoiceProductSummaryController.saveLineAttributes(fakeInvoiceId());
        }
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
                Assert.areEqual(RLM_InvoiceProductSummaryController.SAVE_FAILED_MESSAGE, e.getMessage(),
                    'The page gets a fixed sentence, not the query error');
                Assert.isNotNull(e.getCause(), 'The refused read is kept as the cause');
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

    // ─── buildSummary and the save helpers ───────────────────────────────────
    // Invoice lines, billing period items and line relationships cannot be inserted in Apex, so
    // these tests build them with JSON.deserialize and pass them to the methods the controller
    // calls with the rows it queried.

    private static Id fakeId(Schema.SObjectType objectType, Integer n) {
        return Id.valueOf(objectType.getDescribe().getKeyPrefix() + String.valueOf(n).leftPad(12, '0'));
    }

    private static InvoiceLine line(Map<String, Object> fields) {
        return (InvoiceLine) JSON.deserialize(JSON.serialize(fields), InvoiceLine.class);
    }

    private static BillingPeriodItem periodItem(Id lineId, Date startDate, Date endDate) {
        return (BillingPeriodItem) JSON.deserialize(JSON.serialize(new Map<String, Object>{
            'InvoiceLineId' => lineId, 'BillingPeriodStartDate' => startDate, 'BillingPeriodEndDate' => endDate
        }), BillingPeriodItem.class);
    }

    private static InvoiceLineRelationship relationship(Id mainLineId, Id associatedLineId) {
        return (InvoiceLineRelationship) JSON.deserialize(JSON.serialize(new Map<String, Object>{
            'MainInvoiceLineId' => mainLineId, 'AssociatedInvoiceLineId' => associatedLineId
        }), InvoiceLineRelationship.class);
    }

    private static RLM_InvoiceProductSummaryController.AssetAttributeDetail attribute(String label, String value) {
        RLM_InvoiceProductSummaryController.AssetAttributeDetail a =
            new RLM_InvoiceProductSummaryController.AssetAttributeDetail();
        a.label = label;
        a.value = value;
        return a;
    }

    private static RLM_InvoiceProductSummaryController.InvoiceSummaryResult summarize(
        List<InvoiceLine> lines,
        List<BillingPeriodItem> periodItems,
        Map<Id, String> uomNames,
        Map<Id, Id> bsgToAssetId,
        Map<Id, List<RLM_InvoiceProductSummaryController.AssetAttributeDetail>> assetToAttrs,
        List<InvoiceLineRelationship> relationships
    ) {
        return RLM_InvoiceProductSummaryController.buildSummary(
            'EUR', lines, periodItems, uomNames, bsgToAssetId, assetToAttrs, relationships);
    }

    private static RLM_InvoiceProductSummaryController.InvoiceSummaryResult summarize(List<InvoiceLine> lines) {
        return summarize(lines, new List<BillingPeriodItem>(), new Map<Id, String>(), new Map<Id, Id>(),
            new Map<Id, List<RLM_InvoiceProductSummaryController.AssetAttributeDetail>>(),
            new List<InvoiceLineRelationship>());
    }

    private static RLM_InvoiceProductSummaryController.ProductSummary productNamed(
        RLM_InvoiceProductSummaryController.InvoiceSummaryResult result, String name
    ) {
        for (RLM_InvoiceProductSummaryController.ProductSummary ps : result.products) {
            if (ps.productName == name) {
                return ps;
            }
        }
        Assert.fail('No product named ' + name + ' in the summary');
        return null;
    }

    // Lines group by product, products sort by name, and each total adds the line's charge, its
    // tax, and its line amount (charge plus tax when the line amount is blank).
    @isTest
    static void buildSummary_groupsLinesByProductSortsByNameAndTotals() {
        Id beta = fakeId(Product2.SObjectType, 1);
        Id alpha = fakeId(Product2.SObjectType, 2);
        Id unnamed = fakeId(Product2.SObjectType, 3);
        List<InvoiceLine> lines = new List<InvoiceLine>{
            line(new Map<String, Object>{ 'Id' => fakeId(InvoiceLine.SObjectType, 1), 'Name' => 'Beta Z',
                'Product2Id' => beta, 'Product2' => new Map<String, Object>{ 'Name' => 'Beta' },
                'ChargeAmount' => 100, 'TaxAmount' => 10 }),
            line(new Map<String, Object>{ 'Id' => fakeId(InvoiceLine.SObjectType, 2), 'Name' => 'Beta A',
                'Product2Id' => beta, 'Product2' => new Map<String, Object>{ 'Name' => 'Beta' },
                'RLM_Charge_Type__c' => 'Recurring', 'ChargeAmount' => 50, 'LineAmount' => 55 }),
            line(new Map<String, Object>{ 'Id' => fakeId(InvoiceLine.SObjectType, 6), 'Name' => 'Beta M',
                'Product2Id' => beta, 'Product2' => new Map<String, Object>{ 'Name' => 'Beta' },
                'RLM_Charge_Type__c' => 'One Time', 'ChargeAmount' => 0 }),
            line(new Map<String, Object>{ 'Id' => fakeId(InvoiceLine.SObjectType, 3), 'Name' => 'Alpha 1',
                'Product2Id' => alpha, 'Product2' => new Map<String, Object>{ 'Name' => 'Alpha' },
                'RLM_Charge_Type__c' => 'One Time', 'ChargeAmount' => 20, 'TaxAmount' => 2, 'LineAmount' => 22 }),
            line(new Map<String, Object>{ 'Id' => fakeId(InvoiceLine.SObjectType, 4), 'Name' => 'Fee',
                'ChargeAmount' => 5 }),
            line(new Map<String, Object>{ 'Id' => fakeId(InvoiceLine.SObjectType, 5), 'Name' => 'Orphan',
                'Product2Id' => unnamed })
        };

        Test.startTest();
        RLM_InvoiceProductSummaryController.InvoiceSummaryResult result = summarize(lines);
        Test.stopTest();

        List<String> names = new List<String>();
        for (RLM_InvoiceProductSummaryController.ProductSummary ps : result.products) {
            names.add(ps.productName);
        }
        Assert.areEqual(new List<String>{ 'Alpha', 'Beta', 'No Product', 'Unknown Product' }, names,
            'Products sort by name; a line without a product is "No Product", one whose product is not loaded "Unknown Product"');
        RLM_InvoiceProductSummaryController.ProductSummary betaSummary = productNamed(result, 'Beta');
        Assert.areEqual(beta, betaSummary.productId, 'The product id is the group key');
        Assert.areEqual(3, betaSummary.lineCount, 'Every Beta line is counted');
        Assert.areEqual(150, betaSummary.subtotal, 'The subtotal adds the charges');
        Assert.areEqual(10, betaSummary.taxAmount, 'A blank tax counts as zero');
        Assert.areEqual(165, betaSummary.totalWithTax, 'Charge plus tax where the line amount is blank (110), else the line amount (55)');
        Assert.areEqual('Recurring', betaSummary.chargeType, 'The first charge type found fills a blank one; a later one does not replace it');
        Assert.areEqual('NO_PRODUCT', productNamed(result, 'No Product').productId, 'A line without a product is keyed NO_PRODUCT');
        Assert.areEqual(6, result.totalLines, 'Every line is counted');
        Assert.areEqual(175, result.grandSubtotal, 'The grand subtotal adds every product');
        Assert.areEqual(12, result.grandTax, 'The grand tax adds every product');
        Assert.areEqual(192, result.grandTotal, 'The grand total adds every product');
        Assert.areEqual('EUR', result.currencyCode, 'The currency is the invoice\'s');
        RLM_InvoiceProductSummaryController.InvoiceLineDetail first = betaSummary.lines[0];
        Assert.areEqual('Beta Z', first.name, 'Lines keep their query order within a product, not name order');
        Assert.areEqual('EUR', first.currencyCode, 'Each line carries the invoice currency');
        Assert.isFalse(first.isUsage, 'A line without a usage charge type is not usage');
    }

    // With dated billing period items, a line's period is the earliest start and the latest end
    // (a blank value on the first item would be kept; these items are all dated). A line with no
    // billing period item keeps its own dates. A usage line gets its overage, unit of measure and rate.
    @isTest
    static void buildSummary_periodsAndUsageLines() {
        Id usageLine = fakeId(InvoiceLine.SObjectType, 1);
        Id plainLine = fakeId(InvoiceLine.SObjectType, 2);
        Id noQuantityLine = fakeId(InvoiceLine.SObjectType, 3);
        Id blankQuantityLine = fakeId(InvoiceLine.SObjectType, 4);
        Id uom = fakeId(UnitOfMeasure.SObjectType, 1);
        Date d = Date.newInstance(2026, 1, 1);
        List<InvoiceLine> lines = new List<InvoiceLine>{
            line(new Map<String, Object>{ 'Id' => usageLine, 'Name' => 'Data', 'RLM_Charge_Type__c' => 'usage resource',
                'Quantity' => 3, 'ChargeAmount' => 10, 'UsageOverageQuantity' => 2, 'UnitOfMeasureId' => uom,
                'InvoiceLineStartDate' => d.addYears(1), 'InvoiceLineEndDate' => d.addYears(1) }),
            line(new Map<String, Object>{ 'Id' => plainLine, 'Name' => 'Plain', 'Quantity' => 2, 'UnitPrice' => 4,
                'ChargeAmount' => 8, 'Type' => 'Charge', 'Description' => 'A plain line',
                'UnitOfMeasureId' => uom, 'UsageOverageQuantity' => 1,
                'InvoiceLineStartDate' => d, 'InvoiceLineEndDate' => d.addDays(30) }),
            line(new Map<String, Object>{ 'Id' => noQuantityLine, 'Name' => 'Free data',
                'RLM_Charge_Type__c' => 'Usage Resource', 'Quantity' => 0, 'ChargeAmount' => 1 }),
            line(new Map<String, Object>{ 'Id' => blankQuantityLine, 'Name' => 'Unmetered data',
                'RLM_Charge_Type__c' => 'Usage Resource', 'ChargeAmount' => 1 })
        };
        List<BillingPeriodItem> periods = new List<BillingPeriodItem>{
            periodItem(usageLine, d.addMonths(1), d.addMonths(2)),
            periodItem(usageLine, d, d.addMonths(1).addDays(14)),
            periodItem(usageLine, d.addMonths(2), d.addMonths(5)),
            periodItem(usageLine, d.addMonths(3), d.addMonths(3).addDays(14))
        };

        Test.startTest();
        RLM_InvoiceProductSummaryController.InvoiceSummaryResult result = summarize(lines, periods,
            new Map<Id, String>{ uom => 'GB' }, new Map<Id, Id>(),
            new Map<Id, List<RLM_InvoiceProductSummaryController.AssetAttributeDetail>>(),
            new List<InvoiceLineRelationship>());
        Test.stopTest();

        Map<String, RLM_InvoiceProductSummaryController.InvoiceLineDetail> byName =
            new Map<String, RLM_InvoiceProductSummaryController.InvoiceLineDetail>();
        for (RLM_InvoiceProductSummaryController.InvoiceLineDetail ld : productNamed(result, 'No Product').lines) {
            byName.put(ld.name, ld);
        }
        RLM_InvoiceProductSummaryController.InvoiceLineDetail usage = byName.get('Data');
        Assert.areEqual(d, usage.periodStartDate,
            'The earliest billing period start wins, not the first or last item\'s, nor the line\'s own date');
        Assert.areEqual(d.addMonths(5), usage.periodEndDate,
            'The latest billing period end wins, not the first, last or earliest-starting item\'s');
        Assert.isTrue(usage.isUsage, 'The usage charge type matches in any case');
        Assert.areEqual(2, usage.overageQty, 'A usage line carries its overage');
        Assert.areEqual('GB', usage.unitOfMeasure, 'A usage line names its unit of measure');
        Assert.areEqual(3.3333, usage.rate, 'The rate is the charge per unit, to four places');
        Assert.areEqual(usageLine, usage.lineId, 'The line id is kept');

        RLM_InvoiceProductSummaryController.InvoiceLineDetail plain = byName.get('Plain');
        Assert.areEqual(d, plain.periodStartDate, 'A line with no billing period keeps its start date');
        Assert.areEqual(d.addDays(30), plain.periodEndDate, 'A line with no billing period keeps its end date');
        Assert.areEqual(2, plain.quantity, 'The quantity is kept');
        Assert.areEqual(4, plain.unitPrice, 'The unit price is kept');
        Assert.areEqual(8, plain.totalWithTax, 'No tax and no line amount: the total is the charge');
        Assert.areEqual('Charge', plain.type, 'The line type is kept');
        Assert.areEqual('A plain line', plain.description, 'The description is kept');
        Assert.isFalse(plain.isUsage, 'A line without the usage charge type is not usage');
        Assert.isNull(plain.unitOfMeasure, 'Only a usage line names its unit of measure');
        Assert.isNull(plain.overageQty, 'Only a usage line carries its overage');
        Assert.isNull(plain.rate, 'Only a usage line gets a rate');

        Assert.isNull(byName.get('Free data').rate, 'A usage line with a zero quantity has no rate');
        Assert.isNull(byName.get('Unmetered data').rate, 'A usage line with a blank quantity has no rate');
    }

    // A line's schedule group leads to its asset; each product gets one block merging its
    // assets' attributes, one per label (compared without case).
    @isTest
    static void buildSummary_mergesAssetAttributesPerProduct() {
        Id product = fakeId(Product2.SObjectType, 1);
        Id bsgA = fakeId(BillingScheduleGroup.SObjectType, 1);
        Id bsgB = fakeId(BillingScheduleGroup.SObjectType, 2);
        Id assetA = fakeId(Asset.SObjectType, 1);
        Id assetB = fakeId(Asset.SObjectType, 2);
        Map<String, Object> productRef = new Map<String, Object>{ 'Name' => 'Router' };
        List<InvoiceLine> lines = new List<InvoiceLine>{
            line(new Map<String, Object>{ 'Id' => fakeId(InvoiceLine.SObjectType, 1), 'Name' => 'Router 1',
                'Product2Id' => product, 'Product2' => productRef, 'BillingScheduleGroupId' => bsgA }),
            line(new Map<String, Object>{ 'Id' => fakeId(InvoiceLine.SObjectType, 2), 'Name' => 'Router 2',
                'Product2Id' => product, 'Product2' => productRef, 'BillingScheduleGroupId' => bsgA }),
            line(new Map<String, Object>{ 'Id' => fakeId(InvoiceLine.SObjectType, 3), 'Name' => 'Router 3',
                'Product2Id' => product, 'Product2' => productRef, 'BillingScheduleGroupId' => bsgB })
        };
        Map<Id, List<RLM_InvoiceProductSummaryController.AssetAttributeDetail>> attrs =
            new Map<Id, List<RLM_InvoiceProductSummaryController.AssetAttributeDetail>>{
                assetA => new List<RLM_InvoiceProductSummaryController.AssetAttributeDetail>{
                    attribute('Color', 'Red'), attribute('Size', 'L') },
                assetB => new List<RLM_InvoiceProductSummaryController.AssetAttributeDetail>{
                    attribute('color', 'Blue'), attribute('Ports', '8') }
            };

        Test.startTest();
        RLM_InvoiceProductSummaryController.InvoiceSummaryResult result = summarize(lines,
            new List<BillingPeriodItem>(), new Map<Id, String>(),
            new Map<Id, Id>{ bsgA => assetA, bsgB => assetB }, attrs, new List<InvoiceLineRelationship>());
        Test.stopTest();

        RLM_InvoiceProductSummaryController.ProductSummary router = productNamed(result, 'Router');
        Assert.areEqual(String.valueOf(assetA), router.lines[0].assetId, 'A line names the asset its schedule group resolves to');
        Assert.areEqual(1, router.assetBlocks.size(), 'A product has one merged attribute block');
        RLM_InvoiceProductSummaryController.AssetBlock block = router.assetBlocks[0];
        Assert.areEqual('merged', block.assetId, 'The block is the merged one');
        Assert.isNull(block.assetName, 'The merged block has no asset name');
        List<String> merged = new List<String>();
        for (RLM_InvoiceProductSummaryController.AssetAttributeDetail a : block.attributes) {
            merged.add(a.label + '=' + a.value);
        }
        Assert.areEqual(new List<String>{ 'Color=Red', 'Size=L', 'Ports=8' }, merged,
            'Each label appears once, compared without case; the first asset\'s value wins');
    }

    // Bundle lines: a component is nested under its parent and left out of the product list, a
    // line can be both, and a parent named like its product is marked suppressed.
    @isTest
    static void buildSummary_nestsBundleComponentsUnderTheirParent() {
        Id bundleProduct = fakeId(Product2.SObjectType, 1);
        Id parent = fakeId(InvoiceLine.SObjectType, 1);
        Id middle = fakeId(InvoiceLine.SObjectType, 2);
        Id leaf = fakeId(InvoiceLine.SObjectType, 3);
        Id sibling = fakeId(InvoiceLine.SObjectType, 4);
        Id otherParent = fakeId(InvoiceLine.SObjectType, 5);
        Id otherChild = fakeId(InvoiceLine.SObjectType, 6);
        Id notOnInvoice = fakeId(InvoiceLine.SObjectType, 7);
        Map<String, Object> bundleRef = new Map<String, Object>{ 'Name' => 'Office Bundle' };
        List<InvoiceLine> lines = new List<InvoiceLine>{
            line(new Map<String, Object>{ 'Id' => parent, 'Name' => 'office bundle', 'Product2Id' => bundleProduct,
                'Product2' => bundleRef, 'ChargeAmount' => 100 }),
            line(new Map<String, Object>{ 'Id' => middle, 'Name' => 'Suite', 'Product2Id' => bundleProduct,
                'Product2' => bundleRef, 'ChargeAmount' => 40 }),
            line(new Map<String, Object>{ 'Id' => leaf, 'Name' => 'Seat', 'ChargeAmount' => 10 }),
            line(new Map<String, Object>{ 'Id' => sibling, 'Name' => 'Support', 'Product2Id' => bundleProduct,
                'Product2' => bundleRef, 'ChargeAmount' => 5 }),
            line(new Map<String, Object>{ 'Id' => otherParent, 'Name' => 'Kit', 'ChargeAmount' => 7 }),
            line(new Map<String, Object>{ 'Id' => otherChild, 'Name' => 'Cable', 'ChargeAmount' => 1 })
        };
        List<InvoiceLineRelationship> relationships = new List<InvoiceLineRelationship>{
            relationship(parent, middle),
            relationship(middle, leaf),
            relationship(parent, sibling),
            relationship(otherParent, otherChild),
            relationship(notOnInvoice, fakeId(InvoiceLine.SObjectType, 8)),
            relationship(null, otherParent)
        };

        Test.startTest();
        RLM_InvoiceProductSummaryController.InvoiceSummaryResult result = summarize(lines,
            new List<BillingPeriodItem>(), new Map<Id, String>(), new Map<Id, Id>(),
            new Map<Id, List<RLM_InvoiceProductSummaryController.AssetAttributeDetail>>(), relationships);
        Test.stopTest();

        RLM_InvoiceProductSummaryController.ProductSummary bundle = productNamed(result, 'Office Bundle');
        Assert.areEqual(1, bundle.lines.size(), 'Components are not listed as product lines');
        Assert.areEqual(100, bundle.subtotal, 'Only top-level lines add to the product totals');
        RLM_InvoiceProductSummaryController.InvoiceLineDetail top = bundle.lines[0];
        Assert.isTrue(top.isParent, 'The bundle line is a parent');
        Assert.areEqual('Bundle Parent', top.bundleRole, 'A parent that is no component is a Bundle Parent');
        Assert.isTrue(top.isSuppressedParent, 'A parent named like its product (any case) is suppressed');
        Assert.areEqual(2, top.components.size(), 'Both direct components are nested under the parent');
        RLM_InvoiceProductSummaryController.InvoiceLineDetail suite;
        for (RLM_InvoiceProductSummaryController.InvoiceLineDetail c : top.components) {
            if (c.name == 'Suite') suite = c;
        }
        Assert.isNotNull(suite, 'The nested bundle line is among the parent\'s components');
        Assert.isTrue(suite.isParent && suite.isComponent, 'A nested bundle line is both a parent and a component');
        Assert.areEqual('Bundle Component', suite.bundleRole, 'A line that is both is labelled a component');
        Assert.areEqual('Seat', suite.components[0].name, 'Nesting goes more than one level deep');

        RLM_InvoiceProductSummaryController.ProductSummary loose = productNamed(result, 'No Product');
        Assert.areEqual(1, loose.lines.size(), 'Only the top-level line of the other bundle is listed');
        Assert.isFalse(loose.lines[0].isSuppressedParent, 'A parent not named like its product is not suppressed');
        Assert.areEqual(6, result.totalLines, 'Every line on the invoice is counted');
    }

    // The save writes attributes only to lines whose field is blank, and only for a line whose
    // schedule group resolves to an asset that has attributes. Values are escaped.
    @isTest
    static void saveHelpers_writeAnEscapedTableOnlyWhereThereIsSomethingToWrite() {
        Id written = fakeId(InvoiceLine.SObjectType, 1);
        Id bsgWithAsset = fakeId(BillingScheduleGroup.SObjectType, 1);
        Id bsgWithoutAsset = fakeId(BillingScheduleGroup.SObjectType, 2);
        Id bsgEmptyAsset = fakeId(BillingScheduleGroup.SObjectType, 3);
        Id assetWithAttrs = fakeId(Asset.SObjectType, 1);
        Id emptyAsset = fakeId(Asset.SObjectType, 2);
        List<InvoiceLine> queried = new List<InvoiceLine>{
            line(new Map<String, Object>{ 'Id' => written, 'BillingScheduleGroupId' => bsgWithAsset }),
            line(new Map<String, Object>{ 'Id' => fakeId(InvoiceLine.SObjectType, 2),
                'BillingScheduleGroupId' => bsgWithAsset, 'RLM_Attributes__c' => '<p>kept</p>' }),
            line(new Map<String, Object>{ 'Id' => fakeId(InvoiceLine.SObjectType, 3),
                'BillingScheduleGroupId' => bsgWithoutAsset }),
            line(new Map<String, Object>{ 'Id' => fakeId(InvoiceLine.SObjectType, 4),
                'BillingScheduleGroupId' => bsgEmptyAsset })
        };

        Test.startTest();
        List<InvoiceLine> blank = RLM_InvoiceProductSummaryController.linesWithoutAttributes(queried);
        List<InvoiceLine> updates = RLM_InvoiceProductSummaryController.attributeUpdates(blank,
            new Map<Id, Id>{ bsgWithAsset => assetWithAttrs, bsgEmptyAsset => emptyAsset },
            new Map<Id, List<RLM_InvoiceProductSummaryController.AssetAttributeDetail>>{
                assetWithAttrs => new List<RLM_InvoiceProductSummaryController.AssetAttributeDetail>{
                    attribute('Plan <b>', 'A&B'), attribute(null, null) },
                emptyAsset => new List<RLM_InvoiceProductSummaryController.AssetAttributeDetail>()
            });
        Test.stopTest();

        Assert.areEqual(3, blank.size(), 'A line that already has attributes is not rewritten');
        Assert.areEqual(1, updates.size(), 'Only the line whose asset has attributes is written');
        Assert.areEqual(written, updates[0].Id, 'The update targets that line');
        String html = updates[0].RLM_Attributes__c;
        Assert.isTrue(html.startsWith('<table'), 'The attributes are written as a table. Got: ' + html);
        Assert.isTrue(html.contains('>Plan &lt;b&gt;<'), 'Labels are escaped. Got: ' + html);
        Assert.isTrue(html.contains('>A&amp;B<'), 'Values are escaped. Got: ' + html);
        Integer emptyCell = html.indexOf('></td><td');
        Assert.isTrue(emptyCell > 0 && html.indexOf('>—<', emptyCell) > emptyCell,
            'A blank label is an empty cell, followed by a dash for the blank value. Got: ' + html);
    }

    // The attributes found are grouped under the asset whose state period they belong to, in
    // query order; one from a state period not in the map is dropped.
    @isTest
    static void attributesByAsset_groupsAttributesUnderTheirAsset() {
        Id assetA = fakeId(Asset.SObjectType, 1);
        Id assetB = fakeId(Asset.SObjectType, 2);
        Id periodA = fakeId(AssetStatePeriod.SObjectType, 1);
        Id periodB = fakeId(AssetStatePeriod.SObjectType, 2);
        Id otherPeriod = fakeId(AssetStatePeriod.SObjectType, 3);
        List<AssetStatePeriodAttribute> rows = new List<AssetStatePeriodAttribute>();
        for (List<Object> r : new List<List<Object>>{
            new List<Object>{ periodA, 'Size', 'L' },
            new List<Object>{ periodB, 'Ports', '8' },
            new List<Object>{ periodA, 'Color', 'Red' },
            new List<Object>{ otherPeriod, 'Color', 'Green' }
        }) {
            rows.add((AssetStatePeriodAttribute) JSON.deserialize(JSON.serialize(new Map<String, Object>{
                'AssetStatePeriodId' => r[0], 'AttributeName' => r[1], 'AttributeValue' => r[2]
            }), AssetStatePeriodAttribute.class));
        }

        Test.startTest();
        Map<Id, List<RLM_InvoiceProductSummaryController.AssetAttributeDetail>> result =
            RLM_InvoiceProductSummaryController.attributesByAsset(rows,
                new Map<Id, Id>{ periodA => assetA, periodB => assetB });
        Test.stopTest();

        Assert.areEqual(new Set<Id>{ assetA, assetB }, result.keySet(), 'Only assets with a mapped period get an entry');
        Assert.areEqual(2, result.get(assetA).size(), 'Both of asset A\'s attributes are kept');
        Assert.areEqual('Size', result.get(assetA)[0].label, 'Attributes keep their query order, not label order');
        Assert.areEqual('L', result.get(assetA)[0].value, 'The value comes with its label');
        Assert.areEqual('Red', result.get(assetA)[1].value, 'Each attribute keeps its own value');
        Assert.areEqual('8', result.get(assetB)[0].value, 'Asset B gets its own attribute');
    }
}
