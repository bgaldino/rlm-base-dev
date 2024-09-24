// Query for DecisionTable records with a Status other than 'Active'
List<DecisionTable> decisionTables = [SELECT Id, DeveloperName, Status FROM DecisionTable WHERE Status != 'Active'];

// Check if any records were found
if (!decisionTables.isEmpty()) {
    // Loop through each DecisionTable record and update the Status field
    for (DecisionTable dt : decisionTables) {
        dt.Status = 'Active';
    }
    
    // Perform the update DML operation
    update decisionTables;

    // Log the result
    System.debug('Updated ' + decisionTables.size() + ' DecisionTable record(s) to Active.');
} else {
    System.debug('No DecisionTable records found with a Status other than Active.');
}