@isTest
private class RLM_BSGContextControllerTest {

    // Tests for RLM_BSGContextController. BillingScheduleGroup, BillingSchedule and
    // BsgRelationship cannot be inserted in Apex tests, so getBSGContext itself is covered on
    // the paths that need no BSG: a malformed or null id, an id matching no BSG, and a BSG
    // query the user may not run. What it does with a found group is covered through the seams
    // that take rows (fillContext, getBundleData, the milestone, usage and arrangement helpers),
    // in the tests after "Seams over queried rows". With fake ids fillContext reaches only the
    // usage and standard views; choosing the milestone or bundle view needs real rows (live
    // verification only). The admin-run unknown-id test
    // (getBSGContext_unknownId_returnsEmptyStandard) reaches "not found or refused"
    // (indistinguishable when run as the admin).
    // The bundle assembly (appendComponentsDfs) is covered with in-memory BSGs; the
    // charge-type / frequency helpers are called directly with plain inputs.
    // The refused-access test runs as a plain Minimum Access user with no permission set
    // license (no Billing PSL seat); billing-role read coverage for the controller's fields is
    // in RLM_BillingUIAccessTest (billingOperationsCanRunItsControllerReads).
    //
    // Fixed: groupBilledAmount/groupPendingAmount come from the group's TotalBilledAmount and
    // TotalPendingAmount (no arbitrary single schedule; fillContext_usageGroupWithAnArrangement
    // checks it), and the usage resource names come from the earliest schedule
    // (ORDER BY CreatedDate, Id, first wins; live verification only).
    private static Id fakeBsgId() {
        return Id.valueOf(
            BillingScheduleGroup.SObjectType.getDescribe().getKeyPrefix() + '000000000000'
        );
    }

    @isTest
    static void getBSGContext_malformedId_returnsStandard() {
        Test.startTest();
        RLM_BSGContextController.BSGContext ctx =
            RLM_BSGContextController.getBSGContext('not-a-valid-id');
        Test.stopTest();
        System.assertNotEquals(null, ctx, 'A context should always be returned.');
        System.assertEquals('standard', ctx.viewType,
            'A malformed id must degrade to a standard view, not throw.');
    }

    @isTest
    static void getBSGContext_nullId_returnsStandard() {
        Test.startTest();
        RLM_BSGContextController.BSGContext ctx =
            RLM_BSGContextController.getBSGContext(null);
        Test.stopTest();
        System.assertNotEquals(null, ctx, 'A context should always be returned.');
        System.assertEquals('standard', ctx.viewType,
            'A null id must degrade to a standard view, not throw.');
    }

    @isTest
    static void getBSGContext_unknownId_returnsEmptyStandard() {
        Test.startTest();
        RLM_BSGContextController.BSGContext ctx =
            RLM_BSGContextController.getBSGContext(fakeBsgId());
        Test.stopTest();
        System.assertNotEquals(null, ctx, 'A context should always be returned.');
        System.assertEquals('standard', ctx.viewType,
            'An id matching no BSG must resolve to a standard view.');
        System.assertEquals(null, ctx.bundle, 'No bundle data expected for an unknown id.');
        System.assertEquals(null, ctx.milestonePlan, 'No milestone data expected for an unknown id.');
        System.assertEquals(null, ctx.usage, 'No usage data expected for an unknown id.');
        System.assertEquals(null, ctx.arrangement, 'No arrangement data expected for an unknown id.');
    }

    // ─── Pure-helper coverage ───────────────────────────────────────────────

    @isTest
    static void deriveChargeType_coversAllBranches() {
        Assert.areEqual('Usage',
            RLM_BSGContextController.deriveChargeType('Usage', 'Month', null));
        Assert.areEqual('One-Time',
            RLM_BSGContextController.deriveChargeType('Subscription', 'OneTime', null));
        Assert.areEqual('Evergreen',
            RLM_BSGContextController.deriveChargeType('Subscription', 'Month', null));
        Assert.areEqual('Termed Subscription',
            RLM_BSGContextController.deriveChargeType('Subscription', 'Month', Date.today().addDays(30)));
    }

    @isTest
    static void formatFrequency_coversBranches() {
        Assert.areEqual('One-Time', RLM_BSGContextController.formatFrequency(1, 'OneTime'));
        Assert.areEqual('1 Month', RLM_BSGContextController.formatFrequency(1, 'Month'));
        Assert.areEqual('1 ', RLM_BSGContextController.formatFrequency(null, null));
    }

    // ─── Bundle assembly (appendComponentsDfs) ──────────────────────────────

