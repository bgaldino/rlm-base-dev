@IsTest
private class RLM_QuoteModelUtilityTest {

    private static final Date START_DATE = Date.newInstance(2026, 3, 5);
    private static final Date END_DATE = Date.newInstance(2027, 3, 4);

    private class QuoteFixture {
        Quote quote;
        List<PricebookEntry> entries = new List<PricebookEntry>();
        List<QuoteLineItem> lines = new List<QuoteLineItem>();
        ProductSellingModel sellingModel;
    }

    /**
     * A draft quote with one line per product. With a selling model, every product is priced
     * under a monthly term-defined model whose option carries a proration policy. That policy is
     * not copied onto a line inserted by DML (the tests assert so), so it never reaches the context.
     */
    private static QuoteFixture buildQuote(Integer lineCount, Boolean withSellingModel, Boolean firstIsBundle) {
        Account acct = new Account(Name = 'RLM QMU Account');
        insert acct;
        Opportunity opp = new Opportunity(
            Name = 'RLM QMU Opportunity',
            AccountId = acct.Id,
            StageName = 'Prospecting',
            CloseDate = Date.today().addDays(30)
        );
        insert opp;

        List<Product2> products = new List<Product2>();
        for (Integer i = 0; i < lineCount; i++) {
            products.add(new Product2(Name = 'RLM QMU Product ' + i, IsActive = true));
        }
        if (firstIsBundle) {
            products[0].Type = 'Bundle';
        }
        insert products;

        QuoteFixture f = new QuoteFixture();
        if (withSellingModel) {
            ProrationPolicy policy = new ProrationPolicy(
                Name = 'RLM QMU Proration',
                ProrationPolicyType = 'StandardTimePeriods',
                RemainderStrategy = 'AddToLast',
                ArePartialPeriodsAllowed = true
            );
            insert policy;
            f.sellingModel = new ProductSellingModel(
                Name = 'RLM QMU Term Monthly',
                SellingModelType = 'TermDefined',
                PricingTermUnit = 'Months',
                PricingTerm = 1,
                Status = 'Active'
            );
            insert f.sellingModel;
            List<ProductSellingModelOption> options = new List<ProductSellingModelOption>();
            for (Product2 p : products) {
                options.add(new ProductSellingModelOption(
                    Product2Id = p.Id,
                    ProductSellingModelId = f.sellingModel.Id,
                    ProrationPolicyId = policy.Id,
                    IsDefault = true
                ));
            }
            insert options;
        }

        Id pbId = Test.getStandardPricebookId();
        for (Product2 p : products) {
            f.entries.add(new PricebookEntry(
                Pricebook2Id = pbId,
                Product2Id = p.Id,
                ProductSellingModelId = withSellingModel ? f.sellingModel.Id : null,
                UnitPrice = 100,
                IsActive = true
            ));
        }
        insert f.entries;

        f.quote = new Quote(Name = 'RLM QMU Quote', OpportunityId = opp.Id, Pricebook2Id = pbId, Status = 'Draft');
        insert f.quote;
        for (PricebookEntry pbe : f.entries) {
            f.lines.add(new QuoteLineItem(
                QuoteId = f.quote.Id,
                PricebookEntryId = pbe.Id,
                Quantity = 2,
                UnitPrice = 100,
                StartDate = START_DATE,
                EndDate = END_DATE,
                SubscriptionTerm = 12,
                Discount = 10,
                // Term-defined and evergreen lines must say how often they bill.
                BillingFrequency = withSellingModel ? 'Monthly' : null
            ));
        }
        insert f.lines;
        return f;
    }

    private static String contextFor(Id quoteId) {
        List<String> result = RLM_QuoteModelUtility.CreateQuoteContextString(new List<Id>{ quoteId });
        Assert.areEqual(1, result.size(), 'One context string per call');
        return result[0];
    }

    private static RLM_QuoteModelUtility.SalesTransactionModel parse(String context) {
        RLM_QuoteModelUtility.SalesContextModel ctx = (RLM_QuoteModelUtility.SalesContextModel) JSON.deserialize(
            context, RLM_QuoteModelUtility.SalesContextModel.class
        );
        return ctx.SalesTransaction;
    }

