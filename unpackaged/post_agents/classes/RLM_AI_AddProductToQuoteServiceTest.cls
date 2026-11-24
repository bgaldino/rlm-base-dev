@isTest
private class RLM_AI_AddProductToQuoteServiceTest {

    // ---- Fake invoker: records the inputs and returns a canned result ----
    private class FakeInvoker implements RLM_AI_AddProductToQuoteService.ManagedAddLineInvoker {
        public Boolean returnSuccess;
        public String returnError;
        public Id lastQuoteId;
        public Id lastProductId;
        public Id lastSellingModelId;
        public Decimal lastQuantity;
        public Integer callCount = 0;

        FakeInvoker(Boolean returnSuccess, String returnError) {
            this.returnSuccess = returnSuccess;
            this.returnError = returnError;
        }

        public RLM_AI_AddProductToQuoteService.ManagedResult addLine(
            Id quoteId, Id productId, Id sellingModelId,
            Decimal quantity, Date startDate, Date endDate
        ) {
            this.callCount++;
            this.lastQuoteId = quoteId;
            this.lastProductId = productId;
            this.lastSellingModelId = sellingModelId;
            this.lastQuantity = quantity;
            return new RLM_AI_AddProductToQuoteService.ManagedResult(returnSuccess, returnError);
        }
    }

    @isTest
    static void addsProductByNameWithDefaultSellingModel() {
        Fixture f = buildFixture('Quinn Generator', true, false);
        FakeInvoker fake = new FakeInvoker(true, null);
        RLM_AI_AddProductToQuoteService.invoker = fake;

        RLM_AI_AddProductToQuoteService.AddInput input =
            new RLM_AI_AddProductToQuoteService.AddInput();
        input.quoteId = String.valueOf(f.quoteId);
        input.productName = 'Quinn Generator';
        input.quantity = 3;

        Test.startTest();
        List<RLM_AI_AddProductToQuoteService.AddOutput> results =
            RLM_AI_AddProductToQuoteService.addProduct(
                new List<RLM_AI_AddProductToQuoteService.AddInput>{ input });
        Test.stopTest();

        RLM_AI_AddProductToQuoteService.AddOutput out = results[0];
        System.assertEquals(true, out.isSuccess, 'error: ' + out.errorMessage);
        System.assertEquals('Quinn Generator', out.productNameAdded);
        System.assertEquals(3, out.quantityAdded);
        System.assertEquals(1, fake.callCount, 'Managed add-line should be called once.');
        System.assertEquals(f.productId, fake.lastProductId);
        System.assertEquals(f.sellingModelId, fake.lastSellingModelId,
            'The default selling model should be passed to the managed action.');
        System.assertEquals(3, fake.lastQuantity);
        System.assert(out.lineSummaryDisplay.contains('Quinn Generator'),
            'Confirmation should name the product.');
        // Names-only: the summary must not leak the raw product Id.
        System.assert(!out.lineSummaryDisplay.contains(String.valueOf(f.productId)));
    }

    @isTest
    static void addsProductByIdDefaultsQuantityToOne() {
        Fixture f = buildFixture('Quinn Widget', true, false);
        FakeInvoker fake = new FakeInvoker(true, null);
        RLM_AI_AddProductToQuoteService.invoker = fake;

        RLM_AI_AddProductToQuoteService.AddInput input =
            new RLM_AI_AddProductToQuoteService.AddInput();
        input.quoteId = String.valueOf(f.quoteId);
        input.productId = String.valueOf(f.productId);
        // No quantity supplied.

        List<RLM_AI_AddProductToQuoteService.AddOutput> results =
            RLM_AI_AddProductToQuoteService.addProduct(
                new List<RLM_AI_AddProductToQuoteService.AddInput>{ input });

        System.assertEquals(true, results[0].isSuccess, 'error: ' + results[0].errorMessage);
        System.assertEquals(1, results[0].quantityAdded, 'Quantity should default to 1.');
        System.assertEquals(1, fake.lastQuantity);
    }

