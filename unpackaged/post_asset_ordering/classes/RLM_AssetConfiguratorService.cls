/**
 * Phase 2 - Guided reconfiguration.
 *
 * Thin Apex bridge to the native Product Configurator Connect API
 * (/connect/cpq/configurator/actions/*). The console launches a guided
 * configuration session for a product/line on the consolidated transaction
 * (Quote) produced by Phase 1, so an agent can reconfigure a bundle inside the
 * same flow. All configuration logic (option groups, constraints, pricing) stays
 * server-side in the platform engine - this class only transports requests.
 *
 * Callout pattern mirrors RLM_ExpressionSetManagerController: own-domain REST via
 * System.Url.getOrgDomainUrl() + the RLM_SessionId VF page session id (no remote
 * site setting required for the org's own My Domain).
 *
 * ⚠ LIVE-VERIFICATION REQUIRED: the exact v67 configure request/response shape
 * was not exercised in Phase 0 (org had no configurable products). Treat the
 * request bodies here as the documented shape and confirm against a live org
 * with a configurable bundle before relying on this in production. See
 * .agents/artifacts/abo-endpoint-verification.md and the feature doc.
 */
public with sharing class RLM_AssetConfiguratorService {

    private static final String API_VERSION = 'v67.0';
    private static final String BASE = '/services/data/' + API_VERSION + '/connect/cpq/configurator';

    public class ConfiguratorException extends Exception {}

    /**
     * Start (or continue) a guided configuration for a product. Returns the raw
     * configuration-instance JSON from the platform for the LWC to render.
     *
     * @param productId       product to configure (required)
     * @param transactionId   the consolidated Quote/Order id this config belongs to (optional context)
     * @param quantity        requested quantity (defaults to 1)
     */
    @AuraEnabled
    public static String startConfiguration(Id productId, Id transactionId, Decimal quantity) {
        if (productId == null) {
            throw new AuraHandledException('A product id is required to start configuration.');
        }
        Id prodId = Id.valueOf(productId);
        Map<String, Object> body = new Map<String, Object>{
            'productId' => prodId,
            'quantity' => (quantity == null ? 1 : quantity)
        };
        if (transactionId != null) {
            body.put('salesTransactionId', Id.valueOf(transactionId));
        }
        return callConfigurator('/actions/configure', JSON.serialize(body));
    }

    /**
     * Retrieve the current state of a configuration instance.
     */
    @AuraEnabled
    public static String getInstance(String configurationId) {
        if (String.isBlank(configurationId)) {
            throw new AuraHandledException('A configuration id is required.');
        }
        Map<String, Object> body = new Map<String, Object>{
            'configurationId' => configurationId
        };
        return callConfigurator('/actions/get-instance', JSON.serialize(body));
    }

    /**
     * Generic passthrough for node operations (add/update/delete nodes,
     * set-product-quantity). The LWC supplies the platform-shaped body; this
     * method transports it and returns the updated instance JSON. Kept generic
     * so the client can drive the full configure loop without an Apex change per
     * node verb.
     *
     * @param action e.g. 'update-nodes', 'add-nodes', 'delete-nodes', 'set-product-quantity'
     * @param bodyJson platform-shaped request body
     */
    @AuraEnabled
    public static String applyConfiguratorAction(String action, String bodyJson) {
        if (String.isBlank(action)) {
            throw new AuraHandledException('A configurator action is required.');
        }
        if (String.isBlank(bodyJson)) {
            throw new AuraHandledException('A request body is required.');
        }
        // Whitelist the action verbs to avoid arbitrary path injection.
        Set<String> allowed = new Set<String>{
            'configure', 'get-instance', 'update-nodes', 'add-nodes',
            'delete-nodes', 'set-product-quantity', 'save-instance', 'load-instance'
        };
        String verb = action.trim();
        if (!allowed.contains(verb)) {
            throw new AuraHandledException('Unsupported configurator action: ' + verb);
        }
        return callConfigurator('/actions/' + verb, bodyJson);
    }

    // ------------------------------------------------------------------
    // Callout
    // ------------------------------------------------------------------
    private static String callConfigurator(String path, String bodyJson) {
        HttpRequest req = new HttpRequest();
        req.setEndpoint(orgBaseUrl() + BASE + path);
        req.setMethod('POST');
        req.setHeader('Authorization', 'Bearer ' + sessionId());
        req.setHeader('Content-Type', 'application/json');
        req.setBody(bodyJson);
        req.setTimeout(120000);

        HttpResponse res = new Http().send(req);
        Integer code = res.getStatusCode();
        if (code >= 200 && code < 300) {
            return res.getBody();
        }
        throw new ConfiguratorException(
            'Configurator ' + path + ' failed (' + code + '): ' + res.getBody());
    }

    private static String orgBaseUrl() {
        return System.Url.getOrgDomainUrl().toExternalForm();
    }

    @TestVisible
    private static String sessionId() {
        // In tests, PageReference.getContent() is not permitted; the callout is
        // mocked at the Http layer, so return a stub.
        if (Test.isRunningTest()) {
            return 'TEST_SESSION_ID';
        }
        return Page.RLM_SessionId.getContent().toString().trim();
    }
}
