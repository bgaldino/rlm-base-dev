/**
 * Not covered: the fulfillment-line success path (FulfillmentLineSourceRel to its order item, then
 * the tenant callout). It needs a fulfillment order, its lines and their source relations, which is
 * too heavy a fixture for a unit test; only the missing-relation failure is tested here.
 */
@IsTest
private class RLM_DFOTenantProvisioningCalloutTest {

    private static final String ENDPOINT =
        'callout:RLM/services/apexrest/QuantumBitTenantEnvironment/createNewTenant';

    private class TenantMock implements HttpCalloutMock {
        public Integer statusCode;
        public String body;
        public Integer callCount = 0;
        public HttpRequest lastRequest;

        public TenantMock(Integer statusCode, String body) {
            this.statusCode = statusCode;
            this.body = body;
        }

        public HttpResponse respond(HttpRequest request) {
            callCount++;
            lastRequest = request;
            HttpResponse response = new HttpResponse();
            response.setStatusCode(statusCode);
            response.setBody(body);
            return response;
        }
    }

    @TestSetup
    static void setup() {
        Account acct = new Account(Name = 'RLM DFO Tenant Account');
        insert acct;
        Product2 product = new Product2(Name = 'RLM DFO Tenant Product', IsActive = true);
        insert product;
        Id pbId = Test.getStandardPricebookId();
        PricebookEntry pbe = new PricebookEntry(
            Pricebook2Id = pbId, Product2Id = product.Id, UnitPrice = 10, IsActive = true
        );
        insert pbe;
        Order o = new Order(
            AccountId = acct.Id, Status = 'Draft', EffectiveDate = Date.today(), Pricebook2Id = pbId
        );
        insert o;
        insert new OrderItem(
            OrderId = o.Id, PricebookEntryId = pbe.Id, Product2Id = product.Id, Quantity = 1, UnitPrice = 10
        );
    }

    private class ThrowingMock implements HttpCalloutMock {
        public HttpResponse respond(HttpRequest request) {
            throw new CalloutException('Unable to tunnel through proxy');
        }
    }

    private static void assertFailure(industriesintegrationfwk.IntegrationCalloutResponse result, Integer code, String why) {
        Assert.isFalse(result.isSuccess(), why);
        Assert.areEqual(code, result.getResponseCode(), 'The failure carries its response code: ' + why);
        Assert.isFalse(String.isBlank(result.getErrorMessage()), 'The failure carries a message: ' + why);
    }

    private static OrderItem orderItem() {
        return [SELECT Id, OrderId FROM OrderItem LIMIT 1];
    }

    private static String fakeId(Schema.SObjectType objectType) {
        return objectType.getDescribe().getKeyPrefix() + '000000000001';
    }

    @IsTest
    static void orderItemSourcePostsItsOrderIdToTenantEndpoint() {
        OrderItem oi = orderItem();
        TenantMock mock = new TenantMock(200, '{"tenantId":"T-1"}');
        Test.setMock(HttpCalloutMock.class, mock);

        Test.startTest();
        industriesintegrationfwk.IntegrationCalloutResponse result =
            RLM_DFOTenantProvisioningCallout.executeCallout('guid-1', oi.Id, '', new Map<String, Object>());
        Test.stopTest();

        Assert.isTrue(result.isSuccess(), 'A 200 answer is a success');
        Assert.areEqual(200, result.getResponseCode(), 'The success carries the HTTP status');

        Assert.areEqual(1, mock.callCount, 'Exactly one tenant callout is made');
        Assert.areEqual('POST', mock.lastRequest.getMethod(), 'Tenant creation is a POST');
        Assert.areEqual(ENDPOINT, mock.lastRequest.getEndpoint(), 'The RLM named credential endpoint is used');
        Assert.areEqual('application/json', mock.lastRequest.getHeader('Content-Type'), 'JSON body');
        Assert.areEqual('application/json', mock.lastRequest.getHeader('Accept'), 'JSON response expected');
        Map<String, Object> body = (Map<String, Object>) JSON.deserializeUntyped(mock.lastRequest.getBody());
        Assert.areEqual(String.valueOf(oi.OrderId), body.get('orderId'), 'The order item\'s parent order id is sent');
    }

    @IsTest
    static void httpErrorReportsFailure() {
        OrderItem oi = orderItem();
        TenantMock mock = new TenantMock(500, 'Service Unavailable');
        Test.setMock(HttpCalloutMock.class, mock);

        Test.startTest();
        industriesintegrationfwk.IntegrationCalloutResponse result =
            RLM_DFOTenantProvisioningCallout.executeCallout('guid-2', oi.Id, '', new Map<String, Object>());
        Test.stopTest();

        Assert.areEqual(1, mock.callCount, 'The callout was attempted once');
        assertFailure(result, 500, 'A non-2xx answer from the tenant service is a failure');
        Assert.isTrue(result.getErrorMessage().contains('Service Unavailable'), 'The message carries the start of the response body');
    }

