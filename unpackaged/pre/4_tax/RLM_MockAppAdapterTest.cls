/**
 * Asserts which response each scenario produces (ErrorResponse vs CalculateTaxResponse,
 * null, or an exception) and, through the response's String form, the codes and values
 * the adapter set on it.
 */
@IsTest
private with sharing class RLM_MockAppAdapterTest {

    private static commercetax.TaxEngineResponse process(commercetax.CalculateTaxRequest request) {
        return new RLM_MockAppAdapter().processRequest(RLM_TaxTestFactory.context(request));
    }

    /** Line 1 has a number and an effective date; line 2 has neither. */
    private static commercetax.CalculateTaxRequest requestFor(String documentCode) {
        return RLM_TaxTestFactory.request(
            commercetax.CalculateTaxType.Estimated,
            documentCode,
            new List<commercetax.TaxLineItemRequest>{
                RLM_TaxTestFactory.line(100, '1', RLM_TaxTestFactory.DATE_2001),
                RLM_TaxTestFactory.line(250, null, null)
            });
    }

    @IsTest
    static void processRequest_simulatedFailureCodes_returnErrors() {
        List<String> failureCodes = new List<String>{
            'TaxEngineError',
            'TaxEngineErrorWithSuffix',
            'simulateValidationFailureInAdapter',
            'simulateTaxEngineProcessFailure'
        };
        Map<String, commercetax.TaxEngineResponse> responses = new Map<String, commercetax.TaxEngineResponse>();

        Test.startTest();
        for (String code : failureCodes) {
            responses.put(code, process(requestFor(code)));
        }
        Test.stopTest();

        for (String code : failureCodes) {
            Assert.isInstanceOfType(responses.get(code), commercetax.ErrorResponse.class,
                code + ' should produce an ErrorResponse.');
        }
        RLM_TaxTestFactory.assertResponseField(responses.get('TaxEngineError'), 'errorCode', '504', 'TaxEngineError');
        RLM_TaxTestFactory.assertResponseField(responses.get('TaxEngineErrorWithSuffix'), 'errorCode', '504',
            'Any document code starting with TaxEngineError');
        RLM_TaxTestFactory.assertResponseField(responses.get('simulateValidationFailureInAdapter'), 'errorCode', '400',
            'Validation failure');
        RLM_TaxTestFactory.assertResponseField(responses.get('simulateTaxEngineProcessFailure'), 'errorCode', '500',
            'Process failure');
    }

    @IsTest
    static void processRequest_referenceDocumentCodeError_returnsError() {
        commercetax.CalculateTaxRequest request = requestFor('DOC-APP-REF');
        request.referenceDocumentCode = 'simulateTaxEngineError';

        Test.startTest();
        commercetax.TaxEngineResponse response = process(request);
        Test.stopTest();

        Assert.isInstanceOfType(response, commercetax.ErrorResponse.class,
            'A simulateTaxEngineError reference document code produces an ErrorResponse.');
        RLM_TaxTestFactory.assertResponseField(response, 'errorCode', '504', 'The reference-code error is a 504.');
    }

    @IsTest
    static void processRequest_simulatedUnhandledException_throwsMathException() {
        Exception caught;
        Test.startTest();
        try {
            process(requestFor('simulateUnhandledExceptionInAdapter'));
        } catch (Exception e) {
            caught = e;
        }
        Test.stopTest();

        Assert.isNotNull(caught, 'The adapter should surface an unhandled exception.');
        Assert.isInstanceOfType(caught, MathException.class, 'The simulated failure is a divide by zero: ' + caught);
    }

    @IsTest
    static void processRequest_errorTriggeringLineAmounts_returnErrors() {
        List<Double> errorAmounts = new List<Double>{
            Double.valueOf('100.999'),
            Double.valueOf('-100.999'),
            Double.valueOf('101'),
            Double.valueOf('-101')
        };
        List<commercetax.TaxEngineResponse> responses = new List<commercetax.TaxEngineResponse>();

        Test.startTest();
        for (Double amount : errorAmounts) {
            responses.add(process(RLM_TaxTestFactory.request(
                commercetax.CalculateTaxType.Estimated, 'DOC-APP-AMOUNT', RLM_TaxTestFactory.lines(amount))));
        }
        Test.stopTest();

        for (Integer i = 0; i < errorAmounts.size(); i++) {
            Assert.isInstanceOfType(responses[i], commercetax.ErrorResponse.class,
                'Line amount ' + errorAmounts[i] + ' should produce an ErrorResponse.');
            RLM_TaxTestFactory.assertResponseField(responses[i], 'errorCode', '500', 'Line amount ' + errorAmounts[i]);
        }
    }

    @IsTest
    static void processRequest_documentCodeVariants_returnCalculateTaxResponses() {
        commercetax.CalculateTaxRequest withDocumentCode = requestFor('DOC-APP-1');
        withDocumentCode.isCommit = true;
        withDocumentCode.transactionDate = RLM_TaxTestFactory.DATE_2001;
        withDocumentCode.taxTransactionType = commercetax.TaxTransactionType.Credit;
        withDocumentCode.currencyIsoCode = 'EUR';

        commercetax.CalculateTaxRequest emptyDocumentCode = requestFor('simulateEmptyDocumentCode');
        emptyDocumentCode.isCommit = false;
        emptyDocumentCode.currencyIsoCode = '';

        commercetax.CalculateTaxRequest referenceEntityOnly = requestFor(null);
        referenceEntityOnly.referenceEntityId = 'REF-APP-1';
        referenceEntityOnly.transactionDate = null;
        referenceEntityOnly.taxTransactionType = null;
        referenceEntityOnly.currencyIsoCode = null;

        commercetax.CalculateTaxRequest noCodes = requestFor(null);
        noCodes.referenceEntityId = null;

        List<commercetax.CalculateTaxRequest> requests = new List<commercetax.CalculateTaxRequest>{
            withDocumentCode, emptyDocumentCode, referenceEntityOnly, noCodes
        };
        List<commercetax.TaxEngineResponse> responses = new List<commercetax.TaxEngineResponse>();

        Test.startTest();
        for (commercetax.CalculateTaxRequest request : requests) {
            responses.add(process(request));
        }
        Test.stopTest();

        for (Integer i = 0; i < responses.size(); i++) {
            Assert.isInstanceOfType(responses[i], commercetax.CalculateTaxResponse.class,
                'Variant ' + i + ' returns a calculated response.');
        }

        // Explicit values are echoed.
        RLM_TaxTestFactory.assertResponseField(responses[0], 'documentCode', 'DOC-APP-1', 'An explicit document code is echoed.');
        RLM_TaxTestFactory.assertResponseField(responses[0], 'status', 'Committed', 'isCommit=true is Committed.');
        RLM_TaxTestFactory.assertResponseField(responses[0], 'taxTransactionType', 'Credit', 'The transaction type is echoed.');
        RLM_TaxTestFactory.assertResponseField(responses[0], 'currencyIsoCode', 'EUR', 'An explicit currency is echoed.');
        // A 2001 date can only come from the request (the defaults are now): the transaction date
        // and line 1's effective date are echoed.
        RLM_TaxTestFactory.assertResponseFieldMatches(responses[0], 'transactionDate', RLM_TaxTestFactory.YEAR_2001,
            'The request transaction date is echoed.');
        RLM_TaxTestFactory.assertResponseFieldMatches(responses[0], 'effectiveDate', RLM_TaxTestFactory.YEAR_2001,
            'Line 1 keeps its effective date.');
        // Line 1's number is echoed; line 2's null number is passed through (the adapter computes
        // a fallback number but never uses it).
        Assert.areEqual(1, RLM_TaxTestFactory.countResponseField(responses[0], 'lineNumber', '1'), 'Line 1 keeps its number.');
        Assert.areEqual(1, RLM_TaxTestFactory.countResponseField(responses[0], 'lineNumber', '<null>'),
            'Known gap: a line without a number keeps a null number; the computed fallback is unused. '
            + 'Update this test when it is fixed.');

        // The empty-document-code scenario.
        RLM_TaxTestFactory.assertResponseField(responses[1], 'documentCode', '', 'The document code is set to empty.');
        RLM_TaxTestFactory.assertResponseField(responses[1], 'status', 'Uncommitted', 'isCommit=false is Uncommitted.');
        RLM_TaxTestFactory.assertResponseField(responses[1], 'currencyIsoCode', 'USD', 'A blank currency defaults to USD.');

        // Defaults when only a reference entity is given.
        RLM_TaxTestFactory.assertResponseField(responses[2], 'documentCode', 'REF-APP-1',
            'Without a document code the reference entity id becomes the document code.');
        RLM_TaxTestFactory.assertResponseField(responses[2], 'taxTransactionType', 'Debit',
            'A missing transaction type defaults to Debit.');
        RLM_TaxTestFactory.assertResponseFieldMatches(responses[2], 'transactionDate', RLM_TaxTestFactory.NOT_NULL,
            'A missing transaction date defaults to now.');
        RLM_TaxTestFactory.assertResponseField(responses[2], 'currencyIsoCode', 'USD', 'A null currency defaults to USD.');

        // No codes at all: the generated code is getRandomInteger(0, max), which is always 0.
        RLM_TaxTestFactory.assertResponseField(responses[3], 'documentCode', '0',
            'Known gap: the generated document code is always 0 (getRandomInteger returns min). '
            + 'Update this test when it is fixed.');
    }

    @IsTest
    static void processRequest_nullAmountDetailsScenario_throwsTaxApiException() {
        Exception caught;
        Test.startTest();
        try {
            process(requestFor('SetsNullForResponseWithException'));
        } catch (Exception e) {
            caught = e;
        }
        Test.stopTest();

        Assert.isNotNull(caught, 'Null amount details are rejected by the response setter.');
        // Assert.isInstanceOfType(caught, commercetax.TaxApiException.class) does not compile:
        // "Type is not visible: commercetax.TaxApiException". Match the type name instead.
        Assert.areEqual('commercetax.TaxApiException', caught.getTypeName(), 'The platform setter throws: ' + caught);
        Assert.isTrue(caught.getMessage().contains('Amount details cannot be null'), caught.getMessage());
    }

    @IsTest
    static void processRequest_nullSubResponses_leavesThemNullOnEachLine() {
        Test.startTest();
        commercetax.TaxEngineResponse response = process(requestFor('SetsNullForResponseWithoutException'));
        Test.stopTest();

        Assert.isInstanceOfType(response, commercetax.CalculateTaxResponse.class, 'A calculated response is returned.');
        // Two request lines, one tax detail each; the header addresses are still set.
        Assert.areEqual(2, RLM_TaxTestFactory.countResponseField(response, 'addresses', '<null>'),
            'Both lines leave their addresses null.');
        Assert.areEqual(2, RLM_TaxTestFactory.countResponseField(response, 'imposition', '<null>'),
            'Both tax details leave imposition null.');
        Assert.areEqual(2, RLM_TaxTestFactory.countResponseField(response, 'jurisdiction', '<null>'),
            'Both tax details leave jurisdiction null.');
    }

    @IsTest
    static void processRequest_noLinesScenario_omitsLineItems() {
        Test.startTest();
        commercetax.TaxEngineResponse response = process(requestFor('nolines'));
        Test.stopTest();

        Assert.isInstanceOfType(response, commercetax.CalculateTaxResponse.class, 'A calculated response is returned.');
        RLM_TaxTestFactory.assertResponseField(response, 'lineItems', '<null>', 'The nolines scenario sets no line items.');
        RLM_TaxTestFactory.assertResponseField(response, 'documentCode', 'nolines', 'The header is still built.');
    }

    @IsTest
    static void processRequest_nullRequestType_returnsNull() {
        Test.startTest();
        commercetax.TaxEngineResponse response =
            new RLM_MockAppAdapter().processRequest(RLM_TaxTestFactory.contextWithoutRequestType(requestFor('DOC-APP-2')));
        Test.stopTest();

        Assert.isNull(response, 'Only CalculateTax requests are answered.');
    }

    @IsTest
    static void getRandomInteger_alwaysReturnsMin() {
        Test.startTest();
        Integer fromThree = RLM_MockAppAdapter.getRandomInteger(3, 10);
        Integer fromZero = RLM_MockAppAdapter.getRandomInteger(0, 2147483647);
        Test.stopTest();

        // Integer.valueOf(Math.random()) truncates a value in [0, 1) to 0 (anonymous Apex:
        // Integer.valueOf(0.9d) and Integer.valueOf(0.999999d) both return 0), so the result is always min.
        Assert.areEqual(3, fromThree, 'Known gap: getRandomInteger always returns min. Update this test when it is fixed.');
        Assert.areEqual(0, fromZero, 'Known gap: getRandomInteger always returns min. Update this test when it is fixed.');
    }
}
