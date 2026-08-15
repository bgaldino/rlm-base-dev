/**
 * RLM_UsageUploaderControllerTest
 *
 * Test class for RLM_UsageUploaderController.
 * Tests all CRUD operations for usage uploading on Revenue Cloud assets.
 */
@IsTest
private class RLM_UsageUploaderControllerTest {

    /**
     * Creates test data: Account, Product, UoM, UsageResource, ProductUsageResource, Asset
     */
    @TestSetup
    static void setupTestData() {
        // Account
        Account acc = new Account(Name = 'Test Account');
        insert acc;

        // Product — must have UsageModelType for ProductUsageResource linkage
        Product2 prod = new Product2(
            Name = 'Test Usage Product',
            IsActive = true,
            UsageModelType = 'Anchor'
        );
        insert prod;

        // Unit of Measure Class — must be created in Draft, then activated
        UnitOfMeasureClass uomClass = new UnitOfMeasureClass(
            Name = 'Data Volume',
            Code = 'DATA_VOL',
            Type = 'Usage',
            Status = 'Draft'
        );
        insert uomClass;
        uomClass.Status = 'Active';
        update uomClass;

        // Unit of Measure — must be created in Draft, then activated
        UnitOfMeasure uom = new UnitOfMeasure(
            Name = 'Gigabyte',
            UnitCode = 'GB',
            Type = 'Usage',
            UnitOfMeasureClassId = uomClass.Id,
            Status = 'Draft'
        );
        insert uom;
        uom.Status = 'Active';
        update uom;

        // Usage Resource — must be created in Draft, then activated
        UsageResource ur = new UsageResource(
            Name = 'Data Storage',
            Code = 'DATA_STORAGE',
            Category = 'Usage',
            Status = 'Draft',
            DefaultUnitOfMeasureId = uom.Id,
            UnitOfMeasureClassId = uomClass.Id
        );
        insert ur;
        ur.Status = 'Active';
        update ur;

        // Product Usage Resource — must be created in Draft, then activated
        ProductUsageResource pur = new ProductUsageResource(
            ProductId = prod.Id,
            UsageResourceId = ur.Id,
            Status = 'Draft',
            EffectiveStartDate = Datetime.now().addDays(-30),
            IsOptional = false
        );
        insert pur;
        pur.Status = 'Active';
        update pur;

        // Asset
        Asset ast = new Asset(
            Name = 'Test Usage Asset',
            AccountId = acc.Id,
            Product2Id = prod.Id
        );
        insert ast;
    }

    // ─── Helper Methods ─────────────────────────────────────────────────

    static Asset getTestAsset() {
        return [SELECT Id, Product2Id FROM Asset WHERE Name = 'Test Usage Asset' LIMIT 1];
    }

    static UsageResource getTestUsageResource() {
        return [SELECT Id, Name, DefaultUnitOfMeasureId FROM UsageResource WHERE Name = 'Data Storage' LIMIT 1];
    }

    // ─── getUsageResourcesForAsset Tests ────────────────────────────────

    @IsTest
    static void testGetUsageResourcesForAsset_ReturnsResources() {
        Asset ast = getTestAsset();

        Test.startTest();
        List<RLM_UsageUploaderController.UsageResourceWrapper> resources =
            RLM_UsageUploaderController.getUsageResourcesForAsset(ast.Id);
        Test.stopTest();

        System.assertEquals(1, resources.size(), 'Should return 1 usage resource');
        System.assertEquals('Data Storage', resources[0].resourceName);
        System.assertEquals('Gigabyte', resources[0].unitOfMeasureName);
        System.assertEquals('GB', resources[0].unitOfMeasureCode);
        System.assertNotEquals(null, resources[0].resourceId);
        System.assertNotEquals(null, resources[0].unitOfMeasureId);
        System.assertNotEquals(null, resources[0].unitOfMeasureClassId);
        System.assertNotEquals(null, resources[0].availableUoms);
        System.assert(resources[0].availableUoms.size() >= 1, 'Should have at least 1 available UoM');
        // Verify available UoM contains the default Gigabyte
        Boolean foundGb = false;
        for (RLM_UsageUploaderController.UomOption opt : resources[0].availableUoms) {
            if (opt.uomCode == 'GB') {
                foundGb = true;
                System.assertEquals('Gigabyte', opt.uomName);
            }
        }
        System.assert(foundGb, 'Available UoMs should include Gigabyte (GB)');
    }

