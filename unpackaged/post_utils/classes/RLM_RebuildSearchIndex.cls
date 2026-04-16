public with sharing class RLM_RebuildSearchIndex {

    private static final String PCM_INDEX_PATH = '/services/data/v67.0/connect/pcm/index/deploy';

    @AuraEnabled
    public static Map<String, Object> deployIndex() {
        try {
            HttpResponse httpRes = callPcmDeploy();
            return buildResultMap(httpRes);
        } catch (Exception e) {
            throw new AuraHandledException(e.getMessage());
        }
    }

    @InvocableMethod(label='Deploy PCM Index' description='Calls the Connect API to deploy PCM index after Decision Table refresh')
    public static List<PCMDeployResult> deployPCMIndex(List<PCMDeployRequest> requests) {
        List<PCMDeployResult> results = new List<PCMDeployResult>();

        for (PCMDeployRequest request : requests) {
            PCMDeployResult result = new PCMDeployResult();

            try {
                HttpResponse httpRes = callPcmDeploy();
                Map<String, Object> parsed = buildResultMap(httpRes);

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

            } catch (Exception e) {
                result.isSuccess = false;
                result.message = 'Exception occurred: ' + e.getMessage();
            }

            results.add(result);
        }

        return results;
    }

    private static HttpResponse callPcmDeploy() {
        HttpRequest httpReq = new HttpRequest();
        httpReq.setEndpoint(URL.getOrgDomainUrl().toExternalForm() + PCM_INDEX_PATH);
        httpReq.setMethod('POST');
        httpReq.setHeader('Content-Type', 'application/json');
        httpReq.setHeader('Authorization', 'Bearer ' + getApiSessionId());

        Map<String, Object> requestBody = new Map<String, Object>{
            'snapshot' => new Map<String, Object>{ 'activationType' => 'IMMEDIATE' },
            'buildType' => 'FULL'
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
        
        @InvocableVariable(label='Activation Type' description='The activation type for PCM index (default: IMMEDIATE)')
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