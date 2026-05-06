public with sharing class RLM_RevenueCloudService {

    private static final String API_BASE = '/services/data/v66.0';

    // POST /connect/cpq/products/search
    public static Map<String, Object> searchProducts(String keyword) {
        String endpoint = API_BASE + '/connect/cpq/products/search';
        Map<String, Object> body = new Map<String, Object>();
        if (String.isNotBlank(keyword)) {
            body.put('searchTerm', keyword);
        }
        return makePostRequest(endpoint, JSON.serialize(body));
    }

    // GET /connect/cpq/products/{productId}
    public static Map<String, Object> getProduct(String productId) {
        return makeGetRequest(API_BASE + '/connect/cpq/products/' + productId);
    }

    // POST /connect/core-pricing/pricing
    public static Map<String, Object> calculatePricing(Map<String, Object> pricingRequest) {
        return makePostRequest(API_BASE + '/connect/core-pricing/pricing', JSON.serialize(pricingRequest));
    }

    // POST /connect/rev/sales-transaction/actions/place
    public static Map<String, Object> placeSalesTransaction(Map<String, Object> txnRequest) {
        return makePostRequest(API_BASE + '/connect/rev/sales-transaction/actions/place', JSON.serialize(txnRequest));
    }

    // POST /commerce/payments/payment-methods
    public static Map<String, Object> createPaymentMethod(Map<String, Object> paymentRequest) {
        return makePostRequest(API_BASE + '/commerce/payments/payment-methods', JSON.serialize(paymentRequest));
    }

    // POST /commerce/payments/sales
    public static Map<String, Object> processPaymentSale(Map<String, Object> saleRequest) {
        return makePostRequest(API_BASE + '/commerce/payments/sales', JSON.serialize(saleRequest));
    }

    // POST /commerce/billing/payments/{id}/actions/apply
    public static Map<String, Object> applyPayment(String paymentId, Map<String, Object> applyRequest) {
        String endpoint = API_BASE + '/commerce/billing/payments/' + paymentId + '/actions/apply';
        return makePostRequest(endpoint, JSON.serialize(applyRequest));
    }

    // POST /commerce/invoicing/invoices/collection/actions/generate
    public static Map<String, Object> generateInvoice(Map<String, Object> invoiceRequest) {
        return makePostRequest(
            API_BASE + '/commerce/invoicing/invoices/collection/actions/generate',
            JSON.serialize(invoiceRequest)
        );
    }

    // POST /revenue/billing/document/actions/generate
    public static Map<String, Object> generateBillingDocument(Map<String, Object> docRequest) {
        return makePostRequest(
            API_BASE + '/revenue/billing/document/actions/generate',
            JSON.serialize(docRequest)
        );
    }

    private static Map<String, Object> makeGetRequest(String endpoint) {
        HttpRequest req = buildRequest(endpoint, 'GET');
        return executeRequest(req);
    }

    private static Map<String, Object> makePostRequest(String endpoint, String body) {
        HttpRequest req = buildRequest(endpoint, 'POST');
        req.setBody(body);
        return executeRequest(req);
    }

    private static HttpRequest buildRequest(String endpoint, String method) {
        String sessionId = UserInfo.getSessionId();
        if (String.isBlank(sessionId)) {
            throw new RevenueCloudException(
                'No valid session for RLM API callout. '
                + 'Revenue Cloud API calls require an authenticated user session.'
            );
        }
        HttpRequest req = new HttpRequest();
        req.setEndpoint(URL.getOrgDomainUrl().toExternalForm() + endpoint);
        req.setMethod(method);
        req.setHeader('Authorization', 'Bearer ' + sessionId);
        req.setHeader('Content-Type', 'application/json');
        req.setTimeout(120000);
        return req;
    }

    private static Map<String, Object> executeRequest(HttpRequest req) {
        HttpResponse res = new Http().send(req);
        if (res.getStatusCode() >= 200 && res.getStatusCode() < 300) {
            return (Map<String, Object>) JSON.deserializeUntyped(res.getBody());
        }
        throw new RevenueCloudException(
            'RLM API error (' + res.getStatusCode() + '): ' + res.getBody()
        );
    }

    public class RevenueCloudException extends Exception {}
}