    @IsTest
    static void testGetUsageResourcesForAsset_NoProduct() {
        Account acc = [SELECT Id FROM Account LIMIT 1];
        Asset noProductAsset = new Asset(Name = 'No Product Asset', AccountId = acc.Id);
        insert noProductAsset;

        Test.startTest();
        Boolean exceptionThrown = false;
        try {
            RLM_UsageUploaderController.getUsageResourcesForAsset(noProductAsset.Id);
        } catch (AuraHandledException e) {
            exceptionThrown = true;
        }
        Test.stopTest();

        System.assert(exceptionThrown, 'Should have thrown AuraHandledException for asset without product');
    }

    // ─── uploadUsage Tests ──────────────────────────────────────────────

    @IsTest
    static void testUploadUsage_SingleRecord() {
        Asset ast = getTestAsset();
        UsageResource ur = getTestUsageResource();

        Test.startTest();
        Id journalId = RLM_UsageUploaderController.uploadUsage(
            ast.Id,
            ur.Id,
            150.0,
            Date.today(),
            null
        );
        Test.stopTest();

        System.assertNotEquals(null, journalId, 'Should return a journal ID');

        TransactionJournal tj = [
            SELECT Id, ReferenceRecordId, UsageResourceId, Quantity,
                   ActivityDate, Status, UsageType, QuantityUnitOfMeasureId
            FROM TransactionJournal
            WHERE Id = :journalId
        ];

        System.assertEquals(ast.Id, tj.ReferenceRecordId);
        System.assertEquals(ur.Id, tj.UsageResourceId);
        System.assertEquals(150.0, tj.Quantity);
        // When unitOfMeasureId is null, should fall back to the resource's default UoM
        System.assertEquals(ur.DefaultUnitOfMeasureId, tj.QuantityUnitOfMeasureId);
        // ActivityDate is a datetime stored in UTC — allow 1-day offset from timezone conversion
        Integer dayDiff = Math.abs(Date.today().daysBetween(tj.ActivityDate.date()));
        System.assert(dayDiff <= 1, 'ActivityDate should be within 1 day of today, got: ' + tj.ActivityDate);
        System.assertEquals('Pending', tj.Status);
        System.assertEquals('UsageManagement', tj.UsageType);
    }

    @IsTest
    static void testUploadUsage_DefaultUom() {
        Asset ast = getTestAsset();
        UsageResource ur = getTestUsageResource();

        Test.startTest();
        Id journalId = RLM_UsageUploaderController.uploadUsage(
            ast.Id, ur.Id, 50.0, Date.today(), null
        );
        Test.stopTest();

        System.assertNotEquals(null, journalId, 'Should create journal');
    }

    @IsTest
    static void testUploadUsage_WithExplicitUom() {
        Asset ast = getTestAsset();
        UsageResource ur = getTestUsageResource();

        // Create a second UoM in the same class for explicit selection
        UnitOfMeasureClass uomClass = [SELECT Id FROM UnitOfMeasureClass WHERE Code = 'DATA_VOL' LIMIT 1];
        UnitOfMeasure uom2 = new UnitOfMeasure(
            Name = 'Megabyte',
            UnitCode = 'MB',
            Type = 'Usage',
            UnitOfMeasureClassId = uomClass.Id,
            Status = 'Draft'
        );
        insert uom2;
        uom2.Status = 'Active';
        update uom2;

        Test.startTest();
        Id journalId = RLM_UsageUploaderController.uploadUsage(
            ast.Id, ur.Id, 1024.0, Date.today(), uom2.Id
        );
        Test.stopTest();

        TransactionJournal tj = [
            SELECT QuantityUnitOfMeasureId FROM TransactionJournal WHERE Id = :journalId
        ];
        System.assertEquals(uom2.Id, tj.QuantityUnitOfMeasureId,
            'Should use the explicitly provided UoM, not the default');
    }

