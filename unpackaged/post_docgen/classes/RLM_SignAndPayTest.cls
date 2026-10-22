@IsTest
private class RLM_SignAndPayTest {
    @IsTest
    static void accept_stampsDemoFields() {
        Account account = new Account(Name = 'Sign Pay Test Account');
        insert account;
        Opportunity opportunity = new Opportunity(
            Name = 'Sign Pay Opp',
            StageName = 'Prospecting',
            CloseDate = Date.today().addDays(30),
            AccountId = account.Id
        );
        insert opportunity;
        Quote quoteRecord = new Quote(
            Name = 'Sign Pay Quote',
            OpportunityId = opportunity.Id,
            Pricebook2Id = Test.getStandardPricebookId()
        );
        insert quoteRecord;

        ContentVersion version = new ContentVersion(
            Title = 'RLM Quote Proposal',
            PathOnClient = 'proposal.pdf',
            VersionData = Blob.valueOf('%PDF-1.4 demo'),
            IsMajorVersion = true
        );
        insert version;
        version = [SELECT ContentDocumentId FROM ContentVersion WHERE Id = :version.Id];
        insert new ContentDocumentLink(
            ContentDocumentId = version.ContentDocumentId,
            LinkedEntityId = quoteRecord.Id,
            ShareType = 'V',
            Visibility = 'AllUsers'
        );

        Test.startTest();
        RLM_SignAndPay.QuoteContext ctx = RLM_SignAndPay.loadContext(quoteRecord.Id, null);
        System.assertNotEquals(null, ctx.proposal, 'Expected proposal document');
        RLM_SignAndPay.AcceptResponse res = RLM_SignAndPay.accept(
            quoteRecord.Id,
            ctx.proposal.contentDocumentId,
            'Michael Reyes',
            '4242',
            'Visa'
        );
        Test.stopTest();

        System.assertEquals(true, res.success, res.message);
        Quote updated = [
            SELECT RLM_Demo_Signed_By__c, RLM_Demo_Card_Last4__c, RLM_Demo_Signed_Document_Id__c
            FROM Quote
            WHERE Id = :quoteRecord.Id
        ];
        System.assertEquals('Michael Reyes', updated.RLM_Demo_Signed_By__c);
        System.assertEquals('4242', updated.RLM_Demo_Card_Last4__c);
        System.assertEquals(String.valueOf(ctx.proposal.contentDocumentId), updated.RLM_Demo_Signed_Document_Id__c);
    }
}
