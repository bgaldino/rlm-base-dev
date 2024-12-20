public with sharing class DerivedPriceDAO implements IDerivedPriceDAO  {
    /************************************************
     * Setup class instance
     ************************************************/
    private static IDerivedPriceDAO instance = null;

    public static IDerivedPriceDAO getInstance() {
        if (instance == null) {
            instance = new DerivedPriceDAO();
        }
        return instance;
    }

    /** @description: Make class mockable for unit tests */
    public static void setInstance(IDerivedPriceDAO existingInstance) {
        instance = existingInstance;
    }

    public void insertLines(List<PriceBookEntryDerivedPrice> lines) {
        if (lines.getSObjectType().getDescribe().isCreateable()) {
            Database.insert(lines, SecurityCheck.getAccessLevel());
        }
    }

    public void updateLines(List<PriceBookEntryDerivedPrice> lines) {
        if (lines.getSObjectType().getDescribe().isUpdateable()) {
            Database.update(lines, SecurityCheck.getAccessLevel());
        }
    }

    public void deleteLines(List<PriceBookEntryDerivedPrice> lines) {
        if (lines.getSObjectType().getDescribe().isDeletable()) {
            Database.delete(lines, SecurityCheck.getAccessLevel());
        }
    }

    private List<PriceBookEntryDerivedPrice> runQuery(List<String> fields, Set<Id> pricebookEntryIds, Set<Id> contributingProductIds) {
        String qry = 'SELECT {0} FROM PriceBookEntryDerivedPrice WHERE PricebookEntryId IN :pricebookEntryIds';

        if (contributingProductIds != null && contributingProductIds.size() > 0) {
            qry +=' AND ContributingProductId IN :contributingProductIds';
        }
        
        String query = String.format(qry, new List<String>{ String.join(fields, ', ') }
        );

        return Database.queryWithBinds(query, new Map<String, Object>{ 'pricebookEntryIds' => pricebookEntryIds , 
                                                                       'contributingProductIds' => contributingProductIds }, SecurityCheck.getAccessLevel());
    }
    

    public List<PriceBookEntryDerivedPrice> getDerivedPricesByPriceBookEntryIds(Set<Id> pricebookEntryIds, Set<Id> contributingProductIds) {
        List<String> fields = getDerivedPriceFields();
        return this.runQuery(fields, pricebookEntryIds, contributingProductIds);
    }

    private static List<String> getDerivedPriceFields() {
        return new List<String> {
                'id',
                'ProductId',
                'PricebookEntryId',
                'ContributingProductId',
                'EffectiveFrom',
                'EffectiveTo',
                'Formula'
        };
    }
}