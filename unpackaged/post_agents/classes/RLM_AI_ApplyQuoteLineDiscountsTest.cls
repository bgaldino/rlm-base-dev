@isTest
private class RLM_AI_ApplyQuoteLineDiscountsTest {

    // ---- Fake invoker: records every call and returns a canned result ----
    private class FakeInvoker implements RLM_AI_ApplyQuoteLineDiscountsService.ManagedDiscountInvoker {
        public Boolean returnSuccess = true;
        public String returnError = null;
        public Integer callCount = 0;
        public Map<Id, Decimal> percentByLine = new Map<Id, Decimal>();
        // Ids that should fail when invoked (simulates a per-line managed error).
        public Set<Id> failForLines = new Set<Id>();

        public RLM_AI_ApplyQuoteLineDiscountsService.ManagedResult applyDiscount(
            Id quoteId, Id quoteLineItemId, Decimal discountPercentage
        ) {
            callCount++;
            percentByLine.put(quoteLineItemId, discountPercentage);
            if (failForLines.contains(quoteLineItemId)) {
                return new RLM_AI_ApplyQuoteLineDiscountsService.ManagedResult(false, 'line failed');
            }
            return new RLM_AI_ApplyQuoteLineDiscountsService.ManagedResult(returnSuccess, returnError);
        }
    }

    @isTest
    static void applyToAllDiscountsEveryLineByPercent() {
        Fixture f = buildFixture(new List<String>{ 'Quinn Alpha', 'Quinn Beta' });
        FakeInvoker fake = new FakeInvoker();
        RLM_AI_ApplyQuoteLineDiscountsService.invoker = fake;

        RLM_AI_ApplyQuoteLineDiscountsService.DiscountInput input = baseInput(f.quoteId);
        input.applyToAll = true;
        input.discountMode = 'percent';
        input.discountPercentage = 10;

        Test.startTest();
        List<RLM_AI_ApplyQuoteLineDiscountsService.DiscountOutput> results =
            RLM_AI_ApplyQuoteLineDiscountsService.applyDiscounts(
                new List<RLM_AI_ApplyQuoteLineDiscountsService.DiscountInput>{ input });
        Test.stopTest();

        RLM_AI_ApplyQuoteLineDiscountsService.DiscountOutput out = results[0];
        System.assertEquals(true, out.isSuccess, 'error: ' + out.errorMessage);
        System.assertEquals(2, out.appliedCount);
        System.assertEquals(2, fake.callCount);
        for (Decimal pct : fake.percentByLine.values()) {
            System.assertEquals(10, pct, 'percent mode passes the flat percentage.');
        }
        System.assert(out.resultsDisplay.contains('Quinn Alpha'));
        System.assert(out.resultsDisplay.contains('Quinn Beta'));
        // Names-only: must not leak raw line Ids.
        for (Id lineId : f.lineIds) {
            System.assert(!out.resultsDisplay.contains(String.valueOf(lineId)));
        }
    }

    @isTest
    static void percentOfListConvertsToComplementaryDiscount() {
        Fixture f = buildFixture(new List<String>{ 'Quinn Gamma' });
        FakeInvoker fake = new FakeInvoker();
        RLM_AI_ApplyQuoteLineDiscountsService.invoker = fake;

        RLM_AI_ApplyQuoteLineDiscountsService.DiscountInput input = baseInput(f.quoteId);
        input.applyToAll = true;
        input.discountMode = 'percentOfList';
        input.targetPercentOfList = 90;

        List<RLM_AI_ApplyQuoteLineDiscountsService.DiscountOutput> results =
            RLM_AI_ApplyQuoteLineDiscountsService.applyDiscounts(
                new List<RLM_AI_ApplyQuoteLineDiscountsService.DiscountInput>{ input });

        System.assertEquals(true, results[0].isSuccess, 'error: ' + results[0].errorMessage);
        System.assertEquals(10, fake.percentByLine.get(f.lineIds[0]),
            'Selling at 90% of list = 10% discount.');
    }

