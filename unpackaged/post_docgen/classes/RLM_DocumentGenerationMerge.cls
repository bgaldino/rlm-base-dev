public with sharing class RLM_DocumentGenerationMerge {
    // The exception text reaches any caller (another flow's fault message, an unhandled-fault email),
    // so every exception carries one of the fixed sentences below, including a refused insert (a
    // missing permission, a validation rule): the platform's own message, which names objects and
    // fields, goes to the debug log only.
    @TestVisible
    private static final String NO_REQUEST_MESSAGE = 'No merge request was given, so no documents were merged.';
    @TestVisible
    private static final String NO_PDFS_MESSAGE = 'Choose at least one PDF to merge.';
    @TestVisible
    private static final String MERGE_FAILED_MESSAGE =
        'The documents could not be merged for this record. Check that you can open the record, or contact your administrator.';

    public class DocumentMergeException extends Exception {}

    @InvocableMethod(label='Build a PDF file from Ids and return the merge id' description='Accepts a list of Ids and a DocTitle.' category='Document Generation')
    public static List<Response> MergeDocuments(List<Request> requests) {
        if (requests == null || requests.isEmpty()) {
            throw rejected(NO_REQUEST_MESSAGE, 'no requests');
        }
        List<Response> responses = new List<Response>();
        List<DocumentGenerationProcess> processes = new List<DocumentGenerationProcess>();
        for (Integer index = 0; index < requests.size(); index++) {
            Request req = requests[index];
            if (req == null) {
                throw rejected(NO_REQUEST_MESSAGE, 'request ' + index + ' is null');
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
                throw rejected(NO_PDFS_MESSAGE, 'request ' + index + ' has no non-null recordIds');
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
        try {
            insert as user processes;
        } catch (Exception e) {
            System.debug(LoggingLevel.ERROR, 'RLM_DocumentGenerationMerge process insert refused: '
                + e.getTypeName() + ': ' + e.getMessage());
            throw new DocumentMergeException(MERGE_FAILED_MESSAGE);
        }
        for (DocumentGenerationProcess dgp : processes) {
            Response res = new Response();
            res.MergedRecordId = dgp.Id;
            responses.add(res);
        }
        return responses;
    }

    private static IllegalArgumentException rejected(String message, String detail) {
        System.debug(LoggingLevel.ERROR, 'RLM_DocumentGenerationMerge: ' + detail);
        return new IllegalArgumentException(message);
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
