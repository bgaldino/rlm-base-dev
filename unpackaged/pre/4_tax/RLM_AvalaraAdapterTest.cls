@IsTest
private with sharing class RLM_AvalaraAdapterTest {

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
        // The document code comes from the service's parsed engine payload, not from the request.
        RLM_TaxTestFactory.assertResponseField(response, 'documentCode', 'testDocCode1231245984',
            'The response is the one RLM_CalculateTaxService builds.');
        RLM_TaxTestFactory.assertResponseField(response, 'taxTransactionType', 'Debit',
            'The service echoes the request transaction type.');
        Assert.areEqual(1, mock.requests.size(), 'The service sends one Avalara callout.');
    }

    @IsTest
    static void processRequest_nullRequestType_returnsNullWithoutCallout() {
        RLM_TaxTestFactory.RecordingHttpMock mock = new RLM_TaxTestFactory.RecordingHttpMock(200, '{}');
        Test.setMock(HttpCalloutMock.class, mock);
        commercetax.CalculateTaxRequest request = RLM_TaxTestFactory.request(
            commercetax.CalculateTaxType.Estimated, 'DOC-AVA-2', RLM_TaxTestFactory.lines(232));

        Test.startTest();
        commercetax.TaxEngineResponse response =
            new RLM_AvalaraAdapter().processRequest(RLM_TaxTestFactory.contextWithoutRequestType(request));
        Test.stopTest();

        Assert.isNull(response, 'Only CalculateTax requests are handled.');
        Assert.areEqual(0, mock.requests.size(), 'No callout is made for a request that is not CalculateTax.');
    }
}