    @isTest
    static void disambiguatesMultipleNameMatches() {
        // Two products contain the term, neither equals it exactly -> ambiguous.
        Fixture f = buildFixture('Quinn Server Rack Standard', true, false);
        insertProduct('Quinn Server Rack XL', true, true);
        FakeInvoker fake = new FakeInvoker(true, null);
        RLM_AI_AddProductToQuoteService.invoker = fake;

        RLM_AI_AddProductToQuoteService.AddInput input =
            new RLM_AI_AddProductToQuoteService.AddInput();
        input.quoteId = String.valueOf(f.quoteId);
        input.productName = 'Quinn Server Rack';

        List<RLM_AI_AddProductToQuoteService.AddOutput> results =
            RLM_AI_AddProductToQuoteService.addProduct(
                new List<RLM_AI_AddProductToQuoteService.AddInput>{ input });

        RLM_AI_AddProductToQuoteService.AddOutput out = results[0];
        System.assertEquals(false, out.isSuccess);
        System.assertEquals(true, out.needsDisambiguation);
        System.assertEquals(2, out.candidateProducts.size());
        System.assertEquals(0, fake.callCount, 'No mutation on disambiguation.');
        System.assert(out.candidateSummariesDisplay.contains('Quinn Server Rack'));
    }

    @isTest
    static void exactNameMatchWinsOverPartialSibling() {
        // "Quinn Cable" exact + "Quinn Cable Premium" partial → exact should win.
        Fixture f = buildFixture('Quinn Cable', true, false);
        insertProduct('Quinn Cable Premium', true, true);
        FakeInvoker fake = new FakeInvoker(true, null);
        RLM_AI_AddProductToQuoteService.invoker = fake;

        RLM_AI_AddProductToQuoteService.AddInput input =
            new RLM_AI_AddProductToQuoteService.AddInput();
        input.quoteId = String.valueOf(f.quoteId);
        input.productName = 'Quinn Cable';

        List<RLM_AI_AddProductToQuoteService.AddOutput> results =
            RLM_AI_AddProductToQuoteService.addProduct(
                new List<RLM_AI_AddProductToQuoteService.AddInput>{ input });

        System.assertEquals(true, results[0].isSuccess, 'error: ' + results[0].errorMessage);
        System.assertEquals('Quinn Cable', results[0].productNameAdded);
    }

    @isTest
    static void cleanMessageWhenNoSellingModel() {
        Fixture f = buildFixture('Quinn No PSM Product', false, false);
        FakeInvoker fake = new FakeInvoker(true, null);
        RLM_AI_AddProductToQuoteService.invoker = fake;

        RLM_AI_AddProductToQuoteService.AddInput input =
            new RLM_AI_AddProductToQuoteService.AddInput();
        input.quoteId = String.valueOf(f.quoteId);
        input.productName = 'Quinn No PSM Product';

        List<RLM_AI_AddProductToQuoteService.AddOutput> results =
            RLM_AI_AddProductToQuoteService.addProduct(
                new List<RLM_AI_AddProductToQuoteService.AddInput>{ input });

        System.assertEquals(false, results[0].isSuccess);
        System.assertEquals(false, results[0].needsDisambiguation);
        System.assert(results[0].errorMessage.contains('selling model'),
            'Should explain the missing selling model in plain language.');
        System.assertEquals(0, fake.callCount, 'No mutation when prerequisite missing.');
    }

    @isTest
    static void surfacesManagedFailure() {
        Fixture f = buildFixture('Quinn Failing Product', true, false);
        FakeInvoker fake = new FakeInvoker(false, 'Managed add-line said no.');
        RLM_AI_AddProductToQuoteService.invoker = fake;

        RLM_AI_AddProductToQuoteService.AddInput input =
            new RLM_AI_AddProductToQuoteService.AddInput();
        input.quoteId = String.valueOf(f.quoteId);
        input.productName = 'Quinn Failing Product';

        List<RLM_AI_AddProductToQuoteService.AddOutput> results =
            RLM_AI_AddProductToQuoteService.addProduct(
                new List<RLM_AI_AddProductToQuoteService.AddInput>{ input });

        System.assertEquals(false, results[0].isSuccess);
        System.assertEquals('Managed add-line said no.', results[0].errorMessage);
    }