    // ─── validateUsageEntries Tests ─────────────────────────────────────

    @IsTest
    static void testValidateUsageEntries_ValidEntries() {
        Asset ast = getTestAsset();

        List<RLM_UsageUploaderController.UsageEntry> entries = new List<RLM_UsageUploaderController.UsageEntry>();
        RLM_UsageUploaderController.UsageEntry e = new RLM_UsageUploaderController.UsageEntry();
        e.usageResourceName = 'Data Storage';
        e.quantity = 100;
        e.transactionDate = Date.today();
        entries.add(e);

        Test.startTest();
        List<RLM_UsageUploaderController.ValidationResult> results =
            RLM_UsageUploaderController.validateUsageEntries(ast.Id, entries);
        Test.stopTest();

        System.assertEquals(1, results.size());
        System.assertEquals(true, results[0].isValid);
        System.assertNotEquals(null, results[0].resolvedResourceId);
    }

    @IsTest
    static void testValidateUsageEntries_InvalidResource() {
        Asset ast = getTestAsset();

        List<RLM_UsageUploaderController.UsageEntry> entries = new List<RLM_UsageUploaderController.UsageEntry>();
        RLM_UsageUploaderController.UsageEntry e = new RLM_UsageUploaderController.UsageEntry();
        e.usageResourceName = 'NonExistent Resource';
        e.quantity = 100;
        e.transactionDate = Date.today();
        entries.add(e);

        Test.startTest();
        List<RLM_UsageUploaderController.ValidationResult> results =
            RLM_UsageUploaderController.validateUsageEntries(ast.Id, entries);
        Test.stopTest();

        System.assertEquals(false, results[0].isValid);
        System.assert(results[0].errorMessage.contains('Unknown usage resource'));
    }

    @IsTest
    static void testValidateUsageEntries_InvalidQuantity() {
        Asset ast = getTestAsset();

        List<RLM_UsageUploaderController.UsageEntry> entries = new List<RLM_UsageUploaderController.UsageEntry>();
        RLM_UsageUploaderController.UsageEntry e = new RLM_UsageUploaderController.UsageEntry();
        e.usageResourceName = 'Data Storage';
        e.quantity = -5;
        e.transactionDate = Date.today();
        entries.add(e);

        Test.startTest();
        List<RLM_UsageUploaderController.ValidationResult> results =
            RLM_UsageUploaderController.validateUsageEntries(ast.Id, entries);
        Test.stopTest();

        System.assertEquals(false, results[0].isValid);
        System.assert(results[0].errorMessage.contains('Quantity must be greater than 0'));
    }

    @IsTest
    static void testValidateUsageEntries_NullDate() {
        Asset ast = getTestAsset();

        List<RLM_UsageUploaderController.UsageEntry> entries = new List<RLM_UsageUploaderController.UsageEntry>();
        RLM_UsageUploaderController.UsageEntry e = new RLM_UsageUploaderController.UsageEntry();
        e.usageResourceName = 'Data Storage';
        e.quantity = 100;
        e.transactionDate = null;
        entries.add(e);

        Test.startTest();
        List<RLM_UsageUploaderController.ValidationResult> results =
            RLM_UsageUploaderController.validateUsageEntries(ast.Id, entries);
        Test.stopTest();

        System.assertEquals(false, results[0].isValid);
        System.assert(results[0].errorMessage.contains('Transaction date is required'));
    }

    // ─── bulkUploadUsage Tests ──────────────────────────────────────────

