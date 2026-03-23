/**
 * @description Sets Ramp Mode, Discount, and Unit Price Uplift on Quote Line Item
 * from its Quote Line Group when the item is added to or moved between groups.
 */
trigger RLM_QuoteLineItemRampTrigger on QuoteLineItem (before insert, before update) {
    if (Trigger.isBefore && Trigger.isInsert) {
        RLM_QuoteLineItemRampModeHandler.onBeforeInsert(Trigger.new);
        RLM_QuoteLineItemDiscountUpliftHandler.onBeforeInsert(Trigger.new);
    }
    if (Trigger.isBefore && Trigger.isUpdate) {
        RLM_QuoteLineItemRampModeHandler.onBeforeUpdate(Trigger.new, Trigger.oldMap);
        RLM_QuoteLineItemDiscountUpliftHandler.onBeforeUpdate(Trigger.new, Trigger.oldMap);
    }
}
