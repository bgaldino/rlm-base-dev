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

    // A Minimum Access user holding the Sales Representative set and the docgen runtime grant (see
    // RLM_DocGenTestUsers) creates the process for a quote on their own opportunity. The runtime set
    // overlaps some grants, so this shows the pair is enough; RLM_DocGenTestUsers checks that the
    // Sales Representative set carries each grant itself.
    @IsTest
    static void createDocumentRunsForASalesRepresentative() {
        User rep = RLM_DocGenTestUsers.salesRepresentative();
        Quote quote = createQuote(rep.Id);
        Id templateId = templatesByMethod().get('ContextService').Id;

        List<RLM_DocumentGenerationCreate.Response> responses;
        Test.startTest();
        System.runAs(rep) {
            responses = RLM_DocumentGenerationCreate.CreateDocument(
                new List<RLM_DocumentGenerationCreate.Request>{ requestFor(quote.Id, templateId, 'Rep proposal') });
        }
        Test.stopTest();

        Assert.areEqual(1, responses.size(), 'One response for the one request.');
        DocumentGenerationProcess process = [
            SELECT ReferenceObject, CreatedById FROM DocumentGenerationProcess WHERE Id = :responses[0].NewContentId
        ];
        Assert.areEqual(String.valueOf(quote.Id), process.ReferenceObject, 'The process references the quote.');
        Assert.areEqual(rep.Id, process.CreatedById, 'The process was created as the sales representative.');
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
        assertIllegalArgument(null, RLM_DocumentGenerationCreate.NO_REQUEST_MESSAGE);
        assertIllegalArgument(new List<RLM_DocumentGenerationCreate.Request>(), RLM_DocumentGenerationCreate.NO_REQUEST_MESSAGE);
        assertIllegalArgument(
            new List<RLM_DocumentGenerationCreate.Request>{ null },
            RLM_DocumentGenerationCreate.INCOMPLETE_REQUEST_MESSAGE
        );

        RLM_DocumentGenerationCreate.Request missingRecord = new RLM_DocumentGenerationCreate.Request();
        missingRecord.DocTemplateId = templatesByMethod().get('ContextService').Id;
        assertIllegalArgument(
            new List<RLM_DocumentGenerationCreate.Request>{ missingRecord },
            RLM_DocumentGenerationCreate.INCOMPLETE_REQUEST_MESSAGE
        );

        RLM_DocumentGenerationCreate.Request missingTemplate = new RLM_DocumentGenerationCreate.Request();
        missingTemplate.CurrentRecordId = createQuote().Id;
        assertIllegalArgument(
            new List<RLM_DocumentGenerationCreate.Request>{ missingTemplate },
            RLM_DocumentGenerationCreate.INCOMPLETE_REQUEST_MESSAGE
        );

        assertIllegalArgument(
            new List<RLM_DocumentGenerationCreate.Request>{
                requestFor(createQuote().Id, Id.valueOf('2dt000000000001'), 'Missing template')
            },
            RLM_DocumentGenerationCreate.TEMPLATE_NOT_FOUND_MESSAGE
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
            Assert.areEqual(RLM_DocumentGenerationCreate.TEMPLATE_NOT_FOUND_MESSAGE, caughtException.getMessage(),
                'The builder check uses the same user-facing sentence');
        }
    }

    // A user with no docgen grants gets the fixed sentence, not the platform's refusal (which names
    // the object and field the query was refused on).
    @IsTest
    static void aRefusedTemplateQueryShowsAFixedSentence() {
        User nobody = RLM_DocGenTestUsers.withNoGrants();
        Quote quote = createQuote();
        Id templateId = templatesByMethod().get('ContextService').Id;

        Test.startTest();
        System.runAs(nobody) {
            try {
                RLM_DocumentGenerationCreate.CreateDocument(
                    new List<RLM_DocumentGenerationCreate.Request>{ requestFor(quote.Id, templateId, 'Refused') });
                Assert.fail('Expected the template query to be refused for a user with no docgen grants.');
            } catch (Exception caught) {
                Assert.isInstanceOfType(caught, RLM_DocumentGenerationCreate.DocumentGenerationException.class,
                    'The query itself was refused (not an empty result): ' + caught.getTypeName());
                Assert.areEqual(RLM_DocumentGenerationCreate.TEMPLATE_NOT_FOUND_MESSAGE, caught.getMessage(),
                    'The fixed sentence, not the platform message.');
            }
        }
        Test.stopTest();
        Assert.areEqual(0, [SELECT COUNT() FROM DocumentGenerationProcess], 'Nothing was created.');
    }

    private static Quote createQuote() {
        return createQuote(UserInfo.getUserId());
    }

    // The quote's access follows its opportunity, so a runAs test passes the user who owns the deal.
    private static Quote createQuote(Id ownerId) {
        Account account = new Account(Name = 'DocGen Test Account');
        insert account;
        Opportunity opportunity = new Opportunity(
            Name = 'DocGen Test Opportunity',
            AccountId = account.Id,
            StageName = 'Prospecting',
            CloseDate = Date.today().addDays(30),
            OwnerId = ownerId
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
            Assert.areEqual(expectedMessage, caughtException.getMessage(), 'The exact user-facing sentence');
        }
    }
}
