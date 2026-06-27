@isTest
private class RLM_AI_QuoteLineItemLookupServiceTest {
    @isTest
    static void lookupReturnsMatchWhenProductExists() {
        RLM_AI_ProductConfigTestDataFactory.QuoteFixture fixture =
            RLM_AI_ProductConfigTestDataFactory.createQuoteFixture('FESBA Generator Set');

        RLM_AI_QuoteLineItemLookupService.LookupInput input =
            new RLM_AI_QuoteLineItemLookupService.LookupInput();
        input.quoteId = String.valueOf(fixture.quoteId);
        input.productName = 'FESBA Generator Set';

        Test.startTest();
        List<RLM_AI_QuoteLineItemLookupService.LookupOutput> results =
            RLM_AI_QuoteLineItemLookupService.lookup(
                new List<RLM_AI_QuoteLineItemLookupService.LookupInput>{ input }
            );
        Test.stopTest();

        System.assertEquals(1, results.size(), 'One result should be returned.');
        System.assertEquals(true, results[0].isSuccess, 'Lookup ran correctly.');
        System.assertEquals(true, results[0].isFound, 'Expected product match.');
        System.assertEquals(String.valueOf(fixture.quoteLineItemId), results[0].quoteLineItemId);
        System.assertEquals('FESBA Generator Set', results[0].productNameFound);
        System.assertEquals(false, results[0].needsDisambiguation);
        System.assert(results[0].matchConfidencePercent >= 80);
    }

    @isTest
    static void lookupReturnsNotFoundWhenNoMatch() {
        RLM_AI_ProductConfigTestDataFactory.QuoteFixture fixture =
            RLM_AI_ProductConfigTestDataFactory.createQuoteFixture('FESBA Generator Set');

        RLM_AI_QuoteLineItemLookupService.LookupInput input =
            new RLM_AI_QuoteLineItemLookupService.LookupInput();
        input.quoteId = String.valueOf(fixture.quoteId);
        input.productName = 'NoSuchProduct';

        List<RLM_AI_QuoteLineItemLookupService.LookupOutput> results =
            RLM_AI_QuoteLineItemLookupService.lookup(
                new List<RLM_AI_QuoteLineItemLookupService.LookupInput>{ input }
            );

        System.assertEquals(true, results[0].isSuccess, 'A no-match outcome still ran correctly.');
        System.assertEquals(false, results[0].isFound);
        System.assertNotEquals(null, results[0].errorMessage);
        System.assert(results[0].errorMessage.contains('No QuoteLineItem found'));
    }

    @isTest
    static void lookupHandlesInvalidQuoteId() {
        RLM_AI_QuoteLineItemLookupService.LookupInput input =
            new RLM_AI_QuoteLineItemLookupService.LookupInput();
        input.quoteId = 'not-an-id';
        input.productName = 'Generator';

        List<RLM_AI_QuoteLineItemLookupService.LookupOutput> results =
            RLM_AI_QuoteLineItemLookupService.lookup(
                new List<RLM_AI_QuoteLineItemLookupService.LookupInput>{ input }
            );

        System.assertEquals(false, results[0].isSuccess, 'An invalid quote Id is a system/input error.');
        System.assertEquals(false, results[0].isFound);
        System.assertNotEquals(null, results[0].errorMessage);
        System.assert(results[0].errorMessage.contains('Invalid quote Id'));
    }

    @isTest
    static void lookupPrefersExactMatchOverPartialMatch() {
        RLM_AI_ProductConfigTestDataFactory.QuoteFixture fixture =
            RLM_AI_ProductConfigTestDataFactory.createQuoteFixture('Generator');

        addQuoteLineItem(fixture.quoteId, 'FESBA Generator Set');
        addQuoteLineItem(fixture.quoteId, 'Generator Plus');

        RLM_AI_QuoteLineItemLookupService.LookupInput input =
            new RLM_AI_QuoteLineItemLookupService.LookupInput();
        input.quoteId = String.valueOf(fixture.quoteId);
        input.productName = 'Generator';

        List<RLM_AI_QuoteLineItemLookupService.LookupOutput> results =
            RLM_AI_QuoteLineItemLookupService.lookup(
                new List<RLM_AI_QuoteLineItemLookupService.LookupInput>{ input }
            );

        System.assertEquals(true, results[0].isFound);
        System.assertEquals('Generator', results[0].productNameFound);
        System.assert(results[0].matchConfidencePercent >= 80);
    }