    // Builds a two-level bundle entirely in memory and verifies appendComponentsDfs emits
    // the flat list in depth-first display order with siblings sorted by ProductName, and
    // sets depth / isCurrent / isSubBundle correctly.
    @isTest
    static void appendComponentsDfs_buildsDfsOrderedTree() {
        Id mainId   = mintBsgId();
        Id childB    = mintBsgId(); // ProductName 'Apple'  (sorts first)
        Id childA    = mintBsgId(); // ProductName 'Banana' (sub-bundle)
        Id grandKid  = mintBsgId(); // ProductName 'Cherry'

        Map<Id, BillingScheduleGroup> bsgById = new Map<Id, BillingScheduleGroup>{
            childB   => synthBsg(childB, 'Apple'),
            childA   => synthBsg(childA, 'Banana'),
            grandKid => synthBsg(grandKid, 'Cherry')
        };
        Map<Id, List<Id>> parentToChildren = new Map<Id, List<Id>>{
            mainId => new List<Id>{ childA, childB }, // intentionally unsorted
            childA => new List<Id>{ grandKid }
        };
        Set<Id> subBundleIds = new Set<Id>{ childA };
        List<RLM_BSGContextController.BundleComponentData> result =
            new List<RLM_BSGContextController.BundleComponentData>();

        Test.startTest();
        RLM_BSGContextController.appendComponentsDfs(
            mainId, childB, 1, parentToChildren, subBundleIds, bsgById, result, new Set<Id>()
        );
        Test.stopTest();

        System.assertEquals(3, result.size(), 'All three descendants should be emitted once.');

        // Sibling order: Apple (childB) before Banana (childA); grandchild follows its parent.
        System.assertEquals('Apple', result[0].productName, 'Siblings sort by ProductName.');
        System.assertEquals(1, result[0].depth, 'Direct children are depth 1.');
        System.assertEquals(false, result[0].isSubBundle, 'Apple is a leaf.');
        System.assertEquals(true, result[0].isCurrent, 'childB was passed as the current record.');

        System.assertEquals('Banana', result[1].productName);
        System.assertEquals(1, result[1].depth);
        System.assertEquals(true, result[1].isSubBundle, 'Banana parents a grandchild.');
        System.assertEquals(false, result[1].isCurrent);

        System.assertEquals('Cherry', result[2].productName, 'Grandchild follows its parent (DFS).');
        System.assertEquals(2, result[2].depth, 'Grandchild is depth 2.');
    }

    @isTest
    static void appendComponentsDfs_guardsAgainstRepeatEmission() {
        Id mainId = mintBsgId();
        Id child  = mintBsgId();
        Map<Id, BillingScheduleGroup> bsgById = new Map<Id, BillingScheduleGroup>{
            child => synthBsg(child, 'Solo')
        };
        Map<Id, List<Id>> parentToChildren = new Map<Id, List<Id>>{
            mainId => new List<Id>{ child }
        };
        List<RLM_BSGContextController.BundleComponentData> result =
            new List<RLM_BSGContextController.BundleComponentData>();
        Set<Id> emitted = new Set<Id>{ child }; // already emitted elsewhere

        Test.startTest();
        RLM_BSGContextController.appendComponentsDfs(
            mainId, mainId, 1, parentToChildren, new Set<Id>(), bsgById, result, emitted
        );
        Test.stopTest();

        System.assertEquals(0, result.size(),
            'A component already in the emitted set must not be added again (diamond guard).');
    }

    // ─── Access paths (USER_MODE) ───────────────────────────────────────────

    // A Minimum Access user with no permission sets cannot read BillingScheduleGroup. The
    // premise asserts that the USER_MODE query throws for this user; given that, a returned
    // standard context proves the controller caught the refusal instead of passing it to the
    // LWC. An admin would get the same context from the "no record" path, so the premise is
    // what makes this test mean it.
    @isTest
    static void getBSGContext_refusedBsgQuery_degradesToStandardWithoutThrowing() {
        User u = RLM_BillingUITestUsers.create(
            new List<String>(), new List<String>());
        Id bsgId = fakeBsgId();
        Boolean premise = false;
        RLM_BSGContextController.BSGContext ctx;

        Test.startTest();
        System.runAs(u) {
            try {
                Database.query('SELECT Id FROM BillingScheduleGroup LIMIT 1', AccessLevel.USER_MODE);
            } catch (QueryException e) {
                premise = true;
            }
            ctx = RLM_BSGContextController.getBSGContext(bsgId);
        }
        Test.stopTest();

        Assert.isTrue(premise, 'PRECONDITION: this user must be unable to read BillingScheduleGroup.');
        Assert.isNotNull(ctx, 'A context is returned even when the query is refused.');
        Assert.areEqual('standard', ctx.viewType, 'A refused query degrades to the standard view.');
    }

    // ─── Pure helpers: remaining branches ───────────────────────────────────

    @isTest
    static void deriveChargeType_isCaseInsensitiveAndUsageWins() {
        Assert.areEqual('One-Time', RLM_BSGContextController.deriveChargeType(null, 'onetime', null),
            'OneTime matching ignores case.');
        Assert.areEqual('Usage', RLM_BSGContextController.deriveChargeType('Usage', 'OneTime', Date.today()),
            'Usage billing wins over the term unit.');
        Assert.areEqual('Termed Subscription',
            RLM_BSGContextController.deriveChargeType(null, null, Date.newInstance(2027, 1, 1)),
            'No method or unit, but an end date -> termed.');
        Assert.areEqual('Evergreen', RLM_BSGContextController.deriveChargeType(null, null, null),
            'No method, unit or end date -> evergreen.');
    }

