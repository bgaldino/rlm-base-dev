/**
 * Not covered here:
 * - Term-defined and evergreen renewal terms. Order items inserted by an Apex test carry no
 *   product selling model (the platform does not derive it from the price book entry in a test
 *   context), so new assets always take the default renewal path.
 * - Contract-based renewal for changed assets. The utility keys its asset-contract map by the
 *   relationship id but looks it up by asset id, so that branch never runs.
 */
@IsTest
private class RLM_AssetInfoUtilityTest {

    // Starting values on every asset, chosen to differ from what the utility writes.
    private static final Integer SEEDED_TERM = 6;
    private static final String SEEDED_UNIT = 'Months';

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
        OrderAction action = new OrderAction();
        action.put('OrderId', ctx.order.Id);
        action.put('Type', actionType);
        insert action;
        ctx.orderActionId = action.Id;
        return ctx;
    }

    private static List<Line> createLines(OrderContext ctx, Integer count, String seededPricingSource) {
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
            if (ctx.actionType != 'Add') {
                // A change to an existing asset must state the quantity it starts from.
                item.StartQuantity = 1;
            }
            items.add(item);
            assets.add(new Asset(
                Name = 'RLM Asset Info ' + i,
                AccountId = ctx.accountId,
                Product2Id = ctx.pbe.Product2Id,
                RenewalTerm = SEEDED_TERM,
                RenewalTermUnit = SEEDED_UNIT,
                PricingSource = seededPricingSource
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

    private static void assertSeeded(Id assetId, String pricingSource) {
        Asset a = reload(assetId);
        Assert.areEqual(SEEDED_TERM, a.RenewalTerm.intValue(), 'PRECONDITION: seeded renewal term is stored');
        Assert.areEqual(SEEDED_UNIT, a.RenewalTermUnit, 'PRECONDITION: seeded renewal unit is stored');
        Assert.areEqual(pricingSource, a.PricingSource, 'PRECONDITION: seeded pricing source is stored');
    }

    @IsTest
    static void emptyEventListDoesNothing() {
        Integer dmlBefore = Limits.getDmlStatements();

        RLM_AssetInfoUtility.calculateAssetRenewInfo(new List<CreateAssetOrderEvent>());

        Assert.areEqual(dmlBefore, Limits.getDmlStatements(), 'No assets are written for an empty event list');
    }

    @IsTest
    static void newAssetWithoutRecurringModelRenewsForOneYear() {
        OrderContext ctx = newOrder('Add');
        List<Line> lines = createLines(ctx, 2, 'PriceBookListPrice');
        for (OrderItem oi : [SELECT ProductSellingModelId FROM OrderItem WHERE OrderId = :ctx.order.Id]) {
            Assert.isNull(oi.ProductSellingModelId, 'PRECONDITION: test order items carry no selling model');
        }
        for (Line l : lines) {
            assertSeeded(l.assetId, 'PriceBookListPrice');
        }

        Test.startTest();
        run(lines);
        Test.stopTest();

        for (Line l : lines) {
            Asset a = reload(l.assetId);
            Assert.areEqual(1, a.RenewalTerm.intValue(), 'Default renewal term is 1');
            Assert.areEqual('Annual', a.RenewalTermUnit, 'Default renewal unit is Annual');
            Assert.areEqual('LastTransaction', a.PricingSource, 'New assets renew at the last transaction price');
        }
    }

    @IsTest
    static void changedAssetWithoutContractIsLeftAsIs() {
        OrderContext ctx = newOrder('Amend');
        Line l = createLines(ctx, 1, 'PriceBookListPrice')[0];
        assertSeeded(l.assetId, 'PriceBookListPrice');

        Test.startTest();
        run(new List<Line>{ l });
        Test.stopTest();

        // A new asset on the same path would become 1 / Annual / LastTransaction.
        assertSeeded(l.assetId, 'PriceBookListPrice');
    }

    @IsTest
    static void bulkEventUpdatesEveryAsset() {
        OrderContext ctx = newOrder('Add');
        List<Line> lines = createLines(ctx, 200, 'PriceBookListPrice');
        Set<Id> assetIds = new Set<Id>();
        for (Line l : lines) {
            assetIds.add(l.assetId);
        }

        Test.startTest();
        run(lines);
        Test.stopTest();

        List<Asset> assets = [SELECT RenewalTerm, RenewalTermUnit, PricingSource FROM Asset WHERE Id IN :assetIds];
        Assert.areEqual(200, assets.size(), 'All assets are present');
        for (Asset a : assets) {
            Assert.areEqual(1, a.RenewalTerm.intValue(), 'Every asset in the event is stamped');
            Assert.areEqual('Annual', a.RenewalTermUnit, 'Every asset in the event is stamped');
            Assert.areEqual('LastTransaction', a.PricingSource, 'Every asset in the event is stamped');
        }
    }
}
