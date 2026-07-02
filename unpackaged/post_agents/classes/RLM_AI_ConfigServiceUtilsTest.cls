@isTest
private class RLM_AI_ConfigServiceUtilsTest {

    @isTest
    static void toIdOrNullParsesValidIdAndRejectsOthers() {
        Account a = new Account(Name = 'RLM Utils Test');
        insert a;

        System.assertEquals(a.Id, RLM_AI_ConfigServiceUtils.toIdOrNull(String.valueOf(a.Id)));
        System.assertEquals(a.Id, RLM_AI_ConfigServiceUtils.toIdOrNull('  ' + a.Id + '  '),
            'Leading/trailing whitespace should be trimmed.');
        System.assertEquals(null, RLM_AI_ConfigServiceUtils.toIdOrNull('not-an-id'));
        System.assertEquals(null, RLM_AI_ConfigServiceUtils.toIdOrNull(null));
        System.assertEquals(null, RLM_AI_ConfigServiceUtils.toIdOrNull('   '));
    }

    @isTest
    static void hasPrefixMatchesKeyPrefix() {
        Account a = new Account(Name = 'RLM Utils Prefix');
        insert a;
        String acctPrefix = String.valueOf(a.Id).substring(0, 3);

        System.assertEquals(true, RLM_AI_ConfigServiceUtils.hasPrefix(String.valueOf(a.Id), acctPrefix));
        System.assertEquals(false, RLM_AI_ConfigServiceUtils.hasPrefix(String.valueOf(a.Id), '0Q0'));
        System.assertEquals(false, RLM_AI_ConfigServiceUtils.hasPrefix('not-an-id', acctPrefix));
        System.assertEquals(false, RLM_AI_ConfigServiceUtils.hasPrefix(String.valueOf(a.Id), null));
    }

    @isTest
    static void validateIdReturnsIdOrThrows() {
        Account a = new Account(Name = 'RLM Utils Validate');
        insert a;
        String acctPrefix = String.valueOf(a.Id).substring(0, 3);

        System.assertEquals(a.Id,
            RLM_AI_ConfigServiceUtils.validateId(String.valueOf(a.Id), acctPrefix, 'account Id'));

        // No prefix constraint — any valid Id passes.
        System.assertEquals(a.Id,
            RLM_AI_ConfigServiceUtils.validateId(String.valueOf(a.Id), null, 'account Id'));

        try {
            RLM_AI_ConfigServiceUtils.validateId('not-an-id', acctPrefix, 'account Id');
            System.assert(false, 'Expected IllegalArgumentException for invalid Id.');
        } catch (IllegalArgumentException e) {
            System.assert(e.getMessage().contains('account Id'));
        }

        try {
            RLM_AI_ConfigServiceUtils.validateId(String.valueOf(a.Id), '0QL', 'quote line item Id');
            System.assert(false, 'Expected IllegalArgumentException for wrong prefix.');
        } catch (IllegalArgumentException e) {
            System.assert(e.getMessage().contains('quote line item Id'));
        }
    }

    @isTest
    static void safeSerializeHandlesNullAndValues() {
        System.assertEquals(null, RLM_AI_ConfigServiceUtils.safeSerialize(null));
        System.assertEquals('[]', RLM_AI_ConfigServiceUtils.safeSerialize(new List<String>()));
        System.assertEquals('{"a":1}',
            RLM_AI_ConfigServiceUtils.safeSerialize(new Map<String, Object>{ 'a' => 1 }));
    }

    @isTest
    static void safeDeserializeMapHandlesBlankAndJson() {
        System.assertEquals(0, RLM_AI_ConfigServiceUtils.safeDeserializeMap(null).size());
        System.assertEquals(0, RLM_AI_ConfigServiceUtils.safeDeserializeMap('   ').size());

        Map<String, Object> parsed =
            RLM_AI_ConfigServiceUtils.safeDeserializeMap('{"key":"value"}');
        System.assertEquals('value', parsed.get('key'));

        try {
            RLM_AI_ConfigServiceUtils.safeDeserializeMap('{bad json');
            System.assert(false, 'Expected a JSON exception for malformed input.');
        } catch (Exception e) {
            // expected — callers map this to a parse error
        }
    }

