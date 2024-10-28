public with sharing class ChapiClient implements IChapiClient {

    public Map<String, Object> callCountryRESTService(String countryIsoCode) {
        System.debug('Calling CHAPI For: ' + countryIsoCode);
        return this.invokeApi(String.format('callout:CHAPICallout/countries/{0}', new List<String> { countryIsoCode }));
    }

    public Map<String, Object> callCountryRESTService(String countryIsoCode, String currencyCode) {
        System.debug('Calling CHAPI For: ' + countryIsoCode + ' & ' + currencyCode);
        return this.invokeApi(String.format('callout:CHAPICallout/countries/{0}?currencyISOCode={1}', new List<String> { countryIsoCode, currencyCode }));
    }

    public Map<String, Object> invokeApi(String url) {
        HttpRequest req = new HttpRequest();
        req.setEndpoint(url);
        req.setMethod('GET');
        Http http = new Http();
        HTTPResponse res = http.send(req);
        return RevenueOwnerServiceHelper.parseResponse(res.getBody());
    }
    
    public Map<String, Object> callValidateTaxId(TaxValidationReqItem requestItem) {
        HttpRequest req = new HttpRequest();
        req.setEndpoint('callout:CHAPICallout/validate');
        req.setMethod('PATCH');
        req.setBody(JSON.serialize(requestItem));
        req.setHeader('Content-Type', 'application/json');
        Http http = new Http();
        HTTPResponse res = http.send(req);
        return RevenueOwnerServiceHelper.parseTaxValidationResponse(res.getBody());
    }

}