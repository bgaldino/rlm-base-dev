/**
 * When a BillingScheduleGroup is generated for a software asset that is currently
 * on billing hold (RLM_Asset_Status__c = 'BillingHeld'), push its
 * NextBillingDateOverride to the hold sentinel so the real billing lever matches
 * the status gate. Delegates to RLM_AssetBillingHoldHandler.
 *
 * Fires on after insert AND after update: the billing engine frequently inserts
 * the group with a null ReferenceEntityId and only links it to the Asset in a
 * later update, so an insert-only trigger would see no asset to match and never
 * apply the hold (observed live). The after-update pass catches that moment. The
 * handler is idempotent (setGroupOverride skips a group already at the clamped
 * hold date), so our own override write re-firing after update terminates
 * immediately rather than recursing.
 */
trigger RLM_BillingScheduleGroupHold on BillingScheduleGroup (after insert, after update) {
    RLM_AssetBillingHoldHandler.applyHoldToNewGroups(Trigger.new);
}
