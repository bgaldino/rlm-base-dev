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
}
