@IsTest
private class RLM_AssetActionSourceTriggerTest {

    private static final String ORDER_STATUS = '{"cfgStatus":"User","attributes":[{"attributeName":"sites","cfgStatus":"User"}]}';
    private static final String PRESET_STATUS = '{"node":"preset"}';

    private class Fixture {
        Account account;
        Order order;
        PricebookEntry pbe;
        AssetAction action;
    }

    private static Fixture buildFixture() {
        Fixture f = new Fixture();
        f.account = new Account(Name = 'RLM Node Status Account');
        insert f.account;
        Product2 product = new Product2(Name = 'RLM Node Status Product', IsActive = true);
        insert product;
        f.pbe = new PricebookEntry(
            Pricebook2Id = Test.getStandardPricebookId(), Product2Id = product.Id, UnitPrice = 100, IsActive = true
        );
        insert f.pbe;
        f.order = new Order(
            AccountId = f.account.Id,
            EffectiveDate = Date.today(),
            Status = 'Draft',
            Pricebook2Id = Test.getStandardPricebookId()
        );
        insert f.order;
        Asset a = new Asset(Name = 'RLM Node Status Asset', AccountId = f.account.Id, Product2Id = product.Id);
        insert a;
        f.action = new AssetAction(
            AssetId = a.Id,
            ActionDate = Datetime.now(),
            Amount = 0,
            MrrChange = 0,
            QuantityChange = 0,
            CategoryEnum = 'Other',
            Type = 'Change'
        );
        insert f.action;
        return f;
    }

    private static OrderItem orderItem(Fixture f, String status) {
        OrderItem item = new OrderItem(
            OrderId = f.order.Id,
            PricebookEntryId = f.pbe.Id,
            Quantity = 1,
            UnitPrice = 100,
            RLM_ConstraintEngineNodeStatus__c = status
        );
        insert item;
        return item;
    }

    private static AssetActionSource source(Fixture f, Id referenceId, String status) {
        return new AssetActionSource(
            AssetActionId = f.action.Id,
            ReferenceEntityItemId = referenceId,
            RLM_ConstraintEngineNodeStatus__c = status
        );
    }

    private static String statusOf(Id sourceId) {
        return [SELECT RLM_ConstraintEngineNodeStatus__c FROM AssetActionSource WHERE Id = :sourceId]
            .RLM_ConstraintEngineNodeStatus__c;
    }

    @IsTest
    static void blankSourceTakesItsOrderProductsStatus() {
        Fixture f = buildFixture();
        OrderItem withStatus = orderItem(f, ORDER_STATUS);
        List<AssetActionSource> sources = new List<AssetActionSource>();
        for (Integer i = 0; i < 200; i++) {
            sources.add(source(f, withStatus.Id, null));
        }

        Test.startTest();
        insert sources;
        Test.stopTest();

        for (AssetActionSource saved : [
            SELECT RLM_ConstraintEngineNodeStatus__c FROM AssetActionSource WHERE Id IN :sources
        ]) {
            Assert.areEqual(ORDER_STATUS, saved.RLM_ConstraintEngineNodeStatus__c,
                'Each blank source carries its order product\'s node status');
        }
    }

    @IsTest
    static void presetStatusIsKept() {
        Fixture f = buildFixture();
        OrderItem withStatus = orderItem(f, ORDER_STATUS);
        AssetActionSource preset = source(f, withStatus.Id, PRESET_STATUS);
        AssetActionSource blank = source(f, withStatus.Id, null);

        Test.startTest();
        insert new List<AssetActionSource>{ preset, blank };
        Test.stopTest();

        Assert.areEqual(PRESET_STATUS, statusOf(preset.Id), 'A status already on the source is kept');
        Assert.areEqual(ORDER_STATUS, statusOf(blank.Id), 'The blank source in the same batch is stamped');
    }

    @IsTest
    static void orderProductWithoutStatusLeavesSourceBlank() {
        Fixture f = buildFixture();
        OrderItem withStatus = orderItem(f, ORDER_STATUS);
        OrderItem withoutStatus = orderItem(f, null);
        AssetActionSource stamped = source(f, withStatus.Id, null);
        AssetActionSource blank = source(f, withoutStatus.Id, null);

        Test.startTest();
        insert new List<AssetActionSource>{ stamped, blank };
        Test.stopTest();

        Assert.areEqual(ORDER_STATUS, statusOf(stamped.Id), 'The sourced row in the same batch is stamped');
        Assert.isNull(statusOf(blank.Id), 'A source whose order product has no status stays blank');
    }

    @IsTest
    static void sourceWithoutReferenceIsLeftAsIs() {
        Fixture f = buildFixture();
        AssetActionSource noReference = source(f, null, null);

        Test.startTest();
        insert noReference;
        Test.stopTest();

        Assert.isNull(statusOf(noReference.Id), 'A source with no reference item stays blank');
    }
}
