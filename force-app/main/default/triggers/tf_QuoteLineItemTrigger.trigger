trigger tf_QuoteLineItemTrigger on QuoteLineItem (before insert, before update, after insert, before delete, after delete, after update) {
    new tf_TriggerDispatcher().execute();
}