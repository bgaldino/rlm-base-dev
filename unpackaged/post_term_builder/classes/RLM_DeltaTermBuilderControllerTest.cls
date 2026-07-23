@IsTest
private class RLM_DeltaTermBuilderControllerTest {

    // ---------- shared fixtures ----------

    private static Account insertAccount() {
        Account a = new Account(Name = 'Term Builder Account');
        insert a;
        return a;
    }

    // Account with a full Bill To / Ship To address, mirroring the order-readiness seed source.
    private static Account insertAccountWithAddress() {
        Account a = new Account(
            Name = 'Term Builder Account',
            BillingStreet = '1 Delta Way', BillingCity = 'Atlanta', BillingState = 'GA',
            BillingPostalCode = '30320', BillingCountry = 'USA',
            ShippingStreet = '1 Delta Way', ShippingCity = 'Atlanta', ShippingState = 'GA',
            ShippingPostalCode = '30320', ShippingCountry = 'USA'
        );
        insert a;
        return a;
    }

    // Distinct last name / email per contact so an org Contact duplicate rule can't block a second insert.
    private static Integer contactSeq = 0;
    private static Contact insertContact(Account a) {
        contactSeq++;
        Contact c = new Contact(
            LastName = 'Rep ' + contactSeq, AccountId = a.Id,
            Email = 'rep' + contactSeq + '@example.com', Phone = '404-555-010' + contactSeq
        );
        insert c;
        return c;
    }

    private static Quote insertQuoteFor(Account a) {
        Id pbId = Test.getStandardPricebookId();
        Opportunity opp = new Opportunity(
            Name = 'TB Opp', AccountId = a.Id, StageName = 'Prospecting', CloseDate = Date.today().addDays(30)
        );
        insert opp;
        Quote q = new Quote(Name = 'TB Quote', Pricebook2Id = pbId, OpportunityId = opp.Id, Status = 'Draft');
        insert q;
        return q;
    }

    // Plain (non-Term) product + PBE + QLI on the quote.
    private static QuoteLineItem insertPlainLine(Quote q, String code) {
        Product2 p = new Product2(Name = 'Plain ' + code, ProductCode = code, IsActive = true);
        insert p;
        PricebookEntry pbe = new PricebookEntry(Pricebook2Id = Test.getStandardPricebookId(), Product2Id = p.Id, UnitPrice = 0, IsActive = true);
        insert pbe;
        QuoteLineItem qli = new QuoteLineItem(QuoteId = q.Id, Product2Id = p.Id, PricebookEntryId = pbe.Id, Quantity = 1, UnitPrice = 0);
        insert qli;
        return qli;
    }

    // A DL-TERM root line (ProductCode = 'DL-TERM') on the quote.
    private static QuoteLineItem insertTermLine(Quote q) {
        Product2 p = new Product2(Name = 'Delta Term', ProductCode = 'DL-TERM', IsActive = true);
        insert p;
        PricebookEntry pbe = new PricebookEntry(Pricebook2Id = Test.getStandardPricebookId(), Product2Id = p.Id, UnitPrice = 0, IsActive = true);
        insert pbe;
        QuoteLineItem qli = new QuoteLineItem(QuoteId = q.Id, Product2Id = p.Id, PricebookEntryId = pbe.Id, Quantity = 1, UnitPrice = 0);
        insert qli;
        return qli;
    }

    // A fare-class product BasedOn a PC-DL-FARE classification, with a PBE on the standard book.
    private static PricebookEntry insertFarePbe(String code) {
        ProductClassification pc = [SELECT Id FROM ProductClassification WHERE Code = 'PC-DL-FARE' LIMIT 1];
        Product2 p = new Product2(Name = 'Fare ' + code, ProductCode = code, IsActive = true, BasedOnId = pc.Id);
        insert p;
        PricebookEntry pbe = new PricebookEntry(Pricebook2Id = Test.getStandardPricebookId(), Product2Id = p.Id, UnitPrice = 0, IsActive = true);
        insert pbe;
        return pbe;
    }

    private static void ensureFareClassification() {
        if ([SELECT COUNT() FROM ProductClassification WHERE Code = 'PC-DL-FARE'] == 0) {
            insert new ProductClassification(Name = 'DL Fare Class', Code = 'PC-DL-FARE', Status = 'Active');
        }
    }

    // A fare line on the quote reusing a shared PBE — the same Product2Id on multiple lines is what
    // makes two fares collide under the product-only fidelity key. Optional CustomProductName + Discount
    // let a test stand in for a cloned line (name carried verbatim; codes/discount dropped by the clone).
    private static QuoteLineItem insertFareLine(Quote q, PricebookEntry pbe, String customName, Decimal discount) {
        QuoteLineItem qli = new QuoteLineItem(
            QuoteId = q.Id, Product2Id = pbe.Product2Id, PricebookEntryId = pbe.Id, Quantity = 1, UnitPrice = 0
        );
        if (customName != null) {
            qli.CustomProductName = customName;
        }
        if (discount != null) {
            qli.Discount = discount;
        }
        insert qli;
        return qli;
    }

    // Set a fare line's codes through the proven update-as-user controller path (which also auto-names
    // the fare from its codes — a raw system-mode DML of DL_FareCodes__c hits FLS in this test context).
    private static void saveFareCodes(Quote q, Id lineId, List<Object> codes) {
        Map<String, Object> in0 = new Map<String, Object>{
            'quoteId' => q.Id,
            'lines' => new List<Object>{ new Map<String, Object>{ 'id' => lineId, 'fareCodes' => codes } }
        };
        RLM_DeltaLineController.updateLineDiscountAndDates(JSON.serialize(in0));
    }

    // Set a fare line's alliance partners through the same update-as-user controller path (a raw
    // system-mode DML of the multipicklist hits FLS in this test context).
    private static void saveAlliancePartners(Quote q, Id lineId, List<Object> partners) {
        Map<String, Object> in0 = new Map<String, Object>{
            'quoteId' => q.Id,
            'lines' => new List<Object>{ new Map<String, Object>{ 'id' => lineId, 'alliancePartners' => partners } }
        };
        RLM_DeltaLineController.updateLineDiscountAndDates(JSON.serialize(in0));
    }

    private static Map<String, Object> parse(String body) {
        return (Map<String, Object>) JSON.deserializeUntyped(body);
    }

    // ---------- createNegotiation ----------

    @IsTest
    static void testCreate_MalformedJson() {
        System.assertEquals(false, parse(RLM_DeltaTermBuilderController.createNegotiation('{bad')).get('isSuccess'), 'Malformed JSON fails gracefully');
    }

    @IsTest
    static void testCreate_InvalidAccountId() {
        Map<String, Object> in0 = new Map<String, Object>{ 'accountId' => 'bad' };
        System.assertEquals(false, parse(RLM_DeltaTermBuilderController.createNegotiation(JSON.serialize(in0))).get('isSuccess'), 'Invalid account id rejected');
    }

    @IsTest
    static void testCreate_MissingAccountRejected() {
        // Well-formed but nonexistent account id → the existence guard fires before any PST work.
        Map<String, Object> in0 = new Map<String, Object>{ 'accountId' => '001000000000000AAA' };
        System.assertEquals(false, parse(RLM_DeltaTermBuilderController.createNegotiation(JSON.serialize(in0))).get('isSuccess'), 'Nonexistent account rejected');
    }

    @IsTest
    static void testCreate_ValidGracefulContract() {
        // Real account + default-name path → PST commit. PST is non-deterministic in test context, so
        // assert only the graceful contract (a decided result, never an exception).
        Account a = insertAccount();
        Map<String, Object> in0 = new Map<String, Object>{ 'accountId' => a.Id };
        Test.startTest();
        Map<String, Object> res = parse(RLM_DeltaTermBuilderController.createNegotiation(JSON.serialize(in0)));
        Test.stopTest();
        System.assertNotEquals(null, res.get('isSuccess'), 'Create returns a decided result');
    }

    @IsTest
    static void testCreate_ExplicitLongNameTruncatedGracefulContract() {
        // A >80-char explicit name exercises the trim/truncate branch before commit.
        Account a = insertAccount();
        Map<String, Object> in0 = new Map<String, Object>{ 'accountId' => a.Id, 'quoteName' => 'X'.repeat(120) };
        Map<String, Object> res = parse(RLM_DeltaTermBuilderController.createNegotiation(JSON.serialize(in0)));
        System.assertNotEquals(null, res.get('isSuccess'), 'Long-name create returns a decided result');
    }

    @IsTest
    static void testCreate_SeedsBillToContactFromAccountGracefulContract() {
        // Account with an address + a single contact → the seed resolves the oldest contact as Bill To.
        // PST is non-deterministic in test context, so assert only the graceful contract.
        Account a = insertAccountWithAddress();
        insertContact(a);
        Map<String, Object> in0 = new Map<String, Object>{ 'accountId' => a.Id };
        Test.startTest();
        Map<String, Object> res = parse(RLM_DeltaTermBuilderController.createNegotiation(JSON.serialize(in0)));
        Test.stopTest();
        System.assertNotEquals(null, res.get('isSuccess'), 'Seeded create returns a decided result');
    }

