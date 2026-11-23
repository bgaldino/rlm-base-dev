/**
 * RLM_CalculateTaxService posts the Avalara payload through RLM_HttpService and maps the response body.
 * Every getTax test drives the production path with an HttpCalloutMock (RLM_TaxTestFactory): the request
 * side is asserted through the recorded callout, the response side through the response type and its String
 * form. bodyOrNull is unit-tested directly, without a mock. A mock body stands in for each engine response, a CalloutException-throwing mock for the
 * failed callout (503), and bodies that lack a value, are not JSON or carry an "error" key reach the
 * incomplete (502), unreadable (502) and engine-error (501) branches.
 * Setters in getTax that no assertion covers (every other setter call is asserted): header
 * referenceDocumentCode, header exemptAmount, effectiveDate and transactionDate; imposition subType and
 * type, and the setImposition call; jurisdiction country, region, stateAssignedNumber, id and level; detail taxAuthorityTypeId,
 * taxId and taxRegionId (set from the detail's region code); line effectiveDate, isTaxable (set
 * twice), exemptAmount, productCode and quantity. The detail-level exemptAmount is covered by
 * getTax_detailExemptAmount_nullIsNotExempt_andAnAmountIsMapped (the canned payload's are all 0). Each test supplies its
 * own body, so both status branches are reachable: Temporary (the canned payload) maps to Uncommitted, and
 * getTax_committedStatus_mapsToCommitted covers Committed.
 */
