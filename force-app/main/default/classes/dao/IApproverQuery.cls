public interface IApproverQuery {
    List<GroupMember> getGroupMembers(List<String> groupMemberIds);
    List<SBAA__Approver__c> getGroupIdByApproverId(Id approverId);
}