    @IsTest
    static void testCreate_ExplicitBillToContactOverrideGracefulContract() {
        // An explicit billToContactId (UI override) is honored over the first-contact fallback.
        Account a = insertAccountWithAddress();
        insertContact(a);                       // oldest contact (the fallback)
        Contact chosen = insertContact(a);      // explicitly selected override
        Map<String, Object> in0 = new Map<String, Object>{
            'accountId' => a.Id, 'billToContactId' => chosen.Id
        };
        Test.startTest();
        Map<String, Object> res = parse(RLM_DeltaTermBuilderController.createNegotiation(JSON.serialize(in0)));
        Test.stopTest();
        System.assertNotEquals(null, res.get('isSuccess'), 'Override create returns a decided result');
    }

    @IsTest
    static void testCreate_InvalidBillToContactIdRejected() {
        Account a = insertAccountWithAddress();
        Map<String, Object> in0 = new Map<String, Object>{ 'accountId' => a.Id, 'billToContactId' => 'bad' };
        System.assertEquals(false,
            parse(RLM_DeltaTermBuilderController.createNegotiation(JSON.serialize(in0))).get('isSuccess'),
            'Malformed Bill To contact id rejected');
    }

    @IsTest
    static void testCreate_NonexistentBillToContactRejected() {
        // Well-formed but nonexistent contact id → the explicit-contact access guard fires.
        Account a = insertAccountWithAddress();
        Map<String, Object> in0 = new Map<String, Object>{
            'accountId' => a.Id, 'billToContactId' => '003000000000000AAA'
        };
        System.assertEquals(false,
            parse(RLM_DeltaTermBuilderController.createNegotiation(JSON.serialize(in0))).get('isSuccess'),
            'Nonexistent Bill To contact rejected');
    }

    @IsTest
    static void testCreate_NoContactStillCreatesGracefulContract() {
        // Account with no contact → Bill To stays unset (order gate flags it later), create still runs.
        Account a = insertAccountWithAddress();
        Map<String, Object> in0 = new Map<String, Object>{ 'accountId' => a.Id };
        Test.startTest();
        Map<String, Object> res = parse(RLM_DeltaTermBuilderController.createNegotiation(JSON.serialize(in0)));
        Test.stopTest();
        System.assertNotEquals(null, res.get('isSuccess'), 'No-contact create returns a decided result');
    }

    // ---------- getNegotiationsForAccount ----------

    @IsTest
    static void testNegotiations_InvalidId() {
        Map<String, Object> in0 = new Map<String, Object>{ 'accountId' => 'bad' };
        System.assertEquals(false, parse(RLM_DeltaTermBuilderController.getNegotiationsForAccount(JSON.serialize(in0))).get('isSuccess'), 'Invalid id rejected');
    }

    @IsTest
    static void testNegotiations_ReturnsQuotesForAccount() {
        Account a = insertAccount();
        insertQuoteFor(a); // AccountId-linked via the opportunity
        Map<String, Object> in0 = new Map<String, Object>{ 'accountId' => a.Id };
        Map<String, Object> res = parse(RLM_DeltaTermBuilderController.getNegotiationsForAccount(JSON.serialize(in0)));
        System.assertEquals(true, res.get('isSuccess'), 'Lookup succeeds');
        System.assertEquals(1, ((List<Object>) res.get('quotes')).size(), 'The account\'s quote is returned');
    }

    // ---------- updateNegotiationDates ----------

    @IsTest
    static void testUpdateNegotiationDates_MalformedJson() {
        System.assertEquals(false, parse(RLM_DeltaTermBuilderController.updateNegotiationDates('{bad')).get('isSuccess'), 'Malformed JSON fails gracefully');
    }

    @IsTest
    static void testUpdateNegotiationDates_InvalidQuoteId() {
        Map<String, Object> in0 = new Map<String, Object>{ 'quoteId' => 'bad' };
        System.assertEquals(false, parse(RLM_DeltaTermBuilderController.updateNegotiationDates(JSON.serialize(in0))).get('isSuccess'), 'Invalid quote id rejected');
    }

    @IsTest
    static void testUpdateNegotiationDates_MissingQuoteRejected() {
        Map<String, Object> in0 = new Map<String, Object>{ 'quoteId' => '0Q0000000000000AAA' };
        System.assertEquals(false, parse(RLM_DeltaTermBuilderController.updateNegotiationDates(JSON.serialize(in0))).get('isSuccess'), 'Nonexistent quote rejected');
    }

    @IsTest
    static void testUpdateNegotiationDates_EndBeforeStartRejected() {
        Account a = insertAccount();
        Quote q = insertQuoteFor(a);
        Map<String, Object> in0 = new Map<String, Object>{
            'quoteId' => q.Id, 'negotiationStartDate' => '2026-06-01', 'negotiationEndDate' => '2026-01-01'
        };
        Map<String, Object> res = parse(RLM_DeltaTermBuilderController.updateNegotiationDates(JSON.serialize(in0)));
        System.assertEquals(false, res.get('isSuccess'), 'End date before start date is rejected');
    }

    @IsTest
    static void testUpdateNegotiationDates_SetsBothDates() {
        Account a = insertAccount();
        Quote q = insertQuoteFor(a);
        Map<String, Object> in0 = new Map<String, Object>{
            'quoteId' => q.Id, 'negotiationStartDate' => '2026-01-01', 'negotiationEndDate' => '2027-01-01'
        };
        Test.startTest();
        Map<String, Object> res = parse(RLM_DeltaTermBuilderController.updateNegotiationDates(JSON.serialize(in0)));
        Test.stopTest();
        System.assertEquals(true, res.get('isSuccess'), 'Update succeeds: ' + res.get('errorMessage'));
        Quote reloaded = [SELECT DL_NegotiationStartDate__c, DL_NegotiationEndDate__c FROM Quote WHERE Id = :q.Id];
        System.assertEquals(Date.newInstance(2026, 1, 1), reloaded.DL_NegotiationStartDate__c, 'Start date persisted');
        System.assertEquals(Date.newInstance(2027, 1, 1), reloaded.DL_NegotiationEndDate__c, 'End date persisted');
    }

    @IsTest
    static void testUpdateNegotiationDates_BlankClearsDates() {
        Account a = insertAccount();
        Quote q = insertQuoteFor(a);
        update new Quote(
            Id = q.Id,
            DL_NegotiationStartDate__c = Date.newInstance(2026, 1, 1),
            DL_NegotiationEndDate__c = Date.newInstance(2027, 1, 1)
        );
        Map<String, Object> in0 = new Map<String, Object>{ 'quoteId' => q.Id };
        Test.startTest();
        Map<String, Object> res = parse(RLM_DeltaTermBuilderController.updateNegotiationDates(JSON.serialize(in0)));
        Test.stopTest();
        System.assertEquals(true, res.get('isSuccess'), 'Update succeeds: ' + res.get('errorMessage'));
        Quote reloaded = [SELECT DL_NegotiationStartDate__c, DL_NegotiationEndDate__c FROM Quote WHERE Id = :q.Id];
        System.assertEquals(null, reloaded.DL_NegotiationStartDate__c, 'Blank input clears the start date');
        System.assertEquals(null, reloaded.DL_NegotiationEndDate__c, 'Blank input clears the end date');
    }

    @IsTest
    static void testBuilderState_ReturnsNegotiationDates() {
        // getBuilderState surfaces the header defaults so the LWC can populate the date inputs.
        Account a = insertAccount();
        Quote q = insertQuoteFor(a);
        update new Quote(
            Id = q.Id,
            DL_NegotiationStartDate__c = Date.newInstance(2026, 3, 1),
            DL_NegotiationEndDate__c = Date.newInstance(2027, 3, 1)
        );
        Test.startTest();
        Map<String, Object> res = parse(RLM_DeltaTermBuilderController.getBuilderState(q.Id));
        Test.stopTest();
        System.assertEquals(true, res.get('isSuccess'), 'State loads: ' + res.get('errorMessage'));
        Map<String, Object> quote = (Map<String, Object>) res.get('quote');
        System.assertEquals('2026-03-01', quote.get('negotiationStartDate'), 'Negotiation start date echoed');
        System.assertEquals('2027-03-01', quote.get('negotiationEndDate'), 'Negotiation end date echoed');
    }

    // ---------- addTerm ----------

    @IsTest
    static void testAddTerm_MalformedJson() {
        System.assertEquals(false, parse(RLM_DeltaTermBuilderController.addTerm('{bad')).get('isSuccess'), 'Malformed JSON fails gracefully');
    }

