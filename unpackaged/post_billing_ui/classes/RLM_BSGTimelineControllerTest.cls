@isTest
private class RLM_BSGTimelineControllerTest {

    private static String fakeBsgId() {
        return Id.valueOf(BillingScheduleGroup.SObjectType.getDescribe().getKeyPrefix() + '000000000000');
    }

    // BillingScheduleGroup records are system-managed and not insertable in Apex tests.
    // getBillingScheduleGroupData / getConsolidatedTimeline raise AuraHandledException when the
    // BSG cannot be found; getMilestoneChartData degrades to an empty list. What they do with a
    // found group is covered through the seams that take rows (dataFor, applySuspension,
    // addSchedules, addMilestoneChartItems, consolidate). The admin-run
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

    // ─── Seams over queried rows ─────────────────────────────────────────────
    // Billing schedule groups and schedules cannot be inserted in Apex, and a milestone plan
    // needs a billing treatment, so these pass rows built with JSON.deserialize (and schedule
    // wrappers) to the methods the controller calls with the rows it queried.

    private static Id fakeId(Schema.SObjectType objectType, Integer n) {
        return Id.valueOf(objectType.getDescribe().getKeyPrefix() + String.valueOf(n).leftPad(12, '0'));
    }

    private static SObject row(String objectName, Map<String, Object> fields) {
        return (SObject) JSON.deserialize(JSON.serialize(fields), Type.forName(objectName));
    }

    // True when the org has no such object, by describe or as an Apex type; row() needs both.
    private static Boolean missing(String objectName) {
        return Schema.getGlobalDescribe().get(objectName) == null || Type.forName(objectName) == null;
    }

    // A group with no schedules, suspension or milestones: its own fields are mapped, the account
    // name comes through the relationship, and the schedule list is empty.
    @isTest
    static void dataFor_mapsTheGroupsFields() {
        Id groupId = fakeId(BillingScheduleGroup.SObjectType, 1);
        Date start = Date.newInstance(2026, 1, 1);
        BillingScheduleGroup bsg = (BillingScheduleGroup) row('BillingScheduleGroup', new Map<String, Object>{
            'Id' => groupId, 'BillingScheduleGroupNumber' => 'BSG-0001', 'ProductName' => 'Data Plan',
            'BillingAccount' => new Map<String, Object>{ 'Name' => 'Acme Billing' },
            'TotalBilledAmount' => 100, 'TotalPendingAmount' => 50, 'BillingTerm' => 3,
            'BillingTermUnit' => 'Month', 'BillDayOfMonth' => 15, 'StartDate' => start,
            'EndDate' => start.addYears(1), 'CancellationDate' => start.addMonths(6) });

        Test.startTest();
        RLM_BSGTimelineController.BSGData data = RLM_BSGTimelineController.dataFor(bsg);
        Test.stopTest();

        Assert.areEqual(String.valueOf(groupId), data.id, 'The group id is shown');
        Assert.areEqual('BSG-0001', data.groupNumber, 'The group number is shown');
        Assert.areEqual('Data Plan', data.productName, 'The product is shown');
        Assert.areEqual('Acme Billing', data.accountName, 'The billing account name comes through the relationship');
        Assert.areEqual(100, data.totalBilledAmount, 'Billed is shown');
        Assert.areEqual(50, data.totalPendingAmount, 'Pending is shown');
        Assert.areEqual('3', data.billingTerm, 'The term is shown as text');
        Assert.areEqual('Month', data.billingTermUnit, 'The term unit is shown');
        Assert.areEqual(15, data.billDayOfMonth, 'The bill day is shown');
        Assert.areEqual(start, data.startDate, 'The start date is shown');
        Assert.areEqual(start.addYears(1), data.endDate, 'The end date is shown');
        Assert.areEqual(start.addMonths(6), data.cancellationDate, 'The cancellation date is shown');
        Assert.isTrue(data.billingSchedules.isEmpty(), 'No schedules were found');
    }

