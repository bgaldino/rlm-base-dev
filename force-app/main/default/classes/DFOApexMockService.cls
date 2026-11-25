/*
 * Copyright 2023 salesforce.com, inc.
 * All Rights Reserved
 * Company Confidential
 */
// Mock Apex provider for Dynamic Revenue Orchestrator callout steps. It posts to the BillingSystemNC mock
// endpoint's /delay/3 path only to add latency and does not read the reply. It returns success (response
// code 200) unless the provider attribute Simulate_Failure is true, when it returns failure (response code
// 500). A send that throws (for example, the user cannot access the named credential's external
// credential) fails the step before any result is returned. Simulate_Failure is set on the provider
// definition (shipped as false in post_quantumbit; a redeploy resets it), so it applies to every step that
// uses that definition. The DROBillingService definition runs this class without the attribute.
global with sharing class DFOApexMockService implements industriesintegrationfwk.ProcessIntegrationProviderAdvanced {

    // Named credential for the mock endpoint
    private static final String MOCK_CALLOUT_NAMED_CREDENTIAL = 'callout:BillingSystemNC';
    private final static Integer TIMEOUT = 120000; // Request time out in milliseconds

    @TestVisible private static final String SIMULATE_FAILURE = 'Simulate_Failure';
    @TestVisible private static final String FAILURE_MESSAGE = 'Internal Error - 500.';

    private static final industriesintegrationfwk.ApexProviderAttr NAMED_CRED_ATTR = new industriesintegrationfwk.ApexProviderAttr('Named Credential',
    'Named_Credential', 'BillingSystemNC', true, 'String');

    private static final industriesintegrationfwk.ApexProviderAttr SIMULATE_FAILURE_ATTR = new industriesintegrationfwk.ApexProviderAttr('Simulate Failure',
    SIMULATE_FAILURE, 'false', false, 'String');

    /**
     * @param requestGuid                 Request GUID provided by the client
     * @param inputRecordId               Input Record ID provided by the client
     * @param payload                     Payload to be passed to the Provider Class
     * @param attributes                  Map of config attributes, keyed by attribute developer name
     * @param httpProvider                The framework's HTTP provider that sends the request
     * @return IntegrationCalloutResponse Response sent to the client
    */
    global static industriesintegrationfwk.IntegrationCalloutResponse executeCallout(String requestGuid, String inputRecordId, String payload, Map<String, Object> attributes,
    industriesintegrationfwk.HttpBaseProvider httpProvider) {
        String msgBody = '{\"message\":\"Hello\",'
            + '\n\"requestGuid\":\"' + requestGuid + '\",\n'
            + '\n\"inputRecordId\":\"' + inputRecordId + '\",\n'
            + '\n\"payload\":\"' + payload + '\"}'
            ;
        // Call the mock endpoint (adds latency; its reply is not read)
        makeCallout(httpProvider, msgBody);

        return buildResponse(attributes);
    }

    // The step's result: success with response code 200, or, when Simulate_Failure is true, failure
    // with response code 500 and an error message.
    @TestVisible
    private static industriesintegrationfwk.IntegrationCalloutResponse buildResponse(Map<String, Object> attributes) {
        industriesintegrationfwk.IntegrationCalloutResponse integrationCalloutResponse;
        if (simulateFailure(attributes)) {
            integrationCalloutResponse = new industriesintegrationfwk.IntegrationCalloutResponse(false);
            integrationCalloutResponse.setResponseCode(500);
            integrationCalloutResponse.setErrorMessage(FAILURE_MESSAGE);
        } else {
            integrationCalloutResponse = new industriesintegrationfwk.IntegrationCalloutResponse(true);
            integrationCalloutResponse.setResponseCode(200);
        }
        return integrationCalloutResponse;
    }

    // True only when Simulate_Failure reads "true" (any case, surrounding spaces ignored; a Boolean true
    // reads the same). Missing, blank or any other value means success.
    @TestVisible
    private static Boolean simulateFailure(Map<String, Object> attributes) {
        Object value = attributes == null ? null : attributes.get(SIMULATE_FAILURE);
        return value != null && String.valueOf(value).trim().equalsIgnoreCase('true');
    }

    // Call Mock Service API.
    private static HttpResponse makeCallout(industriesintegrationfwk.HttpBaseProvider httpProvider, String msgBody) {

        // Construct the request object
        String endPoint = MOCK_CALLOUT_NAMED_CREDENTIAL + '/delay/3';
        HttpRequest request = new HttpRequest();
        request.setMethod('POST');
        request.setHeader('Content-Type', 'application/json');
        request.setHeader('Accept', 'application/json');
        request.setEndpoint(endPoint);
        request.setTimeout(TIMEOUT);
        request.setBody(msgBody);

        // Send request through the framework's provider
        HttpResponse response = httpProvider.httpCallout(request);

        return response;
    }

    global static List<industriesintegrationfwk.ApexProviderAttr> getProviderAttributes() {
        List<industriesintegrationfwk.ApexProviderAttr> defaults = new List<industriesintegrationfwk.ApexProviderAttr>();
        defaults.add(NAMED_CRED_ATTR);
        defaults.add(SIMULATE_FAILURE_ATTR);
        return defaults;
    }

}