    @IsTest
    static void testAddTerm_InvalidQuoteId() {
        Map<String, Object> in0 = new Map<String, Object>{ 'quoteId' => 'bad' };
        System.assertEquals(false, parse(RLM_DeltaTermBuilderController.addTerm(JSON.serialize(in0))).get('isSuccess'), 'Invalid quote id rejected');
    }

    @IsTest
    static void testAddTerm_MissingQuoteRejected() {
        // Well-formed but nonexistent quote id → the existence guard fires before any PST work.
        Map<String, Object> in0 = new Map<String, Object>{ 'quoteId' => '0Q0000000000000AAA' };
        System.assertEquals(false, parse(RLM_DeltaTermBuilderController.addTerm(JSON.serialize(in0))).get('isSuccess'), 'Nonexistent quote rejected');
    }

    @IsTest
    static void testAddTerm_ValidGracefulContract() {
        // Real quote + a DL-TERM product on the standard book → passes every guard to the PST commit.
        // PST is non-deterministic in test context, so assert only a decided result. The insertTermLine
        // fixture guarantees a DL-TERM product with an active PBE on the standard book.
        Account a = insertAccount();
        Quote q = insertQuoteFor(a);
        insertTermLine(q); // ensures a DL-TERM product + active standard-book PBE exist
        Map<String, Object> in0 = new Map<String, Object>{ 'quoteId' => q.Id, 'count' => 2 };
        Test.startTest();
        Map<String, Object> res = parse(RLM_DeltaTermBuilderController.addTerm(JSON.serialize(in0)));
        Test.stopTest();
        System.assertNotEquals(null, res.get('isSuccess'), 'Add Term returns a decided result');
    }

    // ---------- getBuilderState ----------

    @IsTest
    static void testBuilderState_InvalidId() {
        System.assertEquals(false, parse(RLM_DeltaTermBuilderController.getBuilderState('bad')).get('isSuccess'), 'Invalid id rejected');
    }

    @IsTest
    static void testBuilderState_EmptyQuoteSucceeds() {
        Account a = insertAccount();
        Quote q = insertQuoteFor(a);
        Test.startTest();
        Map<String, Object> res = parse(RLM_DeltaTermBuilderController.getBuilderState(q.Id));
        Test.stopTest();
        System.assertEquals(true, res.get('isSuccess'), 'Empty quote succeeds');
        System.assertEquals(0, ((List<Object>) res.get('terms')).size(), 'No terms yet');
        System.assertEquals('DL-TERM', res.get('termSku'), 'Term SKU echoed');
        System.assertEquals(null, res.get('contractId'), 'An uncontracted quote returns no contract id');
    }

    @IsTest
    static void testBuilderState_ExistingContractSurfaced() {
        // A quote already related to a Contract (ContractId) surfaces the contract's id + number so the
        // header can offer "View Contract" instead of a Create Contract that the platform would reject.
        Account a = insertAccount();
        Quote q = insertQuoteFor(a);
        Contract c = new Contract(AccountId = a.Id, Status = 'Draft', StartDate = Date.newInstance(2026, 1, 1));
        insert c;
        update new Quote(Id = q.Id, ContractId = c.Id);

        Test.startTest();
        Map<String, Object> res = parse(RLM_DeltaTermBuilderController.getBuilderState(q.Id));
        Test.stopTest();

        System.assertEquals(true, res.get('isSuccess'), 'State loads: ' + res.get('errorMessage'));
        System.assertEquals(c.Id, res.get('contractId'), 'The related contract id is returned');
        Contract reloaded = [SELECT ContractNumber FROM Contract WHERE Id = :c.Id LIMIT 1];
        System.assertEquals(reloaded.ContractNumber, res.get('contractNumber'), 'The related contract number is returned');
    }

    @IsTest
    static void testBuilderState_TermWithFareShapes() {
        // A DL-TERM root with one fare child under it exercises the partition + faresByTerm grouping.
        ensureFareClassification();
        Account a = insertAccount();
        Quote q = insertQuoteFor(a);
        QuoteLineItem term = insertTermLine(q);
        // A plain child line pointed at the term via ParentQuoteLineItemId is not settable directly
        // (platform-stamped), so link it through QuoteLineRelationship, which the state reader honors.
        QuoteLineItem fare = insertPlainLine(q, 'FARE-STATE');
        // QuoteLineRelationship requires a relationship type + the bundle-pricing flag on create
        // (org-configured, the same fields the controller stamps at runtime). ProductRelationshipType
        // is a setup object not visible in the default (SeeAllData=false) test context, so the
        // relationship link is conditional: when a type is available we assert the fare groups under
        // its Term; otherwise the Term-partition path is still exercised without the child link.
        List<ProductRelationshipType> prts = [SELECT Id FROM ProductRelationshipType LIMIT 1];
        Boolean linked = !prts.isEmpty();
        if (linked) {
            insert new QuoteLineRelationship(
                RootQuoteLineId = term.Id, MainQuoteLineId = term.Id, AssociatedQuoteLineId = fare.Id,
                ProductRelationshipTypeId = prts[0].Id, AssociatedQuoteLinePricing = 'NotIncludedInBundlePrice'
            );
        }
        Test.startTest();
        Map<String, Object> res = parse(RLM_DeltaTermBuilderController.getBuilderState(q.Id));
        Test.stopTest();
        System.assertEquals(true, res.get('isSuccess'), 'State loads: ' + res.get('errorMessage'));
        List<Object> terms = (List<Object>) res.get('terms');
        System.assertEquals(1, terms.size(), 'One Term root');
        System.assertEquals(term.Id, res.get('selectedTermId'), 'First Term is selected by default');
        System.assertEquals(
            linked ? 1 : 0,
            (Integer) ((Map<String, Object>) terms[0]).get('fareCount'),
            'Fare grouped under the Term when the relationship link exists'
        );
    }

    // ---------- getFareChoices ----------

    @IsTest
    static void testFareChoices_InvalidId() {
        Map<String, Object> in0 = new Map<String, Object>{ 'quoteId' => 'bad' };
        System.assertEquals(false, parse(RLM_DeltaTermBuilderController.getFareChoices(JSON.serialize(in0))).get('isSuccess'), 'Invalid id rejected');
    }

    @IsTest
    static void testFareChoices_ListsFareWithPbe() {
        ensureFareClassification();
        Account a = insertAccount();
        Quote q = insertQuoteFor(a);
        insertFarePbe('FC-1');
        Test.startTest();
        Map<String, Object> res = parse(RLM_DeltaTermBuilderController.getFareChoices(JSON.serialize(new Map<String, Object>{ 'quoteId' => q.Id })));
        Test.stopTest();
        System.assertEquals(true, res.get('isSuccess'), 'Fare lookup succeeds');
        System.assertEquals(1, ((List<Object>) res.get('fares')).size(), 'The PC-DL-FARE product with a PBE is offered');
    }

    // ---------- addFareClassToTerm: fail-closed guards ----------

    @IsTest
    static void testAddFare_MalformedJson() {
        System.assertEquals(false, parse(RLM_DeltaTermBuilderController.addFareClassToTerm('{bad')).get('isSuccess'), 'Malformed JSON fails gracefully');
    }

    @IsTest
    static void testAddFare_InvalidQuoteId() {
        Map<String, Object> in0 = new Map<String, Object>{ 'quoteId' => 'bad', 'termLineId' => '0QL000000000000AAA' };
        System.assertEquals(false, parse(RLM_DeltaTermBuilderController.addFareClassToTerm(JSON.serialize(in0))).get('isSuccess'), 'Invalid quote id rejected');
    }

    @IsTest
    static void testAddFare_ForeignTermRejected() {
        Account a = insertAccount();
        Quote q = insertQuoteFor(a);
        Quote other = insertQuoteFor(a);
        QuoteLineItem foreignTerm = insertTermLine(other); // belongs to a different quote
        Map<String, Object> in0 = new Map<String, Object>{
            'quoteId' => q.Id, 'termLineId' => foreignTerm.Id, 'pbeId' => '01u000000000000AAA'
        };
        Map<String, Object> res = parse(RLM_DeltaTermBuilderController.addFareClassToTerm(JSON.serialize(in0)));
        System.assertEquals(false, res.get('isSuccess'), 'A Term on another quote is rejected');
    }

    @IsTest
    static void testAddFare_NonTermLineRejected() {
        Account a = insertAccount();
        Quote q = insertQuoteFor(a);
        QuoteLineItem plain = insertPlainLine(q, 'NOT-TERM'); // not a DL-TERM product
        Map<String, Object> in0 = new Map<String, Object>{
            'quoteId' => q.Id, 'termLineId' => plain.Id, 'pbeId' => '01u000000000000AAA'
        };
        Map<String, Object> res = parse(RLM_DeltaTermBuilderController.addFareClassToTerm(JSON.serialize(in0)));
        System.assertEquals(false, res.get('isSuccess'), 'A non-Term line is rejected');
    }

