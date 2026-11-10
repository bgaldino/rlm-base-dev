/**
 * Asserts which response each documentCode scenario produces (ErrorResponse vs
 * CalculateTaxResponse, null, or an exception) and, through the response's String form,
 * the codes and values the adapter set on it.
 */
@IsTest
private with sharing class RLM_MockTaxAdapterTest {

    private static commercetax.TaxEngineResponse process(commercetax.CalculateTaxRequest request) {
        return new RLM_MockTaxAdapter().processRequest(RLM_TaxTestFactory.context(request));
    }

    private static commercetax.CalculateTaxRequest requestFor(String documentCode) {
        return RLM_TaxTestFactory.request(
            commercetax.CalculateTaxType.Estimated,
            documentCode,
            new List<commercetax.TaxLineItemRequest>{
                RLM_TaxTestFactory.line(100, '1', null),
                RLM_TaxTestFactory.line(250, '2', null)
            });
    }

    @IsTest
    static void processRequest_missingDocumentCode_returnsError() {
        Test.startTest();
        commercetax.TaxEngineResponse response = process(requestFor(null));
        Test.stopTest();

        Assert.isInstanceOfType(response, commercetax.ErrorResponse.class, 'documentCode is mandatory for this adapter.');
        RLM_TaxTestFactory.assertResponseField(response, 'errorCode', '404', 'A missing document code is a 404.');
    }

    @IsTest
    static void processRequest_simulatedFailureCodes_returnErrors() {
        List<String> failureCodes = new List<String>{
            'TaxEngineError',
            'simulateValidationFailureInAdapter',
            'simulateMalformedErrorInAdapter',
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
        RLM_TaxTestFactory.assertResponseField(responses.get('simulateValidationFailureInAdapter'), 'errorCode', '400',
            'Validation failure');
        RLM_TaxTestFactory.assertResponseField(responses.get('simulateMalformedErrorInAdapter'), 'errorCode', '',
            'The malformed error carries no error code.');
        RLM_TaxTestFactory.assertResponseField(responses.get('simulateMalformedErrorInAdapter'), 'errorMessage',
            'malformed adapter error response', 'The malformed error keeps its message.');
        RLM_TaxTestFactory.assertResponseField(responses.get('simulateTaxEngineProcessFailure'), 'errorCode', '500',
            'Process failure');
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
    static void processRequest_uncommittedDefaults_returnsCalculateTaxResponse() {
        commercetax.CalculateTaxRequest request = requestFor('DOC-MOCK-1');
        request.isCommit = false;
        request.transactionDate = null;
        request.taxTransactionType = null;
        request.currencyIsoCode = null;

        Test.startTest();
        commercetax.TaxEngineResponse response = process(request);
        Test.stopTest();

        Assert.isInstanceOfType(response, commercetax.CalculateTaxResponse.class,
            'A normal document code is answered with a calculated response.');
        RLM_TaxTestFactory.assertResponseField(response, 'documentCode', 'DOC-MOCK-1', 'The document code is echoed.');
        RLM_TaxTestFactory.assertResponseField(response, 'status', 'Uncommitted', 'isCommit=false is Uncommitted.');
        RLM_TaxTestFactory.assertResponseField(response, 'taxTransactionType', 'Debit',
            'A missing transaction type defaults to Debit.');
        RLM_TaxTestFactory.assertResponseFieldMatches(response, 'transactionDate', RLM_TaxTestFactory.NOT_NULL,
            'A missing transaction date defaults to now.');
        RLM_TaxTestFactory.assertResponseField(response, 'currencyIsoCode', 'USD', 'A null currency defaults to USD.');
        RLM_TaxTestFactory.assertResponseField(response, 'description', 'description',
            'A seller other than testSellerCode gets the default description.');
        Assert.areEqual(1, RLM_TaxTestFactory.countResponseField(response, 'lineNumber', '1'), 'Line 1 is answered.');
        Assert.areEqual(1, RLM_TaxTestFactory.countResponseField(response, 'lineNumber', '2'), 'Line 2 is answered.');
    }

    @IsTest
    static void processRequest_committedWithExplicitValues_echoesThem() {
        commercetax.CalculateTaxRequest request = requestFor('DOC-MOCK-2');
        request.isCommit = true;
        request.sellerDetails = new commercetax.TaxSellerDetailsRequest('testSellerCode');
        request.transactionDate = RLM_TaxTestFactory.DATE_2001;
        request.taxTransactionType = commercetax.TaxTransactionType.Credit;
        request.currencyIsoCode = 'EUR';

        Test.startTest();
        commercetax.TaxEngineResponse response = process(request);
        Test.stopTest();

        Assert.isInstanceOfType(response, commercetax.CalculateTaxResponse.class, 'A calculated response is returned.');
        RLM_TaxTestFactory.assertResponseField(response, 'status', 'Committed', 'isCommit=true is Committed.');
        RLM_TaxTestFactory.assertResponseField(response, 'taxTransactionType', 'Credit', 'The transaction type is echoed.');
        // A 2001 date can only come from the request (the default is now).
        RLM_TaxTestFactory.assertResponseFieldMatches(response, 'transactionDate', RLM_TaxTestFactory.YEAR_2001,
            'The request transaction date is echoed.');
        RLM_TaxTestFactory.assertResponseField(response, 'currencyIsoCode', 'EUR', 'An explicit currency is echoed.');
        RLM_TaxTestFactory.assertResponseField(response, 'description', 'SellerCode fetched from TaxEngine entity',
            'The testSellerCode seller gets its own description.');
    }

    @IsTest
    static void processRequest_emptyDocumentCodeAndBlankCurrency_returnsCalculateTaxResponse() {
        commercetax.CalculateTaxRequest request = requestFor('simulateEmptyDocumentCode');
        request.currencyIsoCode = '';

        Test.startTest();
        commercetax.TaxEngineResponse response = process(request);
        Test.stopTest();

        Assert.isInstanceOfType(response, commercetax.CalculateTaxResponse.class,
            'The empty-document-code scenario still returns a calculated response.');
        RLM_TaxTestFactory.assertResponseField(response, 'documentCode', '', 'The document code is set to empty.');
        RLM_TaxTestFactory.assertResponseField(response, 'currencyIsoCode', 'USD', 'A blank currency defaults to USD.');
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
            new RLM_MockTaxAdapter().processRequest(RLM_TaxTestFactory.contextWithoutRequestType(requestFor('DOC-MOCK-3')));
        Test.stopTest();

        Assert.isNull(response, 'Only CalculateTax requests are answered.');
    }

    @IsTest
    static void getRandomInteger_alwaysReturnsMin() {
        Test.startTest();
        Integer fromFive = RLM_MockTaxAdapter.getRandomInteger(5, 10);
        Integer fromZero = RLM_MockTaxAdapter.getRandomInteger(0, 2147483647);
        Test.stopTest();

        // Integer.valueOf(Math.random()) truncates a value in [0, 1) to 0 (anonymous Apex:
        // Integer.valueOf(0.9d) and Integer.valueOf(0.999999d) both return 0), so the result is always min.
        Assert.areEqual(5, fromFive, 'getRandomInteger returns min.');
        Assert.areEqual(0, fromZero, 'getRandomInteger returns min.');
    }
}
