@isTest
private class RLM_BSGContextControllerTest {

    // Tests for RLM_BSGContextController. BillingScheduleGroup, BillingSchedule and
    // BsgRelationship cannot be inserted in Apex tests, so getBSGContext is covered only on
    // the paths that need no BSG: a malformed or null id, an id matching no BSG, and a BSG
    // query the user may not run. The admin-run unknown-id test
    // (getBSGContext_unknownId_returnsEmptyStandard) reaches "not found or refused"
    // (indistinguishable when run as the admin).
    // The bundle assembly (appendComponentsDfs) is covered with in-memory BSGs; the
    // charge-type / frequency helpers are called directly with plain inputs.
    // The refused-access test runs as a plain Minimum Access user with no permission set
    // license (no Billing PSL seat); billing-role read coverage for the controller's fields is
    // in RLM_BillingUIAccessTest (billingOperationsCanRunItsControllerReads).
    //
    // Known gap (documented, not pinned; needs BSG records): getBSGContext reads
    // bsBilledAmount and bsPendingAmount from one arbitrary BillingSchedule of the group
    // (LIMIT 1, no ORDER BY), and the usage view's resource name likewise comes from one
    // arbitrary schedule. Each usage sibling's resource name is also taken from whichever of
    // its schedules the unordered query returns last (the last row wins). With several
    // schedules the values shown are nondeterministic.
    //
    // Known gap (documented, not pinned; needs BSG records):
    // ArrangementLineData.billingAccountName is never set. The arrangement-line query selects
    // BillingAccountId but the controller never maps it, so the field always reaches the LWC
    // as null.
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

    // A cycle back to the root: collectChildComponents passes every parent in the map as a
    // sub-bundle (the main BSG included) and starts with nothing emitted, so main -> a -> main
    // emits the main BSG as a component of itself, at depth 2.
    @isTest
    static void appendComponentsDfs_cycleToRoot_emitsTheMainBsgAsItsOwnComponent() {
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
            result, new Set<Id>()
        );

        Assert.areEqual(2, result.size(),
            'Known gap: a cycle back to the root emits the main BSG as its own component; update '
            + 'this test when it is fixed.');
        Assert.areEqual(a, result[0].bsgId);
        Assert.areEqual(mainId, result[1].bsgId, 'The main BSG is emitted below its own child.');
        Assert.areEqual(2, result[1].depth);
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
}
