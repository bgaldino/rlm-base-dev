/**
 * @description Test class for RLM_UsageDataController. Validates error handling for invalid
 *              inputs and successful execution against each supported SObject with the
 *              RLM_UsageDatatable FieldSet.
 */
@IsTest
private class RLM_UsageDataControllerTest {

    @IsTest
    static void testGetFieldSetData_invalidObject() {
        Account acc = new Account(Name = 'Test Account');
        insert acc;

        try {
            RLM_UsageDataController.getFieldSetData(acc.Id, 'NonExistentObject__x', 'RLM_UsageDatatable');
            System.assert(false, 'Expected AuraHandledException for invalid SObject name');
        } catch (AuraHandledException e) {
            System.assert(e.getMessage().contains('Invalid SObject'), e.getMessage());
        }
    }

    @IsTest
    static void testGetFieldSetData_invalidFieldSet() {
        Account acc = new Account(Name = 'Test Account');
        insert acc;

        try {
            RLM_UsageDataController.getFieldSetData(acc.Id, 'TransactionJournal', 'NonExistentFieldSet');
            System.assert(false, 'Expected AuraHandledException for invalid FieldSet name');
        } catch (AuraHandledException e) {
            System.assert(e.getMessage().contains('Invalid FieldSet'), e.getMessage());
        }
    }

    @IsTest
    static void testGetFieldSetData_transactionJournal() {
        Account acc = new Account(Name = 'Test Account');
        insert acc;

        Map<String, Object> result = RLM_UsageDataController.getFieldSetData(
            acc.Id, 'TransactionJournal', 'RLM_UsageDatatable'
        );

        System.assertNotEquals(null, result, 'Result should not be null');
        System.assert(result.containsKey('columns'), 'Result should contain columns key');
        System.assert(result.containsKey('records'), 'Result should contain records key');
    }

    @IsTest
    static void testGetFieldSetData_usageSummary() {
        Account acc = new Account(Name = 'Test Account');
        insert acc;

        Map<String, Object> result = RLM_UsageDataController.getFieldSetData(
            acc.Id, 'UsageSummary', 'RLM_UsageDatatable'
        );

        System.assertNotEquals(null, result, 'Result should not be null');
        System.assert(result.containsKey('columns'), 'Result should contain columns key');
        System.assert(result.containsKey('records'), 'Result should contain records key');
    }

    @IsTest
    static void testGetFieldSetData_usageBillingPeriodItem() {
        Account acc = new Account(Name = 'Test Account');
        insert acc;

        Map<String, Object> result = RLM_UsageDataController.getFieldSetData(
            acc.Id, 'UsageBillingPeriodItem', 'RLM_UsageDatatable'
        );

        System.assertNotEquals(null, result, 'Result should not be null');
        System.assert(result.containsKey('columns'), 'Result should contain columns key');
        System.assert(result.containsKey('records'), 'Result should contain records key');
    }
}
