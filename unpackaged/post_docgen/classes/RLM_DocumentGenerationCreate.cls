public class RLM_DocumentGenerationCreate {
    @InvocableMethod(label='Build a PDF file from an Object' description='Accepts the Object Id and a DocTitle.' category='Document Generation')
    public static List<Response> CreateDocument(List<Request> requests) {
        if (requests == null || requests.isEmpty()) {
            throw new IllegalArgumentException('RLM_DocumentGenerationCreate: at least one request is required.');
        }
        // Bulkify: collect all template IDs and query once before the loop.
        Set<Id> templateIds = new Set<Id>();
        for (Request req : requests) {
            if (req.DocTemplateId != null) templateIds.add(req.DocTemplateId);
        }
        Map<Id, DocumentTemplate> templateMap = new Map<Id, DocumentTemplate>(
            [SELECT Id, TokenMappingMethodType FROM DocumentTemplate WHERE Id IN :templateIds]
        );

        List<Response> responses = new List<Response>();
        for (Request req : requests) {
            String stCurrRecordId = req.CurrentRecordId;
            String stDocTitle = req.DocTitle;
            Id stDocTemplateId = req.DocTemplateId;

            DocumentTemplate dt = templateMap.get(stDocTemplateId);
            Boolean isContextService = dt != null && dt.TokenMappingMethodType == 'ContextService';

            DocumentGenerationProcess dgp = new DocumentGenerationProcess();
            dgp.Type = 'GenerateAndConvert';
            dgp.ReferenceObject = stCurrRecordId;
            dgp.DocumentTemplateId = stDocTemplateId;
            // Use JSON.serialize to safely escape DocTitle (avoids invalid JSON on quotes/newlines)
            dgp.RequestText = JSON.serialize(new Map<String, Object>{ 'keepIntermediate' => true, 'title' => stDocTitle });
            dgp.DocGenApiVersionType = 'Advanced';
            dgp.DocumentInputType = 'DocumentTemplate';
            if (isContextService) {
                dgp.DocGenAdditionalInputType = 'ContextService';
                // CS DocGen requires inputData format with the primary node name as key
                String primaryNodeName = 'Quote';
                dgp.DocGenAdditionalInput = JSON.serialize(new Map<String, Object>{
                    'inputData' => new Map<String, Object>{
                        primaryNodeName => new Map<String, Object>{ 'id' => stCurrRecordId }
                    }
                });
            } else {
                dgp.DataRaptorInput = JSON.serialize(new Map<String, Object>{ 'Id' => stCurrRecordId });
            }

            insert dgp;

            Response res = new Response();
            res.NewContentId = dgp.Id;
            responses.add(res);
        }
        return responses;
    }

    public class Request {
        @InvocableVariable(label='Record of the Main object' required=true)
        public String CurrentRecordId;

        @InvocableVariable(required=true)
        public String DocTemplateId;

        @InvocableVariable(required=false)
        public String DocTitle;
    }

    public class Response {
        @InvocableVariable(required=true)
        public Id NewContentId;
    }
}
