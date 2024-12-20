public with sharing class QuoteStatusASTUpdate {
    
    @TestVisible
    private IAppliedTermsDao appliedTermsDao;
   
    @TestVisible
    private IAppliedTermsDao getDaoInstance(){
        this.appliedTermsDao = (IAppliedTermsDao) new AppliedTermsDao();
        return this.appliedTermsDao;
    }

    @TestVisible
    private static ProductTermsSelector selector = new ProductTermsSelector();

    /**l
     * updates the PreviousTermText__c field in the AppliedSpeciaTerm__c object when a quote is rejected.
     */
    public void updatePreviousTermText(List<Quote> quoteList, Map<Id,Quote> oldMapQuotes){
        List<Id> rejectedQuotes = new List<Id>();

        try{
            for(Quote q : quoteList) {
                Quote oldQuote = oldMapQuotes.get(q.Id);
                //check if status was updated to Rejected
                if(q.Status == QuoteBaseConstants.REJECTED_STATUS && oldQuote.Status == QuoteBaseConstants.QUOTE_STATUS_IN_REVIEW){
                    //add the quoteId to rejectedQuotes list
                    rejectedQuotes.add(q.Id);
                }  
            }
            if(!rejectedQuotes.isEmpty()){
                this.getDaoInstance();
                //get applied terms to be updated
                List<AppliedSpecialTerm__c> appliedSpecialTerms = selector.selectAppliedTermsByQuote(rejectedQuotes);
                if(appliedSpecialTerms != null && !appliedSpecialTerms.isEmpty()){
                    for(AppliedSpecialTerm__c aST: appliedSpecialTerms){
                        aST.PreviousTermText__c = aST.TermText__c;
                    }
                    this.appliedTermsDao.upsertAppliedTerms(appliedSpecialTerms);
                }            
            }
        
        }catch(Exception e){
            throw new QuoteStatusASTException(e.getMessage());
        }
    }

    public class QuoteStatusASTException extends Exception{}

}
