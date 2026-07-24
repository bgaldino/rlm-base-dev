public class RLM_SaveQuoteDocument {
    @InvocableMethod(label='Save as Quote PDF' description='Copies PDF bytes into a QuoteDocument and deletes the source ContentDocument.' category='Document Generation')
    public static List<OutputVariable> saveAsQuotePdf(List<InputVariable> requests) {
        if (requests == null || requests.isEmpty()) {
            throw new IllegalArgumentException('RLM_SaveQuoteDocument: at least one request is required.');
        }

        Set<Id> cvIds = new Set<Id>();
        for (InputVariable req : requests) {
            if (req.ContentVersionId != null) {
                cvIds.add(req.ContentVersionId);
            }
        }

        Map<Id, ContentVersion> cvMap = new Map<Id, ContentVersion>([
            SELECT Id, VersionData, ContentDocumentId
            FROM ContentVersion
            WHERE Id IN :cvIds
        ]);

        List<QuoteDocument> qDocs = new List<QuoteDocument>();
        List<Integer> validIndices = new List<Integer>();
        for (Integer i = 0; i < requests.size(); i++) {
            InputVariable req = requests[i];
            ContentVersion cv = cvMap.get(req.ContentVersionId);
            if (cv == null || req.QuoteId == null) {
                continue;
            }
            QuoteDocument qd = new QuoteDocument();
            qd.QuoteId = req.QuoteId;
            qd.Document = cv.VersionData;
            qd.Status = 'Completed';
            qDocs.add(qd);
            validIndices.add(i);
        }

        insert qDocs;

        Set<Id> qdIds = new Set<Id>();
        for (QuoteDocument qd : qDocs) {
            qdIds.add(qd.Id);
        }
        Map<Id, QuoteDocument> insertedQds = new Map<Id, QuoteDocument>([
            SELECT Id, ContentVersionDocumentId
            FROM QuoteDocument
            WHERE Id IN :qdIds
        ]);

        Set<Id> newCvIds = new Set<Id>();
        for (QuoteDocument qd : insertedQds.values()) {
            if (qd.ContentVersionDocumentId != null) {
                newCvIds.add(qd.ContentVersionDocumentId);
            }
        }
        Map<Id, ContentVersion> newCvMap = new Map<Id, ContentVersion>();
        if (!newCvIds.isEmpty()) {
            for (ContentVersion cv : [
                SELECT Id, ContentDocumentId
                FROM ContentVersion
                WHERE Id IN :newCvIds
            ]) {
                newCvMap.put(cv.Id, cv);
            }
        }

        List<ContentDocument> docsToDelete = new List<ContentDocument>();
        Set<Id> deletedDocIds = new Set<Id>();
        for (Integer i = 0; i < requests.size(); i++) {
            ContentVersion sourceCv = cvMap.get(requests[i].ContentVersionId);
            if (sourceCv != null && sourceCv.ContentDocumentId != null && !deletedDocIds.contains(sourceCv.ContentDocumentId)) {
                docsToDelete.add(new ContentDocument(Id = sourceCv.ContentDocumentId));
                deletedDocIds.add(sourceCv.ContentDocumentId);
            }
        }
        if (!docsToDelete.isEmpty()) {
            delete docsToDelete;
        }

        List<OutputVariable> outputs = new List<OutputVariable>();
        Integer validIdx = 0;
        for (Integer i = 0; i < requests.size(); i++) {
            OutputVariable out = new OutputVariable();
            if (validIdx < validIndices.size() && validIndices[validIdx] == i) {
                QuoteDocument qd = qDocs[validIdx];
                QuoteDocument refreshed = insertedQds.get(qd.Id);
                out.QuoteDocumentId = qd.Id;
                if (refreshed != null && refreshed.ContentVersionDocumentId != null) {
                    ContentVersion newCv = newCvMap.get(refreshed.ContentVersionDocumentId);
                    if (newCv != null) {
                        out.NewContentDocumentId = newCv.ContentDocumentId;
                    }
                }
                validIdx++;
            }
            outputs.add(out);
        }
        return outputs;
    }

    public class InputVariable {
        @InvocableVariable(required=true)
        public Id QuoteId;

        @InvocableVariable(required=true)
        public Id ContentVersionId;
    }

    public class OutputVariable {
        @InvocableVariable(required=false)
        public Id QuoteDocumentId;

        @InvocableVariable(required=false)
        public Id NewContentDocumentId;
    }
}