    @IsTest
    static void anyTwoHundredSeriesStatusIsSuccess() {
        OrderItem oi = orderItem();
        TenantMock mock = new TenantMock(201, '{"tenantId":"T-2"}');
        Test.setMock(HttpCalloutMock.class, mock);

        Test.startTest();
        industriesintegrationfwk.IntegrationCalloutResponse result =
            RLM_DFOTenantProvisioningCallout.executeCallout('guid-2b', oi.Id, '', new Map<String, Object>());
        Test.stopTest();

        Assert.isTrue(result.isSuccess(), 'A 2xx answer is a success');
        Assert.areEqual(201, result.getResponseCode(), 'The success carries the HTTP status');
    }

    @IsTest
    static void unsupportedSourceTypeReportsFailureWithoutCallout() {
        TenantMock mock = new TenantMock(200, '{}');
        Test.setMock(HttpCalloutMock.class, mock);

        Test.startTest();
        industriesintegrationfwk.IntegrationCalloutResponse result =
            RLM_DFOTenantProvisioningCallout.executeCallout(
                'guid-3', fakeId(Account.SObjectType), '', new Map<String, Object>()
            );
        Test.stopTest();

        assertFailure(result, 400, 'An unsupported source type is a failure, not a silent success');
        Assert.areEqual(0, mock.callCount, 'Only order items and fulfillment lines trigger a callout');
    }

    @IsTest
    static void fulfillmentLineWithoutOrderItemSourceReportsFailure() {
        TenantMock mock = new TenantMock(200, '{}');
        Test.setMock(HttpCalloutMock.class, mock);

        Test.startTest();
        industriesintegrationfwk.IntegrationCalloutResponse result =
            RLM_DFOTenantProvisioningCallout.executeCallout(
                'guid-4', fakeId(FulfillmentOrderLineItem.SObjectType), '', new Map<String, Object>()
            );
        Test.stopTest();

        assertFailure(result, 400, 'A fulfillment line without an order item source is a failure');
        Assert.areEqual(0, mock.callCount, 'No callout without an order');
    }

    @IsTest
    static void missingOrMalformedRecordIdReportsFailure() {
        TenantMock mock = new TenantMock(200, '{}');
        Test.setMock(HttpCalloutMock.class, mock);

        Test.startTest();
        industriesintegrationfwk.IntegrationCalloutResponse blank =
            RLM_DFOTenantProvisioningCallout.executeCallout('guid-5', null, '', new Map<String, Object>());
        industriesintegrationfwk.IntegrationCalloutResponse malformed =
            RLM_DFOTenantProvisioningCallout.executeCallout('guid-6', 'not-an-id', '', new Map<String, Object>());
        Test.stopTest();

        assertFailure(blank, 400, 'A missing id is a failure');
        assertFailure(malformed, 400, 'A malformed id is a failure');
        Assert.areEqual(0, mock.callCount, 'No callout without a usable id');
    }

    @IsTest
    static void unknownOrderItemReportsFailure() {
        TenantMock mock = new TenantMock(200, '{}');
        Test.setMock(HttpCalloutMock.class, mock);

        Test.startTest();
        industriesintegrationfwk.IntegrationCalloutResponse result =
            RLM_DFOTenantProvisioningCallout.executeCallout(
                'guid-7', fakeId(OrderItem.SObjectType), '', new Map<String, Object>()
            );
        Test.stopTest();

        assertFailure(result, 400, 'An order item that does not exist is a failure');
        Assert.areEqual(0, mock.callCount, 'No callout without an order');
    }

    @IsTest
    static void calloutExceptionReportsFailure() {
        OrderItem oi = orderItem();
        Test.setMock(HttpCalloutMock.class, new ThrowingMock());

        Test.startTest();
        industriesintegrationfwk.IntegrationCalloutResponse result =
            RLM_DFOTenantProvisioningCallout.executeCallout('guid-8', oi.Id, '', new Map<String, Object>());
        Test.stopTest();

        assertFailure(result, 503, 'A callout that cannot be made is a failure, not an exception');
    }

    @IsTest
    static void providerDeclaresNoAttributes() {
        List<industriesintegrationfwk.ApexProviderAttr> attrs =
            new RLM_DFOTenantProvisioningCallout().getProviderAttributes();

        Assert.areEqual(0, attrs.size(), 'The tenant provider has no configurable attributes');
    }
}