    @isTest
    static void targetPriceConvertsFromUnitPrice() {
        // UnitPrice = 100 (factory default). Sell at 75 -> 25% discount.
        Fixture f = buildFixture(new List<String>{ 'Quinn Delta' });
        FakeInvoker fake = new FakeInvoker();
        RLM_AI_ApplyQuoteLineDiscountsService.invoker = fake;

        RLM_AI_ApplyQuoteLineDiscountsService.DiscountInput input = baseInput(f.quoteId);
        input.applyToAll = true;
        input.discountMode = 'targetPrice';
        input.targetPrice = 75;

        List<RLM_AI_ApplyQuoteLineDiscountsService.DiscountOutput> results =
            RLM_AI_ApplyQuoteLineDiscountsService.applyDiscounts(
                new List<RLM_AI_ApplyQuoteLineDiscountsService.DiscountInput>{ input });

        System.assertEquals(true, results[0].isSuccess, 'error: ' + results[0].errorMessage);
        System.assertEquals(25, fake.percentByLine.get(f.lineIds[0]),
            'Target price 75 against list 100 = 25% off.');
    }

    @isTest
    static void targetPriceAboveListIsZeroDiscount() {
        Fixture f = buildFixture(new List<String>{ 'Quinn Epsilon' });
        FakeInvoker fake = new FakeInvoker();
        RLM_AI_ApplyQuoteLineDiscountsService.invoker = fake;

        RLM_AI_ApplyQuoteLineDiscountsService.DiscountInput input = baseInput(f.quoteId);
        input.applyToAll = true;
        input.discountMode = 'targetPrice';
        input.targetPrice = 150;

        List<RLM_AI_ApplyQuoteLineDiscountsService.DiscountOutput> results =
            RLM_AI_ApplyQuoteLineDiscountsService.applyDiscounts(
                new List<RLM_AI_ApplyQuoteLineDiscountsService.DiscountInput>{ input });

        System.assertEquals(0, fake.percentByLine.get(f.lineIds[0]),
            'Target at/above list yields no discount.');
    }

    @isTest
    static void productNameTargetsMatchingLinesOnly() {
        Fixture f = buildFixture(new List<String>{ 'Quinn Server', 'Quinn Cable' });
        FakeInvoker fake = new FakeInvoker();
        RLM_AI_ApplyQuoteLineDiscountsService.invoker = fake;

        RLM_AI_ApplyQuoteLineDiscountsService.DiscountInput input = baseInput(f.quoteId);
        input.productName = 'Server';
        input.discountMode = 'percent';
        input.discountPercentage = 5;

        List<RLM_AI_ApplyQuoteLineDiscountsService.DiscountOutput> results =
            RLM_AI_ApplyQuoteLineDiscountsService.applyDiscounts(
                new List<RLM_AI_ApplyQuoteLineDiscountsService.DiscountInput>{ input });

        System.assertEquals(true, results[0].isSuccess, 'error: ' + results[0].errorMessage);
        System.assertEquals(1, results[0].appliedCount, 'Only the Server line matches.');
        System.assertEquals(1, fake.callCount);
    }

    @isTest
    static void explicitIdsFromOtherQuoteAreRejected() {
        Fixture f = buildFixture(new List<String>{ 'Quinn One' });
        Fixture other = buildFixture(new List<String>{ 'Quinn Other' });
        FakeInvoker fake = new FakeInvoker();
        RLM_AI_ApplyQuoteLineDiscountsService.invoker = fake;

        RLM_AI_ApplyQuoteLineDiscountsService.DiscountInput input = baseInput(f.quoteId);
        input.discountMode = 'percent';
        input.discountPercentage = 10;
        // One Id from this quote, one from another quote.
        input.quoteLineItemIds = new List<String>{
            String.valueOf(f.lineIds[0]), String.valueOf(other.lineIds[0])
        };

        List<RLM_AI_ApplyQuoteLineDiscountsService.DiscountOutput> results =
            RLM_AI_ApplyQuoteLineDiscountsService.applyDiscounts(
                new List<RLM_AI_ApplyQuoteLineDiscountsService.DiscountInput>{ input });

        System.assertEquals(false, results[0].isSuccess);
        System.assertEquals(0, fake.callCount, 'No mutation when ownership validation fails.');
        System.assert(results[0].errorMessage.contains('do not belong to this quote'));
    }