    // The add-line action passes a validation rule's or trigger's own message back for the user;
    // that text is shown as is. Measured shapes (a 264 org) are used verbatim below.
    @isTest
    static void refusalTextIsPassedThroughOnlyWhenItIsWrittenForTheUser() {
        System.assertEquals('Quantity must be at least 5 for this product.',
            RLM_AI_AddProductToQuoteService.userSafeRefusal('Quantity must be at least 5 for this product.'),
            'A validation rule message is shown as written.');
        String triggerFault = 'SomeTrigger: execution of BeforeInsert\n\ncaused by: '
            + 'System.ListException: List index out of bounds: 3\n\nTrigger.SomeTrigger: line 3, column 1';
        System.assertEquals(RLM_AI_AddProductToQuoteService.ADD_REFUSED_MESSAGE,
            RLM_AI_AddProductToQuoteService.userSafeRefusal(triggerFault),
            'A trigger fault is replaced by the fixed sentence.');
        System.assertEquals(RLM_AI_AddProductToQuoteService.ADD_REFUSED_MESSAGE,
            RLM_AI_AddProductToQuoteService.userSafeRefusal('FIELD_INTEGRITY_EXCEPTION: bad value'),
            'A status-code style message is replaced by the fixed sentence.');
        for (String fault : new List<String>{
            'INSUFFICIENT_ACCESS_OR_READONLY, insufficient access rights on object id',
            'Insert failed. First exception on row 0; first error: DUPLICATE_VALUE, duplicate value found',
            'Apex CPU time limit exceeded',
            'System.NullPointerException: Attempt to de-reference a null object'
        }) {
            System.assertEquals(RLM_AI_AddProductToQuoteService.ADD_REFUSED_MESSAGE,
                RLM_AI_AddProductToQuoteService.userSafeRefusal(fault), 'Hidden: ' + fault);
        }
        System.assertEquals('Add this product only to quotes in USD.',
            RLM_AI_AddProductToQuoteService.userSafeRefusal('Add this product only to quotes in USD.'),
            'An acronym in a validation message is not a status code.');
        System.assertEquals(RLM_AI_AddProductToQuoteService.ADD_REFUSED_MESSAGE,
            RLM_AI_AddProductToQuoteService.userSafeRefusal('  '),
            'A blank message gets the fixed sentence.');
    }

    @isTest
    static void hidesAManagedFaultFromTheUser() {
        Fixture f = buildFixture('Quinn Faulting Product', true, false);
        RLM_AI_AddProductToQuoteService.invoker = new FakeInvoker(false,
            'SomeTrigger: execution of BeforeInsert\n\ncaused by: System.NullPointerException: '
            + 'Attempt to de-reference a null object\n\nTrigger.SomeTrigger: line 7, column 1');

        RLM_AI_AddProductToQuoteService.AddInput input =
            new RLM_AI_AddProductToQuoteService.AddInput();
        input.quoteId = String.valueOf(f.quoteId);
        input.productName = 'Quinn Faulting Product';

        List<RLM_AI_AddProductToQuoteService.AddOutput> results =
            RLM_AI_AddProductToQuoteService.addProduct(
                new List<RLM_AI_AddProductToQuoteService.AddInput>{ input });

        System.assertEquals(false, results[0].isSuccess);
        System.assertEquals(RLM_AI_AddProductToQuoteService.ADD_REFUSED_MESSAGE, results[0].errorMessage);
    }

