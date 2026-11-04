// Step 1: Query LegalEntity records that need to be updated
List<LegalEntity> legalEntities = [SELECT Id, Status FROM LegalEntity WHERE Status != 'Active'];

// Step 2: Update LegalEntity records to Active
for (LegalEntity le : legalEntities) {
    le.Status = 'Active';
}
update legalEntities;
