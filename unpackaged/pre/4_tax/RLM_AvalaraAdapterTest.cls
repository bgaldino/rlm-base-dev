@IsTest
private class RLM_AvalaraAdapterTest {

    @IsTest
    static void processRequest_calculateTax_delegatesToCalculateTaxService() {
        RLM_TaxTestFactory.RecordingHttpMock mock = new RLM_TaxTestFactory.RecordingHttpMock(200, '{}');
        Test.setMock(HttpCalloutMock.class, mock);
        commercetax.CalculateTaxRequest request = RLM_TaxTestFactory.request(
            commercetax.CalculateTaxType.Estimated, 'DOC-AVA-1', RLM_TaxTestFactory.lines(232));
        request.taxTransactionType = commercetax.TaxTransactionType.Debit;

        Test.startTest();
        commercetax.TaxEngineResponse response = new RLM_AvalaraAdapter().processRequest(RLM_TaxTestFactory.context(request));
        Test.stopTest();

        Assert.isInstanceOfType(response, commercetax.CalculateTaxResponse.class,
            'A CalculateTax request is answered by RLM_CalculateTaxService.');
        Assert.areEqual(1, mock.requests.size(), 'The service sends one Avalara callout.');
    }

    @IsTest
    static void processRequest_otherRequestType_returnsNullWithoutCallout() {
        RLM_TaxTestFactory.RecordingHttpMock mock = new RLM_TaxTestFactory.RecordingHttpMock(200, '{}');
        Test.setMock(HttpCalloutMock.class, mock);
        commercetax.CalculateTaxRequest request = RLM_TaxTestFactory.request(
            commercetax.CalculateTaxType.Estimated, 'DOC-AVA-2', RLM_TaxTestFactory.lines(232));

        Test.startTest();
        commercetax.TaxEngineResponse response =
            new RLM_AvalaraAdapter().processRequest(RLM_TaxTestFactory.contextWithoutRequestType(request));
        Test.stopTest();

        Assert.isNull(response, 'Only CalculateTax requests are handled.');
        Assert.areEqual(0, mock.requests.size(), 'No callout is made for an unhandled request type.');
    }
}
