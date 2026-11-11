@IsTest
private with sharing class RLM_InvalidAdapterTest {

    @IsTest
    static void processRequest_calculateTaxRequest_returnsNull() {
        commercetax.CalculateTaxRequest request = RLM_TaxTestFactory.request(
            commercetax.CalculateTaxType.Estimated, 'DOC-INVALID', RLM_TaxTestFactory.lines(100));

        Test.startTest();
        commercetax.TaxEngineResponse response = new RLM_InvalidAdapter().processRequest(RLM_TaxTestFactory.context(request));
        Test.stopTest();

        Assert.isNull(response, 'The invalid adapter does not answer even a valid CalculateTax request.');
    }
}
