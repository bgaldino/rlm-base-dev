@isTest
private class RLM_BillingScheduleGroupControllerTest {

    // BillingScheduleGroup records are system-managed and not insertable in Apex tests, so
    // these tests drive getBillingScheduleGroups down its empty and refused paths, and cover what
    // it does with found groups through the seams that take rows (wrappersWithRelationships,
    // buildWrappers). Each System.runAs
    // test creates its user through RLM_BillingUITestUsers; the billing-role tests take a
    // Billing permission set license seat each, the refused-access test (a plain Minimum Access
    // user with no permission set license) does not.

    // A billing role can run the BSG query. For an account with no BSGs and for a null account
    // id it gets empty lists, because no BSGs can exist in tests (the controller has no null
    // guard). Beyond RLM_BillingUIAccessTest, it shows the real controller call succeeds for
    // the role and returns the expected (empty list) shape.
    @isTest
    static void getBillingScheduleGroups_billingRole_noBsgsOrNullAccount_returnsEmptyList() {
        Account acc = new Account(Name = 'RLM BSG Controller Role Test');
        insert acc;
        User u = RLM_BillingUITestUsers.create(
            new List<String>{ 'RLM_BillingUI', 'RevenueLifecycleManagementBillingOperations' },
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL });

        List<RLM_BillingScheduleGroupController.BsgWrapper> result;
        List<RLM_BillingScheduleGroupController.BsgWrapper> nullAccountResult;
        Test.startTest();
        System.runAs(u) {
            result = RLM_BillingScheduleGroupController.getBillingScheduleGroups(acc.Id);
            nullAccountResult = RLM_BillingScheduleGroupController.getBillingScheduleGroups(null);
        }
        Test.stopTest();

