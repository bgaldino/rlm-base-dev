// Delete customer-demo usage rates (CD-DEMO Base Rate Card slice only).
// Safe no-op when absent. Does not touch QB rate cards or unrelated entries.

final String DEMO_RATE_CARD = 'CD-DEMO Base Rate Card';

List<RateCard> demoCards = [
    SELECT Id FROM RateCard WHERE Name = :DEMO_RATE_CARD AND Type = 'Base'
];
if (demoCards.isEmpty()) {
    System.debug('No CD-DEMO Base Rate Card — nothing to delete.');
} else {
    Set<Id> demoCardIds = new Map<Id, RateCard>(demoCards).keySet();

    List<RateCardEntry> activeRces = [
        SELECT Id, Status
        FROM RateCardEntry
        WHERE RateCardId IN :demoCardIds AND Status = 'Active'
    ];
    if (!activeRces.isEmpty()) {
        for (RateCardEntry rce : activeRces) {
            rce.Status = 'Inactive';
        }
        update activeRces;
        System.debug('Deactivated ' + activeRces.size() + ' demo RateCardEntry record(s).');
    }

    List<RateCardEntry> rcesToDelete = [
        SELECT Id FROM RateCardEntry WHERE RateCardId IN :demoCardIds
    ];
    if (!rcesToDelete.isEmpty()) {
        delete rcesToDelete;
        System.debug('Deleted ' + rcesToDelete.size() + ' demo RateCardEntry record(s).');
    }

    List<PriceBookRateCard> pbrcs = [
        SELECT Id FROM PriceBookRateCard WHERE RateCardId IN :demoCardIds
    ];
    if (!pbrcs.isEmpty()) {
        delete pbrcs;
        System.debug('Deleted ' + pbrcs.size() + ' demo PriceBookRateCard record(s).');
    }

    delete demoCards;
    System.debug('Deleted ' + demoCards.size() + ' CD-DEMO Base Rate Card record(s).');
}
