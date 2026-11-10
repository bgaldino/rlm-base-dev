@IsTest
private class RLM_QuoteItemTriggerTest {

    private static final String PRESET_STATUS = '{"node":"preset"}';

    private class Fixture {
        Account account;
        Quote quote;
        PricebookEntry pbe;
    }

    private static Fixture buildFixture() {
        Fixture f = new Fixture();
        f.account = new Account(Name = 'RLM Constraint Status Account');
        insert f.account;
        Opportunity opp = new Opportunity(
            Name = 'RLM Constraint Status Opportunity',
            AccountId = f.account.Id,
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
        return f;
    }

    private static Asset newAsset(Fixture f, String name) {
        Asset a = new Asset(Name = name, AccountId = f.account.Id, Product2Id = f.pbe.Product2Id);
        insert a;
        return a;
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

    private static List<AssetActionSource> actionSources(Id assetActionId, List<String> statuses) {
        List<AssetActionSource> sources = new List<AssetActionSource>();
        for (String status : statuses) {
            sources.add(new AssetActionSource(
                AssetActionId = assetActionId, RLM_ConstraintEngineNodeStatus__c = status
            ));
        }
        insert sources;
        return sources;
    }

    /**
     * Gives the asset a recent action (one source with latestStatus, one with none) and an action
     * a month older (olderStatus). latestFirst sets which is inserted first. The source with no
     * status is the newest, so it sorts first and the trigger has to skip it.
     */
    private static void seedAssetHistory(Id assetId, Boolean latestFirst, String latestStatus, String olderStatus) {
        for (Boolean insertLatest : latestFirst ? new List<Boolean>{ true, false } : new List<Boolean>{ false, true }) {
            if (insertLatest) {
                AssetAction latest = assetAction(assetId, Datetime.now().addDays(-1));
                List<AssetActionSource> sources = actionSources(latest.Id, new List<String>{ latestStatus, null });
                Test.setCreatedDate(sources[0].Id, Datetime.now().addDays(-2));
                Test.setCreatedDate(sources[1].Id, Datetime.now().addHours(-1));
            } else {
                AssetAction older = assetAction(assetId, Datetime.now().addDays(-30));
                actionSources(older.Id, new List<String>{ olderStatus });
            }
        }
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
    static void eachLineInheritsItsAssetsLatestStatusWhateverTheInsertOrder() {
        Fixture f = buildFixture();
        // Asset A's latest action is inserted first, asset B's last: only ActionDate picks both right.
        Asset assetA = newAsset(f, 'RLM Constraint Status Asset A');
        Asset assetB = newAsset(f, 'RLM Constraint Status Asset B');
        seedAssetHistory(assetA.Id, true, '{"node":"a-latest"}', '{"node":"a-older"}');
        seedAssetHistory(assetB.Id, false, '{"node":"b-latest"}', '{"node":"b-older"}');
        QuoteAction amendA = quoteAction(f, assetA.Id, 'Amend');
        QuoteAction amendB = quoteAction(f, assetB.Id, 'Amend');
        Map<Id, String> expectedByAction = new Map<Id, String>{
            amendA.Id => '{"node":"a-latest"}',
            amendB.Id => '{"node":"b-latest"}'
        };
        List<QuoteLineItem> lines = new List<QuoteLineItem>();
        for (Integer i = 0; i < 100; i++) {
            lines.add(amendLine(f, amendA.Id, null));
            lines.add(amendLine(f, amendB.Id, null));
        }

        Test.startTest();
        insert lines;
        Test.stopTest();

        List<QuoteLineItem> saved = [
            SELECT QuoteActionId, RLM_ConstraintEngineNodeStatus__c FROM QuoteLineItem WHERE Id IN :lines
        ];
        Assert.areEqual(200, saved.size(), 'All 200 lines were saved');
        for (QuoteLineItem line : saved) {
            Assert.areEqual(
                expectedByAction.get(line.QuoteActionId), line.RLM_ConstraintEngineNodeStatus__c,
                'Each line carries the latest status of its own asset'
            );
        }
    }

    @IsTest
    static void presetStatusIsNotOverwritten() {
        Fixture f = buildFixture();
        Asset a = newAsset(f, 'RLM Constraint Status Asset');
        seedAssetHistory(a.Id, true, '{"node":"latest"}', '{"node":"older"}');
        QuoteAction amend = quoteAction(f, a.Id, 'Amend');
        QuoteLineItem line = amendLine(f, amend.Id, PRESET_STATUS);

        Test.startTest();
        insert line;
        Test.stopTest();

        Assert.areEqual(PRESET_STATUS, statusOf(line.Id), 'A status already on the line is kept');
    }

    @IsTest
    static void lineWithoutQuoteActionStaysBlank() {
        Fixture f = buildFixture();
        QuoteLineItem line = newLine(f, null, null);

        Test.startTest();
        insert line;
        Test.stopTest();

        Assert.isNull(statusOf(line.Id), 'A new-sale line is saved without error and stays blank');
    }

    @IsTest
    static void quoteActionWithoutSourceAssetStaysBlank() {
        Fixture f = buildFixture();
        QuoteAction add = quoteAction(f, null, 'Add');
        QuoteLineItem line = newLine(f, add.Id, null);

        Test.startTest();
        insert line;
        Test.stopTest();

        Assert.isNull(statusOf(line.Id), 'A line whose quote action has no source asset is saved and stays blank');
    }

    @IsTest
    static void onlyTheLatestActionIsRead() {
        Fixture f = buildFixture();
        Asset a = newAsset(f, 'RLM Constraint Status Asset');
        // The older action has a status; the latest has none. Only the latest action counts.
        AssetAction older = assetAction(a.Id, Datetime.now().addDays(-30));
        actionSources(older.Id, new List<String>{ '{"node":"older"}' });
        AssetAction latest = assetAction(a.Id, Datetime.now().addDays(-1));
        actionSources(latest.Id, new List<String>{ null });
        QuoteAction amend = quoteAction(f, a.Id, 'Amend');
        QuoteLineItem line = amendLine(f, amend.Id, null);

        Test.startTest();
        insert line;
        Test.stopTest();

        Assert.isNull(statusOf(line.Id), 'An older action\'s status is not used when the latest action has none');
    }
}
