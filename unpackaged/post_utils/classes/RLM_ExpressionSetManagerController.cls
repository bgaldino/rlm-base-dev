/**
 * RLM_ExpressionSetManagerController
 *
 * Apex controller for the rlmExpressionSetManager Lightning Web Component.
 * Manages Expression Sets linked to a Context Definition: lists linked
 * (and unlinked Constraint) Expression Sets, and bulk activates / deactivates
 * Expression Set Versions plus Constraint context-definition junctions.
 *
 * Activation/deactivation work runs in Queueables that callout to the
 * Composite REST API, authenticated via the RLM_SessionId Visualforce page.
 * Composite subrequest failures throw so the AsyncApexJob is marked Failed
 * and the LWC poll loop terminates with a surfaced error.
 */
public with sharing class RLM_ExpressionSetManagerController {

    private static final String API_VERSION = 'v67.0';

    @AuraEnabled(cacheable=true)
    public static List<ContextDefinitionWrapper> getContextDefinitions() {
        List<ContextDefinition> defs = [
            SELECT Id, DeveloperName, MasterLabel
            FROM ContextDefinition
            ORDER BY MasterLabel
        ];

        Map<Id, Integer> countsByContext = new Map<Id, Integer>();
        for (AggregateResult ar : [
            SELECT ContextDefinitionId, COUNT_DISTINCT(ExpressionSetDefinitionId) cnt
            FROM ExpressionSetDefinitionContextDefinition
            WHERE ContextDefinitionId IN :defs
            GROUP BY ContextDefinitionId
        ]) {
            countsByContext.put((Id) ar.get('ContextDefinitionId'), (Integer) ar.get('cnt'));
        }

        List<ContextDefinitionWrapper> results = new List<ContextDefinitionWrapper>();
        for (ContextDefinition cd : defs) {
            Integer count = countsByContext.containsKey(cd.Id) ? countsByContext.get(cd.Id) : 0;
            results.add(new ContextDefinitionWrapper(cd.Id, cd.DeveloperName, cd.MasterLabel, count));
        }
        return results;
    }

    @AuraEnabled
    public static List<ExpressionSetInfo> getLinkedExpressionSets(Id contextDefinitionId) {
        // Get currently linked expression sets
        Set<Id> linkedDefIds = new Set<Id>();
        for (ExpressionSetDefinitionContextDefinition j : [
            SELECT ExpressionSetDefinitionId
            FROM ExpressionSetDefinitionContextDefinition
            WHERE ContextDefinitionId = :contextDefinitionId
        ]) {
            linkedDefIds.add(j.ExpressionSetDefinitionId);
        }

        // Find unlinked Constraint expression sets (not linked to this context def)
        Set<Id> unlinkedConstraintDefIds = new Set<Id>();
        for (ExpressionSet es : [
            SELECT ExpressionSetDefinitionId
            FROM ExpressionSet
            WHERE UsageType = 'Constraint'
            AND ExpressionSetDefinitionId NOT IN :linkedDefIds
        ]) {
            unlinkedConstraintDefIds.add(es.ExpressionSetDefinitionId);
        }

        // Combine both sets
        Set<Id> allDefIds = new Set<Id>();
        allDefIds.addAll(linkedDefIds);
        allDefIds.addAll(unlinkedConstraintDefIds);

        if (allDefIds.isEmpty()) {
            return new List<ExpressionSetInfo>();
        }

        Map<Id, ExpressionSetDefinition> defs = new Map<Id, ExpressionSetDefinition>([
            SELECT Id, DeveloperName, MasterLabel
            FROM ExpressionSetDefinition
            WHERE Id IN :allDefIds
            ORDER BY MasterLabel
        ]);

        List<ExpressionSet> sets = [
            SELECT Id, ExpressionSetDefinitionId, UsageType
            FROM ExpressionSet
            WHERE ExpressionSetDefinitionId IN :allDefIds
        ];

        Map<Id, Id> setToDefMap = new Map<Id, Id>();
        Map<Id, Id> defToSetMap = new Map<Id, Id>();
        Map<Id, String> defToUsageType = new Map<Id, String>();
        Set<Id> setIds = new Set<Id>();
        for (ExpressionSet es : sets) {
            setIds.add(es.Id);
            setToDefMap.put(es.Id, es.ExpressionSetDefinitionId);
            defToSetMap.put(es.ExpressionSetDefinitionId, es.Id);
            defToUsageType.put(es.ExpressionSetDefinitionId, es.UsageType);
        }

        List<ExpressionSetVersion> versions = [
            SELECT Id, ExpressionSetId, VersionNumber, IsActive, Rank
            FROM ExpressionSetVersion
            WHERE ExpressionSetId IN :setIds
            ORDER BY ExpressionSetId, VersionNumber DESC
        ];

        Map<Id, List<ExpressionSetVersion>> versionsByDef = new Map<Id, List<ExpressionSetVersion>>();
        for (ExpressionSetVersion v : versions) {
            Id defId = setToDefMap.get(v.ExpressionSetId);
            if (!versionsByDef.containsKey(defId)) {
                versionsByDef.put(defId, new List<ExpressionSetVersion>());
            }
            versionsByDef.get(defId).add(v);
        }

        List<ExpressionSetInfo> results = new List<ExpressionSetInfo>();
        for (Id defId : allDefIds) {
            ExpressionSetDefinition def = defs.get(defId);
            if (def == null) continue;

            List<ExpressionSetVersion> defVersions = versionsByDef.containsKey(defId)
                ? versionsByDef.get(defId)
                : new List<ExpressionSetVersion>();

            Boolean hasActive = false;
            for (ExpressionSetVersion v : defVersions) {
                if (v.IsActive) {
                    hasActive = true;
                    break;
                }
            }

            Boolean isLinked = linkedDefIds.contains(defId);
            results.add(new ExpressionSetInfo(
                def,
                defToSetMap.get(defId),
                defToUsageType.get(defId),
                defVersions,
                hasActive,
                isLinked
            ));
        }
        return results;
    }

    @AuraEnabled
    public static String getActiveJobStatus() {
        Datetime cutoff = Datetime.now().addMinutes(-30);

        List<AsyncApexJob> runningJobs = [
            SELECT Id
            FROM AsyncApexJob
            WHERE ApexClass.Name = 'RLM_ExpressionSetManagerController'
            AND Status IN ('Queued', 'Preparing', 'Processing')
            AND CreatedDate > :cutoff
            LIMIT 1
        ];
        if (!runningJobs.isEmpty()) {
            return 'running';
        }

        List<AsyncApexJob> recentJobs = [
            SELECT Id, Status, ExtendedStatus
            FROM AsyncApexJob
            WHERE ApexClass.Name = 'RLM_ExpressionSetManagerController'
            AND CreatedDate > :cutoff
            ORDER BY CreatedDate DESC
            LIMIT 1
        ];
        if (!recentJobs.isEmpty() && recentJobs[0].Status == 'Failed') {
            String msg = recentJobs[0].ExtendedStatus != null ? recentJobs[0].ExtendedStatus : 'Unknown error';
            return 'failed:' + msg;
        }

        return 'none';
    }

    @AuraEnabled
    public static void deactivateExpressionSets(Id contextDefinitionId, List<Id> definitionIds) {
        // ExpressionSetVersion is the only object actually mutated via Apex SOQL/DML
        // before enqueuing — the junction object is mutated through Composite REST
        // (where the session-id user's permissions are enforced server-side), and
        // its describe returns false for createable/deletable on every profile.
        if (!ExpressionSetVersion.SObjectType.getDescribe().isUpdateable()
                || !ExpressionSetVersion.IsActive.getDescribe().isUpdateable()) {
            throw new AuraHandledException('Insufficient access to deactivate Expression Sets.');
        }
        String sessionId = getApiSessionId();
        // Identify which are Constraint type — those need junction deletion
        Set<Id> constraintDefIds = new Set<Id>();
        for (ExpressionSet es : [
            SELECT ExpressionSetDefinitionId FROM ExpressionSet
            WHERE ExpressionSetDefinitionId IN :definitionIds
            AND UsageType = 'Constraint'
        ]) {
            constraintDefIds.add(es.ExpressionSetDefinitionId);
        }
        System.enqueueJob(new DeactivateQueueable(contextDefinitionId, definitionIds, constraintDefIds, sessionId));
    }

    @AuraEnabled
    public static String getDeactivateStatus(Id contextDefinitionId, List<Id> definitionIds) {
        Integer activeCount = countActiveVersions(definitionIds);
        if (activeCount > 0) return 'in_progress';

        // Also verify constraint junctions are deleted
        Set<Id> constraintDefIds = new Set<Id>();
        for (ExpressionSet es : [
            SELECT ExpressionSetDefinitionId FROM ExpressionSet
            WHERE ExpressionSetDefinitionId IN :definitionIds
            AND UsageType = 'Constraint'
        ]) {
            constraintDefIds.add(es.ExpressionSetDefinitionId);
        }
        if (!constraintDefIds.isEmpty()) {
            Integer remaining = [
                SELECT COUNT()
                FROM ExpressionSetDefinitionContextDefinition
                WHERE ContextDefinitionId = :contextDefinitionId
                AND ExpressionSetDefinitionId IN :constraintDefIds
            ];
            if (remaining > 0) return 'in_progress';
        }

        return 'complete';
    }

    @AuraEnabled
    public static void activateExpressionSets(Id contextDefinitionId, List<Id> definitionIds) {
        // See deactivateExpressionSets — junction is mutated via Composite REST,
        // not Apex DML, so we only guard the field we actually update from Apex.
        if (!ExpressionSetVersion.SObjectType.getDescribe().isUpdateable()
                || !ExpressionSetVersion.IsActive.getDescribe().isUpdateable()) {
            throw new AuraHandledException('Insufficient access to activate Expression Sets.');
        }
        String sessionId = getApiSessionId();
        // Find which ones need junction recreation
        Set<Id> existingDefIds = new Set<Id>();
        for (ExpressionSetDefinitionContextDefinition j : [
            SELECT ExpressionSetDefinitionId
            FROM ExpressionSetDefinitionContextDefinition
            WHERE ContextDefinitionId = :contextDefinitionId
            AND ExpressionSetDefinitionId IN :definitionIds
        ]) {
            existingDefIds.add(j.ExpressionSetDefinitionId);
        }
        Set<Id> needsJunction = new Set<Id>();
        for (Id defId : definitionIds) {
            if (!existingDefIds.contains(defId)) {
                needsJunction.add(defId);
            }
        }
        System.enqueueJob(new ActivateQueueable(contextDefinitionId, definitionIds, needsJunction, sessionId));
    }

    @AuraEnabled
    public static String getActivateStatus(Id contextDefinitionId, List<Id> definitionIds) {
        // Check all junctions exist
        Integer junctionCount = [
            SELECT COUNT()
            FROM ExpressionSetDefinitionContextDefinition
            WHERE ContextDefinitionId = :contextDefinitionId
            AND ExpressionSetDefinitionId IN :definitionIds
        ];
        if (junctionCount < definitionIds.size()) return 'in_progress';

        Integer activeCount = countActiveVersions(definitionIds);
        return activeCount >= definitionIds.size() ? 'complete' : 'in_progress';
    }

    // --- Queueables ---

    public class DeactivateQueueable implements Queueable, Database.AllowsCallouts {
        private Id contextDefinitionId;
        private List<Id> definitionIds;
        private Set<Id> constraintDefIds;
        private String sessionId;

        public DeactivateQueueable(Id contextDefinitionId, List<Id> definitionIds, Set<Id> constraintDefIds, String sessionId) {
            this.contextDefinitionId = contextDefinitionId;
            this.definitionIds = definitionIds;
            this.constraintDefIds = constraintDefIds;
            this.sessionId = sessionId;
        }

        public void execute(QueueableContext ctx) {
            String baseUrl = System.Url.getOrgDomainUrl().toExternalForm();
            Set<Id> setIds = getExpressionSetIds(definitionIds);

            // Deactivate all active versions
            List<ExpressionSetVersion> activeVersions = [
                SELECT Id FROM ExpressionSetVersion
                WHERE ExpressionSetId IN :setIds
                AND IsActive = true
            ];

            if (!activeVersions.isEmpty()) {
                List<Object> subrequests = new List<Object>();
                for (Integer i = 0; i < activeVersions.size(); i++) {
                    subrequests.add(buildVersionPatch(activeVersions[i].Id, false, null, i));
                }
                sendCompositeInChunks(baseUrl, sessionId, subrequests);
            }

            // Delete junctions for Constraint types (platform requires this)
            if (!constraintDefIds.isEmpty()) {
                List<ExpressionSetDefinitionContextDefinition> junctions = [
                    SELECT Id FROM ExpressionSetDefinitionContextDefinition
                    WHERE ContextDefinitionId = :contextDefinitionId
                    AND ExpressionSetDefinitionId IN :constraintDefIds
                ];
                if (!junctions.isEmpty()) {
                    List<String> ids = new List<String>();
                    for (ExpressionSetDefinitionContextDefinition j : junctions) {
                        ids.add(j.Id);
                    }
                    deleteRecords(baseUrl, sessionId, ids);
                }
            }
        }
    }

    public class ActivateQueueable implements Queueable, Database.AllowsCallouts {
        private Id contextDefinitionId;
        private List<Id> definitionIds;
        private Set<Id> needsJunction;
        private String sessionId;

        public ActivateQueueable(Id contextDefinitionId, List<Id> definitionIds, Set<Id> needsJunction, String sessionId) {
            this.contextDefinitionId = contextDefinitionId;
            this.definitionIds = definitionIds;
            this.needsJunction = needsJunction;
            this.sessionId = sessionId;
        }

        public void execute(QueueableContext ctx) {
            String baseUrl = System.Url.getOrgDomainUrl().toExternalForm();

            List<Object> subrequests = new List<Object>();
            Integer refIdx = 0;

            // Recreate junctions for unlinked constraints
            for (Id defId : needsJunction) {
                Map<String, Object> sub = new Map<String, Object>();
                sub.put('method', 'POST');
                sub.put('url', '/services/data/' + API_VERSION + '/sobjects/ExpressionSetDefinitionContextDefinition');
                sub.put('referenceId', 'junction_' + refIdx);
                sub.put('body', new Map<String, Object>{
                    'ExpressionSetDefinitionId' => defId,
                    'ContextDefinitionId' => contextDefinitionId
                });
                subrequests.add(sub);
                refIdx++;
            }

            // Activate highest version per expression set
            Set<Id> setIds = getExpressionSetIds(definitionIds);

            List<ExpressionSetVersion> allVersions = [
                SELECT Id, ExpressionSetId, VersionNumber, Rank
                FROM ExpressionSetVersion
                WHERE ExpressionSetId IN :setIds
                AND IsActive = false
                ORDER BY ExpressionSetId, VersionNumber DESC
            ];

            Set<Id> activated = new Set<Id>();
            for (ExpressionSetVersion v : allVersions) {
                if (!activated.contains(v.ExpressionSetId)) {
                    subrequests.add(buildVersionPatch(v.Id, true, v.Rank, refIdx));
                    activated.add(v.ExpressionSetId);
                    refIdx++;
                }
            }

            if (!subrequests.isEmpty()) {
                sendCompositeInChunks(baseUrl, sessionId, subrequests);
            }
        }
    }

    // --- Shared Helpers ---

    private static Set<Id> getExpressionSetIds(List<Id> definitionIds) {
        Set<Id> setIds = new Set<Id>();
        for (ExpressionSet es : [
            SELECT Id FROM ExpressionSet WHERE ExpressionSetDefinitionId IN :definitionIds
        ]) {
            setIds.add(es.Id);
        }
        return setIds;
    }

    private static Integer countActiveVersions(List<Id> definitionIds) {
        Set<Id> setIds = getExpressionSetIds(definitionIds);
        return [
            SELECT COUNT()
            FROM ExpressionSetVersion
            WHERE ExpressionSetId IN :setIds
            AND IsActive = true
        ];
    }

    private static Map<String, Object> buildVersionPatch(Id versionId, Boolean setActive, Integer currentRank, Integer refIdx) {
        Map<String, Object> sub = new Map<String, Object>();
        sub.put('method', 'PATCH');
        sub.put('url', '/services/data/' + API_VERSION + '/sobjects/ExpressionSetVersion/' + versionId);
        sub.put('referenceId', (setActive ? 'activate_' : 'deactivate_') + refIdx);
        Map<String, Object> body = new Map<String, Object>{ 'IsActive' => setActive };
        if (setActive && currentRank == null) {
            body.put('Rank', 1);
        }
        sub.put('body', body);
        return sub;
    }

    private static void deleteRecords(String baseUrl, String sessionId, List<String> recordIds) {
        for (Integer i = 0; i < recordIds.size(); i += 200) {
            Integer chunkEnd = Math.min(i + 200, recordIds.size());
            List<String> chunk = new List<String>();
            for (Integer j = i; j < chunkEnd; j++) {
                chunk.add(recordIds[j]);
            }
            HttpRequest req = new HttpRequest();
            req.setEndpoint(baseUrl + '/services/data/' + API_VERSION + '/composite/sobjects?ids=' + String.join(chunk, ','));
            req.setMethod('DELETE');
            req.setHeader('Authorization', 'Bearer ' + sessionId);
            req.setTimeout(120000);

            Http http = new Http();
            HttpResponse res = http.send(req);
            if (res.getStatusCode() != 200) {
                throw new CalloutException('Composite delete failed: ' + res.getStatusCode() + ' ' + res.getBody());
            }
        }
    }

    private static void sendCompositeInChunks(String baseUrl, String sessionId, List<Object> subrequests) {
        for (Integer i = 0; i < subrequests.size(); i += 25) {
            Integer chunkEnd = Math.min(i + 25, subrequests.size());
            List<Object> chunk = new List<Object>();
            for (Integer j = i; j < chunkEnd; j++) {
                chunk.add(subrequests[j]);
            }
            sendComposite(baseUrl, sessionId, chunk);
        }
    }

    private static void sendComposite(String baseUrl, String sessionId, List<Object> subrequests) {
        Map<String, Object> compositeBody = new Map<String, Object>{
            'allOrNone' => true,
            'compositeRequest' => subrequests
        };

        HttpRequest req = new HttpRequest();
        req.setEndpoint(baseUrl + '/services/data/' + API_VERSION + '/composite');
        req.setMethod('POST');
        req.setHeader('Authorization', 'Bearer ' + sessionId);
        req.setHeader('Content-Type', 'application/json');
        req.setBody(JSON.serialize(compositeBody));
        req.setTimeout(120000);

        Http http = new Http();
        HttpResponse res = http.send(req);

        if (res.getStatusCode() != 200) {
            throw new CalloutException('Composite request failed: ' + res.getStatusCode() + ' ' + res.getBody());
        }

        Map<String, Object> result = (Map<String, Object>) JSON.deserializeUntyped(res.getBody());
        List<Object> results = (List<Object>) result.get('compositeResponse');
        List<String> failures = new List<String>();
        for (Object r : results) {
            Map<String, Object> subResult = (Map<String, Object>) r;
            Integer httpStatusCode = (Integer) subResult.get('httpStatusCode');
            if (httpStatusCode >= 400) {
                failures.add(JSON.serialize(subResult));
            }
        }
        if (!failures.isEmpty()) {
            throw new CalloutException('Composite subrequest(s) failed: ' + String.join(failures, '; '));
        }
    }

    @TestVisible
    private static String getApiSessionId() {
        if (Test.isRunningTest()) {
            return 'fake-session-id';
        }
        return Page.RLM_SessionId.getContent().toString().trim();
    }

    // --- DTOs ---

    public class ContextDefinitionWrapper {
        @AuraEnabled public Id id;
        @AuraEnabled public String developerName;
        @AuraEnabled public String label;
        @AuraEnabled public Integer expressionSetCount;

        public ContextDefinitionWrapper(Id id, String developerName, String label, Integer expressionSetCount) {
            this.id = id;
            this.developerName = developerName;
            this.label = label;
            this.expressionSetCount = expressionSetCount;
        }
    }

    public class ExpressionSetInfo {
        @AuraEnabled public Id definitionId;
        @AuraEnabled public Id expressionSetId;
        @AuraEnabled public String developerName;
        @AuraEnabled public String label;
        @AuraEnabled public String usageType;
        @AuraEnabled public Boolean hasActiveVersion;
        @AuraEnabled public Boolean isLinked;
        @AuraEnabled public List<VersionInfo> versions;

        public ExpressionSetInfo(ExpressionSetDefinition def, Id esId, String usageType, List<ExpressionSetVersion> versions, Boolean hasActive, Boolean isLinked) {
            this.definitionId = def.Id;
            this.expressionSetId = esId;
            this.developerName = def.DeveloperName;
            this.label = def.MasterLabel;
            this.usageType = usageType;
            this.hasActiveVersion = hasActive;
            this.isLinked = isLinked;
            this.versions = new List<VersionInfo>();
            for (ExpressionSetVersion v : versions) {
                this.versions.add(new VersionInfo(v));
            }
        }
    }

    public class VersionInfo {
        @AuraEnabled public Id versionId;
        @AuraEnabled public Integer versionNumber;
        @AuraEnabled public Boolean isActive;
        @AuraEnabled public Integer rank;

        public VersionInfo(ExpressionSetVersion v) {
            this.versionId = v.Id;
            this.versionNumber = v.VersionNumber;
            this.isActive = v.IsActive;
            this.rank = v.Rank;
        }
    }
}
