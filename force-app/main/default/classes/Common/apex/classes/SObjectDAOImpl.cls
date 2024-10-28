public with sharing class SObjectDAOImpl implements ISObjectDAO{
    public DAOResponse save(DAORequest request) {
        if (request == null || request.recordsToSave == null 
            || request.recordsToSave.isEmpty() || request.mapper == null) {
            throw new DAOException('Input Not Provided.');
        }
        DAOResponse response = new DAOResponse();

        try {
            TransformSObjectResponse transformResponse = request.mapper.doMapping(
                new TransformSObjectRequest (request.recordsToSave)
            );
            List<SObject> sobjects = transformResponse.transformedRecords;
            SObjectType myType = sobjects[0].getSObjectType();
            new SecurityCheck(request.accessLevel, request.operation).check(sobjects, myType);
            switch on request.operation {
                when OP_INSERT {
                    System.debug('insert');
                    Database.SaveResult[] saveResults = Database.insert(sobjects, request.isAllOrNone, request.accessLevel);
                    response.saveResults = getStatusFromSaveResults(saveResults, request.recordsToSave);
                }
                when OP_UPDATE {
                    System.debug('update');
                    Database.SaveResult[] saveResults = Database.update(sobjects, request.isAllOrNone, request.accessLevel);
                    response.saveResults = getStatusFromSaveResults(saveResults, request.recordsToSave);
                }
                when OP_UPSERT {
                    System.debug('upsert');
                    Database.UpsertResult[] saveResults = Database.upsert(sobjects, request.isAllOrNone, request.accessLevel);
                    response.saveResults = getStatusFromUpsertResults(saveResults, request.recordsToSave);
                }
                when else {
                    throw new DAOException('Invalid Save Operation. Save method only supports Insert, Update OR Upsert');
                }
            }
            return response;
        } catch (Exception e) {
            throw new DAOException ('Unable to save records :: ' + e.getMessage());
        }
    }

    private List<DAORecordStatus> getStatusFromSaveResults(Database.SaveResult[] saveResults, List<AbstractRecord> records) {
        if(saveResults == null || saveResults.isEmpty()) {
            return null;
        }
        Integer index = -1;
        List<DAORecordStatus> recordStatuses = new List<DAORecordStatus>();
        for(Database.SaveResult saveResult : saveResults) {
            index++;
            System.debug('saveResult :: ' + saveResult);
            DAORecordStatus recordStatus = new DAORecordStatus();
            recordStatus.record = records.get(index);
            recordStatus.isSuccess = saveResult.isSuccess();
            if (saveResult.isSuccess()) {
                recordStatus.record.id = getRecordIdFromSaveResult(saveResult,recordStatus.record);
                recordStatuses.add(recordStatus);   
                continue;
            }
            List<String> errors = new List<String>();
            for(Database.Error error : saveResult.getErrors()) {
                errors.add(error.getMessage());
            }
            recordStatus.errorMessages = errors;
            recordStatuses.add(recordStatus);   
        }
        return recordStatuses;
    }

    private List<DAORecordStatus> getStatusFromUpsertResults(Database.UpsertResult[] upsertResults, List<AbstractRecord> records) {
        if(upsertResults == null || upsertResults.isEmpty()) {
            return null;
        }
        Integer index = -1;
        List<DAORecordStatus> recordStatuses = new List<DAORecordStatus>();
        for(Database.UpsertResult upsertResult : upsertResults) {
            index++;
            System.debug('upsertResult :: ' + upsertResult);
            DAORecordStatus recordStatus = new DAORecordStatus();
            recordStatus.record = records.get(index);
            recordStatus.isSuccess = upsertResult.isSuccess();
            if (upsertResult.isSuccess()) {
                recordStatus.record.id = getRecordIdFromUpsertResult(upsertResult,recordStatus.record);
                recordStatuses.add(recordStatus);   
                continue;
            }
            List<String> errors = new List<String>();
            for(Database.Error error : upsertResult.getErrors()) {
                errors.add(error.getMessage());
            }
            recordStatus.errorMessages = errors;
            recordStatuses.add(recordStatus);   
        }
        return recordStatuses;
    }

    private Id getRecordIdFromSaveResult(Database.SaveResult saveResult, AbstractRecord record){
        if(record.id != null){
            return record.id;
        }
        return saveResult.getId();
    }

    private Id getRecordIdFromUpsertResult(Database.UpsertResult upsertResult, AbstractRecord record){
        if(record.id != null){
            return record.id;
        }
        return upsertResult.getId();
    }
}