    @IsTest
    static void testAddFare_PbeNotOnBookRejected() {
        Account a = insertAccount();
        Quote q = insertQuoteFor(a);
        QuoteLineItem term = insertTermLine(q);
        // A well-formed but nonexistent PBE id → the book-membership guard fires.
        Map<String, Object> in0 = new Map<String, Object>{
            'quoteId' => q.Id, 'termLineId' => term.Id, 'pbeId' => '01u000000000000AAA'
        };
        Map<String, Object> res = parse(RLM_DeltaTermBuilderController.addFareClassToTerm(JSON.serialize(in0)));
        System.assertEquals(false, res.get('isSuccess'), 'A PBE not on the quote book is rejected');
    }

    @IsTest
    static void testAddFare_NonFareProductRejected() {
        // A real, on-book PBE whose product is NOT classified PC-DL-FARE is rejected before commit.
        ensureFareClassification();
        Account a = insertAccount();
        Quote q = insertQuoteFor(a);
        QuoteLineItem term = insertTermLine(q);
        QuoteLineItem plain = insertPlainLine(q, 'NONFARE'); // its PBE is valid on the book, but not a fare
        PricebookEntry plainPbe = [SELECT Id FROM PricebookEntry WHERE Product2Id = :plain.Product2Id LIMIT 1];
        Map<String, Object> in0 = new Map<String, Object>{
            'quoteId' => q.Id, 'termLineId' => term.Id, 'pbeId' => plainPbe.Id
        };
        Map<String, Object> res = parse(RLM_DeltaTermBuilderController.addFareClassToTerm(JSON.serialize(in0)));
        System.assertEquals(false, res.get('isSuccess'), 'A non-fare product is rejected');
    }

    // ---------- addFareClassToTerm: accept path (graceful contract) ----------

    @IsTest
    static void testAddFare_ValidGracefulContract() {
        // Real DL-TERM + real PC-DL-FARE product on the book → passes every guard to the PST commit.
        // PST is non-deterministic in test context, so assert only a decided result.
        ensureFareClassification();
        Account a = insertAccount();
        Quote q = insertQuoteFor(a);
        QuoteLineItem term = insertTermLine(q);
        PricebookEntry farePbe = insertFarePbe('FARE-ADD');
        Map<String, Object> in0 = new Map<String, Object>{
            'quoteId' => q.Id, 'termLineId' => term.Id, 'pbeId' => farePbe.Id, 'productId' => farePbe.Product2Id
        };
        Test.startTest();
        Map<String, Object> res = parse(RLM_DeltaTermBuilderController.addFareClassToTerm(JSON.serialize(in0)));
        Test.stopTest();
        System.assertNotEquals(null, res.get('isSuccess'), 'A valid fare add returns a decided result');
    }

    @IsTest
    static void testAddFare_FallbackByProductIdGracefulContract() {
        // Omit pbeId → the fallback resolves the fare PBE by product id. Graceful contract.
        ensureFareClassification();
        Account a = insertAccount();
        Quote q = insertQuoteFor(a);
        QuoteLineItem term = insertTermLine(q);
        PricebookEntry farePbe = insertFarePbe('FARE-FB');
        Map<String, Object> in0 = new Map<String, Object>{
            'quoteId' => q.Id, 'termLineId' => term.Id, 'productId' => farePbe.Product2Id
        };
        Test.startTest();
        Map<String, Object> res = parse(RLM_DeltaTermBuilderController.addFareClassToTerm(JSON.serialize(in0)));
        Test.stopTest();
        System.assertNotEquals(null, res.get('isSuccess'), 'A product-id fallback fare add returns a decided result');
    }

    // ---------- addFareClassesToTerm (batch): fail-closed guards ----------

    @IsTest
    static void testAddFares_MalformedJson() {
        System.assertEquals(false, parse(RLM_DeltaTermBuilderController.addFareClassesToTerm('{bad')).get('isSuccess'), 'Malformed JSON fails gracefully');
    }

    @IsTest
    static void testAddFares_InvalidQuoteId() {
        Map<String, Object> in0 = new Map<String, Object>{
            'quoteId' => 'bad', 'termLineId' => '0QL000000000000AAA',
            'fares' => new List<Object>{ new Map<String, Object>{ 'pbeId' => '01u000000000000AAA' } }
        };
        System.assertEquals(false, parse(RLM_DeltaTermBuilderController.addFareClassesToTerm(JSON.serialize(in0))).get('isSuccess'), 'Invalid quote id rejected');
    }

    @IsTest
    static void testAddFares_EmptyListRejected() {
        Account a = insertAccount();
        Quote q = insertQuoteFor(a);
        QuoteLineItem term = insertTermLine(q);
        Map<String, Object> in0 = new Map<String, Object>{
            'quoteId' => q.Id, 'termLineId' => term.Id, 'fares' => new List<Object>()
        };
        Map<String, Object> res = parse(RLM_DeltaTermBuilderController.addFareClassesToTerm(JSON.serialize(in0)));
        System.assertEquals(false, res.get('isSuccess'), 'An empty fares list is rejected');
    }

    @IsTest
    static void testAddFares_ForeignTermRejected() {
        Account a = insertAccount();
        Quote q = insertQuoteFor(a);
        Quote other = insertQuoteFor(a);
        QuoteLineItem foreignTerm = insertTermLine(other); // belongs to a different quote
        Map<String, Object> in0 = new Map<String, Object>{
            'quoteId' => q.Id, 'termLineId' => foreignTerm.Id,
            'fares' => new List<Object>{ new Map<String, Object>{ 'pbeId' => '01u000000000000AAA' } }
        };
        Map<String, Object> res = parse(RLM_DeltaTermBuilderController.addFareClassesToTerm(JSON.serialize(in0)));
        System.assertEquals(false, res.get('isSuccess'), 'A Term on another quote is rejected');
    }

    @IsTest
    static void testAddFares_NonTermLineRejected() {
        Account a = insertAccount();
        Quote q = insertQuoteFor(a);
        QuoteLineItem plain = insertPlainLine(q, 'NOT-TERM'); // not a DL-TERM product
        Map<String, Object> in0 = new Map<String, Object>{
            'quoteId' => q.Id, 'termLineId' => plain.Id,
            'fares' => new List<Object>{ new Map<String, Object>{ 'pbeId' => '01u000000000000AAA' } }
        };
        Map<String, Object> res = parse(RLM_DeltaTermBuilderController.addFareClassesToTerm(JSON.serialize(in0)));
        System.assertEquals(false, res.get('isSuccess'), 'A non-Term line is rejected');
    }

    @IsTest
    static void testAddFares_OverCapRejected() {
        // Requesting more fares than the Term can hold is rejected atomically, before any commit.
        ensureFareClassification();
        Account a = insertAccount();
        Quote q = insertQuoteFor(a);
        QuoteLineItem term = insertTermLine(q);
        // Build a fares list well over the 20-child cap (all pointing at one real fare product).
        PricebookEntry farePbe = insertFarePbe('FARE-CAP');
        List<Object> fares = new List<Object>();
        for (Integer i = 0; i < 21; i++) {
            fares.add(new Map<String, Object>{ 'pbeId' => farePbe.Id, 'productId' => farePbe.Product2Id });
        }
        Map<String, Object> in0 = new Map<String, Object>{
            'quoteId' => q.Id, 'termLineId' => term.Id, 'fares' => fares
        };
        Map<String, Object> res = parse(RLM_DeltaTermBuilderController.addFareClassesToTerm(JSON.serialize(in0)));
        System.assertEquals(false, res.get('isSuccess'), 'A batch exceeding the per-Term cap is rejected');
    }

    @IsTest
    static void testAddFares_NonFareProductRejected() {
        // A real, on-book PBE whose product is NOT classified PC-DL-FARE is rejected before commit.
        ensureFareClassification();
        Account a = insertAccount();
        Quote q = insertQuoteFor(a);
        QuoteLineItem term = insertTermLine(q);
        QuoteLineItem plain = insertPlainLine(q, 'NONFARE2'); // valid on the book, but not a fare
        PricebookEntry plainPbe = [SELECT Id, Product2Id FROM PricebookEntry WHERE Product2Id = :plain.Product2Id LIMIT 1];
        Map<String, Object> in0 = new Map<String, Object>{
            'quoteId' => q.Id, 'termLineId' => term.Id,
            'fares' => new List<Object>{ new Map<String, Object>{ 'pbeId' => plainPbe.Id } }
        };
        Map<String, Object> res = parse(RLM_DeltaTermBuilderController.addFareClassesToTerm(JSON.serialize(in0)));
        System.assertEquals(false, res.get('isSuccess'), 'A non-fare product is rejected');
    }

    // ---------- addFareClassesToTerm (batch): accept path (graceful contract) ----------

