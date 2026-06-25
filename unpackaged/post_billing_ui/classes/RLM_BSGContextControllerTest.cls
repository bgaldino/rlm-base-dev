@isTest
private class RLM_BSGContextControllerTest {

    // BillingScheduleGroup is system-managed and not insertable in Apex tests, so coverage
    // exercises the id-validation and "no matching record" paths, which always run and are
    // exactly the branches hardened in M1 (Id.valueOf guard + empty-list guard + try/catch).
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
        System.assertEquals('Usage',
            RLM_BSGContextController.deriveChargeType('Usage', 'Months', null));
        System.assertEquals('One-Time',
            RLM_BSGContextController.deriveChargeType('Subscription', 'OneTime', null));
        System.assertEquals('Evergreen',
            RLM_BSGContextController.deriveChargeType('Subscription', 'Months', null));
        System.assertEquals('Termed Subscription',
            RLM_BSGContextController.deriveChargeType('Subscription', 'Months', Date.today().addDays(30)));
    }

    @isTest
    static void formatFrequency_coversBranches() {
        System.assertEquals('One-Time', RLM_BSGContextController.formatFrequency(1, 'OneTime'));
        System.assertEquals('1 Months', RLM_BSGContextController.formatFrequency(1, 'Months'));
        System.assertEquals('1 ', RLM_BSGContextController.formatFrequency(null, null));
    }

    // ─── M3 BFS-assembly coverage (the rewritten collectChildComponents path) ──

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
        Map<String, Object> m = new Map<String, Object>{
            'attributes'      => new Map<String, Object>{ 'type' => 'BillingScheduleGroup' },
            'Id'              => id,
            'ProductName'     => productName,
            'BillingMethod'   => 'Subscription',
            'BillingTermUnit' => 'Months',
            'BillingTerm'     => 1
        };
        return (BillingScheduleGroup) JSON.deserialize(JSON.serialize(m), BillingScheduleGroup.class);
    }
}