    @IsTest
    static void testBulkUploadUsage_MixedEntries() {
        Asset ast = getTestAsset();

        List<RLM_UsageUploaderController.UsageEntry> entries = new List<RLM_UsageUploaderController.UsageEntry>();

        // Valid entry
        RLM_UsageUploaderController.UsageEntry e1 = new RLM_UsageUploaderController.UsageEntry();
        e1.usageResourceName = 'Data Storage';
        e1.quantity = 100;
        e1.transactionDate = Date.today();
        entries.add(e1);

        // Valid entry
        RLM_UsageUploaderController.UsageEntry e2 = new RLM_UsageUploaderController.UsageEntry();
        e2.usageResourceName = 'Data Storage';
        e2.quantity = 200;
        e2.transactionDate = Date.today().addDays(-1);
        entries.add(e2);

        // Invalid entry (bad resource name)
        RLM_UsageUploaderController.UsageEntry e3 = new RLM_UsageUploaderController.UsageEntry();
        e3.usageResourceName = 'Bad Resource';
        e3.quantity = 50;
        e3.transactionDate = Date.today();
        entries.add(e3);

        Test.startTest();
        RLM_UsageUploaderController.BulkUploadResult result =
            RLM_UsageUploaderController.bulkUploadUsage(ast.Id, entries);
        Test.stopTest();

        System.assertEquals(2, result.successCount, 'Should have 2 successful inserts');
        System.assertEquals(1, result.errorCount, 'Should have 1 validation error');
        System.assertEquals(2, result.journalIds.size());
        System.assertEquals(1, result.errors.size());
    }

    // ─── getRatesForAsset Tests ──────────────────────────────────────

    @IsTest
    static void testGetRatesForAsset_NoRates() {
        Asset ast = getTestAsset();

        Test.startTest();
        List<RLM_UsageUploaderController.RateInfoWrapper> rates =
            RLM_UsageUploaderController.getRatesForAsset(ast.Id);
        Test.stopTest();

        System.assertEquals(0, rates.size(), 'Asset without rate card entries should return empty list');
    }

    @IsTest
    static void testGetRatesForAsset_WithRateCard() {
        Asset ast = getTestAsset();
        UsageResource ur = getTestUsageResource();

        // Create a Currency UoM Class + UoM for the rate card entry
        UnitOfMeasureClass currencyClass = new UnitOfMeasureClass(
            Name = 'Currency',
            Code = 'CURRENCY',
            Type = 'Currency',
            Status = 'Draft'
        );
        insert currencyClass;
        currencyClass.Status = 'Active';
        update currencyClass;

        UnitOfMeasure uomCurrency = new UnitOfMeasure(
            Name = 'US Dollar',
            UnitCode = 'USD',
            Type = 'Currency',
            UnitOfMeasureClassId = currencyClass.Id,
            Status = 'Draft'
        );
        insert uomCurrency;
        uomCurrency.Status = 'Active';
        update uomCurrency;

        // Create Rate Card
        RateCard rc = new RateCard(
            Name = 'Test Base Rate Card',
            Type = 'Base',
            EffectiveFrom = Datetime.now().addDays(-30)
        );
        insert rc;

        // Create Rate Card Entry
        RateCardEntry rce = new RateCardEntry(
            RateCardId = rc.Id,
            Rate = 0.05,
            RateUnitOfMeasureId = uomCurrency.Id,
            UsageResourceId = ur.Id,
            EffectiveFrom = Datetime.now().addDays(-30),
            Status = 'Draft'
        );
        insert rce;
        rce.Status = 'Active';
        update rce;

        // Create Asset Rate Card Entry
        AssetRateCardEntry arce = new AssetRateCardEntry(
            AssetId = ast.Id,
            RateCardEntryId = rce.Id,
            StartDate = Datetime.now().addDays(-30)
        );
        insert arce;

        Test.startTest();
        List<RLM_UsageUploaderController.RateInfoWrapper> rates =
            RLM_UsageUploaderController.getRatesForAsset(ast.Id);
        Test.stopTest();

        System.assertEquals(1, rates.size(), 'Should return 1 rate entry');
        System.assertEquals('Data Storage', rates[0].usageResourceName);
        System.assertEquals(0.05, rates[0].baseRate);
        System.assertEquals('Test Base Rate Card', rates[0].rateCardName);
    }

    // ─── getGrantsForAsset Tests ──────────────────────────────────────

    @IsTest
    static void testGetGrantsForAsset_NoGrants() {
        Asset ast = getTestAsset();

        Test.startTest();
        List<RLM_UsageUploaderController.GrantInfoWrapper> grants =
            RLM_UsageUploaderController.getGrantsForAsset(ast.Id);
        Test.stopTest();

        System.assertEquals(0, grants.size(), 'Asset without entitlements should return empty list');
    }

