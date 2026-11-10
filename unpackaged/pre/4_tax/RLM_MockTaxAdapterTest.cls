/**
 * Asserts which response each documentCode scenario produces (ErrorResponse vs
 * CalculateTaxResponse, null, or an exception) and, through the response's String form,
 * the codes and values the adapter set on it.
 */
@IsTest
private class RLM_MockTaxAdapterTest {

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
        RLM_TaxTestFactory.assertResponseHas(response, 'errorCode=404', 'A missing document code is a 404.');
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
        RLM_TaxTestFactory.assertResponseHas(responses.get('TaxEngineError'), 'errorCode=504', 'TaxEngineError');
        RLM_TaxTestFactory.assertResponseHas(responses.get('simulateValidationFailureInAdapter'), 'errorCode=400', 'Validation failure');
        RLM_TaxTestFactory.assertResponseHas(responses.get('simulateMalformedErrorInAdapter'),
            'errorMessage=malformed adapter error response', 'Malformed error keeps its message');
        RLM_TaxTestFactory.assertResponseHas(responses.get('simulateTaxEngineProcessFailure'), 'errorCode=500', 'Process failure');
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
        RLM_TaxTestFactory.assertResponseHas(response, 'documentCode=DOC-MOCK-1', 'The document code is echoed.');
        RLM_TaxTestFactory.assertResponseHas(response, 'currencyIsoCode=USD', 'A null currency defaults to USD.');
        RLM_TaxTestFactory.assertResponseHas(response, 'description=description,', 'A non-test seller gets the default description.');
    }

    @IsTest
    static void processRequest_committedWithExplicitValues_returnsCalculateTaxResponse() {
        commercetax.CalculateTaxRequest request = requestFor('DOC-MOCK-2');
        request.isCommit = true;
        request.sellerDetails = new commercetax.TaxSellerDetailsRequest('testSellerCode');
        request.transactionDate = Datetime.newInstanceGmt(2026, 3, 1, 0, 0, 0);
        request.taxTransactionType = commercetax.TaxTransactionType.Credit;
        request.currencyIsoCode = 'EUR';

        Test.startTest();
        commercetax.TaxEngineResponse response = process(request);
        Test.stopTest();

        Assert.isInstanceOfType(response, commercetax.CalculateTaxResponse.class,
            'Explicit commit, seller, date, type and currency values are echoed into a calculated response.');
        RLM_TaxTestFactory.assertResponseHas(response, 'currencyIsoCode=EUR', 'An explicit currency is echoed.');
        RLM_TaxTestFactory.assertResponseHas(response, 'description=SellerCode fetched from TaxEngine entity',
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
        RLM_TaxTestFactory.assertResponseHas(response, 'currencyIsoCode=USD', 'A blank currency defaults to USD.');
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
        // commercetax.TaxApiException is not a visible type in Apex, so match its name.
        Assert.areEqual('commercetax.TaxApiException', caught.getTypeName(), 'The platform setter throws: ' + caught);
        Assert.isTrue(caught.getMessage().contains('Amount details cannot be null'), caught.getMessage());
    }

    @IsTest
    static void processRequest_nullResponseScenarios_returnCalculateTaxResponses() {
        List<String> scenarios = new List<String>{
            'SetsNullForResponseWithoutException',
            'nolines'
        };
        Map<String, commercetax.TaxEngineResponse> responses = new Map<String, commercetax.TaxEngineResponse>();

        Test.startTest();
        for (String scenario : scenarios) {
            responses.put(scenario, process(requestFor(scenario)));
        }
        Test.stopTest();

        for (String scenario : scenarios) {
            Assert.isInstanceOfType(responses.get(scenario), commercetax.CalculateTaxResponse.class,
                scenario + ' builds its (partially null) response inside the adapter without throwing.');
        }
    }

    @IsTest
    static void processRequest_otherRequestType_returnsNull() {
        Test.startTest();
        commercetax.TaxEngineResponse response =
            new RLM_MockTaxAdapter().processRequest(RLM_TaxTestFactory.contextWithoutRequestType(requestFor('DOC-MOCK-3')));
        Test.stopTest();

        Assert.isNull(response, 'Only CalculateTax requests are answered.');
    }

    @IsTest
    static void getRandomInteger_staysWithinBounds() {
        Test.startTest();
        Integer value = RLM_MockTaxAdapter.getRandomInteger(5, 10);
        Test.stopTest();

        Assert.isTrue(value >= 5 && value <= 10, 'getRandomInteger should stay within [min, max]: ' + value);
    }
}