    @isTest
    static void formatFrequency_usesTermAndUnit() {
        Assert.areEqual('12 Month', RLM_BSGContextController.formatFrequency(12, 'Month'));
        Assert.areEqual('One-Time', RLM_BSGContextController.formatFrequency(6, 'ONETIME'),
            'OneTime ignores the term and the case of the unit.');
        Assert.areEqual('3 ', RLM_BSGContextController.formatFrequency(3, null), 'A missing unit is blank.');
        Assert.areEqual('1 Day', RLM_BSGContextController.formatFrequency(null, 'Day'), 'A missing term is 1.');
    }

    // ─── appendComponentsDfs: guards and edge shapes ────────────────────────

    @isTest
    static void appendComponentsDfs_parentWithNoChildren_emitsNothing() {
        Id mainId = mintBsgId();
        Id other = mintBsgId();
        List<RLM_BSGContextController.BundleComponentData> result =
            new List<RLM_BSGContextController.BundleComponentData>();

        RLM_BSGContextController.appendComponentsDfs(
            mainId, mainId, 1,
            new Map<Id, List<Id>>{ mainId => new List<Id>() },
            new Set<Id>(), new Map<Id, BillingScheduleGroup>(), result, new Set<Id>()
        );
        Assert.areEqual(0, result.size(), 'A parent with an empty child list emits nothing.');

        RLM_BSGContextController.appendComponentsDfs(
            other, mainId, 1, new Map<Id, List<Id>>(), new Set<Id>(),
            new Map<Id, BillingScheduleGroup>(), result, new Set<Id>()
        );
        Assert.areEqual(0, result.size(), 'A parent missing from the map emits nothing.');
    }

    // A child id with no loaded BSG is skipped, not emitted as a blank row; its loaded
    // siblings are still emitted.
    @isTest
    static void appendComponentsDfs_skipsChildrenWithoutALoadedBsg() {
        Id mainId = mintBsgId();
        Id visible = mintBsgId();
        Id hidden = mintBsgId();
        List<RLM_BSGContextController.BundleComponentData> result =
            new List<RLM_BSGContextController.BundleComponentData>();

        RLM_BSGContextController.appendComponentsDfs(
            mainId, mainId, 1,
            new Map<Id, List<Id>>{ mainId => new List<Id>{ hidden, visible } },
            new Set<Id>(),
            new Map<Id, BillingScheduleGroup>{ visible => synthBsg(visible, 'Visible') },
            result, new Set<Id>()
        );

        Assert.areEqual(1, result.size(), 'Only the child with a loaded BSG is emitted.');
        Assert.areEqual(visible, result[0].bsgId);
        Assert.isFalse(result[0].isCurrent, 'The main BSG was the current record, not the child.');
    }

    @isTest
    static void appendComponentsDfs_nullProductNameSortsFirst() {
        Id mainId = mintBsgId();
        Id named = mintBsgId();
        Id unnamed = mintBsgId();
        List<RLM_BSGContextController.BundleComponentData> result =
            new List<RLM_BSGContextController.BundleComponentData>();

        RLM_BSGContextController.appendComponentsDfs(
            mainId, mainId, 1,
            new Map<Id, List<Id>>{ mainId => new List<Id>{ named, unnamed } },
            new Set<Id>(),
            new Map<Id, BillingScheduleGroup>{
                named => synthBsg(named, 'Alpha'),
                unnamed => synthBsg(unnamed, null)
            },
            result, new Set<Id>()
        );

        Assert.areEqual(2, result.size());
        Assert.areEqual(unnamed, result[0].bsgId, 'A null product name sorts as empty, ahead of named siblings.');
        Assert.isNull(result[0].productName);
        Assert.areEqual(named, result[1].bsgId);
    }

    // Cycle guard for a cycle below the root: a sub-bundle that lists an ancestor (other than
    // the main BSG) as its child must not loop or emit that ancestor twice.
    @isTest
    static void appendComponentsDfs_cycleIsEmittedOnce() {
        Id mainId = mintBsgId();
        Id a = mintBsgId();
        Id b = mintBsgId();
        Map<Id, List<Id>> parentToChildren = new Map<Id, List<Id>>{
            mainId => new List<Id>{ a },
            a => new List<Id>{ b },
            b => new List<Id>{ a }
        };
        List<RLM_BSGContextController.BundleComponentData> result =
            new List<RLM_BSGContextController.BundleComponentData>();

        RLM_BSGContextController.appendComponentsDfs(
            mainId, b, 1, parentToChildren, new Set<Id>(parentToChildren.keySet()),
            new Map<Id, BillingScheduleGroup>{ a => synthBsg(a, 'A'), b => synthBsg(b, 'B') },
            result, new Set<Id>()
        );

        Assert.areEqual(2, result.size(), 'Each BSG in the cycle is emitted exactly once.');
        Assert.areEqual(a, result[0].bsgId);
        Assert.areEqual(1, result[0].depth);
        Assert.areEqual(b, result[1].bsgId);
        Assert.areEqual(2, result[1].depth);
        Assert.isTrue(result[1].isCurrent, 'b was passed as the current record.');
    }

