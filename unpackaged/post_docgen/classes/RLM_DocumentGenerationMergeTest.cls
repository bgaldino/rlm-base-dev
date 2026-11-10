/**
 * Tests for RLM_DocumentGenerationMerge: one MergePDF DocumentGenerationProcess
 * per request, built from the PDF ids and the document title.
 */
@IsTest
private class RLM_DocumentGenerationMergeTest {

    // Each request becomes an InProgress MergePDF process whose identifier list
    // carries the non-null ids in order and whose title survives JSON escaping.
    @IsTest
    static void mergeCreatesOneMergeProcessPerRequest() {
        Quote quote = createQuote();
        ContentVersion first = newPdf('Proposal.pdf');
        ContentVersion second = newPdf('Terms.pdf');
        insert new List<ContentVersion>{ first, second };

        RLM_DocumentGenerationMerge.Request withNulls = new RLM_DocumentGenerationMerge.Request();
        withNulls.CurrentRecordId = quote.Id;
        withNulls.recordIds = new List<Id>{ first.Id, null, second.Id };
        withNulls.DocTitle = 'Merged "proposal"\nfinal';

        RLM_DocumentGenerationMerge.Request single = new RLM_DocumentGenerationMerge.Request();
        single.CurrentRecordId = quote.Id;
        single.recordIds = new List<Id>{ second.Id };

        Test.startTest();
        List<RLM_DocumentGenerationMerge.Response> responses =
            RLM_DocumentGenerationMerge.MergeDocuments(
                new List<RLM_DocumentGenerationMerge.Request>{ withNulls, single }
            );
        Test.stopTest();

        Assert.areEqual(2, responses.size(), 'One response per request.');
        Set<Id> processIds = new Set<Id>{ responses[0].MergedRecordId, responses[1].MergedRecordId };
        Map<Id, DocumentGenerationProcess> processes = new Map<Id, DocumentGenerationProcess>([
            SELECT Id, Type, Status, RequestText, PdfDocIdentifiersList,
                DocGenApiVersionType, ReferenceObject
            FROM DocumentGenerationProcess
            WHERE Id IN :processIds
        ]);
        Assert.areEqual(2, processes.size(), 'Both merge processes were inserted.');

        DocumentGenerationProcess merged = processes.get(responses[0].MergedRecordId);
        Assert.areEqual('MergePDF', merged.Type);
        Assert.areEqual('InProgress', merged.Status);
        Assert.areEqual('Advanced', merged.DocGenApiVersionType);
        Assert.areEqual(String.valueOf(quote.Id), merged.ReferenceObject);
        Assert.areEqual(String.valueOf(first.Id) + ',' + String.valueOf(second.Id),
            merged.PdfDocIdentifiersList, 'Null ids are dropped; order is kept.');
        Map<String, Object> requestText =
            (Map<String, Object>) JSON.deserializeUntyped(merged.RequestText);
        Assert.areEqual('Merged "proposal"\nfinal', requestText.get('title'),
            'Quotes and newlines in the title round-trip through valid JSON.');

        DocumentGenerationProcess plain = processes.get(responses[1].MergedRecordId);
        Assert.areEqual(String.valueOf(second.Id), plain.PdfDocIdentifiersList);
        Map<String, Object> plainText =
            (Map<String, Object>) JSON.deserializeUntyped(plain.RequestText);
        Assert.isTrue(plainText.containsKey('title'), 'The title key is always written.');
        Assert.isNull(plainText.get('title'), 'An omitted title serializes as null.');
    }

    @IsTest
    static void mergeRejectsMissingRequests() {
        assertRejected(null, 'at least one request is required');
        assertRejected(new List<RLM_DocumentGenerationMerge.Request>(),
            'at least one request is required');
    }

    // A request with no usable PDF ids is rejected before anything is inserted.
    @IsTest
    static void mergeRejectsRequestsWithoutPdfIds() {
        Quote quote = createQuote();

        RLM_DocumentGenerationMerge.Request nullList = new RLM_DocumentGenerationMerge.Request();
        nullList.CurrentRecordId = quote.Id;
        nullList.recordIds = null;

        RLM_DocumentGenerationMerge.Request onlyNulls = new RLM_DocumentGenerationMerge.Request();
        onlyNulls.CurrentRecordId = quote.Id;
        onlyNulls.recordIds = new List<Id>{ null, null };

        Test.startTest();
        assertRejected(new List<RLM_DocumentGenerationMerge.Request>{ nullList },
            'recordIds must contain at least one non-null Id');
        assertRejected(new List<RLM_DocumentGenerationMerge.Request>{ onlyNulls },
            'recordIds must contain at least one non-null Id');
        Test.stopTest();

        String referenceObject = String.valueOf(quote.Id);
        Assert.areEqual(0,
            [SELECT COUNT() FROM DocumentGenerationProcess
             WHERE Type = 'MergePDF' AND ReferenceObject = :referenceObject],
            'A rejected request must not create a merge process.');
    }

    private static ContentVersion newPdf(String pathOnClient) {
        return new ContentVersion(
            Title = pathOnClient,
            PathOnClient = pathOnClient,
            VersionData = Blob.valueOf('RLM merge test content for ' + pathOnClient)
        );
    }

    private static Quote createQuote() {
        Account account = new Account(Name = 'DocGen Merge Test Account');
        insert account;
        Opportunity opportunity = new Opportunity(
            Name = 'DocGen Merge Test Opportunity',
            AccountId = account.Id,
            StageName = 'Prospecting',
            CloseDate = Date.today().addDays(30)
        );
        insert opportunity;
        Quote quote = new Quote(
            Name = 'DocGen Merge Test Quote',
            OpportunityId = opportunity.Id,
            Pricebook2Id = Test.getStandardPricebookId(),
            Status = 'Draft'
        );
        insert quote;
        return quote;
    }

    private static void assertRejected(
            List<RLM_DocumentGenerationMerge.Request> requests, String expectedMessage) {
        try {
            RLM_DocumentGenerationMerge.MergeDocuments(requests);
            Assert.fail('Expected IllegalArgumentException.');
        } catch (IllegalArgumentException caught) {
            Assert.isTrue(caught.getMessage().contains(expectedMessage), caught.getMessage());
        }
    }
}
