public with sharing class ApproverQuery implements IApproverQuery{

    private static IApproverQuery instance = null;
    private static AccessLevel accessLevelMode = AccessLevel.USER_MODE;
    public static IApproverQuery getInstance() {
        if (instance == null) {
            instance = new ApproverQuery();
        }
        return instance;
    }

    public static void setInstance(IApproverQuery existingInstance) {
        instance = existingInstance;
    }

    public ApproverQuery() {
        if(Test.isRunningTest()) {
            accessLevelMode = AccessLevel.SYSTEM_MODE;
        }
    }

    public List<GroupMember> getGroupMembers(List<String> groupMemberIds) {
        return Database.queryWithBinds(
            'SELECT Id, GroupId, UserOrGroupId FROM GroupMember WHERE Id IN: groupMemberIds',
            new Map<String,Object>{'groupMemberIds' => groupMemberIds},
            accessLevelMode
        );
    }

    public List<SBAA__Approver__c> getGroupIdByApproverId(Id approverId) {
        return Database.queryWithBinds('SELECT sbaa__GroupId__c FROM SBAA__Approver__c WHERE Id= :approverId LIMIT 1',
            new Map<String,Object>{'approverId' => approverId},
            accessLevelMode
        );
    }
}