    // A cycle back to the root: collectChildComponents seeds the emitted set with the main BSG,
    // so main -> a -> main emits only a.
    @isTest
    static void appendComponentsDfs_cycleToRoot_neverEmitsTheMainBsgAsItsOwnComponent() {
        Id mainId = mintBsgId();
        Id a = mintBsgId();
        Map<Id, List<Id>> parentToChildren = new Map<Id, List<Id>>{
            mainId => new List<Id>{ a },
            a => new List<Id>{ mainId }
        };
        List<RLM_BSGContextController.BundleComponentData> result =
            new List<RLM_BSGContextController.BundleComponentData>();

        RLM_BSGContextController.appendComponentsDfs(
            mainId, mainId, 1, parentToChildren, new Set<Id>(parentToChildren.keySet()),
            new Map<Id, BillingScheduleGroup>{ a => synthBsg(a, 'A'), mainId => synthBsg(mainId, 'Main') },
            result, new Set<Id>{ mainId }
        );

        Assert.areEqual(1, result.size(), 'The main BSG is never emitted as its own component.');
        Assert.areEqual(a, result[0].bsgId);
    }

    // At most five levels are emitted: a sixth level is never emitted.
    @isTest
    static void appendComponentsDfs_emitsAtMostFiveLevels() {
        Id mainId = mintBsgId();
        List<Id> chain = new List<Id>();
        for (Integer i = 0; i < 6; i++) {
            chain.add(mintBsgId());
        }
        Map<Id, List<Id>> parentToChildren = new Map<Id, List<Id>>{ mainId => new List<Id>{ chain[0] } };
        Map<Id, BillingScheduleGroup> bsgById = new Map<Id, BillingScheduleGroup>();
        for (Integer i = 0; i < chain.size(); i++) {
            bsgById.put(chain[i], synthBsg(chain[i], 'Level ' + (i + 1)));
            if (i < chain.size() - 1) {
                parentToChildren.put(chain[i], new List<Id>{ chain[i + 1] });
            }
        }
        // As in collectChildComponents: every parent in the map, including the main BSG.
        Set<Id> subBundleIds = new Set<Id>(parentToChildren.keySet());
        List<RLM_BSGContextController.BundleComponentData> result =
            new List<RLM_BSGContextController.BundleComponentData>();

        Test.startTest();
        RLM_BSGContextController.appendComponentsDfs(
            mainId, mainId, 1, parentToChildren, subBundleIds, bsgById, result, new Set<Id>()
        );
        Test.stopTest();

        Assert.areEqual(5, result.size(), 'Levels 1-5 are emitted; level 6 is past the safety limit.');
        for (Integer i = 0; i < result.size(); i++) {
            Assert.areEqual(i + 1, result[i].depth, 'Each level is one deeper than its parent.');
            Assert.areEqual(chain[i], result[i].bsgId);
            Assert.areEqual('Level ' + (i + 1), result[i].productName);
        }
    }

    @isTest
    static void appendComponentsDfs_setsChargeTypeAndFrequencyPerComponent() {
        Id mainId = mintBsgId();
        Id usage = mintBsgId();
        Id termed = mintBsgId();
        Map<String, Object> usageFields = new Map<String, Object>{
            'BillingMethod' => 'Usage', 'BillingTermUnit' => 'Month', 'BillingTerm' => 1
        };
        Map<String, Object> termedFields = new Map<String, Object>{
            'BillingMethod' => 'Subscription', 'BillingTermUnit' => 'Month', 'BillingTerm' => 12,
            'EndDate' => '2027-12-31'
        };
        List<RLM_BSGContextController.BundleComponentData> result =
            new List<RLM_BSGContextController.BundleComponentData>();

        RLM_BSGContextController.appendComponentsDfs(
            mainId, mainId, 1,
            new Map<Id, List<Id>>{ mainId => new List<Id>{ usage, termed } },
            new Set<Id>(),
            new Map<Id, BillingScheduleGroup>{
                usage => synthBsg(usage, 'Metered', usageFields),
                termed => synthBsg(termed, 'Subscription', termedFields)
            },
            result, new Set<Id>()
        );

        Assert.areEqual(2, result.size());
        Assert.areEqual('Metered', result[0].productName);
        Assert.areEqual('Usage', result[0].chargeType);
        Assert.areEqual('1 Month', result[0].billingFrequency);
        Assert.areEqual('Subscription', result[1].productName);
        Assert.areEqual('Termed Subscription', result[1].chargeType, 'An end date makes it termed.');
        Assert.areEqual('12 Month', result[1].billingFrequency);
    }

    // ─── Synthetic-record helpers ───────────────────────────────────────────

    private static Integer seq = 0;