    @isTest
    static void escapeLikeTermEscapesWildcards() {
        System.assertEquals('', RLM_AI_ConfigServiceUtils.escapeLikeTerm(null));
        System.assertEquals('100\\% Pure', RLM_AI_ConfigServiceUtils.escapeLikeTerm('100% Pure'));
        System.assertEquals('a\\_b', RLM_AI_ConfigServiceUtils.escapeLikeTerm('a_b'));
        System.assertEquals('a\\\\b', RLM_AI_ConfigServiceUtils.escapeLikeTerm('a\\b'));
    }

    // ---- Tokenized product name matching tests ----

    @isTest
    static void extractTokensSplitsOnWhitePunctuation() {
        List<String> tokens = RLM_AI_ConfigServiceUtils.extractTokens('QB API-Management: Solution!');
        System.assertEquals(4, tokens.size());
        System.assertEquals('qb', tokens[0]);
        System.assertEquals('api', tokens[1]);
        System.assertEquals('management', tokens[2]);
        System.assertEquals('solution', tokens[3]);
    }

    @isTest
    static void extractTokensHandlesBlank() {
        System.assertEquals(0, RLM_AI_ConfigServiceUtils.extractTokens(null).size());
        System.assertEquals(0, RLM_AI_ConfigServiceUtils.extractTokens('   ').size());
    }

    @isTest
    static void productNameMatchesExactCase() {
        System.assertEquals(true,
            RLM_AI_ConfigServiceUtils.productNameMatchesTokens('QB API Management', 'QB API Management'));
        System.assertEquals(true,
            RLM_AI_ConfigServiceUtils.productNameMatchesTokens('QB API Management', 'qb api management'));
    }

    @isTest
    static void productNameMatchesMissingTrailing() {
        System.assertEquals(true,
            RLM_AI_ConfigServiceUtils.productNameMatchesTokens(
                'QB API Management Solution', 'QB API Management'
            ),
            'All search tokens present in product name');
    }

    @isTest
    static void productNameMatchesReordered() {
        System.assertEquals(true,
            RLM_AI_ConfigServiceUtils.productNameMatchesTokens(
                'API Management QB', 'QB Management'
            ),
            'Token order should not matter');
    }

    @isTest
    static void productNameMatchesSingleToken() {
        System.assertEquals(true,
            RLM_AI_ConfigServiceUtils.productNameMatchesTokens(
                'Additional API Product', 'API'
            ),
            'Single token substring match');
    }

    @isTest
    static void productNameMatchFailsMissingToken() {
        System.assertEquals(false,
            RLM_AI_ConfigServiceUtils.productNameMatchesTokens(
                'QB Management Solution', 'QB API Management'
            ),
            'Missing API token should fail');
    }

    @isTest
    static void productNameMatchFailsBlankInput() {
        System.assertEquals(false,
            RLM_AI_ConfigServiceUtils.productNameMatchesTokens('Product', ''));
        System.assertEquals(false,
            RLM_AI_ConfigServiceUtils.productNameMatchesTokens('', 'search'));
        System.assertEquals(false,
            RLM_AI_ConfigServiceUtils.productNameMatchesTokens(null, 'search'));
        System.assertEquals(false,
            RLM_AI_ConfigServiceUtils.productNameMatchesTokens('Product', null));
    }