    // Once the add-line action reports success the line exists, so a failure finding it afterwards
    // must not report the add as failed (a retry would add it twice): success, with no line id.
    @isTest
    static void aFailedLineLookupAfterTheAddStaysASuccess() {
        Fixture f = buildFixture('Quinn Lookup Product', true, false);
        FakeInvoker fake = new FakeInvoker(true, null);
        RLM_AI_AddProductToQuoteService.invoker = fake;
        RLM_AI_AddProductToQuoteService.lineLookupFailure = new QueryException('lookup refused');

        RLM_AI_AddProductToQuoteService.AddInput input =
            new RLM_AI_AddProductToQuoteService.AddInput();
        input.quoteId = String.valueOf(f.quoteId);
        input.productName = 'Quinn Lookup Product';

        List<RLM_AI_AddProductToQuoteService.AddOutput> results =
            RLM_AI_AddProductToQuoteService.addProduct(
                new List<RLM_AI_AddProductToQuoteService.AddInput>{ input });

        System.assertEquals(true, results[0].isSuccess, 'error: ' + results[0].errorMessage);
        System.assertEquals(1, fake.callCount);
        System.assertEquals(null, results[0].quoteLineItemId, 'The id is left blank, not guessed.');
        System.assertEquals(null, results[0].errorMessage);
        System.assert(results[0].lineSummaryDisplay.contains('Quinn Lookup Product'));
    }

    // The add-line action did not run at all: the unexpected-error sentence, not the refusal one.
    @isTest
    static void anActionThatDidNotRunShowsTheUnexpectedErrorSentence() {
        Fixture f = buildFixture('Quinn Unrun Product', true, false);
        RLM_AI_AddProductToQuoteService.invoker = new NotRunInvoker();

        RLM_AI_AddProductToQuoteService.AddInput input =
            new RLM_AI_AddProductToQuoteService.AddInput();
        input.quoteId = String.valueOf(f.quoteId);
        input.productName = 'Quinn Unrun Product';

        List<RLM_AI_AddProductToQuoteService.AddOutput> results =
            RLM_AI_AddProductToQuoteService.addProduct(
                new List<RLM_AI_AddProductToQuoteService.AddInput>{ input });

        System.assertEquals(false, results[0].isSuccess);
        System.assertEquals(RLM_AI_AddProductToQuoteService.ADD_FAILED_MESSAGE, results[0].errorMessage);
    }

    private class NotRunInvoker implements RLM_AI_AddProductToQuoteService.ManagedAddLineInvoker {
        public RLM_AI_AddProductToQuoteService.ManagedResult addLine(
            Id quoteId, Id productId, Id sellingModelId,
            Decimal quantity, Date startDate, Date endDate
        ) {
            RLM_AI_AddProductToQuoteService.ManagedResult r =
                new RLM_AI_AddProductToQuoteService.ManagedResult(false, null);
            r.actionFailed = true;
            return r;
        }
    }

    private class ThrowingInvoker implements RLM_AI_AddProductToQuoteService.ManagedAddLineInvoker {
        public RLM_AI_AddProductToQuoteService.ManagedResult addLine(
            Id quoteId, Id productId, Id sellingModelId,
            Decimal quantity, Date startDate, Date endDate
        ) {
            throw new IllegalArgumentException('internal detail the user must not see');
        }
    }

    @isTest
    static void unexpectedFailureShowsAFixedSentence() {
        Fixture f = buildFixture('Quinn Throwing Product', true, false);
        RLM_AI_AddProductToQuoteService.invoker = new ThrowingInvoker();

        RLM_AI_AddProductToQuoteService.AddInput input =
            new RLM_AI_AddProductToQuoteService.AddInput();
        input.quoteId = String.valueOf(f.quoteId);
        input.productName = 'Quinn Throwing Product';

        List<RLM_AI_AddProductToQuoteService.AddOutput> results =
            RLM_AI_AddProductToQuoteService.addProduct(
                new List<RLM_AI_AddProductToQuoteService.AddInput>{ input });

        System.assertEquals(false, results[0].isSuccess);
        System.assertEquals(RLM_AI_AddProductToQuoteService.ADD_FAILED_MESSAGE, results[0].errorMessage);
    }

