public class RLM_ReturnPDFDocument {
@InvocableMethod(label='Return PDF Document ID' description='Doc Gen creates a Word and a PDF Document' category='Document Generation')
    public static List<OutputVariable> ReturnPDFDocumentId(List<InputVariable> requests) {
    List<OutputVariable> outputs = new List<OutputVariable>();  
    String delimiterString = requests[0].ResponseText; // '068Kj00000dn9ky,068Kj00000dn9lR';
    // Transform 'A, B' into "'A','B'"
    String formattedString = '\'' + String.join(delimiterString.split(','), '\',\'') + '\'';
    String query = 'SELECT Id, FileType, ContentDocumentId FROM ContentVersion WHERE Id IN (' + formattedString + ') AND FileType = \'PDF\'';
    List<ContentVersion> conVersion = Database.query(query);
    String strDocumentId;
    String strContentVersionId;
    if (!conVersion.isEmpty()) {
        strDocumentId = conVersion[0].ContentDocumentId;
        strContentVersionId = conVersion[0].Id;
    }
    OutputVariable output = new OutputVariable();  
    output.ContentDocumentId = strDocumentId;
    output.ContentVersionId = strContentVersionId;
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