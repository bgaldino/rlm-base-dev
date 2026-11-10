/**
 * Tests for RLM_ReturnPDFDocument: picks the PDF out of the comma-separated
 * ContentVersion ids a DocumentGenerationProcess writes to ResponseText.
 */
@IsTest
private class RLM_ReturnPDFDocumentTest {

    // DocGen writes the .docx and the .pdf; ResponseText carries 15-character
    // ContentVersion ids. The PDF's ContentDocument and ContentVersion come back,
    // and blank or malformed tokens are skipped rather than failing the request.
    @IsTest
    static void returnsThePdfAmongTheGeneratedFiles() {
        ContentVersion word = newVersion('Proposal.docx');
        ContentVersion pdf = newVersion('Proposal.pdf');
        insert new List<ContentVersion>{ word, pdf };
        pdf = [SELECT Id, ContentDocumentId, FileType FROM ContentVersion WHERE Id = :pdf.Id];
        Assert.areEqual('PDF', pdf.FileType, 'PRECONDITION: a .pdf path yields FileType PDF.');
        Assert.areNotEqual('PDF',
            [SELECT FileType FROM ContentVersion WHERE Id = :word.Id].FileType,
            'PRECONDITION: the .docx version is not a PDF, so it must be skipped.');

        RLM_ReturnPDFDocument.InputVariable request = new RLM_ReturnPDFDocument.InputVariable();
        request.ResponseText = String.valueOf(word.Id).left(15) + ', ,'
            + String.valueOf(pdf.Id).left(15) + ',not-an-id,';

        Test.startTest();
        List<RLM_ReturnPDFDocument.OutputVariable> outputs =
            RLM_ReturnPDFDocument.ReturnPDFDocumentId(
                new List<RLM_ReturnPDFDocument.InputVariable>{ request }
            );
        Test.stopTest();

        Assert.areEqual(1, outputs.size(), 'One output per request.');
        Assert.areEqual(pdf.Id, outputs[0].ContentVersionId, 'The PDF version is returned.');
        Assert.areEqual(pdf.ContentDocumentId, outputs[0].ContentDocumentId,
            'The PDF version\'s document is returned.');
    }

    // Requests without a PDF still produce an output (with null ids) in request
    // order, so a Flow never fails on a missing result.
    @IsTest
    static void returnsEmptyOutputsForRequestsWithoutAPdf_inRequestOrder() {
        ContentVersion word = newVersion('Proposal.docx');
        ContentVersion pdf = newVersion('Contract.pdf');
        insert new List<ContentVersion>{ word, pdf };
        Assert.areNotEqual('PDF',
            [SELECT FileType FROM ContentVersion WHERE Id = :word.Id].FileType,
            'PRECONDITION: the .docx version is not a PDF.');

        RLM_ReturnPDFDocument.InputVariable blank = new RLM_ReturnPDFDocument.InputVariable();
        blank.ResponseText = '   ';
        RLM_ReturnPDFDocument.InputVariable wordOnly = new RLM_ReturnPDFDocument.InputVariable();
        wordOnly.ResponseText = String.valueOf(word.Id);
        RLM_ReturnPDFDocument.InputVariable withPdf = new RLM_ReturnPDFDocument.InputVariable();
        withPdf.ResponseText = String.valueOf(pdf.Id);

        Test.startTest();
        List<RLM_ReturnPDFDocument.OutputVariable> outputs =
            RLM_ReturnPDFDocument.ReturnPDFDocumentId(
                new List<RLM_ReturnPDFDocument.InputVariable>{ blank, wordOnly, withPdf }
            );
        Test.stopTest();

        Assert.areEqual(3, outputs.size(), 'One output per request, in order.');
        Assert.isNull(outputs[0].ContentVersionId, 'Blank ResponseText yields an empty output.');
        Assert.isNull(outputs[0].ContentDocumentId);
        Assert.isNull(outputs[1].ContentVersionId, 'A Word-only response has no PDF.');
        Assert.isNull(outputs[1].ContentDocumentId);
        Assert.areEqual(pdf.Id, outputs[2].ContentVersionId,
            'A later request is unaffected by earlier empty ones.');
        Assert.isNotNull(outputs[2].ContentDocumentId,
            'The PDF request also carries its ContentDocument.');
    }

    @IsTest
    static void rejectsMissingRequests() {
        assertRejected(null);
        assertRejected(new List<RLM_ReturnPDFDocument.InputVariable>());
    }

    private static ContentVersion newVersion(String pathOnClient) {
        return new ContentVersion(
            Title = pathOnClient,
            PathOnClient = pathOnClient,
            VersionData = Blob.valueOf('RLM docgen test content for ' + pathOnClient)
        );
    }

    private static void assertRejected(List<RLM_ReturnPDFDocument.InputVariable> requests) {
        try {
            RLM_ReturnPDFDocument.ReturnPDFDocumentId(requests);
            Assert.fail('Expected IllegalArgumentException for a missing request list.');
        } catch (IllegalArgumentException caught) {
            Assert.isTrue(caught.getMessage().contains('at least one request is required'),
                caught.getMessage());
        }
    }
}
