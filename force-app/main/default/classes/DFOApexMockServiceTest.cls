@IsTest
private class DFOApexMockServiceTest {

    @IsTest
    static void providerDeclaresTheBillingNamedCredential() {
        List<industriesintegrationfwk.ApexProviderAttr> attrs = DFOApexMockService.getProviderAttributes();

        Assert.areEqual(1, attrs.size(), 'Only the named credential attribute is declared');
        Map<String, Object> attr = (Map<String, Object>) JSON.deserializeUntyped(JSON.serialize(attrs[0]));
        Assert.areEqual('Named_Credential', attr.get('developerName'), 'The attribute is the named credential');
        Assert.areEqual('BillingSystemNC', attr.get('defaultValue'), 'It defaults to the billing named credential');
        Assert.areEqual(true, attr.get('isRequired'), 'The named credential is required');
    }

    @IsTest
    static void nullHttpProviderFailsBeforeAnyResponse() {
        // The request goes through the supplied industriesintegrationfwk.HttpBaseProvider, never
        // Http directly. That provider cannot be subclassed, and its callout ignores Test.setMock,
        // so a test can only show that the provider argument is the one used.
        try {
            DFOApexMockService.executeCallout('guid-1', 'record-1', 'payload-1', new Map<String, Object>(), null);
            Assert.fail('Without an HTTP provider no response can be returned');
        } catch (NullPointerException e) {
            Assert.isTrue(
                e.getMessage().contains('de-reference a null object'),
                'The missing provider is dereferenced: ' + e.getMessage()
            );
        }
    }
}