    private static RLM_QuoteModelUtility.SalesTransactionItemModel itemFor(
        RLM_QuoteModelUtility.SalesTransactionModel txn, Id lineId
    ) {
        for (RLM_QuoteModelUtility.SalesTransactionItemModel item : txn.SalesTransactionItem) {
            if (item.LineItem == String.valueOf(lineId)) {
                return item;
            }
        }
        Assert.fail('No transaction item for quote line ' + lineId);
        return null;
    }

    @IsTest
    static void quoteHeaderAndLinesAreMapped() {
        QuoteFixture f = buildQuote(2, false, false);
        Quote q = RLM_QuoteModelUtility.getQuote(new List<Id>{ f.quote.Id });
        List<QuoteLineItem> stored = [
            SELECT Id, Product2Id, Quantity, Discount, ListPrice, ProrationPolicyId
            FROM QuoteLineItem WHERE QuoteId = :f.quote.Id
        ];
        for (QuoteLineItem line : stored) {
            Assert.areEqual(2, line.Quantity.intValue(), 'PRECONDITION: seeded quantity is stored');
            Assert.areEqual(10, line.Discount.intValue(), 'PRECONDITION: seeded discount is stored');
            // ProrationPolicyId cannot be set by DML and the platform does not derive it here.
            Assert.isNull(line.ProrationPolicyId, 'PRECONDITION: a plain line has no proration policy');
        }

        Test.startTest();
        String context = contextFor(f.quote.Id);
        Test.stopTest();

        Assert.isFalse(context.contains('null'), 'Every null is blanked for the context service');
        RLM_QuoteModelUtility.SalesTransactionModel txn = parse(context);
        Assert.areEqual(String.valueOf(f.quote.Id), txn.SalesTransactionSource, 'The quote is the transaction source');
        Assert.areEqual(String.valueOf(Test.getStandardPricebookId()), txn.PriceBooks, 'The quote price book is carried');
        Assert.areEqual(q.CurrencyIsoCode, txn.CurrencyIsoCode, 'The quote currency is carried');
        Assert.areEqual(
            q.CreatedDate.format('yyyy-MM-dd\'T\'HH:mm:ss.SSS\'Z\''), txn.EffectiveDate,
'Known gap: local time is labelled UTC (Z); update this test when it is fixed (quote creation time as the effective date)'
        );
        Assert.areEqual(stored.size(), txn.SalesTransactionItem.size(), 'Every quote line becomes one transaction item');

        for (QuoteLineItem line : stored) {
            RLM_QuoteModelUtility.SalesTransactionItemModel item = itemFor(txn, line.Id);
            Assert.areEqual(String.valueOf(f.quote.Id), item.SalesTransactionItemParent, 'Items point at their quote');
            Assert.areEqual(String.valueOf(line.Product2Id), item.Product, 'The product is carried');
            Assert.areEqual(String.valueOf(line.Quantity), item.LineItemQuantity, 'The line quantity is carried');
            Assert.areEqual(String.valueOf(line.Discount), item.ItemDiscountPercentage, 'The line discount is carried');
            Assert.areEqual(String.valueOf(line.ListPrice), item.InputUnitPrice, 'The list price is the input price');
            Assert.areEqual('12', item.ItemSubscriptionTerm, 'The subscription term is carried');
            Assert.areEqual('PriceBook', item.ItemPricingSource, 'Items are priced from the price book');
            Assert.areEqual('2026-03-05T00:00:00.000Z', item.EffectiveFrom, 'Known gap: local time is labelled UTC (Z); update this test when it is fixed (start date at the start of the day)');
            Assert.areEqual('2027-03-04T23:59:59.000Z', item.EffectiveTo, 'Known gap: local time is labelled UTC (Z); update this test when it is fixed (end date at the end of the day)');
            Assert.areEqual('5', item.StartProrationPeriodDay, 'The proration day is the start day');
            Assert.areEqual('false', item.AllowPartialProrationPeriods, 'With no proration policy, partial periods are not allowed');
            Assert.isTrue(item.SalesTransactionItemAttribute.isEmpty(), 'No attributes on a plain line');
            Assert.isTrue(item.SalesTrxnItemRelationship.isEmpty(), 'No relationships on a standalone line');
        }
    }

