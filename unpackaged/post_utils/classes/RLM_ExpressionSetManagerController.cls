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
 *
 * ⚠ Atomicity: a bulk action is NOT one transaction. Each Composite request is
 * sent with allOrNone=true, and each sObject-Collections delete batch likewise,
 * so an individual request rolls back on failure — but a selection that
 * generates more than 25 subrequests is split across several requests, and
 * chunks that already succeeded stay committed. sendCompositeInChunks reports
 * how much was applied when it fails past the first chunk, and the LWC's status
 * poll reloads true per-row state. Capping an operation at a single transaction
 * (or adding resume/compensation) is tracked in issue #305.
 */
public with sharing class RLM_ExpressionSetManagerController {

    private static final String API_VERSION = 'v67.0';
    private static final String OPERATION_MAKE_ACTIVE = 'make_active';
    private static final String OPERATION_MAKE_INACTIVE = 'make_inactive';
    private static final Set<String> RUNNING_JOB_STATUSES = new Set<String>{ 'Queued', 'Preparing', 'Processing', 'Holding' };
    private static final Set<String> FAILED_JOB_STATUSES = new Set<String>{ 'Failed', 'Aborted' };

    @AuraEnabled(cacheable=true)
    public static List<ContextDefinitionWrapper> getContextDefinitions() {
        List<ContextDefinition> defs = [
            SELECT Id, DeveloperName, MasterLabel
            FROM ContextDefinition
            WITH USER_MODE
            ORDER BY MasterLabel
        ];

        Map<Id, Integer> countsByContext = new Map<Id, Integer>();
        for (AggregateResult ar : [
            SELECT ContextDefinitionId, COUNT_DISTINCT(ExpressionSetDefinitionId) cnt
            FROM ExpressionSetDefinitionContextDefinition
            WHERE ContextDefinitionId IN :defs
            WITH USER_MODE
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
        Set<Id> linkedDefIds = new Set<Id>();
        for (ExpressionSetDefinitionContextDefinition j : [
            SELECT ExpressionSetDefinitionId
            FROM ExpressionSetDefinitionContextDefinition
            WHERE ContextDefinitionId = :contextDefinitionId
            WITH USER_MODE
        ]) {
            linkedDefIds.add(j.ExpressionSetDefinitionId);
        }

        Set<Id> unlinkedConstraintDefIds = new Set<Id>();
        for (ExpressionSet es : [
            SELECT ExpressionSetDefinitionId
            FROM ExpressionSet
            WHERE UsageType = 'Constraint'
            AND ExpressionSetDefinitionId NOT IN :linkedDefIds
            WITH USER_MODE
        ]) {
            unlinkedConstraintDefIds.add(es.ExpressionSetDefinitionId);
        }

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
            WITH USER_MODE
            ORDER BY MasterLabel
        ]);

        List<ExpressionSet> sets = [
            SELECT Id, ExpressionSetDefinitionId, UsageType
            FROM ExpressionSet
            WHERE ExpressionSetDefinitionId IN :allDefIds
            WITH USER_MODE
        ];

        Map<Id, ExpressionSet> setByDefId = new Map<Id, ExpressionSet>();
        Set<Id> setIds = new Set<Id>();
        for (ExpressionSet es : sets) {
            setIds.add(es.Id);
            setByDefId.put(es.ExpressionSetDefinitionId, es);
        }

        Map<Id, Boolean> hasActiveBySetId = new Map<Id, Boolean>();
        for (AggregateResult ar : [
            SELECT ExpressionSetId setId, COUNT(Id) activeCount
            FROM ExpressionSetVersion
            WHERE ExpressionSetId IN :setIds
            AND IsActive = true
            WITH USER_MODE
            GROUP BY ExpressionSetId
        ]) {
            hasActiveBySetId.put((Id) ar.get('setId'), ((Integer) ar.get('activeCount')) > 0);
        }

        Map<Id, Integer> latestVersionNumberBySetId = new Map<Id, Integer>();
        Set<Integer> latestVersionNumbers = new Set<Integer>();
        for (AggregateResult ar : [
            SELECT ExpressionSetId setId, MAX(VersionNumber) latestVersionNumber
            FROM ExpressionSetVersion
            WHERE ExpressionSetId IN :setIds
            WITH USER_MODE
            GROUP BY ExpressionSetId
        ]) {
            Integer latestVersionNumber = Integer.valueOf(String.valueOf(ar.get('latestVersionNumber')));
            latestVersionNumberBySetId.put((Id) ar.get('setId'), latestVersionNumber);
            latestVersionNumbers.add(latestVersionNumber);
        }

        Map<Id, ExpressionSetVersion> latestVersionBySetId = new Map<Id, ExpressionSetVersion>();
        if (!latestVersionNumbers.isEmpty()) {
            for (ExpressionSetVersion v : [
                SELECT Id, ExpressionSetId, VersionNumber
                FROM ExpressionSetVersion
                WHERE ExpressionSetId IN :setIds
                AND VersionNumber IN :latestVersionNumbers
                WITH USER_MODE
            ]) {
                if (v.VersionNumber == latestVersionNumberBySetId.get(v.ExpressionSetId)) {
                    latestVersionBySetId.put(v.ExpressionSetId, v);
                }
            }
        }

        List<ExpressionSetInfo> results = new List<ExpressionSetInfo>();
        for (Id defId : allDefIds) {
            ExpressionSetDefinition def = defs.get(defId);
            if (def == null) continue;

            ExpressionSet es = setByDefId.get(defId);
            // Skip definitions with no runtime ExpressionSet. They are not
            // actionable: there is no version to toggle, the row would render an
            // /ExpressionSet/null/view link, and activating one enqueues a job
            // that emits no version PATCH — so getActivateStatus would never reach
            // 'complete' and the LWC would poll to the domain timeout.
            if (es == null) continue;

            Id setId = es.Id;
            ExpressionSetVersion latestVersion = latestVersionBySetId.get(setId);
            Boolean hasActive = hasActiveBySetId.containsKey(setId);

            results.add(new ExpressionSetInfo(
                def,
                setId,
                es.UsageType,
                latestVersion,
                hasActive,
                linkedDefIds.contains(defId)
            ));
        }
        return results;
    }

    @AuraEnabled
    public static JobStatus getJobStatus(Id jobId) {
        if (jobId == null) {
            return new JobStatus('unknown', 'Missing job id.');
        }

        // Intentionally system-mode: AsyncApexJob is a system object whose read
        // access cannot be granted via permission-set objectPermissions, so
        // WITH USER_MODE cannot be satisfied by RLM_UtilitiesPermset. The query
        // is scoped to the CALLER's own jobs (CreatedById) for this controller's
        // ApexClass and a specific job id, so the system-mode exception does not
        // bypass record ownership, and returns only job status (no business data).
        Id currentUserId = UserInfo.getUserId();
        List<AsyncApexJob> jobs = [
            SELECT Id, Status, ExtendedStatus, NumberOfErrors
            FROM AsyncApexJob
            WHERE Id = :jobId
            AND CreatedById = :currentUserId
            AND ApexClass.Name = 'RLM_ExpressionSetManagerController'
            LIMIT 1
        ];
        if (jobs.isEmpty()) {
            return new JobStatus('unknown', 'Job was not found.');
        }

        AsyncApexJob job = jobs[0];
        if (RUNNING_JOB_STATUSES.contains(job.Status)) {
            return new JobStatus('running', null);
        }
        if (FAILED_JOB_STATUSES.contains(job.Status) || job.NumberOfErrors > 0) {
            String msg = job.ExtendedStatus != null ? job.ExtendedStatus : 'Operation failed.';
            return new JobStatus('failed', msg);
        }
        return new JobStatus('complete', null);
    }

    @AuraEnabled
    public static Id deactivateExpressionSets(Id contextDefinitionId, List<Id> definitionIds) {
        // ExpressionSetVersion is the only object actually mutated via Apex SOQL/DML
        // before enqueuing — the junction object is mutated through Composite REST
        // (where the session-id user's permissions are enforced server-side), and
        // its describe returns false for createable/deletable on every profile.
        if (!ExpressionSetVersion.SObjectType.getDescribe().isUpdateable()
                || !ExpressionSetVersion.IsActive.getDescribe().isUpdateable()) {
            throw new AuraHandledException('Insufficient access to deactivate Expression Sets.');
        }
        List<Id> validatedDefinitionIds = validateDefinitionIds(contextDefinitionId, definitionIds, OPERATION_MAKE_INACTIVE);
        String sessionId = getApiSessionId();
        Set<Id> constraintDefIds = getConstraintDefIds(validatedDefinitionIds);
        return System.enqueueJob(new DeactivateQueueable(contextDefinitionId, validatedDefinitionIds, constraintDefIds, sessionId));
    }

    @AuraEnabled
    public static String getDeactivateStatus(Id contextDefinitionId, List<Id> definitionIds) {
        List<Id> normalizedDefinitionIds = normalizeDefinitionIds(definitionIds);
        Integer activeCount = countActiveVersions(normalizedDefinitionIds);
        if (activeCount > 0) return 'in_progress';

        Set<Id> constraintDefIds = getConstraintDefIds(normalizedDefinitionIds);
        if (!constraintDefIds.isEmpty()) {
            Integer remaining = [
                SELECT COUNT()
                FROM ExpressionSetDefinitionContextDefinition
                WHERE ContextDefinitionId = :contextDefinitionId
                AND ExpressionSetDefinitionId IN :constraintDefIds
                WITH USER_MODE
            ];
            if (remaining > 0) return 'in_progress';
        }

        return 'complete';
    }

    @AuraEnabled
    public static Id activateExpressionSets(Id contextDefinitionId, List<Id> definitionIds) {
        // See deactivateExpressionSets — junction is mutated via Composite REST,
        // not Apex DML, so we only guard the field we actually update from Apex.
        if (!ExpressionSetVersion.SObjectType.getDescribe().isUpdateable()
                || !ExpressionSetVersion.IsActive.getDescribe().isUpdateable()) {
            throw new AuraHandledException('Insufficient access to activate Expression Sets.');
        }
        List<Id> validatedDefinitionIds = validateDefinitionIds(contextDefinitionId, definitionIds, OPERATION_MAKE_ACTIVE);
        String sessionId = getApiSessionId();
        Set<Id> existingDefIds = new Set<Id>();
        for (ExpressionSetDefinitionContextDefinition j : [
            SELECT ExpressionSetDefinitionId
            FROM ExpressionSetDefinitionContextDefinition
            WHERE ContextDefinitionId = :contextDefinitionId
            AND ExpressionSetDefinitionId IN :validatedDefinitionIds
            WITH USER_MODE
        ]) {
            existingDefIds.add(j.ExpressionSetDefinitionId);
        }
        Set<Id> needsJunction = new Set<Id>();
        for (Id defId : validatedDefinitionIds) {
            if (!existingDefIds.contains(defId)) {
                needsJunction.add(defId);
            }
        }
        return System.enqueueJob(new ActivateQueueable(contextDefinitionId, validatedDefinitionIds, needsJunction, sessionId));
    }

    @AuraEnabled
    public static String getActivateStatus(Id contextDefinitionId, List<Id> definitionIds) {
        List<Id> normalizedDefinitionIds = normalizeDefinitionIds(definitionIds);
        Integer junctionCount = [
            SELECT COUNT()
            FROM ExpressionSetDefinitionContextDefinition
            WHERE ContextDefinitionId = :contextDefinitionId
            AND ExpressionSetDefinitionId IN :normalizedDefinitionIds
            WITH USER_MODE
        ];
        if (junctionCount < normalizedDefinitionIds.size()) return 'in_progress';

        Integer activeCount = countActiveVersions(normalizedDefinitionIds);
        return activeCount >= normalizedDefinitionIds.size() ? 'complete' : 'in_progress';
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

            List<ExpressionSetVersion> activeVersions = [
                SELECT Id FROM ExpressionSetVersion
                WHERE ExpressionSetId IN :setIds
                AND IsActive = true
                WITH USER_MODE
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
                    WITH USER_MODE
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

            Set<Id> setIds = getExpressionSetIds(definitionIds);

            // Sets that already have an active version only need their junction
            // created (an unlinked Constraint linked to another context is
            // submitted for link-only). Do NOT activate one of their inactive
            // versions — that would promote an inactive draft (or fail against the
            // already-active version).
            Set<Id> setsWithActiveVersion = new Set<Id>();
            for (AggregateResult ar : [
                SELECT ExpressionSetId setId
                FROM ExpressionSetVersion
                WHERE ExpressionSetId IN :setIds
                AND IsActive = true
                WITH USER_MODE
                GROUP BY ExpressionSetId
            ]) {
                setsWithActiveVersion.add((Id) ar.get('setId'));
            }

            List<ExpressionSetVersion> allVersions = [
                SELECT Id, ExpressionSetId, VersionNumber, Rank
                FROM ExpressionSetVersion
                WHERE ExpressionSetId IN :setIds
                AND IsActive = false
                WITH USER_MODE
                ORDER BY ExpressionSetId, VersionNumber DESC
            ];

            Set<Id> activated = new Set<Id>();
            for (ExpressionSetVersion v : allVersions) {
                if (!setsWithActiveVersion.contains(v.ExpressionSetId)
                        && !activated.contains(v.ExpressionSetId)) {
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

    private static List<Id> validateDefinitionIds(Id contextDefinitionId, List<Id> definitionIds, String operationMode) {
        if (contextDefinitionId == null) {
            throw new AuraHandledException('Select a Context Definition before managing Expression Sets.');
        }

        List<Id> normalizedDefinitionIds = normalizeDefinitionIds(definitionIds);
        Set<Id> allowedDefinitionIds = getAllowedDefinitionIds(contextDefinitionId, normalizedDefinitionIds, operationMode);
        assertRequestedIdsAllowed(normalizedDefinitionIds, allowedDefinitionIds, operationMode);
        return normalizedDefinitionIds;
    }

    @TestVisible
    private static List<Id> normalizeDefinitionIds(List<Id> definitionIds) {
        if (definitionIds == null || definitionIds.isEmpty()) {
            throw new AuraHandledException('Select at least one Expression Set.');
        }

        List<Id> normalizedDefinitionIds = new List<Id>();
        Set<Id> seen = new Set<Id>();
        for (Id definitionId : definitionIds) {
            if (definitionId == null) {
                throw new AuraHandledException('Expression Set selection contains an empty id.');
            }
            if (!seen.contains(definitionId)) {
                normalizedDefinitionIds.add(definitionId);
                seen.add(definitionId);
            }
        }
        return normalizedDefinitionIds;
    }

    private static Set<Id> getAllowedDefinitionIds(Id contextDefinitionId, List<Id> requestedDefinitionIds, String operationMode) {
        // Only definitions backed by a runtime ExpressionSet are actionable. A
        // linked definition without one has no version to toggle, so accepting it
        // would enqueue a job that does nothing while the status poll waits for an
        // active version that can never appear (getLinkedExpressionSets already
        // filters these out; this rejects a stale or hand-built request).
        Set<Id> definitionIdsWithSet = new Set<Id>();
        for (ExpressionSet backingSet : [
            SELECT ExpressionSetDefinitionId
            FROM ExpressionSet
            WHERE ExpressionSetDefinitionId IN :requestedDefinitionIds
            WITH USER_MODE
        ]) {
            definitionIdsWithSet.add(backingSet.ExpressionSetDefinitionId);
        }

        Set<Id> allowedDefinitionIds = new Set<Id>();
        for (ExpressionSetDefinitionContextDefinition junction : [
            SELECT ExpressionSetDefinitionId
            FROM ExpressionSetDefinitionContextDefinition
            WHERE ContextDefinitionId = :contextDefinitionId
            AND ExpressionSetDefinitionId IN :requestedDefinitionIds
            WITH USER_MODE
        ]) {
            if (definitionIdsWithSet.contains(junction.ExpressionSetDefinitionId)) {
                allowedDefinitionIds.add(junction.ExpressionSetDefinitionId);
            }
        }

        if (operationMode == OPERATION_MAKE_ACTIVE) {
            for (ExpressionSet expressionSet : [
                SELECT ExpressionSetDefinitionId
                FROM ExpressionSet
                WHERE UsageType = 'Constraint'
                AND ExpressionSetDefinitionId IN :requestedDefinitionIds
                WITH USER_MODE
            ]) {
                allowedDefinitionIds.add(expressionSet.ExpressionSetDefinitionId);
            }
        }
        return allowedDefinitionIds;
    }

    @TestVisible
    private static void assertRequestedIdsAllowed(List<Id> requestedDefinitionIds, Set<Id> allowedDefinitionIds, String operationMode) {
        for (Id definitionId : requestedDefinitionIds) {
            if (!allowedDefinitionIds.contains(definitionId)) {
                String action = operationMode == OPERATION_MAKE_ACTIVE ? 'activate' : 'deactivate';
                throw new AuraHandledException('You can only ' + action + ' Expression Sets available for the selected Context Definition.');
            }
        }
    }

    private static Set<Id> getConstraintDefIds(List<Id> definitionIds) {
        Set<Id> constraintDefIds = new Set<Id>();
        for (ExpressionSet es : [
            SELECT ExpressionSetDefinitionId FROM ExpressionSet
            WHERE ExpressionSetDefinitionId IN :definitionIds
            AND UsageType = 'Constraint'
            WITH USER_MODE
        ]) {
            constraintDefIds.add(es.ExpressionSetDefinitionId);
        }
        return constraintDefIds;
    }

    private static Set<Id> getExpressionSetIds(List<Id> definitionIds) {
        Set<Id> setIds = new Set<Id>();
        for (ExpressionSet es : [
            SELECT Id FROM ExpressionSet WHERE ExpressionSetDefinitionId IN :definitionIds WITH USER_MODE
        ]) {
            setIds.add(es.Id);
        }
        return setIds;
    }

    private static Integer countActiveVersions(List<Id> definitionIds) {
        Set<Id> setIds = getExpressionSetIds(definitionIds);
        // Count distinct sets that have at least one active version, not the raw
        // number of active versions: a set can carry multiple active versions
        // (Rank resolves overlaps), so COUNT() would let extra active versions on
        // one set mask another requested set that has none — making activation
        // look complete when it is not (getActivateStatus). >0 still means "any
        // active version remains" for getDeactivateStatus.
        AggregateResult ar = [
            SELECT COUNT_DISTINCT(ExpressionSetId) activeSets
            FROM ExpressionSetVersion
            WHERE ExpressionSetId IN :setIds
            AND IsActive = true
            WITH USER_MODE
        ];
        return (Integer) ar.get('activeSets');
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

    @TestVisible
    private static void deleteRecords(String baseUrl, String sessionId, List<String> recordIds) {
        for (Integer i = 0; i < recordIds.size(); i += 200) {
            Integer chunkEnd = Math.min(i + 200, recordIds.size());
            List<String> chunk = new List<String>();
            for (Integer j = i; j < chunkEnd; j++) {
                chunk.add(recordIds[j]);
            }
            HttpRequest req = new HttpRequest();
            // allOrNone=true: the sObject Collections API defaults it to FALSE, so
            // without it a single undeletable junction would leave the rest of the
            // batch deleted before assertNoCompositeDeleteFailures throws — a
            // partially applied operation.
            req.setEndpoint(baseUrl + '/services/data/' + API_VERSION
                + '/composite/sobjects?allOrNone=true&ids=' + String.join(chunk, ','));
            req.setMethod('DELETE');
            req.setHeader('Authorization', 'Bearer ' + sessionId);
            req.setTimeout(120000);

            Http http = new Http();
            HttpResponse res = http.send(req);
            if (res.getStatusCode() != 200) {
                System.debug(LoggingLevel.FINE, 'Composite delete HTTP ' + res.getStatusCode() + ' body: ' + res.getBody());
                String concise = conciseErrorFromBody(res.getBody());
                throw new CalloutException('Composite delete failed: HTTP ' + res.getStatusCode()
                    + (concise != null ? ' - ' + concise : ''));
            }
            assertNoCompositeDeleteFailures(res.getBody());
        }
    }

    @TestVisible
    private static void sendCompositeInChunks(String baseUrl, String sessionId, List<Object> subrequests) {
        Integer sentSoFar = 0;
        for (Integer i = 0; i < subrequests.size(); i += 25) {
            Integer chunkEnd = Math.min(i + 25, subrequests.size());
            List<Object> chunk = new List<Object>();
            for (Integer j = i; j < chunkEnd; j++) {
                chunk.add(subrequests[j]);
            }
            try {
                sendComposite(baseUrl, sessionId, chunk);
            } catch (Exception e) {
                // allOrNone=true rolls back only the composite request that
                // failed. Chunks already sent are committed, so past the first
                // chunk the operation is partially applied — say so instead of
                // implying the bulk action was atomic. Capping an operation at a
                // single transaction (or adding resume/compensation) is tracked
                // in issue #305.
                if (sentSoFar > 0) {
                    throw new CalloutException(
                        'Operation partially applied: ' + sentSoFar + ' of ' + subrequests.size()
                        + ' change(s) were already committed before this failure, and are not rolled back. '
                        + 'Refresh to see current state. ' + e.getMessage()
                    );
                }
                throw e;
            }
            sentSoFar = chunkEnd;
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
            System.debug(LoggingLevel.FINE, 'Composite HTTP ' + res.getStatusCode() + ' body: ' + res.getBody());
            String concise = conciseErrorFromBody(res.getBody());
            throw new CalloutException('Composite request failed: HTTP ' + res.getStatusCode()
                + (concise != null ? ' - ' + concise : ''));
        }

        assertNoCompositeSubrequestFailures(res.getBody());
    }

    @TestVisible
    private static void assertNoCompositeSubrequestFailures(String responseBody) {
        Map<String, Object> result = (Map<String, Object>) JSON.deserializeUntyped(responseBody);
        List<Object> results = (List<Object>) result.get('compositeResponse');
        List<String> failures = new List<String>();
        for (Object r : results) {
            Map<String, Object> subResult = (Map<String, Object>) r;
            Integer httpStatusCode = (Integer) subResult.get('httpStatusCode');
            if (httpStatusCode >= 400) {
                // Full detail server-side; concise Salesforce message to the user.
                System.debug(LoggingLevel.FINE, 'Composite subrequest failure: ' + JSON.serialize(subResult));
                String concise = conciseCompositeErrors((List<Object>) subResult.get('body'));
                failures.add(concise != null ? concise : ('HTTP ' + httpStatusCode));
            }
        }
        if (!failures.isEmpty()) {
            throw new CalloutException('Composite subrequest(s) failed: ' + String.join(failures, '; '));
        }
    }

    @TestVisible
    private static void assertNoCompositeDeleteFailures(String responseBody) {
        List<Object> results = (List<Object>) JSON.deserializeUntyped(responseBody);
        List<String> failures = new List<String>();
        for (Object r : results) {
            Map<String, Object> deleteResult = (Map<String, Object>) r;
            Boolean success = (Boolean) deleteResult.get('success');
            List<Object> errors = (List<Object>) deleteResult.get('errors');
            if (success != true || (errors != null && !errors.isEmpty())) {
                // Full detail server-side; concise Salesforce message to the user.
                System.debug(LoggingLevel.FINE, 'Composite delete failure: ' + JSON.serialize(deleteResult));
                String concise = conciseCompositeErrors(errors);
                failures.add(concise != null ? concise : 'delete failed');
            }
        }
        if (!failures.isEmpty()) {
            throw new CalloutException('Composite delete subrequest(s) failed: ' + String.join(failures, '; '));
        }
    }

    // Extracts the human-readable Salesforce message(s) from a list of REST error
    // entries (each a { "message": ..., "errorCode": ... } map), so the surfaced
    // exception — and the sticky LWC banner it reaches via AsyncApexJob
    // ExtendedStatus — shows a concise message instead of serialized JSON. Full
    // response detail is written to the debug log at each call site.
    @TestVisible
    private static String conciseCompositeErrors(List<Object> errors) {
        if (errors == null) return null;
        List<String> msgs = new List<String>();
        for (Object e : errors) {
            if (e instanceof Map<String, Object>) {
                Object m = ((Map<String, Object>) e).get('message');
                if (m != null) msgs.add(String.valueOf(m));
            }
        }
        return msgs.isEmpty() ? null : String.join(msgs, '; ');
    }

    // Best-effort concise message from a raw REST error body (transport-level
    // composite / composite-delete failures). Returns null on a shape it does not
    // recognise so the caller falls back to the HTTP status.
    @TestVisible
    private static String conciseErrorFromBody(String responseBody) {
        if (String.isBlank(responseBody)) return null;
        try {
            Object parsed = JSON.deserializeUntyped(responseBody);
            if (parsed instanceof List<Object>) {
                return conciseCompositeErrors((List<Object>) parsed);
            }
            if (parsed instanceof Map<String, Object>) {
                Map<String, Object> m = (Map<String, Object>) parsed;
                if (m.get('message') != null) return String.valueOf(m.get('message'));
                if (m.get('error_description') != null) return String.valueOf(m.get('error_description'));
            }
        } catch (Exception ignored) {
            // Non-JSON body (e.g. HTML) — fall back to the HTTP status.
        }
        return null;
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

    public class JobStatus {
        @AuraEnabled public String state;
        @AuraEnabled public String message;

        public JobStatus(String state, String message) {
            this.state = state;
            this.message = message;
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
        @AuraEnabled public Id latestVersionId;
        @AuraEnabled public Integer latestVersionNumber;
        @AuraEnabled public List<VersionInfo> versions;

        public ExpressionSetInfo(ExpressionSetDefinition def, Id esId, String usageType, ExpressionSetVersion latestVersion, Boolean hasActive, Boolean isLinked) {
            this.definitionId = def.Id;
            this.expressionSetId = esId;
            this.developerName = def.DeveloperName;
            this.label = def.MasterLabel;
            this.usageType = usageType;
            this.hasActiveVersion = hasActive;
            this.isLinked = isLinked;
            this.versions = new List<VersionInfo>();
            if (latestVersion != null) {
                this.latestVersionId = latestVersion.Id;
                this.latestVersionNumber = latestVersion.VersionNumber;
                this.versions.add(new VersionInfo(latestVersion));
            }
        }
    }

    public class VersionInfo {
        @AuraEnabled public Id versionId;
        @AuraEnabled public Integer versionNumber;

        public VersionInfo(ExpressionSetVersion v) {
            this.versionId = v.Id;
            this.versionNumber = v.VersionNumber;
        }
    }
}
