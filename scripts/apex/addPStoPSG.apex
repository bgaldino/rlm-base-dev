/*
This script adds the custom permission set to the permission set group in the org.
In order to deploy RLM, we had to deploy the PSG and Settings before the force/app directory.
In testing, the custom external ID fields were not deploying properly in deploy_pre
Thus, this apex script takes the PS that relies on these metadata types and adds them to the PSG.
If you can find a better way to approach this, I would encourage it.
*/
// Define the API names of the permission set and permission set group
String permissionSetName = 'RLM_BasePermissions';
String permissionSetGroupName = 'Revenue_Cloud_Base';

// Query the PermissionSetGroupComponent records to check if the permission set is already assigned to the group
List<PermissionSetGroupComponent> existingComponents = [SELECT Id FROM PermissionSetGroupComponent WHERE PermissionSet.Name = :permissionSetName AND PermissionSetGroup.DeveloperName = :permissionSetGroupName LIMIT 1];

try {
    // Check if the permission set is already assigned to the group
    if (existingComponents.isEmpty()) {
        // Query the permission set and permission set group
        PermissionSet permissionSet = [SELECT Id FROM PermissionSet WHERE Name = :permissionSetName LIMIT 1];
        PermissionSetGroup permissionSetGroup = [SELECT Id FROM PermissionSetGroup WHERE DeveloperName = :permissionSetGroupName LIMIT 1];
        
        // Create a new PermissionSetGroupComponent record
        PermissionSetGroupComponent component = new PermissionSetGroupComponent();
        component.PermissionSetId = permissionSet.Id;
        component.PermissionSetGroupId = permissionSetGroup.Id;
        
        // Insert the PermissionSetGroupComponent record
        insert component;
        
        System.debug('Permission set assigned successfully.');
    } else {
        System.debug('Permission set is already assigned to the group.');
    }
} catch(Exception e) {
    // Handle any exceptions
    System.debug('An error occurred: ' + e.getMessage());
}