    // ─── Overage resolution ───────────────────────────────────────────
    //
    // 264 removed TransactionUsageEntitlement.ChargeForOverage, so overage is re-sourced from
    // ProductUsageResourcePolicy. These tests drive OverageLookup directly, which is the seam
    // that makes the resolution assertable: TransactionUsageEntitlement is transactional and
    // its ProductId is not createable, so a test cannot insert an entitlement to drive
    // getGrantsForAsset end to end — but it can assert the exact logic that reads one.

    /**
     * An Anchor entitlement resolves from its own product+resource row.
     */
    @IsTest
    static void testOverageLookup_ResolvesOwnProductResourceRow() {
        Asset ast = getTestAsset();
        UsageResource ur = getTestUsageResource();

        RLM_UsageUploaderController.OverageLookup lookup =
            new RLM_UsageUploaderController.OverageLookup();
        lookup.add(ast.Product2Id, ur.Id, 'Yes');

        System.assertEquals(
            'Yes',
            lookup.resolve(ast.Product2Id, ur.Id),
            'An Anchor entitlement must resolve from its own product+resource policy row'
        );
    }

    /**
     * Regression lock for the Pack and Commit case.
     *
     * Only an Anchor product's policy row may carry a UsageOveragePolicy — the platform rejects
     * it on Pack and Commit — so a Pack or Commit entitlement never has a row under its own
     * product. It must fall back to the resource's Anchor-owned value. Resolving strictly on
     * product+resource blanks these out: on the built 264 org, 8 of 14 entitlements are
     * non-Anchor and 7 of them share a resource with an Anchor that does carry a policy.
     */
    @IsTest
    static void testOverageLookup_FallsBackToResourceForNonAnchorProduct() {
        Asset ast = getTestAsset();
        UsageResource ur = getTestUsageResource();

        Product2 packProduct = new Product2(
            Name = 'Pack Sharing The Anchor Resource',
            IsActive = true,
            UsageModelType = 'Pack'
        );
        insert packProduct;

        // Only the Anchor has a policy row, which is the only shape the platform allows.
        RLM_UsageUploaderController.OverageLookup lookup =
            new RLM_UsageUploaderController.OverageLookup();
        lookup.add(ast.Product2Id, ur.Id, 'Yes');

        System.assertEquals(
            'Yes',
            lookup.resolve(packProduct.Id, ur.Id),
            'A Pack entitlement must inherit the resource\'s Anchor-owned overage value, not blank'
        );
    }

    /**
     * Two Anchors disagreeing about one resource is genuinely ambiguous, so the fallback must
     * withdraw rather than return whichever row SOQL happened to yield last.
     */
    @IsTest
    static void testOverageLookup_WithholdsWhenTwoProductsDisagreeOnOneResource() {
        Asset ast = getTestAsset();
        UsageResource ur = getTestUsageResource();

        Product2 secondAnchor = new Product2(
            Name = 'Second Anchor On Same Resource',
            IsActive = true,
            UsageModelType = 'Anchor'
        );
        insert secondAnchor;

        Product2 unrelatedPack = new Product2(
            Name = 'Pack With No Row Of Its Own',
            IsActive = true,
            UsageModelType = 'Pack'
        );
        insert unrelatedPack;

        RLM_UsageUploaderController.OverageLookup lookup =
            new RLM_UsageUploaderController.OverageLookup();
        lookup.add(ast.Product2Id, ur.Id, 'Yes');
        lookup.add(secondAnchor.Id, ur.Id, 'No');

        System.assertEquals(
            null,
            lookup.resolve(unrelatedPack.Id, ur.Id),
            'A resource two Anchors disagree about must resolve to null, not to either value'
        );

        // Each Anchor still resolves its own row unambiguously.
        System.assertEquals(
            'Yes',
            lookup.resolve(ast.Product2Id, ur.Id),
            'An exact product+resource match must survive resource-level ambiguity'
        );
        System.assertEquals(
            'No',
            lookup.resolve(secondAnchor.Id, ur.Id),
            'An exact product+resource match must survive resource-level ambiguity'
        );
    }

