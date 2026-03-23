/**
 * @description Copies RLM_RampMode__c from the parent QuoteLineGroup to the
 * QuoteLineItem when the item is inserted into or moved to a ramped group.
 *
 * Runs in the before context so values are stamped without a separate DML call.
 */
public without sharing class RLM_QuoteLineItemRampModeHandler {

    public static void onBeforeInsert(List<QuoteLineItem> newQLIs) {
        applyRampMode(newQLIs);
    }

    public static void onBeforeUpdate(List<QuoteLineItem> newQLIs, Map<Id, QuoteLineItem> oldMap) {
        List<QuoteLineItem> changed = new List<QuoteLineItem>();
        for (QuoteLineItem qli : newQLIs) {
            if (qli.QuoteLineGroupId != oldMap.get(qli.Id).QuoteLineGroupId) {
                changed.add(qli);
            }
        }
        if (!changed.isEmpty()) {
            applyRampMode(changed);
        }
    }

    private static void applyRampMode(List<QuoteLineItem> qlis) {
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
            SELECT Id, IsRamped, RLM_RampMode__c
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
            qli.RLM_RampMode__c = grp.RLM_RampMode__c;
        }
    }
}
