// Delete customer-demo usage rates (CD-DEMO Base + Tier rate cards only).
// Safe no-op when absent. Does not touch QB rate cards or unrelated entries.

final String DEMO_BASE_CARD = 'CD-DEMO Base Rate Card';
final String DEMO_TIER_CARD = 'CD-DEMO Tier Rate Card';

List<RateCard> demoCards = [
    SELECT Id
    FROM RateCard
    WHERE (Name = :DEMO_BASE_CARD AND Type = 'Base')
       OR (Name = :DEMO_TIER_CARD AND Type = 'Tier')
];
if (demoCards.isEmpty()) {
    System.debug('No CD-DEMO Base/Tier rate cards — nothing to delete.');
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
    System.debug('Deleted ' + demoCards.size() + ' CD-DEMO rate card record(s) (Base and/or Tier).');
}