    @IsTest
    static void sellingModelIsCarriedOnTheItem() {
        QuoteFixture f = buildQuote(1, true, false);
        QuoteLineItem stored = [SELECT ProductSellingModelId, ProrationPolicyId FROM QuoteLineItem WHERE Id = :f.lines[0].Id];
        Assert.areEqual(f.sellingModel.Id, stored.ProductSellingModelId, 'PRECONDITION: the line takes its selling model from the price book entry');
        // The selling model option's proration policy is not copied onto a line inserted by DML.
        Assert.isNull(stored.ProrationPolicyId, 'PRECONDITION: the line has no proration policy');

        Test.startTest();
        RLM_QuoteModelUtility.SalesTransactionItemModel item = itemFor(parse(contextFor(f.quote.Id)), f.lines[0].Id);
        Test.stopTest();

        Assert.areEqual(String.valueOf(f.sellingModel.Id), item.ProductSellingModel, 'The line selling model is carried');
        Assert.areEqual('TermDefined', item.SellingModelType, 'The selling model type is carried');
        Assert.areEqual('Months', item.PricingTermUnit, 'The pricing term unit is carried');
        Assert.areEqual('false', item.AllowPartialProrationPeriods, 'With no proration policy, partial periods are not allowed');
    }

    @IsTest
    static void bundleRelationshipsMapInclusivePrice() {
        QuoteFixture f = buildQuote(3, false, true);
        QuoteLineItem parent = f.lines[0];
        QuoteLineItem excluded = f.lines[1];
        QuoteLineItem included = f.lines[2];
        Id parentProductId = f.entries[0].Product2Id;

        ProductRelationshipType relType = new ProductRelationshipType(
            Name = 'RLM QMU Bundle Component',
            MainProductRoleCat = 'Bundle',
            AssociatedProductRoleCat = 'BundleComponent'
        );
        insert relType;
        // A static bundle's components must be added by default.
        ProductRelatedComponent excludedComponent = new ProductRelatedComponent(
            ParentProductId = parentProductId, ChildProductId = f.entries[1].Product2Id,
            ProductRelationshipTypeId = relType.Id, Quantity = 1, IsDefaultComponent = true
        );
        ProductRelatedComponent includedComponent = new ProductRelatedComponent(
            ParentProductId = parentProductId, ChildProductId = f.entries[2].Product2Id,
            ProductRelationshipTypeId = relType.Id, Quantity = 1, IsDefaultComponent = true
        );
        insert new List<ProductRelatedComponent>{ excludedComponent, includedComponent };
        insert new List<QuoteLineRelationship>{
            new QuoteLineRelationship(
                MainQuoteLineId = parent.Id, AssociatedQuoteLineId = excluded.Id,
                AssociatedQuoteLinePricing = 'NotIncludedInBundlePrice', AssociatedQuantScaleMethod = 'Proportional',
                ProductRelationshipTypeId = relType.Id, ProductRelatedComponentId = excludedComponent.Id
            ),
            new QuoteLineRelationship(
                MainQuoteLineId = parent.Id, AssociatedQuoteLineId = included.Id,
                AssociatedQuoteLinePricing = 'IncludedInBundlePrice', AssociatedQuantScaleMethod = 'Proportional',
                ProductRelationshipTypeId = relType.Id, ProductRelatedComponentId = includedComponent.Id
            )
        };

        Test.startTest();
        RLM_QuoteModelUtility.SalesTransactionModel txn = parse(contextFor(f.quote.Id));
        Test.stopTest();

        Assert.isTrue(itemFor(txn, parent.Id).SalesTrxnItemRelationship.isEmpty(), 'The bundle parent has no relationship of its own');
        Map<Id, String> expectedInclusive = new Map<Id, String>{ excluded.Id => 'FALSE', included.Id => 'TRUE' };
        for (Id childLineId : expectedInclusive.keySet()) {
            List<RLM_QuoteModelUtility.SalesTransactionItemRelationshipModel> rels =
                itemFor(txn, childLineId).SalesTrxnItemRelationship;
            Assert.areEqual(1, rels.size(), 'Each child line carries its one relationship');
            RLM_QuoteModelUtility.SalesTransactionItemRelationshipModel rel = rels[0];
            Assert.areEqual(expectedInclusive.get(childLineId), rel.InclusivePrice, 'Bundle pricing maps to InclusivePrice for ' + childLineId);
            Assert.areEqual(String.valueOf(childLineId), rel.SalesTrnItemRelationshipParent, 'The relationship hangs off the child line');
            Assert.areEqual(String.valueOf(parentProductId), rel.MainItemProduct, 'The bundle parent product is the main item');
            Assert.areEqual(String.valueOf(parentProductId), rel.RootItemProduct, 'The bundle parent product is the root item');
        }
    }

