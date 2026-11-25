/**
 * The request goes through the framework's HttpBaseProvider, which cannot be subclassed and whose callout
 * ignores Test.setMock, so no test gets past the send in executeCallout. The response the step returns is
 * built by buildResponse, which the tests call directly.
 */
@IsTest
private class DFOApexMockServiceTest {

    @IsTest
    static void providerDeclaresTheNamedCredentialAndTheFailureToggle() {
        List<industriesintegrationfwk.ApexProviderAttr> attrs = DFOApexMockService.getProviderAttributes();

        Assert.areEqual(2, attrs.size(), 'The named credential and the failure toggle are declared');
        industriesintegrationfwk.ApexProviderAttr cred = attrs[0];
        Assert.areEqual('Named_Credential', cred.getDeveloperName(), 'The first attribute is the named credential');
        Assert.areEqual('BillingSystemNC', cred.getDefaultValue(), 'It defaults to the billing named credential');
        Assert.isTrue(cred.getIsRequired(), 'The named credential is required');
        industriesintegrationfwk.ApexProviderAttr toggle = attrs[1];
        Assert.areEqual('Simulate_Failure', toggle.getDeveloperName(), 'The second attribute is the failure toggle');
        Assert.areEqual('false', toggle.getDefaultValue(), 'The toggle\'s declared default is false');
        Assert.areEqual('String', toggle.getDataType(), 'The toggle is a String attribute');
        Assert.isFalse(toggle.getIsRequired(), 'The toggle is optional');
    }

    @IsTest
    static void nullHttpProviderFailsBeforeAnyResponse() {
        // A test can only show that the supplied provider is the one used: without it the provider is
        // dereferenced at the send, before any response is built.
        try {
            DFOApexMockService.executeCallout('guid-1', 'record-1', 'payload-1', new Map<String, Object>(), null);
            Assert.fail('Without an HTTP provider no response can be returned');
        } catch (Exception e) {
            Assert.isInstanceOfType(e, NullPointerException.class, 'The missing provider is dereferenced. Got: ' + e);
        }
    }

    @IsTest
    static void buildResponse_succeedsByDefault() {
        for (Map<String, Object> attributes : new List<Map<String, Object>>{
            null,
            new Map<String, Object>(),
            new Map<String, Object>{ 'Named_Credential' => 'BillingSystemNC' },
            new Map<String, Object>{ 'Simulate_Failure' => 'false' }
        }) {
            industriesintegrationfwk.IntegrationCalloutResponse response = DFOApexMockService.buildResponse(attributes);
            Assert.isTrue(response.isSuccess(), 'The step succeeds for ' + attributes);
            Assert.areEqual(200, response.getResponseCode(), 'Success carries response code 200 for ' + attributes);
            Assert.isNull(response.getErrorMessage(), 'Success carries no error message for ' + attributes);
        }
    }

    @IsTest
    static void buildResponse_failsWhenSimulateFailureIsTrue() {
        industriesintegrationfwk.IntegrationCalloutResponse response = DFOApexMockService.buildResponse(
            new Map<String, Object>{ 'Simulate_Failure' => 'true' });

        Assert.isFalse(response.isSuccess(), 'The step fails when the toggle is on');
        Assert.areEqual(500, response.getResponseCode(), 'Failure carries response code 500');
        Assert.areEqual('Internal Error - 500.', response.getErrorMessage(), 'Failure carries the error message');
    }

    @IsTest
    static void simulateFailure_readsTrueInAnyCaseOrAsABoolean() {
        for (Object value : new List<Object>{ 'true', 'TRUE', ' True ', true }) {
            Assert.isTrue(DFOApexMockService.simulateFailure(new Map<String, Object>{ 'Simulate_Failure' => value }),
                'Read as on: ' + value);
        }
        for (Object value : new List<Object>{ 'false', 'untrue', 't', 'yes', '1', '', null, false, 1 }) {
            Assert.isFalse(DFOApexMockService.simulateFailure(new Map<String, Object>{ 'Simulate_Failure' => value }),
                'Read as off: ' + value);
        }
    }
}
