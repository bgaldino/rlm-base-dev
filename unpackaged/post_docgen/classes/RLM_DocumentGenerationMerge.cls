public with sharing class RLM_DocumentGenerationMerge {
    @InvocableMethod(label='Build a PDF file from Ids and return the merge id' description='Accepts a list of Ids and a DocTitle.' category='Document Generation')
    public static List<Response> MergeDocuments(List<Request> requests) {
        if (requests == null || requests.isEmpty()) {
            throw new IllegalArgumentException('RLM_DocumentGenerationMerge: at least one request is required.');
        }
        List<Response> responses = new List<Response>();
        List<DocumentGenerationProcess> processes = new List<DocumentGenerationProcess>();
        for (Integer index = 0; index < requests.size(); index++) {
            Request req = requests[index];
            if (req == null) {
                throw new IllegalArgumentException('RLM_DocumentGenerationMerge: request ' + index + ' is required.');
            }
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
            // Use JSON.serialize to safely escape DocTitle (avoids invalid JSON on quotes/newlines)
            dgp.RequestText = JSON.serialize(new Map<String, Object>{ 'title' => req.DocTitle });
            if (idStrings.isEmpty()) {
                throw new IllegalArgumentException('RLM_DocumentGenerationMerge: recordIds must contain at least one non-null Id.');
            }
            dgp.PdfDocIdentifiersList = String.join(idStrings, ',');
            dgp.Status = 'InProgress';
            dgp.DocGenApiVersionType = 'Advanced';
            dgp.ReferenceObject = req.CurrentRecordId;

            processes.add(dgp);
        }

        // One DML for the whole batch, as the running user. The FLS-controlled fields set above
        // (ReferenceObject, RequestText, PdfDocIdentifiersList) are granted by the Sales
        // Representative set; Type, Status and DocGenApiVersionType are not permissionable. Every request is validated above
        // before anything is inserted; the responses follow request order.
        insert as user processes;
        for (DocumentGenerationProcess dgp : processes) {
            Response res = new Response();
            res.MergedRecordId = dgp.Id;
            responses.add(res);
        }
        return responses;
    }

    public class Request {
        @InvocableVariable(label='Record of the Main object' required=true)
        public Id CurrentRecordId;

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
