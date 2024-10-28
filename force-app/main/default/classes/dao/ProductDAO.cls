public with sharing class ProductDAO implements IProductDAO {
    private static IProductDAO instance = null;

    public static IProductDAO getInstance() {
        if (instance == null) {
            instance = new ProductDAO();
        }
        return instance;
    }

    public List<Product2> queryProducts(Set<Id> productIds) {
        List<String> fields = getProductFields();
        return this.runQueryProducts(fields, productIds);
    }

    private List<Product2> runQueryProducts(List<String> fields, Set<Id> productIds) {
    	String query = String.format(
                'SELECT {0} FROM Product2 WHERE Id IN :productIds',
                new List<String>{ String.join(fields, ', ') }
            );
        return Database.queryWithBinds(query, new Map<String, Object>{ 'productIds' => productIds}, SecurityCheck.getAccessLevel());

    }

    private static List<String> getProductFields() {
        return new List<String>{
            'Id',
            'Name',
            'Org62_Id__c'
        };
    }
}