@isTest
private class RLM_DeltaAttributeSetHashUtilTest {

    private static Id fakeId(Integer n) {
        String padded = String.valueOf(n).leftPad(15, '0');
        return Id.valueOf(padded + 'AAA');
    }

    @isTest
    static void testOrderIndependence() {
        QuoteLineItemAttribute a1 = new QuoteLineItemAttribute(
            AttributeDefinitionId = fakeId(1), AttributeValue = 'Red'
        );
        QuoteLineItemAttribute a2 = new QuoteLineItemAttribute(
            AttributeDefinitionId = fakeId(2), AttributePicklistValueId = fakeId(3)
        );

        String hashForward = RLM_DeltaAttributeSetHashUtil.computeHash(new List<QuoteLineItemAttribute>{ a1, a2 });
        String hashReverse = RLM_DeltaAttributeSetHashUtil.computeHash(new List<QuoteLineItemAttribute>{ a2, a1 });

        System.assertEquals(hashForward, hashReverse, 'Hash must be independent of input row order.');
    }

    @isTest
    static void testEmptySetUsesSentinel() {
        String expected = EncodingUtil.base64Encode(
            Crypto.generateDigest('SHA-256', Blob.valueOf(RLM_DeltaAttributeSetHashUtil.EMPTY_SET_SENTINEL))
        );

        String actual = RLM_DeltaAttributeSetHashUtil.computeHash(new List<QuoteLineItemAttribute>());

        System.assertEquals(expected, actual, 'Empty attribute list must hash the exact sentinel literal.');
        System.assertNotEquals(null, actual, 'Sentinel hash must never be null.');
    }

    @isTest
    static void testPicklistVsFreeTextDiscriminator() {
        Id sharedDefId = fakeId(1);
        Id picklistValueId = fakeId(2);
        String picklistValueIdAsString = String.valueOf(picklistValueId);

        QuoteLineItemAttribute picklistRow = new QuoteLineItemAttribute(
            AttributeDefinitionId = sharedDefId, AttributePicklistValueId = picklistValueId
        );
        QuoteLineItemAttribute freeTextRow = new QuoteLineItemAttribute(
            AttributeDefinitionId = sharedDefId, AttributeValue = picklistValueIdAsString
        );

        String picklistHash = RLM_DeltaAttributeSetHashUtil.computeHash(new List<QuoteLineItemAttribute>{ picklistRow });
        String freeTextHash = RLM_DeltaAttributeSetHashUtil.computeHash(new List<QuoteLineItemAttribute>{ freeTextRow });

        System.assertNotEquals(picklistHash, freeTextHash,
            'A picklist selection and a free-text value with the same characters must hash differently.');
    }

    @isTest
    static void testDelimiterCharactersInValueAreSafe() {
        QuoteLineItemAttribute withDelimiters = new QuoteLineItemAttribute(
            AttributeDefinitionId = fakeId(1), AttributeValue = 'Line1\nLine2:Extra'
        );
        QuoteLineItemAttribute plain = new QuoteLineItemAttribute(
            AttributeDefinitionId = fakeId(1), AttributeValue = 'Line1Line2Extra'
        );

        String hashWithDelimiters;
        try {
            hashWithDelimiters = RLM_DeltaAttributeSetHashUtil.computeHash(new List<QuoteLineItemAttribute>{ withDelimiters });
        } catch (Exception e) {
            System.assert(false, 'A value containing \\n or : must hash without throwing: ' + e.getMessage());
        }
        String hashPlain = RLM_DeltaAttributeSetHashUtil.computeHash(new List<QuoteLineItemAttribute>{ plain });

        System.assertNotEquals(hashWithDelimiters, hashPlain,
            'Length-prefixed serialization must distinguish values that differ only by delimiter characters.');
    }

    @isTest
    static void testPresentButBlankRowIsNotSkipped() {
        QuoteLineItemAttribute blankRow = new QuoteLineItemAttribute(
            AttributeDefinitionId = fakeId(1)
        );

        String hashBlankRow;
        try {
            hashBlankRow = RLM_DeltaAttributeSetHashUtil.computeHash(new List<QuoteLineItemAttribute>{ blankRow });
        } catch (Exception e) {
            System.assert(false, 'A present row with null AttributeValue/AttributePicklistValueId must not throw: ' + e.getMessage());
        }
        String sentinelHash = RLM_DeltaAttributeSetHashUtil.computeHash(new List<QuoteLineItemAttribute>());

        System.assertNotEquals(sentinelHash, hashBlankRow,
            'A present-but-blank row must hash differently from the zero-row sentinel.');
    }
}
