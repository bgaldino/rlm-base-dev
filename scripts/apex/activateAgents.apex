// Activate the latest BotVersion for each RLM agent.
// BotVersion.Status is not DML-writable; activation goes through the
// Connect REST endpoint POST /connect/bot-versions/{botVersionId}/activation
// with body {"status":"Active"}. This mirrors what `sf agent activate` does.
// Latest BotVersion per agent → POST → log result.

Set<String> agentNames = new Set<String>{
    'Revenue_Quote_Management',
    'Billing_Employee_Assistance'
};

Map<Id, BotVersion> latestByBot = new Map<Id, BotVersion>();

for (BotVersion v : [
    SELECT Id, BotDefinitionId, BotDefinition.DeveloperName, VersionNumber, Status
    FROM BotVersion
    WHERE BotDefinition.DeveloperName IN :agentNames
    ORDER BY BotDefinitionId ASC, VersionNumber ASC
]) {
    latestByBot.put(v.BotDefinitionId, v); // last write wins → highest version
}

if (latestByBot.isEmpty()) {
    System.debug('No matching agents found; nothing to activate.');
    return;
}

String baseUrl = URL.getOrgDomainUrl().toExternalForm();
String apiVersion = 'v62.0';

for (BotVersion v : latestByBot.values()) {
    if (v.Status == 'Active') {
        System.debug('Already active: ' + v.BotDefinition.DeveloperName + ' v' + v.VersionNumber);
        continue;
    }

    HttpRequest req = new HttpRequest();
    req.setEndpoint(baseUrl + '/services/data/' + apiVersion + '/connect/bot-versions/' + v.Id + '/activation');
    req.setMethod('POST');
    req.setHeader('Authorization', 'Bearer ' + UserInfo.getSessionId());
    req.setHeader('Content-Type', 'application/json');
    req.setBody('{"status":"Active"}');

    HttpResponse res = new Http().send(req);
    Integer code = res.getStatusCode();
    String body = res.getBody();

    if (code >= 200 && code < 300) {
        System.debug('Activated: ' + v.BotDefinition.DeveloperName + ' v' + v.VersionNumber);
    } else {
        System.debug('Failed to activate ' + v.BotDefinition.DeveloperName + ' v' + v.VersionNumber
            + ' (HTTP ' + code + '): ' + body);
    }
}
