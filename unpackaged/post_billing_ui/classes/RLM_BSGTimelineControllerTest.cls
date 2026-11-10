@isTest
private class RLM_BSGTimelineControllerTest {

    private static String fakeBsgId() {
        return Id.valueOf(BillingScheduleGroup.SObjectType.getDescribe().getKeyPrefix() + '000000000000');
    }

    // BillingScheduleGroup records are system-managed and not insertable in Apex tests.
    // getBillingScheduleGroupData / getConsolidatedTimeline raise AuraHandledException when the
    // BSG cannot be found; getMilestoneChartData degrades to an empty list. Each System.runAs
    // test creates its user through RLM_BillingUITestUsers, which takes a Billing permission
    // set license seat.
    //
    // Known gap (documented, not pinned): getBillingScheduleGroupData throws its not-found
    // AuraHandledException inside a try and rewraps it with e.getMessage(). On a Release 264
    // org, AuraHandledException.getMessage() returned "Script-thrown exception" for both a
    // directly constructed one and this method's not-found error, so the text built for the
    // LWC is the "Error retrieving Billing Schedule Group: " prefix plus that, not "Billing
    // Schedule Group not found". The text the LWC receives is not readable from Apex.
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

    // ─── Malformed input ────────────────────────────────────────────────────

    // A string that is not an id: the two group reads must throw AuraHandledException (not a
    // raw platform exception) and the milestone read must return an empty list. Runs as the
    // running user (no System.runAs), so it does not show which branch inside each method ran.
    @isTest
    static void malformedId_throwsHandledExceptionsAndReturnsNoMilestones() {
        Boolean dataThrew = false;
        Boolean timelineThrew = false;
        List<RLM_BSGTimelineController.MilestoneChartItem> items;

        Test.startTest();
        try {
            RLM_BSGTimelineController.getBillingScheduleGroupData('not-an-id');
        } catch (AuraHandledException e) {
            dataThrew = true;
        }
        try {
            RLM_BSGTimelineController.getConsolidatedTimeline('not-an-id');
        } catch (AuraHandledException e) {
            timelineThrew = true;
        }
        items = RLM_BSGTimelineController.getMilestoneChartData('not-an-id');
        Test.stopTest();

        Assert.isTrue(dataThrew, 'A malformed id surfaces as an AuraHandledException.');
        Assert.isTrue(timelineThrew, 'The timeline surfaces a malformed id as an AuraHandledException.');
        Assert.isNotNull(items, 'Milestone data degrades to a list, never null.');
        Assert.isTrue(items.isEmpty(), 'A malformed id has no milestones.');
    }

    // ─── Access paths (USER_MODE) ───────────────────────────────────────────

    // A Billing-licensed user with only RLM_BillingUI cannot read BillingScheduleGroup, and
    // the milestone link on BillingSchedule is absent or unreadable for them (both need a
    // billing role's user permissions).
    // The group/timeline reads must fail as AuraHandledException (never a raw QueryException
    // to the LWC), and the milestone chart must swallow its refused query and return an empty
    // list. An admin would see the same results from the "no record" paths, so the two
    // asserted premises (both queries throw for this user) are what tie them to the refusal.
    @isTest
    static void userWithoutBillingAccess_getsHandledErrorsAndNoMilestones() {
        User u = RLM_BillingUITestUsers.create(
            new List<String>{ 'RLM_BillingUI' },
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL });
        String bsgId = fakeBsgId();
        Boolean bsgRefused = false;
        Boolean milestoneRefused = false;
        Boolean dataThrew = false;
        Boolean timelineThrew = false;
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
            } catch (AuraHandledException e) {
                dataThrew = true;
            }
            try {
                RLM_BSGTimelineController.getConsolidatedTimeline(bsgId);
            } catch (AuraHandledException e) {
                timelineThrew = true;
            }
            items = RLM_BSGTimelineController.getMilestoneChartData(bsgId);
        }
        Test.stopTest();

        Assert.isTrue(bsgRefused, 'PRECONDITION: this user must be unable to read BillingScheduleGroup.');
        Assert.isTrue(milestoneRefused,
            'PRECONDITION: BillingSchedule.BillingMilestonePlanId must be absent or unreadable for this user.');
        Assert.isTrue(dataThrew, 'A refused read surfaces as an AuraHandledException.');
        Assert.isTrue(timelineThrew, 'The timeline surfaces the refused read as an AuraHandledException.');
        Assert.isNotNull(items, 'Milestone data degrades to a list, never null.');
        Assert.isTrue(items.isEmpty(), 'A refused milestone query yields no milestones.');
    }

    // A billing role gets "not found" (AuraHandledException) for an id with no BSG. The
    // controller's result cannot show whether the not-found throw or a refused query ran, so
    // the premise is the evidence: the role can run a copy of the controller's group query.
    // That query is the only one reached: with no BSG the method throws before its schedule,
    // suspension and milestone reads.
    @isTest
    static void billingRole_canRunTheGroupQuery_unknownIdIsNotFound() {
        User u = RLM_BillingUITestUsers.create(
            new List<String>{ 'RLM_BillingUI', 'RevenueLifecycleManagementBillingOperations' },
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL });
        String bsgId = fakeBsgId();
        String refused;
        Boolean dataThrew = false;

        Test.startTest();
        System.runAs(u) {
            try {
                // Keep in step with the BillingScheduleGroup query in
                // RLM_BSGTimelineController.getBillingScheduleGroupData, and with READS in
                // RLM_BillingUIAccessTest, which asserts the billing role can read these fields.
                Database.query(
                    'SELECT Id, BillingScheduleGroupNumber, ProductName, BillingAccountId, BillingAccount.Name, '
                    + 'CurrencyIsoCode, TotalBilledAmount, TotalPendingAmount, BillingTerm, BillingTermUnit, '
                    + 'BillDayOfMonth, CancellationDate, StartDate, EndDate '
                    + 'FROM BillingScheduleGroup LIMIT 1',
                    AccessLevel.USER_MODE);
            } catch (QueryException e) {
                refused = e.getMessage();
            }
            try {
                RLM_BSGTimelineController.getBillingScheduleGroupData(bsgId);
            } catch (AuraHandledException e) {
                dataThrew = true;
            }
        }
        Test.stopTest();

        Assert.isNull(refused, 'PRECONDITION: a billing role can run the group query: ' + refused);
        Assert.isTrue(dataThrew, 'An unknown BSG is "not found" for a billing role.');
    }
}