    @isTest
    static void matchLinesByProductNameFiltersByToken() {
        Account acct = new Account(Name = 'RLM Utils Match Account');
        insert acct;

        Opportunity opp = new Opportunity(
            Name = 'RLM Utils Match Opportunity',
            AccountId = acct.Id,
            StageName = 'Prospecting',
            CloseDate = Date.today().addDays(30)
        );
        insert opp;

        Id standardPbId = Test.getStandardPricebookId();
        Quote q = new Quote(
            Name = 'RLM Utils Match Quote',
            OpportunityId = opp.Id,
            Pricebook2Id = standardPbId,
            Status = 'Draft'
        );
        insert q;

        Product2 p1 = new Product2(Name = 'QB API Management Solution', IsActive = true);
        Product2 p2 = new Product2(Name = 'QB Server Standard', IsActive = true);
        Product2 p3 = new Product2(Name = 'Quinn Cable', IsActive = true);
        insert new List<Product2>{ p1, p2, p3 };

        PricebookEntry pbe1 = new PricebookEntry(
            Pricebook2Id = standardPbId, Product2Id = p1.Id, UnitPrice = 100, IsActive = true
        );
        PricebookEntry pbe2 = new PricebookEntry(
            Pricebook2Id = standardPbId, Product2Id = p2.Id, UnitPrice = 200, IsActive = true
        );
        PricebookEntry pbe3 = new PricebookEntry(
            Pricebook2Id = standardPbId, Product2Id = p3.Id, UnitPrice = 50, IsActive = true
        );
        insert new List<PricebookEntry>{ pbe1, pbe2, pbe3 };

        QuoteLineItem qli1 = new QuoteLineItem(
            QuoteId = q.Id, PricebookEntryId = pbe1.Id, Quantity = 1, UnitPrice = 100
        );
        QuoteLineItem qli2 = new QuoteLineItem(
            QuoteId = q.Id, PricebookEntryId = pbe2.Id, Quantity = 2, UnitPrice = 200
        );
        QuoteLineItem qli3 = new QuoteLineItem(
            QuoteId = q.Id, PricebookEntryId = pbe3.Id, Quantity = 3, UnitPrice = 50
        );
        insert new List<QuoteLineItem>{ qli1, qli2, qli3 };

        Test.startTest();
        List<QuoteLineItem> matches = RLM_AI_ConfigServiceUtils.matchLinesByProductName(
            q.Id, 'QB API Management'
        );
        Test.stopTest();

        System.assertEquals(1, matches.size(),
            'Only QB API Management Solution should match');
        System.assertEquals(p1.Id, matches[0].Product2Id);
    }

    @isTest
    static void matchLinesByProductNameReturnsEmpty() {
        Account acct = new Account(Name = 'RLM Utils Empty Account');
        insert acct;

        Opportunity opp = new Opportunity(
            Name = 'RLM Utils Empty Opportunity',
            AccountId = acct.Id,
            StageName = 'Prospecting',
            CloseDate = Date.today().addDays(30)
        );
        insert opp;

        Quote q = new Quote(
            Name = 'RLM Utils Empty Quote',
            OpportunityId = opp.Id,
            Pricebook2Id = Test.getStandardPricebookId(),
            Status = 'Draft'
        );
        insert q;

        System.assertEquals(0,
            RLM_AI_ConfigServiceUtils.matchLinesByProductName(q.Id, '').size(),
            'Blank search should return empty');
        System.assertEquals(0,
            RLM_AI_ConfigServiceUtils.matchLinesByProductName(q.Id, 'NoMatch').size(),
            'No match should return empty');
    }

    // ---- productNameScore ----

    @isTest
    static void productNameScoreExactIs100() {
        System.assertEquals(100,
            RLM_AI_ConfigServiceUtils.productNameScore('QuantumBit Complete Solution',
                'quantumbit complete solution'),
            'Exact normalized match scores 100');
    }

    @isTest
    static void productNameScoreNoiseWordIs90() {
        // The live failure: user typed a trailing "bundle" not in the catalog name.
        // Every NAME token is in the search term, so search is a superset -> 90.
        System.assertEquals(90,
            RLM_AI_ConfigServiceUtils.productNameScore('QuantumBit Complete Solution',
                'quantumbit complete solution bundle'),
            'Search superset of name (noise word) scores 90');
    }

    @isTest
    static void productNameScoreContainsAllIs85() {
        // Every SEARCH token is in the name, but the name has an EXTRA token
        // (Premium) not in the search, so it is not a name-subset-of-search
        // (90) case -> classic contains-all = 85.
        System.assertEquals(85,
            RLM_AI_ConfigServiceUtils.productNameScore('QuantumBit Complete Solution Premium',
                'complete solution quantumbit'),
            'All search tokens present in a larger name scores 85');
    }

    @isTest
    static void productNameScorePartialIsBetween1And80() {
        Integer score = RLM_AI_ConfigServiceUtils.productNameScore(
            'QuantumBit Complete Solution', 'quantumbit widget gadget');
        System.assert(score > 0 && score < 85,
            'Partial overlap (1 of 3 search tokens) scores in the partial band, was ' + score);
    }

    @isTest
    static void productNameScoreNoOverlapIsZero() {
        System.assertEquals(0,
            RLM_AI_ConfigServiceUtils.productNameScore('QuantumBit Complete Solution',
                'totally unrelated widget'),
            'No token overlap scores 0');
        System.assertEquals(0,
            RLM_AI_ConfigServiceUtils.productNameScore('', 'anything'));
        System.assertEquals(0,
            RLM_AI_ConfigServiceUtils.productNameScore('Product', ''));
    }

