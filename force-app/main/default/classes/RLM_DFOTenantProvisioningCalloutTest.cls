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

        Assert.isTrue(result.isSuccess(), 'A successful callout reports success');
        Assert.areEqual(1, mock.callCount, 'Exactly one tenant callout is made');
        Assert.areEqual('POST', mock.lastRequest.getMethod(), 'Tenant creation is a POST');
        Assert.areEqual(ENDPOINT, mock.lastRequest.getEndpoint(), 'The RLM named credential endpoint is used');
        Assert.areEqual('application/json', mock.lastRequest.getHeader('Content-Type'), 'JSON body');
        Assert.areEqual('application/json', mock.lastRequest.getHeader('Accept'), 'JSON response expected');
        Map<String, Object> body = (Map<String, Object>) JSON.deserializeUntyped(mock.lastRequest.getBody());
        Assert.areEqual(String.valueOf(oi.OrderId), body.get('orderId'), 'The order item\'s parent order id is sent');
    }

    @IsTest
    static void nonJsonErrorBodyDoesNotThrow() {
        OrderItem oi = orderItem();
        TenantMock mock = new TenantMock(500, 'Service Unavailable');
        Test.setMock(HttpCalloutMock.class, mock);

        Test.startTest();
        industriesintegrationfwk.IntegrationCalloutResponse result =
            RLM_DFOTenantProvisioningCallout.executeCallout('guid-2', oi.Id, '', new Map<String, Object>());
        Test.stopTest();

        Assert.areEqual(1, mock.callCount, 'The callout was attempted once');
        Assert.isTrue(
            result.isSuccess(),
            'Known gap: success is reported whatever the HTTP status; update this test when it is fixed'
        );
    }

    @IsTest
    static void unsupportedSourceTypeMakesNoCallout() {
        TenantMock mock = new TenantMock(200, '{}');
        Test.setMock(HttpCalloutMock.class, mock);

        Test.startTest();
        industriesintegrationfwk.IntegrationCalloutResponse result =
            RLM_DFOTenantProvisioningCallout.executeCallout(
                'guid-3', fakeId(Account.SObjectType), '', new Map<String, Object>()
            );
        Test.stopTest();

        Assert.isTrue(
            result.isSuccess(),
            'Known gap: an unsupported source type reports success without calling out; '
                + 'update this test when it is fixed'
        );
        Assert.areEqual(0, mock.callCount, 'Only order items and fulfillment lines trigger a callout');
    }

    @IsTest
    static void fulfillmentLineWithoutOrderItemSourceFails() {
        TenantMock mock = new TenantMock(200, '{}');
        Test.setMock(HttpCalloutMock.class, mock);

        Test.startTest();
        try {
            RLM_DFOTenantProvisioningCallout.executeCallout(
                'guid-4', fakeId(FulfillmentOrderLineItem.SObjectType), '', new Map<String, Object>()
            );
            Assert.fail('A fulfillment line with no order item source relation must fail');
        } catch (QueryException e) {
            Assert.isTrue(
                e.getMessage().contains('no rows'),
                'Known gap: a fulfillment line without an order item source throws a raw QueryException; '
                    + 'update this test when it is fixed. ' + e.getMessage()
            );
        }
        Test.stopTest();

        Assert.areEqual(0, mock.callCount, 'No callout is made without a resolvable order');
    }

    @IsTest
    static void providerDeclaresNoAttributes() {
        List<industriesintegrationfwk.ApexProviderAttr> attrs =
            new RLM_DFOTenantProvisioningCallout().getProviderAttributes();

        Assert.areEqual(0, attrs.size(), 'The tenant provider has no configurable attributes');
    }
}
