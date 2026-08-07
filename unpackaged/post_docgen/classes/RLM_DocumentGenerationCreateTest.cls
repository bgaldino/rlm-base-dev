@IsTest
private class RLM_DocumentGenerationCreateTest {
    @TestSetup
    static void setupData() {
        insert new List<DocumentTemplate>{
            new DocumentTemplate(
                Name = 'UnitTestContextServiceTemplate',
                Type = 'MicrosoftWord',
                TokenMappingType = 'JSON',
                TokenMappingMethodType = 'ContextService',
                ContextDefinitionName = 'RLM_QuoteDocGenContext',
                ContextMappingName = 'QuoteDocGenMapping'
            ),
            new DocumentTemplate(
                Name = 'UnitTestODTTemplate',
                Type = 'MicrosoftWord',
                TokenMappingType = 'JSON',
                TokenMappingMethodType = 'OmniDataTransform'
            )
        };
    }

    @IsTest
    static void createDocumentBuildsContextServiceAndOdtProcesses() {
        Quote quote = createQuote();
        Map<String, DocumentTemplate> templatesByMethod = templatesByMethod();
        List<RLM_DocumentGenerationCreate.Request> requests = new List<RLM_DocumentGenerationCreate.Request>{
            requestFor(quote.Id, templatesByMethod.get('ContextService').Id, 'Context "proposal"'),
            requestFor(quote.Id, templatesByMethod.get('OmniDataTransform').Id, 'ODT proposal')
        };

        Test.startTest();
        List<RLM_DocumentGenerationCreate.Response> responses =
            RLM_DocumentGenerationCreate.CreateDocument(requests);
        Test.stopTest();

        Assert.areEqual(2, responses.size(), 'Each request should return one DGP response.');
        Set<Id> processIds = new Set<Id>();
        for (RLM_DocumentGenerationCreate.Response response : responses) {
            processIds.add(response.NewContentId);
        }
        Map<Id, DocumentGenerationProcess> processesById = new Map<Id, DocumentGenerationProcess>([
            SELECT Id, ReferenceObject, RequestText, DocGenAdditionalInputType,
                DocGenAdditionalInput, DataRaptorInput
            FROM DocumentGenerationProcess
            WHERE Id IN :processIds
        ]);

        DocumentGenerationProcess contextProcess = processesById.get(responses[0].NewContentId);
        Assert.areEqual(String.valueOf(quote.Id), contextProcess.ReferenceObject);
        Assert.areEqual('ContextService', contextProcess.DocGenAdditionalInputType);
        Assert.areEqual(String.valueOf(quote.Id), contextProcess.DocGenAdditionalInput);
        Assert.isNull(contextProcess.DataRaptorInput, 'Context Service must not receive DataRaptor input.');
        Map<String, Object> contextRequestText =
            (Map<String, Object>) JSON.deserializeUntyped(contextProcess.RequestText);
        Assert.areEqual('Context "proposal"', contextRequestText.get('title'));

        DocumentGenerationProcess odtProcess = processesById.get(responses[1].NewContentId);
        Assert.isNull(odtProcess.DocGenAdditionalInputType, 'ODT must not use Context Service input.');
        Assert.isNull(odtProcess.DocGenAdditionalInput, 'ODT must not use Context Service input.');
        Assert.areEqual(
            String.valueOf(quote.Id),
            ((Map<String, Object>) JSON.deserializeUntyped(odtProcess.DataRaptorInput)).get('Id')
        );
    }

    @IsTest
    static void buildProcessesIsBulkSafeAndPreservesOrder() {
        Quote quote = createQuote();
        Map<String, DocumentTemplate> templatesByMethod = templatesByMethod();
        DocumentTemplate contextTemplate = templatesByMethod.get('ContextService');
        DocumentTemplate odtTemplate = templatesByMethod.get('OmniDataTransform');
        Map<Id, DocumentTemplate> templateMap = new Map<Id, DocumentTemplate>{
            contextTemplate.Id => contextTemplate,
            odtTemplate.Id => odtTemplate
        };
        List<RLM_DocumentGenerationCreate.Request> requests = new List<RLM_DocumentGenerationCreate.Request>();
        for (Integer index = 0; index < 200; index++) {
            requests.add(requestFor(
                quote.Id,
                Math.mod(index, 2) == 0 ? contextTemplate.Id : odtTemplate.Id,
                'Proposal ' + index
            ));
        }

        List<DocumentGenerationProcess> processes =
            RLM_DocumentGenerationCreate.buildProcesses(requests, templateMap);

        Assert.areEqual(200, processes.size(), 'All Flow bulk requests should be built.');
        Assert.areEqual(String.valueOf(quote.Id), processes[0].DocGenAdditionalInput);
        Assert.isNull(processes[1].DocGenAdditionalInput);
        Assert.areEqual(
            'Proposal 199',
            ((Map<String, Object>) JSON.deserializeUntyped(processes[199].RequestText)).get('title')
        );
    }

