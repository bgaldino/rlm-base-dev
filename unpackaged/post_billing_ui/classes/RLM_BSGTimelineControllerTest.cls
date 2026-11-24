@isTest
private class RLM_BSGTimelineControllerTest {

    private static String fakeBsgId() {
        return Id.valueOf(BillingScheduleGroup.SObjectType.getDescribe().getKeyPrefix() + '000000000000');
    }

    // BillingScheduleGroup records are system-managed and not insertable in Apex tests.
    // getBillingScheduleGroupData / getConsolidatedTimeline raise AuraHandledException when the
    // BSG cannot be found; getMilestoneChartData degrades to an empty list. The admin-run
    // unknown-id tests reach "not found or refused" (indistinguishable when run as the admin).
    // The refused-access test runs as a plain Minimum Access user with no permission set
    // license (no Billing PSL seat); billing-role read coverage for the controller's fields is
    // in RLM_BillingUIAccessTest (billingOperationsCanRunItsControllerReads).
    //
    // Fixed: the not-found AuraHandledException is no longer rewrapped, and every
    // AuraHandledException built here calls setMessage, so the LWC receives
    // "Billing Schedule Group not found" (readable from Apex via getMessage).
    @isTest
    static void getBillingScheduleGroupData_unknownBsg_throws() {
        Boolean threw = false;
        String text;
        Test.startTest();
        try {
            RLM_BSGTimelineController.getBillingScheduleGroupData(fakeBsgId());
        } catch (AuraHandledException e) {
            threw = true;
            text = e.getMessage();
        }
        Test.stopTest();
        System.assert(threw, 'A non-existent BSG should raise an AuraHandledException.');
        System.assertEquals('Billing Schedule Group not found', text, 'The not-found text reaches the caller unwrapped.');
    }

    @isTest
    static void getConsolidatedTimeline_unknownBsg_throws() {
        Boolean threw = false;
        Test.startTest();
        try {
            RLM_BSGTimelineController.getConsolidatedTimeline(fakeBsgId());
        } catch (AuraHandledException e) {
            threw = true;
            Assert.areEqual('Billing Schedule Group not found', e.getMessage(),
                'The not-found sentence from the group read reaches the caller unwrapped');
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

    // ─── Malformed input ────────────────────────────────────────────────────

    // A string that is not an id: the two group reads must throw AuraHandledException (not a
    // raw platform exception) and the milestone read must return an empty list. Both failure
    // routes (an invalid or refused bind, and not-found) surface as AuraHandledException with
    // an unreadable message, so the test does not show which branch inside each method ran.
    @isTest
    static void malformedId_throwsHandledExceptionsAndReturnsNoMilestones() {
        Exception dataThrown;
        Exception timelineThrown;
        List<RLM_BSGTimelineController.MilestoneChartItem> items;

        Test.startTest();
        try {
            RLM_BSGTimelineController.getBillingScheduleGroupData('not-an-id');
        } catch (Exception e) {
            dataThrown = e;
        }
        try {
            RLM_BSGTimelineController.getConsolidatedTimeline('not-an-id');
        } catch (Exception e) {
            timelineThrown = e;
        }
        items = RLM_BSGTimelineController.getMilestoneChartData('not-an-id');
        Test.stopTest();

        Assert.isNotNull(dataThrown, 'A malformed id must raise an error.');
        Assert.isInstanceOfType(dataThrown, AuraHandledException.class,
            'A malformed id surfaces as an AuraHandledException, got ' + dataThrown.getTypeName());
        Assert.isNotNull(timelineThrown, 'A malformed id must raise an error from the timeline.');
        Assert.isInstanceOfType(timelineThrown, AuraHandledException.class,
            'The timeline surfaces a malformed id as an AuraHandledException, got ' + timelineThrown.getTypeName());
        Assert.isNotNull(items, 'Milestone data degrades to a list, never null.');
        Assert.isTrue(items.isEmpty(), 'A malformed id has no milestones.');
    }

    // ─── Access paths (USER_MODE) ───────────────────────────────────────────

    // A Minimum Access user with no permission sets cannot read BillingScheduleGroup, and
    // the milestone link on BillingSchedule is absent or unreadable for them.
    // The group/timeline reads must fail as AuraHandledException (never a raw QueryException
    // to the LWC), and the milestone chart must swallow its refused query and return an empty
    // list. An admin would see the same results from the "no record" paths, so the two
    // asserted premises (both queries throw for this user) are what tie them to the refusal.
    @isTest
    static void userWithoutBillingAccess_getsHandledErrorsAndNoMilestones() {
        User u = RLM_BillingUITestUsers.create(
            new List<String>(), new List<String>());
        String bsgId = fakeBsgId();
        Boolean bsgRefused = false;
        Boolean milestoneRefused = false;
        Exception dataThrown;
        Exception timelineThrown;
        List<RLM_BSGTimelineController.MilestoneChartItem> items;

        Test.startTest();
        System.runAs(u) {
            try {
                Database.query('SELECT Id FROM BillingScheduleGroup LIMIT 1', AccessLevel.USER_MODE);
            } catch (QueryException e) {
                bsgRefused = true;
            }
            try {
                Database.query('SELECT BillingMilestonePlanId FROM BillingSchedule LIMIT 1', AccessLevel.USER_MODE);
            } catch (QueryException e) {
                milestoneRefused = true;
            }
            try {
                RLM_BSGTimelineController.getBillingScheduleGroupData(bsgId);
            } catch (Exception e) {
                dataThrown = e;
            }
            try {
                RLM_BSGTimelineController.getConsolidatedTimeline(bsgId);
            } catch (Exception e) {
                timelineThrown = e;
            }
            items = RLM_BSGTimelineController.getMilestoneChartData(bsgId);
        }
        Test.stopTest();

        Assert.isTrue(bsgRefused, 'PRECONDITION: this user must be unable to read BillingScheduleGroup.');
        Assert.isTrue(milestoneRefused,
            'PRECONDITION: BillingSchedule.BillingMilestonePlanId must be absent or unreadable for this user.');
        Assert.isNotNull(dataThrown, 'A refused read must raise an error.');
        Assert.isInstanceOfType(dataThrown, AuraHandledException.class,
            'A refused read surfaces as an AuraHandledException, got ' + dataThrown.getTypeName());
        Assert.isNotNull(timelineThrown, 'A refused read must raise an error from the timeline.');
        Assert.isInstanceOfType(timelineThrown, AuraHandledException.class,
            'The timeline surfaces the refused read as an AuraHandledException, got ' + timelineThrown.getTypeName());
        Assert.isNotNull(items, 'Milestone data degrades to a list, never null.');
        Assert.isTrue(items.isEmpty(), 'A refused milestone query yields no milestones.');
    }
}
