@isTest
private class RLM_BSGTimelineControllerTest {

    private static String fakeBsgId() {
        return Id.valueOf(BillingScheduleGroup.SObjectType.getDescribe().getKeyPrefix() + '000000000000');
    }

    // BillingScheduleGroup records are system-managed and not insertable in Apex tests.
    // getBillingScheduleGroupData / getConsolidatedTimeline raise AuraHandledException when the
    // BSG cannot be found; getMilestoneChartData degrades to an empty list.
    @isTest
    static void getBillingScheduleGroupData_unknownBsg_throws() {
        Boolean threw = false;
        Test.startTest();
        try {
            RLM_BSGTimelineController.getBillingScheduleGroupData(fakeBsgId());
        } catch (AuraHandledException e) {
            threw = true;
        }
        Test.stopTest();
        System.assert(threw, 'A non-existent BSG should raise an AuraHandledException.');
    }

    @isTest
    static void getConsolidatedTimeline_unknownBsg_throws() {
        Boolean threw = false;
        Test.startTest();
        try {
            RLM_BSGTimelineController.getConsolidatedTimeline(fakeBsgId());
        } catch (AuraHandledException e) {
            threw = true;
        }
        Test.stopTest();
        System.assert(threw, 'A non-existent BSG should raise an AuraHandledException for the timeline.');
    }

    @isTest
    static void getMilestoneChartData_unknownBsg_returnsEmptyList() {
        Test.startTest();
        List<RLM_BSGTimelineController.MilestoneChartItem> items =
            RLM_BSGTimelineController.getMilestoneChartData(fakeBsgId());
        Test.stopTest();
        System.assertNotEquals(null, items, 'A non-null list should always be returned.');
        System.assertEquals(0, items.size(), 'No milestones exist for a non-existent BSG.');
    }
}
