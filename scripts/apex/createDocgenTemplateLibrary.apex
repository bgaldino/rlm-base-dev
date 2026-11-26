// Create the Docgen Document Template Library and give runtime users read-only access to it.
//
// Document generation reads the template's file (a ContentVersion in this library) as the
// user who generates. Library files are visible only to library members, and the build
// admin who creates the library is its only member, so without this every other user's
// generation fails with "Could not Enqueue to Kafka for Generate And Convert. The
// contentVersion with ID : {0} is either deleted/non-existent or the user does not have
// access to it." (todo 435). Salesforce Help ("Create a Document Template Library"): to let
// users access the files in the library, add them as members, or grant access to a group
// and add the users to that group.
//
// What this script ensures, each step find-or-create so a rerun changes nothing:
//   1. The library: DeveloperName DocgenDocumentTemplateLibrary. On a fresh 264 build it holds
//      the files of 12 of the 13 DocumentTemplates: the RLM_ templates from
//      unpackaged/post_docgen/documentTemplates/, the billing templates and the collections
//      notices (measured 2026-11-26). The platform's inactive Order_Form has no library.
//   2. A library permission, 'RLM DocGen Template Viewer', with every permission flag off.
//      Measured on 264: a member reads the library's files and generates from them, and a
//      member's new version of a file is refused (INSUFFICIENT_ACCESS_ON_CROSS_REFERENCE_ENTITY).
//   3. A public group, RLM_DocGen_Template_Users. When the group has no members it gets All
//      Internal Users. A library takes only users and public groups as members (adding All
//      Internal Users directly is refused), so the group carries it. Generating any document
//      means reading its template, and templates hold no record data, so every internal
//      user reads them. To narrow it, replace the group's members; a rerun leaves a group that
//      has members alone.
//   4. The group's library membership with that permission. An existing membership for the
//      group is left as it is.
// Any failure throws, so the CCI task fails instead of leaving a library only the admin can read.

final String LIBRARY_API_NAME = 'DocgenDocumentTemplateLibrary';
final String LIBRARY_LABEL = 'Docgen Document Template Library';
final String PERMISSION_NAME = 'RLM DocGen Template Viewer';
final String GROUP_API_NAME = 'RLM_DocGen_Template_Users';
final String GROUP_LABEL = 'RLM DocGen Template Users';

// 1. Library
List<ContentWorkspace> libraries = [
    SELECT Id FROM ContentWorkspace WHERE DeveloperName = :LIBRARY_API_NAME LIMIT 1
];
ContentWorkspace library;
if (libraries.isEmpty()) {
    library = new ContentWorkspace(Name = LIBRARY_LABEL, DeveloperName = LIBRARY_API_NAME);
    insert library;
    System.debug('Created library ' + LIBRARY_API_NAME + ' (' + library.Id + ')');
} else {
    library = libraries[0];
    System.debug('Library ' + LIBRARY_API_NAME + ' already exists (' + library.Id + ')');
}

// 2. Read-only library permission
List<ContentWorkspacePermission> permissions = [
    SELECT Id FROM ContentWorkspacePermission WHERE Name = :PERMISSION_NAME LIMIT 1
];
ContentWorkspacePermission viewer;
if (permissions.isEmpty()) {
    viewer = new ContentWorkspacePermission(
        Name = PERMISSION_NAME,
        Description = 'Read-only access to the Docgen Document Template Library, so users can generate documents from its templates.',
        PermissionsManageWorkspace = false,
        PermissionsAddContent = false,
        PermissionsAddContentOBO = false,
        PermissionsArchiveContent = false,
        PermissionsDeleteContent = false,
        PermissionsFeatureContent = false,
        PermissionsViewComments = false,
        PermissionsAddComment = false,
        PermissionsModifyComments = false,
        PermissionsTagContent = false,
        PermissionsDeliverContent = false,
        PermissionsChatterSharing = false,
        PermissionsOrganizeFileAndFolder = false
    );
    insert viewer;
    System.debug('Created library permission ' + PERMISSION_NAME + ' (' + viewer.Id + ')');
} else {
    viewer = permissions[0];
    System.debug('Library permission ' + PERMISSION_NAME + ' already exists (' + viewer.Id + ')');
}

// 3. Public group, seeded with All Internal Users only while it has no members
List<Group> groups = [
    SELECT Id FROM Group WHERE DeveloperName = :GROUP_API_NAME AND Type = 'Regular' LIMIT 1
];
Group templateUsers;
if (groups.isEmpty()) {
    templateUsers = new Group(
        Name = GROUP_LABEL,
        DeveloperName = GROUP_API_NAME,
        Type = 'Regular',
        DoesIncludeBosses = false,
        DoesSendEmailToMembers = false
    );
    insert templateUsers;
    System.debug('Created public group ' + GROUP_API_NAME + ' (' + templateUsers.Id + ')');
} else {
    templateUsers = groups[0];
    System.debug('Public group ' + GROUP_API_NAME + ' already exists (' + templateUsers.Id + ')');
}
Integer memberCount = [SELECT COUNT() FROM GroupMember WHERE GroupId = :templateUsers.Id];
if (memberCount == 0) {
    Id allInternalUsers = [
        SELECT Id FROM Group WHERE DeveloperName = 'AllInternalUsers' AND Type = 'Organization' LIMIT 1
    ].Id;
    insert new GroupMember(GroupId = templateUsers.Id, UserOrGroupId = allInternalUsers);
    System.debug('Added All Internal Users to ' + GROUP_API_NAME);
} else {
    System.debug(GROUP_API_NAME + ' has ' + memberCount + ' member(s); membership left as is');
}

// 4. The group's library membership
List<ContentWorkspaceMember> memberships = [
    SELECT Id, ContentWorkspacePermissionId FROM ContentWorkspaceMember
    WHERE ContentWorkspaceId = :library.Id AND MemberId = :templateUsers.Id LIMIT 1
];
if (memberships.isEmpty()) {
    insert new ContentWorkspaceMember(
        ContentWorkspaceId = library.Id,
        MemberId = templateUsers.Id,
        ContentWorkspacePermissionId = viewer.Id
    );
    System.debug('Added ' + GROUP_API_NAME + ' to ' + LIBRARY_API_NAME + ' as ' + PERMISSION_NAME);
} else {
    System.debug(GROUP_API_NAME + ' is already a member of ' + LIBRARY_API_NAME + ' (permission '
        + memberships[0].ContentWorkspacePermissionId + '); left as is');
}
