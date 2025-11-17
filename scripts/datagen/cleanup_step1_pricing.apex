// Step 1: Delete Pricing Data (including all derived price references)
System.debug('=== Step 1: Cleaning up pricing data ===');
Integer total = 0, batch = 200;

// Delete PricebookEntryDerivedPrice (by PricebookEntry name)
List<PricebookEntryDerivedPrice> pbedp1 = [SELECT Id FROM PricebookEntryDerivedPrice WHERE PricebookEntry.Name LIKE '%GEN%' LIMIT :batch];
while (!pbedp1.isEmpty()) {
    delete pbedp1;
    total += pbedp1.size();
    pbedp1 = [SELECT Id FROM PricebookEntryDerivedPrice WHERE PricebookEntry.Name LIKE '%GEN%' LIMIT :batch];
}
System.debug('Deleted PricebookEntryDerivedPrice (by entry name): ' + total);

// Delete PricebookEntryDerivedPrice (by Product)
List<PricebookEntryDerivedPrice> pbedp2 = [SELECT Id FROM PricebookEntryDerivedPrice WHERE Product.StockKeepingUnit LIKE '%GEN%' LIMIT :batch];
Integer pbedp2Count = 0;
while (!pbedp2.isEmpty()) {
    delete pbedp2;
    pbedp2Count += pbedp2.size();
    pbedp2 = [SELECT Id FROM PricebookEntryDerivedPrice WHERE Product.StockKeepingUnit LIKE '%GEN%' LIMIT :batch];
}
total += pbedp2Count;
System.debug('Deleted PricebookEntryDerivedPrice (by product): ' + pbedp2Count);

// Delete PricebookEntryDerivedPrice (by ContributingProduct)
List<PricebookEntryDerivedPrice> pbedp3 = [SELECT Id FROM PricebookEntryDerivedPrice WHERE ContributingProduct.StockKeepingUnit LIKE '%GEN%' LIMIT :batch];
Integer pbedp3Count = 0;
while (!pbedp3.isEmpty()) {
    delete pbedp3;
    pbedp3Count += pbedp3.size();
    pbedp3 = [SELECT Id FROM PricebookEntryDerivedPrice WHERE ContributingProduct.StockKeepingUnit LIKE '%GEN%' LIMIT :batch];
}
total += pbedp3Count;
System.debug('Deleted PricebookEntryDerivedPrice (by contributing product): ' + pbedp3Count);

// Delete PricebookEntry
List<PricebookEntry> pbe = [SELECT Id FROM PricebookEntry WHERE Name LIKE '%GEN%' LIMIT :batch];
Integer pbeCount = 0;
while (!pbe.isEmpty()) {
    delete pbe;
    pbeCount += pbe.size();
    pbe = [SELECT Id FROM PricebookEntry WHERE Name LIKE '%GEN%' LIMIT :batch];
}
total += pbeCount;
System.debug('Deleted PricebookEntry: ' + pbeCount);

System.debug('=== Step 1 Complete: ' + total + ' records deleted ===');