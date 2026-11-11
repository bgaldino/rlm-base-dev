@IsTest
private with sharing class RLM_JsonErrorParserTest {

    @IsTest
    static void parse_avalaraErrorPayload_mapsErrorAndDetails() {
        String payload = '{"error":{"code":"GetTaxError","message":"The tax engine rejected the request",'
            + '"target":"IncorrectData","details":[{"code":"AddressRangeError","message":"Address not found",'
            + '"description":"The address could not be geocoded","faultCode":"Client",'
            + '"helpLink":"https://developer.avalara.com/","severity":"Error"},'
            + '{"code":"SecondError","message":"Second message"}]}}';

        Test.startTest();
        RLM_JsonErrorParser parsed = RLM_JsonErrorParser.parse(payload);
        Test.stopTest();

        Assert.isNotNull(parsed.error, 'The error object should be parsed.');
        Assert.areEqual('GetTaxError', parsed.error.code, 'error.code');
        Assert.areEqual('The tax engine rejected the request', parsed.error.message, 'error.message');
        Assert.areEqual('IncorrectData', parsed.error.target, 'error.target');
        Assert.areEqual(2, parsed.error.details.size(), 'Both detail entries should be parsed.');

        RLM_JsonErrorParser.cls_details first = parsed.error.details[0];
        Assert.areEqual('AddressRangeError', first.code, 'details[0].code');
        Assert.areEqual('Address not found', first.message, 'details[0].message');
        Assert.areEqual('The address could not be geocoded', first.description, 'details[0].description');
        Assert.areEqual('Client', first.faultCode, 'details[0].faultCode');
        Assert.areEqual('https://developer.avalara.com/', first.helpLink, 'details[0].helpLink');
        Assert.areEqual('Error', first.severity, 'details[0].severity');

        RLM_JsonErrorParser.cls_details second = parsed.error.details[1];
        Assert.areEqual('SecondError', second.code, 'details[1].code');
        Assert.areEqual('Second message', second.message, 'details[1].message');
        Assert.isNull(second.severity, 'Absent fields stay null.');
    }

    @IsTest
    static void parse_payloadWithoutError_leavesErrorNull() {
        Test.startTest();
        RLM_JsonErrorParser parsed = RLM_JsonErrorParser.parse('{"unrelated":"value"}');
        Test.stopTest();

        Assert.isNull(parsed.error, 'No error key means no error object.');
    }
}