    /**
     * ProductUsageResourcePolicy also carries ProductSellingModelId, so two rows for one
     * product+resource pair are schema-legal. Disagreeing rows must withhold rather than let
     * SOQL order decide.
     */
    @IsTest
    static void testOverageLookup_WithholdsWhenOnePairHasConflictingRows() {
        Asset ast = getTestAsset();
        UsageResource ur = getTestUsageResource();

        RLM_UsageUploaderController.OverageLookup lookup =
            new RLM_UsageUploaderController.OverageLookup();
        lookup.add(ast.Product2Id, ur.Id, 'Yes');
        lookup.add(ast.Product2Id, ur.Id, 'No');

        System.assertEquals(
            null,
            lookup.resolve(ast.Product2Id, ur.Id),
            'Conflicting rows for one product+resource pair must resolve to null'
        );
    }

    /**
     * A resource with no overage policy at all resolves to null, and a null resource cannot
     * match on the product alone.
     */
    @IsTest
    static void testOverageLookup_ResolvesNullWhenNothingGoverns() {
        Asset ast = getTestAsset();
        UsageResource ur = getTestUsageResource();

        RLM_UsageUploaderController.OverageLookup empty =
            new RLM_UsageUploaderController.OverageLookup();

        System.assertEquals(
            null,
            empty.resolve(ast.Product2Id, ur.Id),
            'A resource with no overage policy must resolve to null'
        );
        System.assertEquals(
            null,
            empty.resolve(ast.Product2Id, null),
            'A missing resource must not match on the product alone'
        );

        // A row with no resource is unkeyable and must be ignored outright.
        RLM_UsageUploaderController.OverageLookup lookup =
            new RLM_UsageUploaderController.OverageLookup();
        lookup.add(ast.Product2Id, null, 'Yes');
        System.assertEquals(
            null,
            lookup.resolve(ast.Product2Id, ur.Id),
            'A policy row with no usage resource must not be resolvable'
        );
    }

    /**
     * Covers the query itself — the traversal, the UsageOveragePolicyId filter, and USER_MODE —
     * against real ProductUsageResourcePolicy and UsageOveragePolicy records.
     */
    @IsTest
    static void testLoadOverageLookup_ReadsPolicyFromTheOrg() {
        Asset ast = getTestAsset();
        UsageResource ur = getTestUsageResource();
        ProductUsageResource pur = [
            SELECT Id, ProductId, UsageResourceId FROM ProductUsageResource LIMIT 1
        ];

        UsageOveragePolicy overagePolicy = new UsageOveragePolicy(
            Name = 'Test Overage Policy',
            OverageChargeable = 'Yes'
        );
        insert overagePolicy;

        // The platform requires a rating frequency alongside the overage policy whenever the
        // product is Anchor — "Complete this field when the product associated with the product
        // usage resource is of Anchor usage model type" — which is the same Anchor-centric rule
        // that makes the resource-level fallback in OverageLookup necessary.
        RatingFrequencyPolicy ratingPolicy = new RatingFrequencyPolicy(
            Name = 'Test Rating Frequency Policy',
            RatingPeriod = 'Monthly'
        );
        insert ratingPolicy;

        // UsageAggregationPolicyId points at UsageResourceBillingPolicy, not at an object of
        // the field's own name, and is required on an Anchor row for the same reason.
        UsageResourceBillingPolicy aggregationPolicy = new UsageResourceBillingPolicy(
            Name = 'Test Aggregation Policy',
            Code = 'TEST_AGG',
            Status = 'Draft'
        );
        insert aggregationPolicy;

        insert new ProductUsageResourcePolicy(
            ProductUsageResourceId = pur.Id,
            UsageOveragePolicyId = overagePolicy.Id,
            RatingFrequencyPolicyId = ratingPolicy.Id,
            UsageAggregationPolicyId = aggregationPolicy.Id
        );

        Test.startTest();
        RLM_UsageUploaderController.OverageLookup lookup =
            RLM_UsageUploaderController.loadOverageLookup(new Set<Id>{ ur.Id });
        Test.stopTest();

        System.assertEquals(
            'Yes',
            lookup.resolve(pur.ProductId, ur.Id),
            'The policy row inserted for this product and resource must be readable'
        );
    }