    @IsTest
    static void createDocumentRejectsMissingRequestsAndTemplates() {
        assertIllegalArgument(null, 'at least one request is required');
        assertIllegalArgument(new List<RLM_DocumentGenerationCreate.Request>(), 'at least one request is required');
        assertIllegalArgument(
            new List<RLM_DocumentGenerationCreate.Request>{ null },
            'request 0 is required'
        );

        RLM_DocumentGenerationCreate.Request missingRecord = new RLM_DocumentGenerationCreate.Request();
        missingRecord.DocTemplateId = templatesByMethod().get('ContextService').Id;
        assertIllegalArgument(
            new List<RLM_DocumentGenerationCreate.Request>{ missingRecord },
            'CurrentRecordId is required'
        );

        RLM_DocumentGenerationCreate.Request missingTemplate = new RLM_DocumentGenerationCreate.Request();
        missingTemplate.CurrentRecordId = createQuote().Id;
        assertIllegalArgument(
            new List<RLM_DocumentGenerationCreate.Request>{ missingTemplate },
            'DocTemplateId is required'
        );

        assertIllegalArgument(
            new List<RLM_DocumentGenerationCreate.Request>{
                requestFor(createQuote().Id, Id.valueOf('2dt000000000001'), 'Missing template')
            },
            'DocumentTemplate records were not found'
        );

        try {
            RLM_DocumentGenerationCreate.buildProcesses(
                new List<RLM_DocumentGenerationCreate.Request>{
                    requestFor(createQuote().Id, Id.valueOf('2dt000000000001'), 'Missing template')
                },
                new Map<Id, DocumentTemplate>()
            );
            Assert.fail('Expected an unknown-template error from the defensive builder check.');
        } catch (IllegalArgumentException caughtException) {
            Assert.isTrue(
                caughtException.getMessage().contains('DocumentTemplate was not found for request 0'),
                caughtException.getMessage()
            );
        }
    }

    private static Quote createQuote() {
        Account account = new Account(Name = 'DocGen Test Account');
        insert account;
        Opportunity opportunity = new Opportunity(
            Name = 'DocGen Test Opportunity',
            AccountId = account.Id,
            StageName = 'Prospecting',
            CloseDate = Date.today().addDays(30)
        );
        insert opportunity;
        Quote quote = new Quote(
            Name = 'DocGen Test Quote',
            OpportunityId = opportunity.Id,
            Pricebook2Id = Test.getStandardPricebookId(),
            Status = 'Draft'
        );
        insert quote;
        return quote;
    }

    private static Map<String, DocumentTemplate> templatesByMethod() {
        Map<String, DocumentTemplate> templatesByMethod = new Map<String, DocumentTemplate>();
        for (DocumentTemplate templateRecord : [
            SELECT Id, Name, TokenMappingMethodType
            FROM DocumentTemplate
            WHERE TokenMappingMethodType IN ('ContextService', 'OmniDataTransform')
        ]) {
            templatesByMethod.put(templateRecord.TokenMappingMethodType, templateRecord);
        }
        return templatesByMethod;
    }

    private static RLM_DocumentGenerationCreate.Request requestFor(Id quoteId, Id templateId, String title) {
        RLM_DocumentGenerationCreate.Request request = new RLM_DocumentGenerationCreate.Request();
        request.CurrentRecordId = quoteId;
        request.DocTemplateId = templateId;
        request.DocTitle = title;
        return request;
    }

    private static void assertIllegalArgument(
        List<RLM_DocumentGenerationCreate.Request> requests,
        String expectedMessage
    ) {
        try {
            RLM_DocumentGenerationCreate.CreateDocument(requests);
            Assert.fail('Expected IllegalArgumentException.');
        } catch (IllegalArgumentException caughtException) {
            Assert.isTrue(caughtException.getMessage().contains(expectedMessage), caughtException.getMessage());
        }
    }
}