    // Suspension and resumption dates are taken when set and left blank otherwise.
    @isTest
    static void applySuspension_takesTheDatesThatAreSet() {
        Map<String, Schema.SObjectField> fields = BillingScheduleGroup.SObjectType.getDescribe().fields.getMap();
        if (!fields.containsKey('BillingSuspensionDate') || !fields.containsKey('BillingResumptionDate')) {
            // No suspension fields in this org: the timeline never reads them here.
            return;
        }
        Date suspended = Date.newInstance(2026, 4, 1);
        RLM_BSGTimelineController.BSGData data = new RLM_BSGTimelineController.BSGData();
        RLM_BSGTimelineController.BSGData resumedOnly = new RLM_BSGTimelineController.BSGData();

        Test.startTest();
        RLM_BSGTimelineController.applySuspension(data,
            row('BillingScheduleGroup', new Map<String, Object>{ 'BillingSuspensionDate' => suspended }));
        RLM_BSGTimelineController.applySuspension(resumedOnly,
            row('BillingScheduleGroup', new Map<String, Object>{ 'BillingResumptionDate' => suspended.addMonths(1) }));
        Test.stopTest();

        Assert.areEqual(suspended, data.suspensionDate, 'A set suspension date is taken');
        Assert.isNull(data.resumptionDate, 'A blank resumption date stays blank');
        Assert.isNull(resumedOnly.suspensionDate, 'A blank suspension date stays blank');
        Assert.areEqual(suspended.addMonths(1), resumedOnly.resumptionDate, 'A set resumption date is taken');
    }

    // Each queried schedule becomes one row, in query order, with its fields.
    @isTest
    static void addSchedules_mapsEachScheduleInOrder() {
        Date start = Date.newInstance(2026, 1, 1);
        List<BillingSchedule> rows = new List<BillingSchedule>{
            (BillingSchedule) row('BillingSchedule', new Map<String, Object>{
                'Id' => fakeId(BillingSchedule.SObjectType, 2), 'BillingScheduleNumber' => 'BS-2',
                'Category' => 'Amendment', 'Status' => 'ReadyForInvoicing', 'Quantity' => 3, 'BilledAmount' => 10,
                'PendingAmount' => 20, 'TotalAmount' => 30, 'BillingPeriodAmount' => 5, 'UnitPrice' => 1.5,
                'BillingScheduleStartDate' => start, 'BillingScheduleEndDate' => start.addMonths(3),
                'NextBillingDate' => start.addMonths(1), 'BillingMethod' => 'OrderAmount', 'BillingType' => 'Advance',
                'BillingTerm' => 1, 'BillingTermUnit' => 'Month' }),
            (BillingSchedule) row('BillingSchedule', new Map<String, Object>{
                'Id' => fakeId(BillingSchedule.SObjectType, 1), 'BillingScheduleNumber' => 'BS-1' })
        };
        List<RLM_BSGTimelineController.BillingScheduleData> target = new List<RLM_BSGTimelineController.BillingScheduleData>();

        Test.startTest();
        RLM_BSGTimelineController.addSchedules(target, rows);
        Test.stopTest();

        Assert.areEqual(new List<String>{ 'BS-2', 'BS-1' }, new List<String>{ target[0].scheduleNumber, target[1].scheduleNumber },
            'Rows keep the query order, not number order');
        RLM_BSGTimelineController.BillingScheduleData full = target[0];
        Assert.areEqual('Amendment', full.category, 'The category is mapped');
        Assert.areEqual('ReadyForInvoicing', full.status, 'The status is mapped');
        Assert.areEqual(3, full.quantity, 'The quantity is mapped');
        Assert.areEqual(10, full.billedAmount, 'Billed is mapped');
        Assert.areEqual(20, full.pendingAmount, 'Pending is mapped');
        Assert.areEqual(30, full.totalAmount, 'The total is mapped');
        Assert.areEqual(5, full.billingPeriodAmount, 'The period amount is mapped');
        Assert.areEqual(1.5, full.unitPrice, 'The unit price is mapped');
        Assert.areEqual(start, full.startDate, 'The start date is mapped');
        Assert.areEqual(start.addMonths(3), full.endDate, 'The end date is mapped');
        Assert.areEqual(start.addMonths(1), full.nextBillingDate, 'The next billing date is mapped');
        Assert.areEqual('OrderAmount', full.billingMethod, 'The billing method is mapped');
        Assert.areEqual('Advance', full.billingType, 'The billing type is mapped');
        Assert.areEqual(1, full.billingTerm, 'The term is mapped');
        Assert.areEqual('Month', full.billingTermUnit, 'The term unit is mapped');
    }

