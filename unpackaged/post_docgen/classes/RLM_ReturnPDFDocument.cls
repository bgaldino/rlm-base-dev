public class RLM_ReturnPDFDocument {
    @InvocableMethod(label='Return PDF Document ID' description='Doc Gen creates a Word and a PDF Document' category='Document Generation')
    public static List<OutputVariable> ReturnPDFDocumentId(List<InputVariable> requests) {
        List<OutputVariable> outputs = new List<OutputVariable>();
        List<Id> contentVersionIds = new List<Id>();
        for (String idStr : requests[0].ResponseText.split(',')) {
            contentVersionIds.add((Id) idStr.trim());
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
        outputs.add(output);
        return outputs;
    }

    public class InputVariable {
        @InvocableVariable(required=true)
        public String ResponseText;
    }

    public class OutputVariable {
        @InvocableVariable(required=true)
        public Id ContentDocumentId;

        @InvocableVariable(required=true)
        public Id ContentVersionId;
    }
}