    @isTest
    static void lookupEscapesLikeWildcardsInSearchText() {
        RLM_AI_ProductConfigTestDataFactory.QuoteFixture fixture =
            RLM_AI_ProductConfigTestDataFactory.createQuoteFixture('100% Pure Generator');

        addQuoteLineItem(fixture.quoteId, '100X Pure Generator');

        RLM_AI_QuoteLineItemLookupService.LookupInput input =
            new RLM_AI_QuoteLineItemLookupService.LookupInput();
        input.quoteId = String.valueOf(fixture.quoteId);
        input.productName = '100% Pure';

        List<RLM_AI_QuoteLineItemLookupService.LookupOutput> results =
            RLM_AI_QuoteLineItemLookupService.lookup(
                new List<RLM_AI_QuoteLineItemLookupService.LookupInput>{ input }
            );

        System.assertEquals(true, results[0].isFound);
        System.assertEquals('100% Pure Generator', results[0].productNameFound);
    }

    @isTest
    static void lookupListsAllLinesWhenProductNameIsBlank() {
        RLM_AI_ProductConfigTestDataFactory.QuoteFixture fixture =
            RLM_AI_ProductConfigTestDataFactory.createQuoteFixture('FESBA Generator Set');
        addQuoteLineItem(fixture.quoteId, 'Support Plan');
        addQuoteLineItem(fixture.quoteId, 'Extended Warranty');

        RLM_AI_QuoteLineItemLookupService.LookupInput input =
            new RLM_AI_QuoteLineItemLookupService.LookupInput();
        input.quoteId = String.valueOf(fixture.quoteId);
        input.productName = '  ';

        List<RLM_AI_QuoteLineItemLookupService.LookupOutput> results =
            RLM_AI_QuoteLineItemLookupService.lookup(
                new List<RLM_AI_QuoteLineItemLookupService.LookupInput>{ input }
            );

        // Blank product name = list-all mode: every line is returned as a
        // candidate, never auto-selected, so the agent can offer all/multiple.
        System.assertEquals(true, results[0].isSuccess, 'List-all ran correctly.');
        System.assertEquals(false, results[0].isFound, 'List-all never auto-selects a single line.');
        System.assertEquals(true, results[0].needsDisambiguation);
        System.assertEquals(null, results[0].quoteLineItemId);
        System.assertNotEquals('', results[0].candidateQuoteLineSummariesDisplay);
        System.assert(results[0].candidateQuoteLineSummariesDisplay.contains('Select the quote line(s) to update:'));
        System.assert(results[0].candidateQuoteLineSummariesDisplay.contains('FESBA Generator Set'));

        List<Object> summaries = (List<Object>) JSON.deserializeUntyped(results[0].candidateQuoteLineSummariesJson);
        System.assertEquals(3, summaries.size(), 'All three quote lines should be returned (not capped at 3-candidate disambiguation limit).');
        Set<String> summaryNames = new Set<String>();
        for (Object summaryObj : summaries) {
            Map<String, Object> summary = (Map<String, Object>) summaryObj;
            summaryNames.add(String.valueOf(summary.get('productName')));
            System.assertNotEquals(null, summary.get('quoteLineItemId'));
            System.assertNotEquals(null, summary.get('netUnitPrice'));
            System.assertNotEquals(null, summary.get('netTotalPrice'));
        }
        System.assert(summaryNames.contains('FESBA Generator Set'));
        System.assert(summaryNames.contains('Support Plan'));
        System.assert(summaryNames.contains('Extended Warranty'));
    }

