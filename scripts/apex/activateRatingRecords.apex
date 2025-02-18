// Step 1: Query UnitOfMeasureClass records that need to be updated
List<UnitOfMeasureClass> uomcs = [SELECT Id, Status FROM UnitOfMeasureClass WHERE Status != 'Active'];

// Step 2: Update UnitOfMeasureClass records to Active
for (UnitOfMeasureClass uomc : uomcs) {
    uomc.Status = 'Active';
}
update uomcs;

// Step 3: Query UsageResource records that need to be updated
List<UsageResource> urs = [SELECT Id, Status FROM UsageResource WHERE Status != 'Active'];

// Step 4: Update UsageResource records to Active
for (UsageResource ur : urs) {
    ur.Status = 'Active';
}
update urs;

// Step 5: Query ProductUsageGrant records that need to be updated
List<ProductUsageGrant> prgs = [SELECT Id, Status FROM ProductUsageGrant WHERE Status != 'Active'];

// Step 6: Update ProductUsageGrant records to Active
for (ProductUsageGrant prg : prgs) {
    prg.Status = 'Active';
}
update prgs;