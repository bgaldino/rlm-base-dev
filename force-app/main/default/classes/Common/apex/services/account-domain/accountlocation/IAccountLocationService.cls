public interface IAccountLocationService {
    IResponse associateLocations(IRequest createAccountLocationRequests);
    List<AccountAddress> getAddresses(Id accountId, String addressType);
}