    /**
     * The fail-soft USER_MODE path. Nothing in this repo grants read on
     * ProductUsageResourcePolicy or UsageOveragePolicy, so a low-permission caller's query
     * throws and the catch degrades to a blank overage column rather than taking the whole
     * grants wire down with it.
     *
     * Asserting only "the lookup came back empty" would not test the catch at all — an org
     * that happened to grant the chain would pass identically, and so would a build with the
     * catch deleted if the query never threw. So the query is first shown to throw for this
     * user, which makes the assertion below evidence about the catch specifically. Remove the
     * catch, or narrow it to the wrong exception type, and this test fails.
     */
    @IsTest
    static void testLoadOverageLookup_DegradesToBlankWhenCallerCannotReadPolicies() {
        Asset ast = getTestAsset();
        UsageResource ur = getTestUsageResource();
        Set<Id> resourceIds = new Set<Id>{ ur.Id };
        User lowPermission = buildMinimalAccessUser();

        Boolean rawQueryWasDenied = false;
        RLM_UsageUploaderController.OverageLookup lookup = null;

        System.runAs(lowPermission) {
            try {
                // Negative control: the same traversal the method runs, unguarded.
                List<ProductUsageResourcePolicy> denied = [
                    SELECT Id
                    FROM ProductUsageResourcePolicy
                    WHERE ProductUsageResource.UsageResourceId IN :resourceIds
                    WITH USER_MODE
                ];
                System.debug('policy rows visible to a minimal user: ' + denied.size());
            } catch (QueryException e) {
                rawQueryWasDenied = true;
            }

            lookup = RLM_UsageUploaderController.loadOverageLookup(resourceIds);
        }

        System.assertEquals(
            true,
            rawQueryWasDenied,
            'Premise of this test: a minimal-access user must be denied the policy chain. ' +
            'If this org grants it, the assertions below prove nothing about the catch'
        );
        System.assertNotEquals(
            null,
            lookup,
            'A denied caller must still receive a lookup'
        );
        System.assertEquals(
            null,
            lookup.resolve(ast.Product2Id, ur.Id),
            'A denied caller must get a blank overage column, not a QueryException'
        );
    }

    /**
     * The least-privileged standard profile the org offers, for exercising USER_MODE denial.
     * 'Minimum Access - Salesforce' sorts before 'Standard User', so it wins where it exists
     * and orgs without it still get a user that lacks the Revenue Cloud policy objects.
     */
    private static User buildMinimalAccessUser() {
        Profile leastPrivileged = [
            SELECT Id
            FROM Profile
            WHERE Name IN ('Minimum Access - Salesforce', 'Standard User')
            ORDER BY Name ASC
            LIMIT 1
        ];

        User u = new User(
            ProfileId = leastPrivileged.Id,
            LastName = 'Overage',
            Email = 'rlm.overage.minimal@example.com',
            Username = 'rlm.overage.minimal.' + Datetime.now().getTime() + '@example.com',
            Alias = 'rlmovg',
            TimeZoneSidKey = 'America/Los_Angeles',
            LocaleSidKey = 'en_US',
            EmailEncodingKey = 'UTF-8',
            LanguageLocaleKey = 'en_US'
        );
        insert u;
        return u;
    }

    /**
     * No resources means no query and an empty lookup, not a wasted SOQL call.
     */
    @IsTest
    static void testLoadOverageLookup_SkipsQueryWhenNoResources() {
        Integer before = Limits.getQueries();

        RLM_UsageUploaderController.OverageLookup lookup =
            RLM_UsageUploaderController.loadOverageLookup(new Set<Id>());

        System.assertEquals(
            before,
            Limits.getQueries(),
            'An empty resource set must not consume a SOQL query'
        );
        System.assertEquals(
            null,
            lookup.resolve(getTestAsset().Product2Id, getTestUsageResource().Id),
            'An empty lookup must resolve to null'
        );
    }

    // ─── Wrapper Class Coverage ───────────────────────────────────────