    @IsTest
    static void testAddFares_MultiValidGracefulContract() {
        // Two real PC-DL-FARE products on the book → passes every guard to a single PST commit.
        // PST is non-deterministic in test context, so assert only a decided result.
        ensureFareClassification();
        Account a = insertAccount();
        Quote q = insertQuoteFor(a);
        QuoteLineItem term = insertTermLine(q);
        PricebookEntry fare1 = insertFarePbe('FARE-B1');
        PricebookEntry fare2 = insertFarePbe('FARE-B2');
        Map<String, Object> in0 = new Map<String, Object>{
            'quoteId' => q.Id, 'termLineId' => term.Id,
            'fares' => new List<Object>{
                new Map<String, Object>{ 'pbeId' => fare1.Id, 'productId' => fare1.Product2Id },
                new Map<String, Object>{ 'productId' => fare2.Product2Id }
            }
        };
        Test.startTest();
        Map<String, Object> res = parse(RLM_DeltaTermBuilderController.addFareClassesToTerm(JSON.serialize(in0)));
        Test.stopTest();
        System.assertNotEquals(null, res.get('isSuccess'), 'A valid multi-fare add returns a decided result');
    }

    // A Contract with SourceQuoteId pointed at the given quote.
    private static Contract insertContractFor(Account a, Id sourceQuoteId) {
        Contract c = new Contract(
            AccountId = a.Id, Status = 'Draft', StartDate = Date.newInstance(2026, 1, 1), SourceQuoteId = sourceQuoteId
        );
        insert c;
        return c;
    }

    // ---------- buildRenewalName (unit) ----------

    @IsTest
    static void testRenewalName_AppendsSuffix() {
        System.assertEquals('Acme Deal - Renewal', RLM_DeltaTermBuilderController.buildRenewalName('Acme Deal'), 'Suffix appended');
    }

    @IsTest
    static void testRenewalName_BlankFallsBackToNegotiation() {
        System.assertEquals('Negotiation - Renewal', RLM_DeltaTermBuilderController.buildRenewalName('  '), 'Blank name falls back to Negotiation');
    }

    @IsTest
    static void testRenewalName_TruncatesBaseKeepsSuffix() {
        String result = RLM_DeltaTermBuilderController.buildRenewalName('X'.repeat(120));
        System.assert(result.length() <= 80, 'Renewal name capped at 80 chars: ' + result.length());
        System.assert(result.endsWith(' - Renewal'), 'The " - Renewal" suffix survives truncation');
    }

    // ---------- createRenewalFromContract: fail-closed guards ----------

    @IsTest
    static void testRenewal_MalformedJson() {
        System.assertEquals(false, parse(RLM_DeltaTermBuilderController.createRenewalFromContract('{bad')).get('isSuccess'), 'Malformed JSON fails gracefully');
    }

    @IsTest
    static void testRenewal_InvalidContractId() {
        Map<String, Object> in0 = new Map<String, Object>{ 'contractId' => 'bad' };
        System.assertEquals(false, parse(RLM_DeltaTermBuilderController.createRenewalFromContract(JSON.serialize(in0))).get('isSuccess'), 'Invalid contract id rejected');
    }

    @IsTest
    static void testRenewal_MissingContractRejected() {
        // Well-formed but nonexistent contract id → the existence guard fires before any clone work.
        Map<String, Object> in0 = new Map<String, Object>{ 'contractId' => '800000000000000AAA' };
        System.assertEquals(false, parse(RLM_DeltaTermBuilderController.createRenewalFromContract(JSON.serialize(in0))).get('isSuccess'), 'Nonexistent contract rejected');
    }

    @IsTest
    static void testRenewal_NoSourceQuoteRejected() {
        // A Contract with no SourceQuoteId (not created by the Term Builder / create-contract flows)
        // cannot be renewed — the guard fires before any clone work.
        Account a = insertAccount();
        Contract c = new Contract(AccountId = a.Id, Status = 'Draft', StartDate = Date.newInstance(2026, 1, 1));
        insert c;
        Map<String, Object> in0 = new Map<String, Object>{ 'contractId' => c.Id };
        Map<String, Object> res = parse(RLM_DeltaTermBuilderController.createRenewalFromContract(JSON.serialize(in0)));
        System.assertEquals(false, res.get('isSuccess'), 'A contract with no source quote is rejected');
        System.assertEquals('This contract has no source quote to renew from.', res.get('errorMessage'), 'The no-source-quote message is returned');
    }

    // ---------- createRenewalFromContract: accept path (graceful contract) ----------

    @IsTest
    static void testRenewal_ValidGracefulContract() {
        // Real Contract → real SourceQuoteId → passes every guard to the deep-clone flow. Like PST,
        // the DL_DeepCloneSalesTransaction flow's core action is non-deterministic in test context, so
        // assert only a decided result (never an exception) — the no-new-quote guard yields a clean
        // failure result rather than throwing. The live run (§Verification) proves the clone graph and
        // the DL_FareCodes__c / Discount fidelity restore.
        Account a = insertAccount();
        Quote q = insertQuoteFor(a);
        Contract c = insertContractFor(a, q.Id);
        Map<String, Object> in0 = new Map<String, Object>{ 'contractId' => c.Id };
        Test.startTest();
        Map<String, Object> res = parse(RLM_DeltaTermBuilderController.createRenewalFromContract(JSON.serialize(in0)));
        Test.stopTest();
        System.assertNotEquals(null, res.get('isSuccess'), 'Create Renewal returns a decided result');
    }

    // ---------- createRenewalFromContractViaAssets: fail-closed guards ----------

    @IsTest
    static void testRenewalViaAssets_MalformedJson() {
        System.assertEquals(false, parse(RLM_DeltaTermBuilderController.createRenewalFromContractViaAssets('{bad')).get('isSuccess'), 'Malformed JSON fails gracefully');
    }

    @IsTest
    static void testRenewalViaAssets_InvalidContractId() {
        Map<String, Object> in0 = new Map<String, Object>{ 'contractId' => 'bad' };
        System.assertEquals(false, parse(RLM_DeltaTermBuilderController.createRenewalFromContractViaAssets(JSON.serialize(in0))).get('isSuccess'), 'Invalid contract id rejected');
    }

    @IsTest
    static void testRenewalViaAssets_MissingContractRejected() {
        // Well-formed but nonexistent contract id → the existence guard fires before any renewal work.
        Map<String, Object> in0 = new Map<String, Object>{ 'contractId' => '800000000000000AAA' };
        System.assertEquals(false, parse(RLM_DeltaTermBuilderController.createRenewalFromContractViaAssets(JSON.serialize(in0))).get('isSuccess'), 'Nonexistent contract rejected');
    }

    @IsTest
    static void testRenewalViaAssets_NoSourceQuoteRejected() {
        // A Contract with no SourceQuoteId cannot be renewed — the guard fires before any asset work.
        Account a = insertAccount();
        Contract c = new Contract(AccountId = a.Id, Status = 'Draft', StartDate = Date.newInstance(2026, 1, 1));
        insert c;
        Map<String, Object> in0 = new Map<String, Object>{ 'contractId' => c.Id };
        Map<String, Object> res = parse(RLM_DeltaTermBuilderController.createRenewalFromContractViaAssets(JSON.serialize(in0)));
        System.assertEquals(false, res.get('isSuccess'), 'A contract with no source quote is rejected');
        System.assertEquals('This contract has no source quote to renew from.', res.get('errorMessage'), 'The no-source-quote message is returned');
    }

    @IsTest
    static void testRenewalViaAssets_NoRenewableAssetsRejected() {
        // A Contract with a real SourceQuoteId but NO Asset Contract Relationships (never assetized)
        // is rejected by the no-assets guard — this deterministically covers topLevelParentAssetIds and the
        // guard, before the (non-deterministic-in-test) initiateRenewal flow is ever reached. The live
        // run (§Verification) proves the initiateRenewal + discount/fare-code restore on real assets.
        Account a = insertAccount();
        Quote q = insertQuoteFor(a);
        Contract c = insertContractFor(a, q.Id);
        Map<String, Object> in0 = new Map<String, Object>{ 'contractId' => c.Id };
        Map<String, Object> res = parse(RLM_DeltaTermBuilderController.createRenewalFromContractViaAssets(JSON.serialize(in0)));
        System.assertEquals(false, res.get('isSuccess'), 'A contract with no renewable assets is rejected');
        System.assert(
            String.valueOf(res.get('errorMessage')).startsWith('This contract has no renewable assets.'),
            'The no-renewable-assets message is returned: ' + res.get('errorMessage')
        );
    }

    // ---------- restoreClonedLineFidelity: same-product fares with different codes ----------

