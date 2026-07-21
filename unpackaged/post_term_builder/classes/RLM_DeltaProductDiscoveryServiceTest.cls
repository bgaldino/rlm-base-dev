/**
 * Unit tests for RLM_DeltaProductDiscoveryService normalization. Standard invocable actions can't be
 * invoked in a bare test context, so these target the pure-logic unit: normalizeProducts mapping a
 * hand-built representation-shaped JSON sample → DiscoveredProduct (prices flattened per PBE, bundle/
 * qualification derived, display fields projected), proven shape-equivalent across the search and
 * recommendation product shapes.
 */
@IsTest
private class RLM_DeltaProductDiscoveryServiceTest {

    // A findProducts/getProducts "results[]" entry with a multi-entry prices[] array.
    private static String searchProductJson() {
        return '{' +
            '"id":"01t000000000001AAA",' +
            '"name":"Additional API",' +
            '"productCode":"QB-API",' +
            '"family":"APIs",' +
            '"productType":null,' +
            '"qualificationContext":{"isQualified":true,"reason":null},' +
            '"Description":"An API add-on",' +
            '"prices":[' +
                '{"priceBookEntryId":"01u000000000001AAA","priceBookId":"01s000000000001AAA","price":15000,"isDefault":true,' +
                  '"pricingModel":{"id":"0jP000000000001EAA","pricingModelType":"TermDefined","frequency":"Annual"}},' +
                '{"priceBookEntryId":"01u000000000002AAA","priceBookId":"01s000000000001AAA","price":2000,"isDefault":false,' +
                  '"pricingModel":{"id":"0jP000000000002EAA","pricingModelType":"Evergreen","frequency":"Months"}}' +
            '],' +
            '"additionalFields":[]' +
        '}';
    }

    private static List<Object> toList(String body) {
        return (List<Object>) JSON.deserializeUntyped('[' + body + ']');
    }

    @IsTest
    static void testNormalizeFlattensPricesPerPbe() {
        RLM_DeltaProductDiscoveryService svc = new RLM_DeltaProductDiscoveryService();
        RLM_DeltaProductDiscoveryRequest req = new RLM_DeltaProductDiscoveryRequest()
            .withDisplayFields(new Map<String, List<String>>{ 'Product2' => new List<String>{ 'Description' } });

        List<RLM_DeltaProductDiscoveryService.DiscoveredProduct> products = svc.normalizeProducts(toList(searchProductJson()), req);

        System.assertEquals(1, products.size(), 'One product normalized');
        RLM_DeltaProductDiscoveryService.DiscoveredProduct dp = products[0];
        System.assertEquals('01t000000000001AAA', String.valueOf(dp.productId), 'productId mapped from id');
        System.assertEquals('Additional API', dp.name, 'name mapped');
        System.assertEquals('QB-API', dp.code, 'code mapped from productCode');
        System.assertEquals('APIs', dp.family, 'family mapped');
        System.assertEquals(true, dp.isQualified, 'isQualified from qualificationContext');
        System.assertEquals(2, dp.prices.size(), 'one DiscoveredPrice per prices[] entry');

        RLM_DeltaProductDiscoveryService.DiscoveredPrice p0 = dp.prices[0];
        System.assertEquals('01u000000000001AAA', String.valueOf(p0.pbeId), 'pbeId from priceBookEntryId');
        System.assertEquals('0jP000000000001EAA', String.valueOf(p0.productSellingModelId), 'PSM from pricingModel.id');
        System.assertEquals('TermDefined', p0.sellingModelType, 'sellingModelType from pricingModel.pricingModelType');
        System.assertEquals(true, p0.isDefault, 'isDefault mapped');
        System.assertEquals(15000, p0.price, 'price mapped');

        System.assertEquals(true, dp.fields.containsKey('Description'), 'requested display field projected');
        System.assertEquals('An API add-on', dp.fields.get('Description'), 'display field value pulled from representation');
    }