    @IsTest
    static void testWrapperClassInstantiation() {
        // Exercise RateInfoWrapper
        RLM_UsageUploaderController.RateInfoWrapper rw = new RLM_UsageUploaderController.RateInfoWrapper();
        rw.rateCardEntryId = null;
        rw.rateCardName = 'Test';
        rw.rateCardType = 'Standard';
        rw.usageResourceId = null;
        rw.usageResourceName = 'Test Resource';
        rw.baseRate = 10.0;
        rw.negotiatedRate = 8.0;
        rw.rateUomName = 'USD';
        rw.startDate = Datetime.now();
        rw.endDate = Datetime.now().addDays(365);
        rw.tiers = new List<RLM_UsageUploaderController.TierInfo>();

        // Exercise TierInfo
        RLM_UsageUploaderController.TierInfo ti = new RLM_UsageUploaderController.TierInfo();
        ti.lowerBound = 0;
        ti.upperBound = 100;
        ti.adjustmentType = 'Override';
        ti.adjustmentValue = 0.05;
        ti.rateUomName = 'USD';

        // Exercise GrantInfoWrapper
        RLM_UsageUploaderController.GrantInfoWrapper gw = new RLM_UsageUploaderController.GrantInfoWrapper();
        gw.entitlementId = null;
        gw.entitlementName = 'TUE-001';
        gw.usageResourceId = null;
        gw.usageResourceName = 'Compute Time';
        gw.entitlementQuantity = 1000;
        gw.usageModelType = 'Anchor';
        gw.grantType = 'Grant';
        gw.chargeForOverage = 'Yes';
        gw.startDate = Datetime.now();
        gw.endDate = Datetime.now().addDays(30);
        gw.bucketBalance = 800;
        gw.consumedEntitlement = 200;
        gw.totalConsumedEntitlement = 200;

        // Exercise UomOption
        RLM_UsageUploaderController.UomOption uOpt = new RLM_UsageUploaderController.UomOption();
        uOpt.uomId = null;
        uOpt.uomName = 'Gigabyte';
        uOpt.uomCode = 'GB';

        // Exercise UsageResourceWrapper new fields
        RLM_UsageUploaderController.UsageResourceWrapper urw = new RLM_UsageUploaderController.UsageResourceWrapper();
        urw.unitOfMeasureClassId = null;
        urw.availableUoms = new List<RLM_UsageUploaderController.UomOption>{ uOpt };

        // Verify no exceptions thrown
        System.assertNotEquals(null, rw.rateCardName);
        System.assertNotEquals(null, gw.entitlementName);
        System.assertEquals('Gigabyte', uOpt.uomName);
        System.assertEquals(1, urw.availableUoms.size());
    }

    @IsTest
    static void testBulkUploadUsage_AllValid() {
        Asset ast = getTestAsset();

        List<RLM_UsageUploaderController.UsageEntry> entries = new List<RLM_UsageUploaderController.UsageEntry>();

        RLM_UsageUploaderController.UsageEntry e1 = new RLM_UsageUploaderController.UsageEntry();
        e1.usageResourceName = 'data storage'; // test case-insensitive matching
        e1.quantity = 500;
        e1.transactionDate = Date.today();
        entries.add(e1);

        Test.startTest();
        RLM_UsageUploaderController.BulkUploadResult result =
            RLM_UsageUploaderController.bulkUploadUsage(ast.Id, entries);
        Test.stopTest();

        System.assertEquals(1, result.successCount);
        System.assertEquals(0, result.errorCount);
    }

    @IsTest
    static void testValidateUsageEntries_ByResourceId() {
        Asset ast = getTestAsset();
        UsageResource ur = getTestUsageResource();

        List<RLM_UsageUploaderController.UsageEntry> entries = new List<RLM_UsageUploaderController.UsageEntry>();
        RLM_UsageUploaderController.UsageEntry e = new RLM_UsageUploaderController.UsageEntry();
        e.usageResourceId = ur.Id;
        e.quantity = 75;
        e.transactionDate = Date.today();
        entries.add(e);

        Test.startTest();
        List<RLM_UsageUploaderController.ValidationResult> results =
            RLM_UsageUploaderController.validateUsageEntries(ast.Id, entries);
        Test.stopTest();

        System.assertEquals(1, results.size());
        System.assertEquals(true, results[0].isValid);
        System.assertEquals(ur.Id, results[0].resolvedResourceId);
    }
}