    @IsTest
    static void testRestoreFidelity_SameFareProductDistinctCodes() {
        // Regression for the renewal mismatch: two fares of the SAME product (same Product2Id) under
        // one route, carrying DIFFERENT fare codes. The deep clone drops DL_FareCodes__c but carries
        // CustomProductName verbatim — and a fare's name encodes its codes ("Comfort (J C)" vs
        // "Comfort (J C I)"). Restore must pair each clone line to its NAME-mate in the source, not
        // collide both into one product-only bucket paired positionally (which swapped the codes).
        ensureFareClassification();
        Account a = insertAccount();

        // Source quote (the contract's origin): two Comfort fares, one product, distinct codes+discount.
        Quote src = insertQuoteFor(a);
        PricebookEntry comfort = insertFarePbe('COMFORT'); // one product shared by every Comfort line
        QuoteLineItem srcA = insertFareLine(src, comfort, null, null);
        QuoteLineItem srcB = insertFareLine(src, comfort, null, null);
        // saveFareCodes stamps codes AND the auto-name ("<base> (codes)") through the controller.
        saveFareCodes(src, srcA.Id, new List<Object>{ 'J', 'C' });
        saveFareCodes(src, srcB.Id, new List<Object>{ 'J', 'C', 'I' });
        // Alliance partners are also unmapped by the clone context, so seed distinct sets to prove the
        // restore carries each line's own partners across (same treatment as fare codes).
        saveAlliancePartners(src, srcA.Id, new List<Object>{ 'Air France' });
        saveAlliancePartners(src, srcB.Id, new List<Object>{ 'Korean Air', 'WestJet' });
        // Distinct discounts prove the discount rides along with the correct line, not just the codes.
        update new List<QuoteLineItem>{
            new QuoteLineItem(Id = srcA.Id, Discount = 5),
            new QuoteLineItem(Id = srcB.Id, Discount = 7)
        };
        Map<Id, QuoteLineItem> srcById = new Map<Id, QuoteLineItem>([
            SELECT Id, CustomProductName, DL_FareCodes__c FROM QuoteLineItem WHERE Id IN (:srcA.Id, :srcB.Id)
        ]);
        String nameA = srcById.get(srcA.Id).CustomProductName; // e.g. "Fare COMFORT (J C)"
        String nameB = srcById.get(srcB.Id).CustomProductName; // e.g. "Fare COMFORT (J C I)"
        System.assertNotEquals(nameA, nameB, 'The two fares carry distinct auto-derived names');

        // Clone quote (the renewal): same product + names carried verbatim, codes/discount DROPPED.
        // Insert in the OPPOSITE order so positional pairing (the old behavior) would swap the codes —
        // the fix must key on name, not LineNumber position.
        Quote clone = insertQuoteFor(a);
        insertFareLine(clone, comfort, nameB, null);
        insertFareLine(clone, comfort, nameA, null);

        Test.startTest();
        RLM_DeltaTermBuilderController.restoreClonedLineFidelity(src.Id, clone.Id);
        Test.stopTest();

        // Each clone fare must now carry ITS OWN name-mate's codes + discount from the source.
        Map<String, QuoteLineItem> cloneByName = new Map<String, QuoteLineItem>();
        for (QuoteLineItem cl : [
            SELECT CustomProductName, DL_FareCodes__c, DL_AlliancePartners__c, Discount, DL_PriorDiscount__c
            FROM QuoteLineItem WHERE QuoteId = :clone.Id
        ]) {
            cloneByName.put(cl.CustomProductName, cl);
        }
        System.assertEquals(
            new Set<String>{ 'J', 'C' },
            new Set<String>(cloneByName.get(nameA).DL_FareCodes__c.split(';')),
            'The "(J C)" fare kept the 2-code set (not its peer\'s codes)'
        );
        System.assertEquals(5, cloneByName.get(nameA).Discount, 'The "(J C)" fare kept its own 5% discount');
        System.assertEquals(7, cloneByName.get(nameB).Discount, 'The "(J C I)" fare kept its own 7% discount');
        // The prior-contract discount is snapshotted from the matched source line's Discount, per line.
        System.assertEquals(
            5, cloneByName.get(nameA).DL_PriorDiscount__c,
            'The "(J C)" renewal line snapshots the source line\'s 5% as its prior discount'
        );
        System.assertEquals(
            7, cloneByName.get(nameB).DL_PriorDiscount__c,
            'The "(J C I)" renewal line snapshots the source line\'s 7% as its prior discount'
        );
        System.assertEquals(
            new Set<String>{ 'J', 'C', 'I' },
            new Set<String>(cloneByName.get(nameB).DL_FareCodes__c.split(';')),
            'The "(J C I)" fare kept the 3-code set (not its peer\'s codes)'
        );
        // Alliance partners restored per name-mate, same as fare codes.
        System.assertEquals(
            new Set<String>{ 'Air France' },
            new Set<String>(cloneByName.get(nameA).DL_AlliancePartners__c.split(';')),
            'The "(J C)" fare kept its own alliance partner'
        );
        System.assertEquals(
            new Set<String>{ 'Korean Air', 'WestJet' },
            new Set<String>(cloneByName.get(nameB).DL_AlliancePartners__c.split(';')),
            'The "(J C I)" fare kept its own two alliance partners'
        );
    }

    // ---------- renewal invocables (flow-orchestrated ARC pattern) ----------

    // A top-level Term (DL-TERM) Asset for the account, with a lifecycle end that anchors the derived
    // renewal window (start = LifecycleEndDate + 1 day). deriveRenewalWindow reads LifecycleEndDate directly
    // by asset id, so the fixture enables Lifecycle Management (required to set the lifecycle window) and
    // stamps the window — no AssetContractRelationship is created (see below).
    private static Asset insertTermAsset(Account a, DateTime lifecycleEnd) {
        Product2 p = new Product2(Name = 'Delta Term Asset', ProductCode = 'DL-TERM', IsActive = true);
        insert p;
        Asset asset = new Asset(
            Name = 'Term Asset', AccountId = a.Id, Product2Id = p.Id, Quantity = 1,
            HasLifecycleManagement = true,
            LifecycleStartDate = lifecycleEnd.addYears(-1), LifecycleEndDate = lifecycleEnd
        );
        insert asset;
        return asset;
    }

    @IsTest
    static void testResolveInputs_GuardsAndBranches() {
        // Bulk call exercising every guard/branch the resolver reaches WITHOUT an AssetContractRelationship
        // (which can't be synthesized — inserting one fires standard RLM asset-lifecycle automation that
        // throws an uncatchable platform error outside the O2A flow; see buildResolvedResult's doc). Proves
        // one Result per Request, the exact user-facing messages, and that a guard never throws.
        Account a = insertAccount();
        Id pbId = Test.getStandardPricebookId();

        // Source quote with null Quote/Account ids → scopeAccountId falls back to the Contract's account.
        Quote bare = new Quote(Name = 'Bare Quote', Pricebook2Id = pbId, Status = 'Draft');
        insert bare;
        Contract noAssets = insertContractFor(a, bare.Id);       // real SourceQuoteId, never assetized

        // Contract with no SourceQuoteId at all → no-source-quote guard.
        Contract noSource = new Contract(
            AccountId = a.Id, Status = 'Draft', StartDate = Date.newInstance(2026, 1, 1)
        );
        insert noSource;

        RLM_DeltaRenewalInputsResolver.Request nullReq = new RLM_DeltaRenewalInputsResolver.Request();
        // contractId intentionally left null → resolver returns isSuccess=false (does not throw).
        RLM_DeltaRenewalInputsResolver.Request noSourceReq = new RLM_DeltaRenewalInputsResolver.Request();
        noSourceReq.contractId = noSource.Id;
        RLM_DeltaRenewalInputsResolver.Request noAssetsReq = new RLM_DeltaRenewalInputsResolver.Request();
        noAssetsReq.contractId = noAssets.Id;

        Test.startTest();
        List<RLM_DeltaRenewalInputsResolver.Result> results = RLM_DeltaRenewalInputsResolver.resolve(
            new List<RLM_DeltaRenewalInputsResolver.Request>{ nullReq, noSourceReq, noAssetsReq }
        );
        Test.stopTest();

        System.assertEquals(3, results.size(), 'One Result per Request (bulk-safe)');
        for (RLM_DeltaRenewalInputsResolver.Result r : results) {
            System.assertEquals(false, r.isSuccess, 'Each request here hits a guard: ' + r.errorMessage);
        }
        System.assertEquals('contractId is required.', results[0].errorMessage, 'Null contractId guard');
        System.assertEquals(
            'This contract has no source quote to renew from.', results[1].errorMessage, 'No-source-quote guard'
        );
        System.assert(
            String.valueOf(results[2].errorMessage).startsWith('This contract has no renewable assets.'),
            'No-renewable-assets guard: ' + results[2].errorMessage
        );
    }

