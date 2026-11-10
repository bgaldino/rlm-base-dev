/**
 * RLM_CalculateTaxService posts the Avalara payload through RLM_HttpService, then — under
 * Test.isRunningTest() — parses its own canned success response instead of the callout body.
 * So the request side is asserted through the recorded callout, the response side through
 * the response type and its String form; the error-response branch cannot be reached from a test.
 */
@IsTest
private class RLM_CalculateTaxServiceTest {

    @IsTest
    static void getTax_withLines_postsAvalaraPayloadAndReturnsCalculateTaxResponse() {
        RLM_TaxTestFactory.RecordingHttpMock mock = new RLM_TaxTestFactory.RecordingHttpMock(200, '{}');
        Test.setMock(HttpCalloutMock.class, mock);
        commercetax.CalculateTaxRequest request = RLM_TaxTestFactory.request(
            commercetax.CalculateTaxType.Estimated, 'DOC-CALC-1', RLM_TaxTestFactory.lines(232));
        request.referenceEntityId = 'REF-CALC-1';
        request.taxTransactionType = commercetax.TaxTransactionType.Debit;

        Test.startTest();
        commercetax.TaxEngineResponse response = RLM_CalculateTaxService.getTax(RLM_TaxTestFactory.context(request));
        Test.stopTest();

        Assert.isNotNull(response, 'A request with lines should produce a response.');
        Assert.isInstanceOfType(response, commercetax.CalculateTaxResponse.class,
            'A success payload (no "error") maps to a CalculateTaxResponse, not an ErrorResponse.');
        // Values come from the parsed engine payload (document code, transaction id) and the request.
        RLM_TaxTestFactory.assertResponseHas(response, 'documentCode=testDocCode1231245984',
            'The document code is taken from the parsed engine response.');
        RLM_TaxTestFactory.assertResponseHas(response, 'taxTransactionId=0', 'The engine transaction id is mapped.');
        RLM_TaxTestFactory.assertResponseHas(response, 'referenceEntityId=REF-CALC-1', 'The request reference entity is echoed.');
        RLM_TaxTestFactory.assertResponseHas(response, 'currencyIsoCode=USD', 'The request currency is echoed.');

        Assert.areEqual(1, mock.requests.size(), 'Exactly one Avalara callout should be sent.');
        HttpRequest sent = mock.requests[0];
        Assert.areEqual('POST', sent.getMethod(), 'The transaction is created with a POST.');
        Assert.isTrue(sent.getEndpoint().endsWith('/transactions/create'),
            'The callout targets the Avalara create-transaction path: ' + sent.getEndpoint());
        Assert.areEqual('application/json', sent.getHeader('Content-type'), 'The payload is sent as JSON.');

        Map<String, Object> body = (Map<String, Object>) JSON.deserializeUntyped(sent.getBody());
        Assert.areEqual('SalesOrder', body.get('type'), 'Estimated tax is sent as a SalesOrder.');
        Assert.areEqual('DOC-CALC-1', body.get('code'), 'The document code is sent.');
        Assert.areEqual(1, ((List<Object>) body.get('lines')).size(), 'Every request line is sent.');
    }

    @IsTest
    static void getTax_actualCommittedRequest_returnsCalculateTaxResponse() {
        RLM_TaxTestFactory.RecordingHttpMock mock = new RLM_TaxTestFactory.RecordingHttpMock(200, '{}');
        Test.setMock(HttpCalloutMock.class, mock);
        commercetax.CalculateTaxRequest request = RLM_TaxTestFactory.request(
            commercetax.CalculateTaxType.Actual, 'DOC-CALC-2', new List<commercetax.TaxLineItemRequest>{
                RLM_TaxTestFactory.line(100, '1', null),
                RLM_TaxTestFactory.line(132, '2', null)
            });
        request.isCommit = true;
        request.taxTransactionType = commercetax.TaxTransactionType.Credit;

        Test.startTest();
        commercetax.TaxEngineResponse response = RLM_CalculateTaxService.getTax(RLM_TaxTestFactory.context(request));
        Test.stopTest();

        Assert.isInstanceOfType(response, commercetax.CalculateTaxResponse.class, 'Actual tax also maps to a CalculateTaxResponse.');
        Map<String, Object> body = (Map<String, Object>) JSON.deserializeUntyped(mock.requests[0].getBody());
        Assert.areEqual('SalesInvoice', body.get('type'), 'Actual tax is sent as a SalesInvoice.');
        Assert.areEqual(true, body.get('commit'), 'The commit flag is sent.');
        Assert.areEqual(2, ((List<Object>) body.get('lines')).size(), 'Both lines are sent.');
    }

    @IsTest
    static void getTax_withoutLines_returnsNullWithoutCallout() {
        RLM_TaxTestFactory.RecordingHttpMock mock = new RLM_TaxTestFactory.RecordingHttpMock(200, '{}');
        Test.setMock(HttpCalloutMock.class, mock);
        commercetax.CalculateTaxRequest request = RLM_TaxTestFactory.request(
            commercetax.CalculateTaxType.Estimated, 'DOC-EMPTY', new List<commercetax.TaxLineItemRequest>());

        Test.startTest();
        commercetax.TaxEngineResponse response = RLM_CalculateTaxService.getTax(RLM_TaxTestFactory.context(request));
        Test.stopTest();

        Assert.isNull(response, 'An empty line list returns null.');
        Assert.areEqual(0, mock.requests.size(), 'No callout is made without lines.');
    }

    @IsTest
    static void getTax_nullLineList_rethrows() {
        RLM_TaxTestFactory.RecordingHttpMock mock = new RLM_TaxTestFactory.RecordingHttpMock(200, '{}');
        Test.setMock(HttpCalloutMock.class, mock);
        commercetax.CalculateTaxRequest request = RLM_TaxTestFactory.request(
            commercetax.CalculateTaxType.Estimated, 'DOC-NULL-LINES', null);

        Exception caught;
        Test.startTest();
        try {
            RLM_CalculateTaxService.getTax(RLM_TaxTestFactory.context(request));
        } catch (Exception e) {
            caught = e;
        }
        Test.stopTest();

        Assert.isNotNull(caught, 'A null line list should fail rather than return a response.');
        Assert.isInstanceOfType(caught, NullPointerException.class, 'The original exception is rethrown: ' + caught);
        Assert.areEqual(0, mock.requests.size(), 'No callout is made when the request is unusable.');
    }
}
