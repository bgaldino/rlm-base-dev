public class RLM_ReturnPDFDocument {
    @InvocableMethod(label='Return PDF Document ID' description='Doc Gen creates a Word and a PDF Document' category='Document Generation')
    public static List<OutputVariable> ReturnPDFDocumentId(List<InputVariable> requests) {
        if (requests == null || requests.isEmpty()) {
            throw new IllegalArgumentException('RLM_ReturnPDFDocument: at least one request is required.');
        }
        List<OutputVariable> outputs = new List<OutputVariable>();
        for (InputVariable req : requests) {
            if (String.isBlank(req.ResponseText)) {
                outputs.add(new OutputVariable());
                continue;
            }
            List<Id> contentVersionIds = new List<Id>();
            for (String idStr : req.ResponseText.split(',')) {
                String trimmed = idStr.trim();
                // Skip empty tokens (trailing comma, whitespace-only segments)
                // Catch malformed tokens that are non-blank but not valid Ids.
                if (String.isNotBlank(trimmed)) {
                    try {
                        contentVersionIds.add((Id) trimmed);
                    } catch (Exception e) {
                        // Non-Id token in ResponseText (StringException or TypeException) — skip and continue
                    }
                }
            }

            List<ContentVersion> conVersion = [
                SELECT Id, FileType, ContentDocumentId
                FROM ContentVersion
                WHERE Id IN :contentVersionIds AND FileType = 'PDF'
                LIMIT 1
            ];

            OutputVariable output = new OutputVariable();
            if (!conVersion.isEmpty()) {
                output.ContentDocumentId = conVersion[0].ContentDocumentId;
                output.ContentVersionId = conVersion[0].Id;
            }
            // ContentDocumentId/ContentVersionId left null when no PDF found;
            // marked required=false so Flow does not error on a missing result.
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
