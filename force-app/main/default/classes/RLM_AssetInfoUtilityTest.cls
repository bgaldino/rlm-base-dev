/**
 * Not covered: term-defined and evergreen renewal terms. OrderItem.ProductSellingModelId is not
 * createable, and on a live 264 org an order item inserted by an Apex test stayed without a selling
 * model even when its price book entry had one (a quote line on the same entry did get it). So the
 * fixture uses a plain price book entry, and new assets take the default renewal path.
 *
 * Activating the contract fires the RLM_Contract_Activation_Refresh_Pricing_Tables flow. Its three
 * refreshDecisionTable calls were verified on a live 264 org to run cleanly in test context (each
 * returns Queued; the fault path is never taken).
 *
 * Production gaps are pinned below with "Known gap:" assertions.
 */
@IsTest
private class RLM_AssetInfoUtilityTest {

    // Starting values, chosen to differ from what the path under test can write. The renewal term
    // differs from every branch. RenewalTermUnit and PricingSource have only two values each, so
    // they are seeded per path: a new asset always gets LastTransaction; a changed asset can only
    // get Months / PriceBookListPrice (the contract branch).
    private static final Integer SEEDED_TERM = 7;
    private static final String NEW_ASSET_UNIT = 'Months';
    private static final String NEW_ASSET_SOURCE = 'PriceBookListPrice';
    private static final String CHANGED_ASSET_UNIT = 'Annual';
    private static final String CHANGED_ASSET_SOURCE = 'LastTransaction';

    /** One order line and the asset the platform reported for it. */
    private class Line {
        Id orderItemId;
        Id assetId;
    }

    /** One draft order with a single order action of the given type. */
    private class OrderContext {
        Id accountId;
        Order order;
        Id orderActionId;
        String actionType;
        PricebookEntry pbe;
    }

    private static OrderContext newOrder(String actionType) {
        OrderContext ctx = new OrderContext();
        ctx.actionType = actionType;
        Account acct = new Account(Name = 'RLM Asset Info Account');
        insert acct;
        ctx.accountId = acct.Id;
        Product2 product = new Product2(Name = 'RLM Asset Info Product', IsActive = true);
        insert product;
        ctx.pbe = new PricebookEntry(
            Pricebook2Id = Test.getStandardPricebookId(), Product2Id = product.Id, UnitPrice = 100, IsActive = true
        );
        insert ctx.pbe;
        ctx.order = new Order(
            AccountId = acct.Id,
            Status = 'Draft',
            EffectiveDate = Date.newInstance(2026, 1, 1),
            Pricebook2Id = Test.getStandardPricebookId()
        );
        insert ctx.order;
        OrderAction action = new OrderAction(OrderId = ctx.order.Id, Type = actionType);
        insert action;
        ctx.orderActionId = action.Id;
        return ctx;
    }

    private static Boolean isNew(OrderContext ctx) {
        return ctx.actionType == 'Add';
    }

    private static List<Line> createLines(OrderContext ctx, Integer count) {
        List<OrderItem> items = new List<OrderItem>();
        List<Asset> assets = new List<Asset>();
        for (Integer i = 0; i < count; i++) {
            OrderItem item = new OrderItem(
                OrderId = ctx.order.Id,
                OrderActionId = ctx.orderActionId,
                PricebookEntryId = ctx.pbe.Id,
                Product2Id = ctx.pbe.Product2Id,
                Quantity = 1,
                UnitPrice = 100,
                ServiceDate = Date.newInstance(2026, 1, 1),
                EndDate = Date.newInstance(2026, 12, 31)
            );
            if (!isNew(ctx)) {
                // A change to an existing asset must state the quantity it starts from.
                item.StartQuantity = 1;
            }
            items.add(item);
            assets.add(new Asset(
                Name = 'RLM Asset Info ' + i,
                AccountId = ctx.accountId,
                Product2Id = ctx.pbe.Product2Id,
                // Only a lifecycle-managed asset can be related to a contract.
                HasLifecycleManagement = true,
                RenewalTerm = SEEDED_TERM,
                RenewalTermUnit = isNew(ctx) ? NEW_ASSET_UNIT : CHANGED_ASSET_UNIT,
                PricingSource = isNew(ctx) ? NEW_ASSET_SOURCE : CHANGED_ASSET_SOURCE
            ));
        }
        insert items;
        insert assets;
        List<Line> lines = new List<Line>();
        for (Integer i = 0; i < count; i++) {
            Line l = new Line();
            l.orderItemId = items[i].Id;
            l.assetId = assets[i].Id;
            lines.add(l);
        }
        for (Asset a : [SELECT RenewalTerm, RenewalTermUnit, PricingSource FROM Asset WHERE Id IN :assets]) {
            assertSeeded(ctx, a, 'PRECONDITION: seeded values are stored');
        }
        return lines;
    }

