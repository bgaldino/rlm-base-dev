/**
 * @description Controller for the rlmPricingApiExecutionList LWC.
 *
 *              getAllPricingRuns(lineItemId) — returns the full history of
 *              PricingApiExecution runs for a sales transaction line item by querying
 *              PricingProcessExecution records whose ExecutionTypeKey ends
 *              with '_{lineItemId}' and ExecutionType = 'Pricing_Line'.
 *
 * @see rlmPricingApiExecutionList LWC
 */
public with sharing class RLM_PricingApiExecutionListController {
    // Allow near-simultaneous execution records that can predate line insert by a few seconds.
    private static final Integer RUN_MATCH_TOLERANCE_SECONDS = 5;
    // For generic tokens (QLI0_0__*, OLI0_0__*), only consider a tight creation-time window.
    private static final Integer GENERIC_TOKEN_WINDOW_SECONDS = 120;

    // ── getAllPricingRuns ─────────────────────────────────────────────────────

    /**
     * @description Represents one historical pricing run for a sales transaction line.
     */
    public class PricingRun {
        /** Numeric run identifier (prefix of Pricing_Line.ExecutionTypeKey) */
        @AuraEnabled public String waterfallRunId;
        /** PricingApiExecution.Id — navigate to this for the full debug view */
        @AuraEnabled public String pricingApiExecutionId;
        /** PricingApiExecution.Name (auto-number) */
        @AuraEnabled public String paeName;
        /** PricingApiExecution.Status (overall batch status across all lines) */
        @AuraEnabled public String overallStatus;
        /** PricingProcessExecution.Status for this specific line */
        @AuraEnabled public String lineStatus;
        /** PricingApiExecution.CreatedDate */
        @AuraEnabled public Datetime createdDate;
        /** Total number of lines priced in this API call */
        @AuraEnabled public Integer lineCount;
        /** QuoteLineItem/OrderItem id that matched this execution row */
        @AuraEnabled public String matchedLineItemId;
        /** Why the run matched (SelectedLine or RelatedLine) */
        @AuraEnabled public String matchSource;
        /** Relationship role for matchedLineItemId (if known) */
        @AuraEnabled public String matchRelationshipRole;
        /** Raw execution token extracted from ExecutionTypeKey (suffix after first '_') */
        @AuraEnabled public String matchedExecutionToken;
        /** High-level source type for the matched token/id (Quote vs Order lineage) */
        @AuraEnabled public String matchedRecordType;
        /** Confidence score (0-100) for why this run matched */
        @AuraEnabled public Integer matchConfidenceScore;
        /** Confidence band label (Very High, High, Medium, Low) */
        @AuraEnabled public String matchConfidenceBand;
        /** Human-readable reason for the chosen match confidence */
        @AuraEnabled public String matchConfidenceReason;
    }

    private class MatchAssessment {
        public Integer score;
        public String band;
        public String reason;
        public Boolean isSelectedLine;
    }

    /**
     * @description Returns all historical PricingApiExecution runs for the given
     *              QuoteLineItem or OrderItem Id, oldest first.
     *
     *              Strategy: query PricingProcessExecution WHERE ExecutionType =
     *              'Pricing_Line' AND ExecutionTypeKey LIKE '%_{lineItemId}'.
     *              The ExecutionTypeKey prefix (before '_' + lineItemId) is the
     *              waterfallRunId; the ExecutionKey links to PricingApiExecution.
     *
     * @param lineItemId  The 18-char Salesforce Id of the QuoteLineItem/OrderItem record
     * @return            List of PricingRun objects, oldest first
     */
    @AuraEnabled(cacheable=true)
    public static List<PricingRun> getAllPricingRuns(String lineItemId) {
        if (String.isBlank(lineItemId)) {
            throw new AuraHandledException('lineItemId is required');
        }

        Id seedLineItemId = (Id) lineItemId;
        Schema.SObjectType lineItemType = seedLineItemId.getSObjectType();
        Boolean isQuoteLineItemType = lineItemType == QuoteLineItem.SObjectType;
        Boolean isOrderItemType = lineItemType == OrderItem.SObjectType;
        if (!isQuoteLineItemType && !isOrderItemType) {
            throw new AuraHandledException(
                'Unsupported record type. Expected QuoteLineItem or OrderItem.'
            );
        }

        // Expand lookup scope beyond the selected line so bundle/component runs
        // are discoverable in the same history panel.
        Map<String, String> lineRoleById = collectRelatedLineItemRoles(
            seedLineItemId,
            lineItemType
        );
        Set<String> scopedLineItemIds = new Set<String>();
        for (String scopedId : lineRoleById.keySet()) {
            scopedLineItemIds.add(scopedId);
        }
        if (scopedLineItemIds.isEmpty()) {
            scopedLineItemIds.add(lineItemId);
            lineRoleById.put(lineItemId, 'SelectedLine');
        }

        // Include both line Id tokens and identifier-prefix tokens (ref_...) because
        // bundle/component executions may persist non-QLI keys in ExecutionTypeKey.
        Set<String> scopedMatchTokens = new Set<String>();
        Map<String, String> tokenToLineId = new Map<String, String>();
        Map<String, String> tokenToRole = new Map<String, String>();
        Set<String> selectedAnchorTokens = new Set<String>{ lineItemId };
        Set<String> selectedAnchorRunIds = new Set<String>();
        Set<String> selectedAnchorExecutionKeys = new Set<String>();
        String selectedIdentifierToken;
        Boolean selectedIdentifierIsGeneric = false;
        Set<String> relatedIdentifierTokens = new Set<String>();
        Datetime seedLineCreatedDate;
        Datetime seedLineCreatedDateFloor;
        Datetime seedLineCreatedDateCeiling;

        for (String scopedLineId : scopedLineItemIds) {
            scopedMatchTokens.add(scopedLineId);
            tokenToLineId.put(scopedLineId, scopedLineId);
            tokenToRole.put(scopedLineId, lineRoleById.get(scopedLineId));
        }

        String lineObjectName = isQuoteLineItemType ? 'QuoteLineItem' : 'OrderItem';
        String identifierQuery =
            'SELECT Id, PriceWaterfallIdentifier, CreatedDate ' +
            'FROM ' + lineObjectName + ' ' +
            'WHERE Id IN :scopedLineItemIds';
        for (SObject rec : Database.query(identifierQuery, AccessLevel.USER_MODE)) {
            String recId = (String) rec.get('Id');
            String identifier = (String) rec.get('PriceWaterfallIdentifier');
            Datetime recCreatedDate = (Datetime) rec.get('CreatedDate');

            String token = extractTokenFromPriceWaterfallIdentifier(identifier);
            String runIdFromIdentifier = extractRunIdFromPriceWaterfallIdentifier(identifier);

            if (!String.isBlank(token)) {
                tokenToLineId.put(token, recId);
                tokenToRole.put(
                    token,
                    lineRoleById.containsKey(recId)
                        ? lineRoleById.get(recId)
                        : null
                );
            }

            if (recId == lineItemId) {
                seedLineCreatedDate = recCreatedDate;
                selectedIdentifierToken = token;
                selectedIdentifierIsGeneric = isGenericIdentifierToken(token);
                if (!String.isBlank(runIdFromIdentifier)) {
                    selectedAnchorRunIds.add(runIdFromIdentifier);
                }
                if (!String.isBlank(token) && !selectedIdentifierIsGeneric) {
                    scopedMatchTokens.add(token);
                    selectedAnchorTokens.add(token);
                }
            } else if (!String.isBlank(token) && !isGenericIdentifierToken(token)) {
                scopedMatchTokens.add(token);
                relatedIdentifierTokens.add(token);
            }
        }

        // First pass: anchor to runs that explicitly include the selected line/token.
        List<String> anchorClauses = new List<String>();
        if (!selectedAnchorTokens.isEmpty()) {
            anchorClauses.add('(' + buildExecutionTypeKeyClause(selectedAnchorTokens) + ')');
        }
        if (!selectedAnchorRunIds.isEmpty()) {
            anchorClauses.add('(' + buildWaterfallRunClause(selectedAnchorRunIds) + ')');
        }
        if (anchorClauses.isEmpty()) {
            return new List<PricingRun>();
        }
        if (seedLineCreatedDate != null) {
            seedLineCreatedDateFloor = seedLineCreatedDate.addSeconds(-RUN_MATCH_TOLERANCE_SECONDS);
            seedLineCreatedDateCeiling = seedLineCreatedDate.addSeconds(GENERIC_TOKEN_WINDOW_SECONDS);
        }
        String minCreatedFilter = seedLineCreatedDate == null
            ? ''
            : ' AND CreatedDate >= :seedLineCreatedDateFloor';
        String genericWindowUpperFilter = seedLineCreatedDate == null
            ? ''
            : ' AND CreatedDate <= :seedLineCreatedDateCeiling';
        String anchorQuery =
            'SELECT ExecutionKey ' +
            'FROM PricingProcessExecution ' +
            'WHERE ExecutionType = \'Pricing_Line\' AND (' +
            String.join(anchorClauses, ' OR ') +
            ')' +
            minCreatedFilter;
        for (PricingProcessExecution anchorPpe : (List<PricingProcessExecution>) Database.query(anchorQuery, AccessLevel.USER_MODE)) {
            selectedAnchorExecutionKeys.add(anchorPpe.ExecutionKey);
        }

        // Generic token fallback: include nearby runs in the same creation-time window.
        // This recovers adjacent calls (e.g. paired pricing runs) without pulling old history.
        if (
            selectedIdentifierIsGeneric &&
            !String.isBlank(selectedIdentifierToken) &&
            seedLineCreatedDate != null
        ) {
            String genericTokenAnchorQuery =
                'SELECT ExecutionKey ' +
                'FROM PricingProcessExecution ' +
                'WHERE ExecutionType = \'Pricing_Line\' AND (' +
                buildExecutionTypeKeyClause(new Set<String>{ selectedIdentifierToken }) +
                ')' +
                minCreatedFilter +
                genericWindowUpperFilter;
            for (PricingProcessExecution genericPpe : (List<PricingProcessExecution>) Database.query(genericTokenAnchorQuery, AccessLevel.USER_MODE)) {
                selectedAnchorExecutionKeys.add(genericPpe.ExecutionKey);
            }
        }

        // Co-anchor tightening:
        // If selected identifier token is generic (e.g., QLI0_0__0), require
        // overlap with at least one related non-generic token (usually ref_...)
        // to avoid pulling unrelated historical executions.
        if (
            selectedIdentifierIsGeneric &&
            !relatedIdentifierTokens.isEmpty() &&
            !selectedAnchorExecutionKeys.isEmpty()
        ) {
            Set<String> relatedExecutionKeys = new Set<String>();
            String relatedQuery =
                'SELECT ExecutionKey ' +
                'FROM PricingProcessExecution ' +
                'WHERE ExecutionType = \'Pricing_Line\' AND (' +
                buildExecutionTypeKeyClause(relatedIdentifierTokens) +
                ')' +
                minCreatedFilter;
            for (PricingProcessExecution relatedPpe : (List<PricingProcessExecution>) Database.query(relatedQuery, AccessLevel.USER_MODE)) {
                relatedExecutionKeys.add(relatedPpe.ExecutionKey);
            }

            Set<String> coAnchoredExecutionKeys = new Set<String>();
            coAnchoredExecutionKeys.addAll(selectedAnchorExecutionKeys);
            coAnchoredExecutionKeys.retainAll(relatedExecutionKeys);

            // Only tighten when overlap exists; otherwise retain selected anchors.
            if (!coAnchoredExecutionKeys.isEmpty()) {
                selectedAnchorExecutionKeys = coAnchoredExecutionKeys;
            }
        }

        // Find every Pricing_Line PPE for selected + related tokens.
        String ppeQuery;
        if (!selectedAnchorExecutionKeys.isEmpty()) {
            // Strict mode: include related token matches only for selected-anchored runs.
            ppeQuery =
                'SELECT ExecutionKey, ExecutionTypeKey, Status, CreatedDate ' +
                'FROM PricingProcessExecution ' +
                'WHERE ExecutionType = \'Pricing_Line\' ' +
                'AND ExecutionKey IN :selectedAnchorExecutionKeys ' +
                minCreatedFilter +
                ' ORDER BY CreatedDate ASC';
        } else {
            // Fallback mode if no anchors were found.
            if (scopedMatchTokens.isEmpty()) {
                return new List<PricingRun>();
            }
            ppeQuery =
                'SELECT ExecutionKey, ExecutionTypeKey, Status, CreatedDate ' +
                'FROM PricingProcessExecution ' +
                'WHERE ExecutionType = \'Pricing_Line\' AND (' +
                buildExecutionTypeKeyClause(scopedMatchTokens) +
                ')' +
                minCreatedFilter +
                ' ORDER BY CreatedDate ASC';
        }
        List<PricingProcessExecution> linePPEs =
            (List<PricingProcessExecution>) Database.query(ppeQuery, AccessLevel.USER_MODE);

        if (linePPEs.isEmpty()) {
            return new List<PricingRun>();
        }

        // Build a set of ExecutionKeys and extract waterfallRunId per ExecutionKey
        Set<String> executionKeys = new Set<String>();
        Map<String, String> keyToWaterfallRunId = new Map<String, String>();
        Map<String, String> keyToLineStatus    = new Map<String, String>();
        Map<String, String> keyToMatchedLineId = new Map<String, String>();
        Map<String, String> keyToMatchSource = new Map<String, String>();
        Map<String, String> keyToRelationshipRole = new Map<String, String>();
        Map<String, String> keyToMatchedToken = new Map<String, String>();
        Map<String, String> keyToMatchedRecordType = new Map<String, String>();
        Map<String, Integer> keyToMatchConfidenceScore = new Map<String, Integer>();
        Map<String, String> keyToMatchConfidenceBand = new Map<String, String>();
        Map<String, String> keyToMatchConfidenceReason = new Map<String, String>();

        for (PricingProcessExecution ppe : linePPEs) {
            executionKeys.add(ppe.ExecutionKey);

            String matchedToken = extractMatchTokenFromExecutionTypeKey(
                ppe.ExecutionTypeKey
            );
            String matchedLineId = tokenToLineId.get(matchedToken);
            if (String.isBlank(matchedLineId) && scopedLineItemIds.contains(matchedToken)) {
                matchedLineId = matchedToken;
            }

            MatchAssessment assessment = evaluateMatchConfidence(
                lineItemId,
                selectedIdentifierToken,
                selectedAnchorRunIds,
                ppe.ExecutionTypeKey,
                matchedToken,
                matchedLineId
            );
            Boolean isSelectedLine = assessment.isSelectedLine;
            String matchSource = isSelectedLine ? 'SelectedLine' : 'RelatedLine';
            String relationshipRole = tokenToRole.containsKey(matchedToken)
                ? tokenToRole.get(matchedToken)
                : null;
            if (relationshipRole == null && lineRoleById.containsKey(matchedLineId)) {
                relationshipRole = lineRoleById.get(matchedLineId);
            }

            Integer existingScore = keyToMatchConfidenceScore.get(ppe.ExecutionKey);
            Boolean hasExisting = keyToMatchedLineId.containsKey(ppe.ExecutionKey);
            Boolean existingSelectedLine = keyToMatchSource.get(ppe.ExecutionKey) == 'SelectedLine';
            Boolean shouldReplace =
                !hasExisting ||
                assessment.score > existingScore ||
                (
                    assessment.score == existingScore &&
                    isSelectedLine &&
                    !existingSelectedLine
                );

            if (shouldReplace) {
                keyToMatchedLineId.put(ppe.ExecutionKey, matchedLineId);
                keyToMatchSource.put(ppe.ExecutionKey, matchSource);
                keyToRelationshipRole.put(ppe.ExecutionKey, relationshipRole);
                keyToMatchedToken.put(ppe.ExecutionKey, matchedToken);
                keyToMatchedRecordType.put(
                    ppe.ExecutionKey,
                    classifyMatchedRecordType(matchedToken, matchedLineId)
                );
                keyToMatchConfidenceScore.put(ppe.ExecutionKey, assessment.score);
                keyToMatchConfidenceBand.put(ppe.ExecutionKey, assessment.band);
                keyToMatchConfidenceReason.put(ppe.ExecutionKey, assessment.reason);
                keyToLineStatus.put(ppe.ExecutionKey, ppe.Status);
            }

            if (!keyToWaterfallRunId.containsKey(ppe.ExecutionKey)) {
                // ExecutionTypeKey = '{waterfallRunId}_{lineItemId}'
                keyToWaterfallRunId.put(
                    ppe.ExecutionKey,
                    removeTokenSuffix(ppe.ExecutionTypeKey, matchedToken)
                );
            }
        }

        // Fetch matching PricingApiExecution records
        Map<String, PricingApiExecution> paeByExecutionKey = new Map<String, PricingApiExecution>();
        for (PricingApiExecution pae : [
            SELECT Id, Name, ExecutionKey, Status, CreatedDate
            FROM PricingApiExecution
            WHERE ExecutionKey IN :executionKeys
            WITH USER_MODE
            ORDER BY CreatedDate ASC
        ]) {
            paeByExecutionKey.put(pae.ExecutionKey, pae);
        }

        // Count total lines priced per ExecutionKey (reveals scope of each batch)
        Map<String, Integer> lineCountByKey = new Map<String, Integer>();
        for (AggregateResult ar : [
            SELECT ExecutionKey, COUNT(Id) cnt
            FROM PricingProcessExecution
            WHERE ExecutionType = 'Pricing_Line'
              AND ExecutionKey IN :executionKeys
            WITH USER_MODE
            GROUP BY ExecutionKey
        ]) {
            lineCountByKey.put(
                (String) ar.get('ExecutionKey'),
                (Integer) ar.get('cnt')
            );
        }

        // Assemble result list in PPE order (already sorted ASC by CreatedDate)
        List<PricingRun> runs = new List<PricingRun>();
        Set<String> seen = new Set<String>();

        for (PricingProcessExecution ppe : linePPEs) {
            String execKey = ppe.ExecutionKey;
            if (seen.contains(execKey)) continue; // deduplicate (multi-line runs)
            seen.add(execKey);

            PricingRun run  = new PricingRun();
            run.waterfallRunId = keyToWaterfallRunId.get(execKey);
            run.lineStatus     = keyToLineStatus.get(execKey);
            run.lineCount      = lineCountByKey.get(execKey);
            run.matchedLineItemId = keyToMatchedLineId.get(execKey);
            run.matchSource = keyToMatchSource.get(execKey);
            run.matchRelationshipRole = keyToRelationshipRole.get(execKey);
            run.matchedExecutionToken = keyToMatchedToken.get(execKey);
            run.matchedRecordType = keyToMatchedRecordType.get(execKey);
            run.matchConfidenceScore = keyToMatchConfidenceScore.get(execKey);
            run.matchConfidenceBand = keyToMatchConfidenceBand.get(execKey);
            run.matchConfidenceReason = keyToMatchConfidenceReason.get(execKey);

            PricingApiExecution pae = paeByExecutionKey.get(execKey);
            if (pae != null) {
                run.pricingApiExecutionId = pae.Id;
                run.paeName               = pae.Name;
                run.overallStatus         = pae.Status;
                run.createdDate           = pae.CreatedDate;
            }
            runs.add(run);
        }
        return runs;
    }

    @TestVisible
    private static Map<String, String> collectRelatedLineItemRoles(
        Id seedLineItemId,
        Schema.SObjectType lineItemType
    ) {
        if (lineItemType == QuoteLineItem.SObjectType) {
            return collectRelatedQuoteLineItemRoles(seedLineItemId);
        }
        if (lineItemType == OrderItem.SObjectType) {
            return collectRelatedOrderLineItemRoles(seedLineItemId);
        }
        Map<String, String> roleByLineId = new Map<String, String>();
        roleByLineId.put((String) seedLineItemId, 'SelectedLine');
        return roleByLineId;
    }

    /**
     * Collect selected line + one-hop/expanded related lines from QuoteLineRelationship.
     */
    @TestVisible
    private static Map<String, String> collectRelatedQuoteLineItemRoles(Id seedLineItemId) {
        Map<String, String> roleByLineId = new Map<String, String>();
        roleByLineId.put((String) seedLineItemId, 'SelectedLine');

        Set<Id> frontier = new Set<Id>{ seedLineItemId };
        // Two passes: seed neighbors + a light expansion to catch siblings.
        for (Integer hop = 0; hop < 2; hop++) {
            if (frontier.isEmpty()) break;

            Set<Id> nextFrontier = new Set<Id>();
            for (QuoteLineRelationship rel : [
                SELECT MainQuoteLineId, AssociatedQuoteLineId, RootQuoteLineId
                FROM QuoteLineRelationship
                WHERE MainQuoteLineId IN :frontier
                   OR AssociatedQuoteLineId IN :frontier
                   OR RootQuoteLineId IN :frontier
                WITH USER_MODE
            ]) {
                addRole(roleByLineId, nextFrontier, rel.MainQuoteLineId, 'MainQuoteLine');
                addRole(
                    roleByLineId,
                    nextFrontier,
                    rel.AssociatedQuoteLineId,
                    'AssociatedQuoteLine'
                );
                addRole(roleByLineId, nextFrontier, rel.RootQuoteLineId, 'RootQuoteLine');
            }
            frontier = nextFrontier;
        }
        return roleByLineId;
    }

    /**
     * Collect selected line + one-hop/expanded related lines from OrderItemRelationship.
     */
    @TestVisible
    private static Map<String, String> collectRelatedOrderLineItemRoles(Id seedLineItemId) {
        Map<String, String> roleByLineId = new Map<String, String>();
        roleByLineId.put((String) seedLineItemId, 'SelectedLine');

        Set<Id> frontier = new Set<Id>{ seedLineItemId };
        // Two passes: seed neighbors + a light expansion to catch siblings.
        for (Integer hop = 0; hop < 2; hop++) {
            if (frontier.isEmpty()) break;

            Set<Id> nextFrontier = new Set<Id>();
            for (OrderItemRelationship rel : [
                SELECT
                    MainOrderItemId,
                    AssociatedOrderItemId,
                    RootOrderItemId,
                    MainOrderItemRole,
                    AssociatedOrderItemRole
                FROM OrderItemRelationship
                WHERE MainOrderItemId IN :frontier
                   OR AssociatedOrderItemId IN :frontier
                   OR RootOrderItemId IN :frontier
                WITH USER_MODE
            ]) {
                addRole(
                    roleByLineId,
                    nextFrontier,
                    rel.MainOrderItemId,
                    String.isBlank(rel.MainOrderItemRole)
                        ? 'MainOrderItem'
                        : rel.MainOrderItemRole
                );
                addRole(
                    roleByLineId,
                    nextFrontier,
                    rel.AssociatedOrderItemId,
                    String.isBlank(rel.AssociatedOrderItemRole)
                        ? 'AssociatedOrderItem'
                        : rel.AssociatedOrderItemRole
                );
                addRole(roleByLineId, nextFrontier, rel.RootOrderItemId, 'RootOrderItem');
            }
            frontier = nextFrontier;
        }
        return roleByLineId;
    }

    @TestVisible
    private static void addRole(
        Map<String, String> roleByLineId,
        Set<Id> nextFrontier,
        Id lineId,
        String role
    ) {
        if (lineId == null) return;
        String lineKey = (String) lineId;
        if (!roleByLineId.containsKey(lineKey)) {
            roleByLineId.put(lineKey, role);
            nextFrontier.add(lineId);
        }
    }

    @TestVisible
    private static String buildExecutionTypeKeyClause(Set<String> lineItemIds) {
        List<String> clauses = new List<String>();
        for (String lineId : lineItemIds) {
            clauses.add(
                'ExecutionTypeKey LIKE \'%_' +
                String.escapeSingleQuotes(lineId) +
                '\''
            );
        }
        return String.join(clauses, ' OR ');
    }

    @TestVisible
    private static String extractMatchTokenFromExecutionTypeKey(String executionTypeKey) {
        if (String.isBlank(executionTypeKey)) return null;
        Integer idx = executionTypeKey.indexOf('_');
        if (idx == -1 || idx + 1 >= executionTypeKey.length()) return null;
        return executionTypeKey.substring(idx + 1);
    }

    @TestVisible
    private static String removeTokenSuffix(String executionTypeKey, String token) {
        if (String.isBlank(executionTypeKey) || String.isBlank(token)) {
            return executionTypeKey;
        }
        String suffix = '_' + token;
        return executionTypeKey.endsWith(suffix)
            ? executionTypeKey.removeEnd(suffix)
            : executionTypeKey;
    }

    @TestVisible
    private static String extractTokenFromPriceWaterfallIdentifier(
        String priceWaterfallIdentifier
    ) {
        if (String.isBlank(priceWaterfallIdentifier)) return null;
        Integer idx = priceWaterfallIdentifier.indexOf(':');
        if (idx <= 0) return null;
        return priceWaterfallIdentifier.substring(0, idx);
    }

    @TestVisible
    private static String extractRunIdFromPriceWaterfallIdentifier(
        String priceWaterfallIdentifier
    ) {
        if (String.isBlank(priceWaterfallIdentifier)) return null;
        Integer idx = priceWaterfallIdentifier.indexOf(':');
        if (idx == -1 || idx + 1 >= priceWaterfallIdentifier.length()) return null;
        return priceWaterfallIdentifier.substring(idx + 1);
    }

    @TestVisible
    private static Boolean isGenericIdentifierToken(String token) {
        if (String.isBlank(token)) return false;
        return token.startsWithIgnoreCase('QLI') || token.startsWithIgnoreCase('OLI');
    }

    @TestVisible
    private static String buildWaterfallRunClause(Set<String> runIds) {
        List<String> clauses = new List<String>();
        for (String runId : runIds) {
            clauses.add(
                'ExecutionTypeKey LIKE \'' +
                String.escapeSingleQuotes(runId) +
                '_%\''
            );
        }
        return String.join(clauses, ' OR ');
    }

    @TestVisible
    private static MatchAssessment evaluateMatchConfidence(
        String selectedLineId,
        String selectedIdentifierToken,
        Set<String> selectedAnchorRunIds,
        String executionTypeKey,
        String matchedToken,
        String matchedLineId
    ) {
        MatchAssessment assessment = new MatchAssessment();
        assessment.isSelectedLine = matchedLineId == selectedLineId || matchedToken == selectedLineId;

        String runId = removeTokenSuffix(executionTypeKey, matchedToken);
        Boolean runIdMatch =
            !String.isBlank(runId) &&
            selectedAnchorRunIds != null &&
            selectedAnchorRunIds.contains(runId);
        Boolean tokenMatchSelectedIdentifier =
            !String.isBlank(selectedIdentifierToken) &&
            selectedIdentifierToken == matchedToken;
        Boolean nonGenericToken = !isGenericIdentifierToken(matchedToken);
        Boolean directLineIdSuffix = matchedToken == selectedLineId;

        assessment.score = 50;
        assessment.reason = 'Related context fallback';

        if (directLineIdSuffix) {
            assessment.score = 100;
            assessment.reason = 'Exact selected line ID suffix';
        } else if (assessment.isSelectedLine && tokenMatchSelectedIdentifier && nonGenericToken) {
            assessment.score = 98;
            assessment.reason = 'Exact non-generic identifier token';
        } else if (assessment.isSelectedLine && runIdMatch) {
            assessment.score = 92;
            assessment.reason = 'Identifier run ID matched execution prefix';
        } else if (assessment.isSelectedLine && tokenMatchSelectedIdentifier) {
            assessment.score = 85;
            assessment.reason = 'Generic selected identifier token within controlled window';
        } else if (assessment.isSelectedLine) {
            assessment.score = 80;
            assessment.reason = 'Selected line resolved through scoped mapping';
        } else if (runIdMatch && nonGenericToken) {
            assessment.score = 72;
            assessment.reason = 'Related non-generic token in same run';
        } else if (nonGenericToken) {
            assessment.score = 65;
            assessment.reason = 'Related non-generic token evidence';
        } else if (runIdMatch) {
            assessment.score = 60;
            assessment.reason = 'Related run-ID-only evidence';
        }

        if (assessment.score >= 95) {
            assessment.band = 'Very High';
        } else if (assessment.score >= 85) {
            assessment.band = 'High';
        } else if (assessment.score >= 70) {
            assessment.band = 'Medium';
        } else {
            assessment.band = 'Low';
        }

        return assessment;
    }

    @TestVisible
    private static String classifyMatchedRecordType(String matchedToken, String matchedLineId) {
        String tokenType = classifyRecordTypeFromIdLikeValue(matchedToken);
        if (!String.isBlank(tokenType)) return tokenType;
        return classifyRecordTypeFromIdLikeValue(matchedLineId);
    }

    @TestVisible
    private static String classifyRecordTypeFromIdLikeValue(String value) {
        if (String.isBlank(value)) return null;
        String normalized = value.trim().toUpperCase();
        if (normalized.startsWith('0QL')) return 'Quote/QuoteLineItem';
        if (normalized.startsWith('802')) return 'Order/OrderItem';
        return null;
    }

}