    private static Id mintBsgId() {
        seq++;
        String suffix = String.valueOf(seq);
        while (suffix.length() < 12) {
            suffix = '0' + suffix;
        }
        return Id.valueOf(BillingScheduleGroup.SObjectType.getDescribe().getKeyPrefix() + suffix);
    }

    // BillingScheduleGroup fields are not writeable on a constructed sObject, so build the
    // synthetic record via JSON to populate ProductName etc. for the assembly logic.
    private static BillingScheduleGroup synthBsg(Id id, String productName) {
        return synthBsg(id, productName, new Map<String, Object>());
    }

    // Same defaults as above, with the given fields overriding them.
    private static BillingScheduleGroup synthBsg(Id id, String productName, Map<String, Object> overrides) {
        Map<String, Object> m = new Map<String, Object>{
            'attributes'      => new Map<String, Object>{ 'type' => 'BillingScheduleGroup' },
            'Id'              => id,
            'ProductName'     => productName,
            'BillingMethod'   => 'Subscription',
            'BillingTermUnit' => 'Month',
            'BillingTerm'     => 1
        };
        m.putAll(overrides);
        return (BillingScheduleGroup) JSON.deserialize(JSON.serialize(m), BillingScheduleGroup.class);
    }

    // ─── Seams over queried rows ─────────────────────────────────────────────
    // Billing schedule groups, schedules and relationships cannot be inserted in Apex, and a
    // milestone plan needs a billing treatment, so these tests pass rows built with
    // JSON.deserialize to the methods the controller calls with the rows it queried. Billing
    // arrangements can be inserted, so that read runs against real records.

    private static Id fakeId(Schema.SObjectType objectType, Integer n) {
        return Id.valueOf(objectType.getDescribe().getKeyPrefix() + String.valueOf(n).leftPad(12, '0'));
    }

    private static BillingScheduleGroup bsg(Map<String, Object> fields) {
        return (BillingScheduleGroup) JSON.deserialize(JSON.serialize(fields), BillingScheduleGroup.class);
    }

    private static SObject row(String objectName, Map<String, Object> fields) {
        return (SObject) JSON.deserialize(JSON.serialize(fields), Type.forName(objectName));
    }

    // True when the org has no such object, by describe or as an Apex type; row() needs both.
    private static Boolean missing(String objectName) {
        return Schema.getGlobalDescribe().get(objectName) == null || Type.forName(objectName) == null;
    }

    // A usage group with no milestone and no bundle relationships is a usage view: its own
    // fields, its anchor, no siblings found; its billing arrangement is read (lines need a fully
    // set-up billing account to insert, so addArrangementLines_keepsTheQueryOrder covers them).
    @isTest
    static void fillContext_usageGroupWithAnArrangement() {
        BillingArrangement arrangement = new BillingArrangement(Name = 'RLM Split', Status = 'Draft');
        insert arrangement;
        Id groupId = fakeId(BillingScheduleGroup.SObjectType, 1);
        Id anchorId = fakeId(BillingScheduleGroup.SObjectType, 2);
        RLM_BSGContextController.BSGContext ctx = new RLM_BSGContextController.BSGContext();

        Test.startTest();
        RLM_BSGContextController.fillContext(ctx, bsg(new Map<String, Object>{
            'Id' => groupId, 'BillingScheduleGroupNumber' => 'BSG-0001', 'ProductName' => 'Data Plan',
            'BillingType' => 'Advance', 'BillingMethod' => 'Usage', 'BillingTermUnit' => 'Month',
            'BillingTerm' => 1, 'TotalBilledAmount' => 100, 'TotalPendingAmount' => 50,
            'AnchorProdtBillingSchdGrpId' => anchorId, 'BillingArrangementId' => arrangement.Id }));
        Test.stopTest();

        Assert.areEqual('usage', ctx.viewType, 'A usage group without a milestone or bundle is a usage view');
        Assert.areEqual('BSG-0001', ctx.bsgNumber, 'The group number is shown');
        Assert.areEqual('Data Plan', ctx.productName, 'The product is shown');
        Assert.areEqual(100, ctx.groupBilledAmount, 'Billed comes from the group');
        Assert.areEqual(50, ctx.groupPendingAmount, 'Pending comes from the group');
        Assert.isNull(ctx.milestonePlan, 'No milestone plan was found');
        Assert.isNull(ctx.bundle, 'No bundle relationships were found');
        Assert.areEqual(anchorId, ctx.usage.anchorBsgId, 'The anchor group is named');
        Assert.areEqual('BSG-0001', ctx.usage.currentBsgNumber, 'The current group is named');
        Assert.isTrue(ctx.usage.siblings.isEmpty(), 'No sibling groups exist');
        Assert.areEqual('RLM Split', ctx.arrangement.arrangementName, 'The arrangement is read');
        Assert.areEqual('Draft', ctx.arrangement.status, 'The arrangement status is read');
        Assert.areEqual(arrangement.Id, ctx.arrangement.arrangementId, 'The arrangement id is read');
        Assert.isTrue(ctx.arrangement.lines.isEmpty(), 'An arrangement without lines lists none');
    }

