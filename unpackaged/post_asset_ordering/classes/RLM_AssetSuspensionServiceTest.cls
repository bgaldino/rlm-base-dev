/**
 * Tests for RLM_AssetSuspensionService and RLM_AssetResumeScheduler. The native
 * blngSvcSuspendBilling invocation is replaced with the @TestVisible mock seam;
 * the custom-status DML and the scheduler flip run against real Asset records.
 */
@IsTest
private class RLM_AssetSuspensionServiceTest {

    @TestSetup
    static void setup() {
        Account a = new Account(Name = 'Suspend Acct');
        insert a;
        insert new Asset(Name = 'Suspend Asset', AccountId = a.Id);
    }

    private static Id assetId() {
        return [SELECT Id FROM Asset WHERE Name = 'Suspend Asset' LIMIT 1].Id;
    }

    @IsTest
    static void suspend_success_setsStatus() {
        RLM_AssetSuspensionService.mockSuspendOutcome =
            new RLM_AssetSuspensionService.SuspendOutcome(); // default success
        Test.startTest();
        RLM_AssetSuspensionService.SuspensionResult res =
            RLM_AssetSuspensionService.suspend(
                new List<Id>{ assetId() }, Date.today(), Date.today().addMonths(1));
        Test.stopTest();
        System.assert(res.isSuccess, 'Expected success');
        System.assertEquals(1, res.assetsUpdated);
        Asset a = [SELECT RLM_Asset_Status__c, RLM_Suspension_Resume_Date__c FROM Asset WHERE Id = :assetId()];
        System.assertEquals('Suspended', a.RLM_Asset_Status__c);
        System.assertEquals(Date.today().addMonths(1), a.RLM_Suspension_Resume_Date__c);
    }

    @IsTest
    static void suspend_guards() {
        RLM_AssetSuspensionService.SuspensionResult noAssets =
            RLM_AssetSuspensionService.suspend(new List<Id>(), Date.today(), Date.today().addDays(5));
        System.assert(!noAssets.isSuccess);

        RLM_AssetSuspensionService.SuspensionResult noResume =
            RLM_AssetSuspensionService.suspend(new List<Id>{ assetId() }, Date.today(), null);
        System.assert(!noResume.isSuccess, 'Missing resumption date should fail');
    }

    @IsTest
    static void suspend_nativeFailurePropagates() {
        RLM_AssetSuspensionService.SuspendOutcome bad =
            new RLM_AssetSuspensionService.SuspendOutcome();
        bad.isSuccess = false;
        bad.info = 'billing locked';
        RLM_AssetSuspensionService.mockSuspendOutcome = bad;
        Test.startTest();
        RLM_AssetSuspensionService.SuspensionResult res =
            RLM_AssetSuspensionService.suspend(
                new List<Id>{ assetId() }, Date.today(), Date.today().addMonths(1));
        Test.stopTest();
        System.assert(!res.isSuccess, 'Native failure should fail the result');
    }

    @IsTest
    static void resume_setsActive() {
        // First suspend, then resume.
        RLM_AssetSuspensionService.mockSuspendOutcome =
            new RLM_AssetSuspensionService.SuspendOutcome();
        RLM_AssetSuspensionService.suspend(
            new List<Id>{ assetId() }, Date.today(), Date.today().addMonths(1));
        Test.startTest();
        RLM_AssetSuspensionService.SuspensionResult res =
            RLM_AssetSuspensionService.resume(new List<Id>{ assetId() });
        Test.stopTest();
        System.assert(res.isSuccess);
        Asset a = [SELECT RLM_Asset_Status__c FROM Asset WHERE Id = :assetId()];
        System.assertEquals('Active', a.RLM_Asset_Status__c);
    }

    @IsTest
    static void suspend_noMatchingAssets() {
        RLM_AssetSuspensionService.mockSuspendOutcome =
            new RLM_AssetSuspensionService.SuspendOutcome();
        // A syntactically valid Asset id that matches no record.
        Id ghost = Id.valueOf('02i' + '000000000001'.leftPad(12, '0'));
        RLM_AssetSuspensionService.SuspensionResult res =
            RLM_AssetSuspensionService.suspend(
                new List<Id>{ ghost }, Date.today(), Date.today().addMonths(1));
        System.assert(!res.isSuccess, 'No matching assets should fail');
        System.assert(
            res.messages.contains('No matching assets.'),
            'Expected no-matching-assets message');
    }

    @IsTest
    static void resume_guardsEmpty() {
        RLM_AssetSuspensionService.SuspensionResult res =
            RLM_AssetSuspensionService.resume(new List<Id>());
        System.assert(!res.isSuccess, 'Empty resume selection should fail');
    }

    @IsTest
    static void scheduler_resumesDueAssets() {
        Asset a = [SELECT Id FROM Asset WHERE Name = 'Suspend Asset' LIMIT 1];
        a.RLM_Asset_Status__c = 'Suspended';
        a.RLM_Suspension_Resume_Date__c = Date.today().addDays(-1);
        update a;

        Test.startTest();
        Integer flipped = RLM_AssetResumeScheduler.resumeDueAssets();
        new RLM_AssetResumeScheduler().execute(null); // cover Schedulable entry
        Test.stopTest();

        System.assertEquals(1, flipped, 'One due asset flipped');
        Asset after1 = [SELECT RLM_Asset_Status__c FROM Asset WHERE Id = :a.Id];
        System.assertEquals('Active', after1.RLM_Asset_Status__c);
    }
}