    @isTest
    static void ordinalsMapThroughPendingSelectionJson() {
        Fixture f = buildFixture(new List<String>{ 'Quinn A', 'Quinn B', 'Quinn C' });
        FakeInvoker fake = new FakeInvoker();
        RLM_AI_ApplyQuoteLineDiscountsService.invoker = fake;

        // Map ordinal 2 -> the third line's Id (a list ordered differently than
        // a fresh query), to prove ordinals resolve through the carried map only.
        Map<String, String> pending = new Map<String, String>{
            '1' => String.valueOf(f.lineIds[2]),
            '2' => String.valueOf(f.lineIds[0])
        };

        RLM_AI_ApplyQuoteLineDiscountsService.DiscountInput input = baseInput(f.quoteId);
        input.discountMode = 'percent';
        input.discountPercentage = 15;
        input.selectedDisplayNumbersJson = '[2]';
        input.pendingSelectionJson = JSON.serialize(pending);

        List<RLM_AI_ApplyQuoteLineDiscountsService.DiscountOutput> results =
            RLM_AI_ApplyQuoteLineDiscountsService.applyDiscounts(
                new List<RLM_AI_ApplyQuoteLineDiscountsService.DiscountInput>{ input });

        System.assertEquals(true, results[0].isSuccess, 'error: ' + results[0].errorMessage);
        System.assertEquals(1, fake.callCount);
        System.assert(fake.percentByLine.containsKey(f.lineIds[0]),
            'Ordinal 2 should map to the first line via the pending map.');
    }

    @isTest
    static void ordinalNotInPendingMapIsRejected() {
        Fixture f = buildFixture(new List<String>{ 'Quinn A', 'Quinn B' });
        FakeInvoker fake = new FakeInvoker();
        RLM_AI_ApplyQuoteLineDiscountsService.invoker = fake;

        Map<String, String> pending = new Map<String, String>{
            '1' => String.valueOf(f.lineIds[0])
        };
        RLM_AI_ApplyQuoteLineDiscountsService.DiscountInput input = baseInput(f.quoteId);
        input.discountMode = 'percent';
        input.discountPercentage = 10;
        input.selectedDisplayNumbersJson = '[5]';
        input.pendingSelectionJson = JSON.serialize(pending);

        List<RLM_AI_ApplyQuoteLineDiscountsService.DiscountOutput> results =
            RLM_AI_ApplyQuoteLineDiscountsService.applyDiscounts(
                new List<RLM_AI_ApplyQuoteLineDiscountsService.DiscountInput>{ input });

        System.assertEquals(false, results[0].isSuccess);
        System.assertEquals(0, fake.callCount);
        System.assert(results[0].errorMessage.contains('not in the list shown'));
    }

    @isTest
    static void ordinalsFallBackToFreshList() {
        Fixture f = buildFixture(new List<String>{ 'Quinn A', 'Quinn B', 'Quinn C' });
        FakeInvoker fake = new FakeInvoker();
        RLM_AI_ApplyQuoteLineDiscountsService.invoker = fake;

        // No pendingSelectionJson -> ordinals index into the helper's own list.
        RLM_AI_ApplyQuoteLineDiscountsService.DiscountInput input = baseInput(f.quoteId);
        input.discountMode = 'percent';
        input.discountPercentage = 20;
        input.selectedDisplayNumbersJson = '[1,3]';

        List<RLM_AI_ApplyQuoteLineDiscountsService.DiscountOutput> results =
            RLM_AI_ApplyQuoteLineDiscountsService.applyDiscounts(
                new List<RLM_AI_ApplyQuoteLineDiscountsService.DiscountInput>{ input });

        System.assertEquals(true, results[0].isSuccess, 'error: ' + results[0].errorMessage);
        System.assertEquals(2, results[0].appliedCount);
    }

    @isTest
    static void noTargetingPresentsDisambiguation() {
        Fixture f = buildFixture(new List<String>{ 'Quinn A', 'Quinn B' });
        FakeInvoker fake = new FakeInvoker();
        RLM_AI_ApplyQuoteLineDiscountsService.invoker = fake;

        RLM_AI_ApplyQuoteLineDiscountsService.DiscountInput input = baseInput(f.quoteId);
        input.discountMode = 'percent';
        input.discountPercentage = 10;
        // No applyToAll, no productName, no ordinals, no Ids.

        List<RLM_AI_ApplyQuoteLineDiscountsService.DiscountOutput> results =
            RLM_AI_ApplyQuoteLineDiscountsService.applyDiscounts(
                new List<RLM_AI_ApplyQuoteLineDiscountsService.DiscountInput>{ input });

        RLM_AI_ApplyQuoteLineDiscountsService.DiscountOutput out = results[0];
        System.assertEquals(true, out.needsDisambiguation);
        System.assertEquals(0, fake.callCount);
        System.assert(String.isNotBlank(out.pendingSelectionJson),
            'Disambiguation emits the ordinal map for the next turn.');
        System.assert(out.candidateSummariesDisplay.contains('Quinn A'));
    }

