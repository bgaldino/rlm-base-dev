trigger tf_QuoteTrigger on Quote(before insert, before update, after insert, after update) {
    new tf_TriggerDispatcher().execute();
}
