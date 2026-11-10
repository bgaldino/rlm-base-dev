@isTest
private class RLM_BillingScheduleGroupControllerTest {

    // BillingScheduleGroup records are system-managed and not insertable in Apex tests, so
    // these tests drive the query down its empty and refused paths only. Each System.runAs
    // test creates its user through RLM_BillingUITestUsers, which takes a Billing permission
    // set license seat.
    @isTest
    static void getBillingScheduleGroups_nullAccount_returnsEmptyList() {
        Test.startTest();
        List<RLM_BillingScheduleGroupController.BsgWrapper> result =
            RLM_BillingScheduleGroupController.getBillingScheduleGroups(null);
        Test.stopTest();
        System.assertNotEquals(null, result, 'A non-null list should always be returned.');
        System.assertEquals(0, result.size(), 'A null account id yields no billing schedule groups.');
    }

    // A billing role can run the BSG query, so an account with no BSGs must come back as an
    // empty list.
    @isTest
    static void getBillingScheduleGroups_billingRole_accountWithNoBsgs_returnsEmptyList() {
        Account acc = new Account(Name = 'RLM BSG Controller Role Test');
        insert acc;
        User u = RLM_BillingUITestUsers.create(
            new List<String>{ 'RLM_BillingUI', 'RevenueLifecycleManagementBillingOperations' },
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL });

        List<RLM_BillingScheduleGroupController.BsgWrapper> result;
        Test.startTest();
        System.runAs(u) {
            result = RLM_BillingScheduleGroupController.getBillingScheduleGroups(acc.Id);
        }
        Test.stopTest();

        Assert.isNotNull(result, 'A billing role gets a list, not an error.');
        Assert.isTrue(result.isEmpty(), 'An account with no BSGs yields an empty list.');
    }

    // A Billing-licensed user with only RLM_BillingUI cannot read BillingScheduleGroup. The
    // refused USER_MODE query must reach the LWC as an AuraHandledException, not a raw
    // QueryException. The premise is checked first.
    @isTest
    static void getBillingScheduleGroups_userWithoutBsgAccess_throwsHandledException() {
        Account acc = new Account(Name = 'RLM BSG Controller No Access Test');
        insert acc;
        User u = RLM_BillingUITestUsers.create(
            new List<String>{ 'RLM_BillingUI' },
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL });

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
    }

    @isTest
    static void bsgWrapper_startsWithAnEmptyRelationshipList() {
        RLM_BillingScheduleGroupController.BsgWrapper wrapper =
            new RLM_BillingScheduleGroupController.BsgWrapper();
        Assert.isNotNull(wrapper.relationships, 'Relationships default to an empty list, never null.');
        Assert.isTrue(wrapper.relationships.isEmpty());
        Assert.isNull(wrapper.bsg, 'No BSG until one is assigned.');
    }
}
