@IsTest
private class RLM_DocumentGenerationMergeTest {
    @IsTest
    static void testMergeDocumentsHappyPath() {
        Account acc = new Account(Name = 'Test Account');
        insert acc;

        Opportunity opp = new Opportunity(
            Name = 'Test Opp',
            AccountId = acc.Id,
            StageName = 'Prospecting',
            CloseDate = Date.today().addDays(30)
        );
        insert opp;

        Quote q = new Quote(Name = 'Test Quote', OpportunityId = opp.Id);
        insert q;

        ContentVersion cv1 = new ContentVersion(
            Title = 'Doc1',
            PathOnClient = 'Doc1.pdf',
            VersionData = Blob.valueOf('pdf1')
        );
        ContentVersion cv2 = new ContentVersion(
            Title = 'Doc2',
            PathOnClient = 'Doc2.pdf',
            VersionData = Blob.valueOf('pdf2')
        );
        insert new List<ContentVersion>{ cv1, cv2 };

        List<ContentVersion> inserted = [SELECT Id FROM ContentVersion WHERE Id IN (:cv1.Id, :cv2.Id)];

        RLM_DocumentGenerationMerge.Request req = new RLM_DocumentGenerationMerge.Request();
        req.CurrentRecordId = q.Id;
        req.recordIds = new List<Id>{ inserted[0].Id, inserted[1].Id };
        req.DocTitle = 'Merged Proposal';

        Test.startTest();
        List<RLM_DocumentGenerationMerge.Response> results =
            RLM_DocumentGenerationMerge.MergeDocuments(new List<RLM_DocumentGenerationMerge.Request>{ req });
        Test.stopTest();

        System.assertEquals(1, results.size(), 'Expected one response');
        System.assertNotEquals(null, results[0].MergedRecordId, 'DGP Id should be returned');

        DocumentGenerationProcess dgp = [
            SELECT Id, Type, Status, DocGenApiVersionType, PdfDocIdentifiersList, ReferenceObject
            FROM DocumentGenerationProcess
            WHERE Id = :results[0].MergedRecordId
        ];
        System.assertEquals('MergePDF', dgp.Type);
        System.assertEquals('InProgress', dgp.Status);
        System.assertEquals('Advanced', dgp.DocGenApiVersionType);
        System.assertEquals(String.valueOf(q.Id), dgp.ReferenceObject);
        System.assert(dgp.PdfDocIdentifiersList.contains(String.valueOf(inserted[0].Id)));
        System.assert(dgp.PdfDocIdentifiersList.contains(String.valueOf(inserted[1].Id)));
    }

    @IsTest
    static void testMergeDocumentsNullRequestThrows() {
        Boolean threw = false;
        try {
            RLM_DocumentGenerationMerge.MergeDocuments(null);
        } catch (IllegalArgumentException e) {
            threw = true;
            System.assert(e.getMessage().contains('at least one request is required'));
        }
        System.assert(threw, 'Should throw on null input');
    }

    @IsTest
    static void testMergeDocumentsEmptyRecordIdsThrows() {
        Account acc = new Account(Name = 'Test Account');
        insert acc;
        Opportunity opp = new Opportunity(
            Name = 'Test Opp',
            AccountId = acc.Id,
            StageName = 'Prospecting',
            CloseDate = Date.today().addDays(30)
        );
        insert opp;
        Quote q = new Quote(Name = 'Test Quote', OpportunityId = opp.Id);
        insert q;

        RLM_DocumentGenerationMerge.Request req = new RLM_DocumentGenerationMerge.Request();
        req.CurrentRecordId = q.Id;
        req.recordIds = new List<Id>();
        req.DocTitle = 'Empty Merge';

        Boolean threw = false;
        try {
            RLM_DocumentGenerationMerge.MergeDocuments(new List<RLM_DocumentGenerationMerge.Request>{ req });
        } catch (IllegalArgumentException e) {
            threw = true;
            System.assert(e.getMessage().contains('at least one non-null Id'));
        }
        System.assert(threw, 'Should throw when recordIds is empty');
    }
}
