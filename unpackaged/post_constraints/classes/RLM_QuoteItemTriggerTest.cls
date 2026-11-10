@IsTest
private class RLM_QuoteItemTriggerTest {

    private static final String LATEST_STATUS = '{"node":"latest"}';
    private static final String OLDER_STATUS = '{"node":"older"}';
    private static final String PRESET_STATUS = '{"node":"preset"}';

    private class Fixture {
        Quote quote;
        PricebookEntry pbe;
        Asset asset;
    }

    private static Fixture buildFixture() {
        Fixture f = new Fixture();
        Account acct = new Account(Name = 'RLM Constraint Status Account');
        insert acct;
        Opportunity opp = new Opportunity(
            Name = 'RLM Constraint Status Opportunity',
            AccountId = acct.Id,
            StageName = 'Prospecting',
            CloseDate = Date.today().addDays(30)
        );
        insert opp;
        Product2 product = new Product2(Name = 'RLM Constraint Status Product', IsActive = true);
        insert product;
        f.pbe = new PricebookEntry(
            Pricebook2Id = Test.getStandardPricebookId(), Product2Id = product.Id, UnitPrice = 100, IsActive = true
        );
        insert f.pbe;
        f.quote = new Quote(
            Name = 'RLM Constraint Status Quote',
            OpportunityId = opp.Id,
            Pricebook2Id = Test.getStandardPricebookId(),
            Status = 'Draft'
        );
        insert f.quote;
        f.asset = new Asset(Name = 'RLM Constraint Status Asset', AccountId = acct.Id, Product2Id = product.Id);
        insert f.asset;
        return f;
    }

    private static QuoteAction quoteAction(Fixture f, Id sourceAssetId, String actionType) {
        QuoteAction qa = new QuoteAction(QuoteId = f.quote.Id, SourceAssetId = sourceAssetId, Type = actionType);
        insert qa;
        return qa;
    }

    private static AssetAction assetAction(Id assetId, Datetime actionDate) {
        AssetAction aa = new AssetAction(
            AssetId = assetId,
            ActionDate = actionDate,
            Amount = 0,
            MrrChange = 0,
            QuantityChange = 0,
            CategoryEnum = 'Other',
            Type = 'Change'
        );
        insert aa;
        return aa;
    }

    private static void actionSources(Id assetActionId, List<String> statuses) {
        List<AssetActionSource> sources = new List<AssetActionSource>();
        for (String status : statuses) {
            sources.add(new AssetActionSource(AssetActionId = assetActionId, RLM_ConstraintEngineNodeStatus__c = status));
        }
        insert sources;
    }

    /**
     * The asset's history: a recent action whose source carries the latest status, and an older
     * action. The recent one is inserted first, so only ActionDate (not insert order) picks it.
     */
    private static void seedAssetHistory(Id assetId) {
        AssetAction latest = assetAction(assetId, Datetime.now().addDays(-1));
        actionSources(latest.Id, new List<String>{ LATEST_STATUS, null });
        AssetAction older = assetAction(assetId, Datetime.now().addDays(-30));
        actionSources(older.Id, new List<String>{ OLDER_STATUS });
    }

    private static QuoteLineItem newLine(Fixture f, Id quoteActionId, String status) {
        return new QuoteLineItem(
            QuoteId = f.quote.Id,
            PricebookEntryId = f.pbe.Id,
            Quantity = 1,
            UnitPrice = 100,
            QuoteActionId = quoteActionId,
            RLM_ConstraintEngineNodeStatus__c = status
        );
    }

    /** An amendment line must state the quantity it starts from. */
    private static QuoteLineItem amendLine(Fixture f, Id quoteActionId, String status) {
        QuoteLineItem line = newLine(f, quoteActionId, status);
        line.StartQuantity = 1;
        return line;
    }

    private static String statusOf(Id lineId) {
        return [SELECT RLM_ConstraintEngineNodeStatus__c FROM QuoteLineItem WHERE Id = :lineId]
            .RLM_ConstraintEngineNodeStatus__c;
    }

    @IsTest
    static void amendmentLineInheritsTheLatestAssetActionStatus() {
        Fixture f = buildFixture();
        seedAssetHistory(f.asset.Id);
        QuoteAction amend = quoteAction(f, f.asset.Id, 'Amend');
        QuoteLineItem line = amendLine(f, amend.Id, null);

        Test.startTest();
        insert line;
        Test.stopTest();

        Assert.areEqual(LATEST_STATUS, statusOf(line.Id), 'The status of the asset\'s latest action is carried onto the line');
    }

    @IsTest
    static void presetStatusIsNotOverwritten() {
        Fixture f = buildFixture();
        seedAssetHistory(f.asset.Id);
        QuoteAction amend = quoteAction(f, f.asset.Id, 'Amend');
        QuoteLineItem line = amendLine(f, amend.Id, PRESET_STATUS);

        Test.startTest();
        insert line;
        Test.stopTest();

        Assert.areEqual(PRESET_STATUS, statusOf(line.Id), 'A status already on the line is kept');
    }

    @IsTest
    static void lineWithoutQuoteActionIsUntouched() {
        Fixture f = buildFixture();
        seedAssetHistory(f.asset.Id);
        QuoteLineItem line = newLine(f, null, null);

        Test.startTest();
        insert line;
        Test.stopTest();

        Assert.isNull(statusOf(line.Id), 'A new-sale line has no asset to inherit from');
    }

    @IsTest
    static void quoteActionWithoutSourceAssetIsIgnored() {
        Fixture f = buildFixture();
        seedAssetHistory(f.asset.Id);
        QuoteAction add = quoteAction(f, null, 'Add');
        QuoteLineItem line = newLine(f, add.Id, null);

        Test.startTest();
        insert line;
        Test.stopTest();

        Assert.isNull(statusOf(line.Id), 'A quote action with no source asset carries no status');
    }

    @IsTest
    static void assetWithoutRecordedStatusLeavesLineBlank() {
        Fixture f = buildFixture();
        AssetAction action = assetAction(f.asset.Id, Datetime.now().addDays(-1));
        actionSources(action.Id, new List<String>{ null });
        QuoteAction amend = quoteAction(f, f.asset.Id, 'Amend');
        QuoteLineItem line = amendLine(f, amend.Id, null);

        Test.startTest();
        insert line;
        Test.stopTest();

        Assert.isNull(statusOf(line.Id), 'No recorded status means nothing to inherit');
    }

    @IsTest
    static void bulkInsertStampsEveryLine() {
        Fixture f = buildFixture();
        seedAssetHistory(f.asset.Id);
        QuoteAction amend = quoteAction(f, f.asset.Id, 'Amend');
        List<QuoteLineItem> lines = new List<QuoteLineItem>();
        for (Integer i = 0; i < 200; i++) {
            lines.add(amendLine(f, amend.Id, null));
        }

        Test.startTest();
        insert lines;
        Test.stopTest();

        Map<Id, QuoteLineItem> byId = new Map<Id, QuoteLineItem>(lines);
        List<QuoteLineItem> saved = [
            SELECT RLM_ConstraintEngineNodeStatus__c FROM QuoteLineItem WHERE Id IN :byId.keySet()
        ];
        Assert.areEqual(200, saved.size(), 'All 200 lines were saved');
        for (QuoteLineItem line : saved) {
            Assert.areEqual(LATEST_STATUS, line.RLM_ConstraintEngineNodeStatus__c, 'Every line in the batch is stamped');
        }
    }
}
