/**
 * @description AuraEnabled controller for polling ramp schedule creation progress.
 *
 * Two-phase polling model:
 *   Phase 1 — job poll:  AsyncApexJob.Status → Completed / Failed / Aborted
 *   Phase 2 — quote poll: Quote.CalculationStatus → CompletedWithTax
 *                          Quote.ValidationResult shows 'Transaction Incomplete' while
 *                          awaiting repricing, then clears once repricing finishes.
 */
public with sharing class RLM_RampScheduleStatusController {

    /**
     * @description Poll the AsyncApexJob status for the background migration queueable.
     * Returns a simple map so the LWC doesn't need a typed wrapper.
     *
     * Possible Status values: Queued, Preparing, Processing, Completed, Failed, Aborted
     */
    @AuraEnabled(cacheable=false)
    public static Map<String, String> getJobStatus(String jobId) {
        if (String.isBlank(jobId)) {
            return new Map<String, String>{ 'status' => 'Unknown', 'extendedStatus' => '' };
        }
        try {
            AsyncApexJob job = [
                SELECT Id, Status, ExtendedStatus
                FROM AsyncApexJob
                WHERE Id = :jobId
                LIMIT 1
            ];
            return new Map<String, String>{
                'status'         => job.Status,
                'extendedStatus' => String.isNotBlank(job.ExtendedStatus) ? job.ExtendedStatus : ''
            };
        } catch (Exception e) {
            return new Map<String, String>{ 'status' => 'Unknown', 'extendedStatus' => e.getMessage() };
        }
    }

    /**
     * @description Poll the Quote's CalculationStatus and ValidationResult.
     *
     * Key values to watch:
     *   CalculationStatus = 'CompletedWithTax'  → pricing engine finished
     *   ValidationResult  = 'Transaction Incomplete' → structural change pending reprice
     *   ValidationResult  = 'Success' (or blank)    → quote is fully priced and valid
     */
    @AuraEnabled(cacheable=false)
    public static Map<String, String> getQuoteStatus(String quoteId) {
        if (String.isBlank(quoteId)) {
            return new Map<String, String>{ 'calculationStatus' => '', 'validationResult' => '' };
        }
        try {
            Quote q = [
                SELECT CalculationStatus, ValidationResult
                FROM Quote
                WHERE Id = :quoteId
                LIMIT 1
            ];
            return new Map<String, String>{
                'calculationStatus' => String.isNotBlank(q.CalculationStatus) ? q.CalculationStatus : '',
                'validationResult'  => String.isNotBlank(q.ValidationResult)  ? q.ValidationResult  : ''
            };
        } catch (Exception e) {
            return new Map<String, String>{ 'calculationStatus' => '', 'validationResult' => '' };
        }
    }
}
