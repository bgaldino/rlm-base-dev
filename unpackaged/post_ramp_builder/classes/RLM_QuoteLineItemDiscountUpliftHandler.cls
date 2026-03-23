/**
 * @description Copies Discount and RLM_UpliftPercent__c from the parent QuoteLineGroup
 * to the QuoteLineItem when the item is inserted into or moved to a ramped group.
 *
 * Discount takes precedence over Uplift when both are non-zero on the group.
 * Uplift is expressed as a negative Discount value (e.g. 5% uplift → Discount = -5).
 *
 * Runs in the before context so values are stamped without a separate DML call.
 */
public without sharing class RLM_QuoteLineItemDiscountUpliftHandler {

    public static void onBeforeInsert(List<QuoteLineItem> newQLIs) {
        applyAdjustments(newQLIs);
    }

    public static void onBeforeUpdate(List<QuoteLineItem> newQLIs, Map<Id, QuoteLineItem> oldMap) {
        List<QuoteLineItem> changed = new List<QuoteLineItem>();
        for (QuoteLineItem qli : newQLIs) {
            if (qli.QuoteLineGroupId != oldMap.get(qli.Id).QuoteLineGroupId) {
                changed.add(qli);
            }
        }
        if (!changed.isEmpty()) {
            applyAdjustments(changed);
        }
    }

    private static void applyAdjustments(List<QuoteLineItem> qlis) {
        Set<Id> groupIds = new Set<Id>();
        for (QuoteLineItem qli : qlis) {
            if (qli.QuoteLineGroupId != null) {
                groupIds.add(qli.QuoteLineGroupId);
            }
        }
        if (groupIds.isEmpty()) {
            return;
        }

        Map<Id, QuoteLineGroup> groupMap = new Map<Id, QuoteLineGroup>([
            SELECT Id, IsRamped, Discount, RLM_UpliftPercent__c
            FROM QuoteLineGroup
            WHERE Id IN :groupIds
              AND IsRamped = true
        ]);

        for (QuoteLineItem qli : qlis) {
            if (qli.QuoteLineGroupId == null) {
                continue;
            }
            QuoteLineGroup grp = groupMap.get(qli.QuoteLineGroupId);
            if (grp == null) {
                continue;
            }
            Decimal adjustment = resolveAdjustment(grp.Discount, grp.RLM_UpliftPercent__c);
            if (adjustment != null) {
                qli.Discount = adjustment;
            }
        }
    }

    @TestVisible
    public static Decimal resolveAdjustment(Decimal discount, Decimal uplift) {
        if (discount != null && discount != 0) {
            return discount;
        }
        if (uplift != null && uplift != 0) {
            return -uplift;
        }
        return null;
    }
}
