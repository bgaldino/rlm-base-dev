/**
 * RLM_CalculateTaxService posts the Avalara payload through RLM_HttpService and maps the response body.
 * Every getTax test that reaches the callout drives the production path with an HttpCalloutMock
 * (RLM_TaxTestFactory): the request side is asserted through the recorded callout, the response side
 * through the response type and its String form. The two no-lines tests set a mock but make no callout
 * (they assert none was recorded), and bodyOrNull is unit-tested directly, without a mock. A mock body
 * stands in for each engine response, a CalloutException-throwing mock for the failed callout (RLM_TAX_503), a
 * status outside 2xx for the error carrying that status, and 2xx bodies that lack a value, are not JSON
 * or do not fit the parser, or carry an "error" key reach the incomplete (RLM_TAX_502), unreadable (RLM_TAX_502) and
 * engine-error (RLM_TAX_501) branches. A fault in the adapter itself returns the adapter error (RLM_TAX_500).
 * Setters in getTax that no assertion covers (every other setter call is asserted): header
 * referenceDocumentCode, header exemptAmount, effectiveDate and transactionDate; imposition subType and
 * type, and the setImposition call; jurisdiction country, region, stateAssignedNumber, id and level; detail taxAuthorityTypeId,
 * taxId and taxRegionId (set from the detail's region code); line effectiveDate, isTaxable (set
 * from isItemTaxable), exemptAmount, productCode and quantity. The detail-level exemptAmount is covered by
 * getTax_detailExemptAmount_nullIsNotExempt_andAnAmountIsMapped (the canned payload's are all 0). Both status
 * branches are covered: the canned payload's Temporary maps to Uncommitted, and
 * getTax_committedStatus_mapsToCommitted supplies a body with status Committed; an unmapped status
 * leaves it unset (getTax_unmappedEngineStatus_leavesTheStatusUnset).
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
    static void getTax_withoutTransactionType_returnsTheAdapterErrorAfterCallout() {
        RLM_TaxTestFactory.RecordingHttpMock mock = new RLM_TaxTestFactory.RecordingHttpMock(200, RLM_TaxTestFactory.cannedSuccessBody());
        Test.setMock(HttpCalloutMock.class, mock);
        commercetax.CalculateTaxRequest request = RLM_TaxTestFactory.request(
            commercetax.CalculateTaxType.Estimated, 'DOC-NO-TYPE', RLM_TaxTestFactory.lines(232));
        request.taxTransactionType = null;

        commercetax.TaxEngineContext context = RLM_TaxTestFactory.context(request);
        Test.startTest();
        commercetax.TaxEngineResponse response = RLM_CalculateTaxService.getTax(context);
        Test.stopTest();

        // The platform always supplies a transaction type; without one the null reaches
        // setTaxTransactionType, which throws. That fault is returned as the adapter error, not thrown.
        Assert.isInstanceOfType(response, commercetax.ErrorResponse.class,
            'A fault in the adapter is an error response: ' + RLM_CalculateTaxService.lastDebugDetail);
        RLM_TaxTestFactory.assertResponseField(response, 'errorCode', 'RLM_TAX_500', 'The adapter error code is RLM_TAX_500.');
        RLM_TaxTestFactory.assertResponseField(response, 'errorMessage', RLM_CalculateTaxService.ADAPTER_ERROR_MESSAGE,
            'The adapter error carries its fixed sentence.');
        // The setter's exception type is platform behaviour (see the accepted risk in RLM_TaxTestFactory).
        Assert.isNotNull(RLM_CalculateTaxService.lastDebugDetail, 'The fault is logged.');
        Assert.isTrue(RLM_CalculateTaxService.lastDebugDetail.startsWith('adapter error: System.NullPointerException at '),
            'The fault type and where it was thrown are logged: ' + RLM_CalculateTaxService.lastDebugDetail
            + RLM_TaxTestFactory.SETTER_PREMISE_HINT);
        Assert.areEqual(1, mock.requests.size(), 'The failure comes after the engine callout.');
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
    // response; getTax returns an ErrorResponse when the response is null.
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
        RLM_TaxTestFactory.assertResponseField(response, 'errorCode', 'RLM_TAX_503', 'The error code is RLM_TAX_503.');
        RLM_TaxTestFactory.assertResponseField(response, 'errorMessage', RLM_CalculateTaxService.NO_RESPONSE_MESSAGE,
            'The error carries the no-response message.');
        Assert.areEqual(1, mock.requests.size(), 'The request was still sent before the response was found missing.');
        Assert.areEqual('no response', RLM_CalculateTaxService.lastDebugDetail, 'The missing response is logged.');
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
            'line taxDate' => '{"code":"X","status":"Temporary","totalAmount":10,"totalTax":1.5,"taxDate":"2020-07-15","date":"2020-07-15","lines":[{"lineNumber":"1","lineAmount":10,"taxCalculated":1.5,"isItemTaxable":true}]}',
            'isItemTaxable' => '{"code":"X","status":"Temporary","totalAmount":10,"totalTax":1.5,"taxDate":"2020-07-15","date":"2020-07-15","lines":[{"lineNumber":"1","lineAmount":10,"taxCalculated":1.5,"taxDate":"2020-07-15"}]}'
        };
        for (String missing : bodies.keySet()) {
            commercetax.CalculateTaxRequest request = RLM_TaxTestFactory.request(
                commercetax.CalculateTaxType.Estimated, 'DOC-INCOMPLETE', RLM_TaxTestFactory.lines(232));
            request.taxTransactionType = commercetax.TaxTransactionType.Debit;
            Test.setMock(HttpCalloutMock.class, new RLM_TaxTestFactory.RecordingHttpMock(200, bodies.get(missing)));

            RLM_CalculateTaxService.lastDebugDetail = null;
            commercetax.TaxEngineResponse response = RLM_CalculateTaxService.getTax(RLM_TaxTestFactory.context(request));

            Assert.isInstanceOfType(response, commercetax.ErrorResponse.class, missing + ': an incomplete response is an error response.');
            RLM_TaxTestFactory.assertResponseField(response, 'errorCode', 'RLM_TAX_502', missing + ': the error code is RLM_TAX_502.');
            RLM_TaxTestFactory.assertResponseField(response, 'errorMessage',
                RLM_CalculateTaxService.INCOMPLETE_RESPONSE_MESSAGE, missing + ': a fixed sentence.');
            Assert.areEqual('response value missing: ' + missing,
                RLM_CalculateTaxService.lastDebugDetail, missing + ': the missing value is logged, the body is not.');
        }
    }

    // A response with no line list, or a line with no tax details, still maps to a success response. The line
    // must still carry isItemTaxable: a line without it is the incomplete case above.
    @IsTest
    static void getTax_responseWithoutLinesOrDetails_mapsToASuccessResponse() {
        List<String> noLines = new List<String>{
            '{"code":"X","status":"Temporary","totalAmount":10,"totalTax":1.5,"taxDate":"2020-07-15","date":"2020-07-15"}',
            '{"code":"X","status":"Temporary","totalAmount":10,"totalTax":1.5,"taxDate":"2020-07-15","date":"2020-07-15","lines":[{"lineNumber":"1","lineAmount":10,"taxCalculated":1.5,"taxDate":"2020-07-15","isItemTaxable":true}]}'
        };
        for (String body : noLines) {
            commercetax.CalculateTaxRequest request = RLM_TaxTestFactory.request(
                commercetax.CalculateTaxType.Estimated, 'DOC-SPARSE', RLM_TaxTestFactory.lines(232));
            request.taxTransactionType = commercetax.TaxTransactionType.Debit;
            Test.setMock(HttpCalloutMock.class, new RLM_TaxTestFactory.RecordingHttpMock(200, body));

            RLM_CalculateTaxService.lastDebugDetail = null;
            commercetax.TaxEngineResponse response = RLM_CalculateTaxService.getTax(RLM_TaxTestFactory.context(request));

            Assert.isInstanceOfType(response, commercetax.CalculateTaxResponse.class, 'A sparse but complete response is mapped: ' + body);
        }
    }

    // Routing is on the top-level "error" key. The word "error" in a successful body (here a
    // reason) must not turn it into an error response.
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

    // Every error shape yields a RLM_TAX_501 response with the fixed sentence and never throws: a message,
    // details only, a bare string, an error object with neither message nor details, and an error of
    // an unexpected type. The engine's text stays out of the response and out of the debug log; only
    // its error codes are logged.
    @IsTest
    static void getTax_errorBodies_alwaysReturnTheFixedSentenceAndLogOnlyTheCodes() {
        String longCode = 'C'.repeat(RLM_CalculateTaxService.CODE_LENGTH_LIMIT + 1);
        Map<String, String> loggedByBody = new Map<String, String>{
            '{"error":{"code":"GetTaxError","message":"Address is invalid.","details":[]}}' => 'code: GetTaxError',
            '{"error":{"code":"EngineError","details":[{"message":"First."},{"message":""},{"message":"Last."}]}}' => 'code: EngineError; details: (none), (none), (none)',
            '{"error":"Bad credentials"}' => 'no error codes in the body',
            '{"error":{"code":"EngineError"}}' => 'code: EngineError',
            '{"error":{"code":"EngineError","details":[{"code":"DetailError"}]}}' => 'code: EngineError; details: DetailError',
            '{"error":{"code":"InvalidAddress","message":"123 Example St is not a valid address.","details":[{"code":"AddressRangeError","message":"123 Example St is out of range.","refersTo":"Addresses[0]"}]}}'
                => 'code: InvalidAddress; details: AddressRangeError (refersTo Addresses[0])',
            '{"error":{"code":"InvalidField","details":[{"code":"ValueRequiredError","refersTo":"Lines[1].quantity"}]}}'
                => 'code: InvalidField; details: ValueRequiredError (refersTo Lines[1].quantity)',
            '{"error":{"code":{"nested":"value"},"details":[5,{"code":7,"refersTo":"Lines[1]"}]}}' => 'code: (none); details: (none) (refersTo Lines[1])',
            '{"error":{"code":"' + longCode + '"}}' => 'code: (not logged: too long)',
            '{"error":{"code":"123 Example St is invalid","details":[{"code":"EngineError","refersTo":"Example St"}]}}'
                => 'code: (not logged: not a code); details: EngineError (refersTo (not logged: not a code))',
            '{"error":{"code":""}}' => 'code: (not logged: not a code)',
            '{"error":{"code":"94105"}}' => 'code: (not logged: not a code)',
            // Values that are not AvaTax's shapes: a VAT id, an unspaced postal code, a customer code,
            // a lower-case or one-letter code, and a field path with a hyphen or a value index.
            '{"error":{"code":"GB123456789","details":[{"code":"DetailError","refersTo":"GB123456789"}]}}'
                => 'code: (not logged: not a code); details: DetailError (refersTo (not logged: not a code))',
            '{"error":{"code":"SW1A1AA","details":[{"code":"DetailError","refersTo":"SW1A1AA"}]}}'
                => 'code: (not logged: not a code); details: DetailError (refersTo (not logged: not a code))',
            '{"error":{"code":"CUST-00123","details":[{"code":"DetailError","refersTo":"CUST-00123"}]}}'
                => 'code: (not logged: not a code); details: DetailError (refersTo (not logged: not a code))',
            '{"error":{"code":"engineError","details":[{"code":"E","refersTo":"Lines[x]"}]}}'
                => 'code: (not logged: not a code); details: (not logged: not a code) (refersTo (not logged: not a code))',
            '{"error":{"code":"InvalidAddress","details":[{"code":"AddressRangeError","refersTo":"Addresses.ShipTo.Line1"},{"code":"DetailError","refersTo":"Lines[0].line12"}]}}'
                => 'code: InvalidAddress; details: AddressRangeError (refersTo Addresses.ShipTo.Line1), DetailError (refersTo (not logged: not a code))',
            // Letters alone have the shape of an error name or a field path, so a name is logged.
            '{"error":{"code":"Acme","details":[{"code":"DetailError","refersTo":"Acme"},{"code":"DetailError","refersTo":"Jane.Doe"}]}}'
                => 'code: Acme; details: DetailError (refersTo Acme), DetailError (refersTo Jane.Doe)',
            // All-caps letters pass too, so a name or a region or country code in capitals is logged.
            '{"error":{"code":"ACME","details":[{"code":"WA","refersTo":"GB"}]}}'
                => 'code: ACME; details: WA (refersTo GB)',
            // A field path's word can end in one digit (line1), so a short value of that shape is logged.
            '{"error":{"code":"DetailError","details":[{"code":"DetailError","refersTo":"SW1"}]}}'
                => 'code: DetailError; details: DetailError (refersTo SW1)',
            '{"error":{}}' => 'code: (none)',
            '{"error":""}' => 'no error codes in the body',
            '{"error":42}' => 'no error codes in the body'
        };
        for (String body : loggedByBody.keySet()) {
            commercetax.CalculateTaxRequest request = RLM_TaxTestFactory.request(
                commercetax.CalculateTaxType.Estimated, 'DOC-ERROR-SHAPE', RLM_TaxTestFactory.lines(232));
            request.taxTransactionType = commercetax.TaxTransactionType.Debit;
            Test.setMock(HttpCalloutMock.class, new RLM_TaxTestFactory.RecordingHttpMock(200, body));

            RLM_CalculateTaxService.lastDebugDetail = null;
            commercetax.TaxEngineResponse response = RLM_CalculateTaxService.getTax(RLM_TaxTestFactory.context(request));

            Assert.isInstanceOfType(response, commercetax.ErrorResponse.class, body + ': an error response.');
            RLM_TaxTestFactory.assertResponseField(response, 'errorCode', 'RLM_TAX_501', body + ': the error code is RLM_TAX_501.');
            RLM_TaxTestFactory.assertResponseField(response, 'errorMessage', RLM_CalculateTaxService.ENGINE_ERROR_MESSAGE,
                body + ': the fixed sentence.');
            Assert.areEqual('engine error; ' + loggedByBody.get(body), RLM_CalculateTaxService.lastDebugDetail,
                body + ': only the error codes are logged for the administrator.');
            for (String text : new List<String>{ 'Example St', 'is invalid', 'not a valid', 'First.', 'Last.', 'Bad credentials', 'nested',
                    'GB123456789', 'SW1A1AA', 'CUST-00123', 'engineError', 'Lines[x]' }) {
                Assert.isFalse(RLM_CalculateTaxService.lastDebugDetail.contains(text), body + ': no message text is logged: ' + text);
            }
        }
    }

    // A body that is not JSON cannot be read: a RLM_TAX_502 error response, not a JSONException. An empty or
    // missing body is the same 502 (see the 2xx empty-body case in the non-2xx test).
    @IsTest
    static void getTax_bodyThatIsNotJson_returnsAnUnreadableResponseError() {
        for (String body : new List<String>{ '<html>Bad gateway</html>', '[1,2]', ' ', '' }) {
            commercetax.CalculateTaxRequest request = RLM_TaxTestFactory.request(
                commercetax.CalculateTaxType.Estimated, 'DOC-NOT-JSON', RLM_TaxTestFactory.lines(232));
            request.taxTransactionType = commercetax.TaxTransactionType.Debit;
            Test.setMock(HttpCalloutMock.class, new RLM_TaxTestFactory.RecordingHttpMock(200, body));

            RLM_CalculateTaxService.lastDebugDetail = null;
            commercetax.TaxEngineResponse response = RLM_CalculateTaxService.getTax(RLM_TaxTestFactory.context(request));

            Assert.isInstanceOfType(response, commercetax.ErrorResponse.class, body + ': an error response.');
            RLM_TaxTestFactory.assertResponseField(response, 'errorCode', 'RLM_TAX_502', body + ': the error code is RLM_TAX_502.');
            RLM_TaxTestFactory.assertResponseField(response, 'errorMessage',
                RLM_CalculateTaxService.UNREADABLE_RESPONSE_MESSAGE, body + ': the message.');
            Assert.areEqual('response is not a JSON object', RLM_CalculateTaxService.lastDebugDetail,
                body + ': the failure is logged, the body is not.');
        }
    }

    // A success body whose list field is not a list of objects (a number, an array of numbers) used to
    // send the success parser past the end of the input until the CPU limit ended the transaction. It
    // is the RLM_TAX_502 unreadable response, and the log names the field.
    @IsTest
    static void getTax_successBodyOfTheWrongShape_returnsAnUnreadableResponseError() {
        String head = '{"code":"X","status":"Temporary","totalAmount":10,"totalTax":1.5,"taxDate":"2020-07-15","date":"2020-07-15",';
        String line = '"lineNumber":"1","lineAmount":10,"taxCalculated":1.5,"taxDate":"2020-07-15","isItemTaxable":true';
        List<List<String>> cases = new List<List<String>>{
            new List<String>{ '{"lines":5}', 'lines' },
            new List<String>{ '{"lines":[1]}', 'lines' },
            new List<String>{ '{"lines":{}}', 'lines' },
            new List<String>{ '{"addresses":5}', 'addresses' },
            new List<String>{ '{"addresses":["a"]}', 'addresses' },
            new List<String>{ '{"summary":5}', 'summary' },
            new List<String>{ '{"messages":[1]}', 'messages' },
            new List<String>{ head + '"lines":[{' + line + ',"details":5}]}', 'line details' },
            new List<String>{ head + '"lines":[{' + line + ',"details":[1]}]}', 'line details' },
            new List<String>{ head + '"lines":[{' + line + '},[]]}', 'lines' }
        };
        for (List<String> c : cases) {
            commercetax.TaxEngineResponse response = getTaxAnswering(200, c[0]);

            Assert.isInstanceOfType(response, commercetax.ErrorResponse.class, c[0] + ': an error response.');
            RLM_TaxTestFactory.assertResponseField(response, 'errorCode', 'RLM_TAX_502', c[0] + ': the error code is RLM_TAX_502.');
            RLM_TaxTestFactory.assertResponseField(response, 'errorMessage',
                RLM_CalculateTaxService.UNREADABLE_RESPONSE_MESSAGE, c[0] + ': the unreadable message.');
            Assert.areEqual('response field not a list of objects: ' + c[1], RLM_CalculateTaxService.lastDebugDetail,
                c[0] + ': the field is logged, the body is not.');
        }
    }

    // A text field that holds an object or an array is refused by the success parser rather than read
    // as its opening token, which used to make the parser read the nested fields as the parent's.
    @IsTest
    static void getTax_successBodyWithAnObjectForAText_returnsAnUnreadableResponseError() {
        for (String body : new List<String>{
            '{"code":{"totalAmount":99},"status":"Temporary","totalAmount":10,"totalTax":1.5,"taxDate":"2020-07-15","date":"2020-07-15","lines":[]}',
            '{"code":"X","status":["Temporary"],"totalAmount":10,"totalTax":1.5,"taxDate":"2020-07-15","date":"2020-07-15","lines":[]}'
        }) {
            commercetax.TaxEngineResponse response = getTaxAnswering(200, body);

            Assert.isInstanceOfType(response, commercetax.ErrorResponse.class, body + ': an error response.');
            RLM_TaxTestFactory.assertResponseField(response, 'errorCode', 'RLM_TAX_502', body + ': the error code is RLM_TAX_502.');
            RLM_TaxTestFactory.assertResponseField(response, 'errorMessage',
                RLM_CalculateTaxService.UNREADABLE_RESPONSE_MESSAGE, body + ': the unreadable message.');
            Assert.areEqual('response does not fit the success parser: System.JSONException', RLM_CalculateTaxService.lastDebugDetail,
                body + ': only the parser failure type is logged.');
        }
    }

    // A long engine page is not logged at all: only the status and the fact that the body is not JSON.
    @IsTest
    static void getTax_aLongErrorPage_isNotLogged() {
        String body = '<html>' + 'x'.repeat(5000) + '</html>';
        getTaxAnswering(500, body);
        Assert.areEqual('HTTP status 500; body empty or not JSON', RLM_CalculateTaxService.lastDebugDetail,
            'The page is not logged.');
    }

    // A detail with no exempt amount is not exempt (null is not "exempt"); a detail with one maps
    // the amount and no invented reason.
    @IsTest
    static void getTax_detailExemptAmount_nullIsNotExempt_andAnAmountIsMapped() {
        String head = '{"code":"X","status":"Temporary","totalAmount":10,"totalTax":1.5,"taxDate":"2020-07-15","date":"2020-07-15",'
            + '"lines":[{"lineNumber":"1","lineAmount":10,"taxCalculated":1.5,"taxDate":"2020-07-15","isItemTaxable":true,"details":[';
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

            RLM_CalculateTaxService.lastDebugDetail = null;
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
            'line taxDate' => head + '"taxDate":"2020-07-15","date":"2020-07-15","lines":[{"lineNumber":"1","lineAmount":10,"taxCalculated":1.5,"taxDate":"not a date","isItemTaxable":true}]}'
        };
        for (String field : bodies.keySet()) {
            Test.setMock(HttpCalloutMock.class, new RLM_TaxTestFactory.RecordingHttpMock(200, bodies.get(field)));
            commercetax.CalculateTaxRequest request = RLM_TaxTestFactory.request(
                commercetax.CalculateTaxType.Estimated, 'DOC-BAD-DATE', RLM_TaxTestFactory.lines(232));
            request.taxTransactionType = commercetax.TaxTransactionType.Debit;

            RLM_CalculateTaxService.lastDebugDetail = null;
            commercetax.TaxEngineResponse response = RLM_CalculateTaxService.getTax(RLM_TaxTestFactory.context(request));

            Assert.isInstanceOfType(response, commercetax.ErrorResponse.class, field + ': an invalid date is an error response.');
            RLM_TaxTestFactory.assertResponseField(response, 'errorCode', 'RLM_TAX_502', field + ': the error code is RLM_TAX_502.');
            RLM_TaxTestFactory.assertResponseField(response, 'errorMessage',
                RLM_CalculateTaxService.INVALID_DATE_MESSAGE, field + ': a fixed sentence.');
            Assert.areEqual('response value not a date: ' + field,
                RLM_CalculateTaxService.lastDebugDetail, field + ': the invalid date is logged, the body is not.');
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

    private static commercetax.TaxEngineResponse getTaxAnswering(Integer statusCode, String body) {
        commercetax.CalculateTaxRequest request = RLM_TaxTestFactory.request(
            commercetax.CalculateTaxType.Estimated, 'DOC-STATUS', RLM_TaxTestFactory.lines(232));
        request.taxTransactionType = commercetax.TaxTransactionType.Debit;
        Test.setMock(HttpCalloutMock.class, new RLM_TaxTestFactory.RecordingHttpMock(statusCode, body));
        RLM_CalculateTaxService.lastDebugDetail = null;
        return RLM_CalculateTaxService.getTax(RLM_TaxTestFactory.context(request));
    }

    // A status outside 2xx is an error carrying that status, whatever the body holds: a body that
    // would map as a success, one that is not JSON, or an engine error body, whose text stays out of
    // the response and the debug log; only its error codes are logged.
    @IsTest
    static void getTax_non2xxStatus_returnsAnErrorCarryingTheStatus() {
        String successBody = '{"code":"X","status":"Temporary","totalAmount":10,"totalTax":1.5,'
            + '"taxDate":"2020-07-15","date":"2020-07-15","lines":[]}';
        Map<String, String> loggedByBody = new Map<String, String>{
            successBody => 'no error codes in the body',
            '{"message":"Internal error"}' => 'no error codes in the body',
            '<html>Server error</html>' => 'body empty or not JSON',
            '{"error":{"code":"EngineError","message":"Engine down.","details":[]}}' => 'code: EngineError'
        };
        for (String body : loggedByBody.keySet()) {
            commercetax.TaxEngineResponse response = getTaxAnswering(500, body);

            Assert.isInstanceOfType(response, commercetax.ErrorResponse.class, body + ': an error response.');
            RLM_TaxTestFactory.assertResponseField(response, 'errorCode', '500', body + ': the code is the HTTP status.');
            RLM_TaxTestFactory.assertResponseField(response, 'errorMessage', RLM_CalculateTaxService.HTTP_ERROR_PREFIX + '500.',
                body + ': the message.');
            Assert.areEqual('HTTP status 500; ' + loggedByBody.get(body), RLM_CalculateTaxService.lastDebugDetail,
                body + ': only the error codes are logged.');
        }
        // The mock leaves a null body unset, so getBody returns an empty string (see RecordingHttpMock).
        commercetax.TaxEngineResponse empty = getTaxAnswering(504, null);
        Assert.isInstanceOfType(empty, commercetax.ErrorResponse.class, 'No body: an error response.');
        RLM_TaxTestFactory.assertResponseField(empty, 'errorCode', '504',
            'A status outside 2xx with no body keeps its status.');
        RLM_TaxTestFactory.assertResponseField(empty, 'errorMessage', RLM_CalculateTaxService.HTTP_ERROR_PREFIX + '504.',
            'No body: the message names the status.');
        Assert.areEqual('HTTP status 504; body empty or not JSON', RLM_CalculateTaxService.lastDebugDetail,
            'No body: logged as having no codes.');
        commercetax.TaxEngineResponse emptySuccess = getTaxAnswering(200, null);
        Assert.isInstanceOfType(emptySuccess, commercetax.ErrorResponse.class, 'A 2xx with no body is an error response.');
        RLM_TaxTestFactory.assertResponseField(emptySuccess, 'errorCode', 'RLM_TAX_502', 'A 2xx with no body is unreadable.');
        RLM_TaxTestFactory.assertResponseField(emptySuccess, 'errorMessage', RLM_CalculateTaxService.UNREADABLE_RESPONSE_MESSAGE,
            'A 2xx with no body carries the unreadable-response message.');
        Assert.areEqual('response is not a JSON object', RLM_CalculateTaxService.lastDebugDetail,
            'A 2xx with no body is logged as unreadable.');
        commercetax.TaxEngineResponse unauthorized = getTaxAnswering(401, '{"error":"Bad credentials"}');
        RLM_TaxTestFactory.assertResponseField(unauthorized, 'errorCode', '401', 'A 401 keeps its status.');
        RLM_TaxTestFactory.assertResponseField(unauthorized, 'errorMessage', RLM_CalculateTaxService.HTTP_ERROR_PREFIX + '401.',
            'A 401 names its status; the engine text goes to the debug log.');
        Assert.areEqual('HTTP status 401; no error codes in the body', RLM_CalculateTaxService.lastDebugDetail,
            'The 401 text is not logged.');
        // A 204 No Content is a 2xx without a result: a failure on purpose, not an empty success.
        commercetax.TaxEngineResponse noContent = getTaxAnswering(204, null);
        Assert.isInstanceOfType(noContent, commercetax.ErrorResponse.class, 'A 204 is an error response.');
        RLM_TaxTestFactory.assertResponseField(noContent, 'errorCode', 'RLM_TAX_502', 'A 204 is unreadable.');
        RLM_TaxTestFactory.assertResponseField(noContent, 'errorMessage', RLM_CalculateTaxService.UNREADABLE_RESPONSE_MESSAGE,
            'A 204 carries the unreadable-response message.');
        Assert.areEqual('response is not a JSON object', RLM_CalculateTaxService.lastDebugDetail,
            'A 204 is logged as unreadable.');
    }

    // A 2xx JSON body whose field does not fit the success parser used to throw a JSONException out
    // of getTax; it is the RLM_TAX_502 unreadable response.
    @IsTest
    static void getTax_successBodyWithAFieldOfTheWrongType_returnsAnUnreadableResponseError() {
        commercetax.TaxEngineResponse response = getTaxAnswering(200, '{"code":"X","status":"Temporary",'
            + '"totalAmount":"abc","totalTax":1.5,"taxDate":"2020-07-15","date":"2020-07-15","lines":[]}');

        Assert.isInstanceOfType(response, commercetax.ErrorResponse.class, 'An unparseable body is an error response.');
        RLM_TaxTestFactory.assertResponseField(response, 'errorCode', 'RLM_TAX_502', 'The error code is RLM_TAX_502.');
        RLM_TaxTestFactory.assertResponseField(response, 'errorMessage',
            RLM_CalculateTaxService.UNREADABLE_RESPONSE_MESSAGE, 'The unreadable message.');
        Assert.areEqual('response does not fit the success parser: System.JSONException', RLM_CalculateTaxService.lastDebugDetail,
            'Only the parser failure type is logged.');
        Assert.isFalse(RLM_CalculateTaxService.lastDebugDetail.contains('abc'), 'The refused value is not logged.');
        Assert.isFalse(RLM_CalculateTaxService.lastDebugDetail.contains('Temporary'), 'A success-shaped body is not logged.');
    }

    // Only Temporary and Committed are mapped; any other engine status leaves the response status unset.
    @IsTest
    static void getTax_unmappedEngineStatus_leavesTheStatusUnset() {
        commercetax.TaxEngineResponse response = getTaxAnswering(200, '{"code":"X","status":"Saved",'
            + '"totalAmount":10,"totalTax":1.5,"taxDate":"2020-07-15","date":"2020-07-15","lines":[]}');

        Assert.isInstanceOfType(response, commercetax.CalculateTaxResponse.class, 'The body still maps.');
        RLM_TaxTestFactory.assertResponseField(response, 'status', '<null>', 'An unmapped engine status sets no status.');
        Assert.areEqual('engine status not mapped, status left unset: Saved', RLM_CalculateTaxService.lastDebugDetail,
            'The engine status is logged, not mapped.');
    }

    // Any date text Date.valueOf rejects is named, whatever exception it raises, and never throws.
    @IsTest
    static void invalidResponseDate_namesAnyUnreadableDateWithoutThrowing() {
        for (String text : new List<String>{ 'not a date', '2020-13-45', '2020-07' }) {
            RLM_JsonSuccessParser parsed = RLM_JsonSuccessParser.parse(
                '{"taxDate":' + JSON.serialize(text) + ',"date":"2020-07-15"}');
            Assert.areEqual('taxDate', RLM_CalculateTaxService.invalidResponseDate(parsed), text + ': named as invalid.');
        }
        RLM_JsonSuccessParser valid = RLM_JsonSuccessParser.parse('{"taxDate":"2020-07-15","date":"2020-07-15"}');
        Assert.isNull(RLM_CalculateTaxService.invalidResponseDate(valid), 'Valid dates are not named.');
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
