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

    // A blank ResponseText means generation named no file: the same fixed sentence as an unusable
    // ResponseText, not an empty output the flow would carry on with. A null request in the list is
    // a missing request.
    @IsTest
    static void throwsForANullRequestOrABlankResponseText() {
        try {
            RLM_ReturnPDFDocument.ReturnPDFDocumentId(new List<RLM_ReturnPDFDocument.InputVariable>{ null });
            Assert.fail('Expected IllegalArgumentException for a null request.');
        } catch (IllegalArgumentException caught) {
            Assert.areEqual(RLM_ReturnPDFDocument.NO_REQUEST_MESSAGE, caught.getMessage(),
                'The exact user-facing sentence');
        }
        RLM_ReturnPDFDocument.InputVariable blank = new RLM_ReturnPDFDocument.InputVariable();
        blank.ResponseText = '   ';
        RLM_ReturnPDFDocument.InputVariable empty = new RLM_ReturnPDFDocument.InputVariable();
        Test.startTest();
        for (RLM_ReturnPDFDocument.InputVariable request : new List<RLM_ReturnPDFDocument.InputVariable>{
            blank, empty
        }) {
            try {
                RLM_ReturnPDFDocument.ReturnPDFDocumentId(new List<RLM_ReturnPDFDocument.InputVariable>{ request });
                Assert.fail('Expected PdfNotFoundException for a request that names no file.');
            } catch (RLM_ReturnPDFDocument.PdfNotFoundException caught) {
                Assert.areEqual(RLM_ReturnPDFDocument.NO_USABLE_IDS_MESSAGE, caught.getMessage(),
                    'The exact user-facing sentence');
            }
        }
        Test.stopTest();
    }

    // Ids were given but none is a PDF the user can read (here, Word only): a specific exception,
    // not an empty output that hides a failed generation.
    @IsTest
    static void throwsPdfNotFoundWhenIdsAreGivenButNoneIsAPdf() {
        ContentVersion word = newVersion('Proposal.docx');
        insert word;
        Assert.areNotEqual('PDF',
            [SELECT FileType FROM ContentVersion WHERE Id = :word.Id].FileType,
            'PRECONDITION: the .docx version is not a PDF.');
        RLM_ReturnPDFDocument.InputVariable wordOnly = new RLM_ReturnPDFDocument.InputVariable();
        wordOnly.ResponseText = String.valueOf(word.Id);

        try {
            RLM_ReturnPDFDocument.ReturnPDFDocumentId(
                new List<RLM_ReturnPDFDocument.InputVariable>{ wordOnly });
            Assert.fail('Expected PdfNotFoundException for a Word-only response.');
        } catch (RLM_ReturnPDFDocument.PdfNotFoundException caught) {
            Assert.areEqual(RLM_ReturnPDFDocument.PDF_NOT_FOUND_MESSAGE, caught.getMessage(),
                'The exact user-facing sentence');
        }
    }

    // ResponseText was given but no token in it is an id: generation returned something unusable,
    // so the request fails instead of returning the empty output a blank ResponseText gets.
    @IsTest
    static void throwsWhenResponseTextHasNoUsableIds() {
        RLM_ReturnPDFDocument.InputVariable malformed = new RLM_ReturnPDFDocument.InputVariable();
        malformed.ResponseText = 'not-an-id, ,also-not-an-id,';
        try {
            RLM_ReturnPDFDocument.ReturnPDFDocumentId(
                new List<RLM_ReturnPDFDocument.InputVariable>{ malformed });
            Assert.fail('Expected PdfNotFoundException for a ResponseText with no usable id.');
        } catch (RLM_ReturnPDFDocument.PdfNotFoundException caught) {
            Assert.areEqual(RLM_ReturnPDFDocument.NO_USABLE_IDS_MESSAGE, caught.getMessage(),
                'The exact user-facing sentence');
        }
    }

    // The whole batch is served by one ContentVersion query.
    @IsTest
    static void usesOneQueryForTheWholeBatch() {
        ContentVersion pdf = newVersion('Contract.pdf');
        insert pdf;
        List<RLM_ReturnPDFDocument.InputVariable> requests = new List<RLM_ReturnPDFDocument.InputVariable>();
        for (Integer i = 0; i < 5; i++) {
            RLM_ReturnPDFDocument.InputVariable request = new RLM_ReturnPDFDocument.InputVariable();
            request.ResponseText = String.valueOf(pdf.Id);
            requests.add(request);
        }

        Test.startTest();
        Integer before = Limits.getQueries();
        List<RLM_ReturnPDFDocument.OutputVariable> outputs = RLM_ReturnPDFDocument.ReturnPDFDocumentId(requests);
        Integer used = Limits.getQueries() - before;
        Test.stopTest();

        Assert.areEqual(5, outputs.size());
        Assert.areEqual(1, used, 'One ContentVersion query for all five requests.');
    }

    // A Minimum Access user holding the Sales Representative set and the docgen runtime grant gets
    // back a PDF they uploaded. This shows only that a user can read their own file under USER_MODE;
    // it says nothing about files another user generated, which follow file sharing.
    @IsTest
    static void returnsTheirOwnPdfToASalesRepresentative() {
        User rep = RLM_DocGenTestUsers.salesRepresentative();
        List<RLM_ReturnPDFDocument.OutputVariable> outputs;
        ContentVersion pdf;
        Test.startTest();
        System.runAs(rep) {
            pdf = newVersion('RepContract.pdf');
            insert pdf;
            RLM_ReturnPDFDocument.InputVariable request = new RLM_ReturnPDFDocument.InputVariable();
            request.ResponseText = String.valueOf(pdf.Id);
            outputs = RLM_ReturnPDFDocument.ReturnPDFDocumentId(
                new List<RLM_ReturnPDFDocument.InputVariable>{ request });
        }
        Test.stopTest();

        Assert.areEqual(1, outputs.size(), 'One output for the one request.');
        Assert.areEqual(pdf.Id, outputs[0].ContentVersionId, 'The PDF the representative can read is returned.');
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
            Assert.areEqual(RLM_ReturnPDFDocument.NO_REQUEST_MESSAGE, caught.getMessage(),
                'The exact user-facing sentence');
        }
    }
}