    // Arrangement lines: one row each in query order (the query sorts by share), with the line's
    // account name, share and remainder flag.
    @isTest
    static void addArrangementLines_keepsTheQueryOrder() {
        List<BillingArrangementLine> lines = new List<BillingArrangementLine>();
        for (List<Object> r : new List<List<Object>>{
            new List<Object>{ 'Line B', 'Payer', 60, true },
            new List<Object>{ 'Line A', 'Other', 40, false }
        }) {
            lines.add((BillingArrangementLine) row('BillingArrangementLine', new Map<String, Object>{
                'BillingArrangementLineName' => r[0], 'Account' => new Map<String, Object>{ 'Name' => r[1] },
                'BillingPercentage' => r[2], 'ShouldBillRemainder' => r[3] }));
        }
        List<RLM_BSGContextController.ArrangementLineData> target = new List<RLM_BSGContextController.ArrangementLineData>();

        Test.startTest();
        RLM_BSGContextController.addArrangementLines(target, lines);
        Test.stopTest();

        Assert.areEqual(new List<String>{ 'Line B', 'Line A' }, new List<String>{ target[0].lineName, target[1].lineName },
            'Lines keep the query order, not name order');
        Assert.areEqual('Payer', target[0].accountName, 'The line\'s account name is shown');
        Assert.areEqual(60, target[0].billingPercentage, 'The share is shown');
        Assert.isTrue(target[0].shouldBillRemainder, 'The remainder flag is shown');
        Assert.isFalse(target[1].shouldBillRemainder, 'Each line keeps its own flag');
    }

    // Smoke test: for a plan id that matches no plan, the plan lookup returns an empty plan and
    // does not throw. (A missing row and a swallowed error look the same from here.)
    @isTest
    static void getMilestonePlan_unknownPlanReturnsAnEmptyPlan() {
        Schema.SObjectType planType = Schema.getGlobalDescribe().get('BillingMilestonePlan');
        if (planType == null) {
            // No billing milestone objects in this org: the context never reads a plan here.
            return;
        }

        Test.startTest();
        RLM_BSGContextController.MilestonePlanData plan =
            RLM_BSGContextController.getMilestonePlan(fakeId(planType, 1), 100);
        Test.stopTest();

        Assert.isNull(plan.planId, 'No plan was found, so none is described');
        Assert.isNull(plan.items, 'No plan was found, so no items are read');
    }

    // A group that is neither milestone, bundle nor usage is a standard view, with no arrangement
    // when it has none.
    @isTest
    static void fillContext_plainGroupIsStandard() {
        RLM_BSGContextController.BSGContext ctx = new RLM_BSGContextController.BSGContext();

        Test.startTest();
        RLM_BSGContextController.fillContext(ctx, bsg(new Map<String, Object>{
            'Id' => fakeId(BillingScheduleGroup.SObjectType, 1), 'BillingMethod' => 'OrderAmount' }));
        Test.stopTest();

        Assert.areEqual('standard', ctx.viewType, 'A plain group falls back to the standard view');
        Assert.isNull(ctx.usage, 'Only a usage group gets usage data');
        Assert.isNull(ctx.arrangement, 'A group without an arrangement gets none');
    }

    // A group that is the main side of a relationship is the main bundle, even when it is also a
    // component of another group; it is described by its own charge type and frequency, and with
    // no child groups found it lists no components.
    @isTest
    static void getBundleData_mainSideIsTheMainBundle() {
        Id groupId = fakeId(BillingScheduleGroup.SObjectType, 1);
        BillingScheduleGroup current = bsg(new Map<String, Object>{
            'Id' => groupId, 'ProductName' => 'Suite', 'BillingTermUnit' => 'OneTime', 'BillingTerm' => 1 });
        BsgRelationship asMain = (BsgRelationship) row('BsgRelationship', new Map<String, Object>{
            'MainBsgId' => groupId, 'AssociatedBsgId' => fakeId(BillingScheduleGroup.SObjectType, 2) });
        BsgRelationship alsoComponent = (BsgRelationship) row('BsgRelationship', new Map<String, Object>{
            'MainBsgId' => fakeId(BillingScheduleGroup.SObjectType, 3), 'AssociatedBsgId' => groupId });

        Test.startTest();
        RLM_BSGContextController.BundleData bd = RLM_BSGContextController.getBundleData(
            groupId, current, new List<BsgRelationship>{ asMain }, new List<BsgRelationship>{ alsoComponent });
        Test.stopTest();

        Assert.isTrue(bd.isMainBundle, 'The main side is the main bundle, even as a component');
        Assert.areEqual('Suite', bd.mainBsgProduct, 'The root product is shown');
        Assert.areEqual('One-Time', bd.mainChargeType, 'A one-time term is a one-time charge');
        Assert.areEqual('One-Time', bd.mainBillingFrequency, 'A one-time term has a one-time frequency');
        Assert.isTrue(bd.components.isEmpty(), 'No child groups were found');
    }

