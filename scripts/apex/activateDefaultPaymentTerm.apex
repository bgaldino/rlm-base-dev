// Query for PaymentTerm records named 'Default Payment Term'
List<PaymentTerm> paymentTerms = [SELECT Id, Name, IsDefault, Status FROM PaymentTerm WHERE Name = 'Default Payment Term'];

// Check if any records were found
if (!paymentTerms.isEmpty()) {
    // Loop through each PaymentTerm record and update the fields
    for (PaymentTerm pt : paymentTerms) {
        pt.IsDefault = true;
        pt.Status = 'Active';
    }
    
    // Perform the update DML operation
    update paymentTerms;

    // Log the result
    System.debug('Updated ' + paymentTerms.size() + ' PaymentTerm record(s).');
} else {
    System.debug('No PaymentTerm records found with the name "Default Payment Term".');
}