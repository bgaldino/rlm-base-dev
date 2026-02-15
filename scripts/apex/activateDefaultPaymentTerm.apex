// Step 1: Set IsDefault and activate the Default Payment Term.
// The default must be marked before other PaymentTerms can be activated.
List<PaymentTerm> defaultTerms = [SELECT Id, Name, IsDefault, Status FROM PaymentTerm WHERE Name = 'Default Payment Term' AND Status != 'Active'];
if (!defaultTerms.isEmpty()) {
    for (PaymentTerm pt : defaultTerms) {
        pt.IsDefault = true;
        pt.Status = 'Active';
    }
    update defaultTerms;
    System.debug('Activated ' + defaultTerms.size() + ' Default Payment Term record(s).');
} else {
    System.debug('Default Payment Term is already active or does not exist.');
}

// Step 2: Activate all remaining Draft PaymentTerms.
List<PaymentTerm> draftTerms = [SELECT Id, Name, Status FROM PaymentTerm WHERE Status = 'Draft'];
if (!draftTerms.isEmpty()) {
    for (PaymentTerm pt : draftTerms) {
        pt.Status = 'Active';
    }
    update draftTerms;
    System.debug('Activated ' + draftTerms.size() + ' remaining PaymentTerm record(s).');
} else {
    System.debug('No Draft PaymentTerm records to activate.');
}