    // ---- matchProductsByName ----

    @isTest
    static void matchProductsByNameRanksNoiseWordSearch() {
        Product2 p1 = new Product2(Name = 'QuantumBit Complete Solution', ProductCode = 'QB-CS', IsActive = true);
        Product2 p2 = new Product2(Name = 'QuantumBit Server Standard', ProductCode = 'QB-SS', IsActive = true);
        Product2 p3 = new Product2(Name = 'Unrelated Widget', ProductCode = 'UW', IsActive = true);
        Product2 inactive = new Product2(Name = 'QuantumBit Complete Solution Legacy', IsActive = false);
        insert new List<Product2>{ p1, p2, p3, inactive };

        Test.startTest();
        List<RLM_AI_ConfigServiceUtils.ScoredProduct> ranked =
            RLM_AI_ConfigServiceUtils.matchProductsByName('quantumbit complete solution bundle', 200);
        Test.stopTest();

        System.assert(!ranked.isEmpty(), 'Should match on shared tokens');
        System.assertEquals(p1.Id, ranked[0].product.Id,
            'Complete Solution should rank first for a noise-word superset search');
        System.assert(ranked[0].score >= 85,
            'Top match should be high-confidence, was ' + ranked[0].score);
        // Inactive product must never appear.
        for (RLM_AI_ConfigServiceUtils.ScoredProduct sp : ranked) {
            System.assertNotEquals(inactive.Id, sp.product.Id,
                'Inactive products must be excluded');
        }
    }

    @isTest
    static void matchProductsByNameBlankAndNoMatch() {
        Product2 p = new Product2(Name = 'QuantumBit Complete Solution', IsActive = true);
        insert p;
        System.assertEquals(0,
            RLM_AI_ConfigServiceUtils.matchProductsByName('', 200).size(),
            'Blank search returns empty');
        System.assertEquals(0,
            RLM_AI_ConfigServiceUtils.matchProductsByName('zzqqx nonexistent token', 200).size(),
            'No-overlap search returns empty');
    }

    @isTest
    static void matchProductsByNameRespectsLimit() {
        List<Product2> prods = new List<Product2>();
        for (Integer i = 0; i < 5; i++) {
            prods.add(new Product2(Name = 'Shared Token Product ' + i, IsActive = true));
        }
        insert prods;

        Test.startTest();
        List<RLM_AI_ConfigServiceUtils.ScoredProduct> ranked =
            RLM_AI_ConfigServiceUtils.matchProductsByName('shared token product', 2);
        Test.stopTest();

        System.assertEquals(2, ranked.size(), 'Result count is capped at limitCount');
    }

    // ---- classifyScores (shared single-vs-ambiguous decision) ----

    @isTest
    static void classifyScoresCoversEachOutcome() {
        System.assertEquals(RLM_AI_ConfigServiceUtils.MatchResolution.NONE,
            RLM_AI_ConfigServiceUtils.classifyScores(new List<Integer>()),
            'Empty -> NONE');
        System.assertEquals(RLM_AI_ConfigServiceUtils.MatchResolution.NONE,
            RLM_AI_ConfigServiceUtils.classifyScores(null),
            'Null -> NONE');
        System.assertEquals(RLM_AI_ConfigServiceUtils.MatchResolution.SINGLE,
            RLM_AI_ConfigServiceUtils.classifyScores(new List<Integer>{ 90 }),
            'One candidate -> SINGLE');
        System.assertEquals(RLM_AI_ConfigServiceUtils.MatchResolution.SINGLE,
            RLM_AI_ConfigServiceUtils.classifyScores(new List<Integer>{ 100, 85 }),
            'Unique exact -> SINGLE');
        System.assertEquals(RLM_AI_ConfigServiceUtils.MatchResolution.SINGLE,
            RLM_AI_ConfigServiceUtils.classifyScores(new List<Integer>{ 90, 60 }),
            'Dominant top (>=85, lead >=10) -> SINGLE');
        System.assertEquals(RLM_AI_ConfigServiceUtils.MatchResolution.AMBIGUOUS,
            RLM_AI_ConfigServiceUtils.classifyScores(new List<Integer>{ 90, 85 }),
            'Two close high matches -> AMBIGUOUS');
        System.assertEquals(RLM_AI_ConfigServiceUtils.MatchResolution.AMBIGUOUS,
            RLM_AI_ConfigServiceUtils.classifyScores(new List<Integer>{ 100, 100 }),
            'Two exact matches -> AMBIGUOUS');
    }