        Assert.isNotNull(result, 'A billing role gets a list, not an error.');
        Assert.isTrue(result.isEmpty(), 'An account with no BSGs yields an empty list.');
        Assert.isNotNull(nullAccountResult, 'A null account id returns a list, not null or an error.');
        Assert.isTrue(nullAccountResult.isEmpty(), 'A null account id yields an empty list (no BSGs can exist in tests).');
    }

    // A Minimum Access user with no permission sets cannot read BillingScheduleGroup. The
    // refused USER_MODE query must reach the LWC as an AuraHandledException, not a raw
    // QueryException. The premise is checked first.
    @isTest
    static void getBillingScheduleGroups_userWithoutBsgAccess_throwsHandledException() {
        Account acc = new Account(Name = 'RLM BSG Controller No Access Test');
        insert acc;
        User u = RLM_BillingUITestUsers.create(
            new List<String>(), new List<String>());

        Boolean premise = false;
        Exception thrown;
        Test.startTest();
        System.runAs(u) {
            try {
                Database.query('SELECT Id FROM BillingScheduleGroup LIMIT 1', AccessLevel.USER_MODE);
            } catch (QueryException e) {
                premise = true;
            }
            try {
                RLM_BillingScheduleGroupController.getBillingScheduleGroups(acc.Id);
            } catch (Exception e) {
                thrown = e;
            }
        }
        Test.stopTest();

        Assert.isTrue(premise, 'PRECONDITION: this user must be unable to read BillingScheduleGroup.');
        Assert.isNotNull(thrown, 'A refused read must not come back as an empty list.');
        Assert.isInstanceOfType(thrown, AuraHandledException.class,
            'The refused read is wrapped for the LWC, got ' + thrown.getTypeName());
        Assert.areEqual(RLM_BillingScheduleGroupController.LOAD_FAILED_MESSAGE, thrown.getMessage(),
            'The LWC gets a fixed sentence, not the query error');
        Assert.isInstanceOfType(thrown.getCause(), QueryException.class, 'The query error is kept as the cause');
    }

    @isTest
    static void bsgWrapper_startsWithAnEmptyRelationshipList() {
        RLM_BillingScheduleGroupController.BsgWrapper wrapper =
            new RLM_BillingScheduleGroupController.BsgWrapper();
        Assert.isNotNull(wrapper.relationships, 'Relationships default to an empty list, never null.');
        Assert.isTrue(wrapper.relationships.isEmpty());
        Assert.isNull(wrapper.bsg, 'No BSG until one is assigned.');
    }

    // Groups and relationships cannot be inserted in Apex, so these pass rows built with
    // JSON.deserialize to the methods the controller calls after its group query.
    private static Id fakeId(Schema.SObjectType objectType, Integer n) {
        return Id.valueOf(objectType.getDescribe().getKeyPrefix() + String.valueOf(n).leftPad(12, '0'));
    }

    private static BillingScheduleGroup bsg(Id id, String productName) {
        return (BillingScheduleGroup) JSON.deserialize(JSON.serialize(new Map<String, Object>{
            'Id' => id, 'ProductName' => productName }), BillingScheduleGroup.class);
    }

    private static BsgRelationship relationship(Id id, Id mainId, Id associatedId) {
        return (BsgRelationship) JSON.deserialize(JSON.serialize(new Map<String, Object>{
            'Id' => id, 'MainBsgId' => mainId, 'AssociatedBsgId' => associatedId }), BsgRelationship.class);
    }

    // One wrapper per group in the groups' order, each with the relationships where it is the
    // main group, in their order; a group with none gets an empty list, and a relationship whose
    // main group is not listed is left out.
    @isTest
    static void buildWrappers_attachesEachGroupsMainRelationships() {
        Id groupA = fakeId(BillingScheduleGroup.SObjectType, 1);
        Id groupB = fakeId(BillingScheduleGroup.SObjectType, 2);
        Id groupC = fakeId(BillingScheduleGroup.SObjectType, 3);
        Id unlisted = fakeId(BillingScheduleGroup.SObjectType, 4);
        Id relA1 = fakeId(BsgRelationship.SObjectType, 1);
        Id relA2 = fakeId(BsgRelationship.SObjectType, 2);
        Id relB = fakeId(BsgRelationship.SObjectType, 3);

        Test.startTest();
        List<RLM_BillingScheduleGroupController.BsgWrapper> wrappers = RLM_BillingScheduleGroupController.buildWrappers(
            new List<BillingScheduleGroup>{ bsg(groupB, 'Beta'), bsg(groupA, 'Alpha'), bsg(groupC, 'Gamma') },
            new List<BsgRelationship>{
                relationship(relA2, groupA, groupC),
                relationship(relB, groupB, groupA),
                relationship(fakeId(BsgRelationship.SObjectType, 4), unlisted, groupA),
                relationship(relA1, groupA, groupB)
            });
        Test.stopTest();

        Assert.areEqual(3, wrappers.size(), 'One wrapper per group');
        Assert.areEqual(groupB, wrappers[0].bsg.Id, 'Groups keep their query order, not name order');
        Assert.areEqual('Beta', wrappers[0].bsg.ProductName, 'The group row is passed through');
        Assert.areEqual(new List<Id>{ relB }, idsOf(wrappers[0].relationships), 'B gets only its own relationship');
        Assert.areEqual(new List<Id>{ relA2, relA1 }, idsOf(wrappers[1].relationships),
            'A gets both of its relationships, in their order');
        Assert.isNotNull(wrappers[2].relationships, 'A group without relationships gets a list, not null');
        Assert.isTrue(wrappers[2].relationships.isEmpty(), 'A group without relationships gets an empty list');
    }

    private static List<Id> idsOf(List<BsgRelationship> rels) {
        List<Id> ids = new List<Id>();
        for (BsgRelationship r : rels) {
            ids.add(r.Id);
        }
        return ids;
    }

    // The billing user can run the relationship query, and it runs once for all the groups.
    // (What the rows become is checked in buildWrappers_attachesEachGroupsMainRelationships.)
    @isTest
    static void wrappersWithRelationships_runsTheRelationshipQueryOnce() {
        User u = RLM_BillingUITestUsers.create(
            new List<String>{ 'RLM_BillingUI', 'RevenueLifecycleManagementBillingOperations' },
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL });
        List<BillingScheduleGroup> groups = new List<BillingScheduleGroup>{
            bsg(fakeId(BillingScheduleGroup.SObjectType, 1), 'Alpha'),
            bsg(fakeId(BillingScheduleGroup.SObjectType, 2), 'Beta')
        };
        Integer ran;
        List<RLM_BillingScheduleGroupController.BsgWrapper> wrappers;

        Test.startTest();
        System.runAs(u) {
            Integer before = Limits.getQueries();
            wrappers = RLM_BillingScheduleGroupController.wrappersWithRelationships(groups);
            ran = Limits.getQueries() - before;
        }
        Test.stopTest();

        Assert.areEqual(1, ran, 'The relationship query runs once for all the groups');
        Assert.areEqual(2, wrappers.size(), 'One wrapper per group');
    }
}
