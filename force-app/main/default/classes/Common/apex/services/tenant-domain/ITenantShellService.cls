public interface ITenantShellService {
    Map<Id, Id> findOrCreateDefaultTenant(Id accountId, Set<Id> productIds);
    TenantShellServiceResponse createSingleTenant(Id accountId, String providerName);
    Boolean checkExistingTenants(Id accountId, String providerName);
}
