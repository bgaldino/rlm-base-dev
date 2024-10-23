public interface IAppliedTermsDao {
    void upsertAppliedTerms(List<AppliedSpecialTerm__c> terms);
    void deleteTerms(List<AppliedSpecialTerm__c> terms);
    void updateAppliedTerms(List<AppliedSpecialTerm__c> terms, Boolean allOrNoneDML);
}