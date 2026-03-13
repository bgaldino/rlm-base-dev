public class RLM_DocumentGenerationCreate {
    @InvocableMethod(label='Build a PDF file from an Object' description='Accepts the Object Id and a DocTitle.' category='Document Generation')
    public static List<Response> CreateDocument(List<Request> requests) {
        List<Response> responses = new List<Response>();
        String stCurrRecordId = requests[0].CurrentRecordId;
        String stDocTitle = requests[0].DocTitle;
        String stDocTemplateId = requests[0].DocTemplateId;

        DocumentTemplate dt = [SELECT TokenMappingMethodType, ContextDefinitionName, ContextMappingName FROM DocumentTemplate WHERE Id = :stDocTemplateId LIMIT 1];
        Boolean isContextService = dt.TokenMappingMethodType == 'ContextService';

        DocumentGenerationProcess dgp = new DocumentGenerationProcess();
        dgp.Type = 'GenerateAndConvert';
        dgp.ReferenceObject = stCurrRecordId;
        dgp.DocumentTemplateId = stDocTemplateId;
        dgp.RequestText = '{"keepIntermediate":true,"title":"' + stDocTitle + '"}';
        dgp.DocGenApiVersionType = 'Advanced';
        dgp.DocumentInputType = 'DocumentTemplate';
        if (isContextService) {
            dgp.DocGenAdditionalInputType = 'ContextService';
            // CS DocGen requires inputData format with the primary node name as key
            String primaryNodeName = 'Quote';
            dgp.DocGenAdditionalInput = '{"inputData":{"' + primaryNodeName + '":{"id":"' + stCurrRecordId + '"}}}';
        } else {
            dgp.DataRaptorInput = '{"Id":"' + stCurrRecordId + '"}';
        }

        insert dgp;

        Response res = new Response();
        res.NewContentId = dgp.Id;
        responses.add(res);
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
