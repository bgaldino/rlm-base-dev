/**
 * Not covered: the response executeCallout returns (success flag set, response code 500). The call
 * goes through the framework's HttpBaseProvider, which cannot be subclassed and whose callout
 * ignores Test.setMock, so no test can get past the send.
 */
@IsTest
private class DFOApexMockServiceTest {

    @IsTest
    static void providerDeclaresTheBillingNamedCredential() {
        List<industriesintegrationfwk.ApexProviderAttr> attrs = DFOApexMockService.getProviderAttributes();

        Assert.areEqual(1, attrs.size(), 'Only the named credential attribute is declared');
        industriesintegrationfwk.ApexProviderAttr attr = attrs[0];
        Assert.areEqual('Named_Credential', attr.getDeveloperName(), 'The attribute is the named credential');
        Assert.areEqual('BillingSystemNC', attr.getDefaultValue(), 'It defaults to the billing named credential');
        Assert.isTrue(attr.getIsRequired(), 'The named credential is required');
    }

    @IsTest
    static void nullHttpProviderFailsBeforeAnyResponse() {
        // The request goes through the supplied industriesintegrationfwk.HttpBaseProvider, never
        // Http directly. That provider cannot be subclassed, and its callout ignores Test.setMock,
        // so a test can only show that the provider argument is the one used.
        try {
            DFOApexMockService.executeCallout('guid-1', 'record-1', 'payload-1', new Map<String, Object>(), null);
            Assert.fail('Without an HTTP provider no response can be returned');
        } catch (Exception e) {
            Assert.isInstanceOfType(e, NullPointerException.class, 'The missing provider is dereferenced. Got: ' + e);
        }
    }
}
