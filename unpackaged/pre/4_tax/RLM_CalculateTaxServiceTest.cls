/**
 * RLM_CalculateTaxService posts the Avalara payload through RLM_HttpService, then — under
 * Test.isRunningTest() — parses its own canned success response instead of the callout body.
 * So the request side is asserted through the recorded callout, the response side through
 * the response type and its String form; the error-response branch cannot be reached from a test.
 */
@IsTest
private with sharing class RLM_CalculateTaxServiceTest {

    @IsTest
    static void getTax_withLines_postsAvalaraPayloadAndReturnsCalculateTaxResponse() {
        RLM_TaxTestFactory.RecordingHttpMock mock = new RLM_TaxTestFactory.RecordingHttpMock(200, '{}');
        Test.setMock(HttpCalloutMock.class, mock);
        // The request line number and tax code differ from the engine payload's ("1", "P0000000"),
        // so the response can show which side each value came from.
        Double amount = 232;
        Double quantity = 1;
        commercetax.TaxLineItemRequest requestLine = new commercetax.TaxLineItemRequest(
            RLM_TaxTestFactory.lineAddresses(), amount, 'Test line', RLM_TaxTestFactory.PRODUCT_CODE,
            quantity, 'REQ-7', 'PC040100', null);
        commercetax.CalculateTaxRequest request = RLM_TaxTestFactory.request(
            commercetax.CalculateTaxType.Estimated, 'DOC-CALC-1',
            new List<commercetax.TaxLineItemRequest>{ requestLine });
        request.referenceEntityId = 'REF-CALC-1';
        request.currencyIsoCode = 'EUR';
        request.taxTransactionType = commercetax.TaxTransactionType.Debit;

        Test.startTest();
        commercetax.TaxEngineResponse response = RLM_CalculateTaxService.getTax(RLM_TaxTestFactory.context(request));
        Test.stopTest();

        Assert.isNotNull(response, 'A request with lines should produce a response.');
        Assert.isInstanceOfType(response, commercetax.CalculateTaxResponse.class,
            'A success payload (no "error") maps to a CalculateTaxResponse, not an ErrorResponse.');
        // From the parsed (canned) engine payload: code, id, status "Temporary", one P0000000 line.
        RLM_TaxTestFactory.assertResponseField(response, 'documentCode', 'testDocCode1231245984',
            'The document code is taken from the parsed engine response.');
        RLM_TaxTestFactory.assertResponseField(response, 'taxTransactionId', '0', 'The engine transaction id is mapped.');
        RLM_TaxTestFactory.assertResponseField(response, 'status', 'Uncommitted', 'An engine status of Temporary maps to Uncommitted.');
        RLM_TaxTestFactory.assertResponseField(response, 'lineNumber', '1', 'The engine line number is mapped.');
        RLM_TaxTestFactory.assertResponseField(response, 'taxCode', 'P0000000', 'The engine line tax code is mapped.');
        // The engine line has two tax details: WASHINGTON (rate 0.065) and KING (rate 0).
        RLM_TaxTestFactory.assertResponseFieldCount(response, 'name', 'WASHINGTON', 1,
            'The state jurisdiction detail is mapped.');
        RLM_TaxTestFactory.assertResponseFieldCount(response, 'name', 'KING', 1,
            'The county jurisdiction detail is mapped.');
        RLM_TaxTestFactory.assertResponseFieldCount(response, 'rate', '0.065', 2,
            'Known gap: detail rates accumulate across a line\'s details instead of each detail keeping '
            + 'its own rate (KING reports 0.065, not 0). Update this test when it is fixed.');
        // Amounts from the engine payload: line and header total 232 with tax 23.43; the WASHINGTON
        // detail taxes 15.08 and KING 0, each on 232.
        RLM_TaxTestFactory.assertResponseFieldCount(response, 'totalAmount', '232.0', 2, 'Header and line total amount.');
        RLM_TaxTestFactory.assertResponseFieldCount(response, 'taxAmount', '23.43', 2, 'Header and line tax amount.');
        RLM_TaxTestFactory.assertResponseFieldCount(response, 'totalAmountWithTax', '255.43', 2,
            'Header and line total with tax.');
        RLM_TaxTestFactory.assertResponseFieldCount(response, 'tax', '15.08', 1, 'The WASHINGTON detail tax.');
        RLM_TaxTestFactory.assertResponseFieldCount(response, 'tax', '0.0', 1, 'The KING detail tax.');
        RLM_TaxTestFactory.assertResponseFieldCount(response, 'taxableAmount', '232.0', 2, 'Both details tax 232.');
        RLM_TaxTestFactory.assertResponseField(response, 'statusDescription', 'NotAdjusted',
            'The engine adjustment reason becomes the status description.');
        RLM_TaxTestFactory.assertResponseFieldCount(response, 'lineNumber', 'REQ-7', 0,
            'Response lines come from the engine payload, not the request.');
        RLM_TaxTestFactory.assertResponseFieldCount(response, 'taxCode', 'PC040100', 0,
            'Response tax codes come from the engine payload, not the request.');
        // From the request.
        RLM_TaxTestFactory.assertResponseField(response, 'referenceEntityId', 'REF-CALC-1', 'The request reference entity is echoed.');
        RLM_TaxTestFactory.assertResponseField(response, 'currencyIsoCode', 'EUR', 'The request currency is echoed.');
        RLM_TaxTestFactory.assertResponseField(response, 'taxTransactionType', 'Debit', 'The request transaction type is echoed.');
        RLM_TaxTestFactory.assertResponseField(response, 'taxType', 'Estimated', 'The request tax type is echoed.');

        Assert.areEqual(1, mock.requests.size(), 'Exactly one Avalara callout should be sent.');
        HttpRequest sent = mock.requests[0];
        Assert.areEqual('POST', sent.getMethod(), 'The transaction is created with a POST.');
        Assert.isTrue(sent.getEndpoint().endsWith('/transactions/create'),
            'The callout targets the Avalara create-transaction path: ' + sent.getEndpoint());
        Assert.areEqual('application/json', sent.getHeader('Content-type'), 'The payload is sent as JSON.');

        Map<String, Object> body = (Map<String, Object>) JSON.deserializeUntyped(sent.getBody());
        Assert.areEqual('SalesOrder', body.get('type'), 'Estimated tax is sent as a SalesOrder.');
        Assert.areEqual('DOC-CALC-1', body.get('code'), 'The document code is sent.');
        List<Object> sentLines = (List<Object>) body.get('lines');
        Assert.areEqual(1, sentLines.size(), 'Every request line is sent.');
        Map<String, Object> sentLine = (Map<String, Object>) sentLines[0];
        Assert.areEqual('REQ-7', sentLine.get('number'), 'The request line number is sent to the engine.');
        Assert.areEqual('PC040100', sentLine.get('taxCode'), 'The request tax code is sent to the engine.');
    }

    @IsTest
    static void getTax_actualCommitRequest_sendsSalesInvoiceAndEchoesTransactionType() {
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
        RLM_TaxTestFactory.assertResponseField(response, 'taxTransactionType', 'Credit', 'The request transaction type is echoed.');
        RLM_TaxTestFactory.assertResponseField(response, 'taxType', 'Actual', 'The request tax type is echoed.');
        // The status comes from the engine payload, not from isCommit: the test payload is Temporary.
        RLM_TaxTestFactory.assertResponseField(response, 'status', 'Uncommitted', 'The engine status drives the response status.');

        Assert.areEqual(1, mock.requests.size(), 'Exactly one Avalara callout should be sent.');
        Map<String, Object> body = (Map<String, Object>) JSON.deserializeUntyped(mock.requests[0].getBody());
        Assert.areEqual('SalesInvoice', body.get('type'), 'Actual tax is sent as a SalesInvoice.');
        Assert.areEqual(true, body.get('commit'), 'The commit flag is sent.');
        Assert.areEqual(2, ((List<Object>) body.get('lines')).size(), 'Both lines are sent.');
    }

    @IsTest
    static void getTax_withoutTransactionType_throwsAfterCallout() {
        RLM_TaxTestFactory.RecordingHttpMock mock = new RLM_TaxTestFactory.RecordingHttpMock(200, '{}');
        Test.setMock(HttpCalloutMock.class, mock);
        commercetax.CalculateTaxRequest request = RLM_TaxTestFactory.request(
            commercetax.CalculateTaxType.Estimated, 'DOC-NO-TYPE', RLM_TaxTestFactory.lines(232));
        request.taxTransactionType = null;

        commercetax.TaxEngineContext context = RLM_TaxTestFactory.context(request);
        Exception caught;
        Test.startTest();
        try {
            RLM_CalculateTaxService.getTax(context);
        } catch (Exception e) {
            caught = e;
        }
        Test.stopTest();

        Assert.isNotNull(caught,
            'Known gap: a request without a tax transaction type throws a raw NullPointerException after the '
            + 'callout, because the null is passed unvalidated to setTaxTransactionType (the mock adapters '
            + 'default it to Debit). '
            + 'Update this test when it is fixed.' + RLM_TaxTestFactory.SETTER_PREMISE_HINT);
        // The setter's exception type is platform behaviour (see the accepted risk in RLM_TaxTestFactory).
        Assert.areEqual('System.NullPointerException', caught.getTypeName(),
            'Known gap: the null transaction type reaches the platform setter, which throws a raw '
            + 'NullPointerException. Update this test when it is fixed. ' + caught
            + RLM_TaxTestFactory.SETTER_PREMISE_HINT);
        Assert.areEqual(1, mock.requests.size(), 'The failure comes after the engine callout: ' + caught);
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

        // getTax has an explicit "else return null" for an empty list, like the adapters' explicit
        // null for request types they do not handle, so this is treated as intended, not a gap.
        Assert.isNull(response, 'An empty line list returns null.');
        Assert.areEqual(0, mock.requests.size(), 'No callout is made without lines.');
    }

    @IsTest
    static void getTax_nullLineList_rethrows() {
        RLM_TaxTestFactory.RecordingHttpMock mock = new RLM_TaxTestFactory.RecordingHttpMock(200, '{}');
        Test.setMock(HttpCalloutMock.class, mock);
        commercetax.CalculateTaxRequest request = RLM_TaxTestFactory.request(
            commercetax.CalculateTaxType.Estimated, 'DOC-NULL-LINES', null);

        commercetax.TaxEngineContext context = RLM_TaxTestFactory.context(request);
        Exception caught;
        Test.startTest();
        try {
            RLM_CalculateTaxService.getTax(context);
        } catch (Exception e) {
            caught = e;
        }
        Test.stopTest();

        Assert.isNotNull(caught,
            'Known gap: a null line list is not guarded and getTax throws a raw NullPointerException. '
            + 'Update this test when it is fixed.');
        Assert.isInstanceOfType(caught, NullPointerException.class,
            'Known gap: a null line list is not guarded and getTax throws a raw NullPointerException. '
            + 'Update this test when it is fixed. ' + caught);
        Assert.areEqual(0, mock.requests.size(), 'No callout is made when the request is unusable.');
    }
}
