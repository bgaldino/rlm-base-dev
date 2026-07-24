@IsTest
private class RLM_SaveQuoteDocumentTest {
    @IsTest
    static void testSaveAsQuotePdf() {
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

        ContentVersion cv = new ContentVersion(
            Title = 'TestProposal',
            PathOnClient = 'TestProposal.pdf',
            VersionData = Blob.valueOf('fake pdf content')
        );
        insert cv;

        cv = [SELECT Id, ContentDocumentId FROM ContentVersion WHERE Id = :cv.Id];
        Id sourceDocId = cv.ContentDocumentId;

        RLM_SaveQuoteDocument.InputVariable input = new RLM_SaveQuoteDocument.InputVariable();
        input.QuoteId = q.Id;
        input.ContentVersionId = cv.Id;

        Test.startTest();
        List<RLM_SaveQuoteDocument.OutputVariable> results =
            RLM_SaveQuoteDocument.saveAsQuotePdf(new List<RLM_SaveQuoteDocument.InputVariable>{ input });
        Test.stopTest();

        System.assertEquals(1, results.size(), 'Expected one output');
        RLM_SaveQuoteDocument.OutputVariable result = results[0];
        System.assertNotEquals(null, result.QuoteDocumentId, 'QuoteDocumentId should be populated');
        System.assertNotEquals(null, result.NewContentDocumentId, 'NewContentDocumentId should be populated');

        QuoteDocument qd = [SELECT Id, QuoteId, Status FROM QuoteDocument WHERE Id = :result.QuoteDocumentId];
        System.assertEquals(q.Id, qd.QuoteId);
        System.assertEquals('Completed', qd.Status);

        List<ContentDocument> remaining = [SELECT Id FROM ContentDocument WHERE Id = :sourceDocId];
        System.assertEquals(0, remaining.size(), 'Source ContentDocument should be deleted');
    }
}
