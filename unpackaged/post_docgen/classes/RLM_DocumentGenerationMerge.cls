public class RLM_DocumentGenerationMerge {
  @InvocableMethod(label='Build a PDF file from Ids and return the merge id' description='Accepts a list of Ids and a DocTitle.' category='Document Generation') 

        public static List<Response> MergeDocuments( List<Request> requests ) {
        List<Response> responses = new List<Response>();
    String currRecordId = requests[0].CurrentRecordId;
        String stDocTitle = requests[0].DocTitle;
        List<String> idStrings = new List<String>();
        //List<String> idStrings = new List<String>();
    if (requests != null && !requests.isEmpty()) {
          Request req = requests[0];
      if (req != null && req.recordIds != null) {
            for (Id recordId : req.recordIds) {
                if (recordId != null) {
                  idStrings.add(String.valueOf(recordId));
                }
            } //For Loop
          }
      }  
        String commaSeparatedIds = String.join(idStrings, ',');  
        DocumentGenerationProcess dgp = new DocumentGenerationProcess ();
      String requestText = '{"title":"' + stDocTitle + '"}';
      dgp.Type = 'MergePDF';
      dgp.RequestText = requestText;
      dgp.PdfDocIdentifiersList = commaSeparatedIds; // pdfDocList;
      dgp.Status = 'InProgress';
      dgp.DocGenApiVersionType='Advanced';
      dgp.ReferenceObject = currRecordId;
        //dgp.Id;
        insert dgp;
          
        Response res = new Response();
        res.MergedRecordId = dgp.Id;
          
    responses.add( res );
        return responses;
    }
    
    // ---------------------------------------
    
    public class Request {
        @InvocableVariable(label='Record of the Main object' required=true)
        public String CurrentRecordId;
        
        @InvocableVariable(label='List of PDF Ids' required=true)
        public List<Id> recordIds;
        
        @InvocableVariable(required=false)
        public String DocTitle;
        
    }
    
    public class Response {
        @InvocableVariable(required=true)
        public Id MergedRecordId;
        
    }
    
}