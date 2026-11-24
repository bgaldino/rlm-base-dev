public with sharing class RLM_RebuildSearchIndex {

    private static final String PCM_INDEX_PATH = '/services/data/v68.0/connect/pcm/index/deploy';
    private static final String DEFAULT_BUILD_TYPE = 'FULL';
    private static final String DEFAULT_ACTIVATION_TYPE = 'IMMEDIATE';

    @TestVisible
    private static final String DEPLOY_FAILED_MESSAGE =
        'The search index deployment could not be started. Try again; if it continues, contact your administrator.';
    @TestVisible
    private static final String NULL_REQUEST_MESSAGE = 'No request was given, so no index was deployed.';

    @AuraEnabled
    public static Map<String, Object> deployIndex() {
        try {
            HttpResponse httpRes = callPcmDeploy(DEFAULT_BUILD_TYPE, DEFAULT_ACTIVATION_TYPE);
            return buildResultMap(httpRes);
        } catch (Exception e) {
            throw RLM_UtilsAuraErrors.failed(DEPLOY_FAILED_MESSAGE, 'RLM_RebuildSearchIndex.deployIndex', e);
        }
    }

    @InvocableMethod(label='Deploy PCM Index' description='Calls the Connect API to deploy PCM index after Decision Table refresh')
    public static List<PCMDeployResult> deployPCMIndex(List<PCMDeployRequest> requests) {
        List<PCMDeployResult> results = new List<PCMDeployResult>();
        if (requests == null) {
            return results;
        }

        // One deploy per distinct buildType, not one per request: identical requests share a
        // single callout (a batch of 100+ would otherwise exceed the callout limit), and each
        // request gets its own result copy. The activation type is not part of the key because
        // IMMEDIATE is the only documented value and every request uses it.
        Map<String, Map<String, Object>> parsedByKey = new Map<String, Map<String, Object>>();
        Map<String, String> failureByKey = new Map<String, String>();

        for (PCMDeployRequest request : requests) {
            if (request == null) {
                // One output per input, in order: a null element gets a failed result in its place.
                PCMDeployResult missing = new PCMDeployResult();
                missing.isSuccess = false;
                missing.message = NULL_REQUEST_MESSAGE;
                results.add(missing);
                continue;
            }
            String buildType = normalizeBuildType(request.buildType);
            if (buildType == null) {
                // An unknown build type is rejected, not silently run as a FULL rebuild.
                PCMDeployResult rejected = new PCMDeployResult();
                rejected.isSuccess = false;
                rejected.message = 'Unsupported buildType "' + request.buildType
                    + '". Use FULL or INCREMENTAL.';
                System.debug(LoggingLevel.WARN, 'RLM_RebuildSearchIndex: ' + rejected.message);
                results.add(rejected);
                continue;
            }
            String key = buildType;

            if (!parsedByKey.containsKey(key) && !failureByKey.containsKey(key)) {
                try {
                    parsedByKey.put(key, buildResultMap(callPcmDeploy(buildType, DEFAULT_ACTIVATION_TYPE)));
                } catch (Exception e) {
                    System.debug(LoggingLevel.ERROR, 'RLM_RebuildSearchIndex.deployPCMIndex ' + key + ': '
                        + e.getTypeName() + ': ' + e.getMessage());
                    failureByKey.put(key, DEPLOY_FAILED_MESSAGE);
                }
            }

            PCMDeployResult result = new PCMDeployResult();
            if (failureByKey.containsKey(key)) {
                result.isSuccess = false;
                result.message = failureByKey.get(key);
            } else {
                Map<String, Object> parsed = parsedByKey.get(key);
                result.isSuccess      = (Boolean) parsed.get('isSuccess');
                result.message        = (String)  parsed.get('message');
                result.statusCode     = (String)  parsed.get('statusCode');
                result.snapshotId     = (String)  parsed.get('snapshotId');
                result.activationStatus = (String) parsed.get('activationStatus');
                result.activationType = (String)  parsed.get('activationType');
                result.indexId        = (String)  parsed.get('indexId');
                result.indexBuildType = (String)  parsed.get('indexBuildType');
                result.indexType      = (String)  parsed.get('indexType');
                result.lastBuildStatus = (String) parsed.get('lastBuildStatus');
            }
            results.add(result);
        }

        return results;
    }

    // Documented build types are FULL and INCREMENTAL. A blank value means the default (FULL);
    // any other value returns null so the caller can reject it.
    private static String normalizeBuildType(String value) {
        if (String.isBlank(value)) {
            return DEFAULT_BUILD_TYPE;
        }
        String candidate = value.trim().toUpperCase();
        return (candidate == 'FULL' || candidate == 'INCREMENTAL') ? candidate : null;
    }

    private static HttpResponse callPcmDeploy(String buildType, String activationType) {
        HttpRequest httpReq = new HttpRequest();
        httpReq.setEndpoint(URL.getOrgDomainUrl().toExternalForm() + PCM_INDEX_PATH);
        httpReq.setMethod('POST');
        httpReq.setHeader('Content-Type', 'application/json');
        httpReq.setHeader('Authorization', 'Bearer ' + getApiSessionId());

        Map<String, Object> requestBody = new Map<String, Object>{
            'snapshot' => new Map<String, Object>{ 'activationType' => activationType },
            'buildType' => buildType
        };
        httpReq.setBody(JSON.serialize(requestBody));

        return new Http().send(httpReq);
    }

    @TestVisible
    private static String getApiSessionId() {
        // UserInfo.getSessionId() returns a restricted Lightning session that
        // cannot call Connect/REST APIs. The VF page renders $Api.Session_ID
        // which is a full API-enabled session token.
        if (Test.isRunningTest()) {
            return 'fake-session-id';
        }
        return Page.RLM_SessionId.getContent().toString().trim();
    }

    private static Map<String, Object> buildResultMap(HttpResponse httpRes) {
        Map<String, Object> result = new Map<String, Object>();

        if (httpRes.getStatusCode() == 200 || httpRes.getStatusCode() == 201) {
            Map<String, Object> responseBody = (Map<String, Object>) JSON.deserializeUntyped(httpRes.getBody());
            Map<String, Object> snapshot = (Map<String, Object>) responseBody.get('snapshot');

            result.put('isSuccess', true);
            result.put('snapshotId', (String) snapshot.get('id'));
            result.put('activationStatus', (String) snapshot.get('activationStatus'));
            result.put('activationType', (String) snapshot.get('activationType'));
            result.put('statusCode', String.valueOf(httpRes.getStatusCode()));
            result.put('message', 'PCM Index deployment initiated successfully');

            List<Object> snapshotIndexes = (List<Object>) snapshot.get('snapshotIndexes');
            if (snapshotIndexes != null && !snapshotIndexes.isEmpty()) {
                Map<String, Object> firstIndex = (Map<String, Object>) snapshotIndexes[0];
                result.put('indexId', (String) firstIndex.get('id'));
                result.put('indexBuildType', (String) firstIndex.get('indexBuildType'));
                result.put('indexType', (String) firstIndex.get('indexType'));
                result.put('lastBuildStatus', (String) firstIndex.get('lastBuildStatus'));
            }
        } else {
            result.put('isSuccess', false);
            result.put('statusCode', String.valueOf(httpRes.getStatusCode()));
            result.put('message', 'API call failed: ' + httpRes.getStatus() + ' - ' + httpRes.getBody());
        }

        return result;
    }
    
    // Input wrapper class
    public class PCMDeployRequest {
        @InvocableVariable(label='Build Type' description='The build type for PCM index (default: FULL)')
        public String buildType = 'FULL';
        
        @InvocableVariable(label='Activation Type' description='Reserved. IMMEDIATE is the only documented activation type and is always used, whatever is passed.')
        public String activationType = 'IMMEDIATE';
    }
    
    // Output wrapper class
    public class PCMDeployResult {
        @InvocableVariable(label='Success' description='Indicates if the API call was successful')
        public Boolean isSuccess;
        
        @InvocableVariable(label='Snapshot ID' description='The ID of the created snapshot')
        public String snapshotId;
        
        @InvocableVariable(label='Activation Status' description='The activation status of the snapshot')
        public String activationStatus;
        
        @InvocableVariable(label='Activation Type' description='The activation type of the snapshot')
        public String activationType;
        
        @InvocableVariable(label='Status Code' description='HTTP status code of the API response')
        public String statusCode;
        
        @InvocableVariable(label='Message' description='Success or error message')
        public String message;
        
        @InvocableVariable(label='Index ID' description='The ID of the snapshot index')
        public String indexId;
        
        @InvocableVariable(label='Index Build Type' description='The build type of the index')
        public String indexBuildType;
        
        @InvocableVariable(label='Index Type' description='The type of the index')
        public String indexType;
        
        @InvocableVariable(label='Last Build Status' description='The last build status of the index')
        public String lastBuildStatus;
    }
}