    @isTest
    static void lookupListAllReturnsNoLinesWhenQuoteHasNone() {
        // Quote with no line items: createQuoteFixture always adds one, so
        // build a bare quote to exercise the empty branch.
        Account acct = new Account(Name = 'Empty Quote Account');
        insert acct;
        Opportunity opp = new Opportunity(
            Name = 'Empty Quote Opportunity',
            AccountId = acct.Id,
            StageName = 'Prospecting',
            CloseDate = Date.today().addDays(30)
        );
        insert opp;
        Quote q = new Quote(
            Name = 'Empty Quote',
            Pricebook2Id = Test.getStandardPricebookId(),
            OpportunityId = opp.Id,
            Status = 'Draft'
        );
        insert q;

        RLM_AI_QuoteLineItemLookupService.LookupInput input =
            new RLM_AI_QuoteLineItemLookupService.LookupInput();
        input.quoteId = String.valueOf(q.Id);
        input.productName = null;

        List<RLM_AI_QuoteLineItemLookupService.LookupOutput> results =
            RLM_AI_QuoteLineItemLookupService.lookup(
                new List<RLM_AI_QuoteLineItemLookupService.LookupInput>{ input }
            );

        System.assertEquals(true, results[0].isSuccess, 'Empty list-all still ran correctly.');
        System.assertEquals(false, results[0].isFound);
        System.assertEquals(false, results[0].needsDisambiguation);
        System.assert(results[0].errorMessage.contains('No quote lines were found'));
    }

    @isTest
    static void lookupRequestsDisambiguationForLowConfidencePartialMatch() {
        RLM_AI_ProductConfigTestDataFactory.QuoteFixture fixture =
            RLM_AI_ProductConfigTestDataFactory.createQuoteFixture('FESBA Generator Set');

        addQuoteLineItem(fixture.quoteId, 'FESBA Generator Pro');
        addQuoteLineItem(fixture.quoteId, 'FESBA Generator Ultra');

        RLM_AI_QuoteLineItemLookupService.LookupInput input =
            new RLM_AI_QuoteLineItemLookupService.LookupInput();
        input.quoteId = String.valueOf(fixture.quoteId);
        input.productName = 'Gen';

        List<RLM_AI_QuoteLineItemLookupService.LookupOutput> results =
            RLM_AI_QuoteLineItemLookupService.lookup(
                new List<RLM_AI_QuoteLineItemLookupService.LookupInput>{ input }
            );

        System.assertEquals(true, results[0].isSuccess, 'A disambiguation outcome still ran correctly.');
        System.assertEquals(false, results[0].isFound);
        System.assertEquals(true, results[0].needsDisambiguation);
        System.assert(results[0].matchConfidencePercent < 80);
        System.assertEquals(null, results[0].quoteLineItemId);
        System.assertNotEquals(null, results[0].candidateProductNamesJson);
        System.assert(results[0].candidateProductNamesJson.contains('FESBA Generator Set'));
        System.assertNotEquals(null, results[0].candidateProducts);
        System.assert(results[0].candidateProducts.size() > 0);
        System.assertNotEquals(null, results[0].candidateQuoteLineItems);
        System.assert(results[0].candidateQuoteLineItems.size() > 0);
        System.assertNotEquals(null, results[0].candidateQuoteLineItems[0].Product2.Name);
        System.assertEquals(
            100,
            results[0].candidateQuoteLineItems[0].UnitPrice,
            'Candidate quote lines should display NetUnitPrice when available and otherwise UnitPrice.'
        );
        System.assertNotEquals('[]', results[0].candidateQuoteLineSummariesJson);
        System.assertNotEquals('', results[0].candidateQuoteLineSummariesDisplay);
        System.assert(results[0].candidateQuoteLineSummariesDisplay.contains('Net Unit Price'));
        System.assert(results[0].candidateQuoteLineSummariesDisplay.contains('FESBA Generator Set'));
        List<Object> summaries = (List<Object>) JSON.deserializeUntyped(results[0].candidateQuoteLineSummariesJson);
        System.assert(summaries.size() > 0);
        Set<String> summaryNames = new Set<String>();
        for (Object summaryObj : summaries) {
            Map<String, Object> summary = (Map<String, Object>) summaryObj;
            summaryNames.add(String.valueOf(summary.get('productName')));
            System.assertNotEquals(null, summary.get('netUnitPrice'));
            System.assertNotEquals(null, summary.get('netTotalPrice'));
        }
        System.assert(summaryNames.contains('FESBA Generator Set'));
    }

