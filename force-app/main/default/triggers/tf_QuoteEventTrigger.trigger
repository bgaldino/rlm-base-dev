trigger tf_QuoteEventTrigger on QuoteChangeEvent (after insert) {
    new tf_TriggerDispatcher().execute();
}