/**
 * @description Controller for the rlmPricingWaterfall LWC.
 *
 *              getAllPricingRuns(lineItemId) — returns the full history of
 *              PricingApiExecution runs for a QuoteLineItem by querying
 *              PricingProcessExecution records whose ExecutionTypeKey ends
 *              with '_{lineItemId}' and ExecutionType = 'Pricing_Line'.
 *
 * @see rlmPricingWaterfall LWC
 */
public with sharing class RLM_PricingWaterfallController {

    // ── getAllPricingRuns ─────────────────────────────────────────────────────

    /**
     * @description Represents one historical pricing run for a QuoteLineItem.
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
        /** PricingProcessExecution.Status for this specific QLI */
        @AuraEnabled public String lineStatus;
        /** PricingApiExecution.CreatedDate */
        @AuraEnabled public Datetime createdDate;
        /** Total number of lines priced in this API call */
        @AuraEnabled public Integer lineCount;
        /** Name of the user who triggered pricing */
        @AuraEnabled public String triggeredByName;
        /** QLI id that matched this execution row */
        @AuraEnabled public String matchedLineItemId;
        /** Why the run matched (SelectedLine or RelatedLine) */
        @AuraEnabled public String matchSource;
        /** Relationship role for matchedLineItemId (if known) */
        @AuraEnabled public String matchRelationshipRole;
        /** Raw execution token extracted from ExecutionTypeKey (suffix after first '_') */
        @AuraEnabled public String matchedExecutionToken;
    }

    /**
     * @description Returns all historical PricingApiExecution runs for the given
     *              QuoteLineItem Id, oldest first.
     *
     *              Strategy: query PricingProcessExecution WHERE ExecutionType =
     *              'Pricing_Line' AND ExecutionTypeKey LIKE '%_{lineItemId}'.
     *              The ExecutionTypeKey prefix (before '_' + lineItemId) is the
     *              waterfallRunId; the ExecutionKey links to PricingApiExecution.
     *
     * @param lineItemId  The 18-char Salesforce Id of the QuoteLineItem record
     * @return            List of PricingRun objects, oldest first
     */
    @AuraEnabled(cacheable=true)
    public static List<PricingRun> getAllPricingRuns(String lineItemId) {
        if (String.isBlank(lineItemId)) {
            throw new AuraHandledException('lineItemId is required');
        }

        // Expand lookup scope beyond the selected line so bundle/component runs
        // are discoverable in the same history panel.
        Map<String, String> lineRoleById = collectRelatedLineItemRoles((Id) lineItemId);
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
        Set<String> selectedAnchorExecutionKeys = new Set<String>();

        for (String scopedLineId : scopedLineItemIds) {
            scopedMatchTokens.add(scopedLineId);
            tokenToLineId.put(scopedLineId, scopedLineId);
            tokenToRole.put(scopedLineId, lineRoleById.get(scopedLineId));
        }

        for (QuoteLineItem qli : [
            SELECT Id, PriceWaterfallIdentifier
            FROM QuoteLineItem
            WHERE Id IN :scopedLineItemIds
        ]) {
            String token = extractTokenFromPriceWaterfallIdentifier(
                qli.PriceWaterfallIdentifier
            );
            if (String.isBlank(token)) continue;
            scopedMatchTokens.add(token);
            tokenToLineId.put(token, qli.Id);
            tokenToRole.put(
                token,
                lineRoleById.containsKey((String) qli.Id)
                    ? lineRoleById.get((String) qli.Id)
                    : null
            );

            if ((String) qli.Id == lineItemId) {
                selectedAnchorTokens.add(token);
            }
        }

        // First pass: anchor to runs that explicitly include the selected line/token.
        String anchorQuery =
            'SELECT ExecutionKey ' +
            'FROM PricingProcessExecution ' +
            'WHERE ExecutionType = \'Pricing_Line\' AND (' +
            buildExecutionTypeKeyClause(selectedAnchorTokens) +
            ')';
        for (PricingProcessExecution anchorPpe : (List<PricingProcessExecution>) Database.query(anchorQuery)) {
            selectedAnchorExecutionKeys.add(anchorPpe.ExecutionKey);
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
                'ORDER BY CreatedDate ASC';
        } else {
            // Fallback mode if no anchors were found.
            ppeQuery =
                'SELECT ExecutionKey, ExecutionTypeKey, Status, CreatedDate ' +
                'FROM PricingProcessExecution ' +
                'WHERE ExecutionType = \'Pricing_Line\' AND (' +
                buildExecutionTypeKeyClause(scopedMatchTokens) +
                ') ORDER BY CreatedDate ASC';
        }
        List<PricingProcessExecution> linePPEs =
            (List<PricingProcessExecution>) Database.query(ppeQuery);

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

        for (PricingProcessExecution ppe : linePPEs) {
            executionKeys.add(ppe.ExecutionKey);

            String matchedToken = extractMatchTokenFromExecutionTypeKey(
                ppe.ExecutionTypeKey
            );
            String matchedLineId = tokenToLineId.get(matchedToken);
            if (String.isBlank(matchedLineId) && scopedLineItemIds.contains(matchedToken)) {
                matchedLineId = matchedToken;
            }

            Boolean isSelectedLine = matchedLineId == lineItemId || matchedToken == lineItemId;
            String matchSource = isSelectedLine ? 'SelectedLine' : 'RelatedLine';
            String relationshipRole = tokenToRole.containsKey(matchedToken)
                ? tokenToRole.get(matchedToken)
                : null;
            if (relationshipRole == null && lineRoleById.containsKey(matchedLineId)) {
                relationshipRole = lineRoleById.get(matchedLineId);
            }

            // Prefer selected-line PPE when multiple scoped lines share same key.
            if (
                !keyToMatchedLineId.containsKey(ppe.ExecutionKey) ||
                (isSelectedLine && keyToMatchedLineId.get(ppe.ExecutionKey) != lineItemId)
            ) {
                keyToMatchedLineId.put(ppe.ExecutionKey, matchedLineId);
                keyToMatchSource.put(ppe.ExecutionKey, matchSource);
                keyToRelationshipRole.put(ppe.ExecutionKey, relationshipRole);
                keyToMatchedToken.put(ppe.ExecutionKey, matchedToken);
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

        // Fetch matching PricingApiExecution records (include CreatedById for user lookup)
        Map<String, PricingApiExecution> paeByExecutionKey = new Map<String, PricingApiExecution>();
        Set<Id> createdByIds = new Set<Id>();
        for (PricingApiExecution pae : [
            SELECT Id, Name, ExecutionKey, Status, CreatedDate, CreatedById
            FROM PricingApiExecution
            WHERE ExecutionKey IN :executionKeys
            ORDER BY CreatedDate ASC
        ]) {
            paeByExecutionKey.put(pae.ExecutionKey, pae);
            createdByIds.add(pae.CreatedById);
        }

        // Resolve user names
        Map<Id, String> userNames = new Map<Id, String>();
        for (User u : [SELECT Id, Name FROM User WHERE Id IN :createdByIds]) {
            userNames.put(u.Id, u.Name);
        }

        // Count total lines priced per ExecutionKey (reveals scope of each batch)
        Map<String, Integer> lineCountByKey = new Map<String, Integer>();
        for (AggregateResult ar : [
            SELECT ExecutionKey, COUNT(Id) cnt
            FROM PricingProcessExecution
            WHERE ExecutionType = 'Pricing_Line'
              AND ExecutionKey IN :executionKeys
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
            if (seen.contains(execKey)) continue; // deduplicate (multi-line quotes)
            seen.add(execKey);

            PricingRun run  = new PricingRun();
            run.waterfallRunId = keyToWaterfallRunId.get(execKey);
            run.lineStatus     = keyToLineStatus.get(execKey);
            run.lineCount      = lineCountByKey.get(execKey);
            run.matchedLineItemId = keyToMatchedLineId.get(execKey);
            run.matchSource = keyToMatchSource.get(execKey);
            run.matchRelationshipRole = keyToRelationshipRole.get(execKey);
            run.matchedExecutionToken = keyToMatchedToken.get(execKey);

            PricingApiExecution pae = paeByExecutionKey.get(execKey);
            if (pae != null) {
                run.pricingApiExecutionId = pae.Id;
                run.paeName               = pae.Name;
                run.overallStatus         = pae.Status;
                run.createdDate           = pae.CreatedDate;
                run.triggeredByName       = userNames.get(pae.CreatedById);
            }
            runs.add(run);
        }
        return runs;
    }

    /**
     * Collect selected line + one-hop/expanded related lines from QuoteLineRelationship.
     */
    @TestVisible
    private static Map<String, String> collectRelatedLineItemRoles(Id seedLineItemId) {
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

}