    @isTest
    static void lookupRespectsCustomThresholdAndAutoSelectsWhenLowered() {
        RLM_AI_ProductConfigTestDataFactory.QuoteFixture fixture =
            RLM_AI_ProductConfigTestDataFactory.createQuoteFixture('FESBA Generator Set');
        addQuoteLineItem(fixture.quoteId, 'FESBA Generator Pro');

        RLM_AI_QuoteLineItemLookupService.LookupInput input =
            new RLM_AI_QuoteLineItemLookupService.LookupInput();
        input.quoteId = String.valueOf(fixture.quoteId);
        input.productName = 'Generator';
        input.autoSelectThresholdPercent = 70;

        List<RLM_AI_QuoteLineItemLookupService.LookupOutput> results =
            RLM_AI_QuoteLineItemLookupService.lookup(
                new List<RLM_AI_QuoteLineItemLookupService.LookupInput>{ input }
            );

        System.assertEquals(true, results[0].isFound);
        System.assertEquals(false, results[0].needsDisambiguation);
        System.assert(results[0].matchConfidencePercent >= 70);
    }

    @isTest
    static void lookupRespectsCustomThresholdAndDisambiguatesWhenRaised() {
        RLM_AI_ProductConfigTestDataFactory.QuoteFixture fixture =
            RLM_AI_ProductConfigTestDataFactory.createQuoteFixture('Generator Plus');
        addQuoteLineItem(fixture.quoteId, 'Generator Pro');

        RLM_AI_QuoteLineItemLookupService.LookupInput input =
            new RLM_AI_QuoteLineItemLookupService.LookupInput();
        input.quoteId = String.valueOf(fixture.quoteId);
        input.productName = 'Generator';
        input.autoSelectThresholdPercent = 95;

        List<RLM_AI_QuoteLineItemLookupService.LookupOutput> results =
            RLM_AI_QuoteLineItemLookupService.lookup(
                new List<RLM_AI_QuoteLineItemLookupService.LookupInput>{ input }
            );

        System.assertEquals(false, results[0].isFound);
        System.assertEquals(true, results[0].needsDisambiguation);
        System.assert(results[0].matchConfidencePercent < 95);
        System.assert(results[0].candidateProducts.size() > 0);
        System.assert(results[0].candidateQuoteLineItems.size() > 0);
        System.assert(results[0].errorMessage.contains('95%'));
    }

    @isTest
    static void lookupDisambiguatesWhenDuplicateTopProductLinesExist() {
        RLM_AI_ProductConfigTestDataFactory.QuoteFixture fixture =
            RLM_AI_ProductConfigTestDataFactory.createQuoteFixture('Additional API');
        addQuoteLineItem(fixture.quoteId, 'Additional API');
        addQuoteLineItem(fixture.quoteId, 'Additional API Plus');

        RLM_AI_QuoteLineItemLookupService.LookupInput input =
            new RLM_AI_QuoteLineItemLookupService.LookupInput();
        input.quoteId = String.valueOf(fixture.quoteId);
        input.productName = 'Additional API';

        List<RLM_AI_QuoteLineItemLookupService.LookupOutput> results =
            RLM_AI_QuoteLineItemLookupService.lookup(
                new List<RLM_AI_QuoteLineItemLookupService.LookupInput>{ input }
            );

        System.assertEquals(false, results[0].isFound);
        System.assertEquals(true, results[0].needsDisambiguation);
        System.assertEquals(null, results[0].quoteLineItemId);
        System.assert(results[0].candidateQuoteLineItems.size() >= 2);
        System.assert(results[0].errorMessage.contains('Multiple quote lines were found'));
        List<Object> summaries = (List<Object>) JSON.deserializeUntyped(results[0].candidateQuoteLineSummariesJson);
        System.assert(summaries.size() >= 2);
        for (Object summaryObj : summaries) {
            Map<String, Object> summary = (Map<String, Object>) summaryObj;
            System.assertNotEquals(null, summary.get('quoteLineItemId'));
            System.assertNotEquals(null, summary.get('productName'));
            System.assertNotEquals(null, summary.get('netUnitPrice'));
            System.assertNotEquals(null, summary.get('netTotalPrice'));
        }
    }

    private static Id addQuoteLineItem(Id quoteId, String productName) {
        Id standardPbId = Test.getStandardPricebookId();

        Product2 product = new Product2(
            Name = productName,
            IsActive = true
        );
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