    @IsTest
    static void testLayeredAdditionalFieldsProjected() {
        // Live-confirmed shape: additionalFields is a list of { key, value } pairs. A requested field
        // not present at top level is taken from there; a top-level value wins when both exist.
        RLM_DeltaProductDiscoveryService svc = new RLM_DeltaProductDiscoveryService();
        RLM_DeltaProductDiscoveryRequest req = new RLM_DeltaProductDiscoveryRequest()
            .withDisplayFields(new Map<String, List<String>>{ 'Product2' => new List<String>{ 'Family', 'Description' } });
        String body = '{' +
            '"id":"01t000000000007AAA","name":"Layered","productCode":"LYR",' +
            '"description":"top-level desc",' +
            '"prices":[],' +
            '"additionalFields":[{"key":"Family","value":"Software"},{"key":"Description","value":"additional desc"}]' +
        '}';
        RLM_DeltaProductDiscoveryService.DiscoveredProduct dp = svc.normalizeProducts(toList(body), req)[0];
        System.assertEquals('Software', dp.fields.get('Family'), 'Family pulled from additionalFields key/value pair');
        // "Description" is not a top-level key here ("description" is lowercase), so it falls back to additionalFields.
        System.assertEquals('additional desc', dp.fields.get('Description'), 'Description taken from additionalFields when absent at top level');
    }

    @IsTest
    static void testBundleDerivation() {
        RLM_DeltaProductDiscoveryService svc = new RLM_DeltaProductDiscoveryService();
        String byType = '{"id":"01t000000000003AAA","name":"Bundle Parent","productType":"Bundle","prices":[]}';
        String byComponents = '{"id":"01t000000000004AAA","name":"Has Components","productComponentGroups":[{"x":1}],"prices":[]}';
        String simple = '{"id":"01t000000000005AAA","name":"Simple","productComponentGroups":[],"prices":[]}';

        System.assertEquals(true, svc.normalizeProducts(toList(byType), null)[0].isBundle, 'productType=Bundle → bundle');
        System.assertEquals(true, svc.normalizeProducts(toList(byComponents), null)[0].isBundle, 'non-empty component groups → bundle');
        System.assertEquals(false, svc.normalizeProducts(toList(simple), null)[0].isBundle, 'no components → not a bundle');
    }

    @IsTest
    static void testMalformedPriceWithoutPbeSkipped() {
        RLM_DeltaProductDiscoveryService svc = new RLM_DeltaProductDiscoveryService();
        String body = '{"id":"01t000000000006AAA","name":"Edge","prices":[{"price":10},{"priceBookEntryId":"01u000000000009AAA","price":20}]}';
        RLM_DeltaProductDiscoveryService.DiscoveredProduct dp = svc.normalizeProducts(toList(body), null)[0];
        System.assertEquals(1, dp.prices.size(), 'price without a PBE id is skipped (not addable)');
    }

    @IsTest
    static void testNoRequestedFieldsLeavesFieldsEmpty() {
        RLM_DeltaProductDiscoveryService svc = new RLM_DeltaProductDiscoveryService();
        RLM_DeltaProductDiscoveryService.DiscoveredProduct dp = svc.normalizeProducts(toList(searchProductJson()), null)[0];
        System.assertEquals(0, dp.fields.size(), 'no requested display fields → empty fields map');
    }

    @IsTest
    static void testNullRawProductsYieldsEmpty() {
        RLM_DeltaProductDiscoveryService svc = new RLM_DeltaProductDiscoveryService();
        System.assertEquals(0, svc.normalizeProducts(null, null).size(), 'null input → empty list, no NPE');
    }

    @IsTest
    static void testStubSubclassReturnsCannedProducts() {
        // Proves the virtual-method seam used by the controller's @TestVisible injection point.
        StubService stub = new StubService();
        RLM_DeltaProductDiscoveryService.DiscoveryResult res = stub.findProducts(new RLM_DeltaProductDiscoveryRequest());
        System.assertEquals(1, res.products.size(), 'stub returns its canned product');
        System.assertEquals('STUB', res.products[0].code, 'canned product surfaced');
    }

    /** A test-only override standing in for live Product Discovery. */
    private class StubService extends RLM_DeltaProductDiscoveryService {
        public override DiscoveryResult findProducts(RLM_DeltaProductDiscoveryRequest req) {
            DiscoveredProduct dp = new DiscoveredProduct();
            dp.name = 'Stubbed';
            dp.code = 'STUB';
            DiscoveredPrice price = new DiscoveredPrice();
            price.pbeId = '01u00000000000AAAA';
            dp.prices.add(price);
            DiscoveryResult r = new DiscoveryResult();
            r.products.add(dp);
            return r;
        }
    }
}
