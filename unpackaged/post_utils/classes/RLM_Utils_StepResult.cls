public class RLM_Utils_StepResult {
    @AuraEnabled public String stepName;
    @AuraEnabled public String status;
    @AuraEnabled public Integer deletedCount;
    @AuraEnabled public Integer skippedCount;
    @AuraEnabled public List<String> errors;
    @AuraEnabled public String details;

    public RLM_Utils_StepResult(String stepName) {
        this.stepName = stepName;
        this.status = 'success';
        this.deletedCount = 0;
        this.skippedCount = 0;
        this.errors = new List<String>();
        this.details = '';
    }

    public static RLM_Utils_StepResult success(String stepName, String details) {
        RLM_Utils_StepResult r = new RLM_Utils_StepResult(stepName);
        r.details = details;
        return r;
    }

    public static RLM_Utils_StepResult skipped(String stepName, String details) {
        RLM_Utils_StepResult r = new RLM_Utils_StepResult(stepName);
        r.status = 'skipped';
        r.details = details;
        return r;
    }

    public static RLM_Utils_StepResult failure(String stepName, Exception e) {
        RLM_Utils_StepResult r = new RLM_Utils_StepResult(stepName);
        r.status = 'error';
        r.errors.add(e.getMessage());
        r.details = 'Failed with exception.';
        return r;
    }
}
