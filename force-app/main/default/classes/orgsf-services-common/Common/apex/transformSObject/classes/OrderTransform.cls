public with sharing class OrderTransform implements ITransformSObject {

    public TransformSObjectResponse doMapping(TransformSObjectRequest request) {
        if(request == null || request.recordsToTransform == null || request.recordsToTransform.isEmpty()) {
            throw new DAOException('No Input Provided for Transformation');
        }
        TransformSObjectResponse response = new TransformSObjectResponse();

        for(AbstractRecord abstractRecord: request.recordsToTransform) {
            OrderRecord record = (OrderRecord) abstractRecord;
            Order orderSObject = new Order();
            if(record.id != null) {
                orderSObject.put('Id', record.id);
            }
            if(record.contractId != null) {
                orderSObject.put('contractId', record.contractId);
            }
            if(record.effectiveDate != null) {
                orderSObject.put('EffectiveDate', record.effectiveDate);
            }
            if(record.accountId != null) {
                orderSObject.put('AccountId', record.accountId);
            }
            if(record.status != null) {
                orderSObject.put('Status', record.status);
            }

            response.transformedRecords.add((SObject)orderSObject);

        }
        return response;
    }
}