    @isTest
    static void rejectsBlankQuoteId() {
        RLM_AI_AddProductToQuoteService.AddInput input =
            new RLM_AI_AddProductToQuoteService.AddInput();
        input.quoteId = '   ';
        input.productName = 'Anything';

        List<RLM_AI_AddProductToQuoteService.AddOutput> results =
            RLM_AI_AddProductToQuoteService.addProduct(
                new List<RLM_AI_AddProductToQuoteService.AddInput>{ input });

        System.assertEquals(false, results[0].isSuccess);
        System.assert(results[0].errorMessage.contains('Quote Id is required'));
    }

    @isTest
    static void rejectsInvalidQuoteId() {
        RLM_AI_AddProductToQuoteService.AddInput input =
            new RLM_AI_AddProductToQuoteService.AddInput();
        input.quoteId = 'not-an-id';
        input.productName = 'Anything';

        List<RLM_AI_AddProductToQuoteService.AddOutput> results =
            RLM_AI_AddProductToQuoteService.addProduct(
                new List<RLM_AI_AddProductToQuoteService.AddInput>{ input });

        System.assertEquals(false, results[0].isSuccess);
        System.assert(results[0].errorMessage.contains('Invalid quote Id'));
    }

    @isTest
    static void requiresProductIdentifier() {
        Fixture f = buildFixture('Quinn Base Product', true, false);
        RLM_AI_AddProductToQuoteService.AddInput input =
            new RLM_AI_AddProductToQuoteService.AddInput();
        input.quoteId = String.valueOf(f.quoteId);
        // No productId, no productName.

        List<RLM_AI_AddProductToQuoteService.AddOutput> results =
            RLM_AI_AddProductToQuoteService.addProduct(
                new List<RLM_AI_AddProductToQuoteService.AddInput>{ input });

        System.assertEquals(false, results[0].isSuccess);
        System.assert(results[0].errorMessage.contains('product Id or product name'));
    }

    @isTest
    static void noProductNameMatchReturnsCleanMessage() {
        Fixture f = buildFixture('Quinn Real Product', true, false);
        RLM_AI_AddProductToQuoteService.AddInput input =
            new RLM_AI_AddProductToQuoteService.AddInput();
        input.quoteId = String.valueOf(f.quoteId);
        input.productName = 'Nonexistent Zzzzz Product';

        List<RLM_AI_AddProductToQuoteService.AddOutput> results =
            RLM_AI_AddProductToQuoteService.addProduct(
                new List<RLM_AI_AddProductToQuoteService.AddInput>{ input });

        System.assertEquals(false, results[0].isSuccess);
        System.assert(results[0].errorMessage.contains('No active product'));
    }

    @isTest
    static void honorsUserRequestedSellingModel() {
        // Product with two selling models: a default and a second the user names.
        Fixture f = buildFixture('Quinn Termed Product', true, true);
        ProductSellingModel termed = new ProductSellingModel(
            Name = 'Term Monthly',
            SellingModelType = 'TermDefined',
            PricingTermUnit = 'Months',
            PricingTerm = 1,
            Status = 'Active'
        );
        insert termed;
        insert new ProductSellingModelOption(
            Product2Id = f.productId,
            ProductSellingModelId = termed.Id,
            IsDefault = false
        );

        FakeInvoker fake = new FakeInvoker(true, null);
        RLM_AI_AddProductToQuoteService.invoker = fake;

        RLM_AI_AddProductToQuoteService.AddInput input =
            new RLM_AI_AddProductToQuoteService.AddInput();
        input.quoteId = String.valueOf(f.quoteId);
        input.productName = 'Quinn Termed Product';
        input.sellingModelName = 'term monthly';   // case-insensitive

        Test.startTest();
        List<RLM_AI_AddProductToQuoteService.AddOutput> results =
            RLM_AI_AddProductToQuoteService.addProduct(
                new List<RLM_AI_AddProductToQuoteService.AddInput>{ input });
        Test.stopTest();

        RLM_AI_AddProductToQuoteService.AddOutput out = results[0];
        System.assertEquals(true, out.isSuccess, 'error: ' + out.errorMessage);
        System.assertEquals('Term Monthly', out.sellingModelName,
            'The user-named selling model should be used, not the default.');
        System.assertEquals(termed.Id, fake.lastSellingModelId,
            'The requested model Id should be passed to the managed action.');
    }

