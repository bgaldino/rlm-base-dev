@isTest
private class RLM_AI_QuoteDemoSummaryServiceTest {

    @isTest
    static void summaryReturnsRecapWithLineNames() {
        RLM_AI_ProductConfigTestDataFactory.QuoteFixture fixture =
            RLM_AI_ProductConfigTestDataFactory.createQuoteFixture('FESBA Generator Set');
        addQuoteLineItem(fixture.quoteId, 'Support Plan');

        RLM_AI_QuoteDemoSummaryService.SummaryInput input =
            new RLM_AI_QuoteDemoSummaryService.SummaryInput();
        input.quoteId = String.valueOf(fixture.quoteId);

        Test.startTest();
        List<RLM_AI_QuoteDemoSummaryService.SummaryOutput> results =
            RLM_AI_QuoteDemoSummaryService.getSummary(
                new List<RLM_AI_QuoteDemoSummaryService.SummaryInput>{ input }
            );
        Test.stopTest();

        System.assertEquals(1, results.size(), 'One result should be returned.');
        RLM_AI_QuoteDemoSummaryService.SummaryOutput out = results[0];
        System.assertEquals(true, out.isSuccess, 'Recap should build successfully.');
        System.assertEquals(null, out.errorMessage);
        System.assert(out.summaryDisplay.contains('FESBA Generator Set'),
            'Per-line product name should appear.');
        System.assert(out.summaryDisplay.contains('Support Plan'),
            'All lines should appear by name.');
        System.assert(out.summaryDisplay.contains('Line items: 2'),
            'Line count should be reported.');
        System.assert(out.summaryDisplay.contains('RLM AI Test Quote'),
            'Quote name should appear in the header.');
        // Names-only: no raw QuoteLineItem Ids in the recap.
        System.assert(!out.summaryDisplay.contains(String.valueOf(fixture.quoteLineItemId)),
            'Recap must not leak raw QuoteLineItem Ids.');
    }

    @isTest
    static void summaryHandlesQuoteWithNoLines() {
        Account acct = new Account(Name = 'Empty Recap Account');
        insert acct;
        Opportunity opp = new Opportunity(
            Name = 'Empty Recap Opportunity',
            AccountId = acct.Id,
            StageName = 'Prospecting',
            CloseDate = Date.today().addDays(30)
        );
        insert opp;
        Quote q = new Quote(
            Name = 'Empty Recap Quote',
            Pricebook2Id = Test.getStandardPricebookId(),
            OpportunityId = opp.Id,
            Status = 'Draft'
        );
        insert q;

        RLM_AI_QuoteDemoSummaryService.SummaryInput input =
            new RLM_AI_QuoteDemoSummaryService.SummaryInput();
        input.quoteId = String.valueOf(q.Id);

        List<RLM_AI_QuoteDemoSummaryService.SummaryOutput> results =
            RLM_AI_QuoteDemoSummaryService.getSummary(
                new List<RLM_AI_QuoteDemoSummaryService.SummaryInput>{ input }
            );

        System.assertEquals(true, results[0].isSuccess,
            'A quote with no lines still produces a recap.');
        System.assert(results[0].summaryDisplay.contains('Line items: 0'));
        System.assert(results[0].summaryDisplay.contains('Empty Recap Quote'));
    }

    @isTest
    static void summaryRejectsBlankQuoteId() {
        RLM_AI_QuoteDemoSummaryService.SummaryInput input =
            new RLM_AI_QuoteDemoSummaryService.SummaryInput();
        input.quoteId = '   ';

        List<RLM_AI_QuoteDemoSummaryService.SummaryOutput> results =
            RLM_AI_QuoteDemoSummaryService.getSummary(
                new List<RLM_AI_QuoteDemoSummaryService.SummaryInput>{ input }
            );

        System.assertEquals(false, results[0].isSuccess);
        System.assert(results[0].errorMessage.contains('Quote Id is required'));
    }

    @isTest
    static void summaryRejectsInvalidQuoteId() {
        RLM_AI_QuoteDemoSummaryService.SummaryInput input =
            new RLM_AI_QuoteDemoSummaryService.SummaryInput();
        input.quoteId = 'not-an-id';

        List<RLM_AI_QuoteDemoSummaryService.SummaryOutput> results =
            RLM_AI_QuoteDemoSummaryService.getSummary(
                new List<RLM_AI_QuoteDemoSummaryService.SummaryInput>{ input }
            );

        System.assertEquals(false, results[0].isSuccess);
        System.assert(results[0].errorMessage.contains('Invalid quote Id'));
    }

    @isTest
    static void summaryReturnsEmptyForNullInputList() {
        List<RLM_AI_QuoteDemoSummaryService.SummaryOutput> results =
            RLM_AI_QuoteDemoSummaryService.getSummary(null);
        System.assertEquals(0, results.size());
    }

    private static Id addQuoteLineItem(Id quoteId, String productName) {
        Id standardPbId = Test.getStandardPricebookId();
        Product2 product = new Product2(Name = productName, IsActive = true);
        insert product;
        PricebookEntry pbe = new PricebookEntry(
            Pricebook2Id = standardPbId,
            Product2Id = product.Id,
            UnitPrice = 100,
            IsActive = true
        );
        insert pbe;
        QuoteLineItem qli = new QuoteLineItem(
            QuoteId = quoteId,
            PricebookEntryId = pbe.Id,
            Quantity = 1,
            UnitPrice = 100
        );
        insert qli;
        return qli.Id;
    }
}
