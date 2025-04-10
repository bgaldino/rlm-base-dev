public with sharing class RLM_PatchQuoteTenantUtility {
    @InvocableMethod(label = 'Set Quote Line Tenant Info' description='Set Tenant Environment Lookup on Quote Line through Place Quote API' category='RLM SE TAT')
    public static void callQuotePatchTenantInfo(List<QuoteRecordInput> inputs){
        Http http = new Http();
        HttpRequest httpRequest = new HttpRequest();
        httpRequest.setMethod('POST');
//        httpRequest.setHeader('Authorization', 'OAuth ' + UserInfo.getSessionId());
//        httpRequest.setHeader('Authorization', 'Bearer ' + UserInfo.getSessionId());
        httpRequest.setHeader('Content-Type', 'application/json');

        system.debug('OAuth + Bearer Token is ' + UserInfo.getSessionId());

        RLM_PlaceQuoteModel requestBody = buildRequestBodyObject(inputs.get(0).inputQuote, inputs.get(0).inputQuoteLineItems, inputs.get(0).tenantEnvironmentId);

        httpRequest.setBody(JSON.serialize(requestBody));

        System.debug(JSON.serializePretty(requestBody));

        httpRequest.setEndpoint('callout:RLM/services/data/v64.0/commerce/quotes/actions/place');

        HttpResponse response = http.send(httpRequest);

        system.debug('API response is: ' + response.getStatusCode());

    }

    public static RLM_PlaceQuoteModel buildRequestBodyObject(Quote inputQuote, List<QuoteLineItem> inputQuoteLineItems, String tenantEnvironmentId){
        RLM_PlaceQuoteModel requestBody = new RLM_PlaceQuoteModel();

        requestBody.pricingPref = 'System';
        requestBody.configurationInput = 'RunAndAllowErrors';

        Map<String, Boolean> optionConfigs = new Map<String, Boolean>();

        optionConfigs.put('validateProductCatalog', true);
        optionConfigs.put('validateAmendRenewCancel', true);
        optionConfigs.put('executeConfigurationRules', true);
        optionConfigs.put('addDefaultConfiguration', true);

        requestBody.configurationOptions = optionConfigs;

        requestBody.graph = new RLM_PlaceQuoteModel.QuoteGraphModel();

        requestBody.graph.graphId = 'updateQuote';

        requestBody.graph.records = new List<RLM_PlaceQuoteModel.ObjectRecordModel>();

        RLM_PlaceQuoteModel.ObjectRecordModel quoteModel = new RLM_PlaceQuoteModel.ObjectRecordModel();

        quoteModel.referenceId = inputQuote.Id;

        Map<String, String> quoteAttrMap = new Map<String, String>();

        quoteAttrMap.put('type', 'Quote');
        quoteAttrMap.put('method', 'PATCH');
        quoteAttrMap.put('id', inputQuote.Id);

        quoteModel.record = new Map<String, Object>();

        quoteModel.record.put('attributes', quoteAttrMap);

        requestBody.graph.records.add(quoteModel);

        if(inputQuoteLineItems.size() > 0){
            for(QuoteLineItem inputQuoteLine: inputQuoteLineItems){
                RLM_PlaceQuoteModel.ObjectRecordModel quoteLineModel = new RLM_PlaceQuoteModel.ObjectRecordModel();
                quoteLineModel.referenceId = inputQuoteLine.Id;
                Map<String, String> qlAttrMap = new Map<String, String>();

                qlAttrMap.put('type', 'QuoteLineItem');
                qlAttrMap.put('method', 'PATCH');
                qlAttrMap.put('id', inputQuoteLine.Id);

                quoteLineModel.record = new Map<String, Object>();

                quoteLineModel.record.put('attributes', qlAttrMap);

                requestBody.graph.records.add(quoteLineModel);
            }
        }

        return requestBody;

    }

    static String buildPlaceQuoteRestAPIURL() {
        String sfdcURL = Url.getOrgDomainUrl().toExternalForm();
        String restAPIURL = sfdcURL + '/services/data/v64.0/commerce/quotes/actions/place';
        system.debug(restAPIURL);
        return restAPIURL;
    }

    public class QuoteRecordInput{
        @InvocableVariable
        public Quote inputQuote;

        @InvocableVariable
        public List<QuoteLineItem> inputQuoteLineItems;

        @InvocableVariable
        public String tenantEnvironmentId;
    }
}