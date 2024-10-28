public with sharing abstract class AbstractAccountLocationService implements IAccountLocationService {
    public virtual IResponse associateLocations(IRequest createAccountLocationRequests) {
        throw new NotImplementedException();
    }

    public virtual List<AccountAddress> getAddresses(Id accountId, String addressType) {
        throw new NotImplementedException();
    }
}