    // ---- matchLinesByProductName: now uses the SAME scored engine as products ----

    @isTest
    static void matchLinesByProductNameToleratesNoiseWord() {
        // The consistency fix: a trailing noise word ("bundle") that is not in
        // the catalog name must still resolve the line, just like product search.
        QuoteFixture qf = buildQuoteWithLines(new List<String>{
            'QuantumBit Complete Solution', 'QuantumBit Server Standard'
        });

        Test.startTest();
        List<QuoteLineItem> matches = RLM_AI_ConfigServiceUtils.matchLinesByProductName(
            qf.quoteId, 'quantumbit complete solution bundle'
        );
        Test.stopTest();

        System.assertEquals(1, matches.size(),
            'Noise-word search should resolve to the single Complete Solution line');
        System.assertEquals(qf.productIds[0], matches[0].Product2Id);
    }

    @isTest
    static void matchLinesByProductNameDisambiguatesCloseMatches() {
        // Two lines whose names both fully contain the search term, neither exact
        // -> AMBIGUOUS -> both returned so the caller can disambiguate.
        QuoteFixture qf = buildQuoteWithLines(new List<String>{
            'QuantumBit Server Standard', 'QuantumBit Server Premium'
        });

        Test.startTest();
        List<QuoteLineItem> matches = RLM_AI_ConfigServiceUtils.matchLinesByProductName(
            qf.quoteId, 'quantumbit server'
        );
        Test.stopTest();

        System.assertEquals(2, matches.size(),
            'Two equally-good server lines should both surface for disambiguation');
    }

    @isTest
    static void matchLinesByProductNameDropsWeakOverlap() {
        // A line sharing only a generic token must NOT match (below the floor).
        QuoteFixture qf = buildQuoteWithLines(new List<String>{
            'QuantumBit Complete Solution'
        });

        Test.startTest();
        List<QuoteLineItem> matches = RLM_AI_ConfigServiceUtils.matchLinesByProductName(
            qf.quoteId, 'totally different solution'
        );
        Test.stopTest();

        System.assertEquals(0, matches.size(),
            'Sharing only the generic token "solution" is below the confidence floor');
    }

    // ---- shared quote/line fixture ----

    private class QuoteFixture {
        Id quoteId;
        List<Id> productIds = new List<Id>();
    }

    private static QuoteFixture buildQuoteWithLines(List<String> productNames) {
        Account acct = new Account(Name = 'RLM Line Match Account');
        insert acct;
        Opportunity opp = new Opportunity(
            Name = 'RLM Line Match Opportunity',
            AccountId = acct.Id,
            StageName = 'Prospecting',
            CloseDate = Date.today().addDays(30)
        );
        insert opp;
        Id standardPbId = Test.getStandardPricebookId();
        Quote q = new Quote(
            Name = 'RLM Line Match Quote',
            OpportunityId = opp.Id,
            Pricebook2Id = standardPbId,
            Status = 'Draft'
        );
        insert q;

        QuoteFixture qf = new QuoteFixture();
        List<Product2> prods = new List<Product2>();
        for (String n : productNames) {
            prods.add(new Product2(Name = n, IsActive = true));
        }
        insert prods;

        List<PricebookEntry> pbes = new List<PricebookEntry>();
        for (Product2 p : prods) {
            pbes.add(new PricebookEntry(
                Pricebook2Id = standardPbId, Product2Id = p.Id, UnitPrice = 100, IsActive = true
            ));
            qf.productIds.add(p.Id);
        }
        insert pbes;

        List<QuoteLineItem> qlis = new List<QuoteLineItem>();
        for (PricebookEntry pbe : pbes) {
            qlis.add(new QuoteLineItem(
                QuoteId = q.Id, PricebookEntryId = pbe.Id, Quantity = 1, UnitPrice = 100
            ));
        }
        insert qlis;

        qf.quoteId = q.Id;
        return qf;
    }
}