    @isTest
    static void rejectsUnknownRequestedSellingModel() {
        Fixture f = buildFixture('Quinn One Model Product', true, true);
        FakeInvoker fake = new FakeInvoker(true, null);
        RLM_AI_AddProductToQuoteService.invoker = fake;

        RLM_AI_AddProductToQuoteService.AddInput input =
            new RLM_AI_AddProductToQuoteService.AddInput();
        input.quoteId = String.valueOf(f.quoteId);
        input.productName = 'Quinn One Model Product';
        input.sellingModelName = 'Nonexistent Model';

        List<RLM_AI_AddProductToQuoteService.AddOutput> results =
            RLM_AI_AddProductToQuoteService.addProduct(
                new List<RLM_AI_AddProductToQuoteService.AddInput>{ input });

        RLM_AI_AddProductToQuoteService.AddOutput out = results[0];
        System.assertEquals(false, out.isSuccess);
        System.assert(out.errorMessage.contains('Nonexistent Model'),
            'Error should name the requested model: ' + out.errorMessage);
        System.assert(out.errorMessage.contains('Available'),
            'Error should list available models: ' + out.errorMessage);
        System.assertEquals(0, fake.callCount, 'No mutation when the named model is invalid.');
    }

    @isTest
    static void emptyInputListReturnsEmpty() {
        List<RLM_AI_AddProductToQuoteService.AddOutput> results =
            RLM_AI_AddProductToQuoteService.addProduct(null);
        System.assertEquals(0, results.size());
    }

    // ---- Fixture helpers ----

    private class Fixture {
        Id quoteId;
        Id productId;
        Id sellingModelId;
    }

    private static Fixture buildFixture(String productName, Boolean withSellingModel, Boolean isDefault) {
        Account acct = new Account(Name = 'Quinn Add Account');
        insert acct;
        Opportunity opp = new Opportunity(
            Name = 'Quinn Add Opportunity',
            AccountId = acct.Id,
            StageName = 'Prospecting',
            CloseDate = Date.today().addDays(30)
        );
        insert opp;
        Quote q = new Quote(
            Name = 'Quinn Add Quote',
            OpportunityId = opp.Id,
            Pricebook2Id = Test.getStandardPricebookId(),
            Status = 'Draft'
        );
        insert q;

        ProductRecord pr = insertProduct(productName, true, false);

        Fixture f = new Fixture();
        f.quoteId = q.Id;
        f.productId = pr.productId;

        if (withSellingModel) {
            ProductSellingModel psm = new ProductSellingModel(
                Name = productName + ' Selling Model',
                SellingModelType = 'OneTime',
                Status = 'Active'
            );
            insert psm;
            ProductSellingModelOption opt = new ProductSellingModelOption(
                Product2Id = pr.productId,
                ProductSellingModelId = psm.Id,
                IsDefault = true
            );
            insert opt;
            f.sellingModelId = psm.Id;
        }
        return f;
    }

    private class ProductRecord {
        Id productId;
    }

    private static ProductRecord insertProduct(String name, Boolean active, Boolean withPbe) {
        Product2 product = new Product2(Name = name, IsActive = active);
        insert product;
        if (withPbe) {
            PricebookEntry pbe = new PricebookEntry(
                Pricebook2Id = Test.getStandardPricebookId(),
                Product2Id = product.Id,
                UnitPrice = 100,
                IsActive = true
            );
            insert pbe;
        }
        ProductRecord pr = new ProductRecord();
        pr.productId = product.Id;
        return pr;
    }
}
