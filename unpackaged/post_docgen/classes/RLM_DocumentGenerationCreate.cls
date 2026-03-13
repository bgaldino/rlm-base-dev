public class RLM_DocumentGenerationCreate {
     @InvocableMethod(label='Build a PDF file from an Object' description='Accepts the Object Id and a DocTitle.' category='Document Generation') 

    public static List<Response> CreateDocument( List<Request> requests ) {
        List<Response> responses = new List<Response>();
        String stCurrRecordId = requests[0].CurrentRecordId;
        String stDocTitle = requests[0].DocTitle;
        String stDocTemplateId = requests[0].DocTemplateId;
        
        DocumentGenerationProcess dgp = new DocumentGenerationProcess ();
        dgp.Type = 'GenerateAndConvert';
        dgp.ReferenceObject = stCurrRecordId;
        dgp.DocumentTemplateId = stDocTemplateId; //'2dtKa000000EmixIAC';
        //dgp.RequestText = '{"title":"' + stDocTitle + '"}';
        dgp.RequestText='{"keepIntermediate":true,"title":"' + stDocTitle + '"}';
 //dgp.RequestText = '{"title":"' + stDocTitle + '"}';
        dgp.DocGenApiVersionType='Advanced';
        // Could do Condition here for DocTemplate
        dgp.DocumentInputType = 'DocumentTemplate';
        dgp.DataRaptorInput = '{"Id":"' + stCurrRecordId + '"}';
        
        insert dgp;
        Response res = new Response();
        res.NewContentId = dgp.Id;
        responses.add( res );
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