// Query for DecisionTable records with Status = 'Active'
// This script deactivates decision tables so they can be updated
// Note: DecisionTable uses Tooling API for updates
// Target specific decision tables that are being deployed
List<DecisionTable> decisionTables = [
    SELECT Id, DeveloperName, Status 
    FROM DecisionTable 
    WHERE Status = 'Active' 
    AND DeveloperName IN ('RLM_CostBookEntries', 'RLM_ProductCategoryQualification', 'RLM_ProductQualification')
];

// Check if any records were found
if (!decisionTables.isEmpty()) {
    // Use Tooling API REST call to update DecisionTable records
    String baseUrl = System.Url.getOrgDomainUrl().toExternalForm();
    String sessionId = UserInfo.getSessionId();
    
    Integer successCount = 0;
    Integer errorCount = 0;
    
    for (DecisionTable dt : decisionTables) {
        try {
            HttpRequest req = new HttpRequest();
            req.setEndpoint(baseUrl + '/services/data/v60.0/tooling/sobjects/DecisionTable/' + dt.Id);
            req.setMethod('PATCH');
            req.setHeader('Authorization', 'Bearer ' + sessionId);
            req.setHeader('Content-Type', 'application/json');
            req.setBody('{"Status": "Inactive"}');
            
            Http http = new Http();
            HttpResponse res = http.send(req);
            
            if (res.getStatusCode() == 204 || res.getStatusCode() == 200) {
                successCount++;
            } else {
                errorCount++;
                System.debug('Error deactivating ' + dt.DeveloperName + ': ' + res.getStatusCode() + ' ' + res.getBody());
            }
        } catch (Exception e) {
            errorCount++;
            System.debug('Exception deactivating ' + dt.DeveloperName + ': ' + e.getMessage());
        }
    }
    
    System.debug('Deactivated ' + successCount + ' of ' + decisionTables.size() + ' DecisionTable record(s).');
    if (errorCount > 0) {
        System.debug('Failed to deactivate ' + errorCount + ' DecisionTable record(s).');
    }
    
    // Verify deactivation by querying again
    List<DecisionTable> verifyTables = [
        SELECT Id, DeveloperName, Status 
        FROM DecisionTable 
        WHERE DeveloperName IN ('RLM_CostBookEntries', 'RLM_ProductCategoryQualification', 'RLM_ProductQualification')
    ];
    for (DecisionTable dt : verifyTables) {
        System.debug('DecisionTable ' + dt.DeveloperName + ' Status: ' + dt.Status);
    }
} else {
    System.debug('No DecisionTable records found with Status = Active.');
}