    /**
     * CreateAssetOrderEvent is published only by the platform and its fields are not writeable,
     * so a test builds one by deserializing it, with AssetDetails as a plain array.
     */
    private static CreateAssetOrderEvent buildEvent(List<Line> lines) {
        List<Object> details = new List<Object>();
        for (Line l : lines) {
            details.add(new Map<String, Object>{
                'attributes' => new Map<String, Object>{ 'type' => 'CreateAssetOrderDtlEvent' },
                'OrderItemId' => l.orderItemId,
                'AssetId' => l.assetId,
                'IsSuccess' => true
            });
        }
        String payload = JSON.serialize(new Map<String, Object>{
            'attributes' => new Map<String, Object>{ 'type' => 'CreateAssetOrderEvent' },
            'AssetDetails' => details
        });
        CreateAssetOrderEvent evt = (CreateAssetOrderEvent) JSON.deserialize(payload, CreateAssetOrderEvent.class);
        Assert.areEqual(lines.size(), evt.AssetDetails.size(), 'Every line is in the event');
        return evt;
    }

    private static void run(List<Line> lines) {
        RLM_AssetInfoUtility.calculateAssetRenewInfo(new List<CreateAssetOrderEvent>{ buildEvent(lines) });
    }

    private static Asset reload(Id assetId) {
        return [SELECT RenewalTerm, RenewalTermUnit, PricingSource FROM Asset WHERE Id = :assetId];
    }

    /** Asserts the asset still holds the values createLines seeded for this path. */
    private static void assertUnchanged(OrderContext ctx, Id assetId, String message) {
        assertSeeded(ctx, reload(assetId), message);
    }

    private static void assertSeeded(OrderContext ctx, Asset a, String message) {
        Assert.areEqual(SEEDED_TERM, a.RenewalTerm.intValue(), message + ' (renewal term)');
        Assert.areEqual(
            isNew(ctx) ? NEW_ASSET_UNIT : CHANGED_ASSET_UNIT, a.RenewalTermUnit, message + ' (renewal unit)'
        );
        Assert.areEqual(
            isNew(ctx) ? NEW_ASSET_SOURCE : CHANGED_ASSET_SOURCE, a.PricingSource, message + ' (pricing source)'
        );
    }

    private static void assertDefaultRenewal(Id assetId) {
        Asset a = reload(assetId);
        Assert.areEqual(1, a.RenewalTerm.intValue(), 'Default renewal term is 1');
        Assert.areEqual('Annual', a.RenewalTermUnit, 'Default renewal unit is Annual');
        Assert.areEqual('LastTransaction', a.PricingSource, 'New assets renew at the last transaction price');
    }

    @IsTest
    static void emptyEventListDoesNothing() {
        Integer dmlBefore = Limits.getDmlStatements();

        RLM_AssetInfoUtility.calculateAssetRenewInfo(new List<CreateAssetOrderEvent>());

        Assert.areEqual(dmlBefore, Limits.getDmlStatements(), 'No assets are written for an empty event list');
    }

