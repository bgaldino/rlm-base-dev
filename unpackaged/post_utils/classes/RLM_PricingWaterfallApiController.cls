public with sharing class RLM_PricingWaterfallApiController {

    private static final String WATERFALL_PATH = '/services/data/v67.0/connect/core-pricing/waterfall/';

    @AuraEnabled
    public static Map<String, Object> getWaterfall(String lineItemId, String usageType) {
        if (String.isBlank(lineItemId)) {
            throw new AuraHandledException('lineItemId is required');
        }

        Id recordId = (Id) lineItemId;
        String priceWaterfallIdentifier = queryWaterfallIdentifier(recordId);

        if (String.isBlank(priceWaterfallIdentifier)) {
            throw new AuraHandledException('No PriceWaterfallIdentifier found. Pricing may not have run yet.');
        }

        String[] parts = splitIdentifier(priceWaterfallIdentifier);
        if (parts == null) {
            throw new AuraHandledException('Could not parse PriceWaterfallIdentifier: ' + priceWaterfallIdentifier);
        }

        return callWaterfallApi(parts[0], parts[1], usageType);
    }

    private static Map<String, Object> callWaterfallApi(String lineItemToken, String executionId, String usageType) {
        String path = WATERFALL_PATH
            + EncodingUtil.urlEncode(lineItemToken, 'UTF-8')
            + '/'
            + EncodingUtil.urlEncode(executionId, 'UTF-8');

        if (String.isNotBlank(usageType)) {
            path += '?usageType=' + EncodingUtil.urlEncode(usageType, 'UTF-8');
        }

        HttpRequest req = new HttpRequest();
        req.setEndpoint(URL.getOrgDomainUrl().toExternalForm() + path);
        req.setMethod('GET');
        req.setHeader('Content-Type', 'application/json');
        req.setHeader('Authorization', 'Bearer ' + getApiSessionId());

        HttpResponse res = new Http().send(req);

        if (res.getStatusCode() != 200) {
            throw new AuraHandledException(
                'Waterfall API returned ' + res.getStatusCode() + ': ' + res.getBody()
            );
        }

        Map<String, Object> result = (Map<String, Object>) JSON.deserializeUntyped(res.getBody());
        result.put('_apiPath', path);
        return result;
    }

    private static String queryWaterfallIdentifier(Id recordId) {
        Schema.SObjectType objectType = recordId.getSObjectType();

        if (objectType == QuoteLineItem.SObjectType) {
            QuoteLineItem qli = [
                SELECT PriceWaterfallIdentifier
                FROM QuoteLineItem
                WHERE Id = :recordId
                WITH USER_MODE
                LIMIT 1
            ];
            return qli.PriceWaterfallIdentifier;
        } else if (objectType == OrderItem.SObjectType) {
            OrderItem oi = [
                SELECT PriceWaterfallIdentifier
                FROM OrderItem
                WHERE Id = :recordId
                WITH USER_MODE
                LIMIT 1
            ];
            return oi.PriceWaterfallIdentifier;
        }

        throw new AuraHandledException('Unsupported record type. Expected QuoteLineItem or OrderItem.');
    }

    @TestVisible
    private static String getApiSessionId() {
        if (Test.isRunningTest()) {
            return 'fake-session-id';
        }
        return Page.RLM_SessionId.getContent().toString().trim();
    }

    @TestVisible
    private static String[] splitIdentifier(String identifier) {
        if (String.isBlank(identifier)) return null;
        Integer idx = identifier.indexOf(':');
        if (idx <= 0 || idx + 1 >= identifier.length()) return null;
        return new String[]{ identifier.substring(0, idx), identifier.substring(idx + 1) };
    }
}
