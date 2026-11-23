public with sharing class RLM_ReturnPDFDocument {
    public class PdfNotFoundException extends Exception {}

    @InvocableMethod(label='Return PDF Document ID' description='Doc Gen creates a Word and a PDF Document' category='Document Generation')
    public static List<OutputVariable> ReturnPDFDocumentId(List<InputVariable> requests) {
        if (requests == null || requests.isEmpty()) {
            throw new IllegalArgumentException('RLM_ReturnPDFDocument: at least one request is required.');
        }
        // Parse every request first so one ContentVersion query serves the whole batch.
        List<List<Id>> idsByRequest = new List<List<Id>>();
        Set<Id> allIds = new Set<Id>();
        for (InputVariable req : requests) {
            List<Id> contentVersionIds = new List<Id>();
            if (req != null && String.isNotBlank(req.ResponseText)) {
                for (String idStr : req.ResponseText.split(',')) {
                    String trimmed = idStr.trim();
                    // Skip empty tokens (trailing comma, whitespace-only segments)
                    // Catch malformed tokens that are non-blank but not valid Ids.
                    if (String.isNotBlank(trimmed)) {
                        try {
                            contentVersionIds.add((Id) trimmed);
                        } catch (Exception e) {
                            // Non-Id token in ResponseText (StringException or TypeException) - skip and continue
                        }
                    }
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
            // When Ids were given but none is a PDF the user can read, fail with a specific
            // message: returning nothing would hide a Word-only result, an unreadable file or a
            // failed generation behind an empty output.
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
                    throw new PdfNotFoundException(
                        'RLM_ReturnPDFDocument: none of the ' + contentVersionIds.size()
                        + ' generated file(s) in request ' + i
                        + ' is a PDF the current user can read.'
                    );
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