    @isTest
    static void rejectsMissingMode() {
        Fixture f = buildFixture(new List<String>{ 'Quinn A' });
        RLM_AI_ApplyQuoteLineDiscountsService.DiscountInput input = baseInput(f.quoteId);
        input.applyToAll = true;
        // No mode, no values.

        List<RLM_AI_ApplyQuoteLineDiscountsService.DiscountOutput> results =
            RLM_AI_ApplyQuoteLineDiscountsService.applyDiscounts(
                new List<RLM_AI_ApplyQuoteLineDiscountsService.DiscountInput>{ input });

        System.assertEquals(false, results[0].isSuccess);
        System.assert(results[0].errorMessage.contains('exactly one discount'));
    }

    @isTest
    static void rejectsOutOfRangePercent() {
        Fixture f = buildFixture(new List<String>{ 'Quinn A' });
        RLM_AI_ApplyQuoteLineDiscountsService.DiscountInput input = baseInput(f.quoteId);
        input.applyToAll = true;
        input.discountMode = 'percent';
        input.discountPercentage = 150;

        List<RLM_AI_ApplyQuoteLineDiscountsService.DiscountOutput> results =
            RLM_AI_ApplyQuoteLineDiscountsService.applyDiscounts(
                new List<RLM_AI_ApplyQuoteLineDiscountsService.DiscountInput>{ input });

        System.assertEquals(false, results[0].isSuccess);
        System.assert(results[0].errorMessage.contains('between 0 and 100'));
    }

    @isTest
    static void partialFailureReportsBoth() {
        Fixture f = buildFixture(new List<String>{ 'Quinn A', 'Quinn B' });
        FakeInvoker fake = new FakeInvoker();
        fake.failForLines.add(f.lineIds[1]);
        RLM_AI_ApplyQuoteLineDiscountsService.invoker = fake;

        RLM_AI_ApplyQuoteLineDiscountsService.DiscountInput input = baseInput(f.quoteId);
        input.applyToAll = true;
        input.discountMode = 'percent';
        input.discountPercentage = 10;

        List<RLM_AI_ApplyQuoteLineDiscountsService.DiscountOutput> results =
            RLM_AI_ApplyQuoteLineDiscountsService.applyDiscounts(
                new List<RLM_AI_ApplyQuoteLineDiscountsService.DiscountInput>{ input });

        RLM_AI_ApplyQuoteLineDiscountsService.DiscountOutput out = results[0];
        System.assertEquals(false, out.isSuccess, 'A partial failure is not full success.');
        System.assertEquals(1, out.appliedCount);
        System.assert(out.resultsDisplay.contains('Could not discount'));
    }

    @isTest
    static void rejectsBlankQuoteId() {
        RLM_AI_ApplyQuoteLineDiscountsService.DiscountInput input =
            new RLM_AI_ApplyQuoteLineDiscountsService.DiscountInput();
        input.quoteId = '  ';
        input.applyToAll = true;
        input.discountMode = 'percent';
        input.discountPercentage = 10;

        List<RLM_AI_ApplyQuoteLineDiscountsService.DiscountOutput> results =
            RLM_AI_ApplyQuoteLineDiscountsService.applyDiscounts(
                new List<RLM_AI_ApplyQuoteLineDiscountsService.DiscountInput>{ input });

        System.assertEquals(false, results[0].isSuccess);
        System.assert(results[0].errorMessage.contains('Quote Id is required'));
    }

    @isTest
    static void emptyInputListReturnsEmpty() {
        List<RLM_AI_ApplyQuoteLineDiscountsService.DiscountOutput> results =
            RLM_AI_ApplyQuoteLineDiscountsService.applyDiscounts(null);
        System.assertEquals(0, results.size());
    }

    // ---- Tokenized product-name matching tests ----

    @isTest
    static void tokenMatcherExactMatch() {
        System.assertEquals(true,
            RLM_AI_ConfigServiceUtils.productNameMatchesTokens('QB API Management', 'QB API Management'),
            'Exact match should succeed');
    }

    @isTest
    static void tokenMatcherCaseInsensitive() {
        System.assertEquals(true,
            RLM_AI_ConfigServiceUtils.productNameMatchesTokens('QB API Management', 'qb api management'),
            'Case-insensitive match should succeed');
    }

    @isTest
    static void tokenMatcherMissingTrailingWord() {
        System.assertEquals(true,
            RLM_AI_ConfigServiceUtils.productNameMatchesTokens(
                'QB API Management Solution', 'QB API Management'
            ),
            'All search tokens present should match');
    }

