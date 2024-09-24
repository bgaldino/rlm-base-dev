/*
    WHAT: This script sets the ranks and activates the Expression Set Versions of Expression Set Definitions
    WHY: Expression Set Definitions does not include their Rank and if activated without a Rank it cannot be 
         edited/deactivated normally because it requires the rank to be filled. Activating it as well saves time.
    WHO: Derrick
    WHEN: May 2024
*/

try {
   	List<ExpressionSetVersion> esvs = [SELECT Id FROM ExpressionSetVersion WHERE Rank = null AND IsActive = false AND VersionNumber = 1];

    if(!esvs.isEmpty()) {
        List<ExpressionSetVersion> updatedEsvs = new List<ExpressionSetVersion>();
        for(ExpressionSetVersion esv : esvs) {
            esv.Rank = 1;
            esv.IsActive = true;
            updatedEsvs.add(esv);
        }
        update updatedEsvs;
    } else {
        System.debug('No inactive or no-rank ExpressionSetVersions found');
    }
} catch (Exception e) {
    // Handle any exceptions
    System.debug('An error occurred: ' + e.getMessage());
}