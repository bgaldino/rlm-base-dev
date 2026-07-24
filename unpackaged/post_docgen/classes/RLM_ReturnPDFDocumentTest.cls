@IsTest
private class RLM_ReturnPDFDocumentTest {
    @IsTest
    static void testReturnPDFDocumentFindsThePdf() {
        ContentVersion cvPdf = new ContentVersion(
            Title = 'Proposal',
            PathOnClient = 'Proposal.pdf',
            VersionData = Blob.valueOf('fake pdf bytes')
        );
        insert cvPdf;

        cvPdf = [SELECT Id, ContentDocumentId FROM ContentVersion WHERE Id = :cvPdf.Id];

        RLM_ReturnPDFDocument.InputVariable input = new RLM_ReturnPDFDocument.InputVariable();
        input.ResponseText = cvPdf.Id;

        Test.startTest();
        List<RLM_ReturnPDFDocument.OutputVariable> results =
            RLM_ReturnPDFDocument.ReturnPDFDocumentId(new List<RLM_ReturnPDFDocument.InputVariable>{ input });
        Test.stopTest();

        System.assertEquals(1, results.size());
        System.assertEquals(cvPdf.ContentDocumentId, results[0].ContentDocumentId);
        System.assertEquals(cvPdf.Id, results[0].ContentVersionId);
    }

    @IsTest
    static void testReturnPDFDocumentCsvInput() {
        ContentVersion cvWord = new ContentVersion(
            Title = 'Proposal',
            PathOnClient = 'Proposal.docx',
            VersionData = Blob.valueOf('fake word bytes')
        );
        ContentVersion cvPdf = new ContentVersion(
            Title = 'Proposal',
            PathOnClient = 'Proposal.pdf',
            VersionData = Blob.valueOf('fake pdf bytes')
        );
        insert new List<ContentVersion>{ cvWord, cvPdf };

        cvPdf = [SELECT Id, ContentDocumentId FROM ContentVersion WHERE Id = :cvPdf.Id];
        cvWord = [SELECT Id FROM ContentVersion WHERE Id = :cvWord.Id];

        RLM_ReturnPDFDocument.InputVariable input = new RLM_ReturnPDFDocument.InputVariable();
        input.ResponseText = cvWord.Id + ',' + cvPdf.Id;

        Test.startTest();
        List<RLM_ReturnPDFDocument.OutputVariable> results =
            RLM_ReturnPDFDocument.ReturnPDFDocumentId(new List<RLM_ReturnPDFDocument.InputVariable>{ input });
        Test.stopTest();

        System.assertEquals(1, results.size());
        System.assertEquals(cvPdf.Id, results[0].ContentVersionId, 'Should return the PDF, not the Word doc');
    }

    @IsTest
    static void testReturnPDFDocumentBlankInput() {
        RLM_ReturnPDFDocument.InputVariable input = new RLM_ReturnPDFDocument.InputVariable();
        input.ResponseText = '';

        List<RLM_ReturnPDFDocument.OutputVariable> results =
            RLM_ReturnPDFDocument.ReturnPDFDocumentId(new List<RLM_ReturnPDFDocument.InputVariable>{ input });

        System.assertEquals(1, results.size());
        System.assertEquals(null, results[0].ContentDocumentId, 'Blank input should return null');
        System.assertEquals(null, results[0].ContentVersionId);
    }

    @IsTest
    static void testReturnPDFDocumentMalformedId() {
        RLM_ReturnPDFDocument.InputVariable input = new RLM_ReturnPDFDocument.InputVariable();
        input.ResponseText = 'not-a-valid-id,also-garbage';

        List<RLM_ReturnPDFDocument.OutputVariable> results =
            RLM_ReturnPDFDocument.ReturnPDFDocumentId(new List<RLM_ReturnPDFDocument.InputVariable>{ input });

        System.assertEquals(1, results.size());
        System.assertEquals(null, results[0].ContentDocumentId, 'Malformed IDs should return null gracefully');
    }

    @IsTest
    static void testReturnPDFDocumentNullRequestThrows() {
        Boolean threw = false;
        try {
            RLM_ReturnPDFDocument.ReturnPDFDocumentId(null);
        } catch (IllegalArgumentException e) {
            threw = true;
        }
        System.assert(threw, 'Should throw on null input');
    }
}