    // Each queried milestone item becomes a chart item in query order, carrying the plan's
    // reference amount and the group's billed amount.
    @isTest
    static void addMilestoneChartItems_carryThePlanAndGroupAmounts() {
        if (missing('BillingMilestonePlanItem')) {
            // No billing milestone objects in this org: the timeline never reads milestones here.
            return;
        }
        Date done = Date.newInstance(2026, 3, 1);
        // In the query's order: accomplished items first, which is not name order.
        List<SObject> items = new List<SObject>{
            row('BillingMilestonePlanItem', new Map<String, Object>{ 'Name' => 'Kickoff', 'MilestoneAmount' => 270,
                'Percentage' => 30, 'Status' => 'Accomplished', 'IsMilestoneAccomplished' => true,
                'MilestoneAccomplishmentDate' => done }),
            row('BillingMilestonePlanItem', new Map<String, Object>{ 'Name' => 'Go-live', 'MilestoneAmount' => 630,
                'Percentage' => 70, 'Status' => 'Draft', 'IsMilestoneAccomplished' => false })
        };
        List<RLM_BSGTimelineController.MilestoneChartItem> result = new List<RLM_BSGTimelineController.MilestoneChartItem>();

        Test.startTest();
        RLM_BSGTimelineController.addMilestoneChartItems(result, items, 900, 270);
        Test.stopTest();

        Assert.areEqual(new List<String>{ 'Kickoff', 'Go-live' }, new List<String>{ result[0].name, result[1].name },
            'Items keep the query order, not name order');
        Assert.areEqual(630, result[1].amount, 'The milestone amount is shown');
        Assert.areEqual(70, result[1].percentage, 'The percentage is shown');
        Assert.isFalse(result[1].isAccomplished, 'An open milestone is not accomplished');
        Assert.isNull(result[1].completionDate, 'An open milestone has no completion date');
        Assert.areEqual(done, result[0].completionDate, 'An accomplished milestone has its date');
        for (RLM_BSGTimelineController.MilestoneChartItem item : result) {
            Assert.areEqual(900, item.referenceAmount, 'Every item carries the plan\'s reference amount');
            Assert.areEqual(270, item.billedAmount, 'Every item carries the group\'s billed amount');
        }
    }

    private static RLM_BSGTimelineController.BillingScheduleData schedule(
        String num, Date startDate, Date endDate, Decimal quantity, Decimal periodAmount, String category, String status
    ) {
        RLM_BSGTimelineController.BillingScheduleData bs = new RLM_BSGTimelineController.BillingScheduleData();
        bs.id = num + '-id';
        bs.scheduleNumber = num;
        bs.startDate = startDate;
        bs.endDate = endDate;
        bs.quantity = quantity;
        bs.billingPeriodAmount = periodAmount;
        bs.category = category;
        bs.status = status;
        return bs;
    }

