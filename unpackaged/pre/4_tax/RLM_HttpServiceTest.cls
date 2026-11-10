@IsTest
private with sharing class RLM_HttpServiceTest {

    private static final String POST_ENDPOINT_PREFIX = 'callout:commerce.tax.TaxTypedNamedCredential:test';

    public class SimulatedFailureException extends Exception {}

    /** Throws instead of answering: a CalloutException or an unexpected exception type. */
    public class ThrowingHttpMock implements HttpCalloutMock {
        public Integer calls = 0;
        private Boolean throwCalloutException;

        public ThrowingHttpMock(Boolean throwCalloutException) {
            this.throwCalloutException = throwCalloutException;
        }

        public HttpResponse respond(HttpRequest request) {
            calls++;
            if (throwCalloutException) {
                throw new CalloutException('Simulated read timeout');
            }
            throw new SimulatedFailureException('Simulated unexpected failure');
        }
    }

    @IsTest
    static void getInstance_returnsTheSameInstance() {
        Test.startTest();
        RLM_HttpService first = RLM_HttpService.getInstance();
        RLM_HttpService second = RLM_HttpService.getInstance();
        Test.stopTest();

        Assert.isNotNull(first, 'getInstance should create an instance.');
        Assert.isTrue(first === second, 'getInstance should return the cached singleton.');
    }

    @IsTest
    static void get_sendsGetWithoutBodyAndStoresResponse() {
        RLM_TaxTestFactory.RecordingHttpMock mock = new RLM_TaxTestFactory.RecordingHttpMock(200, '{"ping":"pong"}');
        Test.setMock(HttpCalloutMock.class, mock);
        RLM_HttpService service = new RLM_HttpService();

        Test.startTest();
        service.get('https://example.invalid/api/v2/utilities/ping');
        Test.stopTest();

        Assert.areEqual(1, mock.requests.size(), 'Exactly one callout should be sent.');
        HttpRequest sent = mock.requests[0];
        Assert.areEqual('GET', sent.getMethod(), 'get() should send a GET.');
        Assert.areEqual('https://example.invalid/api/v2/utilities/ping', sent.getEndpoint(), 'get() uses the endpoint as given.');
        String body = sent.getBody();
        Assert.isTrue(body == null || body == '', 'A GET carries no body: [' + body + ']');

        HttpResponse response = service.getResponse();
        Assert.isNotNull(response, 'The response should be stored.');
        Assert.areEqual(200, response.getStatusCode(), 'Stored response status');
        Assert.areEqual('{"ping":"pong"}', response.getBody(), 'Stored response body');
        Assert.isTrue(service.getResponseToString().contains('StatusCode=200'),
            'getResponseToString should describe the stored response: ' + service.getResponseToString());
    }

    @IsTest
    static void post_prefixesNamedCredentialAndSendsHeadersAndBody() {
        RLM_TaxTestFactory.RecordingHttpMock mock = new RLM_TaxTestFactory.RecordingHttpMock(201, '{"id":42}');
        Test.setMock(HttpCalloutMock.class, mock);
        RLM_HttpService service = new RLM_HttpService();
        service.addHeader('Content-type', 'application/json');
        service.addHeader('X-Test-Header', 'rlm');

        Test.startTest();
        service.post('/transactions/create', '{"type":"SalesOrder"}');
        Test.stopTest();

        Assert.areEqual(1, mock.requests.size(), 'Exactly one callout should be sent.');
        HttpRequest sent = mock.requests[0];
        Assert.areEqual('POST', sent.getMethod(), 'post() should send a POST.');
        Assert.areEqual(POST_ENDPOINT_PREFIX + '/transactions/create', sent.getEndpoint(),
            'post() prefixes the tax named credential to the path.');
        Assert.areEqual('{"type":"SalesOrder"}', sent.getBody(), 'The request body is sent as given.');
        Assert.areEqual('application/json', sent.getHeader('Content-type'), 'Added headers are applied.');
        Assert.areEqual('rlm', sent.getHeader('X-Test-Header'), 'Every added header is applied.');
        Assert.areEqual(201, service.getResponse().getStatusCode(), 'The stored response is the mock response.');
        Assert.areEqual('{"id":42}', service.getResponse().getBody(), 'Stored response body');
    }

    @IsTest
    static void post_blankBody_isNotSet() {
        RLM_TaxTestFactory.RecordingHttpMock mock = new RLM_TaxTestFactory.RecordingHttpMock(200, '{}');
        Test.setMock(HttpCalloutMock.class, mock);
        RLM_HttpService service = new RLM_HttpService();

        Test.startTest();
        service.post('/utilities/ping', '   ');
        Test.stopTest();

        Assert.areEqual(1, mock.requests.size(), 'The POST is still sent.');
        // An unset HttpRequest body reads back as ''; the whitespace must not have been set.
        String body = mock.requests[0].getBody();
        Assert.isTrue(body == null || body == '', 'A whitespace-only body is not set on the request: [' + body + ']');
    }

    @IsTest
    static void send_calloutException_isSwallowedAndLeavesNoResponse() {
        ThrowingHttpMock mock = new ThrowingHttpMock(true);
        Test.setMock(HttpCalloutMock.class, mock);
        RLM_HttpService service = new RLM_HttpService();

        Test.startTest();
        service.post('/transactions/create', '{"type":"SalesOrder"}');
        Test.stopTest();

        Assert.areEqual(1, mock.calls, 'The callout should be attempted once.');
        Assert.isNull(service.getResponse(), 'A failed callout leaves no stored response.');
    }

    @IsTest
    static void send_unexpectedException_isSwallowedAndLeavesNoResponse() {
        ThrowingHttpMock mock = new ThrowingHttpMock(false);
        Test.setMock(HttpCalloutMock.class, mock);
        RLM_HttpService service = new RLM_HttpService();

        Test.startTest();
        service.get('https://example.invalid/api/v2/utilities/ping');
        Test.stopTest();

        Assert.areEqual(1, mock.calls, 'The callout should be attempted once.');
        Assert.isNull(service.getResponse(), 'A failed callout leaves no stored response.');
    }
}
