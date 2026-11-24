public with sharing class RLM_ReturnPDFDocument {
    public class PdfNotFoundException extends Exception {}

    // Written for a user (it reaches any caller: another flow's fault message, an unhandled-fault
    // email): no class name or request index. The detail goes to the debug log.
    @TestVisible
    private static final String NO_REQUEST_MESSAGE = 'No generated document was given, so no PDF could be returned.';
    @TestVisible
    private static final String NO_USABLE_IDS_MESSAGE =
        'Document generation did not return a usable file, so no PDF could be returned.';
    @TestVisible
    private static final String PDF_NOT_FOUND_MESSAGE =
        'The generated PDF could not be found, or you do not have access to it.';

    @InvocableMethod(label='Return PDF Document ID' description='Doc Gen creates a Word and a PDF Document' category='Document Generation')
    public static List<OutputVariable> ReturnPDFDocumentId(List<InputVariable> requests) {
        if (requests == null || requests.isEmpty()) {
            System.debug(LoggingLevel.ERROR, 'RLM_ReturnPDFDocument: no requests');
            throw new IllegalArgumentException(NO_REQUEST_MESSAGE);
        }
        // Parse every request first so one ContentVersion query serves the whole batch.
        List<List<Id>> idsByRequest = new List<List<Id>>();
        Set<Id> allIds = new Set<Id>();
        for (Integer i = 0; i < requests.size(); i++) {
            InputVariable req = requests[i];
            List<Id> contentVersionIds = new List<Id>();
            if (req != null && String.isNotBlank(req.ResponseText)) {
                for (String idStr : req.ResponseText.split(',')) {
                    String trimmed = idStr.trim();
                    // Empty tokens (a trailing comma, whitespace-only segments) and malformed tokens
                    // are skipped, so one bad token does not hide a good id beside it.
                    if (String.isNotBlank(trimmed)) {
                        try {
                            contentVersionIds.add((Id) trimmed);
                        } catch (Exception e) {
                            // Not an Id (StringException or TypeException): skip it.
                        }
                    }
                }
                // ResponseText was given but no token in it is an id: generation returned something
                // unusable. Fail rather than return the empty output a blank ResponseText gets.
                if (contentVersionIds.isEmpty()) {
                    System.debug(LoggingLevel.ERROR, 'RLM_ReturnPDFDocument: request ' + i
                        + ' ResponseText has no valid ids: ' + req.ResponseText.abbreviate(200));
                    throw new PdfNotFoundException(NO_USABLE_IDS_MESSAGE);
                }
            }
            idsByRequest.add(contentVersionIds);
            allIds.addAll(contentVersionIds);
        }

        Map<Id, ContentVersion> pdfs = allIds.isEmpty()
            ? new Map<Id, ContentVersion>()
            : new Map<Id, ContentVersion>([
                SELECT Id, FileType, ContentDocumentId
                FROM ContentVersion
                WHERE Id IN :allIds AND FileType = 'PDF'
                WITH USER_MODE
            ]);

        List<OutputVariable> outputs = new List<OutputVariable>();
        for (Integer i = 0; i < idsByRequest.size(); i++) {
            List<Id> contentVersionIds = idsByRequest[i];
            OutputVariable output = new OutputVariable();
            // A blank ResponseText yields an empty output (ContentDocumentId and ContentVersionId
            // null; both are required=false so the Flow does not error on a missing result).
            // Non-blank ResponseText with no valid id failed above. When ids were given but none is
            // a PDF the user can read, fail too: returning nothing would hide a Word-only result,
            // an unreadable file or a failed generation behind an empty output.
            if (!contentVersionIds.isEmpty()) {
                for (Id contentVersionId : contentVersionIds) {
                    ContentVersion pdf = pdfs.get(contentVersionId);
                    if (pdf != null) {
                        output.ContentDocumentId = pdf.ContentDocumentId;
                        output.ContentVersionId = pdf.Id;
                        break;
                    }
                }
                if (output.ContentVersionId == null) {
                    System.debug(LoggingLevel.ERROR, 'RLM_ReturnPDFDocument: none of the '
                        + contentVersionIds.size() + ' generated file(s) in request ' + i
                        + ' is a PDF the current user can read: ' + contentVersionIds);
                    throw new PdfNotFoundException(PDF_NOT_FOUND_MESSAGE);
                }
            }
            outputs.add(output);
        }
        return outputs;
    }

    public class InputVariable {
        @InvocableVariable(required=true)
        public String ResponseText;
    }

    public class OutputVariable {
        @InvocableVariable(required=false)
        public Id ContentDocumentId;

        @InvocableVariable(required=false)
        public Id ContentVersionId;
    }
}
