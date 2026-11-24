public with sharing class RLM_DocumentGenerationCreate {
    // The shipped flow shows its own fixed sentence on a fault, but the exception text still reaches
    // any other caller (another flow's fault message, an unhandled-fault email). Every exception this
    // class throws carries one of the fixed sentences below, including a refused query or insert (a
    // missing permission, a validation rule): the platform's own message, which names objects and
    // fields, goes to the debug log only.
    @TestVisible
    private static final String NO_REQUEST_MESSAGE = 'No document request was given, so no document was generated.';
    @TestVisible
    private static final String INCOMPLETE_REQUEST_MESSAGE =
        'The document could not be generated: a record and a document template are both required.';
    @TestVisible
    private static final String TEMPLATE_NOT_FOUND_MESSAGE =
        'The document template could not be found, or you do not have access to it.';
    @TestVisible
    private static final String CREATE_FAILED_MESSAGE =
        'The document could not be generated for this record. Check that you can open the record, or contact your administrator.';

    public class DocumentGenerationException extends Exception {}

    @InvocableMethod(
        label='Build a PDF file from an Object'
        description='Accepts the Object Id and a DocTitle.'
        category='Document Generation'
    )
    public static List<Response> CreateDocument(List<Request> requests) {
        if (requests == null || requests.isEmpty()) {
            throw rejected(NO_REQUEST_MESSAGE, 'no requests');
        }

        Set<Id> templateIds = new Set<Id>();
        for (Integer index = 0; index < requests.size(); index++) {
            Request request = requests[index];
            validateRequest(request, index);
            templateIds.add(request.DocTemplateId);
        }

        // USER_MODE: TokenMappingMethodType is field-level-security controlled (measured on a 264
        // org: it is permissionable, and RLM_QuantumBit_Sales_Representative grants it read).
        Map<Id, DocumentTemplate> templateMap;
        try {
            templateMap = new Map<Id, DocumentTemplate>(
                [SELECT Id, TokenMappingMethodType FROM DocumentTemplate WHERE Id IN :templateIds WITH USER_MODE]
            );
        } catch (Exception e) {
            throw refused(TEMPLATE_NOT_FOUND_MESSAGE, 'template query', e);
        }
        if (templateMap.size() != templateIds.size()) {
            throw rejected(TEMPLATE_NOT_FOUND_MESSAGE,
                (templateIds.size() - templateMap.size()) + ' of ' + templateIds.size()
                + ' DocumentTemplate ids were not found or are not readable: ' + templateIds);
        }

        List<DocumentGenerationProcess> processes = buildProcesses(requests, templateMap);
        // As the running user. The user needs create on DocumentGenerationProcess. Of the permission sets
        // source-controlled here only RLM_QuantumBit_Sales_Representative grants it; a 264 org also
        // has RLM_Sales_Representative, RLM_Sales_Operations, RLM_DOC, RLM_CLM and RLM_RCB granting it
        // (measured), so a persona outside those needs it from its own permission set. Of the fields set here,
        // only ReferenceObject and RequestText are field-level-security controlled, and the
        // source-controlled RLM_QuantumBit_Sales_Representative set grants both; Type, DocumentTemplateId, DocGenApiVersionType,
        // DocumentInputType, DocGenAdditionalInputType, DocGenAdditionalInput and DataRaptorInput are
        // not permissionable, so insert as user does not check them (measured on a 264 org).
        try {
            insert as user processes;
        } catch (Exception e) {
            throw refused(CREATE_FAILED_MESSAGE, 'process insert', e);
        }

        List<Response> responses = new List<Response>();
        for (DocumentGenerationProcess process : processes) {
            Response response = new Response();
            response.NewContentId = process.Id;
            responses.add(response);
        }
        return responses;
    }

    @TestVisible
    private static List<DocumentGenerationProcess> buildProcesses(
        List<Request> requests,
        Map<Id, DocumentTemplate> templateMap
    ) {
        List<DocumentGenerationProcess> processes = new List<DocumentGenerationProcess>();
        for (Integer index = 0; index < requests.size(); index++) {
            Request request = requests[index];
            validateRequest(request, index);

            DocumentTemplate template = templateMap.get(request.DocTemplateId);
            if (template == null) {
                throw rejected(TEMPLATE_NOT_FOUND_MESSAGE,
                    'DocumentTemplate ' + request.DocTemplateId + ' was not found for request ' + index);
            }

            DocumentGenerationProcess process = new DocumentGenerationProcess();
            process.Type = 'GenerateAndConvert';
            process.ReferenceObject = request.CurrentRecordId;
            process.DocumentTemplateId = request.DocTemplateId;
            process.RequestText = JSON.serialize(
                new Map<String, Object>{ 'keepIntermediate' => true, 'title' => request.DocTitle }
            );
            process.DocGenApiVersionType = 'Advanced';
            process.DocumentInputType = 'DocumentTemplate';

            if (template.TokenMappingMethodType == 'ContextService') {
                process.DocGenAdditionalInputType = 'ContextService';
                // Context Service DocGen expects the primary entity Id, not a runtime Context API payload.
                process.DocGenAdditionalInput = String.valueOf(request.CurrentRecordId);
            } else {
                process.DataRaptorInput = JSON.serialize(
                    new Map<String, Object>{ 'Id' => request.CurrentRecordId }
                );
            }
            processes.add(process);
        }
        return processes;
    }

    private static void validateRequest(Request request, Integer index) {
        if (request == null) {
            throw rejected(INCOMPLETE_REQUEST_MESSAGE, 'request ' + index + ' is null');
        }
        if (request.CurrentRecordId == null) {
            throw rejected(INCOMPLETE_REQUEST_MESSAGE, 'CurrentRecordId is null for request ' + index);
        }
        if (request.DocTemplateId == null) {
            throw rejected(INCOMPLETE_REQUEST_MESSAGE, 'DocTemplateId is null for request ' + index);
        }
    }

    private static DocumentGenerationException refused(String message, String step, Exception cause) {
        System.debug(LoggingLevel.ERROR, 'RLM_DocumentGenerationCreate ' + step + ' refused: '
            + cause.getTypeName() + ': ' + cause.getMessage());
        return new DocumentGenerationException(message);
    }

    private static IllegalArgumentException rejected(String message, String detail) {
        System.debug(LoggingLevel.ERROR, 'RLM_DocumentGenerationCreate: ' + detail);
        return new IllegalArgumentException(message);
    }

    public class Request {
        @InvocableVariable(label='Record of the Main object' required=true)
        public Id CurrentRecordId;

        @InvocableVariable(required=true)
        public Id DocTemplateId;

        @InvocableVariable(required=false)
        public String DocTitle;
    }

    public class Response {
        @InvocableVariable(required=true)
        public Id NewContentId;
    }
}