    // A component group (no relationship where it is the main side) whose parent lookup finds
    // nothing for its fake id is its own root. (Had the lookup returned some other id, the root
    // query would find nothing and fall back to the group too, so this cannot tell those apart.)
    // getBundleData reads only whether asMain is empty, not asComponent.
    @isTest
    static void getBundleData_componentWithNoParentFoundIsItsOwnRoot() {
        Id groupId = fakeId(BillingScheduleGroup.SObjectType, 1);
        BillingScheduleGroup current = bsg(new Map<String, Object>{
            'Id' => groupId, 'ProductName' => 'Seat', 'BillingTermUnit' => 'Month', 'BillingTerm' => 3 });
        BsgRelationship asComponent = (BsgRelationship) row('BsgRelationship', new Map<String, Object>{
            'AssociatedBsgId' => groupId });

        Test.startTest();
        RLM_BSGContextController.BundleData bd = RLM_BSGContextController.getBundleData(
            groupId, current, new List<BsgRelationship>(), new List<BsgRelationship>{ asComponent });
        Test.stopTest();

        Assert.isFalse(bd.isMainBundle, 'A component is not the main bundle');
        Assert.areEqual(groupId, bd.mainBsgId, 'With no parent found, the group is its own root');
        Assert.areEqual('Evergreen', bd.mainChargeType, 'No end date is an evergreen charge');
        Assert.areEqual('3 Month', bd.mainBillingFrequency, 'The frequency is the term and its unit');
    }

    // The plan header takes the plan's own fields and the group's billed amount (zero when
    // blank); items keep their query order, with the accomplishment date as text.
    @isTest
    static void milestonePlanRows_fillTheHeaderAndItems() {
        if (missing('BillingMilestonePlanItem') || missing('BillingMilestonePlan')) {
            // No billing milestone objects in this org: the context never reads a plan here.
            return;
        }
        RLM_BSGContextController.MilestonePlanData plan = new RLM_BSGContextController.MilestonePlanData();
        RLM_BSGContextController.MilestonePlanData noBilled = new RLM_BSGContextController.MilestonePlanData();
        Id planId = fakeId(Schema.getGlobalDescribe().get('BillingMilestonePlan'), 1);
        SObject header = row('BillingMilestonePlan', new Map<String, Object>{
            'Id' => planId, 'Name' => 'Rollout', 'Status' => 'Active', 'Description' => 'Three phases',
            'ReferenceItemAmount' => 900 });
        Date done = Date.newInstance(2026, 3, 1);
        List<SObject> items = new List<SObject>{
            row('BillingMilestonePlanItem', new Map<String, Object>{ 'Name' => 'Kickoff', 'Type' => 'Percentage',
                'Percentage' => 30, 'MilestoneAmount' => 270, 'IsMilestoneAccomplished' => true,
                'MilestoneAccomplishmentDate' => done, 'Status' => 'Invoiced' }),
            row('BillingMilestonePlanItem', new Map<String, Object>{ 'Name' => 'Go-live', 'Type' => 'FlatAmount',
                'FlatAmount' => 630, 'MilestoneAmount' => 600, 'IsMilestoneAccomplished' => false })
        };
        List<RLM_BSGContextController.MilestoneItemData> target = new List<RLM_BSGContextController.MilestoneItemData>();

        Test.startTest();
        RLM_BSGContextController.fillPlanHeader(plan, header, 270);
        RLM_BSGContextController.fillPlanHeader(noBilled, header, null);
        RLM_BSGContextController.addMilestoneItems(target, items);
        Test.stopTest();

        Assert.areEqual(String.valueOf(planId), plan.planId, 'The plan id is shown');
        Assert.areEqual('Rollout', plan.planName, 'The plan name is shown');
        Assert.areEqual('Active', plan.planStatus, 'The plan status is shown');
        Assert.areEqual(900, plan.referenceAmount, 'The reference amount is shown');
        Assert.areEqual(270, plan.billedAmount, 'The billed amount comes from the group');
        Assert.areEqual(0, noBilled.billedAmount, 'A blank billed amount shows zero');
        Assert.areEqual(new List<String>{ 'Kickoff', 'Go-live' },
            new List<String>{ target[0].name, target[1].name }, 'Items keep their query order');
        Assert.areEqual(30, target[0].percentage, 'A percentage item keeps its percentage');
        Assert.isTrue(target[0].isAccomplished, 'The accomplished flag is shown, whatever the status');
        Assert.isFalse(target[1].isAccomplished, 'An open item is not accomplished');
        Assert.isTrue(target[0].accomplishmentDate != null && target[0].accomplishmentDate.startsWith('2026-03-01'),
            'The accomplishment date is shown as text starting with the date. Got: ' + target[0].accomplishmentDate);
        Assert.areEqual(630, target[1].flatAmount, 'A flat item keeps its flat amount');
        Assert.areEqual(600, target[1].milestoneAmount, 'A flat item keeps its milestone amount, separate from the flat one');
        Assert.isNull(target[1].accomplishmentDate, 'An open item has no accomplishment date');
    }

