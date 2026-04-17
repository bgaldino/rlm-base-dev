/*
 * Grant External Credential Principal Access to the RLM_MFG_RCA permission set.
 *
 * Salesforce does not support externalCredentialPrincipalAccess in the PermissionSet
 * Metadata API (the element is rejected as invalid on both retrieve and deploy).
 * This script works around that limitation by:
 *   1. Calling the Tooling API via HTTP to query ExternalCredentialParameter IDs
 *      by principal name (Tooling-only objects, not accessible from standard SOQL).
 *   2. Inserting SetupEntityAccess records via DML to grant each principal to the
 *      RLM_MFG_RCA permission set.
 *
 * Idempotent: skips principals already granted.
 *
 * Credentials granted:
 *   - BillingSystemExtCredentials    / Billing System Principal
 *   - SalesforceContractsExtCredentials / SalesforceContracts
 */

// --- Config ---
String permSetApiName = 'RLM_MFG_RCA';
List<String> targetPrincipalNames = new List<String>{
    'Billing System Principal',
    'SalesforceContracts'
};

// --- Step 1: Tooling API callout to get ExternalCredentialParameter IDs ---
String soql =
    'SELECT Id, ParameterName FROM ExternalCredentialParameter ' +
    'WHERE ParameterType = \'NamedPrincipal\' ' +
    'AND ParameterName IN (\'' + String.join(targetPrincipalNames, '\',\'') + '\')';

String endpoint =
    URL.getOrgDomainUrl().toExternalForm() +
    '/services/data/v66.0/tooling/query?q=' +
    EncodingUtil.urlEncode(soql, 'UTF-8');

HttpRequest req = new HttpRequest();
req.setEndpoint(endpoint);
req.setMethod('GET');
req.setHeader('Authorization', 'Bearer ' + UserInfo.getSessionId());
req.setHeader('Content-Type', 'application/json');

Http http = new Http();
HttpResponse res = http.send(req);

if (res.getStatusCode() != 200) {
    throw new CalloutException(
        'Tooling API query failed [' + res.getStatusCode() + ']: ' + res.getBody()
    );
}

// --- Step 2: Parse principal IDs from Tooling API response ---
Map<String, Object> responseMap = (Map<String, Object>) JSON.deserializeUntyped(res.getBody());
List<Object> records = (List<Object>) responseMap.get('records');

if (records == null || records.isEmpty()) {
    System.debug('WARNING: No ExternalCredentialParameter records found for target principals. Skipping.');
    return;
}

Map<String, Id> principalIdsByName = new Map<String, Id>();
for (Object record : records) {
    Map<String, Object> rec = (Map<String, Object>) record;
    principalIdsByName.put((String) rec.get('ParameterName'), (Id) rec.get('Id'));
}
System.debug('Found ExternalCredentialParameter IDs: ' + principalIdsByName);

// --- Step 3: Query target PermissionSet ---
PermissionSet ps = [SELECT Id FROM PermissionSet WHERE Name = :permSetApiName LIMIT 1];

// --- Step 4: Find which principals are already granted ---
Set<Id> alreadyGranted = new Set<Id>();
for (SetupEntityAccess existing : [
    SELECT SetupEntityId
    FROM SetupEntityAccess
    WHERE ParentId = :ps.Id
    AND SetupEntityId IN :principalIdsByName.values()
]) {
    alreadyGranted.add(existing.SetupEntityId);
}

// --- Step 5: Insert missing SetupEntityAccess records ---
List<SetupEntityAccess> toInsert = new List<SetupEntityAccess>();
for (String principalName : principalIdsByName.keySet()) {
    Id principalId = principalIdsByName.get(principalName);
    if (!alreadyGranted.contains(principalId)) {
        toInsert.add(new SetupEntityAccess(
            ParentId = ps.Id,
            SetupEntityId = principalId
        ));
        System.debug('Queued grant for principal: ' + principalName);
    } else {
        System.debug('Already granted, skipping: ' + principalName);
    }
}

if (!toInsert.isEmpty()) {
    insert toInsert;
    System.debug('SUCCESS: Granted ' + toInsert.size() + ' external credential principal access(es) to ' + permSetApiName + '.');
} else {
    System.debug('All external credential principal accesses already present on ' + permSetApiName + '. Nothing to do.');
}