    @isTest
    static void tokenMatcherReorderedTokens() {
        System.assertEquals(true,
            RLM_AI_ConfigServiceUtils.productNameMatchesTokens(
                'API Management QB Solution', 'QB Management API'
            ),
            'Reordered tokens should match');
    }

    @isTest
    static void tokenMatcherPartialTokenMatch() {
        System.assertEquals(true,
            RLM_AI_ConfigServiceUtils.productNameMatchesTokens(
                'Additional API Product', 'API'
            ),
            'Single token should match multiple products');
    }

    @isTest
    static void tokenMatcherMissingTokenFails() {
        System.assertEquals(false,
            RLM_AI_ConfigServiceUtils.productNameMatchesTokens(
                'QB Management Solution', 'QB API Management'
            ),
            'Missing token API should fail');
    }

    @isTest
    static void tokenMatcherBlankSearchFails() {
        System.assertEquals(false,
            RLM_AI_ConfigServiceUtils.productNameMatchesTokens('Product Name', ''),
            'Blank search should fail');
    }

    @isTest
    static void tokenMatcherBlankProductFails() {
        System.assertEquals(false,
            RLM_AI_ConfigServiceUtils.productNameMatchesTokens('', 'search term'),
            'Blank product should fail');
    }

    @isTest
    static void productNameTokenizedMatchByPartName() {
        Fixture f = buildFixture(new List<String>{
            'QB API Management Solution',
            'QB Server Standard',
            'Quinn Cable'
        });
        FakeInvoker fake = new FakeInvoker();
        RLM_AI_ApplyQuoteLineDiscountsService.invoker = fake;

        RLM_AI_ApplyQuoteLineDiscountsService.DiscountInput input = baseInput(f.quoteId);
        input.productName = 'QB API Management';
        input.discountMode = 'percent';
        input.discountPercentage = 5;

        List<RLM_AI_ApplyQuoteLineDiscountsService.DiscountOutput> results =
            RLM_AI_ApplyQuoteLineDiscountsService.applyDiscounts(
                new List<RLM_AI_ApplyQuoteLineDiscountsService.DiscountInput>{ input });

        RLM_AI_ApplyQuoteLineDiscountsService.DiscountOutput out = results[0];
        System.assertEquals(true, out.isSuccess, 'error: ' + out.errorMessage);
        System.assertEquals(1, out.appliedCount,
            'Only QB API Management Solution should match');
        System.assertEquals(1, fake.callCount);
    }

    // ---- Fixture helpers ----

    private class Fixture {
        Id quoteId;
        List<Id> lineIds = new List<Id>();
    }

    private static RLM_AI_ApplyQuoteLineDiscountsService.DiscountInput baseInput(Id quoteId) {
        RLM_AI_ApplyQuoteLineDiscountsService.DiscountInput input =
            new RLM_AI_ApplyQuoteLineDiscountsService.DiscountInput();
        input.quoteId = String.valueOf(quoteId);
        return input;
    }

    private static Fixture buildFixture(List<String> productNames) {
        Account acct = new Account(Name = 'Quinn Discount Account');
        insert acct;
        Opportunity opp = new Opportunity(
            Name = 'Quinn Discount Opportunity',
            AccountId = acct.Id,
            StageName = 'Prospecting',
            CloseDate = Date.today().addDays(30)
        );
        insert opp;
        Quote q = new Quote(
            Name = 'Quinn Discount Quote',
            OpportunityId = opp.Id,
            Pricebook2Id = Test.getStandardPricebookId(),
            Status = 'Draft'
        );
        insert q;

        Fixture f = new Fixture();
        f.quoteId = q.Id;

        List<QuoteLineItem> lines = new List<QuoteLineItem>();
        for (String name : productNames) {
            Product2 product = new Product2(Name = name, IsActive = true);
            insert product;
            PricebookEntry pbe = new PricebookEntry(
                Pricebook2Id = Test.getStandardPricebookId(),
                Product2Id = product.Id,
                UnitPrice = 100,
                IsActive = true
            );
            insert pbe;
            lines.add(new QuoteLineItem(
                QuoteId = q.Id,
                PricebookEntryId = pbe.Id,
                Quantity = 1,
                UnitPrice = 100
            ));
        }
        insert lines;
        for (QuoteLineItem qli : lines) {
            f.lineIds.add(qli.Id);
        }
        return f;
    }
}
