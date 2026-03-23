/**
 * @description Retained for backward compatibility. Logic has been split into
 * RLM_QuoteLineItemRampModeHandler and RLM_QuoteLineItemDiscountUpliftHandler,
 * which are called directly from RLM_QuoteLineItemRampTrigger (before insert/update).
 *
 * @deprecated Use RLM_QuoteLineItemRampModeHandler and
 *             RLM_QuoteLineItemDiscountUpliftHandler instead.
 */
public without sharing class RLM_QuoteLineItemRampHandler {

    public static void applyGroupAdjustments(List<QuoteLineItem> newQLIs) {
        RLM_QuoteLineItemRampModeHandler.onBeforeInsert(newQLIs);
        RLM_QuoteLineItemDiscountUpliftHandler.onBeforeInsert(newQLIs);
    }

    @TestVisible
    static Decimal resolveAdjustment(Decimal discount, Decimal uplift) {
        return RLM_QuoteLineItemDiscountUpliftHandler.resolveAdjustment(discount, uplift);
    }
}
