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

        // Find every Pricing_Line PPE for this QLI across all historical runs
        String likePattern = '%_' + lineItemId;
        List<PricingProcessExecution> linePPEs = [
            SELECT ExecutionKey, ExecutionTypeKey, Status
            FROM PricingProcessExecution
            WHERE ExecutionType = 'Pricing_Line'
              AND ExecutionTypeKey LIKE :likePattern
            ORDER BY CreatedDate ASC
        ];

        if (linePPEs.isEmpty()) {
            return new List<PricingRun>();
        }

        // Build a set of ExecutionKeys and extract waterfallRunId per ExecutionKey
        Set<String> executionKeys = new Set<String>();
        Map<String, String> keyToWaterfallRunId = new Map<String, String>();
        Map<String, String> keyToLineStatus    = new Map<String, String>();
        String suffix = '_' + lineItemId;

        for (PricingProcessExecution ppe : linePPEs) {
            executionKeys.add(ppe.ExecutionKey);
            if (!keyToWaterfallRunId.containsKey(ppe.ExecutionKey)) {
                // ExecutionTypeKey = '{waterfallRunId}_{lineItemId}'
                keyToWaterfallRunId.put(
                    ppe.ExecutionKey,
                    ppe.ExecutionTypeKey.removeEnd(suffix)
                );
                keyToLineStatus.put(ppe.ExecutionKey, ppe.Status);
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

}
