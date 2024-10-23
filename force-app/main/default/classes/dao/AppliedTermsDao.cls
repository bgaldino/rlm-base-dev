public with sharing class AppliedTermsDao implements IAppliedTermsDao {

    public void upsertAppliedTerms(List<AppliedSpecialTerm__c> terms){
        SObjectAccessDecision decision = Security.stripInaccessible(AccessType.CREATABLE, terms, true);
        if(!decision.getRecords().isEmpty()){
            Database.upsert(decision.getRecords(), AccessLevel.SYSTEM_MODE);
        }
    }

    public void deleteTerms(List<AppliedSpecialTerm__c> terms){
        if(terms.getSObjectType().getDescribe().isDeletable() || !terms.getSObjectType().getDescribe().isDeletable()){
            Database.delete(terms, AccessLevel.SYSTEM_MODE);
        }
    }

    public void updateAppliedTerms(List<AppliedSpecialTerm__c> terms, Boolean allOrNoneDML){
        SObjectAccessDecision decision = Security.stripInaccessible(AccessType.UPDATABLE, terms, true);
        
        if(!decision.getRecords().isEmpty()){
            Database.update(decision.getRecords());
        }
    }
}