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
     * under a monthly term-defined model whose option carries a proration policy.
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

    private static void assertContains(String json, String fragment, String message) {
        Assert.isTrue(json.contains(fragment), message + ' — expected ' + fragment);
    }

    /** Sets a field only if this org's schema has it and lets it be set on create. */
    private static void putIfField(SObject record, String fieldName, Object value) {
        Schema.SObjectField field = record.getSObjectType().getDescribe().fields.getMap().get(fieldName);
        if (field != null && field.getDescribe().isCreateable()) {
            record.put(fieldName, value);
        }
    }

    @IsTest
    static void quoteHeaderAndLinesAreMapped() {
        QuoteFixture f = buildQuote(2, false, false);
        Quote q = RLM_QuoteModelUtility.getQuote(new List<Id>{ f.quote.Id });

        Test.startTest();
        String json = contextFor(f.quote.Id);
        Test.stopTest();

        assertContains(json, '"SalesTransactionSource":"' + f.quote.Id + '"', 'The quote is the transaction source');
        assertContains(json, '"PriceBooks":"' + Test.getStandardPricebookId() + '"', 'The quote price book is carried');
        assertContains(json, '"CurrencyIsoCode":"' + q.CurrencyIsoCode + '"', 'The quote currency is carried');
        assertContains(
            json,
            '"EffectiveDate":"' + q.CreatedDate.format('yyyy-MM-dd\'T\'HH:mm:ss.SSS\'Z\'') + '"',
            'The quote creation time is the effective date'
        );
        for (QuoteLineItem line : f.lines) {
            assertContains(json, '"LineItem":"' + line.Id + '"', 'Every quote line becomes a transaction item');
        }
        // Seeded quantity, discount and list price, compared as the platform stored them.
        for (QuoteLineItem line : RLM_QuoteModelUtility.getQuoteLines(f.quote.Id)) {
            Assert.areEqual(2, line.Quantity.intValue(), 'PRECONDITION: seeded quantity is stored');
            Assert.areEqual(10, line.Discount.intValue(), 'PRECONDITION: seeded discount is stored');
            assertContains(json, '"LineItemQuantity":"' + String.valueOf(line.Quantity) + '"', 'The line quantity is carried');
            assertContains(json, '"ItemDiscountPercentage":"' + String.valueOf(line.Discount) + '"', 'The line discount is carried');
            assertContains(json, '"InputUnitPrice":"' + String.valueOf(line.ListPrice) + '"', 'The list price is the input price');
        }
        assertContains(json, '"SalesTransactionItemParent":"' + f.quote.Id + '"', 'Items point at their quote');
        assertContains(json, '"ItemPricingSource":"PriceBook"', 'Items are priced from the price book');
        assertContains(json, '"ItemSubscriptionTerm":"12"', 'The subscription term is carried');
        assertContains(json, '"Product":"' + f.entries[0].Product2Id + '"', 'The product is carried');
        assertContains(json, '"EffectiveFrom":"2026-03-05T00:00:00.000Z"', 'Start date is the start of the day');
        assertContains(json, '"EffectiveTo":"2027-03-04T23:59:59.000Z"', 'End date is the end of the day');
        assertContains(json, '"StartProrationPeriodDay":"5"', 'The proration day is the start day');
        assertContains(json, '"SalesTransactionItemAttribute":[]', 'No attributes on a plain line');
        assertContains(json, '"SalesTrxnItemRelationship":[]', 'No relationships on a standalone line');
        Assert.isFalse(json.contains('null'), 'Every null is blanked for the context service');
    }

    @IsTest
    static void sellingModelIsCarriedOnTheItem() {
        QuoteFixture f = buildQuote(1, true, false);

        Test.startTest();
        String json = contextFor(f.quote.Id);
        Test.stopTest();

        assertContains(json, '"ProductSellingModel":"' + f.sellingModel.Id + '"', 'The line selling model is carried');
        assertContains(json, '"SellingModelType":"TermDefined"', 'The selling model type is carried');
        assertContains(json, '"PricingTermUnit":"Months"', 'The pricing term unit is carried');
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
        List<ProductRelatedComponent> components = new List<ProductRelatedComponent>{
            new ProductRelatedComponent(
                ParentProductId = parentProductId, ChildProductId = f.entries[1].Product2Id,
                ProductRelationshipTypeId = relType.Id, Quantity = 1, IsDefaultComponent = true
            ),
            new ProductRelatedComponent(
                ParentProductId = parentProductId, ChildProductId = f.entries[2].Product2Id,
                ProductRelationshipTypeId = relType.Id, Quantity = 1, IsDefaultComponent = true
            )
        };
        insert components;

        List<QuoteLineRelationship> rels = new List<QuoteLineRelationship>();
        Map<Id, String> pricingByChild = new Map<Id, String>{
            excluded.Id => 'NotIncludedInBundlePrice',
            included.Id => 'IncludedInBundlePrice'
        };
        Integer i = 0;
        for (Id childLineId : new List<Id>{ excluded.Id, included.Id }) {
            QuoteLineRelationship rel = new QuoteLineRelationship();
            rel.put('MainQuoteLineId', parent.Id);
            rel.put('AssociatedQuoteLineId', childLineId);
            rel.put('AssociatedQuoteLinePricing', pricingByChild.get(childLineId));
            putIfField(rel, 'ProductRelationshipTypeId', relType.Id);
            putIfField(rel, 'ProductRelatedComponentId', components[i].Id);
            putIfField(rel, 'AssociatedQuoteLineRole', 'BundleComponent');
            putIfField(rel, 'AssociatedQuantScaleMethod', 'Proportional');
            rels.add(rel);
            i++;
        }
        insert rels;

        Test.startTest();
        String json = contextFor(f.quote.Id);
        Test.stopTest();

        assertContains(json, '"InclusivePrice":"FALSE"', 'A child priced outside the bundle is not inclusive');
        assertContains(json, '"InclusivePrice":"TRUE"', 'A child priced inside the bundle is inclusive');
        assertContains(json, '"SalesTrnItemRelationshipParent":"' + excluded.Id + '"', 'Relationships hang off the child line');
        assertContains(json, '"SalesTrnItemRelationshipParent":"' + included.Id + '"', 'Relationships hang off the child line');
        assertContains(json, '"MainItemProduct":"' + parentProductId + '"', 'The bundle parent product is the main item');
        assertContains(json, '"RootItemProduct":"' + parentProductId + '"', 'The bundle parent product is the root item');
    }

    // Attribute mapping is not covered: QuoteLineItemAttribute rejects plain DML, and a row saved
    // with Database.insertImmediate is not returned by SOQL in the same test transaction.

    @IsTest
    static void largeQuoteUsesConstantQueries() {
        QuoteFixture f = buildQuote(150, false, false);

        Test.startTest();
        Integer queriesBefore = Limits.getQueries();
        String json = contextFor(f.quote.Id);
        Integer queriesUsed = Limits.getQueries() - queriesBefore;
        Test.stopTest();

        // Quote, lines, attributes, relationships: four queries regardless of line count, so a
        // large quote cannot hit the SOQL limit that per-line child queries used to.
        Assert.areEqual(4, queriesUsed, 'Child objects are queried once per quote, not per line');
        for (QuoteLineItem line : f.lines) {
            assertContains(json, '"LineItem":"' + line.Id + '"', 'Every line of a large quote is mapped');
        }
    }

    @IsTest
    static void unknownQuoteThrows() {
        Id missingQuoteId = Quote.SObjectType.getDescribe().getKeyPrefix() + '000000000001';

        try {
            RLM_QuoteModelUtility.getQuote(new List<Id>{ missingQuoteId });
            Assert.fail('An unknown quote id must not produce a context');
        } catch (ListException e) {
            Assert.isNotNull(e.getMessage(), 'The missing quote is reported');
        }
    }

    @IsTest
    static void getQuoteLinesReturnsOnlyThatQuotesLines() {
        QuoteFixture f = buildQuote(2, false, false);

        List<QuoteLineItem> lines = RLM_QuoteModelUtility.getQuoteLines(f.quote.Id);

        Assert.areEqual(2, lines.size(), 'Both lines of the quote are returned');
        for (QuoteLineItem line : lines) {
            Assert.areEqual(f.quote.Id, line.QuoteId, 'Only lines of the requested quote');
            Assert.areEqual(START_DATE, line.StartDate, 'Line dates are queried');
        }
    }

    @IsTest
    static void dateConversionsSpanTheWholeDay() {
        Date d = Date.newInstance(2026, 11, 9);

        Assert.areEqual('2026-11-09T00:00:00.000Z', RLM_QuoteModelUtility.convertStartDate(d), 'Start of day');
        Assert.areEqual('2026-11-09T23:59:59.000Z', RLM_QuoteModelUtility.convertEndDate(d), 'End of day');
    }
}
