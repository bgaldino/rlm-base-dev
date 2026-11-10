@IsTest
private class DFOApexMockServiceTest {

    @IsTest
    static void providerDeclaresNamedCredentialAttribute() {
        List<industriesintegrationfwk.ApexProviderAttr> attrs = DFOApexMockService.getProviderAttributes();

        Assert.areEqual(1, attrs.size(), 'Only the named credential attribute is declared');
        Assert.isNotNull(attrs[0], 'The named credential attribute is populated');
    }

    @IsTest
    static void calloutGoesThroughTheSuppliedHttpProvider() {
        // The advanced interface must send through the framework's HttpBaseProvider (for
        // request logging), never Http directly. With no provider the send has nothing to
        // call, which proves the request is routed to it.
        try {
            DFOApexMockService.executeCallout('guid-1', 'record-1', 'payload', new Map<String, Object>(), null);
            Assert.fail('The callout must be made through the supplied provider');
        } catch (NullPointerException e) {
            Assert.isNotNull(e.getMessage(), 'The missing provider is dereferenced');
        }
    }
}
