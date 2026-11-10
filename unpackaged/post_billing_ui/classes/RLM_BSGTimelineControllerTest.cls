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

    // ─── Malformed input ────────────────────────────────────────────────────

    // A string that is not an id fails the bind; every entry point must still answer the LWC
    // the way it answers for a missing record.
    @isTest
    static void malformedId_isHandledLikeAMissingRecord() {
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

        Assert.isTrue(dataThrew, 'A malformed id is reported as an AuraHandledException.');
        Assert.isTrue(timelineThrew, 'The timeline wraps the same failure as an AuraHandledException.');
        Assert.isNotNull(items, 'Milestone data degrades to a list, never null.');
        Assert.isTrue(items.isEmpty(), 'A malformed id has no milestones.');
    }

    // ─── Access paths (USER_MODE) ───────────────────────────────────────────

    // A Billing-licensed user with only RLM_BillingUI cannot read BillingScheduleGroup, nor
    // the milestone link on BillingSchedule (both need a billing role's user permissions).
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

        Assert.isTrue(bsgRefused, 'Premise: this user must be unable to read BillingScheduleGroup.');
        Assert.isTrue(milestoneRefused,
            'Premise: this user must be unable to read BillingSchedule.BillingMilestonePlanId.');
        Assert.isTrue(dataThrew, 'A refused read surfaces as an AuraHandledException.');
        Assert.isTrue(timelineThrew, 'The timeline surfaces the refused read as an AuraHandledException.');
        Assert.isNotNull(items, 'Milestone data degrades to a list, never null.');
        Assert.isTrue(items.isEmpty(), 'A refused milestone query yields no milestones.');
    }

    // A billing role can select every field the timeline's queries read, including the
    // milestone extension's dynamic ones, so an unknown id is "not found" rather than "refused".
    @isTest
    static void billingRole_canRunTheTimelineQueries() {
        User u = RLM_BillingUITestUsers.create(
            new List<String>{ 'RLM_BillingUI', 'RevenueLifecycleManagementBillingOperations' },
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL });
        String bsgId = fakeBsgId();
        List<String> refused = new List<String>();
        Boolean dataThrew = false;
        List<RLM_BSGTimelineController.MilestoneChartItem> items;

        // CurrencyIsoCode exists only in multi-currency orgs.
        String currencyField = UserInfo.isMultiCurrencyOrganization() ? 'CurrencyIsoCode, ' : '';

        Test.startTest();
        System.runAs(u) {
            for (String soql : new List<String>{
                'SELECT Id, BillingScheduleGroupNumber, ProductName, BillingAccountId, BillingAccount.Name, '
                    + currencyField
                    + 'TotalBilledAmount, TotalPendingAmount, BillingTerm, BillingTermUnit, BillDayOfMonth, '
                    + 'CancellationDate, StartDate, EndDate, BillingSuspensionDate, BillingResumptionDate '
                    + 'FROM BillingScheduleGroup LIMIT 1',
                'SELECT Id, BillingScheduleNumber, Category, Status, Quantity, BilledAmount, PendingAmount, '
                    + 'TotalAmount, BillingPeriodAmount, UnitPrice, BillingScheduleStartDate, '
                    + 'BillingScheduleEndDate, NextBillingDate, BillingMethod, BillingType, BillingTerm, '
                    + 'BillingTermUnit, BillingMilestonePlanId, CreatedDate FROM BillingSchedule LIMIT 1',
                'SELECT Id, ReferenceItemAmount FROM BillingMilestonePlan LIMIT 1',
                'SELECT Id, Name, MilestoneAmount, Percentage, Status, MilestoneAccomplishmentDate, '
                    + 'IsMilestoneAccomplished, MilestoneType, BillingMilestonePlanId '
                    + 'FROM BillingMilestonePlanItem LIMIT 1'
            }) {
                try {
                    Database.query(soql, AccessLevel.USER_MODE);
                } catch (QueryException e) {
                    refused.add(e.getMessage());
                }
            }
            try {
                RLM_BSGTimelineController.getBillingScheduleGroupData(bsgId);
            } catch (AuraHandledException e) {
                dataThrew = true;
            }
            items = RLM_BSGTimelineController.getMilestoneChartData(bsgId);
        }
        Test.stopTest();

        Assert.isTrue(refused.isEmpty(), 'Premise: a billing role can run the timeline queries: ' + refused);
        Assert.isTrue(dataThrew, 'An unknown BSG is still "not found" for a billing role.');
        Assert.isTrue(items.isEmpty(), 'An unknown BSG has no milestone plan.');
    }
}
