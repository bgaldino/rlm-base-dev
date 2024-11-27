public interface IProductDAO {
    List<SObject> queryProducts(Set<Id> productIds);
}