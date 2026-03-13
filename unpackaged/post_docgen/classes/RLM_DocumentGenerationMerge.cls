public class RLM_DocumentGenerationMerge {
    @InvocableMethod(label='Build a PDF file from Ids and return the merge id' description='Accepts a list of Ids and a DocTitle.' category='Document Generation')
    public static List<Response> MergeDocuments(List<Request> requests) {
        List<Response> responses = new List<Response>();
        Request req = requests[0];
        List<String> idStrings = new List<String>();

        if (req.recordIds != null) {
            for (Id recordId : req.recordIds) {
                if (recordId != null) {
                    idStrings.add(String.valueOf(recordId));
                }
            }
        }

        DocumentGenerationProcess dgp = new DocumentGenerationProcess();
        dgp.Type = 'MergePDF';
        dgp.RequestText = '{"title":"' + req.DocTitle + '"}';
        dgp.PdfDocIdentifiersList = String.join(idStrings, ',');
        dgp.Status = 'InProgress';
        dgp.DocGenApiVersionType = 'Advanced';
        dgp.ReferenceObject = req.CurrentRecordId;

        insert dgp;

        Response res = new Response();
        res.MergedRecordId = dgp.Id;
        responses.add(res);
        return responses;
    }

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