    // Attribute mapping is not covered: QuoteLineItemAttribute rejects plain DML, and a row saved
    // with Database.insertImmediate is not returned by SOQL in the same test transaction.

    @IsTest
    static void largeQuoteUsesConstantQueries() {
        QuoteFixture f = buildQuote(150, false, false);

        Test.startTest();
        Integer queriesBefore = Limits.getQueries();
        String context = contextFor(f.quote.Id);
        Integer queriesUsed = Limits.getQueries() - queriesBefore;
        Test.stopTest();

        // Quote, lines, attributes, relationships: four queries regardless of line count, so a
        // large quote cannot hit the SOQL limit that per-line child queries used to.
        Assert.areEqual(4, queriesUsed, 'Child objects are queried once per quote, not per line');
        RLM_QuoteModelUtility.SalesTransactionModel txn = parse(context);
        Assert.areEqual(150, txn.SalesTransactionItem.size(), 'Every line of a large quote is mapped');
        for (QuoteLineItem line : f.lines) {
            itemFor(txn, line.Id);
        }
    }

    @IsTest
    static void getQuoteFailsForAnUnknownQuote() {
        Id missingQuoteId = Quote.SObjectType.getDescribe().getKeyPrefix() + '000000000001';

        try {
            RLM_QuoteModelUtility.getQuote(new List<Id>{ missingQuoteId });
            Assert.fail('getQuote must not return a quote for an unknown id');
        } catch (ListException e) {
            Assert.isTrue(
                e.getMessage().contains('out of bounds'),
                'Known gap: getQuote throws a raw ListException for an unknown id; update this test when it is fixed. '
                    + e.getMessage()
            );
        }
    }

    @IsTest
    static void onlyOneQuoteIsConvertedPerCall() {
        QuoteFixture first = buildQuote(1, false, false);
        QuoteFixture second = buildQuote(1, false, false);
        Set<String> quoteIds = new Set<String>{ String.valueOf(first.quote.Id), String.valueOf(second.quote.Id) };

        List<String> result = RLM_QuoteModelUtility.CreateQuoteContextString(new List<Id>{ first.quote.Id, second.quote.Id });

        Assert.areEqual(
            1, result.size(),
            'Known gap: getQuote reads LIMIT 1, so only one of several quote ids is converted; update this test when it is fixed'
        );
        Assert.isTrue(quoteIds.contains(parse(result[0]).SalesTransactionSource), 'The context is for one of the requested quotes');
    }

    @IsTest
    static void getQuoteLinesReturnsOnlyThatQuotesLines() {
        QuoteFixture f = buildQuote(2, false, false);
        QuoteFixture other = buildQuote(3, false, false);

        List<QuoteLineItem> lines = RLM_QuoteModelUtility.getQuoteLines(f.quote.Id);

        Assert.areEqual(2, lines.size(), 'Both lines of the quote are returned');
        Set<Id> otherIds = new Map<Id, QuoteLineItem>(other.lines).keySet();
        for (QuoteLineItem line : lines) {
            Assert.areEqual(f.quote.Id, line.QuoteId, 'Only lines of the requested quote');
            Assert.isFalse(otherIds.contains(line.Id), 'Lines of another quote are excluded');
            Assert.areEqual(START_DATE, line.StartDate, 'Line dates are queried');
        }
    }

    @IsTest
    static void dateConversionsSpanTheWholeDay() {
        Date d = Date.newInstance(2026, 11, 9);

        Assert.areEqual('2026-11-09T00:00:00.000Z', RLM_QuoteModelUtility.convertStartDate(d), 'Known gap: local time is labelled UTC (Z); update this test when it is fixed (start of day)');
        Assert.areEqual('2026-11-09T23:59:59.000Z', RLM_QuoteModelUtility.convertEndDate(d), 'Known gap: local time is labelled UTC (Z); update this test when it is fixed (end of day)');
    }
}
