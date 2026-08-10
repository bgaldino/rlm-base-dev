// Assign the CEO Role as a member of all QuantumBit Public Groups (Manager, Director, VP).
// Idempotent: skips groups that already have the role membership.

List<String> groupNames = new List<String>{'Manager', 'Director', 'VP'};

Group roleGroup = [
    SELECT Id FROM Group
    WHERE Type = 'Role' AND DeveloperName = 'CEO'
    LIMIT 1
];

List<Group> publicGroups = [
    SELECT Id, DeveloperName FROM Group
    WHERE Type = 'Regular' AND DeveloperName IN :groupNames
];

Set<Id> alreadyAssigned = new Set<Id>();
for (GroupMember gm : [
    SELECT GroupId FROM GroupMember
    WHERE GroupId IN :publicGroups AND UserOrGroupId = :roleGroup.Id
]) {
    alreadyAssigned.add(gm.GroupId);
}

List<GroupMember> toInsert = new List<GroupMember>();
for (Group pg : publicGroups) {
    if (!alreadyAssigned.contains(pg.Id)) {
        toInsert.add(new GroupMember(GroupId = pg.Id, UserOrGroupId = roleGroup.Id));
    }
}

if (!toInsert.isEmpty()) {
    insert toInsert;
    System.debug('Assigned CEO role to ' + toInsert.size() + ' public group(s)');
} else {
    System.debug('All public groups already have CEO role membership');
}
