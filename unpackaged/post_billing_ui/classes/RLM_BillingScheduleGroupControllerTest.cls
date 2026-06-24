@isTest
private class RLM_BillingScheduleGroupControllerTest {

    // BillingScheduleGroup records are system-managed and not insertable in Apex tests, so a
    // null account and an Account with no BSGs both drive the query down its empty path.
    @isTest
    static void getBillingScheduleGroups_nullAccount_returnsEmptyList() {
        Test.startTest();
        List<RLM_BillingScheduleGroupController.BsgWrapper> result =
            RLM_BillingScheduleGroupController.getBillingScheduleGroups(null);
        Test.stopTest();
        System.assertNotEquals(null, result, 'A non-null list should always be returned.');
        System.assertEquals(0, result.size(), 'A null account id yields no billing schedule groups.');
    }

    @isTest
    static void getBillingScheduleGroups_accountWithNoBsgs_returnsEmptyList() {
        Account acc = new Account(Name = 'RLM BSG Controller Test');
        insert acc;

        Test.startTest();
        List<RLM_BillingScheduleGroupController.BsgWrapper> result =
            RLM_BillingScheduleGroupController.getBillingScheduleGroups(acc.Id);
        Test.stopTest();

        System.assertNotEquals(null, result, 'A non-null list should be returned.');
        System.assertEquals(0, result.size(), 'An account with no BSGs yields an empty list.');
    }
}
