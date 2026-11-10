/**
 * Tests for RLM_ARC_AssetValidator: which assets are flagged usage-based or derived-price,
 * how a request is widened through AssetRelationship in both directions, the
 * action-specific blocked messages, and that the query count does not grow with the number of
 * requests (6 when an asset with a product is blocked; 5 when none is blocked and at least one
 * asset has a product; 3 when none has a product and none is blocked (the cases these tests
 * can build); 0 with no ids).
 *
 * Not covered:
 *  - the ramped branch. AssetStatePeriod.RampIdentifier is not createable (the platform
 *    stamps it when a ramp-deal order activates), so a test cannot seed a ramped period.
 *  - the expired branch. Asset.LifecycleEndDate is not writeable, and the platform does not
 *    derive it from an AssetStatePeriod inserted by DML; only lifecycle-managed assets built
 *    by order activation carry it.
 *  - related assets more than one hop away. Relationship expansion reaches direct neighbours
 *    only, so a usage-based grandchild two hops away is not flagged. It is unverified whether
 *    that is intended; no test pins it.
 */
@IsTest
private with sharing class RLM_ARC_AssetValidatorTest {

    private static final String ACCOUNT_NAME = 'RLM ARC Validator Account';
    private static final String CLEAN_PRODUCT = 'RLM ARC Clean Product';
    private static final String USAGE_PRODUCT = 'RLM ARC Usage Product';
    private static final String DRAFT_USAGE_PRODUCT = 'RLM ARC Draft Usage Product';
    private static final String USAGE_RESOURCE_CODE = 'RLM_ARC_TEST_UR';

    private static final String CLEAN_ASSET = 'RLM ARC Clean Asset';
    private static final String NO_PRODUCT_ASSET = 'RLM ARC No Product Asset';
    private static final String USAGE_ASSET = 'RLM ARC Usage Asset';
    private static final String DRAFT_USAGE_ASSET = 'RLM ARC Draft Usage Asset';

    private static final String MESSAGE_PREFIX = 'This action can\'t be completed. The selected assets include ';
    private static final String MESSAGE_SUFFIX = '. Remove the affected assets and try again.';

    @TestSetup
    static void setupData() {
        Account acc = new Account(Name = ACCOUNT_NAME);
        insert acc;

        Product2 clean = new Product2(Name = CLEAN_PRODUCT, IsActive = true);
        Product2 usage = new Product2(Name = USAGE_PRODUCT, IsActive = true, UsageModelType = 'Anchor');
        Product2 draftUsage = new Product2(Name = DRAFT_USAGE_PRODUCT, IsActive = true, UsageModelType = 'Anchor');
        insert new List<Product2>{ clean, usage, draftUsage };

        // A non-derived price book entry, so the IsDerived filter (not the mere presence of
        // a PricebookEntry) is what keeps the clean product unflagged.
        insert new PricebookEntry(
            Pricebook2Id = Test.getStandardPricebookId(),
            Product2Id = clean.Id,
            UnitPrice = 100,
            IsActive = true
        );

        Id usageResourceId = createActiveUsageResource();
        createProductUsageResource(usage.Id, usageResourceId, true);
        // Draft only: the validator counts Active ProductUsageResource rows, so this product
        // must NOT make its assets usage-based.
        createProductUsageResource(draftUsage.Id, usageResourceId, false);

        insert new List<Asset>{
            new Asset(Name = CLEAN_ASSET, AccountId = acc.Id, Product2Id = clean.Id),
            new Asset(Name = NO_PRODUCT_ASSET, AccountId = acc.Id),
            new Asset(Name = USAGE_ASSET, AccountId = acc.Id, Product2Id = usage.Id),
            new Asset(Name = DRAFT_USAGE_ASSET, AccountId = acc.Id, Product2Id = draftUsage.Id)
        };
    }

    // ─── Fixtures ───────────────────────────────────────────────────────

    /** UoM class → UoM → UsageResource, each created in Draft and then activated. */
    private static Id createActiveUsageResource() {
        UnitOfMeasureClass uomClass = new UnitOfMeasureClass(
            Name = 'RLM ARC Test Volume',
            Code = 'RLM_ARC_TEST_UOMC',
            Type = 'Usage',
            Status = 'Draft'
        );
        insert uomClass;
        uomClass.Status = 'Active';
        update uomClass;

        UnitOfMeasure uom = new UnitOfMeasure(
            Name = 'RLM ARC Test Unit',
            UnitCode = 'RLMARCU',
            Type = 'Usage',
            UnitOfMeasureClassId = uomClass.Id,
            Status = 'Draft'
        );
        insert uom;
        uom.Status = 'Active';
        update uom;

        UsageResource ur = new UsageResource(
            Name = 'RLM ARC Test Resource',
            Code = USAGE_RESOURCE_CODE,
            Category = 'Usage',
            Status = 'Draft',
            DefaultUnitOfMeasureId = uom.Id,
            UnitOfMeasureClassId = uomClass.Id
        );
        insert ur;
        ur.Status = 'Active';
        update ur;
        return ur.Id;
    }

    private static void createProductUsageResource(Id productId, Id usageResourceId, Boolean makeActive) {
        ProductUsageResource pur = new ProductUsageResource(
            ProductId = productId,
            UsageResourceId = usageResourceId,
            Status = 'Draft',
            EffectiveStartDate = Datetime.now().addDays(-30),
            IsOptional = false
        );
        insert pur;
        if (makeActive) {
            pur.Status = 'Active';
            update pur;
        }
    }

    private static Asset assetNamed(String name) {
        return [SELECT Id, Name, AccountId, Product2Id FROM Asset WHERE Name = :name LIMIT 1];
    }

    private static Id findUsageResourceId() {
        return [SELECT Id FROM UsageResource WHERE Code = :USAGE_RESOURCE_CODE LIMIT 1].Id;
    }

    /** A product whose standard price book entry is derived, plus an asset on it. */
    private static Asset createDerivedPriceAsset(String productName, String assetName, Boolean alsoUsageBased) {
        Product2 product = new Product2(Name = productName, IsActive = true);
        if (alsoUsageBased) {
            product.UsageModelType = 'Anchor';
        }
        insert product;
        if (alsoUsageBased) {
            createProductUsageResource(product.Id, findUsageResourceId(), true);
        }

        PricebookEntry pbe = new PricebookEntry(
            Pricebook2Id = Test.getStandardPricebookId(),
            Product2Id = product.Id,
            // The platform rejects a derived entry with a non-zero list price.
            UnitPrice = 0,
            IsActive = true,
            IsDerived = true
        );
        insert pbe;
        Assert.isTrue(
            [SELECT IsDerived FROM PricebookEntry WHERE Id = :pbe.Id].IsDerived,
            'PRECONDITION: the platform must keep IsDerived=true on the inserted entry, or the derived-price ' +
            'assertions below prove nothing'
        );

        Asset a = new Asset(
            Name = assetName,
            AccountId = assetNamed(CLEAN_ASSET).AccountId,
            Product2Id = product.Id
        );
        insert a;
        return a;
    }

    private static RLM_ARC_AssetValidator.Result validateOne(List<Id> recordIds) {
        RLM_ARC_AssetValidator.Request req = new RLM_ARC_AssetValidator.Request();
        req.recordIds = recordIds;
        List<RLM_ARC_AssetValidator.Result> results =
            RLM_ARC_AssetValidator.validate(new List<RLM_ARC_AssetValidator.Request>{ req });
        Assert.areEqual(1, results.size(), 'One result per request');
        return results[0];
    }

    private static String expectedMessage(String reasons, String action) {
        return MESSAGE_PREFIX + reasons + ' assets that don\'t support ' + action + MESSAGE_SUFFIX;
    }

    private static void assertUnblocked(RLM_ARC_AssetValidator.Result res) {
        Assert.isFalse(res.hasRampedAssets, 'No ramped assets');
        Assert.isFalse(res.hasUsageBasedAssets, 'No usage-based assets');
        Assert.isFalse(res.hasExpiredAssets, 'No expired assets');
        Assert.isFalse(res.hasDerivedPriceAssets, 'No derived-price assets');
        Assert.isTrue(res.rampedAssetIds.isEmpty(), 'Ramped id list is empty, not null');
        Assert.isTrue(res.usageBasedAssetIds.isEmpty(), 'Usage-based id list is empty, not null');
        Assert.isTrue(res.expiredAssetIds.isEmpty(), 'Expired id list is empty, not null');
        Assert.isTrue(res.derivedPriceAssetIds.isEmpty(), 'Derived-price id list is empty, not null');
        Assert.isTrue(res.blockedAssets.isEmpty(), 'No blocked assets to display');
        Assert.isNull(res.swapBlockedMessage, 'Swap is allowed');
        Assert.isNull(res.transferBlockedMessage, 'Transfer is allowed');
        Assert.isNull(res.rollbackBlockedMessage, 'Rollback is allowed');
    }

    // ─── Unblocked assets ───────────────────────────────────────────────

    @IsTest
    static void cleanAndProductlessAssetsAreNotBlocked() {
        Asset clean = assetNamed(CLEAN_ASSET);
        Asset noProduct = assetNamed(NO_PRODUCT_ASSET);
        Assert.areEqual(
            1,
            [SELECT COUNT() FROM PricebookEntry WHERE Product2Id = :clean.Product2Id AND IsDerived = false],
            'PRECONDITION: the clean product has a non-derived price book entry, so the IsDerived filter is exercised'
        );
        Assert.isNull(noProduct.Product2Id, 'PRECONDITION: the second asset has no product');

        Test.startTest();
        RLM_ARC_AssetValidator.Result res = validateOne(new List<Id>{ clean.Id, noProduct.Id });
        Integer queries = Limits.getQueries();
        Test.stopTest();

        assertUnblocked(res);
        Assert.areEqual(5, queries, 'With nothing blocked, the blocked-asset display query is skipped');
    }

    @IsTest
    static void productlessAssetSkipsTheProductLookups() {
        Asset noProduct = assetNamed(NO_PRODUCT_ASSET);
        Assert.isNull(noProduct.Product2Id, 'PRECONDITION: the asset has no product');

        Test.startTest();
        RLM_ARC_AssetValidator.Result res = validateOne(new List<Id>{ noProduct.Id });
        Integer queries = Limits.getQueries();
        Test.stopTest();

        assertUnblocked(res);
        // relationships, ramp periods, assets; no product means no usage-resource or price book query
        Assert.areEqual(3, queries, 'With no product, the usage-resource and price book queries are skipped');
    }

    @IsTest
    static void draftProductUsageResourceDoesNotMakeAssetUsageBased() {
        Asset draftUsage = assetNamed(DRAFT_USAGE_ASSET);
        Assert.areEqual(
            1,
            [SELECT COUNT() FROM ProductUsageResource WHERE ProductId = :draftUsage.Product2Id AND Status = 'Draft'],
            'PRECONDITION: the product has a Draft usage resource, so the Active filter is what excludes it'
        );

        Test.startTest();
        RLM_ARC_AssetValidator.Result res = validateOne(new List<Id>{ draftUsage.Id });
        Test.stopTest();

        assertUnblocked(res);
    }

    @IsTest
    static void emptyAndNullRequestsReturnUnblockedWithoutQuerying() {
        RLM_ARC_AssetValidator.Request nullIds = new RLM_ARC_AssetValidator.Request();
        nullIds.recordIds = null;
        RLM_ARC_AssetValidator.Request emptyIds = new RLM_ARC_AssetValidator.Request();
        emptyIds.recordIds = new List<Id>();

        Test.startTest();
        List<RLM_ARC_AssetValidator.Result> results = RLM_ARC_AssetValidator.validate(
            new List<RLM_ARC_AssetValidator.Request>{ nullIds, emptyIds }
        );
        Integer queries = Limits.getQueries();
        Test.stopTest();

        Assert.areEqual(2, results.size(), 'One result per request, even with no ids');
        assertUnblocked(results[0]);
        assertUnblocked(results[1]);
        Assert.areEqual(0, queries, 'With no asset ids every lookup is skipped');
    }

    // ─── Usage-based ────────────────────────────────────────────────────

    @IsTest
    static void usageBasedAssetBlocksSwapTransferAndRollback() {
        Asset usage = assetNamed(USAGE_ASSET);

        Test.startTest();
        RLM_ARC_AssetValidator.Result res = validateOne(new List<Id>{ usage.Id });
        Test.stopTest();

        Assert.isTrue(res.hasUsageBasedAssets, 'An active ProductUsageResource makes the asset usage-based');
        Assert.areEqual(new List<Id>{ usage.Id }, res.usageBasedAssetIds, 'The usage-based asset is listed');
        Assert.isFalse(res.hasRampedAssets, 'Not ramped');
        Assert.isFalse(res.hasExpiredAssets, 'Not expired');
        Assert.isFalse(res.hasDerivedPriceAssets, 'Not derived-price');

        Assert.areEqual(
            expectedMessage('usage-based (1)', 'swap, upgrade, or downgrade'),
            res.swapBlockedMessage,
            'Usage-based blocks swap'
        );
        Assert.areEqual(
            expectedMessage('usage-based (1)', 'transfer'),
            res.transferBlockedMessage,
            'Usage-based blocks transfer'
        );
        Assert.areEqual(
            expectedMessage('usage-based (1)', 'rollback'),
            res.rollbackBlockedMessage,
            'Usage-based blocks rollback'
        );

        Assert.areEqual(1, res.blockedAssets.size(), 'The blocked asset is returned for the datatable');
        Asset blocked = res.blockedAssets[0];
        Assert.areEqual(usage.Id, blocked.Id, 'The blocked asset is the usage-based one');
        Assert.areEqual(USAGE_ASSET, blocked.Name, 'Asset name is queried for display');
        Assert.areEqual(USAGE_PRODUCT, blocked.Product2.Name, 'Product name is queried for display');
    }

    // ─── Derived-price ──────────────────────────────────────────────────

    @IsTest
    static void derivedPriceAssetBlocksOnlySwap() {
        Asset derived = createDerivedPriceAsset('RLM ARC Derived Product', 'RLM ARC Derived Asset', false);

        Test.startTest();
        RLM_ARC_AssetValidator.Result res = validateOne(new List<Id>{ derived.Id });
        Test.stopTest();

        Assert.isTrue(res.hasDerivedPriceAssets, 'A derived PricebookEntry makes the asset derived-price');
        Assert.areEqual(new List<Id>{ derived.Id }, res.derivedPriceAssetIds, 'The derived-price asset is listed');
        Assert.isFalse(res.hasUsageBasedAssets, 'Not usage-based');
        Assert.areEqual(
            expectedMessage('derived-price (1)', 'swap, upgrade, or downgrade'),
            res.swapBlockedMessage,
            'Derived price blocks swap/upgrade/downgrade'
        );
        Assert.isNull(res.transferBlockedMessage, 'Derived price does not block transfer');
        Assert.isNull(res.rollbackBlockedMessage, 'Derived price does not block rollback');
        Assert.areEqual(1, res.blockedAssets.size(), 'The derived-price asset is shown as blocked');
    }

    @IsTest
    static void assetThatIsBothUsageBasedAndDerivedListsBothReasons() {
        Asset both = createDerivedPriceAsset('RLM ARC Usage Derived Product', 'RLM ARC Usage Derived Asset', true);

        Test.startTest();
        RLM_ARC_AssetValidator.Result res = validateOne(new List<Id>{ both.Id });
        Test.stopTest();

        Assert.isTrue(res.hasUsageBasedAssets, 'Usage-based');
        Assert.isTrue(res.hasDerivedPriceAssets, 'Derived-price');
        Assert.areEqual(
            expectedMessage('usage-based (1), derived-price (1)', 'swap, upgrade, or downgrade'),
            res.swapBlockedMessage,
            'Swap lists both blocking conditions, comma separated, usage-based before derived-price'
        );
        Assert.areEqual(
            expectedMessage('usage-based (1)', 'transfer'),
            res.transferBlockedMessage,
            'Transfer omits the derived-price reason'
        );
        Assert.areEqual(
            expectedMessage('usage-based (1)', 'rollback'),
            res.rollbackBlockedMessage,
            'Rollback omits the derived-price reason'
        );
        Assert.areEqual(1, res.blockedAssets.size(), 'An asset blocked twice is listed once');
    }

    // ─── Related-asset expansion ────────────────────────────────────────

    @IsTest
    static void relatedAssetIsFollowedFromTheAssetSide() {
        Asset parent = assetNamed(CLEAN_ASSET);
        Asset child = assetNamed(USAGE_ASSET);
        insert new AssetRelationship(AssetId = parent.Id, RelatedAssetId = child.Id);

        Test.startTest();
        RLM_ARC_AssetValidator.Result res = validateOne(new List<Id>{ parent.Id });
        Test.stopTest();

        Assert.isTrue(res.hasUsageBasedAssets, 'A usage-based related asset blocks the selected one');
        Assert.areEqual(new List<Id>{ child.Id }, res.usageBasedAssetIds, 'The related asset is the one flagged');
        Assert.areEqual(1, res.blockedAssets.size(), 'Only the related asset is blocked');
        Assert.areEqual(child.Id, res.blockedAssets[0].Id, 'The blocked asset is the related one');
        Assert.isNotNull(res.rollbackBlockedMessage, 'A rollback-blocked message is set for the related usage asset');
    }

    @IsTest
    static void relatedAssetIsFollowedFromTheRelatedAssetSide() {
        Asset selected = assetNamed(CLEAN_ASSET);
        Asset other = assetNamed(USAGE_ASSET);
        // The selected asset sits on the RelatedAssetId side of the relationship.
        insert new AssetRelationship(AssetId = other.Id, RelatedAssetId = selected.Id);

        Test.startTest();
        RLM_ARC_AssetValidator.Result res = validateOne(new List<Id>{ selected.Id });
        Test.stopTest();

        Assert.isTrue(res.hasUsageBasedAssets, 'The relationship is followed from the RelatedAssetId side');
        Assert.areEqual(new List<Id>{ other.Id }, res.usageBasedAssetIds, 'The other side of the relationship is flagged');
    }

    @IsTest
    static void unrelatedRequestIsNotWidenedByAnotherRequestsRelationship() {
        Asset parent = assetNamed(CLEAN_ASSET);
        Asset child = assetNamed(USAGE_ASSET);
        Asset unrelated = assetNamed(NO_PRODUCT_ASSET);
        insert new AssetRelationship(AssetId = parent.Id, RelatedAssetId = child.Id);

        RLM_ARC_AssetValidator.Request withRelation = new RLM_ARC_AssetValidator.Request();
        withRelation.recordIds = new List<Id>{ parent.Id };
        RLM_ARC_AssetValidator.Request withoutRelation = new RLM_ARC_AssetValidator.Request();
        withoutRelation.recordIds = new List<Id>{ unrelated.Id };

        Test.startTest();
        List<RLM_ARC_AssetValidator.Result> results = RLM_ARC_AssetValidator.validate(
            new List<RLM_ARC_AssetValidator.Request>{ withRelation, withoutRelation }
        );
        Test.stopTest();

        Assert.isTrue(results[0].hasUsageBasedAssets, 'The first request picks up its related asset');
        assertUnblocked(results[1]);
    }

    // ─── Bulk ───────────────────────────────────────────────────────────

    @IsTest
    static void bulkRequestsMapInOrderWithAFixedQueryCount() {
        Asset clean = assetNamed(CLEAN_ASSET);
        Asset usage = assetNamed(USAGE_ASSET);
        Asset noProduct = assetNamed(NO_PRODUCT_ASSET);
        Asset secondUsage = new Asset(
            Name = 'RLM ARC Second Usage Asset',
            AccountId = usage.AccountId,
            Product2Id = usage.Product2Id
        );
        insert secondUsage;

        // Every request has a different expected result, so a result returned for the wrong
        // request fails one of the assertions below.
        List<RLM_ARC_AssetValidator.Request> requests = new List<RLM_ARC_AssetValidator.Request>();
        for (List<Id> ids : new List<List<Id>>{
            new List<Id>{ clean.Id },
            new List<Id>{ usage.Id },
            new List<Id>{ usage.Id, secondUsage.Id },
            new List<Id>{ noProduct.Id, secondUsage.Id }
        }) {
            RLM_ARC_AssetValidator.Request req = new RLM_ARC_AssetValidator.Request();
            req.recordIds = ids;
            requests.add(req);
        }

        Test.startTest();
        RLM_ARC_AssetValidator.validate(new List<RLM_ARC_AssetValidator.Request>{ requests[1] });
        Integer singleRequestQueries = Limits.getQueries();
        List<RLM_ARC_AssetValidator.Result> results = RLM_ARC_AssetValidator.validate(requests);
        Integer bulkQueries = Limits.getQueries() - singleRequestQueries;
        Test.stopTest();

        Assert.areEqual(4, results.size(), 'One result per request');
        assertUnblocked(results[0]);
        Assert.areEqual(new List<Id>{ usage.Id }, results[1].usageBasedAssetIds, 'Second request: the first usage asset only');
        Assert.areEqual(
            new Set<Id>{ usage.Id, secondUsage.Id },
            new Set<Id>(results[2].usageBasedAssetIds),
            'Third request: both usage assets'
        );
        Assert.areEqual(2, results[2].blockedAssets.size(), 'Third request: both usage assets are blocked');
        Assert.areEqual(
            expectedMessage('usage-based (2)', 'rollback'),
            results[2].rollbackBlockedMessage,
            'Third request: the message counts both assets'
        );
        Assert.areEqual(
            new List<Id>{ secondUsage.Id },
            results[3].usageBasedAssetIds,
            'Fourth request: the second usage asset only'
        );
        Assert.areEqual(1, results[3].blockedAssets.size(), 'Fourth request: the product-less asset is not blocked');

        // relationships, ramp periods, assets, usage resources, price book entries, blocked assets
        Assert.areEqual(6, singleRequestQueries, 'One request uses 6 queries');
        Assert.areEqual(6, bulkQueries, 'Four requests use the same 6 queries as one; the count does not grow with requests');
    }
}
