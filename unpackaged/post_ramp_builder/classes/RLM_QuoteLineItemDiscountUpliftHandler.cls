/**
 * @description Copies Discount and RLM_UpliftPercent__c from the parent QuoteLineGroup
 * to the QuoteLineItem when the item is inserted into or moved to a ramped group.
 *
 * Discount segments  → QuoteLineItem.Discount      (0–100, clears UnitPriceUplift)
 * Uplift segments    → QuoteLineItem.UnitPriceUplift (0–100, clears Discount)
 * Discount takes precedence when both are non-zero on the group.
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

        // Query only ramped groups; non-ramped and null groups fall through to the clear path.
        Map<Id, QuoteLineGroup> groupMap = groupIds.isEmpty()
            ? new Map<Id, QuoteLineGroup>()
            : new Map<Id, QuoteLineGroup>([
                SELECT Id, IsRamped, Discount, RLM_UpliftPercent__c
                FROM QuoteLineGroup
                WHERE Id IN :groupIds
                  AND IsRamped = true
              ]);

        for (QuoteLineItem qli : qlis) {
            if (qli.QuoteLineGroupId == null) {
                // Removed from any group — clear both adjustments.
                qli.Discount        = 0;
                qli.UnitPriceUplift = 0;
                continue;
            }
            QuoteLineGroup grp = groupMap.get(qli.QuoteLineGroupId);
            if (grp == null) {
                // Moved to a non-ramped group — clear stale adjustments.
                qli.Discount        = 0;
                qli.UnitPriceUplift = 0;
                continue;
            }
            Boolean hasDiscount = grp.Discount != null && grp.Discount != 0;
            Boolean hasUplift   = grp.RLM_UpliftPercent__c != null && grp.RLM_UpliftPercent__c != 0;

            if (hasDiscount) {
                qli.Discount        = grp.Discount;
                qli.UnitPriceUplift = 0;
            } else if (hasUplift) {
                qli.Discount        = 0;
                qli.UnitPriceUplift = grp.RLM_UpliftPercent__c;
            } else {
                // Ramped group with no adjustment configured — clear both.
                qli.Discount        = 0;
                qli.UnitPriceUplift = 0;
            }
        }
    }

    /**
     * @description Returns the discount value for a discount segment, or null.
     * Uplift is applied via UnitPriceUplift (not as a negative Discount), so
     * this method returns null for uplift-only groups.
     */
    @TestVisible
    public static Decimal resolveAdjustment(Decimal discount, Decimal uplift) {
        if (discount != null && discount != 0) {
            return discount;
        }
        return null;
    }
}
