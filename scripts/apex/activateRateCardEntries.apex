// Step 1: Query RateCardEntry records that need to be updated
List<RateCardEntry> rates = [SELECT Id, Status FROM RateCardEntry WHERE Status != 'Active'];

// Step 2: Update RateCardEntry records to Active
for (RateCardEntry rate : rates) {
    rate.Status = 'Active';
}
update rates;
