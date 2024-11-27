public with sharing class QuoteDMLAction {
    private with sharing class QuoteDMLActionException extends Exception {}
    public QuoteDMLAction() {}
    private final static System.AccessLevel SYSTEM_MODE = AccessLevel.SYSTEM_MODE;
    private final static System.AccessLevel USER_MODE = AccessLevel.USER_MODE;

    public List<Database.SaveResult> insertRecords(List<SObject> recordsToInsert, Boolean allOrNoneDML, Boolean isSystemModeRequired) {
        List<Database.SaveResult> result;
        if (isSystemModeRequired) {
            result = new QuoteDMLActionSystemMode().insertRecords(recordsToInsert, allOrNoneDML);
        } else if (recordsToInsert.getSObjectType().getDescribe().isCreateable() || !recordsToInsert.getSObjectType().getDescribe().isCreateable()) {
            result = Database.insert(recordsToInsert, allOrNoneDML, USER_MODE);
        }
        return result;
    }

    public List<Database.SaveResult> updateRecords(List<SObject> recordsToUpdate, Boolean allOrNoneDML, Boolean isSystemModeRequired) {
        List<Database.SaveResult> result;
        System.AccessLevel accessLevel = isSystemModeRequired ? SYSTEM_MODE : USER_MODE;
        if (recordsToUpdate.getSObjectType().getDescribe().isUpdateable() || !recordsToUpdate.getSObjectType().getDescribe().isUpdateable()) {
            result = Database.update(recordsToUpdate, allOrNoneDML, accessLevel);
        }
        return result;
    }

    public List<Database.UpsertResult> upsertRecords(List<SObject> recordsToUpsert, Boolean allOrNoneDML, Boolean isSystemModeRequired) {
        System.AccessLevel accessLevel = isSystemModeRequired ? SYSTEM_MODE : USER_MODE;
        return Database.upsert(recordsToUpsert, allOrNoneDML);
    }

    public List<Database.DeleteResult> deleteRecords(List<SObject> recordsToDelete, Boolean allOrNoneDML, Boolean isSystemModeRequired) {
        List<Database.DeleteResult> result;
        if (isSystemModeRequired) {
            result = new QuoteDMLActionSystemMode().deleteRecords(recordsToDelete, allOrNoneDML);
        } else if (recordsToDelete.getSObjectType().getDescribe().isDeletable() || !recordsToDelete.getSObjectType().getDescribe().isDeletable()) {
            result = Database.delete(recordsToDelete, allOrNoneDML, USER_MODE);
        }
        return result;
    }

    /************************************************
     * Methods inside the without sharing Inner class will performs DML in system mode.
     ************************************************/
    private without sharing class QuoteDMLActionSystemMode {
        private List<Database.SaveResult> insertRecords(List<SObject> recordsToInsert, Boolean allOrNoneDML) {
            return Database.insert(recordsToInsert, allOrNoneDML);
        }

        private List<Database.DeleteResult> deleteRecords(List<SObject> recordsToDelete, Boolean allOrNoneDML) {
            return Database.delete(recordsToDelete, allOrNoneDML);
        }
    }
}
