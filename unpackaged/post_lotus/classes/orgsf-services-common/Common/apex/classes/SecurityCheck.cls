public with sharing class SecurityCheck {
    private final AccessLevel accLevel;
    private final DMLOperation operation;

    private static final String ERROR_STRING = 'You do not have permission to perform this DML operation on this object: ';
    private static final String NO_OPERATION = 'No operation specified';

    public SecurityCheck(AccessLevel accessLevel, DMLOperation operation) {
        this.accLevel = accessLevel;
        this.operation = operation;
    }

    public void check(List<SObject> objList, SObjectType myType) {
        if (this.accLevel == AccessLevel.SYSTEM_MODE) {
            return;
        }

        checkObjectLevelSecurity(myType);

        Set<String> fieldsToCheck = new Set<String>();
        Map<String, Schema.SObjectField> fieldMap = myType.getDescribe().fields.getMap();
        for (SObject so : objList) {
            for (String field : so.getPopulatedFieldsAsMap().keySet()) {
                fieldsToCheck.add(field);
            }
        }

        checkFieldLevelSecurity(fieldsToCheck, fieldMap, myType);
    }

    @TestVisible
    private void checkObjectLevelSecurity(SObjectType myType) {
        switch on this.operation {
            when OP_INSERT {
                if ((isDMLOperationAllowed(myType.getDescribe().isCreateable())) == false) {
                    throw new DAOException(ERROR_STRING + myType);
                }
            }
            when OP_UPDATE {
                if ((isDMLOperationAllowed(myType.getDescribe().isUpdateable())) == false) {
                    throw new DAOException(ERROR_STRING + myType);
                }
            }
            when OP_UPSERT {
                if ((isDMLOperationAllowed(myType.getDescribe().isCreateable() && myType.getDescribe().isUpdateable())) == false) {
                    throw new DAOException(ERROR_STRING + myType);
                }
            }
            when else {
                System.debug(NO_OPERATION);
            }
        }
    }

    @TestVisible
    private void checkFieldLevelSecurity(Set<String> fieldNames, Map<String, Schema.SObjectField> fieldMap, SObjectType myType) {
        for (String fieldName : fieldNames) {
            if (fieldName == 'Id') {
                continue;
            }

            Schema.SObjectField myField = fieldMap.get(fieldName);
            if (myField == null) {
                continue;
            }

            checkIfFieldOperationAllowed(myField, myType);
        }
    }

    private void checkIfFieldOperationAllowed(SObjectField myField, SObjectType myType) {
        switch on this.operation {
            when OP_INSERT {
                if ((isDMLOperationAllowed(myField.getDescribe().isCreateable())) == false) {
                    throw new DAOException(ERROR_STRING + myType + ' / ' + myField);
                }
            }
            when OP_UPDATE {
                if ((isDMLOperationAllowed(myField.getDescribe().isUpdateable())) == false) {
                    throw new DAOException(ERROR_STRING + myType + ' / ' + myField);
                }
            }
            when OP_UPSERT {
                if ((isDMLOperationAllowed(myField.getDescribe().isCreateable() && myField.getDescribe().isUpdateable())) == false) {
                    throw new DAOException(ERROR_STRING + myType + ' / ' + myField);
                }
            }
            when else {
                System.debug(NO_OPERATION);
            }
        }
    }

    private Boolean isDMLOperationAllowed(Boolean isAllowed) {
        if (!Test.isRunningTest()) {
            return isAllowed;
        } else {
            return false;
        }
    }

    @TestVisible
    private static Boolean TEST_BYPASS = false;

    public static AccessLevel getAccessLevel() {
        if (!TEST_BYPASS && (UserInfo.getUserType() == 'automatedprocess' || Test.isRunningTest())) {
            return AccessLevel.SYSTEM_MODE;
        }
        return AccessLevel.USER_MODE;
    }
}