    // Sibling usage groups: one row each, with its resource, its billed amount (zero when
    // blank), and the current group marked.
    @isTest
    static void addUsageSiblings_marksTheCurrentGroup() {
        Id current = fakeId(BillingScheduleGroup.SObjectType, 1);
        Id sibling = fakeId(BillingScheduleGroup.SObjectType, 2);
        List<RLM_BSGContextController.UsageSiblingData> target = new List<RLM_BSGContextController.UsageSiblingData>();

        Test.startTest();
        RLM_BSGContextController.addUsageSiblings(target, new List<BillingScheduleGroup>{
            bsg(new Map<String, Object>{ 'Id' => sibling, 'BillingScheduleGroupNumber' => 'BSG-2', 'TotalBilledAmount' => 75 }),
            bsg(new Map<String, Object>{ 'Id' => current, 'BillingScheduleGroupNumber' => 'BSG-1' })
        }, new Map<Id, String>{ sibling => 'Minutes' }, current);
        Test.stopTest();

        Assert.areEqual(2, target.size(), 'One row per sibling group');
        Assert.areEqual('BSG-2', target[0].bsgNumber, 'Rows keep the query order');
        Assert.areEqual('Minutes', target[0].resourceName, 'A group\'s resource is shown');
        Assert.areEqual(75, target[0].billedAmount, 'A group\'s billed amount is shown');
        Assert.isFalse(target[0].isCurrent, 'Another group is not current');
        Assert.isNull(target[1].resourceName, 'A group without a resource shows none');
        Assert.areEqual(0, target[1].billedAmount, 'A blank billed amount shows zero');
        Assert.isTrue(target[1].isCurrent, 'The current group is marked');
    }

    // An arrangement id that matches no arrangement returns an empty arrangement.
    @isTest
    static void getArrangementData_unknownArrangementIsEmpty() {
        Test.startTest();
        RLM_BSGContextController.ArrangementData ad =
            RLM_BSGContextController.getArrangementData(fakeId(BillingArrangement.SObjectType, 1));
        Test.stopTest();

        Assert.isNull(ad.arrangementId, 'No arrangement was found, so none is described');
        Assert.isNull(ad.lines, 'No arrangement was found, so no lines are read');
    }

    // For a user who cannot read billing schedules, the milestone lookup finds no plan rather
    // than throwing. The premise is checked first.
    @isTest
    static void findMilestonePlanId_unreadableSchedulesFindNoPlan() {
        User u = RLM_BillingUITestUsers.create(new List<String>(), new List<String>());
        Boolean premise = false;
        Id found;

        Test.startTest();
        System.runAs(u) {
            try {
                Database.query('SELECT Id FROM BillingSchedule LIMIT 1', AccessLevel.USER_MODE);
            } catch (QueryException e) {
                premise = true;
            }
            found = RLM_BSGContextController.findMilestonePlanId(fakeId(BillingScheduleGroup.SObjectType, 1));
        }
        Test.stopTest();

        Assert.isTrue(premise, 'PRECONDITION: this user must be unable to read BillingSchedule');
        Assert.isNull(found, 'A refused lookup finds no plan instead of throwing');
    }

    // One hierarchy level: each child is listed under its parent in relationship order, and is
    // added to the next frontier and to all children.
    @isTest
    static void addRelationshipLevel_listsChildrenUnderTheirParent() {
        Id parentA = fakeId(BillingScheduleGroup.SObjectType, 1);
        Id parentB = fakeId(BillingScheduleGroup.SObjectType, 2);
        Id child1 = fakeId(BillingScheduleGroup.SObjectType, 3);
        Id child2 = fakeId(BillingScheduleGroup.SObjectType, 4);
        Id child3 = fakeId(BillingScheduleGroup.SObjectType, 5);
        List<BsgRelationship> rels = new List<BsgRelationship>();
        for (List<Id> pair : new List<List<Id>>{
            new List<Id>{ parentA, child2 }, new List<Id>{ parentB, child3 }, new List<Id>{ parentA, child1 }
        }) {
            rels.add((BsgRelationship) row('BsgRelationship', new Map<String, Object>{
                'MainBsgId' => pair[0], 'AssociatedBsgId' => pair[1] }));
        }
        Map<Id, List<Id>> parentToChildren = new Map<Id, List<Id>>();
        Set<Id> allChildIds = new Set<Id>();
        Set<Id> nextFrontier = new Set<Id>();

        Test.startTest();
        RLM_BSGContextController.addRelationshipLevel(rels, parentToChildren, allChildIds, nextFrontier);
        Test.stopTest();

        Assert.areEqual(new List<Id>{ child2, child1 }, parentToChildren.get(parentA),
            'A parent lists its children in relationship order');
        Assert.areEqual(new List<Id>{ child3 }, parentToChildren.get(parentB), 'Each parent gets its own children');
        Assert.areEqual(new Set<Id>{ child1, child2, child3 }, allChildIds, 'Every child is among all children');
        Assert.areEqual(new Set<Id>{ child1, child2, child3 }, nextFrontier, 'Every child is in the next frontier');
    }
}