    // The timeline splits at every schedule start and day after an end. Each segment lists the
    // schedules active in it, adds their quantities, puts positive period amounts in billing and
    // negative ones in credits, and is Cancelled if any is, else Completely Billed if any is.
    @isTest
    static void consolidate_splitsAtEveryBoundaryAndTotalsTheActiveSchedules() {
        Date jan = Date.newInstance(2026, 1, 1);
        Date feb = Date.newInstance(2026, 2, 1);
        Date mar = Date.newInstance(2026, 3, 1);
        Date apr = Date.newInstance(2026, 4, 1);
        // In the query's order (by start date): the fully billed BS-2 comes before the
        // cancellation BS-3.
        List<RLM_BSGTimelineController.BillingScheduleData> schedules = new List<RLM_BSGTimelineController.BillingScheduleData>{
            schedule('BS-1', jan, mar.addDays(30), 2, 100, 'Order', 'Active'),
            schedule('BS-2', feb, apr.addDays(29), 1, -30, 'Order', 'Completely Billed'),
            schedule('BS-3', mar, mar.addDays(30), null, null, 'Cancellation', 'Active')
        };
        // The same span with the cancellation first.
        List<RLM_BSGTimelineController.BillingScheduleData> cancelledFirst = new List<RLM_BSGTimelineController.BillingScheduleData>{
            schedule('BS-4', jan, jan.addDays(30), 1, 10, 'Cancellation', 'Active'),
            schedule('BS-5', jan, jan.addDays(30), 1, 10, 'Order', 'Completely Billed')
        };

        Test.startTest();
        List<RLM_BSGTimelineController.ConsolidatedSegment> segments = RLM_BSGTimelineController.consolidate(schedules);
        List<RLM_BSGTimelineController.ConsolidatedSegment> single = RLM_BSGTimelineController.consolidate(cancelledFirst);
        Test.stopTest();

        Assert.areEqual(4, segments.size(), 'Boundaries Jan 1, Feb 1, Mar 1, Apr 1 and May 1 make four segments');
        Assert.areEqual(1, segments[0].periodNumber, 'Periods are numbered from 1');
        Assert.areEqual(jan, segments[0].startDate, 'The first segment starts at the earliest start');
        Assert.areEqual(feb.addDays(-1), segments[0].endDate, 'A segment ends the day before the next boundary');
        Assert.areEqual(new List<String>{ 'BS-1' }, segments[0].activeScheduleNumbers, 'Only BS-1 runs in January');
        Assert.areEqual(2, segments[0].netQuantity, 'January adds BS-1\'s quantity');
        Assert.areEqual(100, segments[0].periodicBilling, 'A positive period amount is billing');
        Assert.areEqual('Active', segments[0].status, 'No cancelled or fully billed schedule: Active');

        Assert.areEqual(3, segments[1].netQuantity, 'February adds BS-1 and BS-2');
        Assert.areEqual(-30, segments[1].credits, 'A negative period amount is a credit');
        Assert.areEqual('Completely Billed', segments[1].status, 'A fully billed schedule marks the segment');

        Assert.areEqual(new List<String>{ 'BS-1', 'BS-2', 'BS-3' }, segments[2].activeScheduleNumbers,
            'All three run in March, in schedule order');
        Assert.areEqual(3, segments[2].netQuantity, 'A blank quantity adds nothing');
        Assert.areEqual('Cancelled', segments[2].status,
            'A cancellation replaces a fully billed schedule before it');
        Assert.areEqual(1, single.size(), 'Two schedules over the same span make one segment');
        Assert.areEqual('Cancelled', single[0].status,
            'A fully billed schedule after a cancellation does not replace it');

        Assert.areEqual(apr, segments[3].startDate, 'The last segment starts on April 1');
        Assert.areEqual(apr.addDays(29), segments[3].endDate, 'The last segment ends on BS-2\'s end');
        Assert.areEqual(new List<String>{ 'BS-2' }, segments[3].activeScheduleNumbers, 'Only BS-2 runs in April');
    }

    // No schedules, no segments.
    @isTest
    static void consolidate_noSchedulesMakesNoSegments() {
        Test.startTest();
        List<RLM_BSGTimelineController.ConsolidatedSegment> segments =
            RLM_BSGTimelineController.consolidate(new List<RLM_BSGTimelineController.BillingScheduleData>());
        Test.stopTest();

        Assert.isTrue(segments.isEmpty(), 'No schedules give no segments');
    }
}
