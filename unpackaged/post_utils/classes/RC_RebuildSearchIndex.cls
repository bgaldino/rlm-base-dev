public with sharing class RC_RebuildSearchIndex {
    
    @InvocableMethod(label='Deploy PCM Index' description='Calls the Connect API to deploy PCM index after Decision Table refresh')
    public static List<PCMDeployResult> deployPCMIndex(List<PCMDeployRequest> requests) {
        List<PCMDeployResult> results = new List<PCMDeployResult>();
        
        for (PCMDeployRequest request : requests) {
            PCMDeployResult result = new PCMDeployResult();
            
            try {
                // Prepare the API request
                HttpRequest httpReq = new HttpRequest();
                // Get MyDomain URL of the Org
                String myDomainUrl = URL.getOrgDomainUrl().toExternalForm();
                String endpoint = myDomainUrl + '/services/data/v66.0/connect/pcm/index/deploy';
                httpReq.setEndpoint(endpoint);
                httpReq.setMethod('POST');
                httpReq.setHeader('Content-Type', 'application/json');
                // Add Authorization header with Session ID
                httpReq.setHeader('Authorization', 'Bearer ' + UserInfo.getSessionId());
                
                // Build the request body
                Map<String, Object> requestBody = new Map<String, Object>{
                    'snapshot' => new Map<String, Object>{
                        'activationType' => 'IMMEDIATE'
                    },
                    'buildType' => 'FULL'
                };
                
                httpReq.setBody(JSON.serialize(requestBody));
                
                // Make the API call
                Http http = new Http();
                HttpResponse httpRes = http.send(httpReq);
                
                // Process the response
                if (httpRes.getStatusCode() == 200 || httpRes.getStatusCode() == 201) {
                    Map<String, Object> responseBody = (Map<String, Object>) JSON.deserializeUntyped(httpRes.getBody());
                    Map<String, Object> snapshot = (Map<String, Object>) responseBody.get('snapshot');
                    
                    result.isSuccess = true;
                    result.snapshotId = (String) snapshot.get('id');
                    result.activationStatus = (String) snapshot.get('activationStatus');
                    result.activationType = (String) snapshot.get('activationType');
                    result.statusCode = String.valueOf(httpRes.getStatusCode());
                    result.message = 'PCM Index deployment initiated successfully';
                    
                    // Process snapshot indexes if available
                    List<Object> snapshotIndexes = (List<Object>) snapshot.get('snapshotIndexes');
                    if (snapshotIndexes != null && !snapshotIndexes.isEmpty()) {
                        Map<String, Object> firstIndex = (Map<String, Object>) snapshotIndexes[0];
                        result.indexId = (String) firstIndex.get('id');
                        result.indexBuildType = (String) firstIndex.get('indexBuildType');
                        result.indexType = (String) firstIndex.get('indexType');
                        result.lastBuildStatus = (String) firstIndex.get('lastBuildStatus');
                    }
                } else {
                    result.isSuccess = false;
                    result.statusCode = String.valueOf(httpRes.getStatusCode());
                    result.message = 'API call failed: ' + httpRes.getStatus() + ' - ' + httpRes.getBody();
                }
                
            } catch (Exception e) {
                result.isSuccess = false;
                result.message = 'Exception occurred: ' + e.getMessage();
                System.debug('PCM Index Deploy Error: ' + e.getMessage());
            }
            
            results.add(result);
        }
        
        return results;
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