public with sharing class PlaceQuoteService extends AbstractPlaceQuoteService {

    private static final String PLACE_QUOTE_ENDPOINT = '/services/data/v61.0/commerce/quotes/actions/place';
    private PlaceQuote.PlaceQuoteResponse mockPlaceQuoteRLMApexProcessorResponse;

    private static final Integer HTTP_REQUEST_MAX_TIMEOUT = 120000;

    private String getPlaceQuoteEndpoint() {
        return Url.getOrgDomainUrl().toExternalForm() + PLACE_QUOTE_ENDPOINT;
    }

    private class PlaceQuoteConfigurationOptions {
        public Boolean validateProductCatalog;
        public Boolean validateAmendRenewCancel;
        public Boolean executeConfigurationRules;
        public Boolean addDefaultConfiguration;

        public PlaceQuoteConfigurationOptions(PlaceQuoteServiceRequest request)  {
            this.validateProductCatalog = request.config?.validateProductCatalog ?? true;
            this.validateAmendRenewCancel = request.config?.validateAmendRenewCancel ?? true;
            this.executeConfigurationRules = request.config?.executeConfigurationRules ?? true;
            this.addDefaultConfiguration = request.config?.addDefaultConfiguration ?? true;
        }
    }

    public override PlaceQuoteServiceResponse placeQuote(PlaceQuoteServiceRequest request) {
        Http h = new Http();
        HttpRequest req = new HttpRequest();
        req.setTimeout(HTTP_REQUEST_MAX_TIMEOUT);
        req.setMethod(request.method);
        req.setHeader('Content-Type', 'application/json; charset=UTF-8');
        req.setHeader('Accept', 'application/json');
        String sessionId = 'Bearer ' + LEXApiSessionIdGenerator.generateSessionId();
        req.setHeader('Authorization', sessionId);
        req.setEndpoint(getPlaceQuoteEndpoint());
        req.setBody(buildRequestBody(request));

        HttpResponse res = h.send(req);

        Map<String, Object> placeQuoteApiResponse = (Map<String, Object>) JSON.deserializeUntyped(res.getBody());
        // Purposefully logging the response in case of errors, more to do here
        PlaceQuoteServiceResponse resp = new PlaceQuoteServiceResponse();
        if(placeQuoteApiResponse.containsKey('responseError') && placeQuoteApiResponse.get('responseError') != null) {
            resp.responseError = (List<PlaceQuoteServiceResponse.ResponseError>)JSON.deserialize(JSON.serialize(placeQuoteApiResponse.get('responseError')),List<PlaceQuoteServiceResponse.ResponseError>.class);
        }
        if(placeQuoteApiResponse.containsKey('success') && placeQuoteApiResponse.get('success') != null) {
            resp.success = Boolean.valueOf(placeQuoteApiResponse.get('success'));
        }
        resp.quoteId = String.valueOf(placeQuoteApiResponse.get('quoteId'));
        return resp;
    }

    public override void refreshPrices(List<Id> quoteIds) {
        PlaceQuote.PricingPreferenceEnum pricingPreference = PlaceQuote.PricingPreferenceEnum.FORCE;
        PlaceQuote.ConfigurationInputEnum configEnum = PlaceQuote.ConfigurationInputEnum.RunAndAllowErrors;
        PlaceQuote.ConfigurationOptionsInput config = new PlaceQuote.ConfigurationOptionsInput();
        config.addDefaultConfiguration = true;
        config.executeConfigurationRules = true;
        config.validateAmendRenewCancel = true;
        config.validateProductCatalog = true;

       
        List<PlaceQuote.RecordWithReferenceRequest> records = new List<PlaceQuote.RecordWithReferenceRequest>();

        for (Id quoteId : quoteIds) {
             // create the empty object graph w/only a reference to the quote
            PlaceQuote.RecordResource quoteRecord = new PlaceQuote.RecordResource(Quote.getSobjectType(), 'PATCH', quoteId);
            PlaceQuote.RecordWithReferenceRequest quoteObject = new PlaceQuote.RecordWithReferenceRequest('refQuote', quoteRecord);
            records.add(quoteObject);
        }
        
        // Invoke the Place Quote API
        PlaceQuote.GraphRequest graph = new PlaceQuote.GraphRequest('refreshPrices', records);
        PlaceQuote.PlaceQuoteResponse resp = Test.isRunningTest() ? mockPlaceQuoteRLMApexProcessorResponse : PlaceQuote.PlaceQuoteRLMApexProcessor.execute(pricingPreference, graph, configEnum, config);

        System.debug('Refresh Prices Response: ' + resp);
    }

    private String buildRequestBody(PlaceQuoteServiceRequest request) {
        Map<String, Object> bodyParameters = new Map<String, Object>();
        bodyParameters.put('pricingPref', request.pricingPreference);
        bodyParameters.put('configurationInput', request.configEnum);
        bodyParameters.put('configurationOptions', new PlaceQuoteConfigurationOptions(request));
        bodyParameters.put('graph', buildGraphNode(request));

        return JSON.serialize(bodyParameters);
    }

    private Map<String, Object> buildGraphNode(PlaceQuoteServiceRequest request) {
        Map<String, Object> graphRequest = new Map<String, Object>();
        graphRequest.put('graphId', request.graphId);
        List<Map<String, Object>> records = new List<Map<String, Object>>();
        for (PlaceQuote.RecordWithReferenceRequest recRef : request.records) {
            Map<String, Object> recordWithRef = new Map<String, Object>();
            recordWithRef.put('referenceId', recRef.referenceId);
            Map<String, Object> record = new Map<String, Object>();
            Map<String, Object> attributes = new Map<String, Object>();
            attributes.put('type', recRef.record.type.getDescribe().getName());
            attributes.put('method', recRef.record.method);
            record.put('attributes', attributes);
            record.putAll(recRef.record.fieldValues);
            recordWithRef.put('record', record);
            records.add(recordWithRef);
        }
        graphRequest.put('records', records);
        return graphRequest;
    }

    @TestVisible
    private void setMockPlaceQuoteRLMApexProcessorResponse(PlaceQuote.PlaceQuoteResponse mockPlaceQuoteRLMApexProcessorResponse) {
        this.mockPlaceQuoteRLMApexProcessorResponse = mockPlaceQuoteRLMApexProcessorResponse;
    }
}