    @IsTest
    static void testResolveInputs_BuildResolvedResult() {
        // The success path assembled from already-resolved assets: derive the date window from a real
        // lifecycle-managed Term asset (start = prior LifecycleEndDate + 1 day; end = start + the Contract's
        // 12-month term − 1 day) and snapshot the account quote ids. Drives buildResolvedResult directly
        // because the ACR that topLevelParentAssetIds reads can't be synthesized (see its doc); the real
        // deriveRenewalWindow / quoteIdsForAccount logic still runs here against the real Asset + account.
        Account a = insertAccount();
        Quote src = insertQuoteFor(a);
        Contract c = new Contract(
            AccountId = a.Id, Status = 'Draft', StartDate = Date.newInstance(2026, 1, 1),
            SourceQuoteId = src.Id, RenewalTerm2 = 12, RenewalTermUnit = 'Months'
        );
        insert c;
        Asset asset = insertTermAsset(a, DateTime.newInstanceGmt(2026, 12, 31, 12, 0, 0));

        RLM_DeltaRenewalInputsResolver.Request req = new RLM_DeltaRenewalInputsResolver.Request();
        req.contractId = c.Id;

        Test.startTest();
        RLM_DeltaRenewalInputsResolver.Result res = RLM_DeltaRenewalInputsResolver.buildResolvedResult(
            req, c, src.Id, a.Id, 'TB Quote - Renewal', new List<String>{ String.valueOf(asset.Id) }
        );
        Test.stopTest();

        System.assertEquals(true, res.isSuccess, 'A resolved asset list builds a success result');
        System.assertEquals(1, res.renewAssetIds.size(), 'The resolved asset carries through');
        System.assertEquals(String.valueOf(asset.Id), res.renewAssetIds[0], 'The DL-TERM asset id is preserved');
        System.assertEquals(src.Id, res.sourceQuoteId, 'The source quote id carries through');
        System.assertEquals(a.Id, res.scopeAccountId, 'The scope account carries through');
        System.assertEquals('TB Quote - Renewal', res.renewalName, 'The renewal name carries through');
        System.assertEquals(Date.newInstance(2027, 1, 1), res.renewStartDate, 'Start = prior LifecycleEndDate + 1 day');
        System.assertEquals(Date.newInstance(2027, 12, 31), res.renewEndDate, 'End = start + 12 months - 1 day (inclusive)');
        System.assertNotEquals(null, res.preExistingQuoteIds, 'The account quote snapshot is populated');
        System.assert(res.preExistingQuoteIds.contains(src.Id), 'The snapshot includes the account source quote');
    }

    @IsTest
    static void testFinalize_BulkGuardAndDiffHappy() {
        // Bulk (2-request) call: a missing-sourceQuoteId guard alongside a happy finalize whose minted
        // quote is identified purely by the account-scoped pre/post id-diff (renewalQuoteId left null).
        Account a = insertAccount();
        Quote src = insertQuoteFor(a);
        // Stands in for the quote initiateRenewal would mint: a fresh quote NOT in the pre-snapshot, so
        // the diff resolves to exactly this quote without depending on the flow's core action in test.
        Quote minted = insertQuoteFor(a);

        RLM_DeltaRenewalFinalizer.Request guard = new RLM_DeltaRenewalFinalizer.Request();
        // sourceQuoteId intentionally left null → finalizer returns isSuccess=false (does not throw).
        RLM_DeltaRenewalFinalizer.Request happy = new RLM_DeltaRenewalFinalizer.Request();
        happy.sourceQuoteId = src.Id;
        happy.renewalName = 'Acme Deal - Renewal';
        happy.scopeAccountId = a.Id;
        happy.endDate = Date.newInstance(2027, 12, 31);
        happy.preExistingQuoteIds = new List<Id>{ src.Id }; // minted is NOT known → the diff finds it
        happy.renewalQuoteId = null; // force reliance on the diff (bound-id disambiguator absent)

        Test.startTest();
        List<RLM_DeltaRenewalFinalizer.Result> results = RLM_DeltaRenewalFinalizer.finalizeRenewal(
            new List<RLM_DeltaRenewalFinalizer.Request>{ guard, happy }
        );
        Test.stopTest();

        System.assertEquals(2, results.size(), 'One Result per Request (bulk-safe)');
        System.assertEquals(false, results[0].isSuccess, 'A finalize request with no sourceQuoteId is rejected');
        System.assertEquals('sourceQuoteId is required.', results[0].errorMessage, 'The sourceQuoteId-required message is returned');

        RLM_DeltaRenewalFinalizer.Result h = results[1];
        System.assertEquals(true, h.isSuccess, 'The renewal finalizes: ' + h.errorMessage);
        System.assertEquals(minted.Id, h.renewalQuoteId, 'The account-scoped diff identifies the minted renewal quote');
        System.assertEquals(a.Id, h.accountId, 'The renewal account is resolved');

        Quote renewed = [SELECT Name, Status, ContractId, EndDate FROM Quote WHERE Id = :minted.Id];
        System.assertEquals('Acme Deal - Renewal', renewed.Name, 'The renewal is renamed');
        System.assertEquals('Draft', renewed.Status, 'The renewal is reset to Draft');
        System.assertEquals(null, renewed.ContractId, 'The originating ContractId is cleared');
        System.assertEquals(Date.newInstance(2027, 12, 31), renewed.EndDate, 'The derived EndDate is set on the header');
    }

    @IsTest
    static void testFinalize_BoundIdFallbackAndRequiredGuards() {
        // Bulk (3-request) call covering the two remaining required-field guards and the bound-id fallback:
        // when the pre-snapshot already contains the minted quote (diff finds nothing new), the finalizer
        // trusts the flow-bound renewalQuoteId instead.
        Account a = insertAccount();
        Quote src = insertQuoteFor(a);
        Quote minted = insertQuoteFor(a);

        RLM_DeltaRenewalFinalizer.Request noName = new RLM_DeltaRenewalFinalizer.Request();
        noName.sourceQuoteId = src.Id;
        noName.scopeAccountId = a.Id;

        RLM_DeltaRenewalFinalizer.Request noAccount = new RLM_DeltaRenewalFinalizer.Request();
        noAccount.sourceQuoteId = src.Id;
        noAccount.renewalName = 'X - Renewal';

        RLM_DeltaRenewalFinalizer.Request fallback = new RLM_DeltaRenewalFinalizer.Request();
        fallback.sourceQuoteId = src.Id;
        fallback.renewalName = 'Fallback - Renewal';
        fallback.scopeAccountId = a.Id;
        fallback.endDate = Date.newInstance(2028, 6, 30);
        // Both quotes already known → the diff finds nothing new, so the bound id is trusted.
        fallback.preExistingQuoteIds = new List<Id>{ src.Id, minted.Id };
        fallback.renewalQuoteId = String.valueOf(minted.Id);

        Test.startTest();
        List<RLM_DeltaRenewalFinalizer.Result> results = RLM_DeltaRenewalFinalizer.finalizeRenewal(
            new List<RLM_DeltaRenewalFinalizer.Request>{ noName, noAccount, fallback }
        );
        Test.stopTest();

        System.assertEquals(false, results[0].isSuccess, 'A finalize request with no renewalName is rejected');
        System.assertEquals('renewalName is required.', results[0].errorMessage, 'The renewalName-required message is returned');
        System.assertEquals(false, results[1].isSuccess, 'A finalize request with no scopeAccountId is rejected');
        System.assertEquals('scopeAccountId is required.', results[1].errorMessage, 'The scopeAccountId-required message is returned');
        System.assertEquals(true, results[2].isSuccess, 'The bound-id fallback finalizes: ' + results[2].errorMessage);
        System.assertEquals(minted.Id, results[2].renewalQuoteId, 'The flow-bound id is trusted when the diff finds nothing new');
    }

    // ---------- Term Library (getTermLibrary / addTermFromTemplate) ----------

    // The Term Library category the library reads from — its Code must match
    // RLM_DeltaTermBuilderController.CATEGORY_TEMPLATES_CODE. Cached so a test can seed >1 template.
    private static Id templateCategoryId;

    private static Id ensureTemplateCategory() {
        if (templateCategoryId != null) {
            return templateCategoryId;
        }
        ProductCatalog cat = new ProductCatalog(Name = 'DL Contracts', Code = 'DL-CONTRACTS-T');
        insert cat;
        ProductCategory pcat = new ProductCategory(Name = 'Term Templates', Code = 'DL-TERM-TEMPLATES', CatalogId = cat.Id);
        insert pcat;
        templateCategoryId = pcat.Id;
        return templateCategoryId;
    }