    @IsTest
    static void newAssetWithoutSellingModelRenewsForOneYear() {
        List<Line> lines = createLines(newOrder('Add'), 2);

        Test.startTest();
        run(lines);
        Test.stopTest();

        for (Line l : lines) {
            assertDefaultRenewal(l.assetId);
        }
    }

    @IsTest
    static void changedAssetWithoutContractIsLeftAsIs() {
        OrderContext ctx = newOrder('Amend');
        Line l = createLines(ctx, 1)[0];
        Line added = createLines(newOrder('Add'), 1)[0];

        Test.startTest();
        run(new List<Line>{ l, added });
        Test.stopTest();

        assertDefaultRenewal(added.assetId);
        assertUnchanged(ctx, l.assetId, 'Without a contract a changed asset keeps its values');
    }

    @IsTest
    static void changedAssetWithContractIsNotStamped() {
        OrderContext ctx = newOrder('Amend');
        Line l = createLines(ctx, 1)[0];
        Contract c = new Contract(
            AccountId = ctx.accountId, StartDate = Date.today().addMonths(-1), ContractTerm = 24, Status = 'Draft'
        );
        insert c;
        // An asset can only be related to an active, Revenue Lifecycle Management contract.
        insert new AppUsageAssignment(RecordId = c.Id, AppUsageType = 'RevenueLifecycleManagement');
        c.Status = 'Activated';
        update c;
        insert new AssetContractRelationship(AssetId = l.assetId, ContractId = c.Id, StartDate = Datetime.now());
        Assert.areEqual(
            1, [SELECT COUNT() FROM AssetContractRelationship WHERE AssetId = :l.assetId],
            'PRECONDITION: the asset is related to the contract'
        );
        Line added = createLines(newOrder('Add'), 1)[0];

        Test.startTest();
        run(new List<Line>{ l, added });
        Test.stopTest();

        assertDefaultRenewal(added.assetId);
        assertUnchanged(
            ctx, l.assetId,
            'Known gap: acrMap is keyed by relationship Id but looked up by AssetId, so the contract term is '
                + 'never applied; update this test when it is fixed'
        );
    }

    @IsTest
    static void onlyTheFirstEventIsProcessed() {
        List<Line> lines = createLines(newOrder('Add'), 2);
        List<CreateAssetOrderEvent> events = new List<CreateAssetOrderEvent>{
            buildEvent(new List<Line>{ lines[0] }),
            buildEvent(new List<Line>{ lines[1] })
        };

        Test.startTest();
        RLM_AssetInfoUtility.calculateAssetRenewInfo(events);
        Test.stopTest();

        assertDefaultRenewal(lines[0].assetId);
        Asset second = reload(lines[1].assetId);
        Assert.areEqual(
            SEEDED_TERM, second.RenewalTerm.intValue(),
            'Known gap: only the first event in the batch is processed; update this test when it is fixed'
        );
    }

    @IsTest
    static void bulkEventUpdatesEveryAsset() {
        List<Line> lines = createLines(newOrder('Add'), 200);

        Test.startTest();
        run(lines);
        Test.stopTest();

        Set<Id> assetIds = new Set<Id>();
        for (Line l : lines) {
            assetIds.add(l.assetId);
        }
        List<Asset> assets = [SELECT RenewalTerm, RenewalTermUnit, PricingSource FROM Asset WHERE Id IN :assetIds];
        Assert.areEqual(200, assets.size(), 'All assets are present');
        for (Asset a : assets) {
            Assert.areEqual(1, a.RenewalTerm.intValue(), 'Every asset in the event is stamped');
            Assert.areEqual('Annual', a.RenewalTermUnit, 'Every asset in the event is stamped');
            Assert.areEqual('LastTransaction', a.PricingSource, 'Every asset in the event is stamped');
        }
    }
}