@IsTest
private with sharing class RLM_CalculateTaxServiceTest {

    @IsTest
    static void getTax_withLines_postsAvalaraPayloadAndReturnsCalculateTaxResponse() {
        RLM_TaxTestFactory.RecordingHttpMock mock = new RLM_TaxTestFactory.RecordingHttpMock(200, RLM_TaxTestFactory.cannedSuccessBody());
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
        request.currencyIsoCode = 'XTS';
        request.taxTransactionType = commercetax.TaxTransactionType.Debit;

        Test.startTest();
        commercetax.TaxEngineResponse response = RLM_CalculateTaxService.getTax(RLM_TaxTestFactory.context(request));
        Test.stopTest();

        Assert.isNotNull(response, 'A request with lines should produce a response.');
        Assert.isInstanceOfType(response, commercetax.CalculateTaxResponse.class,
            'A success payload (no "error") maps to a CalculateTaxResponse, not an ErrorResponse.');
        // These compare the response with values only the canned engine payload holds: code,
        // status "Temporary" (printed as Uncommitted), one P0000000 line. Every id in that payload
        // is 0, so the taxTransactionId check proves only that the field is set from it.
        RLM_TaxTestFactory.assertResponseField(response, 'documentCode', 'testDocCode1231245984',
            'The document code is taken from the parsed engine response.');
        RLM_TaxTestFactory.assertResponseField(response, 'taxTransactionId', '0', 'The engine transaction id is set.');
        RLM_TaxTestFactory.assertResponseField(response, 'status', 'Uncommitted', 'An engine status of Temporary maps to Uncommitted.');
        RLM_TaxTestFactory.assertResponseField(response, 'lineNumber', '1', 'The engine line number is mapped.');
        RLM_TaxTestFactory.assertResponseField(response, 'taxCode', 'P0000000', 'The engine line tax code is mapped.');
        // The engine line has two tax details: WASHINGTON (rate 0.065) and KING (rate 0).
        RLM_TaxTestFactory.assertResponseFieldCount(response, 'name', 'WASHINGTON', 1,
            'The state jurisdiction detail is mapped.');
        RLM_TaxTestFactory.assertResponseFieldCount(response, 'name', 'KING', 1,
            'The county jurisdiction detail is mapped.');
        RLM_TaxTestFactory.assertResponseFieldCount(response, 'rate', '0.065', 1,
            'Each detail keeps its own rate: WASHINGTON reports 0.065.');
        RLM_TaxTestFactory.assertResponseFieldCount(response, 'rate', '0.0', 1,
            'Each detail keeps its own rate: KING reports 0, not the running total.');
        // These compare the response amounts with the canned payload's: line and header total 232
        // with tax 23.43; the WASHINGTON detail taxes 15.08 and KING 0, each on 232.
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
        // These compare the response with values only the request holds.
        RLM_TaxTestFactory.assertResponseField(response, 'referenceEntityId', 'REF-CALC-1', 'The request reference entity is echoed.');
        RLM_TaxTestFactory.assertResponseField(response, 'currencyIsoCode', 'XTS', 'The request currency is echoed.');
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
        RLM_TaxTestFactory.RecordingHttpMock mock = new RLM_TaxTestFactory.RecordingHttpMock(200, RLM_TaxTestFactory.cannedSuccessBody());
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
        // The response status matches the canned payload's Temporary, not the request's isCommit=true.
        RLM_TaxTestFactory.assertResponseField(response, 'status', 'Uncommitted', 'The engine status drives the response status.');

        Assert.areEqual(1, mock.requests.size(), 'Exactly one Avalara callout should be sent.');
        Map<String, Object> body = (Map<String, Object>) JSON.deserializeUntyped(mock.requests[0].getBody());
        Assert.areEqual('SalesInvoice', body.get('type'), 'Actual tax is sent as a SalesInvoice.');
        Assert.areEqual(true, body.get('commit'), 'The commit flag is sent.');
        Assert.areEqual(2, ((List<Object>) body.get('lines')).size(), 'Both lines are sent.');
    }

    @IsTest
    static void getTax_withoutTransactionType_throwsAfterCallout() {
        RLM_TaxTestFactory.RecordingHttpMock mock = new RLM_TaxTestFactory.RecordingHttpMock(200, RLM_TaxTestFactory.cannedSuccessBody());
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
            'Accepted limitation: a request without a tax transaction type throws a raw NullPointerException '
            + 'after the callout, because the platform always supplies one and the null reaches '
            + 'setTaxTransactionType.' + RLM_TaxTestFactory.SETTER_PREMISE_HINT);
        // The setter's exception type is platform behaviour (see the accepted risk in RLM_TaxTestFactory).
        Assert.areEqual('System.NullPointerException', caught.getTypeName(),
            'Accepted limitation: the null transaction type reaches the platform setter, which throws a raw '
            + 'NullPointerException. ' + caught
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
    static void getTax_nullLineList_returnsNullWithoutCallout() {
        RLM_TaxTestFactory.RecordingHttpMock mock = new RLM_TaxTestFactory.RecordingHttpMock(200, '{}');
        Test.setMock(HttpCalloutMock.class, mock);
        commercetax.CalculateTaxRequest request = RLM_TaxTestFactory.request(
            commercetax.CalculateTaxType.Estimated, 'DOC-NULL-LINES', null);

        Test.startTest();
        commercetax.TaxEngineResponse response = RLM_CalculateTaxService.getTax(RLM_TaxTestFactory.context(request));
        Test.stopTest();

        Assert.isNull(response, 'A null line list is treated like an empty one.');
        Assert.areEqual(0, mock.requests.size(), 'No callout is made without lines.');
    }

    // RLM_HttpService swallows a failed callout (RLM_HttpServiceTest covers that) and leaves a null
    // response; getTax reads the body through bodyOrNull and returns an ErrorResponse when it is null.
    // A mock that throws CalloutException drives that production path. bodyOrNull itself is tested below.
    @IsTest
    static void getTax_failedCallout_returnsTheNoResponseError() {
        RLM_TaxTestFactory.CalloutFailureHttpMock mock = new RLM_TaxTestFactory.CalloutFailureHttpMock();
        Test.setMock(HttpCalloutMock.class, mock);
        commercetax.CalculateTaxRequest request = RLM_TaxTestFactory.request(
            commercetax.CalculateTaxType.Estimated, 'DOC-NO-RESPONSE', RLM_TaxTestFactory.lines(232));
        request.taxTransactionType = commercetax.TaxTransactionType.Debit;

        Test.startTest();
        commercetax.TaxEngineResponse response = RLM_CalculateTaxService.getTax(RLM_TaxTestFactory.context(request));
        Test.stopTest();

        Assert.isInstanceOfType(response, commercetax.ErrorResponse.class, 'A missing response is an error response.');
        RLM_TaxTestFactory.assertResponseField(response, 'errorCode', '503', 'The error code is 503.');
        RLM_TaxTestFactory.assertResponseField(response, 'errorMessage', RLM_CalculateTaxService.NO_RESPONSE_MESSAGE,
            'The error carries the no-response message.');
        Assert.areEqual(1, mock.requests.size(), 'The request was still sent before the response was found missing.');
    }

    @IsTest
    static void getTax_avalaraErrorBody_returnsTheEngineMessage() {
        commercetax.CalculateTaxRequest request = RLM_TaxTestFactory.request(
            commercetax.CalculateTaxType.Estimated, 'DOC-ENGINE-ERROR', RLM_TaxTestFactory.lines(232));
        request.taxTransactionType = commercetax.TaxTransactionType.Debit;
        Test.setMock(HttpCalloutMock.class, new RLM_TaxTestFactory.RecordingHttpMock(200, '{"error":{"code":"GetTaxError","message":"Address is invalid.","details":[]}}'));

        commercetax.TaxEngineResponse response = RLM_CalculateTaxService.getTax(RLM_TaxTestFactory.context(request));

        Assert.isInstanceOfType(response, commercetax.ErrorResponse.class, 'An Avalara error body is an error response.');
        RLM_TaxTestFactory.assertResponseField(response, 'errorCode', '501', 'The error code is 501.');
        RLM_TaxTestFactory.assertResponseField(response, 'errorMessage', 'Address is invalid.', 'The engine message is returned.');
    }

    // A parsed response that lacks a total used to throw a NullPointerException out of getTax.
    @IsTest
    static void getTax_responseWithoutTotals_returnsAnIncompleteResponseError() {
        Map<String, String> bodies = new Map<String, String>{
            'totalAmount' => '{"code":"X","status":"Temporary","totalTax":1.5,"taxDate":"2020-07-15","date":"2020-07-15","lines":[]}',
            'totalTax' => '{"code":"X","status":"Temporary","totalAmount":10,"taxDate":"2020-07-15","date":"2020-07-15","lines":[]}',
            'taxDate' => '{"code":"X","status":"Temporary","totalAmount":10,"totalTax":1.5,"date":"2020-07-15","lines":[]}',
            'date' => '{"code":"X","status":"Temporary","totalAmount":10,"totalTax":1.5,"taxDate":"2020-07-15","lines":[]}',
            'lineAmount' => '{"code":"X","status":"Temporary","totalAmount":10,"totalTax":1.5,"taxDate":"2020-07-15","date":"2020-07-15","lines":[{"lineNumber":"1","taxCalculated":1.5,"taxDate":"2020-07-15"}]}',
            'taxCalculated' => '{"code":"X","status":"Temporary","totalAmount":10,"totalTax":1.5,"taxDate":"2020-07-15","date":"2020-07-15","lines":[{"lineNumber":"1","lineAmount":10,"taxDate":"2020-07-15"}]}',
            'line taxDate' => '{"code":"X","status":"Temporary","totalAmount":10,"totalTax":1.5,"taxDate":"2020-07-15","date":"2020-07-15","lines":[{"lineNumber":"1","lineAmount":10,"taxCalculated":1.5}]}'
        };
        for (String missing : bodies.keySet()) {
            commercetax.CalculateTaxRequest request = RLM_TaxTestFactory.request(
                commercetax.CalculateTaxType.Estimated, 'DOC-INCOMPLETE', RLM_TaxTestFactory.lines(232));
            request.taxTransactionType = commercetax.TaxTransactionType.Debit;
            Test.setMock(HttpCalloutMock.class, new RLM_TaxTestFactory.RecordingHttpMock(200, bodies.get(missing)));

            commercetax.TaxEngineResponse response = RLM_CalculateTaxService.getTax(RLM_TaxTestFactory.context(request));

            Assert.isInstanceOfType(response, commercetax.ErrorResponse.class, missing + ': an incomplete response is an error response.');
            RLM_TaxTestFactory.assertResponseField(response, 'errorCode', '502', missing + ': the error code is 502.');
            RLM_TaxTestFactory.assertResponseField(response, 'errorMessage',
                RLM_CalculateTaxService.INCOMPLETE_RESPONSE_PREFIX + missing + ' is missing.', missing + ': the message names the missing value.');
        }
    }

    // A response with no line list and a line with no tax details still maps to a success response.
    @IsTest
    static void getTax_responseWithoutLinesOrDetails_mapsToASuccessResponse() {
        List<String> noLines = new List<String>{
            '{"code":"X","status":"Temporary","totalAmount":10,"totalTax":1.5,"taxDate":"2020-07-15","date":"2020-07-15"}',
            '{"code":"X","status":"Temporary","totalAmount":10,"totalTax":1.5,"taxDate":"2020-07-15","date":"2020-07-15","lines":[{"lineNumber":"1","lineAmount":10,"taxCalculated":1.5,"taxDate":"2020-07-15"}]}'
        };
        for (String body : noLines) {
            commercetax.CalculateTaxRequest request = RLM_TaxTestFactory.request(
                commercetax.CalculateTaxType.Estimated, 'DOC-SPARSE', RLM_TaxTestFactory.lines(232));
            request.taxTransactionType = commercetax.TaxTransactionType.Debit;
            Test.setMock(HttpCalloutMock.class, new RLM_TaxTestFactory.RecordingHttpMock(200, body));

            commercetax.TaxEngineResponse response = RLM_CalculateTaxService.getTax(RLM_TaxTestFactory.context(request));

            Assert.isInstanceOfType(response, commercetax.CalculateTaxResponse.class, 'A sparse but complete response is mapped: ' + body);
        }
    }

    // Routing is on the top-level "error" key. The word "error" in a successful body (here a
    // reason and a jurisdiction name) must not turn it into an error response.
    @IsTest
    static void getTax_successBodyContainingTheWordError_isStillASuccess() {
        commercetax.CalculateTaxRequest request = RLM_TaxTestFactory.request(
            commercetax.CalculateTaxType.Estimated, 'DOC-WORD-ERROR', RLM_TaxTestFactory.lines(232));
        request.taxTransactionType = commercetax.TaxTransactionType.Debit;
        Test.setMock(HttpCalloutMock.class, new RLM_TaxTestFactory.RecordingHttpMock(200, '{"code":"X","status":"Temporary","adjustmentReason":"corrected an error",'
            + '"totalAmount":10,"totalTax":1.5,"taxDate":"2020-07-15","date":"2020-07-15","lines":[]}'));

        commercetax.TaxEngineResponse response = RLM_CalculateTaxService.getTax(RLM_TaxTestFactory.context(request));

        Assert.isInstanceOfType(response, commercetax.CalculateTaxResponse.class,
            'The word "error" in a value is not an engine error.');
    }

    // Every error shape yields a 501 response and never throws: a message, details only, a bare
    // string, an error object with neither message nor details (used to throw a
    // NullPointerException), and an error of an unexpected type.
    @IsTest
    static void getTax_errorBodies_alwaysReturnAnErrorResponseWithAMessage() {
        Map<String, String> expectedByBody = new Map<String, String>{
            '{"error":{"code":"E","message":"Address is invalid.","details":[]}}' => 'Address is invalid.',
            '{"error":{"code":"E","details":[{"message":"First."},{"message":""},{"message":"Last."}]}}' => 'Last.',
            '{"error":"Bad credentials"}' => 'Bad credentials',
            '{"error":{"code":"E"}}' => RLM_CalculateTaxService.ERROR_WITHOUT_MESSAGE,
            '{"error":{"code":"E","details":[{"code":"D"}]}}' => RLM_CalculateTaxService.ERROR_WITHOUT_MESSAGE,
            '{"error":{}}' => RLM_CalculateTaxService.ERROR_WITHOUT_MESSAGE,
            '{"error":""}' => RLM_CalculateTaxService.ERROR_WITHOUT_MESSAGE,
            '{"error":42}' => RLM_CalculateTaxService.ERROR_WITHOUT_MESSAGE
        };
        for (String body : expectedByBody.keySet()) {
            commercetax.CalculateTaxRequest request = RLM_TaxTestFactory.request(
                commercetax.CalculateTaxType.Estimated, 'DOC-ERROR-SHAPE', RLM_TaxTestFactory.lines(232));
            request.taxTransactionType = commercetax.TaxTransactionType.Debit;
            Test.setMock(HttpCalloutMock.class, new RLM_TaxTestFactory.RecordingHttpMock(200, body));

            commercetax.TaxEngineResponse response = RLM_CalculateTaxService.getTax(RLM_TaxTestFactory.context(request));

            Assert.isInstanceOfType(response, commercetax.ErrorResponse.class, body + ': an error response.');
            RLM_TaxTestFactory.assertResponseField(response, 'errorCode', '501', body + ': the error code is 501.');
            RLM_TaxTestFactory.assertResponseField(response, 'errorMessage', expectedByBody.get(body), body + ': the message.');
        }
    }

    // A body that is not JSON cannot be read: a 502 error response, not a JSONException. A blank body is
    // sent as ' ' because an empty string may read back as no body, which is the 503 path above.
    @IsTest
    static void getTax_bodyThatIsNotJson_returnsAnUnreadableResponseError() {
        for (String body : new List<String>{ '<html>Bad gateway</html>', '[1,2]', ' ' }) {
            commercetax.CalculateTaxRequest request = RLM_TaxTestFactory.request(
                commercetax.CalculateTaxType.Estimated, 'DOC-NOT-JSON', RLM_TaxTestFactory.lines(232));
            request.taxTransactionType = commercetax.TaxTransactionType.Debit;
            Test.setMock(HttpCalloutMock.class, new RLM_TaxTestFactory.RecordingHttpMock(200, body));

            commercetax.TaxEngineResponse response = RLM_CalculateTaxService.getTax(RLM_TaxTestFactory.context(request));

            Assert.isInstanceOfType(response, commercetax.ErrorResponse.class, body + ': an error response.');
            RLM_TaxTestFactory.assertResponseField(response, 'errorCode', '502', body + ': the error code is 502.');
            RLM_TaxTestFactory.assertResponseField(response, 'errorMessage',
                RLM_CalculateTaxService.UNREADABLE_RESPONSE_MESSAGE, body + ': the message.');
        }
    }

    // A detail with no exempt amount is not exempt (null is not "exempt"); a detail with one maps
    // the amount and no invented reason.
    @IsTest
    static void getTax_detailExemptAmount_nullIsNotExempt_andAnAmountIsMapped() {
        String head = '{"code":"X","status":"Temporary","totalAmount":10,"totalTax":1.5,"taxDate":"2020-07-15","date":"2020-07-15",'
            + '"lines":[{"lineNumber":"1","lineAmount":10,"taxCalculated":1.5,"taxDate":"2020-07-15","details":[';
        String detailFields = '"taxName":"WA STATE TAX","jurisName":"WASHINGTON","rate":0.1,"taxCalculated":1.5,"taxableAmount":10';
        String tail = ']}]}';
        List<String> bodies = new List<String>{
            head + '{' + detailFields + '}' + tail,
            head + '{' + detailFields + ',"exemptAmount":5}' + tail
        };
        for (Integer i = 0; i < bodies.size(); i++) {
            commercetax.CalculateTaxRequest request = RLM_TaxTestFactory.request(
                commercetax.CalculateTaxType.Estimated, 'DOC-EXEMPT', RLM_TaxTestFactory.lines(232));
            request.taxTransactionType = commercetax.TaxTransactionType.Debit;
            Test.setMock(HttpCalloutMock.class, new RLM_TaxTestFactory.RecordingHttpMock(200, bodies[i]));

            commercetax.TaxEngineResponse response = RLM_CalculateTaxService.getTax(RLM_TaxTestFactory.context(request));

            Assert.isInstanceOfType(response, commercetax.CalculateTaxResponse.class, 'Detail ' + i + ' maps to a success response.');
            RLM_TaxTestFactory.assertResponseFieldCount(response, 'exemptAmount', '5.0', i,
                'Only the detail that carries an exempt amount reports one.');
            RLM_TaxTestFactory.assertResponseFieldCount(response, 'exemptReason', 'Some reason we dont know', 0,
                'No placeholder exempt reason is set.');
        }
    }

    // A date the engine returns that Date.valueOf cannot read used to throw a TypeException out of getTax.
    @IsTest
    static void getTax_responseWithAnInvalidDate_returnsAnInvalidDateError() {
        String head = '{"code":"X","status":"Temporary","totalAmount":10,"totalTax":1.5,';
        Map<String, String> bodies = new Map<String, String>{
            'taxDate' => head + '"taxDate":"not a date","date":"2020-07-15","lines":[]}',
            'date' => head + '"taxDate":"2020-07-15","date":"not a date","lines":[]}',
            'line taxDate' => head + '"taxDate":"2020-07-15","date":"2020-07-15","lines":[{"lineNumber":"1","lineAmount":10,"taxCalculated":1.5,"taxDate":"not a date"}]}'
        };
        for (String field : bodies.keySet()) {
            Test.setMock(HttpCalloutMock.class, new RLM_TaxTestFactory.RecordingHttpMock(200, bodies.get(field)));
            commercetax.CalculateTaxRequest request = RLM_TaxTestFactory.request(
                commercetax.CalculateTaxType.Estimated, 'DOC-BAD-DATE', RLM_TaxTestFactory.lines(232));
            request.taxTransactionType = commercetax.TaxTransactionType.Debit;

            commercetax.TaxEngineResponse response = RLM_CalculateTaxService.getTax(RLM_TaxTestFactory.context(request));

            Assert.isInstanceOfType(response, commercetax.ErrorResponse.class, field + ': an invalid date is an error response.');
            RLM_TaxTestFactory.assertResponseField(response, 'errorCode', '502', field + ': the error code is 502.');
            RLM_TaxTestFactory.assertResponseField(response, 'errorMessage',
                RLM_CalculateTaxService.INVALID_DATE_PREFIX + field + ' is not a date.', field + ': the message names the date.');
        }
    }

    @IsTest
    static void getTax_committedStatus_mapsToCommitted() {
        commercetax.CalculateTaxRequest request = RLM_TaxTestFactory.request(
            commercetax.CalculateTaxType.Estimated, 'DOC-COMMITTED', RLM_TaxTestFactory.lines(232));
        request.taxTransactionType = commercetax.TaxTransactionType.Debit;
        Test.setMock(HttpCalloutMock.class, new RLM_TaxTestFactory.RecordingHttpMock(200, '{"code":"X","status":"Committed",'
            + '"totalAmount":10,"totalTax":1.5,"taxDate":"2020-07-15","date":"2020-07-15","lines":[]}'));

        commercetax.TaxEngineResponse response = RLM_CalculateTaxService.getTax(RLM_TaxTestFactory.context(request));

        Assert.isInstanceOfType(response, commercetax.CalculateTaxResponse.class, 'A Committed body is a success response.');
        RLM_TaxTestFactory.assertResponseField(response, 'status', 'Committed', 'An engine status of Committed maps to Committed.');
    }

    @IsTest
    static void bodyOrNull_nullResponse_isNull_andABodyIsReturned() {
        Assert.isNull(RLM_CalculateTaxService.bodyOrNull(null), 'No response, no body.');
        HttpResponse response = new HttpResponse();
        response.setBody('{"ok":true}');
        Assert.areEqual('{"ok":true}', RLM_CalculateTaxService.bodyOrNull(response), 'The body is returned.');
    }

    // Unit-tested with a mocked callout; not verified against an Avalara sandbox.
    @IsTest
    static void getTax_lineWithEffectiveDate_sendsALineLevelTaxDateOverride() {
        RLM_TaxTestFactory.RecordingHttpMock mock = new RLM_TaxTestFactory.RecordingHttpMock(200, RLM_TaxTestFactory.cannedSuccessBody());
        Test.setMock(HttpCalloutMock.class, mock);
        commercetax.CalculateTaxRequest request = RLM_TaxTestFactory.request(
            commercetax.CalculateTaxType.Estimated, 'DOC-OVERRIDE',
            new List<commercetax.TaxLineItemRequest>{
                RLM_TaxTestFactory.line(232, 'L1', Datetime.newInstanceGmt(2026, 1, 20, 12, 0, 0))
            });
        request.taxTransactionType = commercetax.TaxTransactionType.Debit;

        Test.startTest();
        RLM_CalculateTaxService.getTax(RLM_TaxTestFactory.context(request));
        Test.stopTest();

        Assert.areEqual(1, mock.requests.size(), 'One callout.');
        Map<String, Object> body = (Map<String, Object>) JSON.deserializeUntyped(mock.requests[0].getBody());
        Map<String, Object> sentLine = (Map<String, Object>) ((List<Object>) body.get('lines'))[0];
        Map<String, Object> addresses = (Map<String, Object>) sentLine.get('addresses');
        Assert.isFalse(addresses.containsKey('taxOverride'), 'taxOverride is not inside addresses.');
        Map<String, Object> sentOverride = (Map<String, Object>) sentLine.get('taxOverride');
        Assert.isNotNull(sentOverride, 'taxOverride is on the line.');
        Assert.areEqual('TaxDate', sentOverride.get('type'), 'type');
        Assert.isNotNull(sentOverride.get('reason'), 'reason');
        Assert.isTrue(String.valueOf(sentOverride.get('taxDate')).startsWith('2026-01-20'), 'taxDate: ' + sentOverride.get('taxDate'));
    }
}