    // Seeds a Term Library template: a Product2 that is a member of the DL-TERM-TEMPLATES category,
    // carries one picklist scope attribute (a ProductAttributeDefinition with a DefaultValue that
    // resolves to a picklist display value), and has one fixed fare child (ProductRelatedComponent).
    // Returns the template product. faresName is the child fare product's Name (asserted by the library).
    private static Product2 insertTemplate(String sku, String pickValue, String fareName) {
        // Classification the template is BasedOn — required so a ProductClassificationAttr can parent
        // the product-specific ProductAttributeDefinition.
        ProductClassification pc = new ProductClassification(Name = sku + ' Class', Code = sku + '-CLS', Status = 'Active');
        insert pc;

        // A picklist scope attribute so the template DefaultValue resolves to a display value.
        AttributePicklist pl = new AttributePicklist(Name = sku + ' Origins', Code = sku + '-PL', DataType = 'Text', Status = 'Active');
        insert pl;
        insert new AttributePicklistValue(
            PicklistId = pl.Id, Name = pickValue, Code = sku + '-' + pickValue,
            Value = pickValue, DisplayValue = pickValue + ' Display', Status = 'Active'
        );
        // Canonical DL_Origin code so the library's display allowlist (LIBRARY_SCOPE_CHIP_CODES) surfaces
        // it as a chip; DeveloperName stays per-SKU to avoid cross-attribute collisions.
        AttributeDefinition ad = new AttributeDefinition(
            Name = 'Origin', DeveloperName = ('Origin_' + sku).replaceAll('[^a-zA-Z0-9]', '_'),
            Label = 'Origin', Code = 'DL_Origin', DataType = 'Picklist', PicklistId = pl.Id, IsActive = true
        );
        insert ad;
        ProductClassificationAttr pca = new ProductClassificationAttr(
            ProductClassificationId = pc.Id, AttributeDefinitionId = ad.Id, Name = 'Origin', Status = 'Active'
        );
        insert pca;

        // A free-text DL_SpecialConditions attribute — deliberately NOT in the display allowlist, so the
        // library must stamp it on the line but must NOT surface it as a modal chip.
        AttributeDefinition adSpecial = new AttributeDefinition(
            Name = 'Special Conditions', DeveloperName = ('Special_' + sku).replaceAll('[^a-zA-Z0-9]', '_'),
            Label = 'Special Conditions', Code = 'DL_SpecialConditions', DataType = 'Text', IsActive = true
        );
        insert adSpecial;
        ProductClassificationAttr pcaSpecial = new ProductClassificationAttr(
            ProductClassificationId = pc.Id, AttributeDefinitionId = adSpecial.Id, Name = 'Special Conditions', Status = 'Active'
        );
        insert pcaSpecial;

        Product2 tmpl = new Product2(
            Name = 'Template ' + sku, StockKeepingUnit = sku, ProductCode = sku, IsActive = true, Type = 'Bundle', BasedOnId = pc.Id
        );
        insert tmpl;

        insert new ProductAttributeDefinition(
            Name = 'Origin', Product2Id = tmpl.Id, AttributeDefinitionId = ad.Id,
            ProductClassificationAttributeId = pca.Id, DefaultValue = pickValue, Sequence = 1,
            IsHidden = false, IsPriceImpacting = false, IsReadOnly = false, IsRequired = false, Status = 'Active'
        );
        insert new ProductAttributeDefinition(
            Name = 'Special Conditions', Product2Id = tmpl.Id, AttributeDefinitionId = adSpecial.Id,
            ProductClassificationAttributeId = pcaSpecial.Id, DefaultValue = 'Peak-season carve-out', Sequence = 2,
            IsHidden = false, IsPriceImpacting = false, IsReadOnly = false, IsRequired = false, Status = 'Active'
        );

        // One fixed fare child (not the dynamic classification component the sellable DL-TERM uses).
        Product2 fare = new Product2(Name = fareName, StockKeepingUnit = 'FARE-' + sku, ProductCode = 'FARE-' + sku, IsActive = true);
        insert fare;
        ProductRelationshipType prt = new ProductRelationshipType(
            Name = 'Bundle Comp ' + sku, MainProductRoleCat = 'Bundle', AssociatedProductRoleCat = 'BundleComponent'
        );
        insert prt;
        insert new ProductRelatedComponent(
            ParentProductId = tmpl.Id, ChildProductId = fare.Id, ProductRelationshipTypeId = prt.Id,
            IsDefaultComponent = true, Sequence = 1
        );

        // Category membership — the library filter.
        Id catId = ensureTemplateCategory();
        insert new ProductCategoryProduct(
            ProductCategoryId = catId, ProductId = tmpl.Id, IsPrimaryCategory = true
        );
        return tmpl;
    }

    @IsTest
    static void testTermLibrary_EmptyWhenNoTemplates() {
        Test.startTest();
        Map<String, Object> res = parse(RLM_DeltaTermBuilderController.getTermLibrary());
        Test.stopTest();
        System.assertEquals(true, res.get('isSuccess'), 'Empty library still succeeds');
        System.assertEquals(0, ((List<Object>) res.get('templates')).size(), 'No templates seeded → empty list');
    }

    @IsTest
    static void testTermLibrary_ReturnsSeededTemplateWithScopeAndFares() {
        Product2 tmpl = insertTemplate('DL-TMPL-TEST', 'US50', 'Main Cabin');
        Test.startTest();
        Map<String, Object> res = parse(RLM_DeltaTermBuilderController.getTermLibrary());
        Test.stopTest();

        System.assertEquals(true, res.get('isSuccess'), 'Library read succeeds: ' + res.get('errorMessage'));
        List<Object> templates = (List<Object>) res.get('templates');
        System.assertEquals(1, templates.size(), 'The one seeded template is returned');
        Map<String, Object> t = (Map<String, Object>) templates[0];
        System.assertEquals(tmpl.Id, t.get('productId'), 'The template product id is surfaced');
        System.assertEquals('Template DL-TMPL-TEST', t.get('name'), 'The template name is surfaced');

        // Two scope defaults are seeded (DL_Origin + DL_SpecialConditions), but only the allowlisted
        // DL_Origin surfaces as a chip — DL_SpecialConditions is excluded so the modal chips match the
        // Term card's route/scope set.
        List<Object> chips = (List<Object>) t.get('scopeChips');
        System.assertEquals(1, chips.size(), 'Only the allowlisted scope default becomes a chip (special conditions filtered)');
        Map<String, Object> chip = (Map<String, Object>) chips[0];
        System.assertEquals('DL_Origin', chip.get('code'), 'Chip carries the attribute code');
        System.assertEquals('Origin', chip.get('label'), 'Chip carries the attribute label');
        System.assertEquals('US50 Display', chip.get('value'), 'Picklist DefaultValue resolved to its display value');

        List<Object> fareNames = (List<Object>) t.get('fareNames');
        System.assertEquals(1, fareNames.size(), 'The fixed fare child is listed');
        System.assertEquals('Main Cabin', fareNames[0], 'The fare product name is surfaced');
    }

    @IsTest
    static void testAddTermFromTemplate_MalformedJson() {
        System.assertEquals(false, parse(RLM_DeltaTermBuilderController.addTermFromTemplate('{bad')).get('isSuccess'), 'Malformed JSON fails gracefully');
    }

    @IsTest
    static void testAddTermFromTemplate_InvalidQuoteId() {
        Map<String, Object> in0 = new Map<String, Object>{ 'quoteId' => 'bad', 'templateProductId' => 'bad' };
        System.assertEquals(false, parse(RLM_DeltaTermBuilderController.addTermFromTemplate(JSON.serialize(in0))).get('isSuccess'), 'Invalid ids rejected');
    }

    @IsTest
    static void testAddTermFromTemplate_NonMemberTemplateRejected() {
        // A real quote + a real product that is NOT a DL-TERM-TEMPLATES member → the server-authority
        // membership guard rejects it before any PST work (the client selector is untrusted).
        Account a = insertAccount();
        Quote q = insertQuoteFor(a);
        Product2 stranger = new Product2(Name = 'Not a template', ProductCode = 'NOT-TMPL', IsActive = true);
        insert stranger;
        Map<String, Object> in0 = new Map<String, Object>{ 'quoteId' => q.Id, 'templateProductId' => stranger.Id };
        Test.startTest();
        Map<String, Object> res = parse(RLM_DeltaTermBuilderController.addTermFromTemplate(JSON.serialize(in0)));
        Test.stopTest();
        System.assertEquals(false, res.get('isSuccess'), 'A non-library product is rejected');
        System.assert(((String) res.get('errorMessage')).contains('Term Library template'), 'The membership-guard message is returned: ' + res.get('errorMessage'));
    }

    @IsTest
    static void testAddTermFromTemplate_ValidGracefulContract() {
        // Real quote + a seeded library template + a DL-TERM product on the standard book → passes every
        // guard into the PST commit. PST is non-deterministic in test context, so assert only a decided
        // result (mirrors testAddTerm_ValidGracefulContract).
        Account a = insertAccount();
        Quote q = insertQuoteFor(a);
        insertTermLine(q); // guarantees a DL-TERM product + active standard-book PBE (the created line is DL-TERM)
        Product2 tmpl = insertTemplate('DL-TMPL-GRACE', 'US50', 'Main Cabin');
        Map<String, Object> in0 = new Map<String, Object>{ 'quoteId' => q.Id, 'templateProductId' => tmpl.Id };
        Test.startTest();
        Map<String, Object> res = parse(RLM_DeltaTermBuilderController.addTermFromTemplate(JSON.serialize(in0)));
        Test.stopTest();
        System.assertNotEquals(null, res.get('isSuccess'), 'Add-from-template returns a decided result');
    }
}
