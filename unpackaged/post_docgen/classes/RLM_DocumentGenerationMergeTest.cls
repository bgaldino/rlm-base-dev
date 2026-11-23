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
        Assert.isTrue(String.valueOf(first.Id) < String.valueOf(second.Id),
            'PRECONDITION: second sorts after first, so a sorted list would differ.');

        RLM_DocumentGenerationMerge.Request withNulls = new RLM_DocumentGenerationMerge.Request();
        withNulls.CurrentRecordId = quote.Id;
        // Passed against Id order (second was inserted after first), so the
        // expected list below proves the given order is kept, not sorted.
        withNulls.recordIds = new List<Id>{ second.Id, null, first.Id };
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
        Assert.areEqual(String.valueOf(second.Id) + ',' + String.valueOf(first.Id),
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

    // A null request in the list is rejected by name, not with a NullPointerException.
    @IsTest
    static void mergeRejectsANullRequest() {
        assertRejected(new List<RLM_DocumentGenerationMerge.Request>{ null }, 'request 0 is required');
    }

    // The whole batch is one DML statement, however many requests it carries.
    @IsTest
    static void mergeUsesOneDmlStatementForTheWholeBatch() {
        Quote quote = createQuote();
        ContentVersion pdf = newPdf('Batch.pdf');
        insert pdf;
        List<RLM_DocumentGenerationMerge.Request> requests = new List<RLM_DocumentGenerationMerge.Request>();
        for (Integer i = 0; i < 5; i++) {
            RLM_DocumentGenerationMerge.Request request = new RLM_DocumentGenerationMerge.Request();
            request.CurrentRecordId = quote.Id;
            request.recordIds = new List<Id>{ pdf.Id };
            requests.add(request);
        }

        Test.startTest();
        // Limits reset on entry to the block and are restored on exit, so read them inside it.
        Integer before = Limits.getDmlStatements();
        List<RLM_DocumentGenerationMerge.Response> responses = RLM_DocumentGenerationMerge.MergeDocuments(requests);
        Integer used = Limits.getDmlStatements() - before;
        Test.stopTest();

        Assert.areEqual(5, responses.size(), 'One response per request.');
        Assert.areEqual(1, used, 'One insert for all five requests.');
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
