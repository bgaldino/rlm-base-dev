public with sharing class QuoteEventTriggerHandler extends tf_TriggerHandler{
    
    public override void handleAfterInsert(){
        //calling method to find unique AppliedSpecialTerms and update it, also updating quotes as well
        EvaluateUniqueTermGateway evaluateUniqueTermGateway = new EvaluateUniqueTermGateway();
        evaluateUniqueTermGateway.findUniqueAppliedTerms(trigger.new);
    }
}