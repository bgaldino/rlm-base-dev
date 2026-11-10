/**
 * Asserts which response each scenario produces (ErrorResponse vs CalculateTaxResponse,
 * null, or an exception) and, through the response's String form, the codes and values
 * the adapter set on it.
 */
@IsTest
private class RLM_MockAppAdapterTest {

    private static commercetax.TaxEngineResponse process(commercetax.CalculateTaxRequest request) {
        return new RLM_MockAppAdapter().processRequest(RLM_TaxTestFactory.context(request));
    }

    private static commercetax.CalculateTaxRequest requestFor(String documentCode) {
        return RLM_TaxTestFactory.request(
            commercetax.CalculateTaxType.Estimated,
            documentCode,
            new List<commercetax.TaxLineItemRequest>{
                RLM_TaxTestFactory.line(100, '1', Datetime.newInstanceGmt(2026, 2, 1, 0, 0, 0)),
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
        RLM_TaxTestFactory.assertResponseHas(responses.get('TaxEngineError'), 'errorCode=504', 'TaxEngineError');
        RLM_TaxTestFactory.assertResponseHas(responses.get('TaxEngineErrorWithSuffix'), 'errorCode=504',
            'Any document code starting with TaxEngineError');
        RLM_TaxTestFactory.assertResponseHas(responses.get('simulateValidationFailureInAdapter'), 'errorCode=400', 'Validation failure');
        RLM_TaxTestFactory.assertResponseHas(responses.get('simulateTaxEngineProcessFailure'), 'errorCode=500', 'Process failure');
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
        RLM_TaxTestFactory.assertResponseHas(response, 'errorCode=504', 'The reference-code error is a 504.');
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
            RLM_TaxTestFactory.assertResponseHas(responses[i], 'errorCode=500', 'Line amount ' + errorAmounts[i]);
        }
    }

    @IsTest
    static void processRequest_documentCodeVariants_returnCalculateTaxResponses() {
        commercetax.CalculateTaxRequest withDocumentCode = requestFor('DOC-APP-1');
        withDocumentCode.isCommit = true;
        withDocumentCode.transactionDate = Datetime.newInstanceGmt(2026, 3, 1, 0, 0, 0);
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

        Assert.areEqual(4, responses.size(), 'Every variant is processed.');
        for (Integer i = 0; i < responses.size(); i++) {
            Assert.isInstanceOfType(responses[i], commercetax.CalculateTaxResponse.class,
                'Variant ' + i + ' (document code, empty code, reference entity, generated code) returns a calculated response.');
        }
        RLM_TaxTestFactory.assertResponseHas(responses[0], 'documentCode=DOC-APP-1', 'An explicit document code is echoed.');
        RLM_TaxTestFactory.assertResponseHas(responses[0], 'currencyIsoCode=EUR', 'An explicit currency is echoed.');
        RLM_TaxTestFactory.assertResponseHas(responses[1], 'currencyIsoCode=USD', 'A blank currency defaults to USD.');
        RLM_TaxTestFactory.assertResponseHas(responses[2], 'documentCode=REF-APP-1',
            'Without a document code the reference entity id becomes the document code.');
        RLM_TaxTestFactory.assertResponseHas(responses[2], 'currencyIsoCode=USD', 'A null currency defaults to USD.');
        Assert.isFalse(String.valueOf(responses[3]).contains('documentCode=<null>'),
            'With no codes at all a document code is generated: ' + responses[3]);
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
            new RLM_MockAppAdapter().processRequest(RLM_TaxTestFactory.contextWithoutRequestType(requestFor('DOC-APP-2')));
        Test.stopTest();

        Assert.isNull(response, 'Only CalculateTax requests are answered.');
    }

    @IsTest
    static void getRandomInteger_staysWithinBounds() {
        Test.startTest();
        Integer value = RLM_MockAppAdapter.getRandomInteger(0, 10);
        Test.stopTest();

        Assert.isTrue(value >= 0 && value <= 10, 'getRandomInteger should stay within [min, max]: ' + value);
    }
}
