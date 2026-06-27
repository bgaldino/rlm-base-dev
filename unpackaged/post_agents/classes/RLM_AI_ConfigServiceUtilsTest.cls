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
}
