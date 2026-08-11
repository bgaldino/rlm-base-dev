/**
 * Tests for RLM_AssetConfiguratorService. The own-domain REST callout is
 * replaced with an HttpCalloutMock, so these tests cover request routing, verb
 * whitelisting, argument guards, and error mapping - NOT the live platform
 * contract, which must be verified on an org with a configurable bundle.
 */
@IsTest
private class RLM_AssetConfiguratorServiceTest {

    private class ConfigMock implements HttpCalloutMock {
        Integer code;
        String body;
        ConfigMock(Integer code, String body) { this.code = code; this.body = body; }
        public HttpResponse respond(HttpRequest req) {
            HttpResponse res = new HttpResponse();
            res.setStatusCode(code);
            res.setBody(body);
            res.setHeader('Content-Type', 'application/json');
            return res;
        }
    }

    private static Id fakeProductId() {
        return Id.valueOf(Product2.SObjectType.getDescribe().getKeyPrefix() + '000000000001');
    }

    @IsTest
    static void startConfiguration_success() {
        Test.setMock(HttpCalloutMock.class, new ConfigMock(200, '{"configurationId":"cfg-1","nodes":[]}'));
        Test.startTest();
        String out = RLM_AssetConfiguratorService.startConfiguration(fakeProductId(), null, 2);
        Test.stopTest();
        System.assert(out.contains('cfg-1'), 'Returns platform body');
    }

    @IsTest
    static void getInstance_and_applyAction_success() {
        Test.setMock(HttpCalloutMock.class, new ConfigMock(200, '{"ok":true}'));
        Test.startTest();
        String gi = RLM_AssetConfiguratorService.getInstance('cfg-1');
        String up = RLM_AssetConfiguratorService.applyConfiguratorAction('update-nodes', '{"configurationId":"cfg-1"}');
        Test.stopTest();
        System.assert(gi.contains('ok'));
        System.assert(up.contains('ok'));
    }

    @IsTest
    static void guards_throw() {
        Integer thrown = 0;
        try { RLM_AssetConfiguratorService.startConfiguration(null, null, 1); } catch (AuraHandledException e) { thrown++; }
        try { RLM_AssetConfiguratorService.getInstance(''); } catch (AuraHandledException e) { thrown++; }
        try { RLM_AssetConfiguratorService.applyConfiguratorAction('', '{}'); } catch (AuraHandledException e) { thrown++; }
        try { RLM_AssetConfiguratorService.applyConfiguratorAction('drop-db', '{}'); } catch (AuraHandledException e) { thrown++; }
        System.assertEquals(4, thrown, 'All guard clauses should throw AuraHandledException');
    }

    @IsTest
    static void errorStatus_mapsToException() {
        Test.setMock(HttpCalloutMock.class, new ConfigMock(400, '{"error":"bad"}'));
        Boolean threw = false;
        Test.startTest();
        try {
            RLM_AssetConfiguratorService.startConfiguration(fakeProductId(), null, 1);
        } catch (RLM_AssetConfiguratorService.ConfiguratorException e) {
            threw = true;
        }
        Test.stopTest();
        System.assert(threw, 'Non-2xx should raise ConfiguratorException');
    }
}
