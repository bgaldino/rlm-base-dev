public with sharing class SObjectTransform implements ITransformSObject {
    public TransformSObjectResponse doMapping(TransformSObjectRequest request) {
        if (request == null || request.recordsToTransform == null || request.recordsToTransform.isEmpty()) {
            throw new DAOException('No Input Provided for Transformation');
        }
        TransformSObjectResponse response = new TransformSObjectResponse();
        for (AbstractRecord abstractRecord : request.recordsToTransform) {
            SObjectRecord record = (SObjectRecord) abstractRecord;
            if (record.sobj != null) {
                response.transformedRecords.add(record.sobj);
            }
        }
        return response;
    }
}